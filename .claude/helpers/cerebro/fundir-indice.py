#!/usr/bin/env python3
"""Funde dois MEMORY.md por UNIÃO POR LINK — nenhum ponteiro some, nunca; e o script
RECUSA gravar se a fusão perderia qualquer um.

Uso:  fundir-indice.py [--simular] [--simular-perda ALVO.md] <LOCAL> <REPO>
      Escreve a fusão nos DOIS (sincronizar.sh e sync-backup.sh passam o local primeiro).
      --simular           só relata; não grava nada
      --simular-perda X   teste do guarda: tira X da saída antes da verificação → exit 2, nada gravado

v4 (10/09/2026 — conserto da involução flagrada pelo MacBook: 244 → 240 links em 4 minutos):
1. A unidade de fusão é o LINK, não a linha. Em v3 "o local vence a linha" descartava os links
   AGRUPADOS na mesma linha do outro lado — ex.: `[LEIS](leis.md) · [parcela](lei-parcela.md)`
   perdia `lei-parcela.md` quando o local só tinha `[LEIS](leis.md)`. Reproduzido com o índice
   real: local pré-união (225) + repo unido (244) → v3 gravava 239; v4 grava 244.
2. Texto: o local vence quando cobre os mesmos links. Se a linha da base tem links a mais, ela
   vence (superset). Se cada lado tem link que o outro não tem, as DUAS ficam — duplicata visível
   vale mais que ponteiro perdido.
3. Guarda pós-condição, independente da contabilidade da fusão: todo link de qualquer entrada
   (menos REVOGADAS) tem que estar no texto de saída. Se não estiver: NÃO grava, lista os
   faltantes em stderr e sai com 2. Os dois índices ficam exatamente como estavam.
4. Idempotente: fundir(X, X) == X. O cabeçalho "RECUPERADAS DO OUTRO MAC" não se repete.
5. Escrita atômica (arquivo temporário + rename): um sync morto no meio nunca deixa índice pela metade.
6. Mantido de v3: REVOGADAS.md (mesma pasta do LOCAL) — alvo banido nunca ressuscita;
   erro de gravação = exit 1 + stderr, nunca silêncio.
"""
import os
import re
import sys

LINK = re.compile(r"\]\(([^)]+\.md)\)")
CABECALHO_RECUPERADAS = "## RECUPERADAS DO OUTRO MAC"


def ler(p):
    try:
        with open(p, encoding="utf-8") as f:
            return f.read().splitlines()
    except Exception:
        return []


def ler_revogadas(local_p):
    rev = set()
    rev_p = os.path.join(os.path.dirname(local_p) or ".", "REVOGADAS.md")
    for l in ler(rev_p):
        l = l.strip().lstrip("-").strip()
        if l and not l.startswith("#") and l.endswith(".md"):
            rev.add(l)
    return rev


def links(linha, revogadas=frozenset()):
    """alvos vivos (não revogados) de uma linha, na ordem, sem repetição"""
    vistos, out = set(), []
    for t in LINK.findall(linha):
        if t not in revogadas and t not in vistos:
            vistos.add(t)
            out.append(t)
    return out


def alvos_de(linhas, revogadas=frozenset()):
    s = set()
    for l in linhas:
        s.update(links(l, revogadas))
    return s


def mapa(linhas):
    """alvo → primeira linha que o contém"""
    m = {}
    for l in linhas:
        for t in LINK.findall(l):
            m.setdefault(t, l)
    return m


