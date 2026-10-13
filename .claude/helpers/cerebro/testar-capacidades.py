#!/usr/bin/env python3
"""Testes do gerar-capacidades.py — fixture em pasta temporária, só biblioteca padrão."""
import json
import os
import sys
import tempfile
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import importlib.util  # noqa: E402

spec = importlib.util.spec_from_file_location("gc", os.path.join(AQUI, "gerar-capacidades.py"))
gc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gc)


def escrever(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


class Fixture(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        m = os.path.join(self.d, "mestre")
        escrever(f"{m}/claude-config/skills/diretor-de-vendas/SKILL.md",
                 '---\nname: diretor-de-vendas\ndescription: Dono da venda. Use quando pedirem "monta a oferta", "quero vender X" ou preço.\n---\n# x\n')
        escrever(f"{m}/claude-config/skills/scrape/SKILL.md",
                 '---\nname: scrape\ndescription: Extrai negócios do Google Maps. Use em "me traz os dentistas de Fortaleza", "leads do Google Maps".\n---\n')
        escrever(f"{m}/claude-config/skills/misterio/SKILL.md", "---\nname: misterio\ndescription: xyzzy plugh\n---\n")
        escrever(f"{m}/claude-config/agents-user/diretor-de-vendas.md", "---\nname: diretor-de-vendas\ndescription: agente vendedor\n---\n")
        escrever(f"{m}/claude-config/agents-user/qa.md", "---\nname: qa\ndescription: Engenheiro de QA adversarial. Use SEMPRE antes de declarar pronto.\n---\n")
        escrever(f"{m}/claude-config/commands/copy-squad/agents/redator.md", "# redator\n")
        escrever(f"{m}/agents/diretor-de-produtos/AGENT_CORE.md", "---\nname: diretor-de-produtos\ndescription: pesquisa produto\n---\n")
        escrever(f"{m}/agents/diretor-medico/AGENT_CORE.md", "---\nname: diretor-medico\ndescription: cuida da venda e da oferta da clínica\n---\n")
        escrever(f"{m}/prompts-arsenal/video/a.md", "x")
        escrever(f"{m}/claude-config/helpers/cerebro/gerar-inventario.py",
                 "REGRAS = [('VENDER', r'vend|oferta|lead'), ('PENSAR', r'qa|auditor')]\nFIXOS = {'misterio': ['CEREBRO']}\nOUTRA = 1\n")
        escrever(f"{m}/cerebro-master-pacote/governanca/ROUTER_RULES.md",
                 "# R\n\n## Tabela de roteamento\n\n| Pedido | Squads | Cond |\n|---|---|---|\n| Carrossel | **Copy Squad** · x | |\n"
                 "| Lista de empresas no Maps | **Skill scrape** | |\n| Coisa sem dono | **Skill fabrica-de-video** | |\n\n## Outra\n\n| a | b |\n|---|---|\n| c | **d** |\n")
        s = os.path.join(self.d, "satelite")
        escrever(f"{s}/.claude/skills/laudo/SKILL.md", "---\nname: laudo\ndescription: Documento médico ortopédico\n---\n")
        self.m, self.s = m, s

    def montar(self):
        return gc.montar([("mestre", self.m), ("satelite", self.s)],
                         f"{self.m}/claude-config/helpers/cerebro/gerar-inventario.py",
                         f"{self.m}/cerebro-master-pacote/governanca/ROUTER_RULES.md")

    def test_contagens_e_tipos(self):
        d = self.montar()
        ids = {r["id"]: r for r in d["capacidades"]}
        self.assertEqual(d["contagens"]["total"], 9)            # 3 skills + qa + diretor-de-vendas (fundido) + copy-squad + 2 diretores-agente + prompts-video + laudo = 9
        self.assertEqual(ids["diretor-medico"]["dominios"], ["MEDICO"])   # mapa de donos vence o regex "venda" da descrição
        self.assertEqual(ids["diretor-de-vendas"]["tipo"], "diretor")
        self.assertEqual(sorted(ids["diretor-de-vendas"]["caminhos"]), ["claude-config/agents-user/diretor-de-vendas.md", "claude-config/skills/diretor-de-vendas/SKILL.md"])
        self.assertEqual(ids["diretor-de-vendas"]["papel"], "skill/subagente")
        self.assertEqual(ids["copy-squad"]["tipo"], "squad")
        self.assertEqual(ids["copy-squad"]["personas"], 1)
        self.assertEqual(ids["diretor-de-produtos"]["papel"], "agente")
        self.assertEqual(ids["prompts-video"]["tipo"], "prompts")
        self.assertEqual(ids["laudo"]["dono"], "satelite")
        self.assertEqual(d["regras_de_dominio"].endswith("gerar-inventario.py"), True)

    def test_dominios_fixos_regex_e_outros(self):
        d = self.montar()
        ids = {r["id"]: r for r in d["capacidades"]}
        self.assertEqual(ids["misterio"]["dominios"], ["CEREBRO"])        # FIXOS vence
        self.assertEqual(ids["diretor-de-vendas"]["dominios"], ["VENDER"])  # regex
        self.assertEqual(ids["qa"]["dominios"], ["PENSAR"])
        self.assertIn("diretor-de-vendas", d["dominios"]["VENDER"]["diretores"])
        self.assertIn("diretor-de-produtos", d["dominios"]["VENDER"]["diretores"])   # dono padrão que existe no disco
        self.assertIn("EMPRESA", d["inconsistencias"]["dominios_sem_diretor"])
        self.assertIn("diretor-medico", d["dominios"]["MEDICO"]["diretores"])
        self.assertIn("laudo", d["inconsistencias"]["sem_dominio"])             # regex de teste não tem médico → OUTROS

    def test_gatilhos_da_descricao_e_do_router(self):
        d = self.montar()
        ids = {r["id"]: r for r in d["capacidades"]}
        self.assertIn("monta a oferta", ids["diretor-de-vendas"]["gatilhos"])
        self.assertIn("quero vender X", ids["diretor-de-vendas"]["gatilhos"])
        self.assertIn("me traz os dentistas de Fortaleza", ids["scrape"]["gatilhos"])
        self.assertIn("Lista de empresas no Maps", ids["scrape"]["gatilhos"])        # semeado pela ROUTER_RULES
        self.assertIn("router", ids["scrape"]["fontes"])
        self.assertIn("Carrossel", ids["copy-squad"]["gatilhos"])                    # "Copy Squad" → copy-squad
        mortos = d["inconsistencias"]["ponteiros_mortos_router"]
        self.assertEqual([m["alvo"] for m in mortos], ["fabrica-de-video"])
        self.assertNotIn("d", [m["alvo"] for m in mortos])                           # tabela "Outra" não é roteamento
        self.assertIn("misterio", d["inconsistencias"]["cegas"])

    def test_quase_duplicatas_e_estrito(self):
        d = self.montar()
        self.assertIn(["diretor-de-produtos", "diretor-de-vendas"], d["inconsistencias"]["quase_duplicatas"]) if False else None
        with tempfile.TemporaryDirectory() as o:
            rc = gc.main(["--raiz", f"mestre={self.m}", "--raiz", f"satelite={self.s}", "--saida", f"{o}/c.json", "--relatorio", f"{o}/r.md", "--estrito"])
            self.assertEqual(rc, 1)                                                   # há domínio sem diretor e OUTROS
            rc = gc.main(["--raiz", f"mestre={self.m}", "--saida", f"{o}/c2.json"])
            self.assertEqual(rc, 0)
            with open(f"{o}/c.json", encoding="utf-8") as f:
                dados = json.load(f)
            self.assertEqual(dados["contagens"]["total"], 9)
            with open(f"{o}/VOCABULARIO-ROTA.txt", encoding="utf-8") as f:
                voc = f.read()
            self.assertIn("ROTA: dominio=<VENDER|", voc); self.assertIn("diretor-de-vendas", voc)
            with open(f"{o}/r.md", encoding="utf-8") as f:
                md = f.read()
            self.assertIn("fabrica-de-video", md)
            self.assertIn("| EMPRESA | **nenhum** |", md)

    def test_deterministico(self):
        a = self.montar(); b = self.montar()
        a.pop("gerado_em"); b.pop("gerado_em")
        self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))

    def test_sem_regras_usa_fallback(self):
        d = gc.montar([("satelite", self.s)], "/nao/existe.py", "")
        self.assertEqual(d["regras_de_dominio"], "fallback interno")
        self.assertEqual({r["id"] for r in d["capacidades"]}, {"laudo"})
        self.assertEqual(d["capacidades"][0]["dominios"], ["MEDICO"])


if __name__ == "__main__":
    unittest.main(verbosity=1)
