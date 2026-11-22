#!/usr/bin/env python3
"""Poesia em vídeo: trecho famoso de poeta em DOMÍNIO PÚBLICO, narrado por voz masculina suave, com vídeos reais.

Uso:  python3 pagina-poesia.py --config paginas/poesia.json [--quantos 1]

Regras embutidas:
- Só autores mortos há mais de 70 anos (Lei 9.610/98, art. 41): a lista `poemas` da config é curada assim, e o script
  recusa qualquer autor com `morte` > ano atual − 71.
- O texto vem da Wikisource (fonte pública). A IA só ESCOLHE o trecho; cada verso escolhido é conferido contra o
  original (similaridade ≥ 0,85, tolerando só a ortografia modernizada). Verso que não confere → vídeo descartado.
- Voz suave e lenta + trilha sintetizada própria (sem música de terceiros). Vídeos de banco gratuito.
"""
import argparse, datetime, difflib, html, importlib.util, json, os, random, re, sys, unicodedata, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
_sp = importlib.util.spec_from_file_location("nv", os.path.join(AQUI, "noticia-em-video.py"))
nv = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(nv)
import banco_videos

PEDIDO = """Abaixo está o texto ORIGINAL do poema "{titulo}", de {autor}, tirado da Wikisource (pode ter lixo de página).
Escolha o trecho MAIS FAMOSO e emocionante, de 6 a 14 versos, dividido em 2 a 4 estrofes curtas para narrar em vídeo.
COPIE os versos exatamente como estão (pode só atualizar a ortografia antiga: "Exilio"→"Exílio", "ph"→"f", "y"→"i"; NÃO
troque palavras, NÃO invente, NÃO resuma). Para cada estrofe, dê 2 a 4 palavras em inglês para achar um vídeo real de
banco de imagens que combine com o sentimento da estrofe (natureza, mar, céu, luz, pessoas de costas, cidade antiga).
Devolva APENAS JSON: {{"estrofes":[{{"versos":["...","..."],"busca":"..."}}],"legenda":"1 frase sobre o poema + 3 hashtags"}}

TEXTO:
{texto}"""


def norm(t):
    t = unicodedata.normalize("NFKD", t.lower()); t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.replace("y", "i").replace("ph", "f").replace("th", "t")
    return re.sub(r"[^a-z]+", " ", t).strip()


def ler_wikisource(pagina):
    h = urllib.request.urlopen(urllib.request.Request("https://pt.wikisource.org/wiki/" + urllib.request.quote(
        pagina.replace(" ", "_")), headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read().decode("utf-8", "ignore")
    b = h.split('class="mw-parser-output"', 1)[-1]
    b = re.sub(r"(?s)<(table|style|script|sup)[^>]*>.*?</\1>", "", b)
    b = re.sub(r"<br\s*/?>", "\n", b); b = re.sub(r"</p>|</div>", "\n\n", b)
    t = html.unescape(re.sub(r"<[^>]+>", "", b))
    return re.sub(r"\n{3,}", "\n\n", t).strip()[:7000]


def confere(versos, original):
    linhas = [norm(l) for l in original.splitlines() if norm(l)]
    for v in versos:
        n = norm(v)
        if not n:
            continue
        melhor = max((difflib.SequenceMatcher(None, n, l).ratio() for l in linhas), default=0)
        if melhor < 0.85:
            return False, v
    return True, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True); ap.add_argument("--quantos", type=int, default=1)
    a = ap.parse_args()
    cfg = json.load(open(os.path.expanduser(a.config)))
    pasta = os.path.expanduser(cfg["pasta"]); os.makedirs(pasta, exist_ok=True)
    est_arq = os.path.join(pasta, "estado.json")
    estado = json.load(open(est_arq)) if os.path.exists(est_arq) else {"feitos": []}
    limite = datetime.date.today().year - 71
    fila = [p for p in cfg["poemas"] if p["pagina"] not in estado["feitos"] and p["morte"] <= limite]
    recusados = [p["autor"] for p in cfg["poemas"] if p["morte"] > limite]
    if recusados:
        print("fora (ainda protegidos por direito autoral):", ", ".join(sorted(set(recusados))), file=sys.stderr)
    random.shuffle(fila)
    destino = os.path.join(pasta, "pendentes", datetime.date.today().isoformat()); os.makedirs(destino, exist_ok=True)
    feitos = 0
    for p in fila:
        if feitos >= a.quantos:
            break
        try:
            original = ler_wikisource(p["pagina"])
            r = nv.openrouter({"model": "google/gemini-2.5-pro", "response_format": {"type": "json_object"},
                               "messages": [{"role": "user", "content": PEDIDO.format(
                                   titulo=p["titulo"], autor=p["autor"], texto=original)}]}, timeout=240)
            j = json.loads(re.sub(r"^```(json)?|```$", "", r["choices"][0]["message"]["content"].strip(), flags=re.M))
            todos = [v for e in j["estrofes"] for v in e["versos"]]
            ok, ruim = confere(todos, original)
            if not ok:
                print(f"• {p['titulo']}: verso não confere com o original ({ruim!r}) — descartado"); continue
            segs = [{"tipo": "titulo", "fala": f"{p['titulo']}. De {p['autor']}.", "tela": p["titulo"],
                     "autor": p["autor"], "busca": j["estrofes"][0]["busca"], "pausa": 1.0}]
            for e in j["estrofes"]:
                segs.append({"tipo": "verso", "fala": " ".join(e["versos"]), "tela": "\n".join(e["versos"]),
                             "busca": e["busca"], "pausa": cfg.get("pausa", 1.1)})
            nome = re.sub(r"[^a-z0-9]+", "-", norm(p["titulo"]))[:40].strip("-")
            mp4 = os.path.join(destino, f"{datetime.datetime.now():%H%M}-{nome}.mp4")
            dur, cred = banco_videos.montar(segs, cfg, mp4, nv.renderizar, nv.CSS_AVATAR, cfg["perfil"], "#f3d9a4")
            leg = (f"“{p['titulo']}”, de {p['autor']} ({p.get('obra', 'domínio público')}).\n\n{j.get('legenda', '')}"
                   + (("\n\nVídeos: " + "; ".join(cred)) if cred else ""))
            open(mp4[:-4] + ".txt", "w").write(leg + "\n")
            estado["feitos"].append(p["pagina"]); json.dump(estado, open(est_arq, "w"), ensure_ascii=False, indent=1)
            feitos += 1
            print(f"• {p['titulo']} — {p['autor']}: pronto {dur:.1f}s → {mp4}")
        except Exception as e:
            print(f"• {p['titulo']}: ERRO {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
