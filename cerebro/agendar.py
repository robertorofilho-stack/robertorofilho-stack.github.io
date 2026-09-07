#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
agendar.py — comando "agendar" do Cerebro.

Le uma subpasta de AGENDAMENTOS/, adapta a legenda para cada rede com o
openrouter_client e agenda tudo pelo uploadpost_client.

Estrutura esperada de uma subpasta:

    AGENDAMENTOS/
      2026-09-07-joelho-corredor/
        video.mp4            <- ou imagem.jpg / foto1.jpg, foto2.jpg (carrossel)
        legenda.txt          <- legenda base, em portugues
        config.json          <- opcional; sobrescreve os padroes
        .publicado.json      <- criado pelo sistema depois de agendar

config.json (todos os campos opcionais):
    {
      "redes": ["tiktok", "instagram"],
      "quando": "2026-09-07T15:00:00Z",   // ou "+10" (minutos), ou "amanha 11:00"
      "perfil": "falardetudo",
      "adaptar": true,                    // false = usa a mesma legenda em todas
      "timezone": "America/Fortaleza",
      "titulo": "titulo do YouTube"
    }

Comandos:
    python3 agendar.py listar
    python3 agendar.py novo minha-ideia          # cria o esqueleto da pasta
    python3 agendar.py preparar PASTA            # so gera as legendas, nao envia
    python3 agendar.py PASTA --em 10             # adapta e agenda em 10 min
    python3 agendar.py todos --em 60             # agenda tudo que esta pendente
    python3 agendar.py PASTA --agora             # publica imediatamente
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Sequence

BASE_DIR = Path(__file__).resolve().parent
PASTA_AGENDAMENTOS = BASE_DIR / "AGENDAMENTOS"

sys.path.insert(0, str(BASE_DIR))

from uploadpost_client import (  # noqa: E402
    REDES_PADRAO, UploadPostClient, UploadPostError, cortar_legenda, limite_de, logger,
)

EXT_VIDEO = {".mp4", ".mov", ".m4v", ".webm", ".avi", ".mkv"}
EXT_IMAGEM = {".jpg", ".jpeg", ".png", ".webp", ".heic"}

MARCADOR = ".publicado.json"


# --------------------------------------------------------------------------
# Adaptacao de legenda por rede
# --------------------------------------------------------------------------

# Como cada rede quer o texto. Vira instrucao para o modelo de legenda.
ESTILO_REDE = {
    "tiktok": (
        "TikTok: primeira linha é um gancho curtíssimo que para o dedo. "
        "Linguagem falada e direta. Até 4 hashtags específicas no fim."
    ),
    "instagram": (
        "Instagram: primeira linha é gancho, depois 2 a 4 linhas curtas que "
        "entregam valor real e dão vontade de salvar. Termine com uma pergunta "
        "que gere comentário. Até 5 hashtags no fim."
    ),
    "youtube": (
        "YouTube Shorts: título/descrição com palavra-chave de busca no começo, "
        "porque o YouTube é buscador. Sem hashtag em excesso, até 3."
    ),
    "linkedin": (
        "LinkedIn: tom profissional, sem gíria e sem hashtag de vaidade. "
        "Abertura com uma observação concreta, corpo em 3 a 5 linhas curtas, "
        "fecho com um ponto de vista. No máximo 3 hashtags."
    ),
    "x": (
        "X (Twitter): no máximo 280 caracteres CONTANDO tudo. Uma ideia só, "
        "afiada. Sem hashtag, ou no máximo uma."
    ),
    "threads": (
        "Threads: conversa, leve, no máximo 500 caracteres. Sem hashtag."
    ),
    "facebook": (
        "Facebook: texto um pouco mais explicativo e caloroso, 3 a 5 linhas."
    ),
}


