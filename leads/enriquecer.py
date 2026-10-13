#!/usr/bin/env python3
"""Enriquecimento sem LLM: visita o site de cada negócio uma vez e extrai Instagram, Facebook, LinkedIn,
e-mails e o número de WhatsApp que o próprio dono colocou no botão do site (o melhor número que existe).

Custo: zero token. Só HTTP + regex, em paralelo. Só biblioteca padrão.
As funções extrair_* são puras e têm teste; só `enriquecer`/`baixar_html` tocam a rede — e tocam com trava:
anti-SSRF (nada de rede privada, loopback, metadados de nuvem, redirecionamento para dentro), robots.txt,
limite de bytes e prazo total por página.
"""
from __future__ import annotations

import html
import ipaddress
import os
import re
import socket
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
import zlib
from concurrent.futures import ThreadPoolExecutor

from normalizar import EMAIL_BUSCA_RE, email_valido, telefone_br

UA = "Mozilla/5.0 (compatible; leads-cerebro/1.0; +https://www.drrobertorodrigues.com)"

REDES_RE = {
    "instagram": re.compile(r"https?://(?:www\.)?instagram\.com/([A-Za-z0-9_.]+)", re.I),
    "facebook": re.compile(r"https?://(?:www\.|m\.|web\.|pt-br\.|business\.)?facebook\.com/([A-Za-z0-9_.\-]+)", re.I),
    "linkedin": re.compile(r"https?://(?:[a-z]{2,3}\.)?linkedin\.com/(?:company|in|school)/([A-Za-z0-9_.\-%]+)", re.I),
}
_HANDLE_LIXO = {"", "home", "pages", "people", "help", "about", "policies", "policy", "legal", "tos", "privacy",
                "settings", "sharer", "tr", "profile.php", "plugins", "dialog", "intent", "login", "share.php",
                "permalink.php", "p", "reel", "reels", "explore", "stories", "tv", "watch", "events", "groups",
                "marketplace", "gaming", "photo", "hashtag", "search", "accounts", "share", "business", "ads",
                "embed.js", "embed", "static", "_u", "web", "oauth", "developer", "developers", "l.php", "widgets",
                "badge", "sharer.php", "v", "api", "graph", "static.xx", "s", "x", "images", "image", "img"}
_HANDLE_LIXO_RE = re.compile(r"^v\d+(?:\.\d+)?$|\.(?:js|php|css|png|jpe?g|svg|gif|json)$", re.I)
WHATSAPP_RE = re.compile(
    r"(?:api\.whatsapp\.com/send/?\?(?:[^\"'\s<>]*&)?phone=|wa\.me/|web\.whatsapp\.com/send/?\?(?:[^\"'\s<>]*&)?phone=|"
    r"whatsapp://send/?\?(?:[^\"'\s<>]*&)?phone=)(?:%2B|\+)?(\d{10,15})", re.I)


def preparar_html(texto):
    """Desfaz entidades (&amp;phone=) e barras escapadas de JSON (https:\\/\\/) antes das regex."""
    return html.unescape(texto or "").replace("\\/", "/")


def rede_da_url(url):
    """'https://www.instagram.com/x' → ('instagram', url). Quando o 'site' do Maps já é a rede social."""
    for rede, rx in REDES_RE.items():
        m = rx.match((url or "").strip())
        if m and not _handle_lixo(m.group(1)):
            return rede, m.group(0).rstrip("\"'/")
    return "", ""


def _handle_lixo(h):
    h = h.lower().rstrip(".")
    return h in _HANDLE_LIXO or bool(_HANDLE_LIXO_RE.search(h))


def extrair_redes(html_texto):
    out = {"instagram": "", "facebook": "", "linkedin": ""}
    for rede, rx in REDES_RE.items():
        for m in rx.finditer(html_texto or ""):
            h = m.group(1).lower().rstrip(".")
            if _handle_lixo(h) or (rede == "facebook" and (h.isdigit() or len(h) < 3)):
                continue
            out[rede] = m.group(0).rstrip("\"'/")
            break
    return out


