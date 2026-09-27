#!/usr/bin/env python3
"""Testes da memoria_viva.py — corpus sintético em pasta temporária, sem rede, sem cache.
Roda no saude.yml e no /manutencao:  python3 .claude/helpers/cerebro/testar-memoria-viva.py
"""
import datetime as dt
import importlib.util
import json
import os
import shutil
import tempfile
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("mv", os.path.join(AQUI, "memoria_viva.py"))
mv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mv)

HOJE = dt.date(2026, 9, 27)


def mem(nome, desc, corpo, modified=None):
    fm = f"---\nname: {nome}\ndescription: {desc}\n"
    if modified:
        fm += f"metadata:\n  modified: {modified}T10:00:00Z\n"
    return fm + "---\n\n" + corpo + "\n"


class Base(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.mem = os.path.join(self.dir, "memory")
        os.makedirs(self.mem)
        arquivos = {
            "produto-preco.md": mem("produto-preco", "Gargalo do produto é PREÇO (27/09)",
                                    "ROAS baixo no Meta. Ver [[auditoria-meta]] e [[lei-nunca-boleto]].", "2026-09-27"),
            "auditoria-meta.md": mem("auditoria-meta", "Auditoria da conta de anúncios (24/09)",
                                     "Pixel duplicado, evento de compra ausente.", "2026-09-24"),
            "lei-nunca-boleto.md": mem("lei-nunca-boleto", "🔴 LEI: nunca boleto", "Checkout só Pix e cartão."),
            "receita-antiga.md": mem("receita-antiga", "anotação solta de 2025", "Nada ligado. 2025-01-10."),
            "curso-video.md": mem("curso-video", "Como estudar curso que só tem vídeo (26/09)",
                                  "Transcrição por whisper; ver (metodo-extra.md)."),
            "metodo-extra.md": mem("metodo-extra", "ffmpeg só áudio", "Baixar m3u8 e transcrever."),
            "MEMORY.md": "# índice — ignorado\n- [x](produto-preco.md)\n",
            "MEMORY-ARQUIVO.md": "# índice de arquivo — ignorado\n[[produto-preco]] [[curso-video]] [[auditoria-meta]]\n",
        }
        for n, t in arquivos.items():
            with open(os.path.join(self.mem, n), "w", encoding="utf-8") as f:
                f.write(t)
        self.estado_arq = os.path.join(self.dir, "estado.json")
        self.docs = mv.carregar([self.mem], HOJE, cache=False)
        self.estado = mv.ler_estado(self.estado_arq)

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)


class Corpus(Base):
    def test_ignora_indice_e_le_frontmatter(self):
        self.assertNotIn("MEMORY.md", self.docs)
        self.assertNotIn("MEMORY-ARQUIVO.md", self.docs)          # hub de índice não entra no grafo
        self.assertEqual(len(self.docs), 6)
        self.assertEqual(self.docs["produto-preco.md"].data, dt.date(2026, 9, 27))

    def test_links_wiki_e_markdown(self):
        self.assertEqual(self.docs["produto-preco.md"].links, {"auditoria-meta.md", "lei-nunca-boleto.md"})
        self.assertEqual(self.docs["curso-video.md"].links, {"metodo-extra.md"})

    def test_data_br_sem_ano_nao_vai_para_o_futuro(self):
        self.assertEqual(self.docs["curso-video.md"].data, dt.date(2026, 9, 26))
        m = mv.RE_DATA_BR.search("(15/12)")
        self.assertEqual(mv._data_br(m, HOJE), dt.date(2025, 12, 15))

    def test_importancia_por_marca(self):
        self.assertGreater(self.docs["lei-nunca-boleto.md"].marca, self.docs["receita-antiga.md"].marca)

    def test_acento_e_caixa_nao_importam(self):
        self.assertEqual(mv.tokens("PREÇO Preco preço"), ["preco", "preco", "preco"])


