#!/usr/bin/env python3
"""Funções puras para limpar a saída do scraper do Google Maps (gosom/google-maps-scraper, CSV de 36 colunas)
e deixá-la pronta para prospecção no Brasil.

Sem rede, sem dependência fora da biblioteca padrão. Tudo aqui tem teste em testes/testar_leads.py.
"""
from __future__ import annotations

import csv
import io
import json
import math
import re
import unicodedata
import urllib.parse

# Colunas do CSV final, na ordem. Só o que serve para contatar e qualificar um lead.
COLUNAS = [
    "nome", "categoria", "telefone", "telefone_e164", "tipo_telefone", "whatsapp", "emails", "site",
    "instagram", "facebook", "linkedin", "whatsapp_site", "nota", "avaliacoes", "endereco", "bairro",
    "cidade", "uf", "maps", "sem_site", "sem_redes", "place_id", "data_id", "termo",
]

# DDDs em uso no Brasil (Anatel). Fora disto não é número brasileiro.
DDDS_VALIDOS = {11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 24, 27, 28, 31, 32, 33, 34, 35, 37, 38,
                41, 42, 43, 44, 45, 46, 47, 48, 49, 51, 53, 54, 55, 61, 62, 63, 64, 65, 66, 67, 68, 69,
                71, 73, 74, 75, 77, 79, 81, 82, 83, 84, 85, 86, 87, 88, 89, 91, 92, 93, 94, 95, 96, 97, 98, 99}
_PREFIXOS_SEM_LINHA = ("0800", "0300", "0500", "0900")      # não geográficos: não recebem WhatsApp nem ligação de volta
_RE_RAMAL = re.compile(r"\b(?:ramal|extens[aã]o|ext\.?|r\.)\s*:?\s*\d+.*$", re.I)

UF_POR_ESTADO = {
    "acre": "AC", "alagoas": "AL", "amapa": "AP", "amazonas": "AM", "bahia": "BA", "ceara": "CE",
    "distrito federal": "DF", "espirito santo": "ES", "goias": "GO", "maranhao": "MA", "mato grosso": "MT",
    "mato grosso do sul": "MS", "minas gerais": "MG", "para": "PA", "paraiba": "PB", "parana": "PR",
    "pernambuco": "PE", "piaui": "PI", "rio de janeiro": "RJ", "rio grande do norte": "RN",
    "rio grande do sul": "RS", "rondonia": "RO", "roraima": "RR", "santa catarina": "SC", "sao paulo": "SP",
    "sergipe": "SE", "tocantins": "TO",
}

EMAIL_RE = re.compile(r"[a-z0-9._%+\-]+@[a-z0-9\-]+(?:\.[a-z0-9\-]+)*\.[a-z]{2,10}")
# Busca dentro de texto/HTML: o TLD é todo minúsculo (ou todo maiúsculo) e não pode ser seguido de letra nem de
# ".letra" — é o que separa "contato@x.com.br" de "contato@x.com.brTelefone" e de "a@b.com.brasil".
EMAIL_BUSCA_RE = re.compile(
    r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)*\.(?:[a-z]{2,10}|[A-Z]{2,10})(?![A-Za-z]|\.[A-Za-z])")
_EMAIL_LIXO = ("example.", "exemplo.", "sentry", "wixpress", "wix.com", "noreply", "no-reply", "nao-responda",
               "naoresponda", "seuemail", "seu-email", "email.com", "domain.com", "dominio.com", "@2x", "@3x",
               "jquery", "bootstrap", "cloudfront", "googleusercontent", "schema.org", "w3.org", "gravatar",
               "@vue", "@angular", "webpack", "@babel")
_DOMINIO_LIXO = (".local", ".invalid", ".test", ".example", ".localhost", ".png", ".jpg", ".jpeg", ".gif", ".svg",
                 ".webp", ".css", ".js", ".woff", ".ico")


def _float(v):
    try:
        x = float(str(v).replace(",", ".")) if v not in (None, "") else 0.0
    except (ValueError, OverflowError):
        return 0.0
    return x if math.isfinite(x) else 0.0


