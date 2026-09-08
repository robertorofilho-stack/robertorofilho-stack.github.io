#!/usr/bin/env python3
"""
Guarda-corpo do SEO médico.

Roda como hook PostToolUse depois de qualquer Edit/Write em .html deste site.
Se a página perder um elemento crítico de SEO/AEO ou quebrar o JSON-LD,
devolve o erro para o Claude (exit 2) para ele corrigir sozinho, na hora.

Também é importado por scripts/verificar-site.py para a varredura completa.
Sem dependências externas: só stdlib.
"""
import json
import re
import sys
from pathlib import Path

DOMINIO = "https://www.drrobertorodrigues.com"

# --- Elementos sem os quais a página perde ranqueamento ou rich result ---
OBRIGATORIOS = [
    (r"<title>\s*\S.*?</title>",
     "title vazio ou ausente"),
    (r'<meta\s+name=["\']description["\']\s+content=["\'][^"\']{50,}',
     "meta description ausente ou com menos de 50 caracteres"),
    (r'<link\s+rel=["\']canonical["\']\s+href=["\']https://',
     "link canonical ausente ou não-absoluto"),
    (r'<meta\s+property=["\']og:title["\']', "og:title ausente"),
    (r'<meta\s+property=["\']og:description["\']', "og:description ausente"),
    (r'<meta\s+property=["\']og:image["\']', "og:image ausente"),
    (r'<meta\s+property=["\']og:url["\']', "og:url ausente"),
    (r'<html[^>]+lang=["\']pt-BR["\']', 'html sem lang="pt-BR"'),
    (r'<meta\s+name=["\']viewport["\']', "meta viewport ausente"),
]


def raiz_do_site(caminho: Path) -> Path | None:
    """Sobe até a pasta que contém o CNAME — a raiz publicada do site."""
    for pasta in [caminho.parent, *caminho.parents]:
        if (pasta / "CNAME").is_file():
            return pasta
    return None


def rota_publica(caminho: Path, raiz: Path) -> str:
    """Caminho em disco -> rota publicada ('/joelho/artrose-do-joelho/')."""
    rel = caminho.relative_to(raiz)
    if rel.name == "index.html":
        pai = rel.parent.as_posix()
        return "/" if pai == "." else f"/{pai}/"
    return f"/{rel.as_posix()}"


def achar_problemas(html: str, caminho: Path) -> list[str]:
    problemas: list[str] = []

    for padrao, erro in OBRIGATORIOS:
        if not re.search(padrao, html, re.I | re.S):
            problemas.append(erro)

    # JSON-LD precisa ser JSON válido, senão o Google descarta o rich result inteiro
    blocos = re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html, re.I | re.S)
    if not blocos:
        problemas.append("nenhum bloco JSON-LD (schema.org) — perde rich result no Google")
    for i, bloco in enumerate(blocos, 1):
        try:
            json.loads(bloco)
        except json.JSONDecodeError as e:
            problemas.append(
                f"JSON-LD #{i} inválido: {e.msg} (linha {e.lineno}, coluna {e.colno})")

    # Imagem sem alt = acessibilidade e SEO de imagem perdidos
    for tag in re.findall(r"<img\b[^>]*>", html, re.I):
        if not re.search(r'\balt\s*=\s*["\']', tag):
            problemas.append(f"<img> sem alt: {tag[:90]}")

    # Canonical tem que apontar para a própria rota, no domínio oficial
    m = re.search(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)', html, re.I)
    raiz = raiz_do_site(caminho)
    if m and raiz:
        declarado = m.group(1)
        esperado = f"{DOMINIO}{rota_publica(caminho, raiz)}"
        if declarado.rstrip("/") != esperado.rstrip("/"):
            problemas.append(f"canonical é {declarado} mas deveria ser {esperado}")

    return problemas


def main() -> int:
    try:
        evento = json.load(sys.stdin)
    except Exception:
        return 0  # sem payload utilizável, não atrapalha o fluxo

    caminho_str = (evento.get("tool_input") or {}).get("file_path", "")
    if not caminho_str.endswith(".html"):
        return 0

    caminho = Path(caminho_str)
    if not caminho.is_file():
        return 0

    try:
        html = caminho.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return 0

    problemas = achar_problemas(html, caminho)
    if not problemas:
        return 0

    print(f"SEO/AEO quebrado em {caminho}:", file=sys.stderr)
    for p in problemas:
        print(f"  - {p}", file=sys.stderr)
    print("Corrija antes de seguir: este site é o canal de captação de pacientes.",
          file=sys.stderr)
    return 2  # exit 2 devolve o stderr para o Claude corrigir


if __name__ == "__main__":
    sys.exit(main())
