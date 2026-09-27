#!/usr/bin/env python3
"""AVALIAR-HILBERT — o canal do espaço de Hilbert (hilbert.py) melhora a busca do Cérebro? Medido, não opinado.

Gabarito: o mesmo do memoria_viva (ganchos do MEMORY.md → arquivo). Três versões de cada consulta:
  limpa      — como está (favorece o BM25: os ganchos usam as palavras da memória)
  suja       — erro de digitação, letra faltando, palavra cortada (semente fixa: reprodutível)
  flexionada — plural/singular e troca de sufixo (-ção/-ções, -ar/-ou, -ico/-ica…)
Canais: bm25 · hilbert (n-gramas de caracteres em C^d) · trigrama exato (o limite que a projeção aproxima) ·
fusão RRF (bm25 + hilbert). Métricas: recall@1, recall@5, MRR@10.
Uso: avaliar-hilbert.py [--mem PASTA] [--d 1024] [--semente 7]
"""
import argparse
import importlib.util
import math
import os
import random
import re
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))


def mod(nome):
    s = importlib.util.spec_from_file_location(nome.replace("-", "_"), os.path.join(AQUI, nome + ".py"))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


mv, hb = mod("memoria_viva"), mod("hilbert")


def sujar(q, rng):
    out = []
    for w in q.split():
        if len(w) >= 5 and rng.random() < 0.6:
            op = rng.choice(["troca", "apaga", "corta"])
            i = rng.randrange(1, len(w) - 2)
            if op == "troca":
                w = w[:i] + w[i + 1] + w[i] + w[i + 2:]
            elif op == "apaga":
                w = w[:i] + w[i + 1:]
            else:
                w = w[:max(4, len(w) - 3)]
        out.append(w)
    return " ".join(out)


SUFIXOS = [("ções", "ção"), ("ção", "ções"), ("ais", "al"), ("al", "ais"), ("ar", "ou"), ("ado", "ar"),
           ("ica", "ico"), ("ico", "ica"), ("ia", "ias"), ("es", "e"), ("os", "o"), ("as", "a"), ("o", "os"), ("a", "as")]


def flexionar(q, rng):
    out = []
    for w in q.split():
        if len(w) >= 5 and rng.random() < 0.6:
            for s, t in SUFIXOS:
                if w.lower().endswith(s):
                    w = w[: -len(s)] + t
                    break
        out.append(w)
    return " ".join(out)


class CanalHilbert:
    def __init__(self, docs, d, n=3):
        self.enc = hb.CodificadorTexto(d=d, n=n)
        self.ids = list(docs)
        cont = [self.enc.contagem(docs[i].tf) for i in self.ids]
        df = {}
        for c in cont:
            for g in c:
                df[g] = df.get(g, 0) + 1
        N = len(cont)
        self.idf = {g: math.log(1 + N / f) for g, f in df.items()}
        self.cont = cont
        M = np.stack([self.enc.vetor(c, self.idf) for c in cont])
        self.M = M / np.maximum(np.linalg.norm(M, axis=1, keepdims=True), 1e-9)

    def ranquear(self, consulta, k=10):
        q = self.enc.vetor(self.enc.contagem({w: 1.0 for w in mv.tokens(consulta)}), self.idf)
        if not np.any(q):
            return []
        s = np.real(self.M.conj() @ q) / np.linalg.norm(q)
        o = np.argsort(-s)[:k]
        return [self.ids[i] for i in o]

    def ranquear_exato(self, consulta, k=10):
        """trigrama tf-idf com cosseno EXATO (sem projeção) — o que o vetor de Hilbert aproxima."""
        qc = self.enc.contagem({w: 1.0 for w in mv.tokens(consulta)})
        qv = {g: (1 + math.log(c)) * self.idf.get(g, 0) for g, c in qc.items()}
        nq = math.sqrt(sum(v * v for v in qv.values())) or 1
        sc = []
        for i, c in enumerate(self.cont):
            dv = {g: (1 + math.log(x)) * self.idf[g] for g, x in c.items()}
            nd = math.sqrt(sum(v * v for v in dv.values())) or 1
            sc.append(sum(v * dv.get(g, 0) for g, v in qv.items()) / (nq * nd))
        o = np.argsort(-np.array(sc))[:k]
        return [self.ids[i] for i in o]


def rrf(*listas, k=60):
    s = {}
    for l in listas:
        for r, x in enumerate(l):
            s[x] = s.get(x, 0) + 1 / (k + r + 1)
    return [x for x, _ in sorted(s.items(), key=lambda t: -t[1])]


def metricas(rankings, casos):
    r1 = r5 = rr = 0.0
    for ids, (_, alvo) in zip(rankings, casos):
        ids = ids[:10]
        r1 += ids[:1] == [alvo]
        r5 += alvo in ids[:5]
        rr += 1 / (ids.index(alvo) + 1) if alvo in ids else 0
    n = len(casos) or 1
    return round(r1 / n, 3), round(r5 / n, 3), round(rr / n, 3)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--mem", default=None)
    ap.add_argument("--d", type=int, default=1024)
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--semente", type=int, default=7)
    ap.add_argument("--exato", action="store_true", help="também o trigrama exato (lento)")
    ap.add_argument("--minimos", type=float, nargs="+", default=[0.45, 0.55, 0.65])
    a = ap.parse_args(argv)
    pastas = [a.mem] if a.mem else mv.pastas_padrao()
    docs = mv.carregar(pastas)
    gab = [(q, al) for q, al in mv.gabarito_do_indice(pastas[0]) if al in docs and mv.tokens(q)]
    canal = CanalHilbert(docs, a.d, a.n)
    vocab = {}
    for dd in docs.values():
        for w, c in dd.tf.items():
            vocab[w] = vocab.get(w, 0) + c
    limpa = {m: hb.LimpezaDeVocabulario(vocab, d=a.d, n=a.n, minimo=m) for m in a.minimos}

    def corrigida(q, lim):
        return " ".join(lim.corrigir(w)[0] for w in mv.tokens(q))
    rng = random.Random(a.semente)
    variantes = {"limpa": gab, "suja": [(sujar(q, rng), al) for q, al in gab],
                 "flexionada": [(flexionar(q, rng), al) for q, al in gab]}
    print(f"memórias {len(docs)} · casos {len(gab)} · d={a.d} · n-grama={a.n} · semente={a.semente}")
    print(f"{'variante':11} {'canal':22} {'r@1':>6} {'r@5':>6} {'MRR':>6}")
    res = {}
    for nome, casos in variantes.items():
        bm = [[x for x, _ in sorted(mv.bm25(docs, q).items(), key=lambda t: -t[1])][:10] for q, _ in casos]
        hi = [canal.ranquear(q) for q, _ in casos]
        fu = [rrf(b, h) for b, h in zip(bm, hi)]
        linhas = {"bm25 (atual)": bm, "hilbert (C^d, n-gramas)": hi, "fusão RRF bm25+hilbert": fu}
        for m, lim in limpa.items():
            linhas[f"bm25 + limpeza ≥{m}"] = [[x for x, _ in sorted(mv.bm25(docs, corrigida(q, lim)).items(),
                                                                   key=lambda t: -t[1])][:10] for q, _ in casos]
        if a.exato:
            linhas["trigrama exato"] = [canal.ranquear_exato(q) for q, _ in casos]
        for canal_nome, rk in linhas.items():
            m = metricas(rk, casos)
            res[(nome, canal_nome)] = m
            print(f"{nome:11} {canal_nome:22} {m[0]:6} {m[1]:6} {m[2]:6}")
    return res


if __name__ == "__main__":
    main()
    sys.exit(0)
