#!/usr/bin/env python3
"""Testes do leads/ — só biblioteca padrão. Rode: python3 leads/testes/testar_leads.py"""
import http.server
import json
import os
import sys
import tempfile
import threading
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(AQUI))

import enriquecer  # noqa: E402
import normalizar as N  # noqa: E402
import scrape  # noqa: E402

CSV_GOSOM = (
    "input_id,link,title,category,address,open_hours,popular_times,website,phone,plus_code,review_count,"
    "review_rating,reviews_per_rating,latitude,longitude,cid,status,descriptions,reviews_link,thumbnail,"
    "timezone,price_range,data_id,street_view_url,place_id,images,reservations,order_online,menu,owner,complete_address,"
    "credit_cards_accepted,about,user_reviews,user_reviews_extended,emails\n"
    'x,https://maps.google.com/?cid=1,Clínica Fisio Aldeota,Clínica de fisioterapia,"R. Dr. José Lourenço, 2000 - Aldeota, Fortaleza - CE, 60115-282, Brazil",,,https://fisioaldeota.com.br,(85) 99999-0001,,127,4.8,,-3.73,-38.52,1,,,,,,,,,ChIJ-A,,,,,,,,,,,"contato@fisioaldeota.com.br, logo@2x.png"\n'
    'x,https://maps.google.com/?cid=2,Fisio Centro,Fisioterapeuta,"Av. Santos Dumont, 1500 - Loja 3 - Centro, Fortaleza - CE, Brazil",,,,(85) 3333-4444,,12,4.2,,-3.72,-38.53,2,,,,,,,,,ChIJ-B,,,,,,,,,,,\n'
    'x,https://maps.google.com/?cid=1,Clínica Fisio Aldeota,Clínica de fisioterapia,"R. Dr. José Lourenço, 2000 - Aldeota, Fortaleza - CE, Brazil",,,https://fisioaldeota.com.br,+55 85 99999-0001,,127,4.8,,-3.73,-38.52,1,,,,,,,,,ChIJ-A,,,,,,,,,,,\n'
    # ficha vazia, como o Google devolve quando serve a página sem conteúdo (só o link vem)
    'x,https://www.google.com/maps/place/Vazia/data=!4m7,,,,{},{},,,,0,0.000000,"{""1"":0}",0.000000,0.000000,,,,,,,,,,,,[],null,null,"{""link"":""""}","{""id"":""""}","{""borough"":""""}",,null,[],null,\n'
)


class Telefone(unittest.TestCase):
    def test_celular_com_mascara(self):
        self.assertEqual(N.telefone_br("(85) 99999-0001"), "5585999990001")

    def test_fixo(self):
        self.assertEqual(N.telefone_br("85 3333-4444"), "558533334444")

    def test_ja_com_ddi_e_mais(self):
        self.assertEqual(N.telefone_br("+55 85 99999-0001"), "5585999990001")

    def test_zero_de_operadora(self):
        self.assertEqual(N.telefone_br("085 99999-0001"), "5585999990001")

    def test_ddd_55_sem_ddi(self):
        self.assertEqual(N.telefone_br("(55) 3222-1234"), "555532221234")

    def test_internacional_vira_vazio(self):
        self.assertEqual(N.telefone_br("+1 305 555 0100"), "")
        self.assertEqual(N.telefone_br("0044 20 7946 0958"), "")
        self.assertEqual(N.telefone_br("+55 (85) 3333-4444"), "558533334444")
        self.assertEqual(N.telefone_br("abc"), "")
        self.assertEqual(N.telefone_br(""), "")

    def test_tipo_e_links(self):
        self.assertEqual(N.tipo_telefone("5585999990001"), "celular")
        self.assertEqual(N.tipo_telefone("558533334444"), "fixo")
        self.assertEqual(N.link_whatsapp("5585999990001"), "https://wa.me/5585999990001")
        self.assertEqual(N.link_whatsapp("558533334444"), "")
        self.assertEqual(N.formatar_telefone("5585999990001"), "+55 85 99999-0001")
        self.assertEqual(N.formatar_telefone("558533334444"), "+55 85 3333-4444")


class Endereco(unittest.TestCase):
    def test_completo(self):
        self.assertEqual(N.partes_endereco("R. Dr. José Lourenço, 2000 - Aldeota, Fortaleza - CE, 60115-282, Brazil"),
                         ("Aldeota", "Fortaleza", "CE"))

    def test_com_complemento(self):
        self.assertEqual(N.partes_endereco("Av. Santos Dumont, 1500 - Loja 3 - Centro, Fortaleza - CE, Brazil"),
                         ("Centro", "Fortaleza", "CE"))

    def test_sem_bairro(self):
        self.assertEqual(N.partes_endereco("R. X, 100, Sobral - CE, Brazil"), ("", "Sobral", "CE"))

    def test_lixo(self):
        self.assertEqual(N.partes_endereco(""), ("", "", ""))
        self.assertEqual(N.partes_endereco("Brazil"), ("", "", ""))


