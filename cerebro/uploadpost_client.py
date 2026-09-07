#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uploadpost_client.py — Cliente do Upload-Post para o Cerebro.

Substitui o Higgsfield na etapa de PUBLICACAO. Publica e agenda em TikTok,
Instagram, YouTube, LinkedIn e outras redes numa unica chamada.

API real (verificada em docs.upload-post.com/openapi.json):
  Base ........ https://api.upload-post.com/api
  Auth ........ Authorization: Apikey <UPLOAD_POST_API_KEY>
  POST /upload ............... video (multipart)
  POST /upload_photos ........ fotos / carrossel
  POST /upload_text .......... texto puro
  GET  /uploadposts/users .... perfis conectados
  GET  /uploadposts/me ....... valida a chave
  GET  /uploadposts/status ... status por request_id ou job_id
  GET  /uploadposts/history .. historico
  DELETE /uploadposts/schedule/{job_id} ... cancela agendamento

Regras fixas de TikTok exigidas pelo dono do sistema:
  publico, comentarios/duet/stitch liberados, marcado como conteudo de IA.
  -> privacy_level=PUBLIC_TO_EVERYONE, disable_comment/duet/stitch=False,
     is_aigc=True, is_ai_generated=True, post_mode=DIRECT_POST

Uso como biblioteca:
    from uploadpost_client import UploadPostClient
    up = UploadPostClient()
    up.listar_perfis()
    up.publicar_video("video.mp4", "Legenda", plataformas=["tiktok","instagram"])
    up.agendar_video("video.mp4", "Legenda", quando="2026-09-07T15:00:00Z")

Uso na linha de comando:
    python3 uploadpost_client.py perfis
    python3 uploadpost_client.py validar
    python3 uploadpost_client.py publicar video.mp4 "Minha legenda" --redes tiktok,instagram
    python3 uploadpost_client.py agendar video.mp4 "Legenda" --em 10
    python3 uploadpost_client.py status --job-id abc123
