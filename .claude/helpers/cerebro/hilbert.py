#!/usr/bin/env python3
"""HILBERT — memória vetorial no espaço de Hilbert complexo C^d, na versão RIGOROSA (27/09/2026).

Origem: o material colado (H.E.V.E.N./S.E.P.H.I.R.O.T.H./N.E.X.U.S.) usava "espaço de Hilbert", "ressonância",
"interferência" e "memória holográfica" com a matemática errada (revisão do Codex, revisoes/codex-motores-27-09):
fase aleatória SEM relação com o conteúdo, sem operação de ligação (binding), sem limpeza (cleanup), limiar comparado
a uma estatística de escala errada, e energia que premia o erro. Aqui está o que cada ideia é de verdade:

  C^d com <u,v> = Σ u_k·conj(v_k)             é um espaço de Hilbert (dimensão finita ⇒ completo). O nome era legítimo.
  "vetor de onda" de um símbolo               = hipervetor FHRR: fasores e^{iθ_k}, θ ~ U[0,2π), SEMENTE = o símbolo
                                                (determinístico: o mesmo símbolo gera sempre o mesmo vetor).
  quase-ortogonalidade                        para u,v independentes, Re<u,v>/d ~ N(0, 1/(2d)); |<u,v>| segue Rayleigh:
                                                média √(πd)/2, RMS √d  (o 55,9 do meu relatório era o RMS; o Codex certo).
  "fusão de memórias"                         = LIGAR (binding): u⊙v (produto elemento a elemento); inversa EXATA:
                                                u⊙v⊙conj(v) = u. Ligar gera vetor ~ortogonal aos dois fatores.
  "interferência construtiva"                 = AGRUPAR (bundling): Σ u_i — o resultado é parecido com cada parcela.
  "ressonância"                               = similaridade Re<q,m>/d, comparada ao limiar certo para o ruído
                                                (limiar_ruido: z·σ, σ = √(1/(2d)) por unidade).
  "memória holográfica"                       = memória chave→valor  M = Σ k_i⊙v_i ; consulta: M⊙conj(k_j) = v_j + ruído
                                                (Plate 1995; FHRR: Kanerva 2009, Frady et al. 2018).
  "colapso" / limpeza                         = memória associativa de HOPFIELD MODERNA (Ramsauer et al. 2020):
                                                ξ ← X·softmax(β·Re(X^H ξ)) — capacidade exponencial em d; 1 passo basta.
  texto → vetor                               = n-gramas de caracteres codificados por ligação com permutação de posição
                                                (HDC clássico): tolera erro de digitação, flexão, acento.

Honestidade: isto é uma PROJEÇÃO ALEATÓRIA de vetores de n-gramas (Johnson–Lindenstrauss). Nada de quântico, nada de
"consciência". O ganho possível para o Cérebro é um só e é mensurável: casar consulta "suja" (erro de digitação,
palavra cortada, flexão) que o BM25, por palavra exata, perde. Medir antes de adotar: avaliar-hilbert.py.
"""
import hashlib
import math

import numpy as np

D_PADRAO = 1024


# ---------------------------------------------------------------- álgebra FHRR
def simbolo(nome, d=D_PADRAO):
    """Hipervetor de fase unitária, determinístico pelo nome (a 'onda' agora DEPENDE do conteúdo)."""
    semente = int.from_bytes(hashlib.blake2b(f"{d}:{nome}".encode(), digest_size=8).digest(), "little")
    theta = np.random.default_rng(semente).uniform(0.0, 2 * np.pi, d)
    return np.exp(1j * theta).astype(np.complex64)


def ligar(a, b):
    """binding: resultado ~ortogonal a a e a b; inverso exato por conj."""
    return a * b


def desligar(c, b):
    """unbinding: c ⊙ conj(b). Para fasores unitários, desligar(ligar(a,b), b) == a (a menos de arredondamento)."""
    return c * np.conj(b)


def agrupar(vetores, pesos=None):
    """bundling (superposição): soma ponderada. NÃO normaliza a fase — preserva a informação de magnitude."""
    v = np.asarray(vetores)
    if pesos is None:
        return v.sum(axis=0)
    return (np.asarray(pesos, dtype=np.float32)[:, None] * v).sum(axis=0)


def permutar(a, k=1):
    """permutação cíclica ρ^k: codifica POSIÇÃO/ordem (ρ(a) ~ortogonal a a)."""
    return np.roll(a, k)


def sim(a, b):
    """similaridade cosseno real no espaço de Hilbert: Re<a,b>/(‖a‖‖b‖) ∈ [-1, 1]."""
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.real(np.vdot(b, a)) / (na * nb))


def limiar_ruido(d, z=3.0):
    """Limiar de 'ressonância' com significado: para vetores independentes, cos ~ N(0, 1/(2d)).
    z=3 ⇒ falso-positivo ≈ 0,13% (uma cauda). O código colado usava 20 contra |<u,v>| de média ~√(πd)/2 ≈ 49:
    ativava ~88% dos pares ao acaso (medido pelo Codex)."""
    return z * math.sqrt(1.0 / (2 * d))


