#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
openrouter_client.py — Cerebro do texto: pesquisa, roteiro e legenda.

Uma chave, centenas de modelos, API compativel com OpenAI. Se o OpenRouter
falhar, cai sozinho para o apimart_client (que continua sendo o dono de video
e voz). Cada chamada grava custo em logs/custos.jsonl.

Modelos (IDs conferidos em openrouter.ai/api/v1/models em 2026-09-07):
  pesquisa  -> google/gemini-3.8-flash     US$ 0,75 / 1M entrada | 3,75 / 1M saida
  roteiro   -> anthropic/claude-sonnet-5   US$ 2,00 / 1M entrada | 10,00 / 1M saida
  legenda   -> anthropic/claude-sonnet-5   idem
  trivial   -> openai/gpt-5-nano           US$ 0,05 / 1M entrada | 0,40 / 1M saida

Para trocar sem mexer no codigo, use o .env:
  OPENROUTER_MODELO_PESQUISA, OPENROUTER_MODELO_ROTEIRO,
  OPENROUTER_MODELO_LEGENDA, OPENROUTER_MODELO_TRIVIAL
Aliases que acompanham sozinhos o modelo mais novo (custo pode mudar sem aviso):
  ~google/gemini-flash-latest, ~anthropic/claude-sonnet-latest

Uso como biblioteca:
    from openrouter_client import pesquisar, roteiro, legenda, trivial
    texto = pesquisar("tendencias de dor no joelho em corredores")
    script = roteiro("Faca um roteiro de 45s sobre " + texto)

Uso na linha de comando:
    python3 openrouter_client.py testar
    python3 openrouter_client.py pesquisa "assunto"
    python3 openrouter_client.py custos
    python3 openrouter_client.py testar-fallback
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Sequence

import requests

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
LOG_CUSTOS = LOG_DIR / "custos.jsonl"
LOG_TEXTO = LOG_DIR / "openrouter.log"

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODELOS_URL = "https://openrouter.ai/api/v1/models"


def _carregar_env() -> None:
    for env_path in (BASE_DIR / ".env", BASE_DIR.parent / ".env"):
        if not env_path.is_file():
            continue
        for linha in env_path.read_text(encoding="utf-8", errors="replace").splitlines():
            linha = linha.strip()
            if not linha or linha.startswith("#") or "=" not in linha:
                continue
            chave, _, valor = linha.partition("=")
            os.environ.setdefault(chave.strip(), valor.strip().strip('"').strip("'"))


_carregar_env()


def _montar_logger() -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log = logging.getLogger("openrouter")
    if log.handlers:
        return log
    log.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s", "%Y-%m-%d %H:%M:%S")
    fh = logging.FileHandler(LOG_TEXTO, encoding="utf-8")
    fh.setFormatter(fmt)
    log.addHandler(fh)
    sh = logging.StreamHandler(sys.stderr)
    sh.setFormatter(fmt)
    log.addHandler(sh)
    return log


logger = _montar_logger()


class OpenRouterError(RuntimeError):
    """Falha no OpenRouter depois de esgotar tentativas E fallback."""


# --------------------------------------------------------------------------
# Catalogo de modelos
# --------------------------------------------------------------------------

# Precos em US$ por token (nao por milhao), como o OpenRouter publica.
# Servem para calcular custo mesmo quando a resposta nao traz o campo de custo.
PRECOS: dict[str, tuple[float, float]] = {
    "google/gemini-3.8-flash":      (0.00000075, 0.00000375),
    "google/gemini-3.1-flash-lite": (0.00000025, 0.0000015),
    "anthropic/claude-sonnet-5":    (0.000002,   0.00001),
    "anthropic/claude-opus-5":      (0.000005,   0.000025),
    "anthropic/claude-haiku-4.5":   (0.000001,   0.000005),
    "openai/gpt-5-nano":            (0.00000005, 0.0000004),
    "openai/gpt-oss-20b":           (0.00000003, 0.00000013),
    "openai/gpt-5-mini":            (0.00000025, 0.000002),
}