def adaptar_legenda(base: str, rede: str, contexto: str = "") -> tuple[str, float]:
    """Reescreve a legenda base no estilo da rede. Devolve (texto, custo)."""
    import openrouter_client as orc

    estilo = ESTILO_REDE.get(rede.lower(), f"{rede}: texto curto e direto.")
    limite = limite_de(rede)
    instrucao = (
        f"Reescreva a legenda abaixo para {rede}.\n\n"
        f"REGRAS DA REDE: {estilo}\n"
        f"LIMITE ABSOLUTO: {limite} caracteres.\n"
        f"{('CONTEXTO DO VÍDEO: ' + contexto) if contexto else ''}\n\n"
        f"LEGENDA BASE:\n{base}\n\n"
        "Devolva SOMENTE a legenda final, sem explicação e sem aspas."
    )
    try:
        r = orc.legenda(instrucao)
        texto = (r.texto or "").strip().strip('"')
        if not texto:
            raise ValueError("modelo devolveu texto vazio")
        return cortar_legenda(texto, rede), r.custo_usd
    except Exception as exc:
        # Nunca deixa o post morrer por causa da legenda: usa a base cortada.
        logger.warning("Falha ao adaptar legenda para %s (%s). Usando a base.", rede, exc)
        return cortar_legenda(base, rede), 0.0


# --------------------------------------------------------------------------
# Leitura da pasta
# --------------------------------------------------------------------------

