#!/usr/bin/env python3
"""Testes do leads/ — só biblioteca padrão. Rode: python3 leads/testes/testar_leads.py"""
import http.server
import json
import os
import sys
import tempfile
import threading
import time
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(AQUI))

import enriquecer  # noqa: E402
import normalizar as N  # noqa: E402
import scrape  # noqa: E402

CABECALHO = (
    "input_id,link,title,category,address,open_hours,popular_times,website,phone,plus_code,review_count,"
    "review_rating,reviews_per_rating,latitude,longitude,cid,status,descriptions,reviews_link,thumbnail,"
    "timezone,price_range,data_id,street_view_url,place_id,images,reservations,order_online,menu,owner,complete_address,"
    "credit_cards_accepted,about,user_reviews,user_reviews_extended,emails\n")
CSV_GOSOM = (
    CABECALHO
    + 'x,https://maps.google.com/?cid=1,Clínica Fisio Aldeota,Clínica de fisioterapia,"R. Dr. José Lourenço, 2000 - Aldeota, Fortaleza - CE, 60115-282, Brazil",,,https://fisioaldeota.com.br,(85) 99999-0001,,127,4.8,,-3.73,-38.52,1,,,,,,,0x1:0xa,,ChIJ-A,,,,,,,,,,,"contato@fisioaldeota.com.br, logo@2x.png"\n'
    + 'x,https://maps.google.com/?cid=2,Fisio Centro,Fisioterapeuta,"Av. Santos Dumont, 1500 - Loja 3 - Centro, Fortaleza - CE, Brazil",,,,(85) 3333-4444,,12,4.2,,-3.72,-38.53,2,,,,,,,0x2:0xb,,ChIJ-B,,,,,,,,,,,\n'
    + 'x,https://maps.google.com/?cid=1,Clínica Fisio Aldeota,Clínica de fisioterapia,"R. Dr. José Lourenço, 2000 - Aldeota, Fortaleza - CE, Brazil",,,https://fisioaldeota.com.br,+55 85 99999-0001,,127,4.8,,-3.73,-38.52,1,,,,,,,0x1:0xa,,ChIJ-A,,,,,,,,,,,\n'
    # ficha vazia, como o Google devolve quando serve a página sem conteúdo (só o link vem)
    + 'x,https://www.google.com/maps/place/Vazia/data=!4m7,,,,{},{},,,,0,0.000000,"{""1"":0}",0.000000,0.000000,,,,,,,,,,,[],null,null,"{""link"":""""}","{""id"":""""}","{""borough"":""""}",,null,[],null,\n'
)
LINHA_VAZIA = CSV_GOSOM.splitlines()[4] + "\n"
CSV_VAZIO = CABECALHO + LINHA_VAZIA * 3
# fast_mode real: place_id e cid vazios, data_id preenchido e único, link vazio
CSV_RAPIDO = (CABECALHO
              + 'x,,Clínica Vida,Clínica,"R. A, 1 - Centro, Fortaleza - CE",,,,+558599999-0002,,10,5.0,,-3.70,-38.50,,,,,,,,0x1:0x11,,,,,,,,,,,,,\n'
              + 'x,,Clínica Vida,Clínica,"R. B, 99 - Aldeota, Fortaleza - CE",,,,+558599999-0003,,20,4.0,,-3.71,-38.51,,,,,,,,0x1:0x22,,,,,,,,,,,,,\n')


def ler(caminho):
    with open(caminho, encoding="utf-8") as f:
        return f.read()


