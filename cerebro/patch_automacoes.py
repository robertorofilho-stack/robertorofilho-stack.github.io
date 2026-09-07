#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_automacoes.py — troca Higgsfield -> Upload-Post e APIMart(texto) -> OpenRouter
nas automacoes que ja existem na maquina.

Este script NAO adivinha. Ele faz duas coisas, nessa ordem:

  1) DIAGNOSTICO (padrao): varre os .py da pasta, acha toda linha que fala com
     Higgsfield ou que usa o apimart para TEXTO, e mostra arquivo:linha com o
     trecho. Nada e alterado.

  2) APLICACAO (--aplicar): reescreve so o que e mecanicamente seguro
     (imports e chamadas de padrao conhecido), sempre com backup .bak.
     Tudo que for ambiguo fica marcado com um comentario TODO no proprio
     arquivo, para revisao humana — nunca reescrito no escuro.

Por que assim: reescrever chamada de API por regex, sem ver o codigo, quebra
producao. O diagnostico leva 2 segundos e mostra exatamente o que mudar.

Uso:
    python3 patch_automacoes.py                    # diagnostico
    python3 patch_automacoes.py --pasta ~/cerebro  # outra pasta
    python3 patch_automacoes.py --aplicar          # aplica o que e seguro
    python3 patch_automacoes.py --reverter         # restaura os .bak
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Arquivos que sao do proprio cerebro novo e nao devem ser alterados.
IGNORAR = {
    "uploadpost_client.py", "openrouter_client.py", "agendar.py",
    "configurar_chaves.py", "patch_automacoes.py", "testar.py",
}
IGNORAR_DIRS = {".git", "__pycache__", "venv", ".venv", "node_modules", "AGENDAMENTOS", "logs"}

# ---------------------------------------------------------------------------
# Padroes de deteccao
# ---------------------------------------------------------------------------

PADROES_PUBLICACAO = [
    (re.compile(r"\bimport\s+higgsfield\b|\bfrom\s+higgsfield\b", re.I), "import do Higgsfield"),
    (re.compile(r"\bhiggsfield[_\.]", re.I), "uso do Higgsfield"),
    (re.compile(r"HIGGSFIELD_[A-Z_]*KEY", re.I), "chave do Higgsfield"),
    (re.compile(r"\btiktok_publish\b|\btiktok_prepare_publish\b", re.I), "publicacao TikTok via Higgsfield"),
    (re.compile(r"api\.higgsfield\.ai|higgsfield\.ai/api", re.I), "endpoint do Higgsfield"),
]

PADROES_TEXTO = [
    (re.compile(r"apimart\w*\.\s*(chat|completion|complete|gerar_texto|texto|gpt|llm)", re.I),
     "APIMart usado para TEXTO"),
    (re.compile(r"\b(pesquisar|pesquisa|roteiro|legenda|caption|script)\s*\(", re.I),
     "funcao de pesquisa/roteiro/legenda"),
]

# Substituicoes mecanicamente seguras (import por import).
SUBS_SEGURAS = [
    (re.compile(r"^(\s*)import\s+higgsfield.*$", re.M),
     r"\1import uploadpost_client as publicador  # trocado: Higgsfield -> Upload-Post"),
    (re.compile(r"^(\s*)from\s+higgsfield\s+import\s+.*$", re.M),
     r"\1from uploadpost_client import UploadPostClient  # trocado: Higgsfield -> Upload-Post"),
]

CABECALHO_SUGERIDO = """\
# --- Cerebro: publicacao via Upload-Post (substitui Higgsfield) ---
from uploadpost_client import UploadPostClient
# --- Cerebro: texto via OpenRouter (fallback automatico para APIMart) ---
from openrouter_client import pesquisar, roteiro, legenda, trivial
"""

RECEITA = """\
=============================================================================
COMO TROCAR NA MAO (2 minutos por automacao)
=============================================================================

1) PUBLICACAO — onde hoje chama o Higgsfield, passe a chamar:

    from uploadpost_client import UploadPostClient
    up = UploadPostClient()

    # publicar agora:
    up.publicar_video("video_final.mp4", legenda_texto, ["tiktok", "instagram"])

    # agendar para daqui a 10 minutos:
    up.publicar_video("video_final.mp4", legenda_texto, ["tiktok", "instagram"],
                      quando=10)

   O TikTok ja vai publico, com comentario/duet/stitch liberados e marcado
   como conteudo de IA — isso e padrao no cliente, nao precisa passar nada.

2) TEXTO — onde hoje chama o apimart para pesquisa/roteiro/legenda:

    from openrouter_client import pesquisar, roteiro, legenda

    fatos   = pesquisar("tema do dia").texto
    script  = roteiro(f"Roteiro de 45 segundos sobre: {fatos}").texto
    caption = legenda(f"Legenda para Instagram sobre: {script}").texto

   Se o OpenRouter cair, essas funcoes caem sozinhas no apimart_client.
   Video e voz continuam no fal.ai e no ElevenLabs — nao mexa.

3) Rode uma vez com --seco / --em 10 antes de deixar no cron das 11h.
=============================================================================
"""