class Busca(Base):
    def test_texto_acha_o_certo_primeiro(self):
        r = mv.buscar(self.docs, self.estado, "preço do produto", hoje=HOJE)
        self.assertEqual(r[0]["id"], "produto-preco.md")

    def test_associacao_traz_vizinho_sem_palavra_em_comum(self):
        r = mv.buscar(self.docs, self.estado, "produto ROAS", hoje=HOJE)
        ids = {x["id"]: x for x in r}
        self.assertIn("auditoria-meta.md", ids)                 # não contém "produto" nem "roas"
        self.assertEqual(ids["auditoria-meta.md"]["via"], "associação")

    def test_contexto_agentir_reordena_sem_inventar_tema(self):
        sem = [x["id"] for x in mv.buscar(self.docs, self.estado, "estudar", hoje=HOJE, vagas_assoc=0)]
        com = [x["id"] for x in mv.buscar(self.docs, self.estado, "estudar", hoje=HOJE, vagas_assoc=0,
                                          contexto="baixar m3u8 e transcrever com ffmpeg")]
        self.assertIn("metodo-extra.md", com)
        self.assertNotIn("metodo-extra.md", sem)
        self.assertEqual(mv.buscar(self.docs, self.estado, "xyzzy", hoje=HOJE, contexto="produto ffmpeg"), [])

    def test_ultima_resposta_do_transcript(self):
        p = os.path.join(self.dir, "t.jsonl")
        with open(p, "w", encoding="utf-8") as f:
            f.write(json.dumps({"type": "user", "message": {"content": "oi"}}) + "\n")
            f.write(json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": "primeira"}]}}) + "\n")
            f.write("linha quebrada {\n")
            f.write(json.dumps({"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "x"}]}}) + "\n")
            f.write(json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": "segunda resposta"}]}}) + "\n")
        self.assertEqual(mv.ultima_resposta(p), "segunda resposta")
        self.assertEqual(mv.ultima_resposta(os.path.join(self.dir, "nao-existe")), "")

    def test_consulta_vazia_ou_sem_acerto(self):
        self.assertEqual(mv.buscar(self.docs, self.estado, "", hoje=HOJE), [])
        self.assertEqual(mv.buscar(self.docs, self.estado, "xyzzyqwerty", hoje=HOJE), [])

    def test_scores_em_faixa_e_texto_ordenado(self):
        r = mv.buscar(self.docs, self.estado, "curso vídeo transcrição", hoje=HOJE)
        self.assertTrue(all(0 <= v <= 1 for x in r for v in x["partes"].values()))
        t = [x["score"] for x in r if x["via"] == "texto"]
        self.assertEqual(t, sorted(t, reverse=True))

    def test_associacao_nunca_desaloja_acerto_de_texto(self):
        r = mv.buscar(self.docs, self.estado, "produto ROAS", k=3, hoje=HOJE)
        self.assertEqual(r[0]["id"], "produto-preco.md")
        vias = [x["via"] for x in r]
        self.assertEqual(vias, sorted(vias, key=lambda v: v != "texto"))   # texto antes, ↔ depois
        self.assertLessEqual(vias.count("associação"), mv.VAGAS_ASSOCIACAO)

    def test_recencia_decai_meia_vida(self):
        d = self.docs["produto-preco.md"]
        self.assertAlmostEqual(mv.recencia(d, self.estado, HOJE + dt.timedelta(days=30), 30), 0.5, places=6)
        self.assertEqual(mv.recencia(self.docs["lei-nunca-boleto.md"], self.estado, HOJE, 30), 0.5)  # sem data: neutra


class Hebb(Base):
    def test_sinapse_cresce_monotona_e_nunca_passa_de_1(self):
        k = mv.chave_sinapse("curso-video.md", "receita-antiga.md")
        ws = []
        for _ in range(200):
            mv.hebb(self.estado, ["curso-video.md", "receita-antiga.md"], True, HOJE)
            ws.append(self.estado["sinapses"][k])
        self.assertEqual(ws, sorted(ws))
        self.assertLessEqual(ws[-1], 1.0)
        self.assertGreater(ws[-1], 0.3)

    def test_sucesso_esperado_reforca_menos_que_surpreendente(self):
        """GRPO/vantagem relativa: o 50º sucesso seguido quase não muda a sinapse; o 1º muda muito."""
        k = mv.chave_sinapse("a.md", "b.md")
        mv.hebb(self.estado, ["a.md", "b.md"], True, HOJE)
        primeiro = self.estado["sinapses"][k]
        for _ in range(48):
            mv.hebb(self.estado, ["a.md", "b.md"], True, HOJE)
        antes = self.estado["sinapses"][k]
        mv.hebb(self.estado, ["a.md", "b.md"], True, HOJE)
        self.assertLess(self.estado["sinapses"][k] - antes, primeiro / 10)
        # fracasso depois de muitos sucessos = surpresa grande = queda forte
        mv.hebb(self.estado, ["a.md", "b.md"], False, HOJE)
        self.assertLess(self.estado["sinapses"][k], antes)

    def test_fracasso_enfraquece_e_nunca_fica_negativa(self):
        k = mv.chave_sinapse("a.md", "b.md")
        mv.hebb(self.estado, ["a.md", "b.md"], True, HOJE)
        w1 = self.estado["sinapses"][k]
        for _ in range(100):
            mv.hebb(self.estado, ["a.md", "b.md"], False, HOJE)
        self.assertLess(self.estado["sinapses"][k], w1)
        self.assertGreaterEqual(self.estado["sinapses"][k], 0.0)

    def test_sinapse_aprendida_passa_a_puxar_na_busca(self):
        antes = {x["id"] for x in mv.buscar(self.docs, self.estado, "produto preço", k=10, hoje=HOJE)}
        self.assertNotIn("curso-video.md", antes)
        for _ in range(5):
            mv.hebb(self.estado, ["produto-preco.md", "curso-video.md"], True, HOJE)
        depois = {x["id"]: x for x in mv.buscar(self.docs, self.estado, "produto preço", k=10, hoje=HOJE)}
        self.assertIn("curso-video.md", depois)
        self.assertEqual(depois["curso-video.md"]["via"], "associação")

    def test_confianca_beta(self):
        self.assertEqual(mv.confianca(self.estado, "x.md"), 0.5)
        mv.hebb(self.estado, ["x.md"], True, HOJE)
        mv.hebb(self.estado, ["x.md"], True, HOJE)
        self.assertAlmostEqual(mv.confianca(self.estado, "x.md"), 0.75)


class Episodios(Base):
    def cli(self, *args):
        return mv.main(["--mem", self.mem, "--estado", self.estado_arq, "--hoje", HOJE.isoformat(), *args])

    def test_episodio_grava_e_recusa_memoria_inexistente(self):
        self.assertEqual(self.cli("episodio", "--tarefa", "t", "--resultado", "ok", "--fonte", "teste",
                                  "--usadas", "produto-preco.md", "auditoria-meta.md", "--licao", "l"), 0)
        e = mv.ler_estado(self.estado_arq)
        self.assertEqual(len(e["episodios"]), 1)
        self.assertEqual(len(e["sinapses"]), 1)
        self.assertEqual(self.cli("episodio", "--tarefa", "t", "--resultado", "ok", "--fonte", "humano", "--usadas", "nao-existe.md"), 2)
        self.assertEqual(len(mv.ler_estado(self.estado_arq)["episodios"]), 1)

    def test_consolidacao_exige_repeticao(self):
        self.cli("episodio", "--tarefa", "a", "--resultado", "ok", "--fonte", "metrica", "--licao", "checar pixel antes de subir campanha no Meta")
        self.assertEqual(mv.consolidar(mv.ler_estado(self.estado_arq)), [])
        self.cli("episodio", "--tarefa", "b", "--resultado", "falha", "--fonte", "metrica", "--licao", "checar o pixel antes de subir a campanha")
        self.cli("episodio", "--tarefa", "c", "--resultado", "ok", "--fonte", "metrica", "--licao", "transcrever áudio com whisper")
        regras = mv.consolidar(mv.ler_estado(self.estado_arq))
        self.assertEqual(len(regras), 1)
        self.assertEqual(regras[0]["suporte"], 2)
        self.assertAlmostEqual(regras[0]["sucesso"], 0.5)
        self.assertEqual(self.cli("consolidar", "--marcar"), 0)
        self.assertTrue(mv.consolidar(mv.ler_estado(self.estado_arq))[0]["ja_consolidada"])

    def test_frias_lista_e_nunca_apaga(self):
        antes = sorted(os.listdir(self.mem))
        self.assertEqual(self.cli("frias", "--limiar", "0.2"), 0)
        self.assertEqual(sorted(os.listdir(self.mem)), antes)
        ids = [r["id"] for r in mv.frias(self.docs, self.estado, 0.2, HOJE)]
        self.assertEqual(ids, ["receita-antiga.md"])        # velha, sem link; as ligadas não entram

    def test_estado_json_atomico(self):
        self.cli("episodio", "--tarefa", "t", "--resultado", "ok", "--fonte", "teste")
        with open(self.estado_arq, encoding="utf-8") as f:
            self.assertEqual(json.load(f)["versao"], 1)
        self.assertFalse(os.path.exists(self.estado_arq + ".tmp"))


class PisoFormaSkill(Base):
    def test_piso_zera_consulta_sem_relevancia_e_mantem_a_boa(self):
        self.assertEqual(mv.buscar(self.docs, self.estado, "ok pode seguir", hoje=HOJE, piso=50.0), [])
        self.assertTrue(mv.buscar(self.docs, self.estado, "produto preço ROAS", hoje=HOJE, piso=0.5))

    def test_contexto_pode_salvar_consulta_vaga_do_piso(self):
        vaga = mv.buscar(self.docs, self.estado, "e agora", hoje=HOJE, piso=0.5)
        com = mv.buscar(self.docs, self.estado, "e agora curso", hoje=HOJE, piso=0.5,
                        contexto="transcrever curso video whisper ffmpeg")
        self.assertEqual(vaga, [])
        self.assertTrue(com)

    def cli(self, *args):
        return mv.main(["--mem", self.mem, "--estado", self.estado_arq, "--hoje", HOJE.isoformat(), *args])

    def test_ruido_registra_mas_nao_ensina_sinapse(self):
        self.cli("episodio", "--tarefa", "t", "--resultado", "ok", "--fonte", "teste", "--forma", "ruido",
                 "--usadas", "produto-preco.md", "auditoria-meta.md")
        e = mv.ler_estado(self.estado_arq)
        self.assertEqual(len(e["episodios"]), 1)
        self.assertEqual(e["episodios"][0]["forma"], "ruido")
        self.assertEqual(e["sinapses"], {})

    def test_skill_como_usada_liga_uso_ao_resultado(self):
        self.assertEqual(self.cli("episodio", "--tarefa", "caçada", "--resultado", "falha", "--fonte", "humano",
                                  "--usadas", "skill:cacar-produto", "produto-preco.md"), 0)
        e = mv.ler_estado(self.estado_arq)
        self.assertIn("skill:cacar-produto", e["usos"])
        self.assertEqual(e["usos"]["skill:cacar-produto"]["ok"], 0)


class BrechasDaMutacao(Base):
    """Testes escritos a partir dos mutantes sobreviventes de 27/09 (mutacao.py: 12/25 mortos antes)."""

    def test_data_mais_recente_do_corpo(self):
        fm, corpo = mv.frontmatter("---\nname: x\n---\nvisto em 2025-01-02 e revisto em 2026-09-20; nota 2024-05-05\n")
        self.assertEqual(mv.data_de(fm, corpo, HOJE), dt.date(2026, 9, 20))

    def test_contexto_forte_resgata_pergunta_abaixo_do_piso(self):
        q, ctx = "estudar", "baixar m3u8 transcrever ffmpeg audio metodo extra"
        topo_q = max(mv.bm25(self.docs, q).values())
        topo_c = max(mv.bm25(self.docs, ctx).values())
        self.assertGreater(topo_c, topo_q)
        piso = (topo_q + topo_c) / 2
        self.assertEqual(mv.buscar(self.docs, self.estado, q, hoje=HOJE, piso=piso), [])
        self.assertTrue(mv.buscar(self.docs, self.estado, q, hoje=HOJE, piso=piso, contexto=ctx))

    def test_vagas_de_associacao_exatas(self):
        todos = mv.buscar(self.docs, self.estado, "produto ROAS", k=100, hoje=HOJE, vagas_assoc=100)
        disponiveis = sum(1 for x in todos if x["via"] == "associação")
        r = mv.buscar(self.docs, self.estado, "produto ROAS", k=3, hoje=HOJE)
        self.assertEqual(sum(1 for x in r if x["via"] == "associação"), min(mv.VAGAS_ASSOCIACAO, disponiveis, 2))
        self.assertLessEqual(len(r), 3)

    def test_jaccard(self):
        self.assertEqual(mv.jaccard("", "pixel campanha"), 0.0)
        self.assertAlmostEqual(mv.jaccard("pixel campanha", "pixel checkout"), 1 / 3)

    def test_bm25_sem_documentos_nao_divide_por_zero(self):
        self.assertEqual(mv.bm25({}, "qualquer coisa"), {})

    def test_sinapse_zerada_nao_cria_aresta(self):
        viz = mv.grafo(self.docs, {mv.chave_sinapse("curso-video.md", "receita-antiga.md"): 0.0})
        self.assertNotIn("receita-antiga.md", viz["curso-video.md"])
        viz = mv.grafo(self.docs, {mv.chave_sinapse("curso-video.md", "receita-antiga.md"): 0.4})
        self.assertIn("receita-antiga.md", viz["curso-video.md"])

    def test_consolidacao_ordena_memorias_por_frequencia(self):
        est = {"episodios": [{"id": "e1", "resultado": "ok", "licao": "checar pixel antes", "usadas": ["x.md", "y.md"]},
                             {"id": "e2", "resultado": "ok", "licao": "checar o pixel antes", "usadas": ["y.md"]}],
               "consolidados": []}
        self.assertEqual(mv.consolidar(est)[0]["memorias"], ["y.md", "x.md"])


class FonteEAvaliacao(Base):
    def test_episodio_sem_fonte_e_recusado(self):
        with self.assertRaises(SystemExit):
            mv.main(["--mem", self.mem, "--estado", self.estado_arq, "episodio", "--tarefa", "t", "--resultado", "ok"])
        with self.assertRaises(SystemExit):
            mv.main(["--mem", self.mem, "--estado", self.estado_arq, "episodio", "--tarefa", "t",
                     "--resultado", "ok", "--fonte", "juiz"])

    def test_avaliacao_pelo_gabarito_do_indice(self):
        with open(os.path.join(self.mem, "MEMORY.md"), "w", encoding="utf-8") as f:
            f.write("- 💰 **[Gargalo do produto é o preço (27/09)](produto-preco.md)** — ROAS baixo\n"
                    "- 🎥 [Estudar curso só em vídeo](curso-video.md) — transcrição\n- linha sem link\n")
        gab = mv.gabarito_do_indice(self.mem)
        self.assertEqual([a for _, a in gab], ["produto-preco.md", "curso-video.md"])
        self.assertNotIn("27/09", gab[0][0])
        res = mv.avaliar(self.docs, self.estado, gab, HOJE)
        self.assertEqual(res["bm25 puro"]["casos"], 2)
        self.assertEqual(res["pilha calibrada (canal de texto)"]["recall@5"], 1.0)


class LoboFrontal(Base):
    def regra_e_estado(self):
        est = {"episodios": [{"id": "e1", "tarefa": "t", "resultado": "ok", "fonte": "teste", "licao": "checar pixel"},
                             {"id": "e2", "tarefa": "u", "resultado": "falha", "fonte": "humano", "licao": "checar o pixel"}]}
        return {"episodios": ["e1", "e2"]}, est

    def test_abstracao_valida_exige_limite_contraexemplo_e_evidencia(self):
        r, est = self.regra_e_estado()
        vistos = {}

        def chat(sistema, usuario):
            vistos["u"] = usuario
            return 'ok {"regra":"Checar o pixel antes de subir campanha","quando_aplica":"campanha nova",' \
                   '"quando_nao_aplica":"campanha sem conversão","contraexemplo":"tráfego para perfil","evidencia":["e1","e2"],"confianca":0.6}'
        j = mv.abstrair_llm(r, est, chat)
        self.assertTrue(j["valida"])
        self.assertIn("fonte=teste", vistos["u"])

    def test_abstracao_sem_limite_ou_com_evidencia_inventada_e_invalida(self):
        r, est = self.regra_e_estado()
        j = mv.abstrair_llm(r, est, lambda s, u: '{"regra":"x","contraexemplo":"y","evidencia":["e1"]}')
        self.assertFalse(j["valida"])
        self.assertIn("quando_nao_aplica", j["faltam"])
        j = mv.abstrair_llm(r, est, lambda s, u: '{"regra":"x","quando_nao_aplica":"z","contraexemplo":"y","evidencia":["e9"]}')
        self.assertFalse(j["valida"])
        self.assertFalse(mv.abstrair_llm(r, est, lambda s, u: "sem json")["valida"])


class Cache(Base):
    def test_cache_reaproveita_e_invalida_por_mudanca(self):
        os.environ["XDG_CACHE_HOME"] = os.path.join(self.dir, "cache")
        try:
            a = mv.carregar([self.mem], HOJE)
            b = mv.carregar([self.mem], HOJE)
            self.assertEqual(set(a), set(b))
            p = os.path.join(self.mem, "auditoria-meta.md")
            with open(p, "a", encoding="utf-8") as f:
                f.write("\nproduto agora aparece aqui também, com texto novo bem maior\n")
            c = mv.carregar([self.mem], HOJE)
            self.assertIn("produto", c["auditoria-meta.md"].tf)
            cdir = os.path.join(self.dir, "cache", "memoria-viva")
            self.assertTrue(os.listdir(cdir))
            self.assertFalse(os.path.commonpath([cdir, self.mem]) == self.mem)
        finally:
            os.environ.pop("XDG_CACHE_HOME", None)


if __name__ == "__main__":
    unittest.main(verbosity=1)