class Telefone(unittest.TestCase):
    def test_formatos_brasileiros(self):
        for bruto in ("(85) 99999-0001", "85 9 9999-0001", "+55 85 99999-0001", "+55 (85) 9.9999-0001",
                      "085 99999-0001", "0 85 99999-0001", "5585999990001", "85999990001 (WhatsApp)"):
            self.assertEqual(N.telefone_br(bruto), "5585999990001", bruto)

    def test_fixo(self):
        self.assertEqual(N.telefone_br("85 3333-4444"), "558533334444")
        self.assertEqual(N.telefone_br("+55 (85) 3333-4444"), "558533334444")
        self.assertEqual(N.telefone_br("85 9876-5432"), "558598765432")          # fixo antigo começando em 9

    def test_ddd_55_sem_ddi(self):
        self.assertEqual(N.telefone_br("(55) 3222-1234"), "555532221234")
        self.assertEqual(N.telefone_br("55 55 99999-1234"), "5555999991234")

    def test_recusas(self):
        for bruto in ("+1 305 555 0100", "0044 20 7946 0958", "1 305 555 0100", "abc", "", "55", "+55",
                      "99999-0001", "0800 123 4567", "0300 313 1234", "+55 85 99999 0001 / 3333-4444",
                      "٨٥٩٩٧٦٢٤٢٢١", "85 3333-44445", "(20) 99999-0001"):
            self.assertEqual(N.telefone_br(bruto), "", bruto)

    def test_ramal_cortado(self):
        self.assertEqual(N.telefone_br("Tel: 85 3333-4444 ramal 2"), "558533334444")
        self.assertEqual(N.telefone_br("85 3333-4444 r. 12"), "558533334444")

    def test_tipo_e_links(self):
        self.assertEqual(N.tipo_telefone("5585999990001"), "celular")
        self.assertEqual(N.tipo_telefone("558533334444"), "fixo")
        self.assertEqual(N.link_whatsapp("5585999990001"), "https://wa.me/5585999990001")
        self.assertEqual(N.link_whatsapp("558533334444"), "")
        self.assertEqual(N.formatar_telefone("5585999990001"), "(85) 99999-0001")   # sem '+' → sem apóstrofo no CSV
        self.assertEqual(N.formatar_telefone("558533334444"), "(85) 3333-4444")
        self.assertEqual(N.formatar_telefone(""), "")


class Endereco(unittest.TestCase):
    def test_completo(self):
        self.assertEqual(N.partes_endereco("R. Dr. José Lourenço, 2000 - Aldeota, Fortaleza - CE, 60115-282, Brazil"),
                         ("Aldeota", "Fortaleza", "CE"))

    def test_com_complemento_e_hifen_no_logradouro(self):
        self.assertEqual(N.partes_endereco("Av. Santos Dumont, 1500 - Loja 3 - Centro, Fortaleza - CE, Brazil"),
                         ("Centro", "Fortaleza", "CE"))
        self.assertEqual(N.partes_endereco("Av. Rio - Mar, 10, Fortaleza - CE"), ("", "Fortaleza", "CE"))

    def test_sem_bairro_e_sem_espaco(self):
        self.assertEqual(N.partes_endereco("R. X, 100, Sobral - CE, Brazil"), ("", "Sobral", "CE"))
        self.assertEqual(N.partes_endereco("Fortaleza-CE"), ("", "Fortaleza", "CE"))

    def test_travessao_e_ingles(self):
        self.assertEqual(N.partes_endereco("R. X, 10 – Centro, Fortaleza – CE"), ("Centro", "Fortaleza", "CE"))
        self.assertEqual(N.partes_endereco("Fortaleza, State of Ceará, Brazil"), ("", "Fortaleza", "CE"))
        self.assertEqual(N.partes_endereco("R. X, 10 - Centro, Fortaleza, State of Ceará, Brazil"), ("Centro", "Fortaleza", "CE"))

    def test_lixo(self):
        self.assertEqual(N.partes_endereco(""), ("", "", ""))
        self.assertEqual(N.partes_endereco("Brazil"), ("", "", ""))


class Emails(unittest.TestCase):
    def test_lista_json_e_lixo(self):
        self.assertEqual(N.lista_emails('["Contato@x.com.br", "logo@2x.png", "a@sentry.io", 5, {"a": 1}]'), ["contato@x.com.br"])
        self.assertEqual(N.lista_emails('{"a": 1}'), [])

    def test_lista_virgula(self):
        self.assertEqual(N.lista_emails("a@b.com, a@b.com; c@d.org"), ["a@b.com", "c@d.org"])

    def test_vazio_e_lixo_de_cdn(self):
        self.assertEqual(N.lista_emails(""), [])
        self.assertEqual(N.lista_emails(None), [])
        for e in ("x@cloudfront.net", "admin@site.local", "a@b.invalid", "contato@fisio.com.brTelefone", "noreply@x.com"):
            self.assertEqual(N.email_valido(e), "", e)
        self.assertEqual(N.email_valido("Contato@Clinica.COM.BR"), "contato@clinica.com.br")


class Numeros(unittest.TestCase):
    def test_inf_nan_overflow_nao_derrubam(self):
        for v in ("inf", "nan", "1e400", "-inf", "abc", None, ""):
            self.assertEqual(N._int(v), 0, v)
            self.assertEqual(N._float(v), 0.0, v)
        self.assertEqual(N._float("4,8"), 4.8)
        self.assertEqual(N._int("127.0"), 127)


