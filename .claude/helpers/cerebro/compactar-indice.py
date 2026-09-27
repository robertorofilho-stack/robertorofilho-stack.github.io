#!/usr/bin/env python3
"""COMPACTAR ÍNDICE — tira do MEMORY.md as entradas mais antigas e as leva para MEMORY-ARQUIVO.md, nas DUAS cópias.

Por quê: o MEMORY.md é cortado acima de ~24,4 KB (gotcha-indice-memoria-truncado, 27/09) — o fim do índice deixa de
ser lido. E o sincronizar.sh funde as duas cópias (local do Mac + repositório) por UNIÃO de links: linha tirada de uma
cópia só volta no sync seguinte. Então a mesma escolha é aplicada nas duas, na mesma execução.

Regras (Lei da Monotonia — nada some):
  - nunca apaga arquivo de memória; a linha vai para MEMORY-ARQUIVO.md da mesma pasta;
  - nunca move: cabeçalho, seção "LEIS E REGRAS MESTRAS", linha com LEI / 🔴 / ⭐, nem as entradas do topo (as mais novas);
  - move primeiro a entrada mais antiga: data do gancho ("(12/09)", "2026-09-12") ou, sem ela, a data do próprio
    arquivo da memória (frontmatter "modified" ou a data mais recente citada nele); sem nenhuma data, não sai;
  - nada dos últimos 7 dias sai;
  - para ao atingir o alvo (padrão 23.500 bytes, folga abaixo do corte);
  - confere antes de gravar: links(MEMORY) ∪ links(ARQUIVO) depois == antes, em cada cópia. Diferença = recusa (sai 2).

Uso:
  compactar-indice.py PASTA_LOCAL PASTA_REPO [--alvo 23500] [--aplicar]
  sem --aplicar: só mostra o que moveria (nada é gravado)
"""
import datetime as dt
import os
import re
import shutil
import sys

LINK = re.compile(r"\]\(([^)\s]+\.md)\)")
PROTEGIDO = re.compile(r"\bLEI\b|🔴|⭐|lei-|feedback-|gotcha-", re.I)   # leis, regras de comportamento e gotchas ficam
SECAO_PROTEGIDA = "LEIS E REGRAS MESTRAS"
DATA_BR = re.compile(r"\b(\d{1,2})/(\d{1,2})(?:/(20\d\d))?\b")
DATA_ISO = re.compile(r"\b(20\d\d)-(\d\d)-(\d\d)\b")


