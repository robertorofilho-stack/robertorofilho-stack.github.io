#!/usr/bin/env python3
"""Verifica o índice de memória do Cérebro: toda memória .md tem ponteiro no MEMORY.md?

Uso:  verificar-indice.py [DIR] [--indice ARQ] [--estrito] [--quieto]
      DIR      pasta de memórias (padrão: ~/.claude/memory)
      --indice índice a checar (padrão: DIR/MEMORY.md) — permite checar a cópia do repo
      --estrito ponteiro quebrado (link sem arquivo) também falha
      --quieto  só imprime quando há problema (para hooks)

Sai 1 se houver memória ÓRFÃ: arquivo .md em DIR sem nenhum ponteiro no índice e fora de
REVOGADAS.md. Os arquivos nunca somem; o que some é o ponteiro — e memória sem ponteiro é
invisível. O `_capacidades.sh` cobre skills/agentes/hooks; este cobre o índice.
"""
import os
import re
import sys

LINK = re.compile(r"\]\(([^)]+\.md)\)")
IGNORAR = {"MEMORY.md", "REVOGADAS.md"}


def ler(p):
    try:
        with open(p, encoding="utf-8") as f:
            return f.read().splitlines()
    except Exception:
        return []


def revogadas(d):
    out = set()
    for l in ler(os.path.join(d, "REVOGADAS.md")):
        l = l.strip().lstrip("-").strip()
        if l and not l.startswith("#") and l.endswith(".md"):
            out.add(l)
    return out


def arquivos(d):
    out = set()
    for raiz, pastas, nomes in os.walk(d):
        pastas[:] = [p for p in pastas if not p.startswith(".")]
        for n in nomes:
            if n.endswith(".md") and not n.startswith("."):
                rel = os.path.relpath(os.path.join(raiz, n), d)
                if rel not in IGNORAR:
                    out.add(rel)
    return out


def verificar(d, indice=None):
    """Devolve (orfas, quebrados, n_ponteiros, n_arquivos)."""
    indice = indice or os.path.join(d, "MEMORY.md")
    alvos = set()
    for l in ler(indice):
        alvos.update(LINK.findall(l))
    arqs = arquivos(d)
    rev = revogadas(d)
    orfas = sorted(a for a in arqs - alvos if os.path.basename(a) not in rev and a not in rev)
    quebrados = sorted(
        t for t in alvos
        if not os.path.exists(os.path.normpath(os.path.join(d, t)))
    )
    return orfas, quebrados, len(alvos), len(arqs)


def main(argv):
    d, indice, estrito, quieto = None, None, False, False
    it = iter(argv)
    for a in it:
        if a == "--indice":
            indice = next(it, None)
        elif a == "--estrito":
            estrito = True
        elif a == "--quieto":
            quieto = True
        elif a.startswith("-"):
            print(f"verificar-indice: opção desconhecida {a}", file=sys.stderr)
            return 64
        else:
            d = a
    d = os.path.expanduser(d or "~/.claude/memory")
    if not os.path.isdir(d):
        if not quieto:
            print(f"verificar-indice: pasta não existe: {d}")
        return 0
    orfas, quebrados, n_ponteiros, n_arquivos = verificar(d, indice)
    falha = bool(orfas) or (estrito and bool(quebrados))
    if quieto and not falha:
        return 0
    print(
        f"indice {indice or os.path.join(d, 'MEMORY.md')}: {n_ponteiros} ponteiros · "
        f"{n_arquivos} memorias · ORFAS: {len(orfas)} · QUEBRADOS: {len(quebrados)}"
    )
    for a in orfas:
        print(f"  ✗ ORFA (arquivo sem ponteiro no indice): {a}")
    for t in quebrados:
        print(f"  ⚠ QUEBRADO (ponteiro sem arquivo): {t}")
    if falha:
        print("✗ involucao no indice: memoria sem ponteiro e invisivel. Restaure a linha (git log -p MEMORY.md) — nunca apague o arquivo.")
        return 1
    if not quieto:
        print("✓ indice integro: toda memoria tem ponteiro")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