def _int(v):
    try:
        x = float(str(v).replace(",", ".")) if v not in (None, "") else 0.0
    except (ValueError, OverflowError):
        return 0
    return int(x) if math.isfinite(x) and abs(x) < 1e12 else 0


def slug(texto, maximo=60):
    t = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode().lower()
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return t[:maximo] or "busca"


# ── Telefone ──────────────────────────────────────────────────────────────────
def telefone_br(bruto, ddi="55"):
    """Normaliza para E.164 sem '+': '(85) 99762-4221' → '5585997624221'.
    Devolve '' quando não parece número brasileiro: internacional, DDD inexistente, 0800/0300, ramal grudado,
    dois números no mesmo campo, 11 dígitos sem o 9 do celular, curto demais, lixo."""
    texto = _RE_RAMAL.sub("", (bruto or "").strip())
    d = re.sub(r"[^0-9]", "", texto)                     # só dígitos ASCII (dígitos de outros alfabetos caem fora)
    internacional = texto.startswith("+") or d.startswith("00")
    if d.startswith("00"):
        d = d[2:]
    if d.startswith(ddi) and len(d) - len(ddi) in (10, 11):
        local = d[len(ddi):]
    elif internacional:                                   # '+1 305…' ou '0044…': o prefixo diz o país, e não é o Brasil
        return ""
    else:
        if d.startswith(_PREFIXOS_SEM_LINHA):
            return ""
        if len(d) in (11, 12) and d[0] == "0":            # com zero de operadora: 085 9xxxx-xxxx
            d = d[1:]
        if len(d) in (10, 11) and d[0] != "0":
            local = d
        else:
            return ""
    if int(local[:2]) not in DDDS_VALIDOS:
        return ""
    if len(local) == 11 and local[2] != "9":              # 11 dígitos só existe para celular (9 na frente)
        return ""
    return ddi + local


def tipo_telefone(e164):
    if not e164:
        return ""
    local = e164[2:]
    return "celular" if len(local) == 11 and local[2] == "9" else "fixo"


def link_whatsapp(e164):
    """Link direto só para celular. Fixo pode até ter WhatsApp Business, mas não dá para saber daqui."""
    return f"https://wa.me/{e164}" if e164 and tipo_telefone(e164) == "celular" else ""


def formatar_telefone(e164):
    """'5585997624221' → '(85) 99762-4221'. Sem '+' na frente: planilha não confunde com fórmula."""
    if not e164:
        return ""
    local = e164[2:]
    ddd, num = local[:2], local[2:]
    if len(num) == 9:
        return f"({ddd}) {num[:5]}-{num[5:]}"
    if len(num) == 8:
        return f"({ddd}) {num[:4]}-{num[4:]}"
    return local


# ── Endereço ──────────────────────────────────────────────────────────────────
def partes_endereco(endereco):
    """'R. Dr. José Lourenço, 2000 - Aldeota, Fortaleza - CE, 60115-282, Brazil' → ('Aldeota', 'Fortaleza', 'CE').
    Aceita travessão/meia-risca no lugar do hífen e o formato em inglês 'Fortaleza, State of Ceará, Brazil'."""
    e = (endereco or "").replace("–", "-").replace("—", "-")
    partes = [p.strip() for p in e.split(",")]
    for i, p in enumerate(partes):
        m = re.match(r"^(.+?)\s*-\s*([A-Z]{2})$", p)
        if not m:
            continue
        cidade, uf = m.group(1).strip(), m.group(2)
        bairro = ""
        if " - " in cidade:                            # 'Centro - Fortaleza - CE'
            bairro, cidade = [x.strip() for x in cidade.rsplit(" - ", 1)]
        if i > 0 and " - " in partes[i - 1]:           # '2000 - Aldeota' ou '1500 - Loja 3 - Aldeota'
            bairro = partes[i - 1].rsplit(" - ", 1)[1].strip()
        return bairro, cidade, uf
    m = re.search(r"^(.*?),\s*State of ([^,]+)", e)
    if m:
        antes = [p.strip() for p in m.group(1).split(",")]
        cidade = antes[-1] if antes else ""
        bairro = antes[-2].rsplit(" - ", 1)[1].strip() if len(antes) > 1 and " - " in antes[-2] else ""
        return bairro, cidade, UF_POR_ESTADO.get(slug(m.group(2)).replace("-", " "), "")
    return "", "", ""


