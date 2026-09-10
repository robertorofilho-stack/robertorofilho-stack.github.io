#!/usr/bin/env python3
"""Verifica o índice de memória do Cérebro: toda memória .md tem ponteiro no MEMORY.md?

Uso:  verificar-indice.py [DIR ...] [--indice ARQ] [--estrito] [--quieto] [--listar]
      DIR       pasta(s) de memória. Sem DIR: AUTO-DETECÇÃO — o cofre real do Cérebro fica na
                memória de projeto do Claude Code (no Mac: ~/.claude/projects/-Users-<user>-Claude/memory),
                não em ~/.claude/memory. Candidatos, nesta ordem, todos verificados:
                  $CEREBRO_MEMORIA · ~/.claude/memory · ~/.claude/projects/*/memory ·
                  $CEREBRO_PRIVADO, ~/Claude/cerebro-backup, ~/cerebro-backup (claude-config/memory)
      --indice  índice a checar em vez de DIR/MEMORY.md (só com um DIR) — ex.: a cópia do repo
      --estrito ponteiro quebrado (link sem arquivo) também falha
      --quieto  só imprime quando há problema (para hooks); sem cofre = silêncio, exit 0
      --listar  imprime os cofres detectados, um por linha, e sai

Sai 1 se houver memória ÓRFÃ: arquivo .md sem nenhum ponteiro no índice e fora de REVOGADAS.md.
Os arquivos nunca somem; o que some é o ponteiro — e memória sem ponteiro é invisível.
O `_capacidades.sh` cobre skills/agentes/hooks; este cobre o índice.
"""
import glob
import os
import sys

# regex simples e sem dependência: alvo de link markdown que termina em .md
import re

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


def candidatos(home=None):
    """Cofres de memória existentes nesta máquina (com MEMORY.md), sem repetição."""
    home = home or os.path.expanduser("~")
    brutos = []
    if os.environ.get("CEREBRO_MEMORIA"):
        brutos.append(os.environ["CEREBRO_MEMORIA"])
    brutos.append(os.path.join(home, ".claude", "memory"))
    brutos.extend(sorted(
        os.path.dirname(p) for p in glob.glob(os.path.join(home, ".claude", "projects", "*", "memory", "MEMORY.md"))
    ))
    for base in (os.environ.get("CEREBRO_PRIVADO"),
                 os.path.join(home, "Claude", "cerebro-backup"),
                 os.path.join(home, "cerebro-backup")):
        if base:
            brutos.append(os.path.join(base, "claude-config", "memory"))
    vistos, out = set(), []
    for d in brutos:
        d = os.path.expanduser(d)
        if not os.path.isfile(os.path.join(d, "MEMORY.md")):
            continue
        r = os.path.realpath(d)
        if r in vistos:
            continue
        vistos.add(r)
        out.append(d)
    return out


def main(argv):
    dirs, indice, estrito, quieto, listar = [], None, False, False, False
    it = iter(argv)
    for a in it:
        if a == "--indice":
            indice = next(it, None)
        elif a == "--estrito":
            estrito = True
        elif a == "--quieto":
            quieto = True
        elif a == "--listar":
            listar = True
        elif a.startswith("-"):
            print(f"verificar-indice: opção desconhecida {a}", file=sys.stderr)
            return 64
        else:
            dirs.append(os.path.expanduser(a))

    auto = not dirs
    if auto:
        dirs = candidatos()
    if listar:
        for d in dirs:
            print(d)
        return 0
    if indice and len(dirs) != 1:
        print("verificar-indice: --indice exige exatamente um DIR", file=sys.stderr)
        return 64
    if not dirs:
        if not quieto:
            print("verificar-indice: nenhum cofre de memória encontrado nesta máquina "
                  "(~/.claude/projects/*/memory, ~/.claude/memory, cerebro-backup)")
        return 0

    falhou = False
    for d in dirs:
        if not os.path.isdir(d):
            if not quieto:
                print(f"verificar-indice: pasta não existe: {d}")
            continue
        orfas, quebrados, n_ponteiros, n_arquivos = verificar(d, indice)
        falha = bool(orfas) or (estrito and bool(quebrados))
        falhou = falhou or falha
        if quieto and not falha:
            continue
        print(
            f"indice {indice or os.path.join(d, 'MEMORY.md')}: {n_ponteiros} ponteiros · "
            f"{n_arquivos} memorias · ORFAS: {len(orfas)} · QUEBRADOS: {len(quebrados)}"
        )
        for a in orfas:
            print(f"  ✗ ORFA (arquivo sem ponteiro no indice): {a}")
        for t in quebrados:
            print(f"  ⚠ QUEBRADO (ponteiro sem arquivo): {t}")
        if falha:
            print("✗ involucao no indice: memoria sem ponteiro e invisivel. "
                  "Restaure a linha (git log -p MEMORY.md) — nunca apague o arquivo.")
        elif not quieto:
            print("✓ indice integro: toda memoria tem ponteiro")
    return 1 if falhou else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