class Emails(unittest.TestCase):
    def test_lista_json_e_lixo(self):
        self.assertEqual(N.lista_emails('["Contato@x.com.br", "logo@2x.png", "a@sentry.io"]'), ["contato@x.com.br"])

    def test_lista_virgula(self):
        self.assertEqual(N.lista_emails("a@b.com, a@b.com; c@d.org"), ["a@b.com", "c@d.org"])

    def test_vazio(self):
        self.assertEqual(N.lista_emails(""), [])
        self.assertEqual(N.lista_emails(None), [])


class Normalizacao(unittest.TestCase):
    def test_linha_para_lead_e_dedupe(self):
        linhas = N.ler_csv(CSV_GOSOM)
        self.assertEqual(len(linhas), 4)
        self.assertEqual(linhas[0]["place_id"], "ChIJ-A")                       # 36 colunas reais alinhadas
        self.assertEqual(linhas[0]["emails"], "contato@fisioaldeota.com.br, logo@2x.png")
        linhas = [l for l in linhas if l["title"]]
        leads = N.deduplicar([N.normalizar(l, "fisio") for l in linhas])
        self.assertEqual(len(leads), 2)
        a = leads[0]
        self.assertEqual(a["telefone_e164"], "5585999990001")
        self.assertEqual(a["whatsapp"], "https://wa.me/5585999990001")
        self.assertEqual(a["emails"], "contato@fisioaldeota.com.br")
        self.assertEqual((a["bairro"], a["cidade"], a["uf"]), ("Aldeota", "Fortaleza", "CE"))
        self.assertEqual(a["sem_site"], "nao")
        self.assertEqual(a["nota"], 4.8)
        self.assertEqual(a["avaliacoes"], 127)
        b = leads[1]
        self.assertEqual(b["sem_site"], "sim")
        self.assertEqual(b["tipo_telefone"], "fixo")
        self.assertEqual(b["whatsapp"], "")

    def test_dedupe_sem_place_id_usa_nome_e_telefone(self):
        l1 = N.normalizar({"title": "Fisio X", "phone": "(85) 99999-0000"})
        l2 = N.normalizar({"title": "FISIO  X", "phone": "85999990000"})
        l3 = N.normalizar({"title": "Fisio X", "phone": "(85) 98888-0000"})
        self.assertEqual(len(N.deduplicar([l1, l2, l3])), 2)

    def test_ponte_apify_tem_os_campos_do_ranquear(self):
        lead = N.normalizar(N.ler_csv(CSV_GOSOM)[0], "fisio")
        ap = N.para_apify(lead)
        for campo in ("title", "phone", "phoneUnformatted", "website", "totalScore", "reviewsCount",
                      "categoryName", "address", "neighborhood", "url"):
            self.assertIn(campo, ap)
        self.assertEqual(ap["phoneUnformatted"], "+5585999990001")
        self.assertEqual(ap["emails"], ["contato@fisioaldeota.com.br"])
        self.assertEqual(ap["location"], {"lat": -3.73, "lng": -38.52})

    def test_csv_final_so_tem_colunas_definidas(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "x.csv")
            N.escrever_csv([N.normalizar(N.ler_csv(CSV_GOSOM)[0])], p)
            cab = open(p, encoding="utf-8").readline().strip().split(",")
            self.assertEqual(cab, N.COLUNAS)

    def test_csv_nao_executa_formula(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "x.csv")
            N.escrever_csv([N.normalizar({"title": "=HYPERLINK(\"http://mal\")", "phone": "+1 2"})], p)
            conteudo = open(p, encoding="utf-8").read()
            self.assertIn("'=HYPERLINK", conteudo)
            self.assertEqual(N.celula_segura("-3.7"), "'-3.7")
            self.assertEqual(N.celula_segura("Fisio"), "Fisio")
            self.assertEqual(N.celula_segura(4.8), 4.8)

    def test_resumo(self):
        leads = N.deduplicar([N.normalizar(l) for l in N.ler_csv(CSV_GOSOM) if l["title"]])
        md = N.resumo(leads, "Teste")
        self.assertIn("Negócios únicos: **2**", md)
        self.assertIn("sem site: 1", md)
        self.assertIn("LGPD", md)