# ── E-mail ────────────────────────────────────────────────────────────────────
def email_valido(e):
    original = (e or "").strip().strip("\"'<>().,;:")
    ultimo = original.rsplit(".", 1)[-1]
    if ultimo and not (ultimo.islower() or ultimo.isupper()):      # 'com.brTelefone': TLD colado em texto
        return ""
    e = original.lower()
    if not EMAIL_RE.fullmatch(e):
        return ""
    if e.endswith(_DOMINIO_LIXO) or any(l in e for l in _EMAIL_LIXO):
        return ""
    return e


def lista_emails(campo):
    """Aceita o campo 'emails' do scraper (JSON ou separado por vírgula/;/espaço) e devolve lista limpa, sem repetição."""
    if not campo:
        return []
    campo = str(campo).strip()
    itens = []
    if campo.startswith("["):
        try:
            itens = json.loads(campo)
        except ValueError:
            itens = []
        if not isinstance(itens, list):
            itens = []
    if not itens:
        itens = re.split(r"[,;\s]+", campo)
    out = []
    for e in itens:
        v = email_valido(str(e))
        if v and v not in out:
            out.append(v)
    return out


# ── Linha do scraper → lead ───────────────────────────────────────────────────
def normalizar(linha, termo=""):
    """Converte uma linha do CSV do gosom (36 colunas) num lead com as COLUNAS acima."""
    e164 = telefone_br(linha.get("phone"))
    endereco = (linha.get("address") or "").strip()
    if not endereco:
        completo = (linha.get("complete_address") or "").strip()
        endereco = completo if completo and not completo.startswith("{") else ""
    bairro, cidade, uf = partes_endereco(endereco)
    site = (linha.get("website") or "").strip()
    emails = lista_emails(linha.get("emails"))
    nome = (linha.get("title") or "").strip()
    maps = (linha.get("link") or "").strip()
    if not maps and nome:                                 # fast_mode não traz o link: busca pelo nome + endereço
        maps = "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote_plus(f"{nome} {endereco}".strip())
    return {
        "nome": nome,
        "categoria": (linha.get("category") or "").strip(),
        "telefone": formatar_telefone(e164),
        "telefone_e164": e164,
        "tipo_telefone": tipo_telefone(e164),
        "whatsapp": link_whatsapp(e164),
        "emails": "; ".join(emails),
        "site": site,
        "instagram": "", "facebook": "", "linkedin": "", "whatsapp_site": "",
        "nota": _float(linha.get("review_rating")),
        "avaliacoes": _int(linha.get("review_count")),
        "endereco": endereco, "bairro": bairro, "cidade": cidade, "uf": uf,
        "maps": maps,
        "sem_site": "nao" if site else "sim",
        "sem_redes": "",                                  # preenchido por enriquecer.py
        "place_id": (linha.get("place_id") or "").strip(),
        "cid": (linha.get("cid") or "").strip(),
        "data_id": (linha.get("data_id") or "").strip(),
        "latitude": linha.get("latitude") or "", "longitude": linha.get("longitude") or "",
        "termo": termo,
    }


def _coord(v):
    x = _float(v)
    return round(x, 4) if x else ""


def chave_dedupe(l):
    """place_id → cid → data_id (único mesmo no fast_mode) → nome + telefone + coordenada + endereço."""
    return (l.get("place_id") or l.get("cid") or l.get("data_id")
            or (slug(l.get("nome"), 200), l.get("telefone_e164", ""), _coord(l.get("latitude")),
                _coord(l.get("longitude")), slug(l.get("endereco"), 80)))


def deduplicar(leads):
    """Mesmo negócio vindo de dois termos de busca conta uma vez."""
    vistos, out = set(), []
    for l in leads:
        chave = chave_dedupe(l)
        if chave in vistos:
            continue
        vistos.add(chave)
        out.append(l)
    return out