def fundir(ll, lr, revogadas=frozenset()):
    """Fusão pura. Devolve (linhas_de_saida, relatorio). Não toca em disco."""
    revogadas = frozenset(revogadas)

    def banida(l):
        return bool(LINK.findall(l)) and not links(l, revogadas)

    m_local, m_repo = mapa(ll), mapa(lr)
    base = ll if len(m_local) >= len(m_repo) else lr

    saida, tem, emitidas = [], set(), set()
    rel = {"preservadas_local": 0, "duplicadas_por_seguranca": 0, "revogadas": 0, "recuperadas": 0}

    def emitir(l):
        if l in emitidas:
            return
        saida.append(l)
        emitidas.add(l)
        tem.update(links(l, revogadas))

    for l in base:
        todos = LINK.findall(l)
        if not todos:
            saida.append(l)  # estrutura: títulos, vazias, prosa
            continue
        if banida(l):
            rel["revogadas"] += 1
            continue
        sb = set(links(l, revogadas))
        if sb <= tem:
            continue  # tudo já coberto → linha redundante
        pref = m_local.get(todos[0], l)  # texto do LOCAL para esta memória
        if banida(pref):
            pref = l
        sl = set(links(pref, revogadas))
        if sl >= sb:  # local cobre tudo → texto do local vence
            if pref != l:
                rel["preservadas_local"] += 1
            emitir(pref)
        elif sb > sl:  # base tem links a mais → linha mais rica vence
            emitir(l)
        else:  # cada lado tem link que o outro não tem → as duas ficam
            rel["duplicadas_por_seguranca"] += 1
            emitir(pref)
            emitir(l)

    recuperadas = []
    for fonte in (ll, lr):  # local primeiro: seu texto vence
        for l in fonte:
            if not LINK.findall(l) or banida(l) or l in emitidas:
                continue
            if any(t not in tem for t in links(l, revogadas)):
                recuperadas.append(l)
                emitidas.add(l)
                tem.update(links(l, revogadas))
    if recuperadas:
        if CABECALHO_RECUPERADAS not in saida:
            if saida and saida[-1].strip():
                saida.append("")
            saida.append(CABECALHO_RECUPERADAS)
        saida.extend(recuperadas)
        rel["recuperadas"] = len(recuperadas)

    rel["total"] = len(tem)
    return saida, rel


def faltantes(saida, ll, lr, revogadas=frozenset()):
    """Guarda independente: re-lê os links do TEXTO de saída e compara com as entradas."""
    return sorted(alvos_de(ll + lr, revogadas) - alvos_de(saida, revogadas))


def gravar_atomico(p, txt):
    d = os.path.dirname(p) or "."
    os.makedirs(d, exist_ok=True)
    tmp = os.path.join(d, f".{os.path.basename(p)}.tmp-{os.getpid()}")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(txt)
    os.replace(tmp, p)


def main(argv):
    simular, simular_perda, pos = False, None, []
    it = iter(argv)
    for a in it:
        if a == "--simular":
            simular = True
        elif a == "--simular-perda":
            simular_perda = next(it, None)
        elif a.startswith("-"):
            print(f"fundir-indice: opção desconhecida {a}", file=sys.stderr)
            return 64
        else:
            pos.append(a)
    if len(pos) != 2:
        print("uso: fundir-indice.py [--simular] [--simular-perda ALVO.md] <LOCAL> <REPO>", file=sys.stderr)
        return 64
    local_p, repo_p = pos
    ll, lr = ler(local_p), ler(repo_p)
    if not ll and not lr:
        return 0

    revogadas = ler_revogadas(local_p)
    saida, rel = fundir(ll, lr, revogadas)
    if simular_perda:  # só para provar que o guarda dispara
        saida = [l for l in saida if f"]({simular_perda})" not in l]

    perdidos = faltantes(saida, ll, lr, revogadas)
    if perdidos:
        print(
            f"fundir-indice RECUSOU GRAVAR: {len(perdidos)} ponteiro(s) sumiriam na fusão: "
            + " ".join(perdidos),
            file=sys.stderr,
        )
        print("fundir-indice: NADA foi gravado — os dois índices continuam como estavam.", file=sys.stderr)
        return 2

    print(
        f"indice fundido: {rel['total']} memorias | +{rel['recuperadas']} recuperadas | "
        f"{rel['preservadas_local']} preservadas do local | "
        f"{rel['duplicadas_por_seguranca']} duplicadas por seguranca | "
        f"{rel['revogadas']} revogadas filtradas"
        + (" | SIMULACAO: nada gravado" if simular else "")
    )
    if simular:
        return 0

    txt = "\n".join(saida).rstrip("\n") + "\n"
    erros = 0
    for p in (local_p, repo_p):
        try:
            gravar_atomico(p, txt)
        except Exception as e:
            erros += 1
            print(f"fundir-indice ERRO gravando {p}: {e}", file=sys.stderr)
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
