#!/usr/bin/env python3
"""RUBRICA — nota ponderada, auditoria dos itens e calibração do juiz (CMU 11-768 aula 10, deep research eval).

Três ferramentas pequenas, sem rede, para /auditar, /conselho, /cacar-produto e /arvore:

  nota         score = Σ w·b / Σ w  (b = 1 se o item foi atendido, 0 se não; ou fração 0–1)
               Pontua por ITEM atendido, nunca por extensão da resposta (aula 9: não premiar resposta longa).
  auditar      a aula mostrou que ~15% dos itens de rubrica gerados por LLM eram vazios, errados ou pouco claros.
               Antes de usar: acusa item curto, vago (sem critério checável), duplicado e peso inválido.
  concordancia juiz LLM × humano: % de acordo e kappa de Cohen. Na aula, juiz × especialista = 79% e
               especialista × especialista = 80% — só se automatiza decisão quando o juiz chega perto do humano.

Uso:
  rubrica.py nota rubrica.json julgamentos.json      rubrica: [{"item": "...", "peso": 3}, ...]
                                                     julgamentos: {"<item>": true|false|0.5, ...}
  rubrica.py auditar rubrica.json
  rubrica.py concordancia juiz.json humano.json [--base 0.80]   listas de rótulos na mesma ordem
"""
import json
import re
import sys
import unicodedata

VAGOS = ("bom", "boa", "adequad", "de qualidade", "claro", "clara", "interessante", "relevante", "legal",
         "satisfatori", "apropriad", "suficiente", "coerente", "bem feito", "bem escrito")
CHECAVEL = re.compile(r"\d|%|R\$|US\$|cita|fonte|link|prazo|preço|preco|garantia|pix|cartão|cartao|nunca|sempre|"
                      r"inclui|contém|contem|menciona|lista|mostra|verific|teste|exato|máximo|maximo|mínimo|minimo")


def _norm(t):
    t = unicodedata.normalize("NFKD", t.lower())
    return "".join(c for c in t if not unicodedata.combining(c))


def nota(rubrica, julgamentos):
    tot = sum(float(i.get("peso", 1)) for i in rubrica)
    if tot <= 0:
        raise ValueError("soma de pesos ≤ 0")
    s = 0.0
    faltando = []
    for i in rubrica:
        b = julgamentos.get(i["item"])
        if b is None:
            faltando.append(i["item"])
            b = 0
        s += float(i.get("peso", 1)) * (1.0 if b is True else 0.0 if b is False else max(0.0, min(1.0, float(b))))
    return round(s / tot, 4), faltando


def auditar(rubrica):
    problemas = []
    vistos = []
    for n, i in enumerate(rubrica, 1):
        txt = str(i.get("item", "")).strip()
        palavras = re.findall(r"\w+", txt)
        try:
            peso = float(i.get("peso", 1))
        except (TypeError, ValueError):
            peso = -1
        if len(palavras) < 4:
            problemas.append((n, "curto/vazio", txt))
        low = _norm(txt)
        if any(v in low for v in VAGOS) and not CHECAVEL.search(low):
            problemas.append((n, "vago: sem critério checável", txt))
        if peso <= 0:
            problemas.append((n, "peso inválido", txt))
        a = set(re.findall(r"\w{3,}", low))
        for m, b in vistos:
            if a and b and len(a & b) / len(a | b) >= 0.7:
                problemas.append((n, f"duplica o item {m}", txt))
        vistos.append((n, a))
    return problemas


def concordancia(a, b):
    if len(a) != len(b) or not a:
        raise ValueError("listas de tamanhos diferentes ou vazias")
    n = len(a)
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    rotulos = set(a) | set(b)
    pe = sum((a.count(r) / n) * (b.count(r) / n) for r in rotulos)
    kappa = (po - pe) / (1 - pe) if pe < 1 else 1.0
    return round(po, 4), round(kappa, 4)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] not in ("nota", "auditar", "concordancia"):
        print(__doc__)
        return 2
    cmd, args = argv[0], argv[1:]
    ler = lambda p: json.load(open(p, encoding="utf-8"))  # noqa: E731
    if cmd == "nota":
        s, faltando = nota(ler(args[0]), ler(args[1]))
        print(f"nota ponderada: {s:.3f}" + (f" · itens sem julgamento (contados como 0): {faltando}" if faltando else ""))
        return 0
    if cmd == "auditar":
        pr = auditar(ler(args[0]))
        for n, tipo, txt in pr:
            print(f"✗ item {n}: {tipo} — {txt[:90]}")
        print(f"{len(pr)} problema(s) em {len(ler(args[0]))} itens" + (" — corrigir ANTES de usar a rubrica" if pr else " ✓"))
        return 1 if pr else 0
    base = 0.80
    if "--base" in args:
        base = float(args[args.index("--base") + 1])
    po, k = concordancia(ler(args[0]), ler(args[1]))
    ok = po >= base - 0.05
    print(f"acordo juiz×humano {po:.0%} · kappa {k:.2f} · referência humano×humano {base:.0%} → "
          + ("PODE automatizar esta decisão" if ok else "NÃO automatizar: juiz abaixo do humano"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