class Normalizacao(unittest.TestCase):
    def test_linha_para_lead_e_dedupe(self):
        linhas = N.ler_csv(CSV_GOSOM)
        self.assertEqual(len(linhas), 4)
        self.assertEqual(linhas[0]["place_id"], "ChIJ-A")                       # 36 colunas reais alinhadas
        self.assertEqual(linhas[0]["data_id"], "0x1:0xa")
        self.assertEqual(linhas[0]["emails"], "contato@fisioaldeota.com.br, logo@2x.png")
        linhas = [l for l in linhas if l["title"]]
        leads = N.deduplicar([N.normalizar(l, "fisio") for l in linhas])
        self.assertEqual(len(leads), 2)
        a = leads[0]
        self.assertEqual(a["telefone_e164"], "5585999990001")
        self.assertEqual(a["telefone"], "(85) 99999-0001")
        self.assertEqual(a["whatsapp"], "https://wa.me/5585999990001")
        self.assertEqual(a["emails"], "contato@fisioaldeota.com.br")
        self.assertEqual((a["bairro"], a["cidade"], a["uf"]), ("Aldeota", "Fortaleza", "CE"))
        self.assertEqual(a["sem_site"], "nao")
        self.assertEqual(a["nota"], 4.8)
        self.assertEqual(a["avaliacoes"], 127)
        self.assertEqual(a["maps"], "https://maps.google.com/?cid=1")
        b = leads[1]
        self.assertEqual(b["sem_site"], "sim")
        self.assertEqual(b["tipo_telefone"], "fixo")
        self.assertEqual(b["whatsapp"], "")

    def test_dedupe_por_cid_e_por_data_id(self):
        l1 = N.normalizar({"title": "A", "cid": "9"}); l2 = N.normalizar({"title": "B", "cid": "9"})
        self.assertEqual(len(N.deduplicar([l1, l2])), 1)
        rapidos = [N.normalizar(l) for l in N.ler_csv(CSV_RAPIDO)]
        self.assertEqual(len(N.deduplicar(rapidos)), 2)                           # homônimos no fast_mode: data_id separa
        self.assertTrue(rapidos[0]["maps"].startswith("https://www.google.com/maps/search/?api=1&query=Cl"))

    def test_dedupe_sem_ids_usa_nome_telefone_coordenada_endereco(self):
        l1 = N.normalizar({"title": "Fisio X", "phone": "(85) 99999-0000"})
        l2 = N.normalizar({"title": "FISIO  X", "phone": "85999990000"})
        l3 = N.normalizar({"title": "Fisio X", "phone": "(85) 98888-0000"})
        l4 = N.normalizar({"title": "Clínica Vida", "address": "R. A, 1 - Centro, Fortaleza - CE"})
        l5 = N.normalizar({"title": "Clínica Vida", "address": "R. B, 99 - Aldeota, Fortaleza - CE"})
        self.assertEqual(len(N.deduplicar([l1, l2, l3, l4, l5])), 4)
        longo = "Clínica " + "x" * 120
        l6 = N.normalizar({"title": longo + " A", "phone": "(85) 99999-0000"})
        l7 = N.normalizar({"title": longo + " B", "phone": "(85) 99999-0000"})
        self.assertEqual(len(N.deduplicar([l6, l7])), 2)                          # nome longo não colapsa

    def test_ponte_apify_tem_os_campos_do_ranquear(self):
        lead = N.normalizar(N.ler_csv(CSV_GOSOM)[0], "fisio")
        ap = N.para_apify(lead)
        for campo in ("title", "phone", "phoneUnformatted", "website", "totalScore", "reviewsCount",
                      "categoryName", "address", "neighborhood", "url"):
            self.assertIn(campo, ap)
        self.assertEqual(ap["phoneUnformatted"], "+5585999990001")
        self.assertEqual(ap["emails"], ["contato@fisioaldeota.com.br"])
        self.assertEqual(ap["location"], {"lat": -3.73, "lng": -38.52})
        self.assertEqual(ap["dataId"], "0x1:0xa")

    def test_csv_final_so_tem_colunas_definidas_e_sem_apostrofo_no_telefone(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "x.csv")
            N.escrever_csv([N.normalizar(N.ler_csv(CSV_GOSOM)[0])], p)
            conteudo = ler(p)
            self.assertEqual(conteudo.splitlines()[0].split(","), N.COLUNAS)
            self.assertIn(",(85) 99999-0001,", conteudo)
            self.assertNotIn("'(85)", conteudo)

    def test_csv_nao_executa_formula(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "x.csv")
            N.escrever_csv([N.normalizar({"title": "=HYPERLINK(\"http://mal\")", "phone": "+1 2"})], p)
            self.assertIn("'=HYPERLINK", ler(p))
        for v in ("=x", "+x", "-3.7", "@x", "\tx", "\rx"):
            self.assertEqual(N.celula_segura(v), "'" + v, v)
        self.assertEqual(N.celula_segura("Fisio"), "Fisio")
        self.assertEqual(N.celula_segura(4.8), 4.8)

    def test_csv_com_quebra_de_linha_crua_nao_derruba(self):
        hostil = CABECALHO + 'x,l,Clínica\rQuebrada,c,"R. X, 1 - Centro, Fortaleza - CE",,,,(85) 3333-4444,,1,4.0,,,,,,,,,,,,,,,,,,,,,,,,\n'
        linhas = N.ler_csv(hostil)
        self.assertEqual(len(linhas), 1)
        self.assertIn("Clínica", linhas[0]["title"])
        self.assertEqual(N.ler_csv("x,y\r\n1,2\r\n"), [{"x": "1", "y": "2"}])

    def test_slug_trunca_e_bom(self):
        self.assertEqual(len(N.slug("a" * 500)), 60)
        self.assertEqual(N.slug("../../etc/x", 80), "etc-x")
        self.assertEqual(N.slug("🚀"), "busca")
        self.assertEqual(N.ler_csv("﻿" + CSV_GOSOM)[0]["input_id"], "x")

    def test_resumo(self):
        leads = N.deduplicar([N.normalizar(l) for l in N.ler_csv(CSV_GOSOM) if l["title"]])
        md = N.resumo(leads, "Teste", notas=["obs | x"])
        self.assertIn("Negócios únicos: **2**", md)
        self.assertIn("sem site: 1", md)
        self.assertIn("LGPD", md)
        self.assertIn("obs \\| x", md)
        md2 = N.resumo([N.normalizar({"title": "A | B"})], "t")
        self.assertIn("| A \\| B |", md2)


