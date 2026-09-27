#!/usr/bin/env python3
"""Testes do corretor_lexico.py (SymSpell + Damerau-Levenshtein) e da correção da consulta no memoria_viva."""
import importlib.util
import os
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location("corretor_lexico", os.path.join(AQUI, "corretor_lexico.py"))
cl = importlib.util.module_from_spec(_s)
_s.loader.exec_module(cl)
FREQ = {"freezer": 30, "sincronizacao": 12, "artrose": 40, "artroses": 2, "joelho": 50, "campanha": 20, "memoria": 90,
        "compactacao": 5, "casa": 10, "caso": 3}


class Distancia(unittest.TestCase):
    def test_damerau_levenshtein(self):
        self.assertEqual(cl.dl("abc", "abc"), 0)
        self.assertEqual(cl.dl("abc", "acb"), 1)          # transposição conta 1
        self.assertEqual(cl.dl("frezer", "freezer"), 1)
        self.assertEqual(cl.dl("kitten", "sitting"), 3)


class Corretor(unittest.TestCase):
    def setUp(self):
        self.c = cl.Corretor(FREQ)

    def test_corrige_digitacao_e_flexao(self):
        self.assertEqual(self.c.corrigir("frezer")[0], "freezer")
        self.assertEqual(self.c.corrigir("sincronisacao")[0], "sincronizacao")
        self.assertEqual(self.c.corrigir("artroze")[0], "artrose")
        self.assertEqual(self.c.corrigir("campnaha")[0], "campanha")    # troca de letras vizinhas

    def test_palavra_conhecida_e_curta_intocadas(self):
        self.assertEqual(self.c.corrigir("joelho"), ("joelho", 0))
        self.assertEqual(self.c.corrigir("cas"), ("cas", 0))
        self.assertEqual(self.c.corrigir("xyzqwv"), ("xyzqwv", None))

    def test_empate_vai_para_a_mais_frequente(self):
        self.assertEqual(self.c.corrigir("casx")[0], "casa")            # casa (10) > caso (3), mesma distância

    def test_palavra_curta_so_aceita_uma_edicao(self):
        self.assertEqual(self.c.corrigir("cxsx")[0], "cxsx")            # 2 edições em 4 letras: não arrisca


class NaBusca(unittest.TestCase):
    def test_consulta_com_erro_acha_a_memoria_e_limpa_fica_igual(self):
        import tempfile
        s = importlib.util.spec_from_file_location("memoria_viva", os.path.join(AQUI, "memoria_viva.py"))
        mv = importlib.util.module_from_spec(s)
        s.loader.exec_module(mv)
        with tempfile.TemporaryDirectory() as d:
            for nome, txt in (("freezer.md", "---\nname: freezer\ndescription: campanha do freezer no meta\n---\nroas cpa freezer campanha\n"),
                              ("joelho.md", "---\nname: joelho\ndescription: artrose do joelho\n---\nartrose joelho dor\n")):
                with open(os.path.join(d, nome), "w") as f:
                    f.write(txt)
            docs = mv.carregar([d], cache=False)
            self.assertEqual(mv.limpar_consulta(docs, "campanha do freezer"), "campanha do freezer")
            self.assertIn("freezer", mv.limpar_consulta(docs, "campanha do frezer"))
            est = mv.estado_padrao([d])
            est = mv.ler_estado(est) if isinstance(est, str) else est
            ids = [x["id"] for x in mv.buscar(docs, est, "campnaha do frezer", k=2, vagas_assoc=0)]
            self.assertEqual(ids[0], "freezer.md")


if __name__ == "__main__":
    unittest.main(verbosity=1)