# ---------------------------------------------------------------- memória chave→valor ("holográfica")
class MemoriaHolografica:
    """M = Σ ligar(chave_i, valor_i). Recuperar = desligar + limpeza contra o dicionário de valores conhecidos."""

    def __init__(self, d=D_PADRAO):
        self.d = d
        self.M = np.zeros(d, dtype=np.complex64)
        self.valores = {}

    def gravar(self, chave, valor):
        k, v = simbolo("k:" + chave, self.d), simbolo("v:" + valor, self.d)
        self.valores[valor] = v
        self.M += ligar(k, v)

    def recuperar(self, chave, beta=None):
        """Devolve (valor, similaridade, confiavel?). confiavel = acima do limiar de ruído."""
        ruidoso = desligar(self.M, simbolo("k:" + chave, self.d))
        nomes = list(self.valores)
        X = np.stack([self.valores[n] for n in nomes])
        s = np.real(X.conj() @ ruidoso) / (self.d * max(1e-9, np.linalg.norm(ruidoso) / math.sqrt(self.d)))
        i = int(np.argmax(s))
        return nomes[i], float(s[i]), bool(s[i] > limiar_ruido(self.d))


def hopfield(X, q, beta=8.0, passos=1):
    """Hopfield moderna (Ramsauer et al. 2020): ξ ← Xᵀ softmax(β·cos(X, ξ)). X: (n, d) padrões guardados.
    Devolve (ξ_final, pesos). Com β alto, converge em 1 passo para o padrão mais próximo (limpeza/"colapso")."""
    Xn = X / np.linalg.norm(X, axis=1, keepdims=True)
    xi = q.astype(np.complex64)
    p = None
    for _ in range(passos):
        c = np.real(Xn.conj() @ xi) / max(1e-9, np.linalg.norm(xi))
        p = np.exp(beta * (c - c.max()))
        p /= p.sum()
        xi = (p[:, None] * Xn).sum(axis=0)
    return xi, p


# ---------------------------------------------------------------- texto → vetor (n-gramas de caracteres)
class CodificadorTexto:
    """Palavra → n-gramas de caracteres com fronteira ('#joelho#' → '#jo','joe',…), cada n-grama codificado por
    ligação de caracteres permutados por posição: ρ⁰(c1)⊙ρ¹(c2)⊙ρ²(c3). Documento = agrupar(n-gramas · peso)."""

    def __init__(self, d=D_PADRAO, n=3):
        self.d, self.n = d, n
        self._letra, self._ngrama = {}, {}

    def letra(self, c):
        if c not in self._letra:
            self._letra[c] = simbolo("c:" + c, self.d)
        return self._letra[c]

    def ngrama(self, g):
        if g not in self._ngrama:
            v = np.ones(self.d, dtype=np.complex64)
            for i, c in enumerate(g):
                v = ligar(v, permutar(self.letra(c), i))
            self._ngrama[g] = v
        return self._ngrama[g]

    def ngramas_da_palavra(self, w):
        s = f"#{w}#"
        return [s[i:i + self.n] for i in range(len(s) - self.n + 1)]

    def contagem(self, pesos_palavras):
        """{palavra: peso} → {n-grama: peso somado}"""
        c = {}
        for w, p in pesos_palavras.items():
            for g in self.ngramas_da_palavra(w):
                c[g] = c.get(g, 0.0) + p
        return c

    def vetor(self, contagem_ngramas, idf=None):
        if not contagem_ngramas:
            return np.zeros(self.d, dtype=np.complex64)
        gs = list(contagem_ngramas)
        pesos = [(1 + math.log(contagem_ngramas[g])) * (idf.get(g, 1.0) if idf else 1.0) for g in gs]
        return agrupar([self.ngrama(g) for g in gs], pesos).astype(np.complex64)


# ---------------------------------------------------------------- limpeza de consulta ("ressonância" que serve)
class LimpezaDeVocabulario:
    """Memória de limpeza (cleanup) de Hopfield sobre o VOCABULÁRIO do Cérebro: palavra da consulta que não existe
    em nenhuma memória (erro de digitação, corte, flexão) é trocada pela palavra guardada mais próxima em C^d
    (n-gramas de caracteres). Palavra que existe não é tocada — consulta limpa fica idêntica (zero regressão).
    Aceita a troca só acima de `minimo` de cosseno (calibrado no gabarito; abaixo disso é ruído, não parentesco)."""

    def __init__(self, vocabulario, d=D_PADRAO, n=3, minimo=0.55, frequencia=None, X=None, minimo_curta=0.50, curta_ate=7):
        self.enc = CodificadorTexto(d=d, n=n)
        self.vocab = sorted(vocabulario)
        self.freq = frequencia or {}
        if X is None:
            X = np.stack([self.enc.vetor(self.enc.contagem({w: 1.0})) for w in self.vocab])
            X = X / np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-9)
        self.X = X.astype(np.complex64)
        self.conj = set(self.vocab)
        self.minimo = minimo
        # palavra curta: 1 letra errada muda fração maior dos n-gramas → corte menor (3 sementes novas: +0,4…+1,2 pt MRR)
        self.minimo_curta, self.curta_ate = minimo_curta, curta_ate

    def corrigir(self, palavra):
        """→ (palavra_corrigida, cosseno) ; devolve a própria palavra se ela existe ou nada passa do mínimo."""
        if palavra in self.conj or len(palavra) < 4:
            return palavra, 1.0
        q = self.enc.vetor(self.enc.contagem({palavra: 1.0}))
        c = np.real(self.X.conj() @ q) / max(1e-9, np.linalg.norm(q))
        i = int(np.argmax(c))
        corte = self.minimo_curta if len(palavra) <= self.curta_ate else self.minimo
        return (self.vocab[i], float(c[i])) if c[i] >= corte else (palavra, float(c[i]))