"""

from __future__ import annotations

import argparse
import json
import logging
import mimetypes
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence

import requests

# --------------------------------------------------------------------------
# Caminhos e ambiente
# --------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "publicacao.log"

API_BASE = "https://api.upload-post.com/api"

# Tamanho maximo aceito pela API por arquivo (limite pratico; acima disso o
# upload costuma estourar timeout do gateway).
MAX_BYTES = 1024 * 1024 * 1024  # 1 GB


def _carregar_env() -> None:
    """Le o .env da pasta (e da pasta pai) sem sobrescrever o ambiente real."""
    for env_path in (BASE_DIR / ".env", BASE_DIR.parent / ".env"):
        if not env_path.is_file():
            continue
        for linha in env_path.read_text(encoding="utf-8", errors="replace").splitlines():
            linha = linha.strip()
            if not linha or linha.startswith("#") or "=" not in linha:
                continue
            chave, _, valor = linha.partition("=")
            chave = chave.strip()
            valor = valor.strip().strip('"').strip("'")
            # Variavel ja exportada no shell tem prioridade sobre o .env.
            os.environ.setdefault(chave, valor)


_carregar_env()


# --------------------------------------------------------------------------
# Log
# --------------------------------------------------------------------------

def _montar_logger() -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log = logging.getLogger("publicacao")
    if log.handlers:
        return log
    log.setLevel(logging.INFO)
    formato = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(message)s", "%Y-%m-%d %H:%M:%S"
    )
    arquivo = logging.FileHandler(LOG_FILE, encoding="utf-8")
    arquivo.setFormatter(formato)
    log.addHandler(arquivo)
    console = logging.StreamHandler(sys.stderr)
    console.setFormatter(formato)
    log.addHandler(console)
    return log


logger = _montar_logger()


class UploadPostError(RuntimeError):
    """Falha definitiva do Upload-Post, ja depois de esgotar as tentativas."""


# --------------------------------------------------------------------------
# Constantes de plataforma
# --------------------------------------------------------------------------

# Redes que o Upload-Post aceita hoje. Usado so para avisar sobre erro de
# digitacao — nao bloqueia, porque a lista cresce com o tempo.
REDES_CONHECIDAS = {
    "tiktok", "instagram", "youtube", "linkedin", "facebook", "x", "threads",
    "pinterest", "reddit", "bluesky", "snapchat", "discord", "telegram",
    "google_business",
}

# Redes das duas automacoes diarias.
REDES_PADRAO = ["tiktok", "instagram"]

# Politica fixa de TikTok. Alterar aqui muda as duas automacoes de uma vez.
TIKTOK_PADRAO: dict[str, Any] = {
    "privacy_level": "PUBLIC_TO_EVERYONE",  # publico
    "disable_comment": False,               # comentarios liberados
    "disable_duet": False,                  # duet liberado
    "disable_stitch": False,                # stitch liberado
    "post_mode": "DIRECT_POST",             # publica direto, sem rascunho
    "is_aigc": True,                        # conteudo gerado por IA (TikTok)
    "cover_timestamp": 1000,
}

# Disclosure de IA que vale para todas as redes.
IA_PADRAO: dict[str, Any] = {"is_ai_generated": True}

# Limite de caracteres por rede, usado para cortar legenda com seguranca.
LIMITE_LEGENDA = {
    "tiktok": 2200,
    "instagram": 2200,
    "youtube": 5000,
    "linkedin": 3000,
    "x": 280,
    "threads": 500,
    "facebook": 5000,
    "pinterest": 500,
    "reddit": 40000,
    "bluesky": 300,
}


def limite_de(rede: str) -> int:
    return LIMITE_LEGENDA.get(rede.lower(), 2200)


def cortar_legenda(texto: str, rede: str) -> str:
    """Corta no limite da rede sem quebrar palavra e sem cortar hashtag pela metade."""
    limite = limite_de(rede)
    texto = (texto or "").strip()
    if len(texto) <= limite:
        return texto
    corte = texto[: limite - 1]
    if " " in corte:
        corte = corte[: corte.rindex(" ")]
    return corte.rstrip() + "…"


# --------------------------------------------------------------------------
# Cliente
# --------------------------------------------------------------------------

class UploadPostClient:
    """Cliente com retry 3x e log em logs/publicacao.log."""

    def __init__(
        self,
        api_key: str | None = None,
        usuario: str | None = None,
        tentativas: int = 3,
        timeout: int = 300,
    ) -> None:
        self.api_key = api_key or os.environ.get("UPLOAD_POST_API_KEY", "")
        if not self.api_key:
            raise UploadPostError(
                "UPLOAD_POST_API_KEY nao encontrada. Rode: "
                "python3 configurar_chaves.py --upload-post SUA_CHAVE"
            )
        # 'user' na API = nome do perfil dentro da sua conta Upload-Post.
        self.usuario = usuario or os.environ.get("UPLOAD_POST_USER", "")
        self.tentativas = max(1, tentativas)
        self.timeout = timeout
        self.sessao = requests.Session()
        self.sessao.headers.update({"Authorization": f"Apikey {self.api_key}"})

    # -- infraestrutura ----------------------------------------------------

    def _requisitar(
        self,
        metodo: str,
        caminho: str,
        *,
        params: dict | None = None,
        data: Sequence[tuple[str, Any]] | dict | None = None,
        arquivos: Sequence[tuple[str, Any]] | None = None,
        json_body: dict | None = None,
        rotulo: str = "",
    ) -> dict:
        """Executa a chamada com ate `self.tentativas` tentativas.

        Repete em erro de rede e em 429/5xx. Nao repete em 4xx (a nao ser 429),
        porque erro de parametro nao melhora com insistencia.
        """
        url = f"{API_BASE}{caminho}"
        rotulo = rotulo or f"{metodo} {caminho}"
        ultimo_erro: Exception | None = None

        for tentativa in range(1, self.tentativas + 1):
            # Arquivos precisam ser reabertos a cada tentativa: o handle fica
            # no fim do arquivo depois de um upload que falhou.
            abertos: list[Any] = []
            try:
                envio = None
                if arquivos:
                    envio = []
                    for campo, caminho_arq in arquivos:
                        fh = open(caminho_arq, "rb")
                        abertos.append(fh)
                        tipo = mimetypes.guess_type(str(caminho_arq))[0] or "application/octet-stream"
                        envio.append((campo, (Path(caminho_arq).name, fh, tipo)))

                inicio = time.time()
                resposta = self.sessao.request(
                    metodo,
                    url,
                    params=params,
                    data=data,
                    files=envio,
                    json=json_body,
                    timeout=self.timeout,
                )
                duracao = time.time() - inicio

                if resposta.status_code < 400:
                    logger.info(
                        "%s | OK %s em %.1fs (tentativa %d)",
                        rotulo, resposta.status_code, duracao, tentativa
                    )
                    try:
                        return resposta.json()
                    except ValueError:
                        return {"raw": resposta.text}

                corpo = resposta.text[:600]
                repetivel = resposta.status_code == 429 or resposta.status_code >= 500
                logger.warning(
                    "%s | HTTP %s (tentativa %d/%d)%s | %s",
                    rotulo, resposta.status_code, tentativa, self.tentativas,
                    "" if repetivel else " [nao repetivel]", corpo,
                )
                if not repetivel:
                    raise UploadPostError(
                        f"{rotulo}: HTTP {resposta.status_code} — {corpo}"
                    )
                ultimo_erro = UploadPostError(
                    f"{rotulo}: HTTP {resposta.status_code} — {corpo}"
                )

            except (requests.RequestException, OSError) as exc:
                ultimo_erro = exc
                logger.warning(
                    "%s | falha de rede (tentativa %d/%d): %s",
                    rotulo, tentativa, self.tentativas, exc
                )
            finally:
                for fh in abertos:
                    try:
                        fh.close()
                    except Exception:
                        pass

            if tentativa < self.tentativas:
                espera = 2 ** tentativa  # 2s, 4s
                logger.info("%s | aguardando %ds antes de repetir", rotulo, espera)
                time.sleep(espera)

        logger.error("%s | FALHOU apos %d tentativas: %s", rotulo, self.tentativas, ultimo_erro)
        raise UploadPostError(f"{rotulo} falhou apos {self.tentativas} tentativas: {ultimo_erro}")

    def _resolver_usuario(self, usuario: str | None) -> str:
        """Decide qual perfil usar. Se so existe um perfil na conta, usa ele."""
        alvo = usuario or self.usuario
        if alvo:
            return alvo
        perfis = self.listar_perfis()
        nomes = [p.get("username") for p in perfis if p.get("username")]
        if len(nomes) == 1:
            logger.info("Perfil unico detectado, usando '%s'", nomes[0])
            self.usuario = nomes[0]
            return nomes[0]
        raise UploadPostError(
            "Defina o perfil: UPLOAD_POST_USER no .env ou usuario=... "
            f"(perfis disponiveis: {nomes or 'nenhum'})"
        )

    @staticmethod
    def _validar_arquivo(caminho: str | Path) -> Path:
        p = Path(caminho).expanduser()
        if not p.is_file():
            raise UploadPostError(f"Arquivo nao encontrado: {p}")
        tamanho = p.stat().st_size
        if tamanho == 0:
            raise UploadPostError(f"Arquivo vazio: {p}")
        if tamanho > MAX_BYTES:
            raise UploadPostError(
                f"Arquivo grande demais ({tamanho/1e6:.0f} MB, maximo {MAX_BYTES/1e6:.0f} MB): {p}"
            )
        return p

    @staticmethod
    def _campos(base: dict[str, Any], plataformas: Iterable[str]) -> list[tuple[str, str]]:
        """Converte dict + lista de redes no formato multipart que a API espera.

        A API exige `platform[]` repetido, um por rede. Booleano vira 'true'/'false'.
        """
        campos: list[tuple[str, str]] = []
        for rede in plataformas:
            campos.append(("platform[]", rede))
        for chave, valor in base.items():
            if valor is None:
                continue
            if isinstance(valor, bool):
                campos.append((chave, "true" if valor else "false"))
            elif isinstance(valor, (list, tuple)):
                for item in valor:
                    campos.append((f"{chave}[]", str(item)))
            else:
                campos.append((chave, str(valor)))
        return campos

    @staticmethod
    def _normalizar_data(quando: str | datetime | int | None) -> str | None:
        """Aceita ISO-8601, datetime, ou minutos a partir de agora (int)."""
        if quando is None:
            return None
        if isinstance(quando, int):
            alvo = datetime.now(timezone.utc) + timedelta(minutes=quando)
        elif isinstance(quando, datetime):
            alvo = quando if quando.tzinfo else quando.replace(tzinfo=timezone.utc)
        else:
            texto = str(quando).strip()
            try:
                alvo = datetime.fromisoformat(texto.replace("Z", "+00:00"))
            except ValueError as exc:
                raise UploadPostError(
                    f"Data invalida: {quando!r}. Use ISO-8601 (2026-09-07T15:00:00Z) "
                    "ou um numero de minutos."
                ) from exc
            if alvo.tzinfo is None:
                alvo = alvo.replace(tzinfo=timezone.utc)

        alvo = alvo.astimezone(timezone.utc)
        if alvo <= datetime.now(timezone.utc):
            raise UploadPostError(
                f"scheduled_date precisa estar no futuro (recebi {alvo.isoformat()})"
            )
        return alvo.strftime("%Y-%m-%dT%H:%M:%SZ")

    # -- leitura -----------------------------------------------------------

    def validar_chave(self) -> dict:
        """GET /uploadposts/me — confirma que a chave funciona."""
        return self._requisitar("GET", "/uploadposts/me", rotulo="validar chave")

    def listar_perfis(self) -> list[dict]:
        """GET /uploadposts/users — perfis e redes conectadas."""
        resposta = self._requisitar("GET", "/uploadposts/users", rotulo="listar perfis")
        if isinstance(resposta, list):
            return resposta
        for chave in ("profiles", "users", "data", "results"):
            valor = resposta.get(chave)
            if isinstance(valor, list):
                return valor
        return []

    def redes_conectadas(self, usuario: str | None = None) -> dict[str, list[str]]:
        """Mapa {perfil: [redes conectadas]}, lendo o payload de /users.

        O payload traz as contas sociais em `social_accounts`; uma rede conta
        como conectada quando o valor nao e vazio/nulo.
        """
        mapa: dict[str, list[str]] = {}
        for perfil in self.listar_perfis():
            nome = perfil.get("username") or perfil.get("profile_username") or "?"
            if usuario and nome != usuario:
                continue
            contas = perfil.get("social_accounts") or perfil.get("accounts") or {}
            conectadas: list[str] = []
            if isinstance(contas, dict):
                for rede, dados in contas.items():
                    if not dados:
                        continue
                    if isinstance(dados, dict):
                        # Considera conectada se houver qualquer identificador.
                        if any(dados.get(k) for k in
                               ("username", "display_name", "id", "open_id",
                                "account_name", "social_images", "connected")):
                            conectadas.append(rede)
                    else:
                        conectadas.append(rede)
            elif isinstance(contas, list):
                conectadas = [str(c) for c in contas if c]
            mapa[nome] = sorted(conectadas)
        return mapa

    def status(self, request_id: str | None = None, job_id: str | None = None) -> dict:
        """GET /uploadposts/status — status de upload assincrono ou agendamento."""
        if not request_id and not job_id:
            raise UploadPostError("Informe request_id (upload async) ou job_id (agendado).")
        params = {k: v for k, v in (("request_id", request_id), ("job_id", job_id)) if v}
        return self._requisitar("GET", "/uploadposts/status", params=params, rotulo="status")

    def historico(self, limite: int = 20, **filtros: Any) -> dict:
        """GET /uploadposts/history — ultimos posts."""
        params = {"limit": limite, **{k: v for k, v in filtros.items() if v is not None}}
        return self._requisitar("GET", "/uploadposts/history", params=params, rotulo="historico")

    def agendamentos(self) -> dict:
        """GET /uploadposts/schedule — fila de agendados."""
        return self._requisitar("GET", "/uploadposts/schedule", rotulo="agendamentos")

    def cancelar_agendamento(self, job_id: str) -> dict:
        """DELETE /uploadposts/schedule/{job_id}."""
        return self._requisitar(
            "DELETE", f"/uploadposts/schedule/{job_id}", rotulo=f"cancelar {job_id}"
        )

    def tiktok_settings(self, usuario: str | None = None) -> dict:
        """GET /uploadposts/tiktok/settings — opcoes de privacidade que a conta permite.

        Serve para detectar contas que so aceitam SELF_ONLY (perfil privado ou
        app sem auditoria), caso em que 'publico' seria recusado pelo TikTok.
        """
        alvo = self._resolver_usuario(usuario)
        return self._requisitar(
            "GET", "/uploadposts/tiktok/settings",
            params={"user": alvo}, rotulo="tiktok settings",
        )

    # -- publicacao --------------------------------------------------------

    def publicar_video(
        self,
        video: str | Path,
        legenda: str = "",
        plataformas: Sequence[str] | None = None,
        *,
        usuario: str | None = None,
        titulo: str | None = None,
        descricao: str | None = None,
        legendas_por_rede: dict[str, str] | None = None,
        quando: str | datetime | int | None = None,
        timezone_iana: str | None = None,
        assincrono: bool = True,
        extras: dict[str, Any] | None = None,
    ) -> dict:
        """POST /upload — publica (ou agenda) um video.

        `legendas_por_rede` permite texto diferente por rede; cai para `legenda`
        nas redes nao listadas. `quando` agenda: ISO-8601, datetime ou minutos.
        """
        caminho = self._validar_arquivo(video)
        alvo = self._resolver_usuario(usuario)
        redes = list(plataformas or REDES_PADRAO)
        if not redes:
            raise UploadPostError("Nenhuma plataforma informada.")

        desconhecidas = [r for r in redes if r.lower() not in REDES_CONHECIDAS]
        if desconhecidas:
            logger.warning("Rede(s) fora da lista conhecida: %s", desconhecidas)

        texto = legenda or titulo or ""
        corpo: dict[str, Any] = {
            "user": alvo,
            "title": cortar_legenda(titulo or texto, "youtube"),
            "async_upload": assincrono,
        }
        if descricao:
            corpo["description"] = descricao

        # Politica fixa de TikTok + disclosure de IA em todas as redes.
        corpo.update(IA_PADRAO)
        if "tiktok" in [r.lower() for r in redes]:
            corpo.update(TIKTOK_PADRAO)

        # Texto especifico por rede.
        por_rede = dict(legendas_por_rede or {})
        for rede in redes:
            chave = rede.lower()
            especifico = por_rede.get(chave, texto)
            if chave == "tiktok":
                corpo["tiktok_title"] = cortar_legenda(especifico, "tiktok")
            elif chave == "instagram":
                corpo["instagram_title"] = cortar_legenda(especifico, "instagram")
            elif chave == "youtube":
                corpo["youtube_title"] = cortar_legenda(especifico, "youtube")[:100]
                corpo["youtube_description"] = cortar_legenda(especifico, "youtube")
            elif chave == "linkedin":
                corpo["linkedin_title"] = cortar_legenda(especifico, "linkedin")

        agendado = self._normalizar_data(quando)
        if agendado:
            corpo["scheduled_date"] = agendado
            if timezone_iana:
                corpo["timezone"] = timezone_iana

        if extras:
            corpo.update(extras)

        campos = self._campos(corpo, redes)
        acao = f"agendar para {agendado}" if agendado else "publicar"
        logger.info(
            "%s video '%s' | perfil=%s | redes=%s | %.1f MB",
            acao.capitalize(), caminho.name, alvo, ",".join(redes),
            caminho.stat().st_size / 1e6,
        )

        resposta = self._requisitar(
            "POST", "/upload",
            data=campos,
            arquivos=[("video", caminho)],
            rotulo=f"{acao} video ({','.join(redes)})",
        )
        self._registrar_resultado(resposta, redes)
        return resposta

    def publicar_imagem(
        self,
        imagens: str | Path | Sequence[str | Path],
        legenda: str = "",
        plataformas: Sequence[str] | None = None,
        *,
        usuario: str | None = None,
        legendas_por_rede: dict[str, str] | None = None,
        quando: str | datetime | int | None = None,
        timezone_iana: str | None = None,
        assincrono: bool = True,
        extras: dict[str, Any] | None = None,
    ) -> dict:
        """POST /upload_photos — publica (ou agenda) uma foto ou carrossel."""
        if isinstance(imagens, (str, Path)):
            lista = [imagens]
        else:
            lista = list(imagens)
        if not lista:
            raise UploadPostError("Nenhuma imagem informada.")
        caminhos = [self._validar_arquivo(i) for i in lista]

        alvo = self._resolver_usuario(usuario)
        redes = list(plataformas or REDES_PADRAO)
        texto = legenda or ""

        corpo: dict[str, Any] = {
            "user": alvo,
            "title": cortar_legenda(texto, "instagram"),
            "async_upload": assincrono,
        }
        corpo.update(IA_PADRAO)
        if "tiktok" in [r.lower() for r in redes]:
            # Post de foto no TikTok usa um subconjunto dos parametros de video.
            corpo.update({
                "privacy_level": TIKTOK_PADRAO["privacy_level"],
                "disable_comment": TIKTOK_PADRAO["disable_comment"],
                "post_mode": TIKTOK_PADRAO["post_mode"],
                "photo_cover_index": 0,
            })
            corpo["tiktok_description"] = cortar_legenda(
                (legendas_por_rede or {}).get("tiktok", texto), "tiktok"
            )
        if "instagram" in [r.lower() for r in redes]:
            corpo["media_type"] = "IMAGE"
            corpo["instagram_title"] = cortar_legenda(
                (legendas_por_rede or {}).get("instagram", texto), "instagram"
            )

        agendado = self._normalizar_data(quando)
        if agendado:
            corpo["scheduled_date"] = agendado
            if timezone_iana:
                corpo["timezone"] = timezone_iana
        if extras:
            corpo.update(extras)

        campos = self._campos(corpo, redes)
        acao = f"agendar para {agendado}" if agendado else "publicar"
        logger.info(
            "%s %d imagem(ns) | perfil=%s | redes=%s",
            acao.capitalize(), len(caminhos), alvo, ",".join(redes)
        )
        resposta = self._requisitar(
            "POST", "/upload_photos",
            data=campos,
            arquivos=[("photos[]", c) for c in caminhos],
            rotulo=f"{acao} imagem ({','.join(redes)})",
        )
        self._registrar_resultado(resposta, redes)
        return resposta

    def publicar_texto(
        self,
        texto: str,
        plataformas: Sequence[str] | None = None,
        *,
        usuario: str | None = None,
        quando: str | datetime | int | None = None,
        assincrono: bool = True,
    ) -> dict:
        """POST /upload_text — post so de texto (X, LinkedIn, Threads, ...)."""
        alvo = self._resolver_usuario(usuario)
        redes = list(plataformas or ["x", "linkedin", "threads"])
        corpo: dict[str, Any] = {
            "user": alvo,
            "title": texto,
            "async_upload": assincrono,
        }
        agendado = self._normalizar_data(quando)
        if agendado:
            corpo["scheduled_date"] = agendado
        resposta = self._requisitar(
            "POST", "/upload_text",
            data=self._campos(corpo, redes),
            rotulo=f"publicar texto ({','.join(redes)})",
        )
        self._registrar_resultado(resposta, redes)
        return resposta

    # Apelidos explicitos para agendamento (mesma API, `quando` obrigatorio).
    def agendar_video(self, video, legenda="", plataformas=None, *, quando, **kw):
        if quando is None:
            raise UploadPostError("agendar_video exige 'quando'.")
        return self.publicar_video(video, legenda, plataformas, quando=quando, **kw)

    def agendar_imagem(self, imagens, legenda="", plataformas=None, *, quando, **kw):
        if quando is None:
            raise UploadPostError("agendar_imagem exige 'quando'.")
        return self.publicar_imagem(imagens, legenda, plataformas, quando=quando, **kw)

    # -- pos-processamento -------------------------------------------------

    @staticmethod
    def _registrar_resultado(resposta: dict, redes: Sequence[str]) -> None:
        """Loga sucesso/falha por rede. A API responde por plataforma."""
        if not isinstance(resposta, dict):
            return
        ids = {
            k: resposta.get(k)
            for k in ("request_id", "job_id", "scheduled_id")
            if resposta.get(k)
        }
        if ids:
            logger.info("IDs retornados: %s", json.dumps(ids, ensure_ascii=False))

        resultados = resposta.get("results")
        if isinstance(resultados, dict):
            for rede, dados in resultados.items():
                ok = bool(dados.get("success")) if isinstance(dados, dict) else bool(dados)
                if ok:
                    link = ""
                    if isinstance(dados, dict):
                        link = dados.get("post_url") or dados.get("url") or ""
                    logger.info("  %-12s PUBLICADO %s", rede, link)
                else:
                    erro = dados.get("error") or dados if isinstance(dados, dict) else dados
                    logger.error("  %-12s FALHOU: %s", rede, str(erro)[:300])


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _imprimir(dado: Any) -> None:
    print(json.dumps(dado, indent=2, ensure_ascii=False, default=str))


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="uploadpost_client.py",
        description="Publica e agenda nas redes via Upload-Post.",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("validar", help="Confere se a chave funciona")
    sub.add_parser("perfis", help="Lista perfis e redes conectadas")
    sub.add_parser("fila", help="Lista posts agendados")

    p_tt = sub.add_parser("tiktok-settings", help="Opcoes de privacidade permitidas no TikTok")
    p_tt.add_argument("--perfil")

    p_pub = sub.add_parser("publicar", help="Publica agora")
    p_pub.add_argument("arquivo")
    p_pub.add_argument("legenda", nargs="?", default="")
    p_pub.add_argument("--redes", default=",".join(REDES_PADRAO))
    p_pub.add_argument("--perfil")
    p_pub.add_argument("--imagem", action="store_true", help="Trata o arquivo como imagem")

    p_ag = sub.add_parser("agendar", help="Agenda para o futuro")
    p_ag.add_argument("arquivo")
    p_ag.add_argument("legenda", nargs="?", default="")
    p_ag.add_argument("--redes", default=",".join(REDES_PADRAO))
    p_ag.add_argument("--perfil")
    p_ag.add_argument("--imagem", action="store_true")
    grupo = p_ag.add_mutually_exclusive_group(required=True)
    grupo.add_argument("--em", type=int, help="Minutos a partir de agora")
    grupo.add_argument("--data", help="ISO-8601, ex: 2026-09-07T15:00:00Z")

    p_st = sub.add_parser("status", help="Status de um post")
    p_st.add_argument("--request-id")
    p_st.add_argument("--job-id")

    p_hist = sub.add_parser("historico", help="Ultimos posts")
    p_hist.add_argument("--limite", type=int, default=20)

    p_canc = sub.add_parser("cancelar", help="Cancela um agendamento")
    p_canc.add_argument("job_id")

    args = ap.parse_args(argv)

    try:
        up = UploadPostClient(usuario=getattr(args, "perfil", None))

        if args.cmd == "validar":
            _imprimir(up.validar_chave())

        elif args.cmd == "perfis":
            perfis = up.listar_perfis()
            if not perfis:
                print("Nenhum perfil encontrado. Crie um perfil em upload-post.com "
                      "e conecte as redes.")
                return 1
            _imprimir(perfis)
            print("\n--- redes conectadas por perfil ---")
            for nome, redes in up.redes_conectadas().items():
                print(f"  {nome}: {', '.join(redes) if redes else '(nenhuma)'}")
                faltando = sorted(set(REDES_PADRAO) - set(redes))
                if faltando:
                    print(f"    FALTA CONECTAR: {', '.join(faltando)}")

        elif args.cmd == "fila":
            _imprimir(up.agendamentos())

        elif args.cmd == "tiktok-settings":
            _imprimir(up.tiktok_settings(args.perfil))

        elif args.cmd in ("publicar", "agendar"):
            redes = [r.strip() for r in args.redes.split(",") if r.strip()]
            quando = None
            if args.cmd == "agendar":
                quando = args.em if args.em is not None else args.data
            fn = up.publicar_imagem if args.imagem else up.publicar_video
            _imprimir(fn(args.arquivo, args.legenda, redes, quando=quando))

        elif args.cmd == "status":
            _imprimir(up.status(args.request_id, args.job_id))

        elif args.cmd == "historico":
            _imprimir(up.historico(args.limite))

        elif args.cmd == "cancelar":
            _imprimir(up.cancelar_agendamento(args.job_id))

    except UploadPostError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
