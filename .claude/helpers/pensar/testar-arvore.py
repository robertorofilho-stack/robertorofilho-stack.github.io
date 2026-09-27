#!/usr/bin/env python3
"""Testes da arvore.py — sem rede (motor Simulado e verificador do Jogo 24).
Roda no saude.yml:  python3 .claude/helpers/pensar/testar-arvore.py
"""
import importlib.util
import os
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("arvore", os.path.join(AQUI, "arvore.py"))
ar = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ar)


class Politica(unittest.TestCase):
    def test_priors_normalizados_somam_1(self):
        p = ar.normalizar_priors([0.6, 0.3, 0.1])
        self.assertAlmostEqual(sum(p), 1.0)
        self.assertEqual(ar.normalizar_priors([0, 0]), [0.5, 0.5])
        self.assertEqual(ar.normalizar_priors([-1, 0]), [0.5, 0.5])

    def test_puct_explora_ja_na_primeira_descida(self):
        pai = ar.No()
        f = ar.No("x", pai, 0.5)
        self.assertGreater(ar.puct(pai, f), 0)     # no pseudocódigo original dava 0 (√0)

    def test_puct_prefere_nao_visitado_de_prior_igual(self):
        pai = ar.No()
        pai.n = 10
        a, b = ar.No("a", pai, 0.5), ar.No("b", pai, 0.5)
        a.n, a.w = 5, 2.5
        self.assertGreater(ar.puct(pai, b), ar.puct(pai, a) - a.q)


class Busca(unittest.TestCase):
    def test_acha_solucao_mesmo_com_propositor_enganado(self):
        m = ar.Simulado("LUCRO")
        r = ar.buscar(m, "p", iteracoes=40, k=3, prof_max=5)
        self.assertEqual("".join(r["melhor"]), "LUCRO")
        self.assertEqual(r["valor"], 1.0)
        self.assertEqual(r["parou"], "solução verificada (verificador exato)")
        self.assertTrue(r["verificada"])

    def test_reflexao_do_erro_entra_nos_prompts_seguintes(self):
        m = ar.Simulado("LUCRO")
        r = ar.buscar(m, "p", iteracoes=40, k=3, prof_max=5)
        self.assertTrue(r["reflexoes"])
        self.assertTrue(any(p["reflexoes"] for p in m.prompts[1:]))

    def test_estagnacao_sobe_temperatura_e_pede_diversidade(self):
        class Travado(ar.Simulado):
            def avaliar(self, problema, caminho):
                self.chamadas += 1
                return 0.1, "sem progresso"

            def verificar(self, problema, caminho):
                return None
        m = Travado("LUCRO")
        ar.buscar(m, "p", iteracoes=10, k=2, prof_max=5, paciencia=2)
        self.assertTrue(any(p["diverso"] for p in m.prompts))
        self.assertGreater(max(p["temperatura"] for p in m.prompts), 0.7)
        self.assertLessEqual(max(p["temperatura"] for p in m.prompts), 1.2)

    def test_sem_nenhum_sinal_para_cedo_e_explica(self):
        class Perdido(ar.Simulado):
            def avaliar(self, problema, caminho):
                self.chamadas += 1
                return 0.05, "nada a ver"

            def verificar(self, problema, caminho):
                return None
        m = Perdido("LUCRO")
        r = ar.buscar(m, "p", iteracoes=100, k=2, prof_max=5, paciencia=2)
        self.assertIn("sem sinal", r["parou"])
        self.assertLess(m.chamadas, 30)

    def test_orcamento_duro_para_a_busca(self):
        class Caro(ar.Simulado):
            def propor(self, *a):
                if self.chamadas >= 5:
                    raise ar.Orcamento("teto")
                return super().propor(*a)
        m = Caro("LUCROSOLIDO")
        r = ar.buscar(m, "p", iteracoes=100, k=3, prof_max=11)
        self.assertIn("teto", r["parou"])
        self.assertLessEqual(m.chamadas, 12)

    def test_proposta_vazia_uma_vez_nao_mata_a_raiz(self):
        class Gago(ar.Simulado):
            def propor(self, *a):
                if self.chamadas == 0:
                    self.chamadas += 1
                    return []                                  # 1ª resposta ilegível (visto ao vivo em 27/09)
                return super().propor(*a)
        r = ar.buscar(Gago("OK"), "p", iteracoes=20, k=2, prof_max=2)
        self.assertTrue(r["verificada"])

    def test_relatorio_markdown(self):
        r = ar.buscar(ar.Simulado("OK"), "p", iteracoes=20, k=2, prof_max=2)
        md = ar.relatorio("p", r)
        self.assertIn("## Melhor caminho", md)
        self.assertIn("1. O", md)


class JuizNaoFecha(unittest.TestCase):
    """Regressão da execução real de 27/09: o juiz LLM deu 1,0 para um Jogo 24 errado."""

    def test_juiz_otimista_nao_vira_solucao_verificada(self):
        class Bajulador(ar.Simulado):
            def avaliar(self, problema, caminho):
                self.chamadas += 1
                return 1.0, ""                          # aprova tudo

            def verificar(self, problema, caminho):
                return None if len(caminho) < 5 else (1.0 if "".join(caminho) == self.alvo else 0.0)
        r = ar.buscar(Bajulador("LUCRO"), "p", iteracoes=3, k=2, prof_max=5)
        self.assertFalse(r["verificada"])
        self.assertNotIn("verificada", r["parou"])

    def test_sem_verificador_rotula_como_nao_verificada(self):
        class SoJuiz(ar.Simulado):
            tem_verificador = False

            def avaliar(self, problema, caminho):
                self.chamadas += 1
                return 1.0, ""

            def verificar(self, problema, caminho):
                return None
        r = ar.buscar(SoJuiz("LUCRO"), "p", iteracoes=5, k=2, prof_max=5)
        self.assertEqual(r["parou"], "aprovada pelo juiz LLM — NÃO verificada")
        self.assertFalse(r["verificada"])


class Jogo24(unittest.TestCase):
    def test_passo_com_texto_extra_e_reprovado(self):
        j = ar.Jogo24([4, 7, 8, 8])
        self.assertEqual(j.valor(["8 - 4 = 4", "7 - 4 = 3; ficam 8 e 3, que dão 8 × 3 = 24"]), 0.0)

    def test_poda_parcial_exata(self):
        j = ar.Jogo24([4, 7, 8, 8])
        self.assertEqual(j.valor(["8 * 8 = 64", "64 * 7 = 448"]), 0.0)   # 448 e 4 não chegam a 24
        self.assertIsNone(j.valor(["8 / 8 = 1"]))                        # 4, 7, 1 ainda chegam

    def test_verificador_exato(self):
        j = ar.Jogo24([4, 7, 8, 8])
        self.assertEqual(j.valor(["7 - 4 = 3", "8 / 8 = 1", "3 * 8 = 24"]), 0.0)   # usa o 8 duas vezes depois de consumir
        self.assertEqual(j.valor(["8 / 8 = 1", "7 - 1 = 6", "6 * 4 = 24"]), 1.0)
        self.assertEqual(j.valor(["8 / 8 = 2"]), 0.0)                              # conta errada
        self.assertEqual(j.valor(["9 + 1 = 10"]), 0.0)                             # número que não existe

    def test_solucivel(self):
        self.assertTrue(ar.Jogo24([4, 7, 8, 8]).solucivel([4, 7, 8, 8]))
        self.assertFalse(ar.Jogo24([1, 1, 1, 1]).solucivel([1, 1, 1, 1]))


if __name__ == "__main__":
    unittest.main(verbosity=1)