class Enriquecimento(unittest.TestCase):
    HTML = ('<a href="https://www.instagram.com/fisioaldeota/">ig</a> <a href="https://facebook.com/sharer/sharer.php">x</a>'
            '<script src="https://www.instagram.com/embed.js"></script> <a href="https://www.facebook.com/v12.0/plugins">p</a>'
            '<a href="https://www.facebook.com/FisioAldeota">fb</a> <a href="https://br.linkedin.com/company/fisio-aldeota">in</a>'
            '<a href="https://api.whatsapp.com/send?text=Ola&amp;phone=5585999990001">zap</a> contato@fisioaldeota.com.br '
            'img@2x.png noreply@site.com <span>mail@fisio.com.brTelefone</span>')

    def test_redes(self):
        r = enriquecer.extrair_redes(enriquecer.preparar_html(self.HTML))
        self.assertEqual(r["instagram"], "https://www.instagram.com/fisioaldeota")
        self.assertEqual(r["facebook"], "https://www.facebook.com/FisioAldeota")
        self.assertEqual(r["linkedin"], "https://br.linkedin.com/company/fisio-aldeota")
        lixo = ('<a href="https://instagram.com/p/abc">p</a><a href="https://instagram.com/explore/tags/x">t</a>'
                '<a href="https://facebook.com/profile.php?id=1">x</a><a href="https://facebook.com/l.php?u=x">l</a>'
                '<a href="https://www.instagram.com/static/x.js">s</a>')
        self.assertEqual(enriquecer.extrair_redes(lixo), {"instagram": "", "facebook": "", "linkedin": ""})

    def test_emails(self):
        self.assertEqual(enriquecer.extrair_emails(self.HTML), ["contato@fisioaldeota.com.br"])
        self.assertEqual(enriquecer.extrair_emails("fale: contato@x.com.br. ok"), ["contato@x.com.br"])
        self.assertEqual(enriquecer.extrair_emails("mailto:A@B.CO.UK?subject=x"), ["a@b.co.uk"])

    def test_whatsapp_no_site(self):
        self.assertEqual(enriquecer.extrair_whatsapp(enriquecer.preparar_html(self.HTML)), "5585999990001")
        for h, esperado in ((' href="https://wa.me/5585999990000?text=oi"', "5585999990000"),
                            (' href="https://wa.me/%2B5585999990000"', "5585999990000"),
                            ('"whatsapp://send?text=oi&phone=+5585999990000"', "5585999990000"),
                            ('"https:\\/\\/api.whatsapp.com\\/send?phone=5585999990000"', "5585999990000"),
                            (' href="https://wa.me/message/ABCDEF"', ""), ("<p>sem nada</p>", "")):
            self.assertEqual(enriquecer.extrair_whatsapp(enriquecer.preparar_html(h)), esperado, h)

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

    def test_site_que_ja_e_rede_social_conta_sem_visitar(self):
        self.assertEqual(enriquecer.rede_da_url("https://www.instagram.com/drjorge/")[0], "instagram")
        self.assertEqual(enriquecer.rede_da_url("https://www.instagram.com/p/abc")[0], "")
        l = N.normalizar({"title": "X", "website": "https://www.instagram.com/drjorge"})
        est = enriquecer.enriquecer([l])
        self.assertEqual(l["instagram"], "https://www.instagram.com/drjorge")
        self.assertEqual(l["sem_redes"], "nao")
        self.assertEqual(est["sites"], 0)

    def test_decodificacao_gzip_e_charset(self):
        import gzip
        corpo = gzip.compress("<p>olá contato@x.com.br</p>".encode("utf-8"))
        self.assertIn("contato@x.com.br", enriquecer._decodificar(corpo, "text/html"))
        self.assertIn("ação", enriquecer._decodificar("ação".encode("latin-1"), "text/html; charset=iso-8859-1"))
        self.assertIn("ação", enriquecer._decodificar(b'<meta charset="latin-1">' + "ação".encode("latin-1"), ""))