class Enriquecimento(unittest.TestCase):
    HTML = ('<a href="https://www.instagram.com/fisioaldeota/">ig</a> <a href="https://facebook.com/sharer/sharer.php">x</a>'
            '<a href="https://www.facebook.com/FisioAldeota">fb</a> <a href="https://br.linkedin.com/company/fisio-aldeota">in</a>'
            '<a href="https://api.whatsapp.com/send?phone=5585999990001&text=Ola">zap</a> contato@fisioaldeota.com.br '
            'img@2x.png noreply@site.com')

    def test_redes(self):
        r = enriquecer.extrair_redes(self.HTML)
        self.assertEqual(r["instagram"], "https://www.instagram.com/fisioaldeota")
        self.assertEqual(r["facebook"], "https://www.facebook.com/FisioAldeota")
        self.assertEqual(r["linkedin"], "https://br.linkedin.com/company/fisio-aldeota")

    def test_emails(self):
        self.assertEqual(enriquecer.extrair_emails(self.HTML), ["contato@fisioaldeota.com.br"])

    def test_whatsapp_no_site(self):
        self.assertEqual(enriquecer.extrair_whatsapp(self.HTML), "5585999990001")
        self.assertEqual(enriquecer.extrair_whatsapp('href="https://wa.me/5585999990000?text=oi"'), "5585999990000")
        self.assertEqual(enriquecer.extrair_whatsapp('href="https://wa.me/%2B5585999990000"'), "5585999990000")
        self.assertEqual(enriquecer.extrair_whatsapp("<p>sem nada</p>"), "")

    def test_enriquecer_um_preenche_e_marca(self):
        lead = N.normalizar({"title": "Fisio", "phone": "(85) 3333-4444", "website": "https://x.com"})
        enriquecer.enriquecer_um(lead, self.HTML)
        self.assertEqual(lead["sem_redes"], "nao")
        self.assertEqual(lead["whatsapp_site"], "5585999990001")
        self.assertEqual(lead["whatsapp"], "https://wa.me/5585999990001")   # fixo no Maps, mas o site tem o zap
        self.assertEqual(lead["emails"], "contato@fisioaldeota.com.br")
        vazio = N.normalizar({"title": "Sem nada"})
        enriquecer.enriquecer_um(vazio, "")
        self.assertEqual(vazio["sem_redes"], "sim")


CSV_VAZIO = CSV_GOSOM.splitlines()[0] + "\n" + "\n".join([CSV_GOSOM.splitlines()[4]] * 3) + "\n"


class RedeSegura(unittest.TestCase):
    def test_destinos_proibidos(self):
        for u in ("http://127.0.0.1:8080/api/v1/jobs/x", "http://localhost/", "http://10.0.0.5/", "http://192.168.1.1/",
                  "http://169.254.169.254/latest/meta-data/", "http://[::1]/", "file:///etc/passwd", "javascript:alert(1)",
                  "ftp://x.com/", "http://metadata.google.internal/", "http://host.docker.internal/", "http://1.2.3.4:9/"):
            self.assertFalse(enriquecer.destino_permitido(u), u)

    def test_destino_publico_por_ip(self):
        self.assertTrue(enriquecer.destino_permitido("https://8.8.8.8/"))
        self.assertTrue(enriquecer.destino_permitido("http://1.1.1.1:8080/x"))

    def test_baixar_html_recusa_sem_tocar_a_rede(self):
        self.assertEqual(enriquecer.baixar_html("http://127.0.0.1:1/"), "")
        self.assertEqual(enriquecer.baixar_html("javascript:alert(1)"), "")

    def test_redirecionamento_para_rede_privada_e_bloqueado(self):
        class Redir(http.server.BaseHTTPRequestHandler):
            def log_message(self, *a): pass
            def do_GET(self):
                if self.path == "/robots.txt":
                    self.send_response(404); self.end_headers(); return
                self.send_response(302); self.send_header("Location", "http://127.0.0.1:1/segredo"); self.end_headers()
        srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Redir)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            url = f"http://127.0.0.1:{srv.server_address[1]}/"
            # o servidor de teste é loopback (proibido por destino_permitido); testamos o handler diretamente
            h = enriquecer._RedirecionamentoSeguro()
            with self.assertRaises(Exception):
                h.redirect_request(None, None, 302, "Found", {}, "http://127.0.0.1:1/segredo")
            self.assertEqual(enriquecer.baixar_html(url), "")
        finally:
            srv.shutdown(); srv.server_close()

    def test_robots_bloqueia(self):
        class Robots(http.server.BaseHTTPRequestHandler):
            def log_message(self, *a): pass
            def do_GET(self):
                corpo = b"User-agent: *\nDisallow: /privado\n" if self.path == "/robots.txt" else b"<a href='https://instagram.com/x'>x</a>"
                self.send_response(200); self.send_header("Content-Type", "text/plain" if self.path == "/robots.txt" else "text/html")
                self.send_header("Content-Length", str(len(corpo))); self.end_headers(); self.wfile.write(corpo)
        srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Robots)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            raiz = f"http://127.0.0.1:{srv.server_address[1]}"
            self.assertFalse(enriquecer.robots_permite(raiz + "/privado/x"))
            self.assertTrue(enriquecer.robots_permite(raiz + "/publico"))
        finally:
            srv.shutdown(); srv.server_close()