class Post:
    """Uma subpasta de AGENDAMENTOS/ lida e validada."""

    def __init__(self, pasta: Path) -> None:
        self.pasta = pasta
        self.config = self._ler_config()
        self.videos = self._buscar(EXT_VIDEO)
        self.imagens = self._buscar(EXT_IMAGEM)
        self.legenda_base = self._ler_legenda()

    def _ler_config(self) -> dict:
        arq = self.pasta / "config.json"
        if not arq.is_file():
            return {}
        try:
            return json.loads(arq.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise UploadPostError(f"config.json invalido em {self.pasta.name}: {exc}") from exc

    def _buscar(self, exts: set[str]) -> list[Path]:
        achados = [
            p for p in sorted(self.pasta.iterdir())
            if p.is_file() and p.suffix.lower() in exts and not p.name.startswith(".")
        ]
        return achados

    def _ler_legenda(self) -> str:
        for nome in ("legenda.txt", "caption.txt", "texto.txt"):
            arq = self.pasta / nome
            if arq.is_file():
                return arq.read_text(encoding="utf-8").strip()
        return ""

    @property
    def ja_publicado(self) -> bool:
        return (self.pasta / MARCADOR).is_file()

    @property
    def redes(self) -> list[str]:
        return list(self.config.get("redes") or REDES_PADRAO)

    @property
    def tem_midia(self) -> bool:
        return bool(self.videos or self.imagens)

    def validar(self) -> list[str]:
        problemas = []
        if not self.tem_midia:
            problemas.append("nenhum video ou imagem na pasta")
        if not self.legenda_base:
            problemas.append("legenda.txt ausente ou vazio")
        if len(self.videos) > 1:
            problemas.append(f"{len(self.videos)} videos na pasta — deixe apenas 1")
        return problemas

    def marcar_publicado(self, resultado: dict, legendas: dict, custo: float) -> None:
        (self.pasta / MARCADOR).write_text(
            json.dumps({
                "quando": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "redes": self.redes,
                "legendas": legendas,
                "custo_legendas_usd": round(custo, 6),
                "resposta": resultado,
            }, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )


def listar_posts(somente_pendentes: bool = False) -> list[Post]:
    if not PASTA_AGENDAMENTOS.is_dir():
        return []
    posts = []
    for pasta in sorted(PASTA_AGENDAMENTOS.iterdir()):
        if not pasta.is_dir() or pasta.name.startswith((".", "_")):
            continue
        try:
            p = Post(pasta)
        except UploadPostError as exc:
            logger.error("%s", exc)
            continue
        if somente_pendentes and p.ja_publicado:
            continue
        posts.append(p)
    return posts


# --------------------------------------------------------------------------
# Interpretacao de data
# --------------------------------------------------------------------------

def interpretar_quando(valor: Any) -> Any:
    """Aceita '+10', 10, ISO-8601, 'amanha 11:00', 'hoje 15:30'."""
    if valor is None:
        return None
    if isinstance(valor, int):
        return valor
    texto = str(valor).strip().lower()
    if texto.startswith("+"):
        return int(texto[1:])
    if texto.isdigit():
        return int(texto)

    m = re.match(r"^(hoje|amanha|amanhã)\s+(\d{1,2}):(\d{2})$", texto)
    if m:
        dia, hora, minuto = m.group(1), int(m.group(2)), int(m.group(3))
        agora = datetime.now().astimezone()
        alvo = agora.replace(hour=hora, minute=minuto, second=0, microsecond=0)
        if dia in ("amanha", "amanhã"):
            alvo += timedelta(days=1)
        elif alvo <= agora:
            alvo += timedelta(days=1)  # "hoje 09:00" ja passou -> amanha
        return alvo.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return valor  # deixa o uploadpost_client validar como ISO-8601


# --------------------------------------------------------------------------
# Execucao
# --------------------------------------------------------------------------

def preparar_legendas(post: Post, adaptar: bool = True) -> tuple[dict[str, str], float]:
    """Gera o texto de cada rede. Devolve ({rede: texto}, custo total)."""
    base = post.legenda_base
    contexto = post.config.get("contexto", "")
    if not adaptar or not post.config.get("adaptar", True):
        return {r: cortar_legenda(base, r) for r in post.redes}, 0.0

    legendas: dict[str, str] = {}
    custo = 0.0
    for rede in post.redes:
        texto, c = adaptar_legenda(base, rede, contexto)
        legendas[rede] = texto
        custo += c
        print(f"  [{rede}] {len(texto)} chars — {texto[:80]}{'...' if len(texto) > 80 else ''}")
    return legendas, custo


def agendar_post(
    post: Post,
    quando: Any,
    *,
    adaptar: bool = True,
    seco: bool = False,
    forcar: bool = False,
) -> dict:
    """Adapta as legendas e agenda (ou publica) o post."""
    problemas = post.validar()
    if problemas:
        raise UploadPostError(f"{post.pasta.name}: " + "; ".join(problemas))

    if post.ja_publicado and not forcar:
        raise UploadPostError(
            f"{post.pasta.name} ja foi publicado (existe {MARCADOR}). "
            "Use --forcar para publicar de novo."
        )

    print(f"\n=== {post.pasta.name} ===")
    print(f"Redes: {', '.join(post.redes)}")
    midia = post.videos[0] if post.videos else post.imagens
    print(f"Midia: {midia if isinstance(midia, Path) else [m.name for m in midia]}")

    print("Gerando legendas por rede...")
    legendas, custo = preparar_legendas(post, adaptar)
    print(f"Custo das legendas: US$ {custo:.6f}")

    alvo = interpretar_quando(quando if quando is not None else post.config.get("quando"))

    if seco:
        print("\n[SIMULACAO] Nada foi enviado. Payload que seria mandado:")
        print(json.dumps({
            "midia": str(midia) if isinstance(midia, Path) else [str(m) for m in midia],
            "redes": post.redes,
            "quando": str(alvo),
            "legendas": legendas,
        }, indent=2, ensure_ascii=False))
        return {"simulacao": True, "legendas": legendas, "custo_usd": custo}

    up = UploadPostClient(usuario=post.config.get("perfil"))
    comum: dict[str, Any] = {
        "plataformas": post.redes,
        "legendas_por_rede": legendas,
        "quando": alvo,
        "timezone_iana": post.config.get("timezone"),
    }

    if post.videos:
        resultado = up.publicar_video(
            post.videos[0],
            legendas.get(post.redes[0], post.legenda_base),
            titulo=post.config.get("titulo"),
            **comum,
        )
    else:
        resultado = up.publicar_imagem(
            post.imagens,
            legendas.get(post.redes[0], post.legenda_base),
            **comum,
        )

    post.marcar_publicado(resultado, legendas, custo)
    print(f"\nOK — {'agendado para ' + str(alvo) if alvo else 'publicado agora'}")
    return {"resposta": resultado, "legendas": legendas, "custo_usd": custo}


def criar_esqueleto(nome: str) -> Path:
    slug = re.sub(r"[^a-z0-9-]+", "-", nome.lower()).strip("-")
    pasta = PASTA_AGENDAMENTOS / f"{datetime.now():%Y-%m-%d}-{slug}"
    pasta.mkdir(parents=True, exist_ok=True)
    legenda = pasta / "legenda.txt"
    if not legenda.exists():
        legenda.write_text(
            "Escreva aqui a legenda base, em português.\n"
            "A primeira linha é o gancho.\n",
            encoding="utf-8",
        )
    cfg = pasta / "config.json"
    if not cfg.exists():
        cfg.write_text(json.dumps({
            "redes": REDES_PADRAO,
            "quando": "amanha 11:00",
            "adaptar": True,
            "timezone": "America/Fortaleza",
        }, indent=2, ensure_ascii=False), encoding="utf-8")
    return pasta


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="agendar.py",
        description="Le AGENDAMENTOS/<pasta>, adapta a legenda por rede e agenda.",
    )
    ap.add_argument("alvo", nargs="?", help="Nome da subpasta, 'todos', 'listar' ou 'novo'")
    ap.add_argument("nome", nargs="?", help="Nome da nova pasta (com 'novo')")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--em", type=int, help="Minutos a partir de agora")
    g.add_argument("--data", help="ISO-8601 ou 'amanha 11:00'")
    g.add_argument("--agora", action="store_true", help="Publica imediatamente")
    ap.add_argument("--sem-adaptar", action="store_true", help="Usa a mesma legenda em todas as redes")
    ap.add_argument("--seco", action="store_true", help="Simula: nao envia nada")
    ap.add_argument("--forcar", action="store_true", help="Republica mesmo se ja publicado")

    args = ap.parse_args(argv)
    PASTA_AGENDAMENTOS.mkdir(parents=True, exist_ok=True)

    if not args.alvo or args.alvo == "listar":
        posts = listar_posts()
        if not posts:
            print(f"Nenhum post em {PASTA_AGENDAMENTOS}.")
            print("Crie um com: python3 agendar.py novo minha-ideia")
            return 0
        print(f"{'PASTA':<42} {'STATUS':<12} {'MIDIA':<8} REDES")
        for p in posts:
            status = "publicado" if p.ja_publicado else "pendente"
            problemas = p.validar()
            if problemas and not p.ja_publicado:
                status = "INCOMPLETO"
            midia = "video" if p.videos else (f"{len(p.imagens)} img" if p.imagens else "-")
            print(f"{p.pasta.name:<42} {status:<12} {midia:<8} {','.join(p.redes)}")
            if problemas and not p.ja_publicado:
                print(f"    -> {'; '.join(problemas)}")
        return 0

    if args.alvo == "novo":
        if not args.nome:
            print("Uso: python3 agendar.py novo nome-da-ideia", file=sys.stderr)
            return 1
        pasta = criar_esqueleto(args.nome)
        print(f"Criado: {pasta}")
        print("Coloque o video (video.mp4) ou as imagens na pasta, edite legenda.txt e rode:")
        print(f"  python3 agendar.py {pasta.name} --em 60")
        return 0

    quando: Any = None
    if args.agora:
        quando = None
    elif args.em is not None:
        quando = args.em
    elif args.data:
        quando = args.data

    if args.alvo == "preparar":
        print("Uso: python3 agendar.py PASTA --seco", file=sys.stderr)
        return 1

    alvos = listar_posts(somente_pendentes=True) if args.alvo == "todos" else None
    if alvos is None:
        pasta = PASTA_AGENDAMENTOS / args.alvo
        if not pasta.is_dir():
            print(f"Pasta nao encontrada: {pasta}", file=sys.stderr)
            print("Veja as disponiveis com: python3 agendar.py listar", file=sys.stderr)
            return 1
        alvos = [Post(pasta)]

    if not alvos:
        print("Nada pendente para agendar.")
        return 0

    erros = 0
    custo_total = 0.0
    for post in alvos:
        try:
            r = agendar_post(
                post, quando,
                adaptar=not args.sem_adaptar,
                seco=args.seco,
                forcar=args.forcar,
            )
            custo_total += float(r.get("custo_usd") or 0)
        except (UploadPostError, Exception) as exc:
            erros += 1
            print(f"ERRO em {post.pasta.name}: {exc}", file=sys.stderr)

    print(f"\nCusto total de legendas nesta rodada: US$ {custo_total:.6f}")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