TAREFAS: dict[str, str] = {
    "pesquisa": os.environ.get("OPENROUTER_MODELO_PESQUISA", "google/gemini-3.8-flash"),
    "roteiro":  os.environ.get("OPENROUTER_MODELO_ROTEIRO",  "anthropic/claude-sonnet-5"),
    "legenda":  os.environ.get("OPENROUTER_MODELO_LEGENDA",  "anthropic/claude-sonnet-5"),
    "trivial":  os.environ.get("OPENROUTER_MODELO_TRIVIAL",  "openai/gpt-5-nano"),
}


@dataclass
class Resposta:
    """Resultado de uma chamada, com a conta do que custou."""
    texto: str
    modelo: str
    tarefa: str
    provedor: str            # "openrouter" ou "apimart"
    tokens_entrada: int = 0
    tokens_saida: int = 0
    custo_usd: float = 0.0
    segundos: float = 0.0
    tentativas: int = 1
    caiu_para_fallback: bool = False
    bruto: dict = field(default_factory=dict, repr=False)

    def __str__(self) -> str:
        return self.texto


# --------------------------------------------------------------------------
# Registro de custo
# --------------------------------------------------------------------------

def registrar_custo(r: Resposta) -> None:
    """Grava uma linha JSON por chamada em logs/custos.jsonl."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    linha = {
        "quando": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "tarefa": r.tarefa,
        "modelo": r.modelo,
        "provedor": r.provedor,
        "tokens_entrada": r.tokens_entrada,
        "tokens_saida": r.tokens_saida,
        "custo_usd": round(r.custo_usd, 8),
        "segundos": round(r.segundos, 2),
        "tentativas": r.tentativas,
        "fallback": r.caiu_para_fallback,
    }
    with open(LOG_CUSTOS, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(linha, ensure_ascii=False) + "\n")
    logger.info(
        "%s | %s via %s | %d+%d tokens | US$ %.6f | %.1fs%s",
        r.tarefa, r.modelo, r.provedor, r.tokens_entrada, r.tokens_saida,
        r.custo_usd, r.segundos, " | FALLBACK" if r.caiu_para_fallback else "",
    )


def calcular_custo(modelo: str, entrada: int, saida: int) -> float:
    preco = PRECOS.get(modelo)
    if not preco:
        # Modelo fora da tabela: nao inventa numero, registra zero e avisa.
        logger.warning("Sem preco cadastrado para '%s' — custo registrado como 0.", modelo)
        return 0.0
    return entrada * preco[0] + saida * preco[1]


def resumo_custos(desde: str | None = None) -> dict:
    """Le custos.jsonl e soma por tarefa, modelo e provedor."""
    if not LOG_CUSTOS.is_file():
        return {"total_usd": 0.0, "chamadas": 0, "por_tarefa": {}, "por_modelo": {}}
    total = 0.0
    chamadas = 0
    por_tarefa: dict[str, dict] = {}
    por_modelo: dict[str, dict] = {}
    fallbacks = 0
    for linha in LOG_CUSTOS.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha:
            continue
        try:
            d = json.loads(linha)
        except json.JSONDecodeError:
            continue
        if desde and d.get("quando", "") < desde:
            continue
        custo = float(d.get("custo_usd") or 0)
        total += custo
        chamadas += 1
        if d.get("fallback"):
            fallbacks += 1
        for mapa, chave in ((por_tarefa, d.get("tarefa", "?")), (por_modelo, d.get("modelo", "?"))):
            item = mapa.setdefault(chave, {"chamadas": 0, "custo_usd": 0.0,
                                           "tokens_entrada": 0, "tokens_saida": 0})
            item["chamadas"] += 1
            item["custo_usd"] = round(item["custo_usd"] + custo, 8)
            item["tokens_entrada"] += int(d.get("tokens_entrada") or 0)
            item["tokens_saida"] += int(d.get("tokens_saida") or 0)
    return {
        "total_usd": round(total, 6),
        "chamadas": chamadas,
        "fallbacks": fallbacks,
        "por_tarefa": por_tarefa,
        "por_modelo": por_modelo,
    }


# --------------------------------------------------------------------------
# Fallback: APIMart
# --------------------------------------------------------------------------

def _chamar_apimart(mensagens: list[dict], tarefa: str, **kw: Any) -> Resposta:
    """Ultimo recurso: reaproveita o apimart_client que ja existe na pasta.

    Nao assume um nome de funcao especifico — procura o primeiro nome plausivel
    que o modulo exponha, para funcionar com a versao que estiver instalada.
    """
    sys.path.insert(0, str(BASE_DIR))
    try:
        import apimart_client  # type: ignore
    except ImportError as exc:
        raise OpenRouterError(
            "OpenRouter falhou e o apimart_client nao pode ser importado "
            f"({exc}). Sem fallback disponivel."
        ) from exc

    candidatos = [
        "chat", "chat_completion", "completar", "completion", "gerar_texto",
        "texto", "gerar", "ask", "perguntar", "call", "chamar",
    ]
    alvo: Callable | None = None
    nome_usado = ""
    for nome in candidatos:
        fn = getattr(apimart_client, nome, None)
        if callable(fn):
            alvo, nome_usado = fn, nome
            break
    if alvo is None:
        for nome in dir(apimart_client):
            if nome.startswith("_"):
                continue
            fn = getattr(apimart_client, nome)
            if callable(fn) and any(p in nome.lower() for p in ("chat", "text", "texto", "gpt", "llm")):
                alvo, nome_usado = fn, nome
                break
    if alvo is None:
        raise OpenRouterError(
            "apimart_client importado, mas nenhuma funcao de texto reconhecida. "
            f"Disponiveis: {[n for n in dir(apimart_client) if not n.startswith('_')]}"
        )

    prompt = "\n\n".join(m.get("content", "") for m in mensagens if m.get("content"))
    inicio = time.time()
    logger.warning("FALLBACK -> apimart_client.%s() para tarefa '%s'", nome_usado, tarefa)

    # Tenta a assinatura mais rica primeiro e vai simplificando.
    for tentativa_kwargs in ({"messages": mensagens}, {"prompt": prompt}, {}):
        try:
            saida = alvo(**tentativa_kwargs) if tentativa_kwargs else alvo(prompt)
            break
        except TypeError:
            continue
    else:
        raise OpenRouterError(f"Nao consegui chamar apimart_client.{nome_usado} com nenhuma assinatura.")

    if isinstance(saida, dict):
        texto = (
            saida.get("text")
            or saida.get("content")
            or saida.get("choices", [{}])[0].get("message", {}).get("content", "")
        )
    else:
        texto = str(saida)

    r = Resposta(
        texto=texto.strip(),
        modelo=f"apimart:{nome_usado}",
        tarefa=tarefa,
        provedor="apimart",
        segundos=time.time() - inicio,
        caiu_para_fallback=True,
        bruto=saida if isinstance(saida, dict) else {},
    )
    registrar_custo(r)
    return r


# --------------------------------------------------------------------------
# Cliente
# --------------------------------------------------------------------------

class OpenRouterClient:
    def __init__(
        self,
        api_key: str | None = None,
        tentativas: int = 3,
        timeout: int = 180,
        usar_fallback: bool = True,
    ) -> None:
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY", "")
        self.tentativas = max(1, tentativas)
        self.timeout = timeout
        self.usar_fallback = usar_fallback
        self.sessao = requests.Session()
        self.sessao.headers.update({
            "Content-Type": "application/json",
            # Cabecalhos opcionais do OpenRouter: identificam o app no ranking.
            "HTTP-Referer": os.environ.get("OPENROUTER_REFERER", "https://www.drrobertorodrigues.com"),
            "X-Title": os.environ.get("OPENROUTER_TITLE", "Cerebro Roberto"),
        })
        if self.api_key:
            self.sessao.headers["Authorization"] = f"Bearer {self.api_key}"

    # -- chamada base ------------------------------------------------------

    def completar(
        self,
        prompt: str | list[dict],
        tarefa: str = "trivial",
        *,
        modelo: str | None = None,
        sistema: str | None = None,
        temperatura: float = 0.7,
        max_tokens: int | None = None,
        json_estrito: bool = False,
        _forcar_falha: bool = False,
    ) -> Resposta:
        """Chama o OpenRouter. Se falhar de vez, cai para o apimart_client.

        `_forcar_falha=True` simula queda do OpenRouter — usado no teste de
        fallback. Nao usar em producao.
        """
        modelo_alvo = modelo or TAREFAS.get(tarefa, TAREFAS["trivial"])

        if isinstance(prompt, str):
            mensagens: list[dict] = []
            if sistema:
                mensagens.append({"role": "system", "content": sistema})
            mensagens.append({"role": "user", "content": prompt})
        else:
            mensagens = list(prompt)

        corpo: dict[str, Any] = {
            "model": modelo_alvo,
            "messages": mensagens,
            "temperature": temperatura,
            # Pede a contagem de uso/custo real na resposta.
            "usage": {"include": True},
        }
        if max_tokens:
            corpo["max_tokens"] = max_tokens
        if json_estrito:
            corpo["response_format"] = {"type": "json_object"}

        ultimo_erro: Exception | None = None

        # Modelos de raciocinio (Gemini 3.x, GPT-5, Sonnet 5) gastam tokens
        # "pensando" antes de escrever. Com orcamento apertado, a resposta volta
        # com finish_reason='length' e content vazio. Quando isso acontece,
        # aumentamos o teto e tentamos de novo em vez de devolver texto vazio.
        teto = corpo.get("max_tokens")

        if not self.api_key and not _forcar_falha:
            ultimo_erro = OpenRouterError("OPENROUTER_API_KEY nao configurada")
            logger.warning("Sem OPENROUTER_API_KEY — indo direto para o fallback.")
        else:
            for tentativa in range(1, self.tentativas + 1):
                try:
                    if _forcar_falha:
                        raise requests.ConnectionError("falha simulada para teste de fallback")

                    inicio = time.time()
                    resp = self.sessao.post(API_URL, json=corpo, timeout=self.timeout)
                    duracao = time.time() - inicio

                    if resp.status_code < 400:
                        dados = resp.json()
                        if "error" in dados and not dados.get("choices"):
                            raise OpenRouterError(str(dados["error"])[:400])
                        r = self._montar_resposta(
                            dados, modelo_alvo, tarefa, duracao, tentativa
                        )

                        # Texto vazio por falta de orcamento: aumenta o teto e
                        # tenta de novo, em vez de devolver "" em silencio.
                        escolha = (dados.get("choices") or [{}])[0]
                        if not r.texto and escolha.get("finish_reason") == "length":
                            registrar_custo(r)  # a tentativa perdida tambem custou
                            novo_teto = max((teto or 256) * 4, 1024)
                            if novo_teto <= (teto or 0) or novo_teto > 32768:
                                raise OpenRouterError(
                                    f"{modelo_alvo} devolveu texto vazio mesmo com "
                                    f"max_tokens={teto} (o raciocinio consumiu todo o orcamento)"
                                )

                            logger.warning(
                                "%s devolveu vazio com max_tokens=%s (raciocinio consumiu tudo). "
                                "Repetindo com %s.", modelo_alvo, teto, novo_teto,
                            )
                            teto = novo_teto
                            corpo["max_tokens"] = novo_teto
                            continue

                        if not r.texto:
                            raise OpenRouterError(
                                f"{modelo_alvo} devolveu texto vazio "
                                f"(finish_reason={escolha.get('finish_reason')})"
                            )

                        registrar_custo(r)
                        return r

                    corpo_erro = resp.text[:400]
                    repetivel = resp.status_code == 429 or resp.status_code >= 500
                    logger.warning(
                        "OpenRouter HTTP %s (tentativa %d/%d)%s: %s",
                        resp.status_code, tentativa, self.tentativas,
                        "" if repetivel else " [nao repetivel]", corpo_erro,
                    )
                    ultimo_erro = OpenRouterError(f"HTTP {resp.status_code}: {corpo_erro}")
                    if not repetivel:
                        break

                except (requests.RequestException, OpenRouterError, ValueError) as exc:
                    ultimo_erro = exc
                    logger.warning(
                        "OpenRouter falhou (tentativa %d/%d): %s",
                        tentativa, self.tentativas, exc
                    )

                if tentativa < self.tentativas:
                    time.sleep(2 ** tentativa)

        # Esgotou o OpenRouter.
        if self.usar_fallback:
            logger.error("OpenRouter indisponivel (%s). Acionando fallback APIMart.", ultimo_erro)
            return _chamar_apimart(mensagens, tarefa)

        raise OpenRouterError(f"OpenRouter falhou e o fallback esta desligado: {ultimo_erro}")

    @staticmethod
    def _montar_resposta(
        dados: dict, modelo: str, tarefa: str, duracao: float, tentativas: int
    ) -> Resposta:
        escolhas = dados.get("choices") or []
        texto = ""
        if escolhas:
            texto = (escolhas[0].get("message") or {}).get("content") or ""

        uso = dados.get("usage") or {}
        entrada = int(uso.get("prompt_tokens") or 0)
        saida = int(uso.get("completion_tokens") or 0)

        # O OpenRouter devolve o custo real em `usage.cost` (US$). Se vier,
        # ele vale mais que a tabela local de precos.
        custo_api = uso.get("cost")
        custo = float(custo_api) if custo_api not in (None, "") else calcular_custo(modelo, entrada, saida)

        return Resposta(
            texto=texto.strip(),
            modelo=dados.get("model") or modelo,
            tarefa=tarefa,
            provedor="openrouter",
            tokens_entrada=entrada,
            tokens_saida=saida,
            custo_usd=custo,
            segundos=duracao,
            tentativas=tentativas,
            bruto=dados,
        )

    # -- utilidades --------------------------------------------------------

    def creditos(self) -> dict:
        """Saldo pre-pago da conta."""
        r = self.sessao.get("https://openrouter.ai/api/v1/credits", timeout=30)
        r.raise_for_status()
        return r.json()

    def modelo_existe(self, modelo_id: str) -> bool:
        try:
            r = self.sessao.get(MODELOS_URL, timeout=60)
            r.raise_for_status()
            return any(m.get("id") == modelo_id for m in r.json().get("data", []))
        except requests.RequestException:
            return False


# --------------------------------------------------------------------------
# Atalhos por tarefa — e o que as automacoes chamam
# --------------------------------------------------------------------------

_cliente: OpenRouterClient | None = None


def cliente() -> OpenRouterClient:
    global _cliente
    if _cliente is None:
        _cliente = OpenRouterClient()
    return _cliente


SISTEMA_PESQUISA = (
    "Voce e um pesquisador objetivo. Responda em portugues do Brasil, com fatos "
    "verificaveis, numeros e fontes quando existirem. Sem enrolacao, sem elogio."
)

SISTEMA_ROTEIRO = (
    "Voce escreve roteiros curtos para video vertical (TikTok/Reels) em portugues "
    "do Brasil. Regras: primeira frase e um gancho que para o dedo; frases curtas; "
    "linguagem falada, humana, direta; uma ideia por frase; termina com uma frase "
    "que gera comentario ou compartilhamento. Devolva SOMENTE o texto a ser narrado, "
    "sem marcacao de cena, sem emojis, sem aspas."
)

SISTEMA_LEGENDA = (
    "Voce escreve legendas de redes sociais em portugues do Brasil que geram "
    "salvamento e comentario. Primeira linha e gancho. Sem emoji em excesso. "
    "Hashtags so no fim, no maximo 5, especificas e relevantes."
)


def pesquisar(assunto: str, **kw: Any) -> Resposta:
    return cliente().completar(assunto, "pesquisa", sistema=SISTEMA_PESQUISA, temperatura=0.3, **kw)


def roteiro(instrucao: str, **kw: Any) -> Resposta:
    return cliente().completar(instrucao, "roteiro", sistema=SISTEMA_ROTEIRO, temperatura=0.8, **kw)


def legenda(instrucao: str, **kw: Any) -> Resposta:
    return cliente().completar(instrucao, "legenda", sistema=SISTEMA_LEGENDA, temperatura=0.8, **kw)


def trivial(instrucao: str, **kw: Any) -> Resposta:
    return cliente().completar(instrucao, "trivial", temperatura=0.2, **kw)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="openrouter_client.py",
        description="Texto (pesquisa/roteiro/legenda) via OpenRouter, com fallback APIMart.",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    for nome in ("pesquisa", "roteiro", "legenda", "trivial"):
        p = sub.add_parser(nome, help=f"Roda a tarefa '{nome}'")
        p.add_argument("texto")
        p.add_argument("--modelo")

    sub.add_parser("testar", help="Uma chamada em cada modelo configurado")
    sub.add_parser("testar-fallback", help="Simula queda do OpenRouter e prova o fallback")
    sub.add_parser("creditos", help="Saldo da conta OpenRouter")
    sub.add_parser("modelos", help="Mostra os modelos configurados e o preco")
    p_c = sub.add_parser("custos", help="Resumo de custo acumulado")
    p_c.add_argument("--desde", help="ISO-8601, ex: 2026-09-01")

    args = ap.parse_args(argv)

    try:
        if args.cmd in ("pesquisa", "roteiro", "legenda", "trivial"):
            fn = {"pesquisa": pesquisar, "roteiro": roteiro,
                  "legenda": legenda, "trivial": trivial}[args.cmd]
            r = fn(args.texto, **({"modelo": args.modelo} if args.modelo else {}))
            print(r.texto)
            print(
                f"\n--- {r.modelo} via {r.provedor} | {r.tokens_entrada}+{r.tokens_saida} tokens "
                f"| US$ {r.custo_usd:.6f} | {r.segundos:.1f}s ---",
                file=sys.stderr,
            )

        elif args.cmd == "modelos":
            print(f"{'TAREFA':<10} {'MODELO':<32} {'US$/1M in':>10} {'US$/1M out':>11}")
            for tarefa, modelo in TAREFAS.items():
                p = PRECOS.get(modelo)
                ent = f"{p[0]*1e6:.2f}" if p else "?"
                sai = f"{p[1]*1e6:.2f}" if p else "?"
                print(f"{tarefa:<10} {modelo:<32} {ent:>10} {sai:>11}")

        elif args.cmd == "custos":
            print(json.dumps(resumo_custos(args.desde), indent=2, ensure_ascii=False))

        elif args.cmd == "creditos":
            print(json.dumps(cliente().creditos(), indent=2, ensure_ascii=False))

        elif args.cmd == "testar":
            total = 0.0
            falhas = 0
            for tarefa, modelo in TAREFAS.items():
                print(f"\n=== {tarefa} -> {modelo} ===")
                try:
                    r = cliente().completar(
                        "Responda exatamente: OK", tarefa, max_tokens=20, temperatura=0,
                    )
                    total += r.custo_usd
                    marca = "OK" if r.provedor == "openrouter" else "FALLBACK"
                    print(f"[{marca}] {r.texto[:120]!r} | US$ {r.custo_usd:.6f} | {r.segundos:.1f}s")
                    if r.provedor != "openrouter":
                        falhas += 1
                except Exception as exc:
                    falhas += 1
                    print(f"[FALHOU] {exc}")
            print(f"\nCusto total do teste: US$ {total:.6f}")
            return 1 if falhas else 0

        elif args.cmd == "testar-fallback":
            print("Simulando queda do OpenRouter (_forcar_falha=True)...")
            try:
                r = cliente().completar("Responda: OK", "trivial", _forcar_falha=True)
                print(f"Fallback respondeu via '{r.provedor}' ({r.modelo}): {r.texto[:120]!r}")
                return 0 if r.provedor == "apimart" else 1
            except OpenRouterError as exc:
                print(f"Fallback NAO funcionou: {exc}", file=sys.stderr)
                return 1

    except Exception as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
