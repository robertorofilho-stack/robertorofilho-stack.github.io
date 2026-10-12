#!/usr/bin/env python3
"""Funções puras para limpar a saída do scraper do Google Maps (gosom/google-maps-scraper)
e deixá-la pronta para prospecção no Brasil.

Sem rede, sem dependência fora da biblioteca padrão. Tudo aqui tem teste em testes/testar_leads.py.
"""
from __future__ import annotations

import csv
import io
import json
import re
import unicodedata

# Colunas do CSV final, na ordem. Só o que serve para contatar e qualificar um lead.
COLUNAS = [
    "nome", "categoria", "telefone", "telefone_e164", "tipo_telefone", "whatsapp", "emails", "site",
    "instagram", "facebook", "linkedin", "whatsapp_site", "nota", "avaliacoes", "endereco", "bairro",
    "cidade", "uf", "maps", "sem_site", "sem_redes", "place_id", "termo",
]

EMAIL_RE = re.compile(r"[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}")
_EMAIL_LIXO = ("example.", "exemplo.", "sentry", "wixpress", "noreply", "no-reply", "nao-responda",
               "seuemail", "seu-email", "email.com", "domain.com", "dominio.com", "@2x", "jquery")
_EXT_LIXO = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".css", ".js", ".woff", ".ico")


def _so_digitos(texto):
    return re.sub(r"\D", "", texto or "")


def _float(v):
    try:
        return float(str(v).replace(",", ".")) if v not in (None, "") else 0.0
    except ValueError:
        return 0.0


def _int(v):
    try:
        return int(float(str(v).replace(",", "."))) if v not in (None, "") else 0
    except ValueError:
        return 0


def slug(texto, maximo=60):
    t = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode().lower()
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return t[:maximo] or "busca"


# ── Telefone ──────────────────────────────────────────────────────────────────
def telefone_br(bruto, ddi="55"):
    """Normaliza para E.164 sem '+': '(85) 99999-0001' → '5585999990001'.
    Devolve '' quando não parece número brasileiro (internacional, curto demais, lixo)."""
    texto = (bruto or "").strip()
    d = _so_digitos(texto)
    internacional = texto.startswith("+") or d.startswith("00")
    if d.startswith("00"):
        d = d[2:]
    if d.startswith(ddi) and len(d) - len(ddi) in (10, 11):
        return d
    if internacional:                                # '+1 305…' ou '0044…': o prefixo diz o país, e não é o Brasil
        return ""
    if len(d) in (11, 12) and d[0] == "0":          # com zero de operadora: 085 9xxxx-xxxx
        d = d[1:]
    if len(d) in (10, 11) and d[0] != "0":
        return ddi + d
    return ""


def tipo_telefone(e164):
    if not e164:
        return ""
    local = e164[2:]
    return "celular" if len(local) == 11 and local[2] == "9" else "fixo"


def link_whatsapp(e164):
    """Link direto só para celular. Fixo pode até ter WhatsApp Business, mas não dá para saber daqui."""
    return f"https://wa.me/{e164}" if e164 and tipo_telefone(e164) == "celular" else ""


def formatar_telefone(e164):
    """'5585999990001' → '+55 85 99999-0001' (leitura humana)."""
    if not e164:
        return ""
    local = e164[2:]
    ddd, num = local[:2], local[2:]
    if len(num) == 9:
        return f"+55 {ddd} {num[:5]}-{num[5:]}"
    if len(num) == 8:
        return f"+55 {ddd} {num[:4]}-{num[4:]}"
    return "+" + e164


# ── Endereço ──────────────────────────────────────────────────────────────────
def partes_endereco(endereco):
    """'R. Dr. José Lourenço, 2000 - Aldeota, Fortaleza - CE, 60115-282, Brazil' → ('Aldeota', 'Fortaleza', 'CE')."""
    partes = [p.strip() for p in (endereco or "").split(",")]
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
    return "", "", ""


# ── E-mail ────────────────────────────────────────────────────────────────────
def email_valido(e):
    e = (e or "").strip().strip("\"'<>").lower()
    if not EMAIL_RE.fullmatch(e) or e.endswith(_EXT_LIXO):
        return ""
    if any(l in e for l in _EMAIL_LIXO):
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
    """Converte uma linha do CSV do gosom (34 colunas) num lead com as COLUNAS acima."""
    e164 = telefone_br(linha.get("phone"))
    endereco = (linha.get("address") or linha.get("complete_address") or "").strip()
    bairro, cidade, uf = partes_endereco(endereco)
    site = (linha.get("website") or "").strip()
    emails = lista_emails(linha.get("emails"))
    return {
        "nome": (linha.get("title") or "").strip(),
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
        "maps": (linha.get("link") or "").strip(),
        "sem_site": "nao" if site else "sim",
        "sem_redes": "",                                  # preenchido por enriquecer.py
        "place_id": (linha.get("place_id") or "").strip(),
        "cid": (linha.get("cid") or "").strip(),
        "latitude": linha.get("latitude") or "", "longitude": linha.get("longitude") or "",
        "termo": termo,
    }


def deduplicar(leads):
    """Mesmo negócio vindo de dois termos de busca conta uma vez. Chave: place_id → cid → nome+telefone."""
    vistos, out = set(), []
    for l in leads:
        chave = l.get("place_id") or l.get("cid") or (slug(l.get("nome")), l.get("telefone_e164", ""))
        if chave in vistos:
            continue
        vistos.add(chave)
        out.append(l)
    return out


def ler_csv(texto):
    return list(csv.DictReader(io.StringIO(texto)))


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
        "url": l["maps"], "placeId": l["place_id"], "cid": l.get("cid", ""),
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
def resumo(leads, titulo, enriquecido=False):
    n = len(leads)

    def conta(cond):
        return sum(1 for l in leads if cond(l))

    linhas = [f"# {titulo}", "",
              f"- Negócios únicos: **{n}**",
              f"- Com telefone: {conta(lambda l: l['telefone_e164'])} · celular (WhatsApp provável): {conta(lambda l: l['tipo_telefone'] == 'celular')}",
              f"- Com site: {conta(lambda l: l['site'])} · **sem site: {conta(lambda l: not l['site'])}** (candidato a oferta de site)",
              f"- Com e-mail: {conta(lambda l: l['emails'])}"]
    if enriquecido:
        linhas.append(f"- Com Instagram: {conta(lambda l: l['instagram'])} · Facebook: {conta(lambda l: l['facebook'])} · "
                      f"LinkedIn: {conta(lambda l: l['linkedin'])} · WhatsApp no site: {conta(lambda l: l['whatsapp_site'])}")
    linhas += ["", "| # | Nome | Telefone | Nota | Aval. | Site | Bairro |", "|---|---|---|---|---|---|---|"]
    for i, l in enumerate(sorted(leads, key=lambda x: (x["avaliacoes"], x["nota"]), reverse=True)[:15], 1):
        linhas.append(f"| {i} | {l['nome']} | {l['telefone']} | {l['nota']:.1f} | {l['avaliacoes']} | "
                      f"{'sim' if l['site'] else '—'} | {l['bairro']} |")
    linhas += ["", "_Dado público de empresa, para contato comercial. LGPD: base legal é legítimo interesse (art. 7, IX); "
               "quem pedir descadastro sai da lista. Nunca revender a lista. Nunca disparo frio por WhatsApp comum._"]
    return "\n".join(linhas) + "\n"