def ler(p):
    try:
        with open(p, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def links(txt):
    return set(LINK.findall(txt))


def data_da_linha(l, hoje):
    datas = []
    for m in DATA_ISO.finditer(l):
        try:
            datas.append(dt.date(*map(int, m.groups())))
        except ValueError:
            pass
    for m in DATA_BR.finditer(l):
        d, mes, ano = int(m.group(1)), int(m.group(2)), int(m.group(3) or hoje.year)
        try:
            x = dt.date(ano, mes, d)
        except ValueError:
            continue
        if x > hoje and not m.group(3):
            x = x.replace(year=x.year - 1)
        datas.append(x)
    return min(datas) if datas else None


def data_do_arquivo(pasta, nome, hoje):
    txt = ler(os.path.join(pasta, nome))[:20000]
    m = re.search(r"modified:\s*(20\d\d)-(\d\d)-(\d\d)", txt)
    if m:
        return dt.date(*map(int, m.groups()))
    datas = [x for x in (data_da_linha(l, hoje) for l in txt.splitlines()) if x]
    return max(datas) if datas else None


def candidatas(texto, hoje, pasta=None):
    """(data, 1º link, linha) das linhas que podem sair, da mais antiga para a mais nova."""
    out, secao, viu_secao = [], "", False
    for l in texto.splitlines():
        if l.startswith("#"):
            if l.startswith("## "):
                secao, viu_secao = l, True
            continue
        if not viu_secao or not l.startswith("- "):
            continue                                   # topo do índice = entradas mais novas: ficam
        if SECAO_PROTEGIDA in secao or PROTEGIDO.search(l):
            continue
        lk = LINK.findall(l)
        if not lk or "MEMORY-ARQUIVO.md" in lk:
            continue
        d = data_da_linha(l, hoje) or (data_do_arquivo(pasta, lk[0], hoje) if pasta else None)
        if d and (hoje - d).days >= 7:
            out.append((d, lk[0], l))
    out.sort(key=lambda x: (x[0], x[1]))
    return out


def escolher(texto, alvo, hoje, pasta=None):
    tamanho = len(texto.encode("utf-8"))
    escolha = []
    for d, lk, l in candidatas(texto, hoje, pasta):
        if tamanho <= alvo:
            break
        escolha.append((d, lk, l))
        tamanho -= len((l + "\n").encode("utf-8"))
    return escolha, tamanho


def aplicar_em(pasta, primeiros_links, hoje, gravar):
    idx, arq = os.path.join(pasta, "MEMORY.md"), os.path.join(pasta, "MEMORY-ARQUIVO.md")
    texto, arquivo = ler(idx), ler(arq)
    antes = links(texto) | links(arquivo)
    ficam, saem = [], []
    for l in texto.splitlines(keepends=True):
        lk = LINK.findall(l)
        if l.startswith("- ") and lk and lk[0] in primeiros_links:
            saem.append(l.rstrip("\n"))
        else:
            ficam.append(l)
    novo_idx = "".join(ficam)
    ja = set(arquivo.splitlines())
    novas = [l for l in saem if l not in ja]
    novo_arq = arquivo.rstrip("\n") + (f"\n\n## Compactação de {hoje.isoformat()} (índice acima do corte)\n" + "\n".join(novas) + "\n"
                                      if novas else "\n")
    depois = links(novo_idx) | links(novo_arq)
    if depois != antes:
        return {"pasta": pasta, "erro": f"ponteiros mudariam: {sorted(antes ^ depois)[:5]}"}
    r = {"pasta": pasta, "saem": len(saem), "bytes_antes": len(texto.encode()), "bytes_depois": len(novo_idx.encode())}
    if gravar and saem:
        for p in (idx, arq):
            if os.path.exists(p):
                shutil.copy2(p, p + ".antes-compactar")
        for p, conteudo in ((arq, novo_arq), (idx, novo_idx)):
            tmp = p + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(conteudo)
            os.replace(tmp, p)
    return r


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    gravar = "--aplicar" in a
    alvo = int(a[a.index("--alvo") + 1]) if "--alvo" in a else 23500
    hoje = dt.date.fromisoformat(a[a.index("--hoje") + 1]) if "--hoje" in a else dt.date.today()
    pastas = [x for i, x in enumerate(a) if not x.startswith("--") and (i == 0 or a[i - 1] not in ("--alvo", "--hoje"))]
    pastas = [os.path.expanduser(p) for p in pastas]
    if len(pastas) < 1 or not all(os.path.isfile(os.path.join(p, "MEMORY.md")) for p in pastas):
        print(__doc__)
        print("compactar-indice: informe as pastas que têm MEMORY.md (local do Mac e claude-config/memory do repo)", file=sys.stderr)
        return 2
    base = max(pastas, key=lambda p: len(ler(os.path.join(p, "MEMORY.md")).encode()))    # a maior decide a escolha
    escolha, previsto = escolher(ler(os.path.join(base, "MEMORY.md")), alvo, hoje, base)
    primeiros = {lk for _, lk, _ in escolha}
    print(f"{'APLICANDO' if gravar else 'SIMULAÇÃO (nada gravado)'} · alvo {alvo} bytes · {len(escolha)} entrada(s) mais antigas saem:")
    for d, lk, l in escolha:
        print(f"  {d.isoformat()}  {l[:100]}")
    erros = 0
    for p in pastas:
        r = aplicar_em(p, primeiros, hoje, gravar)
        if "erro" in r:
            erros += 1
            print(f"  ✗ {p}: RECUSADO — {r['erro']}")
        else:
            print(f"  ✓ {p}: {r['bytes_antes']} → {r['bytes_depois']} bytes · {r['saem']} linha(s) para MEMORY-ARQUIVO.md")
    if erros:
        return 2
    if previsto > alvo:
        print(f"  ⚠ só há entradas antigas para chegar a {previsto} bytes (alvo {alvo}) — o resto é recente ou protegido")
    if not gravar and escolha:
        print("\nPara aplicar: rode de novo com --aplicar")
    return 0


if __name__ == "__main__":
    sys.exit(main())