class ServidorFalso(http.server.BaseHTTPRequestHandler):
    """Imita a API do gosom: cria job, 'working' na 1ª consulta, 'ok' depois, CSV no download.
    Com `modo_datacenter`, o job completo devolve fichas vazias e só o fast_mode devolve dados."""
    consultas = 0
    modo_datacenter = False
    jobs = []

    def log_message(self, *a):  # silencioso
        pass

    def _json(self, codigo, obj):
        corpo = json.dumps(obj).encode()
        self.send_response(codigo); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(corpo))); self.end_headers(); self.wfile.write(corpo)

    def do_GET(self):
        if self.path == "/api/v1/jobs":
            return self._json(200, [])
        if self.path == "/api/v1/jobs/abc/download":
            ultimo = ServidorFalso.jobs[-1] if ServidorFalso.jobs else {}
            vazio = ServidorFalso.modo_datacenter and not ultimo.get("fast_mode")
            corpo = (CSV_VAZIO if vazio else CSV_GOSOM).encode("utf-8")
            self.send_response(200); self.send_header("Content-Type", "text/csv")
            self.send_header("Content-Length", str(len(corpo))); self.end_headers(); return self.wfile.write(corpo)
        if self.path == "/api/v1/jobs/abc":
            ServidorFalso.consultas += 1
            return self._json(200, {"ID": "abc", "Status": "working" if ServidorFalso.consultas == 1 else "ok"})
        self._json(404, {"erro": "não achei"})

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        corpo = json.loads(self.rfile.read(n) or b"{}")
        ServidorFalso.ultimo_job = corpo
        ServidorFalso.jobs.append(corpo)
        faltam = [c for c in ("keywords", "lat", "lon", "max_time") if c not in corpo]
        if faltam:
            return self._json(422, {"erro": faltam})
        self._json(201, {"id": "abc"})


