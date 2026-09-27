#!/usr/bin/env python3
"""MERGE-INDICE v2 — fusão de 3 vias do MEMORY.md (driver de merge do git e função usada pelo sync-memoria.py).

v1 (27/09, tarde) resolvia o arquivo inteiro com a lógica por link. O Codex reproduziu 4 defeitos com git real
(revisoes/codex-migracao-memoria-27-09): retirada lida da REVOGADAS.md NÃO commitada; link duplicado com uma cópia
editada apagado; prosa editada de um lado sumindo; retirada parcial de linha agrupada ressuscitando.

v2 (27/09, noite):
  1. o GIT faz a fusão de 3 vias linha a linha (`git merge-file --diff3`) — o que só um lado mudou, vale sem discussão;
  2. só os TRECHOS EM CONFLITO passam pela lógica por link (resolver_trecho): o que B mudou e A deixou como estava,
     vale o de B; os dois mudaram a mesma entrada → A (quem está sincronizando) vence o texto; entrada nova entra;
  3. RETIRADA = link que um lado tirou e que o outro NÃO tocou em NENHUMA das linhas que o contêm (multiconjunto);
  4. guarda final: todo link de A ∪ B, menos retiradas e revogadas COMMITADAS (HEAD), tem de estar na saída — senão
     sai 1 e o git marca conflito (o sync aborta; nada é gravado errado).
Driver: git config merge.indice-cerebro.driver "python3 <repo>/claude-config/helpers/cerebro/merge-indice.py %O %A %B"
"""
import collections
import difflib
import os
import re
import subprocess
import sys
import tempfile

LINK = re.compile(r"\]\(([^)\s]+\.md)\)")
MARCA_A, MARCA_O, MARCA_S, MARCA_B = "<<<<<<< A", "||||||| O", "=======", ">>>>>>> B"


def links(linha, fora=frozenset()):
    vistos, out = set(), []
    for t in LINK.findall(linha):
        if t not in fora and t not in vistos:
            vistos.add(t)
            out.append(t)
    return out


def alvos(linhas, fora=frozenset()):
    return {t for l in linhas for t in links(l, fora)}


def linhas_de(linhas):
    """link → multiconjunto (lista ordenada) de TODAS as linhas que o contêm"""
    m = collections.defaultdict(list)
    for l in linhas:
        for t in set(LINK.findall(l)):
            m[t].append(l)
    return {t: sorted(v) for t, v in m.items()}


def retiradas(o, a, b):
    """links que um lado tirou e o outro não tocou (nenhuma linha com o link mudou desse outro lado)"""
    lo, la, lb = linhas_de(o), linhas_de(a), linhas_de(b)
    ret = set()
    for t, lin_o in lo.items():
        if t not in la and lb.get(t) == lin_o:
            ret.add(t)
        if t not in lb and la.get(t) == lin_o:
            ret.add(t)
    return ret


def resolver_trecho(o, a, b, ret):
    """Conflito num trecho: parte de A e aplica as mudanças de B que não colidem com mudanças de A."""
    res = list(a)
    mudadas_a = [x for x in a if x not in o]
    prosa_mudada_a = any(x not in o and not LINK.findall(x) and x.strip() for x in a)
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, o, b, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        seg_o, seg_b = o[i1:i2], b[j1:j2]
        pos = None
        for l in seg_o:                           # linha de O que B mudou/tirou e A deixou igual → sai
            if l in res:
                k = res.index(l)
                pos = k if pos is None else min(pos, k)
                res.pop(k)
        novas = []
        for l in seg_b:
            if l in res or l in novas:
                continue
            vivos = set(links(l)) - ret
            if LINK.findall(l) and not vivos:
                continue                          # só link retirado: não volta
            colide = [x for x in mudadas_a if vivos & set(links(x))]
            if colide:                            # os dois mudaram a mesma entrada: A vence, mas nenhum link some
                if vivos - alvos(res):
                    novas.append(l)
                continue
            if not vivos and l.strip() and pos is None and prosa_mudada_a:
                continue                          # prosa mudada pelos dois no mesmo ponto: A vence
            novas.append(l)
        if pos is None:                           # sem âncora em A: logo depois da linha de O que precede o trecho
            ant = o[i1 - 1] if i1 > 0 else None
            pos = res.index(ant) + 1 if ant in res else len(res)
        res[pos:pos] = novas
    return res


def diff3(o, a, b):
    """git merge-file --diff3; devolve lista de itens: str (linha resolvida) ou (o_h, a_h, b_h)."""
    with tempfile.TemporaryDirectory() as d:
        ps = []
        for nome, linhas in (("a", a), ("o", o), ("b", b)):
            p = os.path.join(d, nome)
            with open(p, "w", encoding="utf-8") as f:
                f.write("".join(l + "\n" for l in linhas))
            ps.append(p)
        r = subprocess.run(["git", "merge-file", "-p", "--diff3", "-L", "A", "-L", "O", "-L", "B", *ps],
                           capture_output=True, text=True)
        if r.returncode < 0 or (r.returncode > 0 and MARCA_A not in r.stdout):
            raise RuntimeError(f"git merge-file falhou: {r.returncode} {r.stderr}")
        saida = r.stdout.split("\n")
        if saida and saida[-1] == "":
            saida.pop()
    itens, i = [], 0
    while i < len(saida):
        l = saida[i]
        if l == MARCA_A:
            a_h, o_h, b_h = [], [], []
            i += 1
            while saida[i] != MARCA_O:
                a_h.append(saida[i]); i += 1
            i += 1
            while saida[i] != MARCA_S:
                o_h.append(saida[i]); i += 1
            i += 1
            while saida[i] != MARCA_B:
                b_h.append(saida[i]); i += 1
            itens.append((o_h, a_h, b_h))
        else:
            itens.append(l)
        i += 1
    return itens


def mesclar(o, a, b, revogadas=frozenset()):
    """o, a, b: listas de linhas (sem \\n). Devolve (saida, faltantes)."""
    ret = retiradas(o, a, b)
    saida = []
    for it in diff3(o, a, b):
        if isinstance(it, tuple):
            saida.extend(resolver_trecho(*it, ret))
        else:
            saida.append(it)
    exigidos = (alvos(a) | alvos(b)) - ret - set(revogadas)
    return saida, sorted(exigidos - alvos(saida))


def ler(p):
    try:
        with open(p, encoding="utf-8") as f:
            return f.read().splitlines()
    except OSError:
        return []


def revogadas_commitadas():
    """REVOGADAS.md do HEAD — nunca da árvore viva (achado 5 do Codex)."""
    r = subprocess.run(["git", "show", "HEAD:claude-config/memory/REVOGADAS.md"], capture_output=True, text=True)
    rev = set()
    for l in (r.stdout if r.returncode == 0 else "").splitlines():
        l = l.strip().lstrip("-").strip()
        if l and not l.startswith("#") and l.endswith(".md"):
            rev.add(l)
    return rev


def main(argv):
    if len(argv) < 3:
        print(__doc__, file=sys.stderr)
        return 2
    p_o, p_a, p_b = argv[:3]
    saida, faltam = mesclar(ler(p_o), ler(p_a), ler(p_b), revogadas_commitadas())
    if faltam:
        print(f"merge-indice RECUSOU: {len(faltam)} ponteiro(s) sumiriam: {faltam[:6]}", file=sys.stderr)
        return 1
    with open(p_a, "w", encoding="utf-8") as f:
        f.write("".join(l + "\n" for l in saida))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
