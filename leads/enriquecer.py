#!/usr/bin/env python3
"""Enriquecimento sem LLM: visita o site de cada negócio uma vez e extrai Instagram, Facebook, LinkedIn,
e-mails e o número de WhatsApp que o próprio dono colocou no botão do site (o melhor número que existe).

Custo: zero token. Só HTTP + regex, em paralelo. Só biblioteca padrão.
As funções extrair_* são puras e têm teste; só `enriquecer` toca a rede.
"""
from __future__ import annotations

import ipaddress
import os
import re
import socket
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from concurrent.futures import ThreadPoolExecutor

from normalizar import email_valido, telefone_br

UA = "Mozilla/5.0 (compatible; leads-cerebro/1.0; +https://www.drrobertorodrigues.com)"

REDES_RE = {
    "instagram": re.compile(r"https?://(?:www\.)?instagram\.com/([A-Za-z0-9_.]+)", re.I),
    "facebook": re.compile(r"https?://(?:www\.|m\.|web\.|pt-br\.)?facebook\.com/([A-Za-z0-9_.\-]+)", re.I),
    "linkedin": re.compile(r"https?://(?:[a-z]{2,3}\.)?linkedin\.com/(?:company|in|school)/([A-Za-z0-9_.\-%]+)", re.I),
}
_HANDLE_LIXO = {"", "home", "pages", "people", "help", "about", "policies", "policy", "legal", "tos", "privacy",
                "settings", "sharer", "tr", "profile.php", "plugins", "dialog", "intent", "login", "share.php",
                "permalink.php", "p", "reel", "reels", "explore", "stories", "tv", "watch", "events", "groups",
                "marketplace", "gaming", "photo", "hashtag", "search", "accounts", "share", "business", "ads"}
WHATSAPP_RE = re.compile(
    r"(?:api\.whatsapp\.com/send/?\?(?:[^\"'\s]*&)?phone=|wa\.me/|web\.whatsapp\.com/send/?\?(?:[^\"'\s]*&)?phone=|whatsapp://send\?phone=)"
    r"(?:%2B|\+)?(\d{10,15})", re.I)


def extrair_redes(html):
    out = {"instagram": "", "facebook": "", "linkedin": ""}
    for rede, rx in REDES_RE.items():
        for m in rx.finditer(html or ""):
            h = m.group(1).lower().rstrip(".")
            if h in _HANDLE_LIXO or (rede == "facebook" and (h.isdigit() or len(h) < 3)):
                continue
            out[rede] = m.group(0).rstrip("\"'/").replace("\\", "")
            break
    return out


def extrair_emails(html, maximo=3):
    out = []
    for m in re.finditer(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}", html or ""):
        v = email_valido(m.group(0))
        if v and v not in out:
            out.append(v)
        if len(out) >= maximo:
            break
    return out


def extrair_whatsapp(html):
    """Número do botão de WhatsApp do site, normalizado (E.164 sem '+'). '' se não houver."""
    for m in WHATSAPP_RE.finditer(html or ""):
        n = telefone_br(m.group(1))
        if n:
            return n
    return ""


# ── Rede segura: o site de um negócio é entrada hostil ────────────────────────
# Lição do mestre (campanha de e-mail 01/10): enriquecedor sem trava de SSRF nem robots.txt não entra em produção.
_NOMES_PROIBIDOS = ("localhost", ".local", ".internal", ".localdomain", "metadata.google", "host.docker.internal")


def _ip_publico(ip):
    try:
        a = ipaddress.ip_address(ip)
    except ValueError:
        return False
    return a.is_global and not a.is_multicast


def destino_permitido(url):
    """Só http(s), host público. Recusa loopback, rede privada, link-local (metadados de nuvem) e nomes internos.
    Com proxy de saída configurado e DNS local indisponível, delega a política ao proxy."""
    try:
        u = urllib.parse.urlsplit(url)
    except ValueError:
        return False
    host = (u.hostname or "").lower().rstrip(".")
    if u.scheme not in ("http", "https") or not host:
        return False
    if host in _NOMES_PROIBIDOS or any(host.endswith(n) for n in _NOMES_PROIBIDOS if n.startswith(".")):
        return False
    try:
        porta = u.port
    except ValueError:                                   # 'javascript:alert(1)' e afins
        return False
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


def baixar_html(url, timeout=10, max_bytes=400_000):
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
            tipo = r.headers.get("Content-Type", "")
            if tipo and "html" not in tipo and "text" not in tipo and "xml" not in tipo:
                return ""                                         # PDF, imagem, zip: não é página
            return r.read(max_bytes).decode("utf-8", "replace")
    except Exception:  # noqa: BLE001
        return ""


def enriquecer_um(lead, html):
    """Aplica as extrações a um lead (puro: recebe o HTML já baixado)."""
    lead.update(extrair_redes(html))
    novos = extrair_emails(html)
    atuais = [e for e in (lead.get("emails") or "").split("; ") if e]
    lead["emails"] = "; ".join(atuais + [e for e in novos if e not in atuais])
    lead["whatsapp_site"] = extrair_whatsapp(html)
    if lead["whatsapp_site"] and not lead.get("whatsapp"):
        lead["whatsapp"] = f"https://wa.me/{lead['whatsapp_site']}"
    lead["sem_redes"] = "nao" if (lead["instagram"] or lead["facebook"] or lead["linkedin"]) else "sim"
    return lead


def enriquecer(leads, trabalhadores=8, timeout=10, saida=sys.stderr):
    """Visita cada site uma vez, em paralelo. Lead sem site fica marcado sem_redes='sim'."""
    for l in leads:
        l.setdefault("instagram", ""); l.setdefault("facebook", ""); l.setdefault("linkedin", "")
        l.setdefault("whatsapp_site", ""); l["sem_redes"] = "sim"
    com_site = [l for l in leads if l.get("site")]
    feitos = 0

    def trabalho(l):
        return enriquecer_um(l, baixar_html(l["site"], timeout=timeout))

    with ThreadPoolExecutor(max_workers=trabalhadores) as ex:
        for _ in ex.map(trabalho, com_site):
            feitos += 1
            print(f"\r  sites visitados: {feitos}/{len(com_site)}", end="", file=saida, flush=True)
    if com_site:
        print(file=saida)
    return {"sites": len(com_site),
            "redes": sum(1 for l in leads if l["sem_redes"] == "nao"),
            "whatsapp_site": sum(1 for l in leads if l["whatsapp_site"]),
            "emails": sum(1 for l in leads if l.get("emails"))}