def arquivos_python(pasta: Path) -> list[Path]:
    achados = []
    for p in sorted(pasta.rglob("*.py")):
        if any(parte in IGNORAR_DIRS for parte in p.parts):
            continue
        if p.name in IGNORAR:
            continue
        achados.append(p)
    return achados


def diagnosticar(pasta: Path) -> dict[Path, list[tuple[int, str, str]]]:
    resultado: dict[Path, list[tuple[int, str, str]]] = {}
    for arq in arquivos_python(pasta):
        try:
            linhas = arq.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        achados: list[tuple[int, str, str]] = []
        for n, linha in enumerate(linhas, 1):
            if linha.strip().startswith("#"):
                continue
            for padrao, rotulo in PADROES_PUBLICACAO + PADROES_TEXTO:
                if padrao.search(linha):
                    achados.append((n, rotulo, linha.strip()[:120]))
                    break
        if achados:
            resultado[arq] = achados
    return resultado


def aplicar(pasta: Path) -> int:
    alterados = 0
    for arq in arquivos_python(pasta):
        original = arq.read_text(encoding="utf-8", errors="replace")
        novo = original
        for padrao, troca in SUBS_SEGURAS:
            novo = padrao.sub(troca, novo)

        # Marca linhas ambiguas com TODO, sem reescrever.
        linhas = novo.splitlines()
        saida = []
        for linha in linhas:
            marcada = linha
            if not linha.strip().startswith("#"):
                for padrao, rotulo in PADROES_PUBLICACAO:
                    if padrao.search(linha) and "uploadpost_client" not in linha:
                        marcada = linha + f"  # TODO CEREBRO: {rotulo} -> trocar por uploadpost_client"
                        break
            saida.append(marcada)
        novo = "\n".join(saida)
        if novo != original:
            shutil.copy2(arq, arq.with_suffix(arq.suffix + ".bak"))
            arq.write_text(novo + ("\n" if original.endswith("\n") else ""), encoding="utf-8")
            print(f"  alterado: {arq}  (backup em {arq.name}.bak)")
            alterados += 1
    return alterados


def reverter(pasta: Path) -> int:
    n = 0
    for bak in sorted(pasta.rglob("*.py.bak")):
        alvo = bak.with_suffix("")
        shutil.copy2(bak, alvo)
        bak.unlink()
        print(f"  revertido: {alvo}")
        n += 1
    return n


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Troca Higgsfield->Upload-Post e APIMart(texto)->OpenRouter.")
    ap.add_argument("--pasta", default=str(BASE_DIR.parent), help="Pasta das automacoes (padrao: pasta pai)")
    ap.add_argument("--aplicar", action="store_true", help="Aplica o que e seguro (com backup)")
    ap.add_argument("--reverter", action="store_true", help="Restaura os .bak")
    args = ap.parse_args(argv)

    pasta = Path(args.pasta).expanduser().resolve()
    if not pasta.is_dir():
        print(f"Pasta nao encontrada: {pasta}", file=sys.stderr)
        return 1

    if args.reverter:
        n = reverter(pasta)
        print(f"\n{n} arquivo(s) revertido(s).")
        return 0

    print(f"Varrendo {pasta} ...\n")
    achados = diagnosticar(pasta)

    if not achados:
        print("Nenhuma referencia a Higgsfield ou a texto via APIMart encontrada.")
        print("Se as automacoes estao em outra pasta, use --pasta CAMINHO.")
        print(RECEITA)
        return 0

    print(f"{len(achados)} arquivo(s) com pontos a trocar:\n")
    for arq, itens in achados.items():
        print(f"--- {arq}")
        for n, rotulo, trecho in itens:
            print(f"    linha {n:>4} | {rotulo}")
            print(f"               | {trecho}")
        print()

    if args.aplicar:
        print("Aplicando substituicoes seguras...\n")
        n = aplicar(pasta)
        print(f"\n{n} arquivo(s) alterado(s). Procure por 'TODO CEREBRO' para o resto.")
        print("Para desfazer tudo: python3 patch_automacoes.py --reverter")
    else:
        print("Nada foi alterado (diagnostico). Para aplicar: --aplicar")

    print(RECEITA)
    return 0


if __name__ == "__main__":
    sys.exit(main())
