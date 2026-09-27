#!/usr/bin/env python3
"""MERGE-INDICE — driver de merge do git para o MEMORY.md (27/09/2026). Fusão de 3 VIAS de verdade, por link.

Desde a migração, a memória viva mora DENTRO do repositório (a pasta de memória de cada Mac é um link simbólico para
claude-config/memory). Quem junta o que os dois Macs fizeram é o git — e o git conhece o ANCESTRAL comum (%O). É o
que faltou a todos os consertos de 30/08 a 27/09: a fusão de 2 vias não sabia quem tinha mudado o quê.

Regras (por memória = por link):
  - um lado tirou a memória do índice e o outro NÃO mexeu na linha dela → a retirada vale (compactação/revogação);
  - um lado mudou o texto e o outro não → a mudança vale (fundir-indice v5 com ancestral);
  - os dois mudaram → o nosso lado (quem está sincronizando) vence o texto; nenhum link some;
  - memória nova de qualquer lado entra;
  - guarda: todo link de A ∪ B, menos as retiradas aceitas e as revogadas, tem de estar na saída. Senão sai 1
    (o git marca conflito e o sync aborta o merge — nada é gravado errado).
Configuração (feita pelo sincronizar.sh e pelo sync-backup.sh a cada execução):
  git config merge.indice-cerebro.driver "python3 <repo>/claude-config/helpers/cerebro/merge-indice.py %O %A %B"
  .gitattributes: claude-config/memory/MEMORY.md merge=indice-cerebro
"""
import importlib.util
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location("fundir_indice", os.path.join(AQUI, "fundir-indice.py"))
fi = importlib.util.module_from_spec(_s)
_s.loader.exec_module(fi)


def mesclar(o, a, b, revogadas=frozenset()):
    """o, a, b: listas de linhas. Devolve (saida, faltantes)."""
    mo, ma, mb = fi.mapa(o), fi.mapa(a), fi.mapa(b)
    retiradas = set()
    for t, linha_o in mo.items():
        if t not in ma and t in mb and mb[t] == linha_o:
            retiradas.add(t)                     # A tirou, B não mexeu
        if t not in mb and t in ma and ma[t] == linha_o:
            retiradas.add(t)                     # B tirou, A não mexeu

    def sem_retiradas(linhas):
        out = []
        for l in linhas:
            vivos = fi.links(l, revogadas)
            if vivos and all(t in retiradas for t in vivos):
                continue
            out.append(l)
        return out

    a2, b2, o2 = sem_retiradas(a), sem_retiradas(b), sem_retiradas(o)
    saida, _ = fi.fundir(a2, b2, revogadas, frozenset(), ancestral=o2)
    exigidos = (fi.alvos_de(a, revogadas) | fi.alvos_de(b, revogadas)) - retiradas
    return saida, sorted(exigidos - fi.alvos_de(saida, revogadas))


def main(argv):
    if len(argv) < 3:
        print(__doc__, file=sys.stderr)
        return 2
    p_o, p_a, p_b = argv[:3]
    rev = fi.ler_revogadas(os.path.join(os.getcwd(), "claude-config", "memory", "MEMORY.md"))
    saida, faltam = mesclar(fi.ler(p_o), fi.ler(p_a), fi.ler(p_b), rev)
    if faltam:
        print(f"merge-indice RECUSOU: {len(faltam)} ponteiro(s) sumiriam: {faltam[:6]}", file=sys.stderr)
        return 1
    with open(p_a, "w", encoding="utf-8") as f:     # o git lê o resultado de %A
        f.write("\n".join(saida).rstrip("\n") + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
