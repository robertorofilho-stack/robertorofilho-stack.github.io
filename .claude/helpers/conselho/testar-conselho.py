#!/usr/bin/env python3
"""Testes do conselho.py — SEM rede: o HTTP é substituído por respostas canônicas.
Roda no saude.yml e no /manutencao:  python3 .claude/helpers/conselho/testar-conselho.py
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
CONSELHO = os.path.join(AQUI, "conselho.py")
spec = importlib.util.spec_from_file_location("conselho", CONSELHO)
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)

CHAVES = ("OPENROUTER_API_KEY", "OPENAI_API_KEY", "XAI_API_KEY", "GEMINI_API_KEY", "DEEPSEEK_API_KEY", "CONSELHO_MODELOS", "CONSELHO_ENV", "CONSELHO_SEM_SONDA")


def limpar_env():
    for k in CHAVES:
        os.environ.pop(k, None)


def modelos_falsos(*ids, created=None):
    return {"data": [{"id": i, "created": (created or {}).get(i, 0),
                      "pricing": {"prompt": "0.000002", "completion": "0.000008"}} for i in ids]}


def resposta_falsa(texto="1. OBJEÇÕES — …", ent=300, sai=200, cost=None):
    uso = {"prompt_tokens": ent, "completion_tokens": sai}
    if cost is not None:
        uso["cost"] = cost
    return {"choices": [{"message": {"content": texto}}], "usage": uso}


class Base(unittest.TestCase):
    def setUp(self):
        limpar_env()
        self.chamadas = []
        self._http = c._http

    def tearDown(self):
        c._http = self._http
        limpar_env()

    def falso_http(self, tabela):
        """tabela: função(url, dados) -> (status, json)"""
        def f(url, dados=None, cabecalhos=None, timeout=0):
            self.chamadas.append((url, dados, cabecalhos))
            return tabela(url, dados)
        c._http = f


class TesteChaves(Base):
    def test_sem_chave_status_exit_2(self):
        r = subprocess.run([sys.executable, CONSELHO, "--status"], capture_output=True, text=True,
                           env=dict({k: v for k, v in os.environ.items() if k not in CHAVES}, CONSELHO_SEM_SONDA="1"))
        self.assertEqual(r.returncode, 2)
        self.assertIn("nenhuma chave", r.stdout)

    def test_dotenv_fora_do_repo_e_lido_sem_sobrescrever_ambiente(self):
        d = tempfile.mkdtemp()
        p = os.path.join(d, "conselho.env")
        with open(p, "w") as f:
            f.write("# cofre\nexport OPENROUTER_API_KEY=\"sk-or-v1-FAKE0001\"\nXAI_API_KEY='xai-FAKE0002'\n")
        os.environ["CONSELHO_ENV"] = p
        os.environ["XAI_API_KEY"] = "xai-JA-EXISTIA"
        c.carregar_chaves()
        self.assertEqual(os.environ["OPENROUTER_API_KEY"], "sk-or-v1-FAKE0001")
        self.assertEqual(os.environ["XAI_API_KEY"], "xai-JA-EXISTIA")

    def test_mascarar_nunca_deixa_a_chave_inteira(self):
        os.environ["OPENAI_API_KEY"] = "sk-proj-SEGREDO99"
        self.assertNotIn("SEGREDO99", c.mascarar("erro com sk-proj-SEGREDO99 no meio"))


class TesteCredencialNoProxy(Base):
    def test_sonda_200_sem_chave_liga_modo_proxy_e_nao_envia_authorization(self):
        def tabela(url, dados):
            if url.endswith("/auth/key"):
                return 200, {"data": {"label": "cerebro"}}
            if url.endswith("/models"):
                return (200, modelos_falsos("openai/gpt-6", "x-ai/grok-4.6")) if "openrouter" in url else (401, {"error": "no"})
            return 200, resposta_falsa()
        self.falso_http(tabela)
        self.assertEqual(c.detectar_proxy(), ["openrouter"])
        self.assertEqual(os.environ["OPENROUTER_API_KEY"], c.PROXY)
        res, _ = c.rodar("tese")
        self.assertTrue(all(r["ok"] for r in res))
        for _, dados, cab in self.chamadas:
            self.assertNotIn("Authorization", cab or {})

    def test_com_chave_no_ambiente_nao_sonda(self):
        os.environ["OPENROUTER_API_KEY"] = "sk-or-v1-FAKE0001"
        self.falso_http(lambda url, dados: (500, {}))
        self.assertEqual(c.detectar_proxy(), [])
        self.assertEqual(self.chamadas, [])

    def test_sem_proxy_e_sem_chave_continua_exit_2(self):
        self.falso_http(lambda url, dados: (401, {"error": "unauthorized"}))
        self.assertEqual(c.detectar_proxy(), [])
        self.assertEqual(c.chaves_presentes(), {})

    def test_status_mostra_modo_proxy(self):
        os.environ["OPENROUTER_API_KEY"] = c.PROXY
        os.environ["CONSELHO_SEM_SONDA"] = "1"
        r = subprocess.run([sys.executable, CONSELHO, "--status"], capture_output=True, text=True, env=dict(os.environ))
        os.environ.pop("CONSELHO_SEM_SONDA", None)
        self.assertEqual(r.returncode, 0)
        self.assertIn("credencial no proxy", r.stdout)


class TesteEscolhaDeModelo(Base):
    def test_mais_novo_da_familia_sem_variante_especializada(self):
        ms = modelos_falsos("openai/gpt-4.1", "openai/gpt-5", "openai/gpt-5-mini", "openai/gpt-5-codex", "openai/gpt-4o")["data"]
        ms = [{"id": m["id"], "created": 0, "preco_in": 0, "preco_out": 0} for m in ms]
        self.assertEqual(c.escolher(ms, r"^openai/gpt-")["id"], "openai/gpt-5")

    def test_especializada_so_quando_nao_ha_outra(self):
        ms = [{"id": "google/gemini-2.5-flash-preview", "created": 0, "preco_in": 0, "preco_out": 0}]
        self.assertEqual(c.escolher(ms, r"^google/gemini-")["id"], "google/gemini-2.5-flash-preview")
        self.assertIsNone(c.escolher(ms, r"^x-ai/grok-"))

    def test_gpt_oss_batch_e_build_nao_sao_o_gpt_principal(self):
        ids = ["openai/gpt-oss-120b", "openai/gpt-6-astra", "openai/gpt-6-astra:batch", "openai/gpt-5.6-luna-pro"]
        ms = [{"id": i, "created": 0, "preco_in": 1e-6, "preco_out": 5e-6} for i in ids]
        self.assertEqual(c.escolher(ms, r"^openai/gpt-")["id"], "openai/gpt-6-astra")
        self.assertEqual(c._versao("openai/gpt-oss-120b"), 0.0)
        self.assertEqual(c._versao("deepseek/deepseek-v4.1-flash"), 4.1)
        self.assertEqual(c._versao("x-ai/grok-4.6"), 4.6)
        xs = [{"id": i, "created": 0, "preco_in": 0, "preco_out": 0} for i in ["x-ai/grok-build-0.1", "x-ai/grok-4.6"]]
        self.assertEqual(c.escolher(xs, r"^x-ai/grok-")["id"], "x-ai/grok-4.6")

    def test_teto_de_custo_pula_o_caro_e_cai_no_mais_barato_se_todos_passam(self):
        caro = {"id": "openai/gpt-7", "created": 9, "preco_in": 100e-6, "preco_out": 500e-6}   # ~US$ 0.90
        ok = {"id": "openai/gpt-6", "created": 5, "preco_in": 10e-6, "preco_out": 50e-6}        # ~US$ 0.09
        self.assertEqual(c.escolher([caro, ok], r"^openai/gpt-")["id"], "openai/gpt-6")
        c.TETO_USD = 0.01
        try:
            self.assertEqual(c.escolher([caro, ok], r"^openai/gpt-")["id"], "openai/gpt-6")  # todos acima → mais barato
        finally:
            c.TETO_USD = 0.25

    def test_desempate_por_created_na_mesma_versao(self):
        ms = [{"id": "x-ai/grok-4", "created": 10, "preco_in": 0, "preco_out": 0},
              {"id": "x-ai/grok-4-0709", "created": 20, "preco_in": 0, "preco_out": 0}]
        self.assertEqual(c.escolher(ms, r"^x-ai/grok-")["id"], "x-ai/grok-4-0709")


class TesteConselho(Base):
    def test_openrouter_resolve_quatro_familias_e_roda_em_paralelo(self):
        os.environ["OPENROUTER_API_KEY"] = "sk-or-v1-FAKE0001"
        def tabela(url, dados):
            if url.endswith("/models"):
                return 200, modelos_falsos("openai/gpt-5", "x-ai/grok-4", "google/gemini-2.5-pro", "deepseek/deepseek-r1", "meta/llama-4")
            return 200, resposta_falsa(f"objeções de {dados['model']}", cost=0.0123)
        self.falso_http(tabela)
        res, erros = c.rodar("Vender um curso de IA para médicos a R$ 497")
        self.assertEqual(erros, {})
        self.assertEqual([r["familia"] for r in res], ["openai", "xai", "google", "deepseek"])
        self.assertTrue(all(r["ok"] for r in res))
        self.assertEqual(res[0]["custo_usd"], 0.0123)
        # prompt adversarial e tese chegaram ao modelo
        _, dados, cab = [x for x in self.chamadas if x[1]][0]
        self.assertIn("NÃO é confirmar", dados["messages"][0]["content"])
        self.assertIn("R$ 497", dados["messages"][1]["content"])
        self.assertTrue(cab["Authorization"].startswith("Bearer sk-or-v1-"))
        md = c.markdown("tese", res, erros, "contra")
        self.assertIn("4/4 motores responderam", md)
        self.assertIn("| openai |", md)

    def test_direto_vence_openrouter_na_mesma_familia_e_custo_por_preco(self):
        os.environ["OPENROUTER_API_KEY"] = "sk-or-v1-FAKE0001"
        os.environ["OPENAI_API_KEY"] = "sk-proj-FAKE0003"
        def tabela(url, dados):
            if url.startswith("https://api.openai.com") and url.endswith("/models"):
                return 200, {"data": [{"id": "gpt-5", "created": 5}, {"id": "gpt-4o", "created": 1}]}
            if url.endswith("/models"):
                return 200, modelos_falsos("openai/gpt-5", "x-ai/grok-4")
            return 200, resposta_falsa(ent=1000, sai=500)
        self.falso_http(tabela)
        res, _ = c.rodar("tese", maximo=4)
        fam = {r["familia"]: r for r in res}
        self.assertEqual(fam["openai"]["prov"], "openai")          # direto venceu
        self.assertIsNone(fam["openai"]["custo_usd"])              # direto não informa preço
        self.assertAlmostEqual(fam["xai"]["custo_usd"], 1000 * 0.000002 + 500 * 0.000008, places=6)

    def test_uma_falha_nao_derruba_o_conselho(self):
        os.environ["OPENROUTER_API_KEY"] = "sk-or-v1-FAKE0001"
        def tabela(url, dados):
            if url.endswith("/models"):
                return 200, modelos_falsos("openai/gpt-5", "x-ai/grok-4")
            if dados["model"] == "x-ai/grok-4":
                return 400, {"error": {"message": "modelo indisponível"}}
            return 200, resposta_falsa()
        self.falso_http(tabela)
        res, _ = c.rodar("tese")
        self.assertEqual([r["ok"] for r in res], [True, False])
        self.assertIn("HTTP 400", res[1]["erro"])
        self.assertIn("## Falhas", c.markdown("tese", res, {}, "contra"))

    def test_modelos_forcados_por_env(self):
        os.environ["GEMINI_API_KEY"] = "AIzaFAKE0004"
        os.environ["CONSELHO_MODELOS"] = "gemini:gemini-2.5-pro,openai:gpt-5"   # openai sem chave → ignorado
        self.falso_http(lambda url, dados: (200, resposta_falsa()))
        res, _ = c.rodar("tese")
        self.assertEqual([(r["prov"], r["modelo"]) for r in res], [("gemini", "gemini-2.5-pro")])
        self.assertFalse(any(u.endswith("/models") for u, _, _ in self.chamadas))  # forçado não lista

    def test_cli_sem_chave_exit_2_e_sem_tese_exit_64(self):
        env = {k: v for k, v in os.environ.items() if k not in CHAVES}
        env["CONSELHO_SEM_SONDA"] = "1"
        r = subprocess.run([sys.executable, CONSELHO, "--tese", "x"], capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 2)
        self.assertIn("/adversarial", r.stderr)
        r = subprocess.run([sys.executable, CONSELHO], capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 64)

    def test_retry_em_429_e_depois_sucesso(self):
        os.environ["OPENROUTER_API_KEY"] = "sk-or-v1-FAKE0001"
        c.time.sleep = lambda s: None
        vezes = {"n": 0}
        import urllib.error, io
        def f(url, dados=None, cabecalhos=None, timeout=0):
            if url.endswith("/models"):
                return 200, modelos_falsos("deepseek/deepseek-r1")
            vezes["n"] += 1
            if vezes["n"] == 1:
                raise urllib.error.HTTPError(url, 429, "rate", {}, io.BytesIO(b'{"error":{"message":"slow down"}}'))
            return 200, resposta_falsa()
        c._http = f
        res, _ = c.rodar("tese")
        self.assertTrue(res[0]["ok"])
        self.assertEqual(vezes["n"], 2)


if __name__ == "__main__":
    unittest.main(verbosity=1)
