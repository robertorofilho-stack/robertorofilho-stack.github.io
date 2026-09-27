#!/usr/bin/env python3
"""Testes do mutacao.py — mutante morto, sobrevivente e o bug do bytecode (27/09). Roda no saude.yml."""
import importlib.util
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
MUT = os.path.join(AQUI, "mutacao.py")


class Mutacao(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.alvo = os.path.join(self.d, "alvo.py")
        with open(self.alvo, "w") as f:
            f.write(textwrap.dedent('''\
                def igual(a, b):
                    return a == b


                def sem_teste(x):
                    return x > 0
                '''))
        self.teste = os.path.join(self.d, "teste.py")
        with open(self.teste, "w") as f:
            f.write(textwrap.dedent(f'''\
                import importlib.util, sys
                spec = importlib.util.spec_from_file_location("alvo", {self.alvo!r})
                m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
                sys.exit(0 if m.igual(1, 1) and not m.igual(1, 2) else 1)
                '''))

    def test_placar_morto_e_sobrevivente(self):
        r = subprocess.run([sys.executable, MUT, self.alvo, self.teste, "--minimo", "0.4"], capture_output=True, text=True)
        self.assertIn("1/2 mutantes mortos", r.stdout)
        self.assertIn("sobreviveu L6", r.stdout)            # x > 0 não tem teste
        self.assertEqual(r.returncode, 0)

    def test_original_restaurado_e_sem_bytecode_de_mutante(self):
        with open(self.alvo) as f:
            antes = f.read()
        subprocess.run([sys.executable, MUT, self.alvo, self.teste], capture_output=True, text=True)
        with open(self.alvo) as f:
            self.assertEqual(f.read(), antes)
        self.assertFalse(os.path.exists(self.alvo + ".mutacao-bak"))
        spec = importlib.util.spec_from_file_location("alvo_pos", self.alvo)      # import em processo, com cache
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        self.assertTrue(m.igual(3, 3))
        self.assertTrue(m.sem_teste(1))


if __name__ == "__main__":
    unittest.main(verbosity=1)
