#!/usr/bin/env python3
"""Testes do fundir-indice.py (v4) e do verificar-indice.py — Lei da Monotonia no índice.

Roda em CI (saude.yml) e no /manutencao:  python3 .claude/helpers/cerebro/testar-fundir.py
Fixtures sintéticas: reproduzem a forma do bug real (links agrupados numa linha) sem conteúdo privado.
"""
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
FUNDIR = os.path.join(AQUI, "fundir-indice.py")
VERIFICAR = os.path.join(AQUI, "verificar-indice.py")


def carregar(nome, caminho):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


fi = carregar("fundir_indice", FUNDIR)
vi = carregar("verificar_indice", VERIFICAR)


def alvos(linhas):
    return fi.alvos_de(linhas)


def ler(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


class TesteFusaoPorLink(unittest.TestCase):
    def test_link_agrupado_nao_some(self):
        """O bug real: local tem [A]; repo unido tem [A] · [B] na MESMA linha. v3 perdia B."""
        local = ["# Índice", "- ⚖️ [LEIS](leis.md) — nunca boleto"]
        repo = ["# Índice", "- ⚖️ [LEIS](leis.md) · [parcela mínima](lei-parcela.md) — nunca boleto · R$6"]
        saida, rel = fi.fundir(local, repo)
        self.assertEqual(alvos(saida), {"leis.md", "lei-parcela.md"})
        self.assertEqual(fi.faltantes(saida, local, repo), [])
        self.assertEqual(sum(1 for l in saida if "leis.md" in l), 1, "linha mais rica vence, sem duplicar")

    def test_primeiro_link_ja_visto_nao_engole_os_outros(self):
        """v3 pulava a linha inteira se o PRIMEIRO link já tinha aparecido."""
        local = ["- [A](a.md) — sozinho", "- [A](a.md) · [C](c.md) — agrupado depois"]
        repo = []
        saida, _ = fi.fundir(local, repo)
        self.assertIn("c.md", alvos(saida))
        self.assertEqual(fi.faltantes(saida, local, repo), [])

    def test_local_vence_o_texto_com_os_mesmos_links(self):
        local = ["- [A](a.md) — texto editado no local"]
        repo = ["- [A](a.md) — texto antigo do repo"]
        saida, rel = fi.fundir(local, repo)
        self.assertEqual(saida, ["- [A](a.md) — texto editado no local"])
        self.assertEqual(rel["preservadas_local"], 0)  # base já era o local

    def test_local_vence_texto_mesmo_quando_repo_e_a_base(self):
        local = ["- [A](a.md) — texto do local"]
        repo = ["- [A](a.md) — texto do repo", "- [B](b.md) — só no repo"]
        saida, rel = fi.fundir(local, repo)
        self.assertIn("- [A](a.md) — texto do local", saida)
        self.assertIn("b.md", alvos(saida))
        self.assertEqual(rel["preservadas_local"], 1)

    def test_cada_lado_com_link_exclusivo_mantem_as_duas_linhas(self):
        local = ["- [A](a.md) · [X](x.md) — local agrupou com X"]
        repo = ["- [A](a.md) · [Y](y.md) — repo agrupou com Y"]
        saida, rel = fi.fundir(local, repo)  # base = local (empate) → a linha do repo entra em RECUPERADAS
        self.assertEqual(alvos(saida), {"a.md", "x.md", "y.md"})
        self.assertIn(local[0], saida)
        self.assertIn(repo[0], saida)
        self.assertEqual(rel["duplicadas_por_seguranca"] + rel["recuperadas"], 1)

    def test_base_repo_com_link_exclusivo_dos_dois_lados_emite_as_duas(self):
        local = ["- [A](a.md) · [X](x.md) — local agrupou com X"]
        repo = ["- [A](a.md) · [Y](y.md) — repo agrupou com Y", "- [B](b.md)"]
        saida, rel = fi.fundir(local, repo)  # base = repo (mais links) → ramo "as duas ficam"
        self.assertEqual(alvos(saida), {"a.md", "x.md", "y.md", "b.md"})
        self.assertIn(local[0], saida)
        self.assertIn(repo[0], saida)
        self.assertEqual(rel["duplicadas_por_seguranca"], 1)
        self.assertEqual(rel["recuperadas"], 0)

    def test_revogada_nao_ressuscita_e_nao_conta_como_perda(self):
        local = ["- [A](a.md)"]
        repo = ["- [A](a.md)", "- [velha](velha.md) — banida", "- [A](a.md) · [velha](velha.md) mista"]
        rev = {"velha.md"}
        saida, rel = fi.fundir(local, repo, rev)
        self.assertNotIn("- [velha](velha.md) — banida", saida)
        self.assertEqual(fi.faltantes(saida, local, repo, rev), [])
        self.assertEqual(rel["revogadas"], 1)

    def test_local_vazio_preserva_o_repo(self):
        repo = ["# Índice", "", "## SETUP", "- [A](a.md)", "- [B](b.md) · [C](c.md)"]
        saida, _ = fi.fundir([], repo)
        self.assertEqual(saida, repo)

    def test_repo_vazio_preserva_o_local(self):
        local = ["# Índice", "- [A](a.md)"]
        saida, _ = fi.fundir(local, [])
        self.assertEqual(saida, local)

    def test_estrutura_e_secoes_preservadas(self):
        local = ["# Índice", "", "## QUEM É", "- [perfil](perfil.md)", "", "## SETUP", "- [sync](sync.md)"]
        repo = ["# Índice", "", "## QUEM É", "- [perfil](perfil.md)", "", "## SETUP", "- [sync](sync.md) · [novo](novo.md)"]
        saida, _ = fi.fundir(local, repo)
        self.assertEqual([l for l in saida if l.startswith("#")], ["# Índice", "## QUEM É", "## SETUP"])
        self.assertIn("novo.md", alvos(saida))

    def test_recuperadas_vao_para_secao_propria_sem_repetir_cabecalho(self):
        local = ["# Índice", "- [A](a.md)"]
        repo = ["# Outro", "- [Z](z.md)"]
        saida, rel = fi.fundir(local, repo)
        self.assertEqual(rel["recuperadas"], 1)
        self.assertEqual(saida.count(fi.CABECALHO_RECUPERADAS), 1)
        saida2, rel2 = fi.fundir(saida, ["- [W](w.md)"])
        self.assertEqual(saida2.count(fi.CABECALHO_RECUPERADAS), 1)
        self.assertEqual(alvos(saida2), {"a.md", "z.md", "w.md"})

    def test_idempotente(self):
        local = ["# Índice", "- [A](a.md) · [X](x.md)", "- [B](b.md) — local"]
        repo = ["# Índice", "- [A](a.md) · [Y](y.md)", "- [B](b.md) — repo", "- [C](c.md)"]
        saida, _ = fi.fundir(local, repo)
        self.assertEqual(fi.fundir(saida, saida)[0], saida)
        self.assertEqual(fi.fundir(saida, repo)[0], saida)
        self.assertEqual(fi.fundir(saida, local)[0], saida)

    def test_forma_do_indice_real_pre_uniao_vs_uniao(self):
        """Mesma forma do incidente 10/09: 4 links agrupados em 4 linhas diferentes do índice unido."""
        pre = ["# 🧠 Índice", "", "## LEIS", "- ⚖️ [LEIS](leis.md) — texto", "", "## PROJETOS",
               "- 👁️ [VISÃO](visao.md) — produto", "- 📺 [YOUTUBE](missao-yt.md) — vídeo",
               "", "## SETUP", "- 🔧 [Auditoria](auditoria.md) · [Severa](severa.md)"]
        unido = ["# 🧠 Índice", "", "## LEIS", "- ⚖️ [LEIS](leis.md) · [parcela](lei-parcela.md) — texto", "",
                 "## PROJETOS", "- 👁️ [VISÃO](visao.md) · [rede casa](rede-casa.md) — produto",
                 "- 📺 [YOUTUBE](missao-yt.md) · [projeto yt](projeto-yt.md) — vídeo", "",
                 "## SETUP", "- 🔧 [Auditoria](auditoria.md) · [Severa](severa.md) · [clickmax](clickmax.md)"]
        saida, _ = fi.fundir(pre, unido)
        self.assertEqual(fi.faltantes(saida, pre, unido), [])
        self.assertEqual(len(alvos(saida)), 9)


class TesteGuardaEmDisco(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.local = os.path.join(self.d, "local", "MEMORY.md")
        self.repo = os.path.join(self.d, "repo", "MEMORY.md")
        os.makedirs(os.path.dirname(self.local))
        os.makedirs(os.path.dirname(self.repo))
        with open(self.local, "w", encoding="utf-8") as f:
            f.write("# I\n- [A](a.md)\n")
        with open(self.repo, "w", encoding="utf-8") as f:
            f.write("# I\n- [A](a.md) · [B](b.md)\n")

    def rodar(self, *args):
        return subprocess.run([sys.executable, FUNDIR, *args, self.local, self.repo],
                              capture_output=True, text=True)

    def test_guarda_recusa_gravar_e_nao_toca_nos_arquivos(self):
        antes = (ler(self.local), ler(self.repo))
        r = self.rodar("--simular-perda", "b.md")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("RECUSOU GRAVAR", r.stderr)
        self.assertIn("b.md", r.stderr)
        self.assertEqual((ler(self.local), ler(self.repo)), antes)

    def test_simular_nao_grava(self):
        antes = ler(self.local)
        r = self.rodar("--simular")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("SIMULACAO", r.stdout)
        self.assertEqual(ler(self.local), antes)

    def test_grava_nos_dois_e_sem_lixo_temporario(self):
        r = self.rodar()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(ler(self.local), ler(self.repo))
        self.assertIn("b.md", ler(self.local))
        self.assertEqual([n for n in os.listdir(os.path.dirname(self.local)) if n.startswith(".")], [])

    def test_cli_sem_argumentos_falha_alto(self):
        r = subprocess.run([sys.executable, FUNDIR], capture_output=True, text=True)
        self.assertEqual(r.returncode, 64)


class TesteVerificarIndice(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        for n in ("a.md", "b.md", "c-revogada.md", "d-orfa.md"):
            with open(os.path.join(self.d, n), "w") as f:
                f.write("x")
        with open(os.path.join(self.d, "REVOGADAS.md"), "w") as f:
            f.write("# banidas\nc-revogada.md\n")
        with open(os.path.join(self.d, "MEMORY.md"), "w") as f:
            f.write("# I\n- [A](a.md)\n- [B](b.md) · [X](x-nao-existe.md)\n")

    def test_orfa_e_quebrado(self):
        orfas, quebrados, n_p, n_a = vi.verificar(self.d)
        self.assertEqual(orfas, ["d-orfa.md"])
        self.assertEqual(quebrados, ["x-nao-existe.md"])
        self.assertEqual((n_p, n_a), (3, 4))

    def test_exit_1_com_orfa_e_0_sem(self):
        r = subprocess.run([sys.executable, VERIFICAR, self.d], capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertIn("d-orfa.md", r.stdout)
        with open(os.path.join(self.d, "MEMORY.md"), "a") as f:
            f.write("- [D](d-orfa.md)\n")
        r = subprocess.run([sys.executable, VERIFICAR, self.d], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout)
        r = subprocess.run([sys.executable, VERIFICAR, self.d, "--estrito"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 1, "quebrado falha no modo estrito")

    def test_quieto_so_fala_com_problema(self):
        r = subprocess.run([sys.executable, VERIFICAR, self.d, "--quieto"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertIn("ORFA", r.stdout)
        r = subprocess.run([sys.executable, VERIFICAR, os.path.join(self.d, "nao-existe"), "--quieto"],
                           capture_output=True, text=True)
        self.assertEqual((r.returncode, r.stdout), (0, ""))


class TesteAutoDeteccao(unittest.TestCase):
    """O cofre real do Mac é ~/.claude/projects/-Users-<user>-Claude/memory, não ~/.claude/memory."""

    def setUp(self):
        self.home = tempfile.mkdtemp()
        self.cofre = os.path.join(self.home, ".claude", "projects", "-Users-teste-Claude", "memory")
        os.makedirs(self.cofre)
        with open(os.path.join(self.cofre, "MEMORY.md"), "w") as f:
            f.write("# I\n- [A](a.md)\n")
        with open(os.path.join(self.cofre, "a.md"), "w") as f:
            f.write("x")
        # pasta de projeto SEM MEMORY.md não conta
        os.makedirs(os.path.join(self.home, ".claude", "projects", "-Users-teste-outro", "memory"))
        self.env = dict(os.environ, HOME=self.home)
        self.env.pop("CEREBRO_MEMORIA", None)
        self.env.pop("CEREBRO_PRIVADO", None)

    def rodar(self, *args):
        return subprocess.run([sys.executable, VERIFICAR, *args], capture_output=True, text=True, env=self.env)

    def test_listar_acha_o_cofre_de_projeto(self):
        r = self.rodar("--listar")
        self.assertEqual(r.stdout.strip().splitlines(), [self.cofre])

    def test_cofre_do_repo_tambem_entra_sem_repetir(self):
        repo = os.path.join(self.home, "Claude", "cerebro-backup", "claude-config", "memory")
        os.makedirs(repo)
        with open(os.path.join(repo, "MEMORY.md"), "w") as f:
            f.write("# I\n")
        r = self.rodar("--listar")
        self.assertEqual(r.stdout.strip().splitlines(), [self.cofre, repo])

    def test_auto_quieto_silencia_quando_integro_e_acusa_orfa(self):
        r = self.rodar("--quieto")
        self.assertEqual((r.returncode, r.stdout), (0, ""))
        with open(os.path.join(self.cofre, "orfa.md"), "w") as f:
            f.write("x")
        r = self.rodar("--quieto")
        self.assertEqual(r.returncode, 1)
        self.assertIn("orfa.md", r.stdout)
        self.assertIn(self.cofre, r.stdout)

    def test_sem_cofre_nenhum_e_silencio_com_exit_0(self):
        vazio = tempfile.mkdtemp()
        env = dict(self.env, HOME=vazio)
        r = subprocess.run([sys.executable, VERIFICAR, "--quieto"], capture_output=True, text=True, env=env)
        self.assertEqual((r.returncode, r.stdout), (0, ""))
        r = subprocess.run([sys.executable, VERIFICAR], capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0)
        self.assertIn("nenhum cofre", r.stdout)

    def test_variavel_cerebro_memoria_vem_primeiro(self):
        outro = tempfile.mkdtemp()
        with open(os.path.join(outro, "MEMORY.md"), "w") as f:
            f.write("# I\n")
        env = dict(self.env, CEREBRO_MEMORIA=outro)
        r = subprocess.run([sys.executable, VERIFICAR, "--listar"], capture_output=True, text=True, env=env)
        self.assertEqual(r.stdout.strip().splitlines()[0], outro)


if __name__ == "__main__":
    unittest.main(verbosity=2)
