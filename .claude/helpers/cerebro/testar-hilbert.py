#!/usr/bin/env python3
"""Testes do hilbert.py — as propriedades matemáticas que o material colado alegava e não tinha, agora verificadas."""
import importlib.util
import math
import os
import unittest

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location("hilbert", os.path.join(AQUI, "hilbert.py"))
hb = importlib.util.module_from_spec(_s)
_s.loader.exec_module(hb)
D = 1024


class Algebra(unittest.TestCase):
    def test_simbolo_depende_do_conteudo_e_e_deterministico(self):
        self.assertTrue(np.array_equal(hb.simbolo("joelho", D), hb.simbolo("joelho", D)))
        self.assertLess(abs(hb.sim(hb.simbolo("joelho", D), hb.simbolo("ombro", D))), hb.limiar_ruido(D))
        self.assertTrue(np.allclose(np.abs(hb.simbolo("x", D)), 1.0, atol=1e-5))        # fasor unitário

    def test_ligar_tem_inversa_exata_e_gera_vetor_novo(self):
        a, b = hb.simbolo("a", D), hb.simbolo("b", D)
        c = hb.ligar(a, b)
        self.assertTrue(np.allclose(hb.desligar(c, b), a, atol=1e-5))
        self.assertLess(abs(hb.sim(c, a)), hb.limiar_ruido(D))                           # ~ortogonal aos fatores

    def test_agrupar_parece_com_as_parcelas(self):
        a, b, z = hb.simbolo("a", D), hb.simbolo("b", D), hb.simbolo("z", D)
        s = hb.agrupar([a, b])
        self.assertGreater(hb.sim(s, a), 0.6)
        self.assertLess(abs(hb.sim(s, z)), hb.limiar_ruido(D))

    def test_permutar_codifica_posicao(self):
        a = hb.simbolo("a", D)
        self.assertLess(abs(hb.sim(hb.permutar(a), a)), hb.limiar_ruido(D))


class Estatistica(unittest.TestCase):
    def test_ruido_segue_rayleigh(self):
        """|<u,v>| de fasores independentes: média √(πd)/2, RMS √d. (O relatório antigo confundiu RMS com média.)"""
        v = np.array([abs(np.vdot(hb.simbolo(f"x{i}", D), hb.simbolo(f"y{i}", D))) for i in range(1500)])
        self.assertAlmostEqual(v.mean() / (math.sqrt(math.pi * D) / 2), 1.0, delta=0.05)
        self.assertAlmostEqual(math.sqrt((v ** 2).mean()) / math.sqrt(D), 1.0, delta=0.05)

    def test_limiar_de_3_sigma_da_poucos_falsos_positivos(self):
        c = np.array([hb.sim(hb.simbolo(f"p{i}", D), hb.simbolo(f"q{i}", D)) for i in range(3000)])
        self.assertLess((c > hb.limiar_ruido(D)).mean(), 0.01)


class Memorias(unittest.TestCase):
    def test_memoria_chave_valor_dentro_da_capacidade(self):
        m = hb.MemoriaHolografica(D)
        for i in range(50):
            m.gravar(f"k{i}", f"v{i}")
        acertos = sum(m.recuperar(f"k{i}")[0] == f"v{i}" for i in range(50))
        self.assertGreaterEqual(acertos, 49)

    def test_memoria_chave_valor_satura_acima_da_capacidade(self):
        """honestidade: um vetor único NÃO guarda o Cérebro inteiro (~dezenas de pares em d=1024)."""
        m = hb.MemoriaHolografica(D)
        for i in range(400):
            m.gravar(f"k{i}", f"v{i}")
        acertos = sum(m.recuperar(f"k{i}")[0] == f"v{i}" for i in range(400))
        self.assertLess(acertos / 400, 0.6)

    def test_hopfield_moderna_limpa_ruido_forte(self):
        rng = np.random.default_rng(1)
        X = np.stack([hb.simbolo(f"p{i}", D) for i in range(500)])
        ok = 0
        for i in range(50):
            q = X[i] + 2.0 * (rng.normal(size=D) + 1j * rng.normal(size=D)) / math.sqrt(2)
            _, p = hb.hopfield(X, q.astype(np.complex64), beta=30.0)
            ok += int(np.argmax(p) == i)
        self.assertEqual(ok, 50)


class Limpeza(unittest.TestCase):
    vocab = ["freezer", "sincronizacao", "compactacao", "joelho", "artrose", "campanha", "memoria", "indice"]

    def test_corrige_erro_de_digitacao(self):
        lim = hb.LimpezaDeVocabulario(self.vocab, d=256)
        self.assertEqual(lim.corrigir("frezer")[0], "freezer")
        self.assertEqual(lim.corrigir("sincronisacao")[0], "sincronizacao")
        self.assertEqual(lim.corrigir("artroze")[0], "artrose")

    def test_palavra_existente_e_intocada_e_ruido_nao_vira_palavra(self):
        lim = hb.LimpezaDeVocabulario(self.vocab, d=256)
        self.assertEqual(lim.corrigir("joelho"), ("joelho", 1.0))
        self.assertEqual(lim.corrigir("xyzqwv")[0], "xyzqwv")


if __name__ == "__main__":
    unittest.main(verbosity=1)