class RedeSegura(unittest.TestCase):
    def test_destinos_proibidos(self):
        for u in ("http://127.0.0.1:8080/api/v1/jobs/x", "http://localhost/", "http://10.0.0.5/", "http://192.168.1.1/",
                  "http://169.254.169.254/latest/meta-data/", "http://[::1]/", "file:///etc/passwd", "javascript:alert(1)",
                  "ftp://x.com/", "http://metadata.google.internal/", "http://host.docker.internal/", "http://1.2.3.4:9/",
                  "http://127.0.0.1.nip.io/", "http://localtest.me/", "http://10-0-0-1.sslip.io/", "http://127-0-0-1.x.com/",
                  "http://0.0.0.0/", "http://100.64.0.1/", "http://x.com:65536/"):
            self.assertFalse(enriquecer.destino_permitido(u), u)

    def test_destino_publico_por_ip(self):
        self.assertTrue(enriquecer.destino_permitido("https://8.8.8.8/"))
        self.assertTrue(enriquecer.destino_permitido("http://1.1.1.1:8080/x"))

    def test_baixar_html_recusa_sem_tocar_a_rede(self):
        self.assertEqual(enriquecer.baixar_html("http://127.0.0.1:1/"), "")
        self.assertEqual(enriquecer.baixar_html("javascript:alert(1)"), "")
        self.assertEqual(enriquecer.baixar_html(""), "")

    def test_redirecionamento_para_rede_privada_e_bloqueado(self):
        h = enriquecer._RedirecionamentoSeguro()
        with self.assertRaises(Exception):
            h.redirect_request(None, None, 302, "Found", {}, "http://127.0.0.1:1/segredo")
        with self.assertRaises(Exception):
            h.redirect_request(None, None, 302, "Found", {}, "file:///etc/passwd")

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
    Modos: `modo_datacenter` (completo devolve fichas vazias; só fast_mode traz dados), `modo_preso` (nunca sai de
    working), `modo_quebrado` (status 500 e depois JSON inválido antes de responder certo), `download` (corpo fixo)."""
    consultas = 0
    modo_datacenter = False
    modo_preso = False
    modo_quebrado = 0
    download = None
    jobs = []

    def log_message(self, *a):  # silencioso
        pass

    def _json(self, codigo, obj):
        corpo = json.dumps(obj).encode()
        self.send_response(codigo); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(corpo))); self.end_headers(); self.wfile.write(corpo)

    def _bruto(self, codigo, corpo, tipo):
        self.send_response(codigo); self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo))); self.end_headers(); self.wfile.write(corpo)

    def do_GET(self):
        if self.path == "/api/v1/jobs":
            return self._json(200, [])
        if self.path.endswith("/download"):
            if ServidorFalso.download is not None:
                return self._bruto(200, ServidorFalso.download.encode("utf-8"), "text/csv")
            ultimo = ServidorFalso.jobs[-1] if ServidorFalso.jobs else {}
            vazio = ServidorFalso.modo_datacenter and not ultimo.get("fast_mode")
            return self._bruto(200, (CSV_VAZIO if vazio else CSV_GOSOM).encode("utf-8"), "text/csv")
        if self.path.startswith("/api/v1/jobs/"):
            ServidorFalso.consultas += 1
            if ServidorFalso.modo_quebrado > 0:
                ServidorFalso.modo_quebrado -= 1
                return self._json(500, {"erro": "interno"}) if ServidorFalso.modo_quebrado % 2 else self._bruto(200, b"{nao-json", "application/json")
            if ServidorFalso.modo_preso:
                return self._json(200, {"ID": "abc", "Status": "working"})
            return self._json(200, {"ID": "abc", "Status": "working" if ServidorFalso.consultas == 1 else "ok"})
        self._json(404, {"erro": "não achei"})

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        corpo = json.loads(self.rfile.read(n) or b"{}")
        ServidorFalso.ultimo_job = corpo
        ServidorFalso.jobs.append(corpo)
        faltam = [c for c in ("keywords", "lat", "lon", "max_time") if c not in corpo]
        if faltam or len(corpo.get("lang", "")) != 2:
            return self._json(422, {"erro": faltam or "invalid lang"})
        self._json(201, {"id": "abc"})

    def do_DELETE(self):
        self._json(200, {"ok": True})


class FluxoCompleto(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), ServidorFalso)
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{cls.srv.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown(); cls.srv.server_close()

    def setUp(self):
        ServidorFalso.modo_datacenter = False; ServidorFalso.modo_preso = False
        ServidorFalso.modo_quebrado = 0; ServidorFalso.download = None

    def rodar(self, *args):
        return scrape.main(["--base-url", self.base, "--intervalo", "0", *args])

    def test_ponta_a_ponta_sem_rede_externa(self):
        with tempfile.TemporaryDirectory() as d:
            campanha = os.path.join(d, "campanha")
            cod = self.rodar("clínicas de fisioterapia em Fortaleza CE", "--cidade", "Fortaleza, CE", "--sem-rede-geo",
                             "--saida", d, "--nome", "teste", "--campanha", campanha, "--bruto")
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
            self.assertEqual(len(ler(os.path.join(d, "teste.csv")).strip().splitlines()), 1 + 2)   # cabeçalho + 2 únicos
            with open(os.path.join(campanha, "raw", "teste.json"), encoding="utf-8") as f:
                self.assertEqual(json.load(f)[0]["title"], "Clínica Fisio Aldeota")

    def test_cidade_sai_do_termo_sem_cidade(self):
        self.assertEqual(scrape.cidade_do_termo("clínicas de fisioterapia em Fortaleza CE"), "Fortaleza, CE")
        self.assertEqual(scrape.cidade_do_termo("dentistas em São Paulo - SP"), "São Paulo, SP")
        self.assertEqual(scrape.cidade_do_termo("lojas de Sobral CE"), "Sobral, CE")
        self.assertEqual(scrape.cidade_do_termo("pizzarias"), "")
        for c in ("Fortaleza, CE", "Fortaleza CE", "Fortaleza - CE", "fortaleza"):
            self.assertEqual(scrape.geocodificar(c, usar_rede=False), (-3.7319, -38.5267), c)
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(self.rodar("clínicas de fisioterapia em Fortaleza CE", "--sem-rede-geo", "--saida", d), 0)
            self.assertEqual(ServidorFalso.ultimo_job["lat"], "-3.7319")

    def test_rapido_manda_fast_mode_e_desliga_email(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(self.rodar("x em Fortaleza CE", "--cidade", "Fortaleza, CE", "--sem-rede-geo", "--rapido", "--saida", d), 0)
            self.assertTrue(ServidorFalso.ultimo_job["fast_mode"])
            self.assertFalse(ServidorFalso.ultimo_job["email"])

    def test_fallback_automatico_para_rapido_quando_fichas_vazias(self):
        ServidorFalso.modo_datacenter = True
        with tempfile.TemporaryDirectory() as d:
            antes = len(ServidorFalso.jobs)
            inicio = time.time()
            cod = self.rodar("x", "--lat", "1", "--lon", "2", "--saida", d, "--nome", "fb")
            self.assertEqual(cod, 0)
            self.assertGreaterEqual(time.time() - inicio, 4.5)                     # pausa antes do 2º job
            novos = ServidorFalso.jobs[antes:]
            self.assertEqual([j["fast_mode"] for j in novos], [False, True])         # completo → rápido, sozinho
            self.assertEqual(len(ler(os.path.join(d, "fb.csv")).strip().splitlines()), 1 + 2)
            self.assertIn("2º job", ler(os.path.join(d, "fb.md")))
            antes = len(ServidorFalso.jobs)
            cod = self.rodar("x", "--lat", "1", "--lon", "2", "--saida", d, "--nome", "sf", "--sem-fallback")
            self.assertEqual(cod, 3)                                                   # sem fallback: avisa e sai com 3
            self.assertEqual(len(ServidorFalso.jobs) - antes, 1)

    def test_por_bairros_gera_um_termo_por_bairro(self):
        termos = scrape.expandir_bairros(["clínicas de fisioterapia em Fortaleza CE"], ["Aldeota", "Meireles"], "Fortaleza, CE")
        self.assertEqual(termos, ["clínicas de fisioterapia no bairro Aldeota, Fortaleza",
                                  "clínicas de fisioterapia no bairro Meireles, Fortaleza"])
        self.assertEqual(scrape.expandir_bairros(["dentistas"], ["Centro"], None), ["dentistas no bairro Centro"])
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(self.rodar("dentistas em Fortaleza CE", "--cidade", "Fortaleza, CE", "--sem-rede-geo", "--rapido",
                                        "--por-bairros", "Aldeota, Meireles,Centro", "--saida", d), 0)
            self.assertEqual(len(ServidorFalso.ultimo_job["keywords"]), 3)
            self.assertEqual(self.rodar("dentistas", "--lat", "1", "--lon", "2", "--por-bairros", "/nao/existe.txt", "--saida", d), 1)

    def test_arquivo_com_comentario_indentado_e_bom(self):
        with tempfile.TemporaryDirectory() as d:
            arq = os.path.join(d, "t.txt")
            with open(arq, "w", encoding="utf-8") as f:
                f.write("﻿# cabeçalho\n  # indentado\n\nfisio em Fortaleza CE\r\nfisio em Fortaleza CE\n")
            self.assertEqual(self.rodar("--arquivo", arq, "--sem-rede-geo", "--rapido", "--saida", d), 0)
            self.assertEqual(ServidorFalso.ultimo_job["keywords"], ["fisio em Fortaleza CE"])

    def test_validacao_de_argumentos(self):
        with tempfile.TemporaryDirectory() as d:
            for args in (("x", "--lat", "1"), ("x", "--lat", "1", "--lon", "999"), ("x", "--lat", "1", "--lon", "2", "--profundidade", "0"),
                         ("x", "--lat", "1", "--lon", "2", "--max-tempo", "0"), ("x", "--lat", "1", "--lon", "2", "--raio", "-1"),
                         ("x", "--lat", "1", "--lon", "2", "--zoom", "99"), ("x", "--lat", "1", "--lon", "2", "--idioma", "portugues"),
                         ("--lat", "1", "--lon", "2"), ("--termo", "", "--lat", "1", "--lon", "2")):
                self.assertEqual(self.rodar(*args, "--saida", d), 1, args)
            self.assertEqual(len(ServidorFalso.jobs), len(ServidorFalso.jobs))

    def test_nome_nao_sai_da_pasta(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(self.rodar("x", "--lat", "1", "--lon", "2", "--saida", d, "--nome", "../../fora"), 0)
            self.assertEqual(sorted(f for f in os.listdir(d) if f.startswith("fora")), ["fora.csv", "fora.json", "fora.md"])

    def test_de_csv_reprocessa_sem_api_e_avisa_ficha_vazia(self):
        with tempfile.TemporaryDirectory() as d:
            bruto = os.path.join(d, "x-bruto.csv")
            with open(bruto, "w", encoding="utf-8") as f:
                f.write("﻿" + CSV_GOSOM)                                          # com BOM
            self.assertEqual(scrape.main(["--de-csv", bruto, "--saida", d, "--nome", "re"]), 0)
            self.assertEqual(len(ler(os.path.join(d, "re.csv")).strip().splitlines()), 1 + 2)   # a ficha vazia não virou lead
            so_vazias = os.path.join(d, "v-bruto.csv")
            with open(so_vazias, "w", encoding="utf-8") as f:
                f.write(CSV_VAZIO)
            self.assertEqual(scrape.main(["--de-csv", so_vazias, "--saida", d, "--nome", "v"]), 3)
            self.assertEqual(scrape.main(["--de-csv", "/nao/existe.csv", "--saida", d]), 1)
            arquivo = os.path.join(d, "arquivo")
            open(arquivo, "w").close()
            self.assertEqual(scrape.main(["--de-csv", bruto, "--saida", arquivo]), 1)       # --saida é arquivo: erro limpo

    def test_download_que_nao_e_csv_e_vazio(self):
        with tempfile.TemporaryDirectory() as d:
            ServidorFalso.download = "<!DOCTYPE html><html>index</html>"
            self.assertEqual(self.rodar("x", "--lat", "1", "--lon", "2", "--saida", d), 1)
            ServidorFalso.download = "a,b\n1,2\n"
            self.assertEqual(self.rodar("x", "--lat", "1", "--lon", "2", "--saida", d), 1)
            ServidorFalso.download = ""
            self.assertEqual(self.rodar("x", "--lat", "1", "--lon", "2", "--saida", d), 2)
            ServidorFalso.download = CABECALHO
            self.assertEqual(self.rodar("x", "--lat", "1", "--lon", "2", "--saida", d), 2)

    def test_api_instavel_e_job_preso(self):
        with tempfile.TemporaryDirectory() as d:
            ServidorFalso.modo_quebrado = 2                                            # 500 e depois JSON inválido
            self.assertEqual(self.rodar("x", "--lat", "1", "--lon", "2", "--saida", d, "--nome", "inst"), 0)
            ServidorFalso.modo_preso = True
            s = scrape.Scraper(self.base)
            inicio = time.time()
            self.assertEqual(s.esperar("abc", 0, 0), "timeout")
            self.assertLess(time.time() - inicio, 10)
            self.assertEqual(self.rodar("x", "--lat", "1", "--lon", "2", "--saida", d, "--max-tempo", "30"), 1)
            ServidorFalso.modo_preso = False
            self.assertEqual(self.rodar("--job", "abc", "--saida", d, "--nome", "retomado"), 0)   # retoma sem criar job
            self.assertTrue(os.path.exists(os.path.join(d, "retomado.csv")))

    def test_pending_nao_e_terminal(self):
        s = scrape.Scraper(self.base)
        for st in ("pending", "working", "desconhecido"):
            self.assertNotIn(st, ("ok", "failed"))
        self.assertEqual(s.status("abc") in ("working", "ok"), True)

    def test_sem_termo_e_scraper_fora(self):
        self.assertEqual(scrape.main(["--cidade", "Fortaleza, CE", "--sem-rede-geo"]), 1)
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(scrape.main(["x", "--lat", "1", "--lon", "2", "--base-url", "http://127.0.0.1:9", "--saida", d]), 1)

    def test_motor_docker_sem_docker(self):
        caminho = os.environ.get("PATH", "")
        os.environ["PATH"] = "/nao/existe"
        try:
            with tempfile.TemporaryDirectory() as d:
                self.assertEqual(scrape.main(["x", "--lat", "1", "--lon", "2", "--motor", "docker", "--saida", d]), 1)
        finally:
            os.environ["PATH"] = caminho

    def test_cidade_desconhecida_sem_rede(self):
        self.assertIsNone(scrape.geocodificar("Vila Inexistente do Norte, XX", usar_rede=False))
        self.assertEqual(scrape.geocodificar("São Paulo, SP", usar_rede=False), (-23.5505, -46.6333))


class Env(unittest.TestCase):
    def test_env_com_export_e_precedencia(self):
        caminho = os.path.join(scrape.AQUI, ".env")
        existia = os.path.exists(caminho)
        if existia:
            self.skipTest("leads/.env existe nesta máquina; não sobrescrever")
        for k in ("SCRAPER_PORT", "PROXIES", "SCRAPER_BASE_URL"):
            os.environ.pop(k, None)
        try:
            with open(caminho, "w", encoding="utf-8") as f:
                f.write("export SCRAPER_PORT=8099\nPROXIES\nSCRAPER_BASE_URL='http://x:1'\nOUTRA=1\n")
            scrape.carregar_env()
            self.assertEqual(os.environ.get("SCRAPER_PORT"), "8099")
            self.assertEqual(os.environ.get("SCRAPER_BASE_URL"), "http://x:1")
            self.assertNotIn("PROXIES", os.environ)
            self.assertNotIn("OUTRA", os.environ)
        finally:
            os.remove(caminho)
            for k in ("SCRAPER_PORT", "PROXIES", "SCRAPER_BASE_URL"):
                os.environ.pop(k, None)


if __name__ == "__main__":
    unittest.main(verbosity=1)