def extrair_emails(html_texto, maximo=3):
    out = []
    for m in EMAIL_BUSCA_RE.finditer(html_texto or ""):
        v = email_valido(m.group(0))
        if v and v not in out:
            out.append(v)
        if len(out) >= maximo:
            break
    return out


def extrair_whatsapp(html_texto):
    """Número do botão de WhatsApp do site, normalizado (E.164 sem '+'). '' se não houver."""
    for m in WHATSAPP_RE.finditer(html_texto or ""):
        n = telefone_br(m.group(1))
        if n:
            return n
    return ""


# ── Rede segura: o site de um negócio é entrada hostil ────────────────────────
# Lição do mestre (campanha de e-mail 01/10): enriquecedor sem trava de SSRF nem robots.txt não entra em produção.
_NOMES_PROIBIDOS = ("localhost", ".local", ".internal", ".localdomain", ".localhost", "metadata.google",
                    "host.docker.internal", ".nip.io", ".sslip.io", ".localtest.me", ".xip.io", "localtest.me",
                    ".localhost.direct")
_PARECE_IP_NO_NOME = re.compile(r"^\d{1,3}(?:[.\-]\d{1,3}){3}")


def _ip_publico(ip):
    try:
        a = ipaddress.ip_address(ip)
    except ValueError:
        return False
    return a.is_global and not a.is_multicast


