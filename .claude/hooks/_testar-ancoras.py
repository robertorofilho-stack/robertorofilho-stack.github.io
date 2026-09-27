#!/usr/bin/env python3
"""Teste de cenário longo do checkpoint (CMU 11-768: "you kind of need to test them in the wild").

Proibição na 1ª mensagem, PR aberto no passo 3, 40 mensagens depois, compactação: o checkpoint precisa
trazer o objetivo original, a proibição literal e o PR já feito. Roda no saude.yml.
"""
import importlib.util
import json
import os
import subprocess
import tempfile
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("ancoras", os.path.join(AQUI, "_ancoras.py"))
an = importlib.util.module_from_spec(spec)
spec.loader.exec_module(an)


def u(txt):
    return {"type": "user", "message": {"content": txt}}


def ferramenta(nome, entrada):
    return {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": nome, "input": entrada}]}}


def resultado():
    return {"type": "user", "message": {"content": [{"type": "tool_result", "content": "nunca mostre isto"}]}}


class Cenario(unittest.TestCase):
    def setUp(self):
        linhas = [u("Monte a página de vendas do guia. Nunca use boleto. Não publique sem eu aprovar."),
                  ferramenta("Bash", {"command": "npm run build"}), resultado(),
                  ferramenta("mcp__github__create_pull_request", {"title": "Página do guia", "head": "x"}), resultado(),
                  ferramenta("Bash", {"command": "git push -u origin x"}), resultado()]
        for i in range(40):
            linhas += [u(f"ajuste número {i} no texto"), ferramenta("Edit", {"file_path": "p.html"}), resultado()]
        linhas += [u("<system-reminder>ruído do sistema</system-reminder>"), u("agora revise a headline")]
        self.tr = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8")
        self.tr.write("\n".join(json.dumps(x, ensure_ascii=False) for x in linhas))
        self.tr.close()

    def test_objetivo_proibicoes_e_efeitos_sobrevivem(self):
        md = an.markdown(self.tr.name)
        self.assertIn("Monte a página de vendas do guia", md.split("### Últimos")[0])     # 1º pedido
        self.assertIn("Nunca use boleto.", md)
        self.assertIn("Não publique sem eu aprovar.", md)
        self.assertIn("create_pull_request", md)
        self.assertIn("git push -u origin x", md)
        self.assertIn("agora revise a headline", md)                                     # último pedido

    def test_nao_confunde_resultado_de_ferramenta_nem_ruido_com_pedido(self):
        md = an.markdown(self.tr.name)
        self.assertNotIn("nunca mostre isto", md)
        self.assertNotIn("ruído do sistema", md)
        self.assertNotIn("npm run build", md)          # build não é efeito externo

    def test_hook_completo_grava_e_carregar_reinjeta_so_na_compactacao(self):
        cache = tempfile.mkdtemp()
        env = dict(os.environ, XDG_CACHE_HOME=cache, CLAUDE_PROJECT_DIR=os.path.dirname(os.path.dirname(AQUI)))
        entrada = json.dumps({"session_id": "cen-1", "transcript_path": self.tr.name})
        subprocess.run(["bash", os.path.join(AQUI, "checkpoint.sh")], input=entrada, text=True, env=env,
                       capture_output=True, timeout=30, check=True)
        with open(os.path.join(cache, "cerebro", "checkpoint-cen-1.md"), encoding="utf-8") as f:
            self.assertIn("Nunca use boleto.", f.read())
        for fonte, deve in (("compact", True), ("startup", False)):
            r = subprocess.run(["bash", os.path.join(AQUI, "carregar-cerebro.sh")], text=True, env=env,
                               input=json.dumps({"session_id": "cen-1", "source": fonte}),
                               capture_output=True, timeout=30)
            ctx = json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"]
            self.assertEqual("Nunca use boleto." in ctx, deve, fonte)


if __name__ == "__main__":
    unittest.main(verbosity=1)