def ler_csv(texto):
    """Lê o CSV do scraper. `newline=""` é o que o módulo csv pede; quebra de linha crua dentro de campo
    (CSV malformado) é normalizada em vez de derrubar a leitura."""
    texto = (texto or "").lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "")   # o scraper só escreve \n
    try:
        return list(csv.DictReader(io.StringIO(texto, newline="")))
    except csv.Error:
        return []


def celula_segura(v):
    """Excel e Google Sheets executam células que começam com = + - @ (injeção de fórmula CSV).
    Um nome de negócio malicioso no Maps não pode virar comando na sua planilha."""
    if isinstance(v, str) and v[:1] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + v
    return v


def escrever_csv(leads, caminho):
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUNAS, extrasaction="ignore")
        w.writeheader()
        for l in leads:
            w.writerow({k: celula_segura(l.get(k, "")) for k in COLUNAS})


# ── Ponte para a skill prospeccao-com-agentes (formato do ator da Apify) ──────
def para_apify(l):
    """Mesmos campos que ranquear.py lê: title, phone, phoneUnformatted, website, totalScore,
    reviewsCount, categoryName, address, neighborhood, url. O resto é bônus."""
    return {
        "title": l["nome"], "categoryName": l["categoria"],
        "phone": l["telefone"],
        "phoneUnformatted": ("+" + l["telefone_e164"]) if l["telefone_e164"] else "",
        "website": l["site"], "totalScore": l["nota"], "reviewsCount": l["avaliacoes"],
        "address": l["endereco"], "neighborhood": l["bairro"], "city": l["cidade"], "state": l["uf"],
        "url": l["maps"], "placeId": l["place_id"], "cid": l.get("cid", ""), "dataId": l.get("data_id", ""),
        "location": {"lat": _float(l.get("latitude")), "lng": _float(l.get("longitude"))},
        "emails": [e for e in l["emails"].split("; ") if e],
        "instagram": l["instagram"], "facebook": l["facebook"], "linkedin": l["linkedin"],
        "whatsappSite": l["whatsapp_site"], "searchString": l["termo"],
        "origem": "gosom/google-maps-scraper",
    }


def escrever_json_apify(leads, caminho):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump([para_apify(l) for l in leads], f, ensure_ascii=False, indent=2)


# ── Resumo em Markdown ────────────────────────────────────────────────────────
def _md(texto):
    return str(texto).replace("|", "\\|").replace("\n", " ")


def resumo(leads, titulo, enriquecido=False, notas=None):
    n = len(leads)

    def conta(cond):
        return sum(1 for l in leads if cond(l))

    linhas = [f"# {_md(titulo)}", "",
              f"- Negócios únicos: **{n}**",
              f"- Com telefone: {conta(lambda l: l['telefone_e164'])} · celular (WhatsApp provável): {conta(lambda l: l['tipo_telefone'] == 'celular')}",
              f"- Com site: {conta(lambda l: l['site'])} · **sem site: {conta(lambda l: not l['site'])}** (candidato a oferta de site)",
              f"- Com e-mail: {conta(lambda l: l['emails'])}"]
    if enriquecido:
        linhas.append(f"- Com Instagram: {conta(lambda l: l['instagram'])} · Facebook: {conta(lambda l: l['facebook'])} · "
                      f"LinkedIn: {conta(lambda l: l['linkedin'])} · WhatsApp no site: {conta(lambda l: l['whatsapp_site'])}")
    for nota in notas or []:
        linhas.append(f"- {_md(nota)}")
    linhas += ["", "| # | Nome | Telefone | Nota | Aval. | Site | Bairro |", "|---|---|---|---|---|---|---|"]
    for i, l in enumerate(sorted(leads, key=lambda x: (x["avaliacoes"], x["nota"]), reverse=True)[:15], 1):
        linhas.append(f"| {i} | {_md(l['nome'])} | {l['telefone']} | {l['nota']:.1f} | {l['avaliacoes']} | "
                      f"{'sim' if l['site'] else '—'} | {_md(l['bairro'])} |")
    linhas += ["", "_Dado público de empresa, para contato comercial. LGPD: base legal é legítimo interesse (art. 7, IX); "
               "quem pedir descadastro sai da lista. Nunca revender a lista. Nunca disparo frio por WhatsApp comum._"]
    return "\n".join(linhas) + "\n"
