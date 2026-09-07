#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
configurar_chaves.py — grava chaves no .env sem apagar o que ja existe.

Regras:
  - Se a chave ja existe no .env, o valor e SUBSTITUIDO na mesma linha.
  - Se nao existe, e ACRESCENTADA no fim.
  - Todas as outras linhas, comentarios e espacos ficam intactos.
  - Faz backup em .env.bak antes de qualquer alteracao.
  - Nunca imprime a chave inteira na tela.

Uso:
    python3 configurar_chaves.py --upload-post up_xxxxx
    python3 configurar_chaves.py --openrouter sk-or-v1-xxxxx
    python3 configurar_chaves.py --upload-post-user falardetudo
    python3 configurar_chaves.py --ver
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Procura o .env na pasta do cerebro e, se nao achar, na pasta pai.
def achar_env() -> Path:
    for candidato in (BASE_DIR / ".env", BASE_DIR.parent / ".env"):
        if candidato.is_file():
            return candidato
    return BASE_DIR / ".env"  # cria aqui se nao existe nenhum


def mascarar(valor: str) -> str:
    if len(valor) <= 8:
        return "*" * len(valor)
    return f"{valor[:4]}...{valor[-4:]} ({len(valor)} chars)"


def definir(env: Path, chave: str, valor: str) -> str:
    """Define uma chave no .env. Devolve 'atualizada' ou 'adicionada'."""
    if not valor or not valor.strip():
        raise SystemExit(f"Valor vazio para {chave}.")
    valor = valor.strip()

    if env.is_file():
        shutil.copy2(env, env.with_suffix(env.suffix + ".bak"))
        linhas = env.read_text(encoding="utf-8", errors="replace").splitlines()
    else:
        linhas = []

    acao = "adicionada"
    novas: list[str] = []
    encontrada = False
    for linha in linhas:
        despido = linha.strip()
        # So mexe em linha de atribuicao real, nunca em comentario.
        if not despido.startswith("#") and "=" in despido:
            nome = despido.split("=", 1)[0].strip()
            if nome == chave:
                novas.append(f"{chave}={valor}")
                encontrada = True
                acao = "atualizada"
                continue
        novas.append(linha)

    if not encontrada:
        if novas and novas[-1].strip():
            novas.append("")
        novas.append(f"{chave}={valor}")

    env.write_text("\n".join(novas).rstrip("\n") + "\n", encoding="utf-8")
    try:
        env.chmod(0o600)  # so o dono le
    except OSError:
        pass
    return acao


def listar(env: Path) -> None:
    if not env.is_file():
        print(f"Nao existe .env em {env}")
        return
    print(f"Chaves em {env}:")
    interessantes = (
        "UPLOAD_POST", "OPENROUTER", "APIMART", "ELEVEN", "FAL", "HIGGSFIELD",
    )
    for linha in env.read_text(encoding="utf-8", errors="replace").splitlines():
        despido = linha.strip()
        if despido.startswith("#") or "=" not in despido:
            continue
        nome, _, valor = despido.partition("=")
        nome = nome.strip()
        marca = "  " if any(p in nome.upper() for p in interessantes) else "  "
        print(f"{marca}{nome:<32} = {mascarar(valor.strip().strip(chr(34)).strip(chr(39)))}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Grava chaves no .env sem apagar as outras.")
    ap.add_argument("--upload-post", metavar="CHAVE", help="UPLOAD_POST_API_KEY")
    ap.add_argument("--upload-post-user", metavar="PERFIL", help="UPLOAD_POST_USER (nome do perfil)")
    ap.add_argument("--openrouter", metavar="CHAVE", help="OPENROUTER_API_KEY")
    ap.add_argument("--definir", nargs=2, metavar=("CHAVE", "VALOR"), help="Qualquer outra variavel")
    ap.add_argument("--ver", action="store_true", help="Lista as chaves (mascaradas)")
    ap.add_argument("--env", help="Caminho do .env (padrao: detecta sozinho)")
    args = ap.parse_args(argv)

    env = Path(args.env).expanduser() if args.env else achar_env()

    if args.ver:
        listar(env)
        return 0

    pares: list[tuple[str, str]] = []
    if args.upload_post:
        pares.append(("UPLOAD_POST_API_KEY", args.upload_post))
    if args.upload_post_user:
        pares.append(("UPLOAD_POST_USER", args.upload_post_user))
    if args.openrouter:
        pares.append(("OPENROUTER_API_KEY", args.openrouter))
    if args.definir:
        pares.append((args.definir[0], args.definir[1]))

    if not pares:
        ap.print_help()
        return 1

    for chave, valor in pares:
        acao = definir(env, chave, valor)
        print(f"{chave} {acao} em {env} -> {mascarar(valor)}")
    print(f"Backup do arquivo anterior: {env}.bak")
    return 0


if __name__ == "__main__":
    sys.exit(main())
