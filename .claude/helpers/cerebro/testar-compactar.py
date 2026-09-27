#!/usr/bin/env python3
"""Testes do compactar-indice.py — duas cópias, nada some, protegidos ficam, recente fica, idempotente."""
import importlib.util
import os
import shutil
import tempfile
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("ci", os.path.join(AQUI, "compactar-indice.py"))
ci = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)
import datetime as dt  # noqa: E402

HOJE = dt.date(2026, 9, 27)
INDICE = """# Índice
- 🆕 [novíssima do topo (26/09)](topo.md)
## LEIS E REGRAS MESTRAS
- [lei antiga sem data](lei-velha.md)
## PROJETOS
- [projeto de julho](proj-julho.md) · [outro](proj-outro.md)
- [regra de comportamento (02/07)](feedback-modo.md)
- [projeto recente (25/09)](proj-recente.md)
- [projeto sem data em lugar nenhum](proj-sem-data.md)
- [projeto de agosto (10/08)](proj-agosto.md)
""" + "".join(f"- [enchimento {i} (21/09)](enche-{i}.md)\n" for i in range(3))


class Compactar(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.local, self.repo = os.path.join(self.d, "local"), os.path.join(self.d, "repo")
        for p in (self.local, self.repo):
            os.makedirs(p)
            with open(os.path.join(p, "MEMORY.md"), "w", encoding="utf-8") as f:
                f.write(INDICE)
            with open(os.path.join(p, "proj-julho.md"), "w", encoding="utf-8") as f:
                f.write("---\nname: x\nmetadata:\n  modified: 2026-07-03T10:00:00Z\n---\n")
        with open(os.path.join(self.local, "MEMORY.md"), "a", encoding="utf-8") as f:
            f.write("- [só no Mac (27/09)](so-mac.md)\n")

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def rodar(self, alvo, aplicar):
        args = [self.local, self.repo, "--hoje", HOJE.isoformat(), "--alvo", str(alvo)] + (["--aplicar"] if aplicar else [])
        return ci.main(args)

    def ler(self, p, n="MEMORY.md"):
        with open(os.path.join(p, n), encoding="utf-8") as f:
            return f.read()

    def test_move_os_mais_antigos_nas_duas_copias_sem_perder_ponteiro(self):
        antes = {p: ci.links(self.ler(p)) for p in (self.local, self.repo)}
        self.assertEqual(self.rodar(200, True), 0)
        for p in (self.local, self.repo):
            idx, arq = self.ler(p), self.ler(p, "MEMORY-ARQUIVO.md")
            self.assertNotIn("proj-julho.md", idx)                  # data do arquivo (julho)
            self.assertNotIn("proj-agosto.md", idx)                 # data do gancho (agosto)
            self.assertIn("proj-julho.md", arq)
            self.assertEqual(ci.links(idx) | ci.links(arq), antes[p])
        self.assertIn("so-mac.md", self.ler(self.local))

    def test_protegidos_recentes_e_sem_data_ficam(self):
        self.rodar(10, True)                                        # alvo impossível: move tudo o que pode
        idx = self.ler(self.repo)
        for fica in ("topo.md", "lei-velha.md", "feedback-modo.md", "proj-recente.md", "proj-sem-data.md", "enche-0.md"):
            self.assertIn(fica, idx, fica)

    def test_simulacao_nao_grava_e_segunda_execucao_nao_move_nada(self):
        antes = self.ler(self.repo)
        self.rodar(200, False)
        self.assertEqual(self.ler(self.repo), antes)
        self.assertFalse(os.path.exists(os.path.join(self.repo, "MEMORY-ARQUIVO.md")))
        self.rodar(200, True)
        depois = self.ler(self.repo)
        self.rodar(200, True)
        self.assertEqual(self.ler(self.repo), depois)

    def test_pasta_sem_indice_recusa(self):
        self.assertEqual(ci.main([os.path.join(self.d, "nao-existe")]), 2)


if __name__ == "__main__":
    unittest.main(verbosity=1)