class FluxoCompleto(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), ServidorFalso)
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{cls.srv.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown(); cls.srv.server_close()

    def test_ponta_a_ponta_sem_rede_externa(self):
        with tempfile.TemporaryDirectory() as d:
            campanha = os.path.join(d, "campanha")
            cod = scrape.main(["clínicas de fisioterapia em Fortaleza CE", "--cidade", "Fortaleza, CE", "--sem-rede-geo",
                               "--base-url", self.base, "--intervalo", "0", "--saida", d, "--nome", "teste",
                               "--campanha", campanha, "--bruto"])
            self.assertEqual(cod, 0)
            job = ServidorFalso.ultimo_job
            self.assertEqual(job["keywords"], ["clínicas de fisioterapia em Fortaleza CE"])
            self.assertEqual((job["lat"], job["lon"]), ("-3.7319", "-38.5267"))     # tabela interna, sem Nominatim
            self.assertEqual(job["lang"], "pt")
            self.assertTrue(job["email"])
            self.assertFalse(job["fast_mode"])
            self.assertEqual(job["max_time"], 600)
            self.assertNotIn("proxies", job)
            for ext in (".csv", ".json", ".md", "-bruto.csv"):
                self.assertTrue(os.path.exists(os.path.join(d, "teste" + ext)), ext)
            linhas = open(os.path.join(d, "teste.csv"), encoding="utf-8").read().strip().splitlines()
            self.assertEqual(len(linhas), 1 + 2)                                     # cabeçalho + 2 únicos
            raw = json.load(open(os.path.join(campanha, "raw", "teste.json"), encoding="utf-8"))
            self.assertEqual(raw[0]["title"], "Clínica Fisio Aldeota")

    def test_nome_nao_sai_da_pasta(self):
        with tempfile.TemporaryDirectory() as d:
            cod = scrape.main(["x", "--lat", "1", "--lon", "2", "--base-url", self.base, "--intervalo", "0",
                               "--saida", d, "--nome", "../../fora"])
            self.assertEqual(cod, 0)
            self.assertTrue(os.path.exists(os.path.join(d, "fora.csv")))
            self.assertEqual(sorted(f for f in os.listdir(d) if f.startswith("fora")), ["fora.csv", "fora.json", "fora.md"])
            self.assertEqual(scrape.slug("../../etc/x", 80), "etc-x")           # nunca sai da pasta de saída

    def test_rapido_manda_fast_mode_e_desliga_email(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(scrape.main(["x em Fortaleza CE", "--cidade", "Fortaleza, CE", "--sem-rede-geo", "--rapido",
                                          "--base-url", self.base, "--intervalo", "0", "--saida", d]), 0)
            self.assertTrue(ServidorFalso.ultimo_job["fast_mode"])
            self.assertFalse(ServidorFalso.ultimo_job["email"])

    def test_fallback_automatico_para_rapido_quando_fichas_vazias(self):
        ServidorFalso.modo_datacenter = True
        try:
            with tempfile.TemporaryDirectory() as d:
                antes = len(ServidorFalso.jobs)
                cod = scrape.main(["x", "--lat", "1", "--lon", "2", "--base-url", self.base, "--intervalo", "0", "--saida", d, "--nome", "fb"])
                self.assertEqual(cod, 0)
                novos = ServidorFalso.jobs[antes:]
                self.assertEqual([j["fast_mode"] for j in novos], [False, True])         # completo → rápido, sozinho
                linhas = open(os.path.join(d, "fb.csv"), encoding="utf-8").read().strip().splitlines()
                self.assertEqual(len(linhas), 1 + 2)
                antes = len(ServidorFalso.jobs)
                cod = scrape.main(["x", "--lat", "1", "--lon", "2", "--base-url", self.base, "--intervalo", "0", "--saida", d,
                                   "--nome", "sf", "--sem-fallback"])
                self.assertEqual(cod, 3)                                                   # sem fallback: avisa e sai com 3
                self.assertEqual(len(ServidorFalso.jobs) - antes, 1)
        finally:
            ServidorFalso.modo_datacenter = False

    def test_por_bairros_gera_um_termo_por_bairro(self):
        termos = scrape.expandir_bairros(["clínicas de fisioterapia em Fortaleza CE"], ["Aldeota", "Meireles"], "Fortaleza, CE")
        self.assertEqual(termos, ["clínicas de fisioterapia no bairro Aldeota, Fortaleza",
                                  "clínicas de fisioterapia no bairro Meireles, Fortaleza"])
        self.assertEqual(scrape.expandir_bairros(["dentistas"], ["Centro"], None), ["dentistas no bairro Centro"])
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(scrape.main(["dentistas em Fortaleza CE", "--cidade", "Fortaleza, CE", "--sem-rede-geo", "--rapido",
                                          "--por-bairros", "Aldeota, Meireles,Centro", "--base-url", self.base, "--intervalo", "0",
                                          "--saida", d]), 0)
            self.assertEqual(len(ServidorFalso.ultimo_job["keywords"]), 3)

    def test_sem_termo_e_scraper_fora(self):
        self.assertEqual(scrape.main(["--cidade", "Fortaleza, CE", "--sem-rede-geo"]), 1)
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(scrape.main(["x", "--lat", "1", "--lon", "2", "--base-url", "http://127.0.0.1:9", "--saida", d]), 1)

    def test_de_csv_reprocessa_sem_api_e_avisa_ficha_vazia(self):
        with tempfile.TemporaryDirectory() as d:
            bruto = os.path.join(d, "x-bruto.csv")
            open(bruto, "w", encoding="utf-8").write("\ufeff" + CSV_GOSOM)          # com BOM
            self.assertEqual(scrape.main(["--de-csv", bruto, "--saida", d, "--nome", "re"]), 0)
            linhas = open(os.path.join(d, "re.csv"), encoding="utf-8").read().strip().splitlines()
            self.assertEqual(len(linhas), 1 + 2)                                  # a ficha vazia não virou lead
            so_vazias = os.path.join(d, "v-bruto.csv")
            open(so_vazias, "w", encoding="utf-8").write(CSV_GOSOM.splitlines()[0] + "\n" + CSV_GOSOM.splitlines()[4] + "\n")
            self.assertEqual(scrape.main(["--de-csv", so_vazias, "--saida", d, "--nome", "v"]), 3)

    def test_cidade_desconhecida_sem_rede(self):
        self.assertIsNone(scrape.geocodificar("Vila Inexistente do Norte, XX", usar_rede=False))
        self.assertEqual(scrape.geocodificar("São Paulo, SP", usar_rede=False), (-23.5505, -46.6333))


if __name__ == "__main__":
    unittest.main(verbosity=1)
