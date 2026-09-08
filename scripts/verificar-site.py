#!/usr/bin/env python3
"""
Varredura completa do site antes de publicar.

Checa, em uma passada:
  1. SEO/AEO e JSON-LD de cada página (mesma regra do hook)
  2. sitemap.xml x arquivos em disco (nos dois sentidos)
  3. links internos quebrados
  4. links do llms.txt que não existem mais
  5. imagens referenciadas que sumiram

Uso:  python3 scripts/verificar-site.py
Saída: 0 se limpo, 1 se houver problema. Só stdlib.
"""
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".claude" / "hooks"))
from validar_pagina import achar_problemas  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
DOMINIO = "https://www.drrobertorodrigues.com"
IGNORAR = {".git", "node_modules", ".claude"}


def paginas() -> list[Path]:
    return sorted(
        p for p in RAIZ.rglob("*.html")
        if not any(parte in IGNORAR for parte in p.parts)
    )


def rota(pagina: Path) -> str:
    """Caminho do arquivo -> rota pública ('/joelho/artrose-do-joelho/')."""
    rel = pagina.relative_to(RAIZ)
    if rel.name == "index.html":
        pai = rel.parent.as_posix()
        return "/" if pai == "." else f"/{pai}/"
    return f"/{rel.as_posix()}"


def main() -> int:
    achados: list[str] = []
    todas = paginas()
    rotas_em_disco = {rota(p) for p in todas}

    # 1. Qualidade de cada página
    for p in todas:
        for problema in achar_problemas(p.read_text(encoding="utf-8", errors="replace"), p):
            achados.append(f"[pagina]  {rota(p)}: {problema}")

    # 2. sitemap.xml nos dois sentidos
    sitemap = RAIZ / "sitemap.xml"
    if sitemap.is_file():
        urls = re.findall(r"<loc>\s*([^<]+?)\s*</loc>", sitemap.read_text(encoding="utf-8"))
        rotas_no_sitemap = {urlparse(u).path or "/" for u in urls}
        for r in sorted(rotas_no_sitemap - rotas_em_disco):
            achados.append(f"[sitemap] {r} está no sitemap mas não existe em disco (404 para o Google)")
        for r in sorted(rotas_em_disco - rotas_no_sitemap):
            achados.append(f"[sitemap] {r} existe mas está fora do sitemap (não será rastreada)")
    else:
        achados.append("[sitemap] sitemap.xml ausente")

    # 3. Links internos e 5. imagens
    for p in todas:
        html = p.read_text(encoding="utf-8", errors="replace")
        alvos = re.findall(r'(?:href|src|srcset)\s*=\s*["\']([^"\']+)["\']', html)
        for alvo in alvos:
            alvo = alvo.split()[0].split("?")[0].split("#")[0]
            if not alvo.startswith("/") or alvo.startswith("//"):
                continue  # externo, âncora ou relativo — fora do escopo
            destino = RAIZ / alvo.lstrip("/")
            if alvo.endswith("/"):
                destino = destino / "index.html"
            if not destino.exists():
                achados.append(f"[link]    {rota(p)} aponta para {alvo} que não existe")

    # 4. llms.txt
    llms = RAIZ / "llms.txt"
    if llms.is_file():
        for url in re.findall(rf"{re.escape(DOMINIO)}([^\s\)]*)", llms.read_text(encoding="utf-8")):
            caminho = url or "/"
            if caminho.startswith("/") and caminho not in rotas_em_disco:
                achados.append(f"[llms]    llms.txt cita {caminho} que não existe em disco")

    if not achados:
        print(f"Site limpo: {len(todas)} páginas verificadas, nenhum problema.")
        return 0

    print(f"{len(achados)} problema(s) em {len(todas)} páginas:\n")
    for a in sorted(set(achados)):
        print(f"  {a}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
