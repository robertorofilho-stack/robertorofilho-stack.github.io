#!/usr/bin/env python3
"""Busca negócios no Google Maps pelo scraper local (gosom/google-maps-scraper) e devolve leads limpos,
prontos para contato: telefone no padrão brasileiro, link de WhatsApp, e-mail, site, redes sociais.

Uso (o scraper precisa estar de pé: docker compose -f leads/docker-compose.yml up -d):

  python3 leads/scrape.py "clínicas de fisioterapia em Fortaleza CE" --cidade "Fortaleza, CE" --profundidade 5 --redes
  python3 leads/scrape.py --arquivo leads/exemplos/termos.txt --cidade "Recife, PE"
  python3 leads/scrape.py "dentistas em Sobral CE" --cidade "Sobral, CE" --campanha ~/prospeccao/dentistas
      → também grava {campanha}/raw/<termo>.json no formato que a skill prospeccao-com-agentes (mestre) lê

Sem Docker de pé mas com Docker instalado: --motor docker roda o scraper uma vez e sai (não precisa do compose).

Saída: leads/dados/<termo>-<data>.csv (planilha), .json (formato Apify) e .md (resumo). Só biblioteca padrão.
Códigos de saída: 0 ok · 1 erro · 2 nenhum resultado (termo errado ou IP limitado) · 3 fichas vieram vazias (consentimento/bloqueio/idioma).
Reprocessar um CSV bruto já baixado, sem nova busca: python3 leads/scrape.py --de-csv leads/dados/x-bruto.csv --redes
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from normalizar import (COLUNAS, deduplicar, escrever_csv, escrever_json_apify, ler_csv,  # noqa: E402
                        normalizar, resumo, slug)

AQUI = os.path.dirname(os.path.abspath(__file__))
UA = "leads-cerebro/1.0 (https://github.com/robertorofilho-stack/robertorofilho-stack.github.io)"
IMAGEM = "gosom/google-maps-scraper:v1.18.1"

# Centros das capitais e cidades grandes: evita rede para o caso comum. Raio padrão 10 km em volta.
# Cidade grande (SP, Rio, BH) tem mais negócios do que cabe num raio: busque por zona/bairro no termo.
CIDADES = {
    "fortaleza": (-3.7319, -38.5267), "sao paulo": (-23.5505, -46.6333), "rio de janeiro": (-22.9068, -43.1729),
    "belo horizonte": (-19.9167, -43.9345), "brasilia": (-15.7939, -47.8828), "salvador": (-12.9777, -38.5016),
    "curitiba": (-25.4284, -49.2733), "recife": (-8.0476, -34.8770), "porto alegre": (-30.0346, -51.2177),
    "manaus": (-3.1190, -60.0217), "belem": (-1.4558, -48.4902), "goiania": (-16.6869, -49.2648),
    "campinas": (-22.9056, -47.0608), "sao luis": (-2.5307, -44.3068), "maceio": (-9.6658, -35.7353),
    "natal": (-5.7945, -35.2110), "teresina": (-5.0892, -42.8019), "joao pessoa": (-7.1195, -34.8450),
    "aracaju": (-10.9472, -37.0731), "cuiaba": (-15.6014, -56.0979), "campo grande": (-20.4697, -54.6201),
    "florianopolis": (-27.5954, -48.5480), "vitoria": (-20.3155, -40.3128), "palmas": (-10.2491, -48.3243),
    "macapa": (0.0349, -51.0694), "boa vista": (2.8235, -60.6758), "porto velho": (-8.7612, -63.9004),
    "rio branco": (-9.9754, -67.8249), "uberlandia": (-18.9186, -48.2772), "sorocaba": (-23.5015, -47.4526),
    "ribeirao preto": (-21.1775, -47.8103), "juiz de fora": (-21.7642, -43.3503), "londrina": (-23.3045, -51.1696),
    "joinville": (-26.3045, -48.8487), "caxias do sul": (-29.1678, -51.1794), "feira de santana": (-12.2664, -38.9663),
    "santos": (-23.9608, -46.3336), "niteroi": (-22.8833, -43.1036), "sobral": (-3.6880, -40.3497),
    "caucaia": (-3.7361, -38.6531), "juazeiro do norte": (-7.2130, -39.3150), "maracanau": (-3.8767, -38.6256),
}


def log(msg):
    print(msg, file=sys.stderr, flush=True)


def carregar_env():
    """Lê leads/.env (o mesmo arquivo que o docker compose lê) sem sobrescrever o ambiente."""
    try:
        with open(os.path.join(AQUI, ".env"), encoding="utf-8") as f:
            for linha in f:
                k, sep, v = linha.strip().partition("=")
                if sep and k.startswith("SCRAPER_") or k == "PROXIES":
                    os.environ.setdefault(k, v.strip().strip("\"'"))
    except OSError:
        pass


# ── Geocodificação ────────────────────────────────────────────────────────────
def geocodificar(cidade, usar_rede=True):
    chave = slug(cidade.split(",")[0]).replace("-", " ")
    if chave in CIDADES:
        return CIDADES[chave]
    if not usar_rede:
        return None
    q = urllib.parse.urlencode({"format": "json", "limit": 1, "countrycodes": "br", "q": cidade})
    req = urllib.request.Request(f"https://nominatim.openstreetmap.org/search?{q}", headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            hits = json.loads(r.read())
        time.sleep(1)                                   # política do Nominatim: ~1 pedido/s
        if hits:
            return float(hits[0]["lat"]), float(hits[0]["lon"])
    except Exception as e:  # noqa: BLE001
        log(f"  geocodificação falhou: {e}")
    return None


# ── Cliente da API do scraper ─────────────────────────────────────────────────
class Scraper:
    def __init__(self, base, chave=""):
        self.base, self.chave = base.rstrip("/"), chave

    def _req(self, metodo, caminho, corpo=None, timeout=60):
        cab = {"Content-Type": "application/json", "User-Agent": UA}
        if self.chave:
            cab["X-API-Key"] = self.chave
        dados = json.dumps(corpo).encode() if corpo is not None else None
        req = urllib.request.Request(self.base + caminho, data=dados, headers=cab, method=metodo)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()

    def de_pe(self):
        try:
            self._req("GET", "/api/v1/jobs", timeout=10)
            return True
        except Exception:  # noqa: BLE001
            return False

    def criar(self, termos, lat, lon, profundidade, email, max_tempo, idioma, zoom, raio, proxies, nome, rapido=False):
        corpo = {"name": nome, "keywords": termos, "lang": idioma, "zoom": zoom, "lat": str(lat), "lon": str(lon),
                 "fast_mode": bool(rapido), "radius": raio, "depth": profundidade,
                 "email": bool(email) and not rapido, "max_time": max_tempo}
        if proxies:
            corpo["proxies"] = proxies
        _, bruto = self._req("POST", "/api/v1/jobs", corpo)
        ident = json.loads(bruto).get("id")
        if not ident:
            raise RuntimeError(f"API não devolveu id: {bruto[:200]!r}")
        return ident

    def status(self, ident):
        _, bruto = self._req("GET", f"/api/v1/jobs/{ident}")
        return json.loads(bruto).get("Status") or json.loads(bruto).get("status")

    def esperar(self, ident, max_tempo, intervalo=8):
        limite = time.time() + max_tempo + 120
        while time.time() < limite:
            s = self.status(ident)
            log(f"  status: {s}")
            if s in ("ok", "failed"):
                return s
            time.sleep(intervalo)
        return "timeout"

    def baixar(self, ident):
        _, bruto = self._req("GET", f"/api/v1/jobs/{ident}/download", timeout=300)
        return bruto.decode("utf-8", "replace")


def rodar_docker(termos, lat, lon, profundidade, email, idioma, zoom, raio, proxies, max_tempo, imagem=IMAGEM, rapido=False):
    """Modo sem servidor: `docker run --rm` uma vez, lê o CSV e sai."""
    pasta = tempfile.mkdtemp(prefix="leads-")
    with open(os.path.join(pasta, "termos.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(termos) + "\n")
    cmd = ["docker", "run", "--rm", "-v", f"{pasta}:/dados"]
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    if proxy:                                           # nuvem do Claude Code: mesma receita do leads/nuvem.sh
        ca = os.environ.get("SSL_CERT_FILE", "")
        cmd += ["--network", "host"]
        for k in ("HTTPS_PROXY", "https_proxy", "HTTP_PROXY", "http_proxy"):
            cmd += ["-e", f"{k}={proxy}"]
        cmd += ["-e", f"NO_PROXY={os.environ.get('NO_PROXY', 'localhost,127.0.0.1')}"]
        if ca and os.path.isfile(ca):
            cmd += ["-e", f"SSL_CERT_FILE={ca}", "-v", f"{ca}:{ca}:ro"]
        if os.path.isdir("/root/.pki"):
            cmd += ["-v", "/root/.pki:/root/.pki:ro"]
    cmd += [imagem, "-input", "/dados/termos.txt",
           "-results", "/dados/resultado.csv", "-depth", str(profundidade), "-lang", idioma,
           "-geo", f"{lat},{lon}", "-zoom", str(zoom), "-radius", str(raio), "-exit-on-inactivity", "3m"]
    if email and not rapido:
        cmd.append("-email")
    if rapido:
        cmd.append("-fast-mode")
    if proxies:
        cmd += ["-proxies", ",".join(proxies)]
    log("  " + " ".join(cmd))
    subprocess.run(cmd, check=True, timeout=max_tempo + 300)
    with open(os.path.join(pasta, "resultado.csv"), encoding="utf-8", errors="replace") as f:
        return f.read()


# ── Fluxo ─────────────────────────────────────────────────────────────────────
def expandir_bairros(termos, bairros, cidade):
    """'clínicas de fisioterapia em Fortaleza CE' × ['Aldeota', 'Meireles'] → um termo por bairro.
    A cidade sai do termo e volta no fim, para o Google não confundir bairro com outra cidade."""
    nome_cidade = (cidade or "").split(",")[0].strip()
    out = []
    for t in termos:
        base = t
        for sep in (" em ", " na ", " no "):
            if nome_cidade and sep + nome_cidade in t:
                base = t.split(sep + nome_cidade)[0]
                break
        for b in bairros:
            out.append(f"{base} no bairro {b}, {nome_cidade}" if nome_cidade else f"{base} no bairro {b}")
    return out


def coletar_termos(a):
    termos = []
    if a.termo:
        termos.append(a.termo)
    termos += a.mais or []
    if a.arquivo:
        with open(a.arquivo, encoding="utf-8-sig") as f:
            termos += [l.strip() for l in f if l.strip() and not l.startswith("#")]
    bairros = getattr(a, "por_bairros", None)
    if bairros and termos:
        if os.path.isfile(bairros):
            with open(bairros, encoding="utf-8-sig") as f:
                lista = [l.strip() for l in f if l.strip() and not l.startswith("#")]
        else:
            lista = [b.strip() for b in bairros.split(",") if b.strip()]
        termos = expandir_bairros(termos, lista, a.cidade)
    vistos, out = set(), []
    for t in termos:
        if t not in vistos:
            vistos.add(t); out.append(t)
    return out


def montar_parser():
    p = argparse.ArgumentParser(description="Leads do Google Maps, limpos para o Brasil.")
    p.add_argument("termo", nargs="?", help='ex.: "clínicas de fisioterapia em Fortaleza CE" (cidade no termo ajuda)')
    p.add_argument("--termo", dest="mais", action="append", help="termo extra (repetível) — vão todos num job só")
    p.add_argument("--arquivo", help="arquivo com um termo por linha")
    p.add_argument("--cidade", help='centro da busca, ex.: "Fortaleza, CE" (capitais não precisam de rede)')
    p.add_argument("--lat", type=float); p.add_argument("--lon", type=float)
    p.add_argument("--profundidade", type=int, default=5, help="rolagem nos resultados; 5 ≈ 40–60 por termo (padrão 5)")
    p.add_argument("--raio", type=int, default=10000, help="metros em volta do centro (padrão 10000)")
    p.add_argument("--zoom", type=int, default=15)
    p.add_argument("--idioma", default="pt", help="código de 2 letras exigido pela API (pt, en, es)")
    p.add_argument("--rapido", action="store_true", help="fast_mode do scraper: ~20 por termo em segundos, sem horário/avaliações detalhadas; "
                   "é o modo que funciona de IP de datacenter (nuvem). E-mail só via --redes")
    p.add_argument("--sem-email", action="store_true", help="modo completo sem o scraper visitar sites atrás de e-mail")
    p.add_argument("--sem-fallback", action="store_true", help="não cair para --rapido quando o modo completo devolver fichas vazias")
    p.add_argument("--por-bairros", help="lista de bairros (vírgula) ou arquivo com um por linha: gera um termo por bairro, no mesmo job")
    p.add_argument("--redes", action="store_true", help="visitar o site de cada negócio: Instagram/Facebook/LinkedIn, e-mail e WhatsApp do site")
    p.add_argument("--max-tempo", type=int, default=600, help="limite do job em segundos (padrão 600)")
    p.add_argument("--intervalo", type=float, default=8, help="segundos entre consultas de status")
    p.add_argument("--proxies", help="lista separada por vírgula (http://, socks5://); também lê PROXIES do .env")
    p.add_argument("--motor", choices=["api", "docker"], default="api", help="api = scraper de pé (compose); docker = docker run avulso")
    p.add_argument("--base-url", default=None, help="padrão http://localhost:8080 ou SCRAPER_BASE_URL/SCRAPER_PORT do .env")
    p.add_argument("--saida", default=os.path.join(AQUI, "dados"), help="pasta de saída (padrão leads/dados)")
    p.add_argument("--nome", default=None, help="nome base dos arquivos (padrão: termo + data)")
    p.add_argument("--campanha", help="pasta de campanha da skill prospeccao-com-agentes: grava raw/<nome>.json lá")
    p.add_argument("--bruto", action="store_true", help="também salvar o CSV bruto do scraper (34 colunas)")
    p.add_argument("--sem-rede-geo", action="store_true", help="não consultar o Nominatim (só tabela interna)")
    p.add_argument("--de-csv", help="não busca nada: reprocessa um CSV bruto do scraper (34+ colunas) já baixado")
    return p


def executar(a):
    carregar_env()
    if a.de_csv:
        return processar(a, open(a.de_csv, encoding="utf-8-sig", errors="replace").read(),
                         coletar_termos(a) or [os.path.splitext(os.path.basename(a.de_csv))[0]])
    termos = coletar_termos(a)
    if not termos:
        log("✗ Nenhum termo. Passe um termo, --termo ou --arquivo."); return 1

    if a.lat is not None and a.lon is not None:
        lat, lon = a.lat, a.lon
    else:
        lugar = a.cidade or termos[0]
        coords = geocodificar(lugar, usar_rede=not a.sem_rede_geo)
        if not coords:
            log(f"✗ Não achei coordenadas para \"{lugar}\". Passe --lat/--lon ou --cidade mais clara."); return 1
        lat, lon = coords
    modo = "rápido (fast_mode)" if a.rapido else ("completo, sem e-mail" if a.sem_email else "completo + e-mail")
    log(f"▶ Centro: {lat}, {lon} · {len(termos)} termo(s) · profundidade {a.profundidade} · modo {modo}")
    for t in termos:
        log(f"    • {t}")
    if a.profundidade >= 15 or len(termos) >= 10:
        log("⚠ Job grande. Sem proxy, o Google pode limitar seu IP por algumas horas. Uma busca por vez.")

    proxies = [p.strip() for p in (a.proxies or os.environ.get("PROXIES") or "").split(",") if p.strip()]
    nome = slug(a.nome, 80) if a.nome else f"{slug(termos[0])}-{dt.date.today().isoformat()}"   # sem ../ nem barra
    os.makedirs(a.saida, exist_ok=True)

    def buscar(rapido):
        if a.motor == "docker":
            return rodar_docker(termos, lat, lon, a.profundidade, not a.sem_email, a.idioma, a.zoom, a.raio, proxies,
                                a.max_tempo, rapido=rapido)
        base = a.base_url or os.environ.get("SCRAPER_BASE_URL") or f"http://localhost:{os.environ.get('SCRAPER_PORT') or '8080'}"
        s = Scraper(base, os.environ.get("SCRAPER_API_KEY", ""))
        if not s.de_pe():
            raise RuntimeError(f"Scraper não responde em {base}. Suba com: docker compose -f leads/docker-compose.yml up -d")
        try:
            ident = s.criar(termos, lat, lon, a.profundidade, not a.sem_email, a.max_tempo, a.idioma, a.zoom, a.raio,
                            proxies, nome, rapido=rapido)
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"Criação falhou: HTTP {e.code} — {e.read().decode()[:200]}")
        log(f"  job {ident}")
        fim = s.esperar(ident, a.max_tempo, a.intervalo)
        if fim != "ok":
            raise RuntimeError(f"Job terminou em '{fim}'. Repetindo muito? Provável limite de IP: espere 1–2 h, baixe a profundidade ou use --proxies.")
        return s.baixar(ident)

    try:
        texto = buscar(a.rapido)
        if not a.rapido and not a.sem_fallback and fichas_vazias(texto):
            log("⚠ O modo completo devolveu as fichas SEM dados (o Google serve a página vazia para este IP — comum em nuvem/datacenter).")
            log("▶ Refazendo em modo rápido (fast_mode): ~20 por termo, com nome, telefone, site, nota e endereço…")
            texto = buscar(True)
            a.rapido = True
    except (RuntimeError, subprocess.SubprocessError, FileNotFoundError) as e:
        log(f"✗ {e}"); return 1

    if a.bruto:
        with open(os.path.join(a.saida, f"{nome}-bruto.csv"), "w", encoding="utf-8") as f:
            f.write(texto)
    return processar(a, texto, termos, nome)


def fichas_vazias(texto, limiar=0.8):
    """True quando ≥ 80% das linhas vieram sem título: o scraper 'deu certo', mas o Google não entregou os dados."""
    linhas = ler_csv(texto.lstrip("\ufeff"))
    if not linhas:
        return False
    return sum(1 for l in linhas if not (l.get("title") or "").strip()) / len(linhas) >= limiar


def processar(a, texto, termos, nome=None):
    """Do CSV bruto do scraper até os arquivos finais. Separado para rodar também com --de-csv."""
    nome = nome or (slug(a.nome, 80) if a.nome else f"{slug(termos[0])}-{dt.date.today().isoformat()}")
    os.makedirs(a.saida, exist_ok=True)
    linhas = ler_csv(texto.lstrip("\ufeff"))
    vazias = [l for l in linhas if not (l.get("title") or "").strip()]
    cheias = [l for l in linhas if (l.get("title") or "").strip()]
    leads = deduplicar([normalizar(l, termos[0] if len(termos) == 1 else "") for l in cheias])
    log(f"✓ {len(linhas)} linhas do scraper → {len(cheias)} com dados → {len(leads)} negócios únicos")
    if vazias:
        log(f"⚠ {len(vazias)} ficha(s) vieram SEM dados (só o link): o Google serviu a página sem conteúdo — "
            "tela de consentimento/bloqueio para o seu IP, ou idioma que o extrator não leu. Não é falta de negócio.")
    if not leads:
        if vazias:
            log("✗ Nenhuma ficha com dados. Tente --idioma en, espere 1–2 h, ou rode de um IP residencial (seu Mac).")
            return 3
        log("⚠ 0 resultados: termo sem negócios OU Google limitou o IP (passa sozinho em 1–2 h). Tente outro termo, profundidade menor ou --proxies.")
        return 2

    estat = None
    if a.redes:
        from enriquecer import enriquecer
        log("▶ Visitando os sites (redes, e-mail, WhatsApp do site)…")
        estat = enriquecer(leads)
        log(f"  {estat['sites']} sites · redes em {estat['redes']} · WhatsApp no site: {estat['whatsapp_site']} · com e-mail: {estat['emails']}")

    csv_path = os.path.join(a.saida, f"{nome}.csv")
    escrever_csv(leads, csv_path)
    escrever_json_apify(leads, os.path.join(a.saida, f"{nome}.json"))
    with open(os.path.join(a.saida, f"{nome}.md"), "w", encoding="utf-8") as f:
        f.write(resumo(leads, f"Leads: {', '.join(termos)}", enriquecido=bool(a.redes)))
    if a.rapido:
        log("  modo rápido: ~20 por termo. Para mais, use --por-bairros (um termo por bairro, no mesmo job).")
    if a.campanha:
        raw = os.path.join(os.path.expanduser(a.campanha), "raw")
        os.makedirs(raw, exist_ok=True)
        escrever_json_apify(leads, os.path.join(raw, f"{nome}.json"))
        log(f"  campanha: {raw}/{nome}.json (rode ranquear.py da skill prospeccao-com-agentes)")
    log(f"  salvo → {csv_path} (+ .json, .md)")
    for l in leads[:5]:
        log(f"  • {l['nome']} | {l['telefone']} | {l['site'] or '—'} | {l['emails'] or '—'}")
    return 0


def main(argv=None):
    return executar(montar_parser().parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