def destino_permitido(url):
    """Só http(s), porta web, host público. Recusa loopback, rede privada, link-local (metadados de nuvem), nomes
    internos e domínios-curinga que apontam para qualquer IP. Com proxy de saída e sem DNS local, delega ao proxy."""
    try:
        u = urllib.parse.urlsplit(url)
        porta = u.port
    except ValueError:                                   # 'javascript:alert(1)' e afins
        return False
    host = (u.hostname or "").lower().rstrip(".")
    if u.scheme not in ("http", "https") or not host:
        return False
    if host in _NOMES_PROIBIDOS or any(host.endswith(n) for n in _NOMES_PROIBIDOS if n.startswith(".")):
        return False
    if _PARECE_IP_NO_NOME.match(host) and not host.replace(".", "").isdigit():
        return False                                     # 127-0-0-1.algo / 10.0.0.1.algo: nome que embute IP
    if porta and porta not in (80, 443, 8080, 8443):
        return False
    try:
        ipaddress.ip_address(host)
        return _ip_publico(host)
    except ValueError:
        pass
    try:
        enderecos = {r[4][0] for r in socket.getaddrinfo(host, porta or (443 if u.scheme == "https" else 80))}
    except OSError:
        return bool(os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy"))
    return bool(enderecos) and all(_ip_publico(ip) for ip in enderecos)


class _RedirecionamentoSeguro(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not destino_permitido(newurl):
            raise urllib.error.URLError(f"redirecionamento recusado: {newurl[:80]}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


_abridor = urllib.request.build_opener(_RedirecionamentoSeguro)   # mantém o proxy do ambiente
_robots_cache, _robots_trava = {}, threading.Lock()


def robots_permite(url, timeout=6):
    """Respeita o robots.txt do site (uma leitura por host). Sem robots ou com erro: permite."""
    u = urllib.parse.urlsplit(url)
    raiz = f"{u.scheme}://{u.netloc}"
    with _robots_trava:
        rp = _robots_cache.get(raiz)
    if rp is None:
        rp = urllib.robotparser.RobotFileParser()
        try:
            req = urllib.request.Request(raiz + "/robots.txt", headers={"User-Agent": UA})
            with _abridor.open(req, timeout=timeout) as r:
                rp.parse(r.read(100_000).decode("utf-8", "replace").splitlines())
        except Exception:  # noqa: BLE001 — sem robots legível = sem restrição
            rp = None
        with _robots_trava:
            _robots_cache[raiz] = rp or False
    if not rp:
        return True
    try:
        return rp.can_fetch(UA, url)
    except Exception:  # noqa: BLE001
        return True


def _decodificar(dados, tipo):
    if (dados[:2] == b"\x1f\x8b"):
        try:
            dados = zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(dados)   # tolera gzip truncado
        except zlib.error:
            pass
    m = re.search(r"charset=[\"']?([\w\-]+)", tipo or "", re.I) or re.search(rb"charset=[\"']?([\w\-]+)", dados[:4096], re.I)
    charset = (m.group(1) if isinstance(m.group(1), str) else m.group(1).decode("ascii", "ignore")) if m else "utf-8"
    try:
        return dados.decode(charset, "replace")
    except LookupError:
        return dados.decode("utf-8", "replace")


def baixar_html(url, timeout=10, max_bytes=400_000):
    """Baixa uma página com prazo total (timeout×3), teto de bytes e só tipos de texto. '' em qualquer recusa ou erro."""
    if not url:
        return ""
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    if not destino_permitido(url) or not robots_permite(url):
        return ""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*;q=0.8",
                                               "Accept-Language": "pt-BR,pt;q=0.9"})
    try:
        with _abridor.open(req, timeout=timeout) as r:
            tipo = (r.headers.get("Content-Type") or "").lower()
            if tipo and not any(t in tipo for t in ("html", "text", "xml", "json")):
                return ""                                 # PDF, imagem, zip: não é página
            limite, partes, total = time.monotonic() + timeout * 3, [], 0
            while total < max_bytes and time.monotonic() < limite:
                bloco = r.read1(min(16384, max_bytes - total))
                if not bloco:
                    break
                partes.append(bloco)
                total += len(bloco)
            return _decodificar(b"".join(partes), tipo)
    except Exception:  # noqa: BLE001
        return ""


def enriquecer_um(lead, html_texto):
    """Aplica as extrações a um lead (puro: recebe o HTML já baixado)."""
    texto = preparar_html(html_texto)
    redes = extrair_redes(texto)
    for rede, valor in redes.items():
        if valor and not lead.get(rede):
            lead[rede] = valor
    novos = extrair_emails(texto)
    atuais = [e for e in (lead.get("emails") or "").split("; ") if e]
    lead["emails"] = "; ".join(atuais + [e for e in novos if e not in atuais])
    lead["whatsapp_site"] = extrair_whatsapp(texto)
    if lead["whatsapp_site"] and not lead.get("whatsapp"):
        lead["whatsapp"] = f"https://wa.me/{lead['whatsapp_site']}"
    lead["sem_redes"] = "nao" if (lead.get("instagram") or lead.get("facebook") or lead.get("linkedin")) else "sim"
    return lead


def enriquecer(leads, trabalhadores=8, timeout=10, saida=sys.stderr):
    """Visita cada site uma vez, em paralelo. Site que já é rede social conta como rede, sem visita."""
    for l in leads:
        for k in ("instagram", "facebook", "linkedin", "whatsapp_site"):
            l.setdefault(k, "")
        l["sem_redes"] = "sim"
        rede, url = rede_da_url(l.get("site", ""))
        if rede:
            l[rede] = url
            l["sem_redes"] = "nao"
    visitar = [l for l in leads if l.get("site") and not rede_da_url(l["site"])[0]]
    feitos = 0

    def trabalho(l):
        return enriquecer_um(l, baixar_html(l["site"], timeout=timeout))

    with ThreadPoolExecutor(max_workers=trabalhadores) as ex:
        for _ in ex.map(trabalho, visitar):
            feitos += 1
            print(f"\r  sites visitados: {feitos}/{len(visitar)}", end="", file=saida, flush=True)
    if visitar:
        print(file=saida)
    return {"sites": len(visitar),
            "redes": sum(1 for l in leads if l["sem_redes"] == "nao"),
            "whatsapp_site": sum(1 for l in leads if l["whatsapp_site"]),
            "emails": sum(1 for l in leads if l.get("emails"))}
