#!/usr/bin/env python3
"""Testes do merge-indice.py (driver de merge do git, 3 vias por link) — reproduzem os incidentes de 30/08 a 27/09."""
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location("mi", os.path.join(AQUI, "merge-indice.py"))
mi = importlib.util.module_from_spec(_s)
_s.loader.exec_module(mi)
O = ["# Índice", "- [a](a.md) — velha", "- [b](b.md) — texto b", "- [c](c.md) — c"]


class Tres(unittest.TestCase):
    def test_compactacao_de_um_lado_sobrevive_ao_outro_parado(self):       # 27/09: o MacBook desfazia o mini
        a = ["# Índice", "- [b](b.md) — texto b", "- [c](c.md) — c"]
        for x, y in ((a, O), (O, a)):
            saida, falt = mi.mesclar(O, x, y)
            self.assertFalse(any("a.md" in l for l in saida))
            self.assertEqual(falt, [])

    def test_encurtamento_de_um_lado_vence_texto_parado(self):
        a = ["# Índice", "- [a](a.md) — velha", "- [b](b.md) — b", "- [c](c.md) — c"]
        for x, y in ((a, O), (O, a)):
            self.assertIn("- [b](b.md) — b", mi.mesclar(O, x, y)[0])

    def test_memoria_nova_dos_dois_lados_entra(self):                     # 30/08: um índice apagava o do outro
        a, b = O + ["- [d](d.md) — do mini"], O + ["- [e](e.md) — do macbook"]
        saida, _ = mi.mesclar(O, a, b)
        self.assertTrue(any("d.md" in l for l in saida) and any("e.md" in l for l in saida))

    def test_linha_mudada_pelos_dois_nao_duplica_e_nao_perde(self):       # merge=union guardava as duas versões
        a = ["# Índice", "- [a](a.md) — velha", "- [b](b.md) — versão A", "- [c](c.md) — c"]
        b = ["# Índice", "- [a](a.md) — velha", "- [b](b.md) — versão B", "- [c](c.md) — c"]
        saida, falt = mi.mesclar(O, a, b)
        self.assertEqual(sum("b.md" in l for l in saida), 1)
        self.assertEqual(falt, [])

    def test_tirar_de_um_lado_e_editar_no_outro_mantem(self):             # dúvida → nada some
        a = ["# Índice", "- [b](b.md) — texto b", "- [c](c.md) — c"]
        b = ["# Índice", "- [a](a.md) — velha ✅ RESOLVIDO", "- [b](b.md) — texto b", "- [c](c.md) — c"]
        self.assertTrue(any("a.md" in l for l in mi.mesclar(O, a, b)[0]))

    def test_link_agrupado_so_sai_se_todos_sairem(self):
        o = ["- [a](a.md) · [b](b.md)"]
        a = ["- [b](b.md)"]
        saida, falt = mi.mesclar(o, a, o)
        self.assertEqual(falt, [])
        self.assertTrue(any("b.md" in l for l in saida))

    def test_driver_de_verdade_num_merge_do_git(self):
        with tempfile.TemporaryDirectory() as d:
            g = lambda *a: subprocess.run(["git", "-C", d, *a], check=True, capture_output=True, text=True)
            g("init", "-q", "-b", "master"); g("config", "user.email", "t@t"); g("config", "user.name", "t")
            os.makedirs(os.path.join(d, "claude-config", "memory"))
            idx = os.path.join(d, "claude-config", "memory", "MEMORY.md")
            with open(os.path.join(d, ".gitattributes"), "w") as f:
                f.write("claude-config/memory/MEMORY.md merge=indice-cerebro\n")
            g("config", "merge.indice-cerebro.driver", f'python3 "{os.path.join(AQUI, "merge-indice.py")}" %O %A %B')
            with open(idx, "w") as f:
                f.write("\n".join(O) + "\n")
            g("add", "-A"); g("commit", "-qm", "base")
            g("checkout", "-qb", "macbook")
            with open(idx, "w") as f:
                f.write("\n".join(O + ["- [e](e.md) — nova do macbook"]) + "\n")
            g("commit", "-qam", "macbook")
            g("checkout", "-q", "master")
            with open(idx, "w") as f:
                f.write("\n".join(["# Índice", "- [b](b.md) — b", "- [c](c.md) — c"]) + "\n")
            g("commit", "-qam", "mini compacta")
            g("merge", "-q", "--no-edit", "macbook")
            with open(idx) as f:
                txt = f.read()
            self.assertNotIn("<<<<<<<", txt)
            self.assertNotIn("a.md", txt)
            self.assertIn("e.md", txt)
            self.assertIn("- [b](b.md) — b\n", txt)


if __name__ == "__main__":
    unittest.main(verbosity=1)
