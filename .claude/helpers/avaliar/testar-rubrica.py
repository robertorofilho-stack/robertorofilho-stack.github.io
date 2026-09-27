#!/usr/bin/env python3
"""Testes da rubrica.py — sem rede. Roda no saude.yml."""
import importlib.util
import os
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("rubrica", os.path.join(AQUI, "rubrica.py"))
rb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rb)

RUB = [{"item": "Cita a fonte de cada número de preço", "peso": 3},
       {"item": "Checkout sem boleto, só Pix e cartão", "peso": 2},
       {"item": "Garantia de 7 dias explícita na página", "peso": 1}]


class Nota(unittest.TestCase):
    def test_ponderada(self):
        s, falt = rb.nota(RUB, {RUB[0]["item"]: True, RUB[1]["item"]: False, RUB[2]["item"]: 0.5})
        self.assertAlmostEqual(s, (3 + 0 + 0.5) / 6, places=4)
        self.assertEqual(falt, [])

    def test_item_sem_julgamento_conta_zero_e_e_avisado(self):
        s, falt = rb.nota(RUB, {RUB[0]["item"]: True})
        self.assertAlmostEqual(s, 0.5)
        self.assertEqual(len(falt), 2)

    def test_resposta_longa_nao_ganha_ponto(self):
        # nota depende só dos itens: não há como "texto maior" subir o placar
        self.assertEqual(rb.nota(RUB, {r["item"]: True for r in RUB})[0], 1.0)


class Auditoria(unittest.TestCase):
    def test_rubrica_boa_passa(self):
        self.assertEqual(rb.auditar(RUB), [])

    def test_acusa_curto_vago_duplicado_e_peso(self):
        ruim = RUB + [{"item": "É bom", "peso": 1},
                      {"item": "A copy é adequada e de qualidade", "peso": 1},
                      {"item": "Cita a fonte de cada número de preço exibido", "peso": 1},
                      {"item": "Menciona prazo de entrega em dias", "peso": 0}]
        tipos = [t for _, t, _ in rb.auditar(ruim)]
        self.assertIn("curto/vazio", tipos)
        self.assertIn("vago: sem critério checável", tipos)
        self.assertTrue(any(t.startswith("duplica") for t in tipos))
        self.assertIn("peso inválido", tipos)
        self.assertEqual(rb.main(["auditar", self._grava(ruim)]), 1)

    def _grava(self, obj):
        import json, tempfile
        f = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        json.dump(obj, f, ensure_ascii=False)
        f.close()
        return f.name


class Concordancia(unittest.TestCase):
    def test_acordo_e_kappa(self):
        po, k = rb.concordancia(["s", "s", "n", "n"], ["s", "s", "n", "n"])
        self.assertEqual((po, k), (1.0, 1.0))
        po, k = rb.concordancia(["s", "n", "s", "n"], ["s", "s", "n", "n"])
        self.assertEqual(po, 0.5)
        self.assertAlmostEqual(k, 0.0)

    def test_juiz_que_so_diz_sim_tem_kappa_baixo_mesmo_com_acordo_alto(self):
        humano = ["s"] * 8 + ["n"] * 2
        juiz = ["s"] * 10
        po, k = rb.concordancia(juiz, humano)
        self.assertEqual(po, 0.8)
        self.assertLessEqual(k, 0.0)

    def test_tamanhos_diferentes(self):
        with self.assertRaises(ValueError):
            rb.concordancia(["s"], ["s", "n"])


if __name__ == "__main__":
    unittest.main(verbosity=1)
