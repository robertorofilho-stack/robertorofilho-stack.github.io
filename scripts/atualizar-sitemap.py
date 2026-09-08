#!/usr/bin/env python3
"""
Sincroniza sitemap.xml com o que existe em disco e com o que o git diz que mudou.

  - páginas novas entram no sitemap
  - páginas apagadas saem
  - lastmod só muda nas páginas realmente alteradas (git), não em todas

Uso:
    python3 scripts/atualizar-sitemap.py            # aplica
    python3 scripts/atualizar-sitemap.py --conferir # só mostra o que mudaria

Só stdlib.
"""
import argparse
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parent.parent
SITEMAP = RAIZ / "sitemap.xml"
DOMINIO = "https://www.drrobertorodrigues.com"
IGNORAR = {".git", "node_modules", ".claude"}


def rota(pagina: Path) -> str:
    rel = pagina.relative_to(RAIZ)
    if rel.name == "index.html":
        pai = rel.parent.as_posix()
        return "/" if pai == "." else f"/{pai}/"
    return f"/{rel.as_posix()}"


def rotas_em_disco() -> list[str]:
    paginas = [p for p in RAIZ.rglob("*.html")
               if not any(parte in IGNORAR for parte in p.parts)]
    # raiz primeiro, depois alfabética — sitemap legível
    return sorted((rota(p) for p in paginas), key=lambda r: (r != "/", r))


def rotas_alteradas() -> set[str]:
    """Rotas cujo HTML mudou segundo o git (working tree + staged)."""
    try:
        saida = subprocess.run(
            ["git", "-C", str(RAIZ), "status", "--porcelain"],
            capture_output=True, text=True, check=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return set()
    mudadas = set()
    for linha in saida.splitlines():
        caminho = linha[3:].strip().strip('"').split(" -> ")[-1]
        if caminho.endswith(".html"):
            arquivo = RAIZ / caminho
            if arquivo.is_file():
                mudadas.add(rota(arquivo))
    return mudadas


def lastmods_atuais() -> dict[str, str]:
    if not SITEMAP.is_file():
        return {}
    texto = SITEMAP.read_text(encoding="utf-8")
    mapa = {}
    for loc, mod in re.findall(r"<loc>\s*([^<]+?)\s*</loc>\s*<lastmod>\s*([^<]+?)\s*</lastmod>", texto):
        mapa[urlparse(loc).path or "/"] = mod
    return mapa


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--conferir", action="store_true",
                    help="mostra o que mudaria sem gravar")
    args = ap.parse_args()

    hoje = date.today().isoformat()
    disco = rotas_em_disco()
    antigos = lastmods_atuais()
    alteradas = rotas_alteradas()

    novas = [r for r in disco if r not in antigos]
    removidas = [r for r in antigos if r not in disco]
    atualizadas = [r for r in disco if r in antigos and r in alteradas
                   and antigos[r] != hoje]

    linhas = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for r in disco:
        if r in novas or r in alteradas:
            mod = hoje
        else:
            mod = antigos.get(r, hoje)
        linhas.append(f"  <url><loc>{DOMINIO}{r}</loc><lastmod>{mod}</lastmod></url>")
    linhas.append("</urlset>")
    novo = "\n".join(linhas) + "\n"

    for r in novas:
        print(f"  + entra no sitemap: {r}")
    for r in removidas:
        print(f"  - sai do sitemap:   {r}")
    for r in atualizadas:
        print(f"  ~ lastmod {antigos[r]} -> {hoje}: {r}")
    if not (novas or removidas or atualizadas):
        print(f"  sitemap já em dia ({len(disco)} páginas).")
        return 0

    if args.conferir:
        print("\n(--conferir: nada foi gravado)")
        return 0

    SITEMAP.write_text(novo, encoding="utf-8")
    print(f"\nsitemap.xml atualizado: {len(disco)} páginas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
