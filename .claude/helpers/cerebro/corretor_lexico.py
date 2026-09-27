#!/usr/bin/env python3
"""CORRETOR LÉXICO — conserta a palavra da consulta que não existe em nenhuma memória (27/09/2026).

Como chegou aqui (medido, não opinado — avaliar-hilbert.py e revisoes do conselho de 27/09):
  - "limpeza" pelo espaço de Hilbert (n-gramas em C^256, Hopfield/argmax): MRR +0,047 em consulta suja/flexionada, 21 ms;
  - o conselho (GPT, Grok, Gemini, DeepSeek — 4/4 AJUSTAR) mandou comparar com um corretor "burro" de distância de
    edição. Resultado, 954 consultas perturbadas (3 sementes que nada viu): distância de edição +0,084, 4,6 ms;
    Hilbert − edição = −0,037 [−0,050, −0,025]; edição + Hilbert = +0,002 (ruído). O burro ganhou. Fica ele.
Método: SymSpell (Garbe 2012) — índice de DELEÇÕES até k; candidatos conferidos pela distância de Damerau-Levenshtein
(transposição adjacente conta 1). k=1 para palavra ≤5 letras, 2 acima. Empate: menor distância, depois mais frequente.
Só biblioteca padrão. Palavra que existe no vocabulário NUNCA é tocada (consulta limpa fica idêntica).
"""
import itertools


def dl(a, b, teto=3):
    """Damerau-Levenshtein (alinhamento ótimo de cadeias). Para cedo acima de `teto`."""
    if abs(len(a) - len(b)) > teto:
        return teto + 1
    ant2, ant = None, list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        cur = [i] + [0] * len(b)
        for j in range(1, len(b) + 1):
            custo = a[i - 1] != b[j - 1]
            cur[j] = min(ant[j] + 1, cur[j - 1] + 1, ant[j - 1] + custo)
            if ant2 is not None and i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                cur[j] = min(cur[j], ant2[j - 2] + 1)
        if min(cur) > teto:
            return teto + 1
        ant2, ant = ant, cur
    return ant[-1]


def delecoes(w, k):
    out = {w}
    borda = {w}
    for _ in range(k):
        nova = set()
        for x in borda:
            for i in range(len(x)):
                nova.add(x[:i] + x[i + 1:])
        out |= nova
        borda = nova
    return out


class Corretor:
    def __init__(self, frequencia, kmax=2):
        self.freq = dict(frequencia)
        self.kmax = kmax
        self.indice = {}
        for w in self.freq:
            for d in delecoes(w, kmax):
                self.indice.setdefault(d, []).append(w)

    def k_para(self, w):
        return 1 if len(w) <= 5 else self.kmax

    def corrigir(self, w):
        """→ (palavra, distância). Palavra conhecida ou sem candidato: devolve ela mesma."""
        if w in self.freq or len(w) < 4:
            return w, 0
        k = self.k_para(w)
        cand = set()
        for d in delecoes(w, k):
            cand.update(self.indice.get(d, ()))
        melhor = None
        for c in cand:
            dist = dl(w, c, k)
            if dist <= k:
                chave = (dist, -self.freq[c], c)
                if melhor is None or chave < melhor[0]:
                    melhor = (chave, c, dist)
        return (melhor[1], melhor[2]) if melhor else (w, None)
