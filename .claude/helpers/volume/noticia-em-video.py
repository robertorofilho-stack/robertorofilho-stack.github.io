#!/usr/bin/env python3
"""Notícia → vídeo explicado (colagem de papel + narração), formato Reels 1080x1920.

Uso:
  python3 noticia-em-video.py URL_DA_NOTICIA --saida video.mp4 [--perfil @minhapagina] [--voz pt-BR-AntonioNeural]
         [--publico "direita|esquerda|fofoca|saude|geral"] [--sem-imagens] [--fps 24]

Passos: lê a matéria → roteiro em JSON por IA (OpenRouter) só com fatos do texto → narração por cena (edge-tts) →
1 imagem de papel recortado por cena (OpenRouter, opcional) → cenas em HTML animado → quadros pelo Chromium → MP4.

Regras embutidas: o roteiro só usa fatos da matéria e cita a fonte na tela; nenhuma foto da matéria é usada
(foto de agência tem dono) — as imagens são geradas; sem afirmação de saúde como promessa; sem acusar pessoa de crime
que a matéria não afirma.
Custo típico: roteiro ~US$ 0,01 + ~US$ 0,04 por imagem (5 cenas ≈ US$ 0,21); voz grátis.
"""
import argparse, base64, html, json, os, re, shutil, subprocess, sys, tempfile, urllib.request

OR = "https://openrouter.ai/api/v1/chat/completions"
CORES = ["#f2c94c", "#5b8bd9", "#c9a26b", "#e8dfcf", "#e46b4f", "#7fb59a"]


def openrouter(corpo, timeout=180):
    h = {"Content-Type": "application/json"}
    if os.environ.get("OPENROUTER_API_KEY"):
        h["Authorization"] = "Bearer " + os.environ["OPENROUTER_API_KEY"]
    return json.load(urllib.request.urlopen(urllib.request.Request(OR, data=json.dumps(corpo).encode(), headers=h),
                                            timeout=timeout))


def ler_noticia(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    h = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
    tit = (re.search(r'<meta[^>]+property="og:title"[^>]+content="([^"]+)"', h)
           or re.search(r'<meta[^>]+content="([^"]+)"[^>]+property="og:title"', h)
           or re.search(r"<title[^>]*>(.*?)</title>", h, re.S))
    site = (re.search(r'<meta[^>]+property="og:site_name"[^>]+content="([^"]+)"', h)
            or re.search(r'<meta[^>]+content="([^"]+)"[^>]+property="og:site_name"', h))
    corpo = re.sub(r"(?is)<(script|style|nav|header|footer|aside)[^>]*>.*?</\1>", " ", h)
    paras = [html.unescape(re.sub(r"<[^>]+>", "", p)).strip() for p in re.findall(r"(?is)<p[^>]*>(.*?)</p>", corpo)]
    texto = "\n".join(p for p in paras if len(p) > 60)[:9000]
    dom = re.sub(r"^https?://(www\.)?([^/]+).*", r"\2", url)
    nomes = {"bbc.com/portuguese": "BBC News Brasil", "bbc.co": "BBC News", "g1.globo": "g1", "theguardian": "The Guardian",
             "agenciabrasil": "Agência Brasil", "reuters": "Reuters", "apnews": "AP News", "nytimes": "The New York Times"}
    fonte = next((v for k, v in nomes.items() if k in url), html.unescape(site.group(1)) if site else dom)
    return html.unescape(tit.group(1).strip()) if tit else "", texto, fonte


ROTEIRO = """Você é roteirista de um canal de "notícia explicada" em vídeo vertical curto (estilo colagem de papel).
Escreva em português do Brasil, frases curtas, tom de conversa, gancho forte no início. Público: {publico}.
Se a matéria estiver em outro idioma, TRADUZA para o português do Brasil. Nunca copie frases da matéria: reescreva com
suas palavras (os fatos não têm dono; o texto do jornal tem). A fonte é sempre citada na tela.
REGRAS: use SÓ fatos que estão na matéria abaixo; não invente número, nome, data nem fala; não acuse ninguém de crime
que a matéria não afirma; sem promessa de cura ou de dinheiro; o "ângulo" do público muda o ENFOQUE, nunca os fatos.
Duração total da narração: 35 a 55 segundos (≈ 90 a 140 palavras no total).
Devolva APENAS JSON válido neste formato:
{{"manchete_curta": "até 8 palavras, para o recorte de jornal",
  "cenas": [
    {{"fala": "o que o narrador diz (1 ou 2 frases)",
      "palavra": "1 a 3 palavras-chave que aparecem escritas à mão e circuladas",
      "imagem": "objeto ou cena simples para ilustrar, em inglês, sem texto, sem pessoa real identificável",
      "busca": "2 a 4 palavras em inglês para achar um VÍDEO real de banco de imagens que ilustre a cena"}}
  ],
  "fechamento": "frase final curta convidando a seguir a página"}}
Use de 4 a 6 cenas. A 1ª cena é o gancho (pergunta ou fato surpreendente).
MATÉRIA ({fonte}) — título: {titulo}
{texto}"""


def roteiro(titulo, texto, fonte, publico):
    r = openrouter({"model": "google/gemini-2.5-flash", "response_format": {"type": "json_object"},
                    "messages": [{"role": "user", "content": ROTEIRO.format(publico=publico, fonte=fonte,
                                                                            titulo=titulo, texto=texto)}]})
    bruto = r["choices"][0]["message"]["content"]
    bruto = re.sub(r"^```(json)?|```$", "", bruto.strip(), flags=re.M)
    return json.loads(bruto), r.get("usage", {}).get("cost", 0) or 0


def imagem(prompt, destino):
    r = openrouter({"model": "google/gemini-2.5-flash-image", "modalities": ["image", "text"],
                    "messages": [{"role": "user", "content": "Paper cut-out collage style illustration, isolated "
                                  "object on plain white background, no text, no letters, flat cut paper with slight "
                                  "drop shadow: " + prompt}]})
    ims = r["choices"][0]["message"].get("images") or []
    if not ims:
        return 0, False
    open(destino, "wb").write(base64.b64decode(ims[0]["image_url"]["url"].split(",", 1)[1]))
    return r.get("usage", {}).get("cost", 0) or 0, True


def narrar(texto, voz, mp3):
    subprocess.run(["edge-tts", "--voice", voz, "--rate=+8%", "--text", texto, "--write-media", mp3], check=True,
                   capture_output=True)


def duracao(arq):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", arq],
                                capture_output=True, text=True).stdout.strip())


CSS = """
@import url('https://fonts.googleapis.com/css2?family=Caveat:wght@700&family=Anton&family=Special+Elite&display=swap');
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;overflow:hidden}
body{background:var(--cor);font-family:'Special Elite',monospace;position:relative}
.grao{position:absolute;inset:0;opacity:.35;mix-blend-mode:multiply;
 background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='3'/><feColorMatrix values='0 0 0 0 .4  0 0 0 0 .35  0 0 0 0 .3  0 0 0 .55 0'/></filter><rect width='300' height='300' filter='url(%23n)'/></svg>")}
.jornal{position:absolute;left:70px;right:70px;top:120px;background:#f4efe3;padding:40px 46px 50px;
 box-shadow:0 18px 30px rgba(0,0,0,.28);transform:rotate(-1.5deg);
 clip-path:polygon(0 2%,4% 0,12% 1.5%,22% 0,35% 1.2%,48% 0,60% 1.5%,74% 0,86% 1.3%,100% 0,99% 30%,100% 62%,99% 100%,85% 98.5%,70% 100%,52% 98.6%,38% 100%,20% 98.4%,6% 100%,0 98%,1% 60%,0 30%);
 animation:entra .55s cubic-bezier(.2,1.4,.4,1) both}
.mast{font-family:'Anton',sans-serif;font-size:74px;letter-spacing:2px;color:#1d1a16;text-align:center;border-bottom:4px double #1d1a16;padding-bottom:10px}
.data{font-size:28px;text-align:center;color:#4a4237;margin:10px 0 18px}
.manchete{font-family:'Anton',sans-serif;font-size:92px;line-height:1.02;color:#111;text-transform:uppercase}
.recorte{position:absolute;left:90px;right:90px;top:250px;background:#fffdf6;padding:34px 40px;font-family:'Anton',sans-serif;
 font-size:70px;line-height:1.05;color:#141210;text-transform:uppercase;box-shadow:0 14px 24px rgba(0,0,0,.25);
 transform:rotate(var(--rot));clip-path:polygon(0 4%,8% 0,30% 3%,55% 0,80% 3%,100% 0,98% 50%,100% 96%,75% 100%,50% 97%,25% 100%,0 96%,2% 50%);
 animation:entra .5s cubic-bezier(.2,1.4,.4,1) both}
.img{position:absolute;left:50%;top:700px;width:600px;height:600px;margin-left:-300px;mix-blend-mode:multiply;
 animation:pop .6s .25s cubic-bezier(.2,1.5,.4,1) both}
.img img{width:100%;height:100%;object-fit:contain}
.palavra{position:absolute;left:0;right:0;top:1310px;text-align:center;font-family:'Caveat',cursive;font-size:118px;color:#1a1a1a;
 animation:escreve .6s .55s ease-out both}
.palavra span{position:relative;display:inline-block;padding:0 30px}
.palavra svg{position:absolute;left:-10px;top:-18px;width:calc(100% + 20px);height:calc(100% + 36px);overflow:visible}
.palavra ellipse{fill:none;stroke:#d62b1f;stroke-width:9;stroke-linecap:round;stroke-dasharray:1400;stroke-dashoffset:1400;
 animation:circula .7s .95s ease-out forwards}
.leg{position:absolute;left:60px;right:60px;bottom:120px;background:#141210;color:#fff7e6;font-family:'Special Elite',monospace;
 font-size:46px;line-height:1.25;padding:22px 30px;text-align:center;box-shadow:0 10px 20px rgba(0,0,0,.3)}
.fonte{position:absolute;right:50px;top:40px;font-size:26px;color:#1d1a16;background:#fffdf6;padding:6px 14px;transform:rotate(2deg)}
.perfil{position:absolute;left:50px;top:40px;font-family:'Anton',sans-serif;font-size:34px;color:#1d1a16}
.carimbo{position:absolute;left:50%;top:1000px;margin-left:-330px;width:660px;text-align:center;font-family:'Anton',sans-serif;
 font-size:150px;color:#c8261b;border:14px solid #c8261b;border-radius:18px;padding:0 20px;opacity:.88;transform:rotate(-12deg);
 animation:carimba .45s .4s cubic-bezier(.3,1.6,.5,1) both}
.fim{position:absolute;left:80px;right:80px;top:470px;font-family:'Anton',sans-serif;font-size:96px;line-height:1.05;color:#141210;
 text-align:center;text-transform:uppercase;animation:entra .5s both}
.tesoura{position:absolute;font-size:120px;top:200px;animation:corta 1s ease-in-out both}
@keyframes entra{from{transform:translateY(-140px) rotate(-8deg);opacity:0}to{opacity:1}}
@keyframes pop{from{transform:scale(.2) rotate(-25deg);opacity:0}to{transform:scale(1) rotate(0);opacity:1}}
@keyframes escreve{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}
@keyframes circula{to{stroke-dashoffset:0}}
@keyframes carimba{from{transform:scale(3) rotate(-12deg);opacity:0}to{transform:scale(1) rotate(-12deg);opacity:.88}}
@keyframes corta{from{left:-150px}to{left:1100px}}
"""


def _css_avatar():
    import importlib.util
    sp = importlib.util.spec_from_file_location("pt", os.path.join(os.path.dirname(os.path.abspath(__file__)), "pagina-temas.py"))
    src = open(sp.origin).read()
    return src.split('CSS = """', 1)[1].split('"""', 1)[0]


CSS_AVATAR = _css_avatar()


def pagina(cor, miolo, legenda, perfil, fonte):
    return (f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head>"
            f"<body style='--cor:{cor}'><div class='grao'></div>"
            f"<div class='perfil'>{html.escape(perfil)}</div><div class='fonte'>Fonte: {html.escape(fonte)}</div>"
            f"{miolo}<div class='leg'>{html.escape(legenda)}</div></body></html>")


def cena_html(i, c, img, perfil, fonte, manchete, data):
    cor = CORES[i % len(CORES)]
    if i == 0:
        miolo = (f"<div class='jornal'><div class='mast'>O DIÁRIO DE HOJE</div><div class='data'>{html.escape(data)}</div>"
                 f"<div class='manchete'>{html.escape(manchete)}</div></div><div class='tesoura'>✂️</div>")
        cor = "#e8dfcf"
    else:
        rot = [-2.5, 2, -1.2, 2.8, -2][i % 5]
        miolo = f"<div class='recorte' style='--rot:{rot}deg'>{html.escape(manchete)}</div>"
    if img:
        miolo += f"<div class='img'><img src='file://{img}'></div>"
    miolo += (f"<div class='palavra'><span>{html.escape(c['palavra'])}<svg viewBox='0 0 100 100' preserveAspectRatio='none'>"
              f"<ellipse cx='50' cy='50' rx='49' ry='46'/></svg></span></div>")
    return pagina(cor, miolo, c["fala"], perfil, fonte)


def fim_html(frase, perfil, fonte):
    miolo = f"<div class='fim'>{html.escape(frase)}</div><div class='carimbo'>EXPLICADO</div>"
    return pagina("#f2c94c", miolo, perfil, perfil, fonte)


def renderizar(paginas, fps, pasta, png=False):
    lista = os.path.join(pasta, "..", "cenas.json")
    json.dump(paginas, open(lista, "w"))
    js = os.path.join(os.path.dirname(os.path.abspath(__file__)), "renderizar.cjs")
    r = subprocess.run(["node", js, lista, pasta, str(fps)] + (["png"] if png else []), capture_output=True, text=True)
    if r.returncode:
        sys.exit("falha ao renderizar: " + r.stderr[-800:])
    return int(r.stdout.strip().splitlines()[-1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url"); ap.add_argument("--saida", required=True)
    ap.add_argument("--perfil", default="@suapagina"); ap.add_argument("--voz", default="pt-BR-AntonioNeural")
    ap.add_argument("--publico", default="geral"); ap.add_argument("--sem-imagens", action="store_true")
    ap.add_argument("--fps", type=int, default=24); ap.add_argument("--data", default="")
    ap.add_argument("--visual", default="video", choices=["video", "colagem"],
                    help="video = clipes reais de banco gratuito (padrão 22/11); colagem = papel recortado")
    ap.add_argument("--rate", default="-5%"); ap.add_argument("--avatar", default="", help="JSON do bloco avatar (HeyGen ou simulado): apresentador fala a notícia")
    a = ap.parse_args()
    custo = 0.0
    titulo, texto, fonte = ler_noticia(a.url)
    if len(texto) < 300:
        sys.exit("não consegui ler o texto da matéria (site bloqueou ou é só vídeo)")
    print(f"matéria: {titulo} ({fonte}, {len(texto)} caracteres)")
    r, c = roteiro(titulo, texto, fonte, a.publico); custo += c
    cenas = r["cenas"]
    print(f"roteiro: {len(cenas)} cenas")
    if not a.data:
        meses = "janeiro fevereiro março abril maio junho julho agosto setembro outubro novembro dezembro".split()
        import datetime
        d = datetime.date.today(); a.data = f"{d.day} de {meses[d.month - 1]} de {d.year}"
    if a.visual == "video" and not a.avatar:                # vídeo de verdade, narração mais calma
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import banco_videos
        segs = [{"tipo": "gancho", "fala": cenas[0]["fala"], "tela": r["manchete_curta"], "busca": cenas[0].get("busca", "")}]
        segs += [{"tipo": "cena", "fala": c["fala"], "tela": c["palavra"], "busca": c.get("busca", "")} for c in cenas[1:]]
        fim = (r.get("fechamento") or f"Segue {a.perfil}")
        segs.append({"tipo": "fim", "fala": fim, "tela": fim, "busca": cenas[0].get("busca", "")})
        cfgv = {"voz": a.voz, "rate": a.rate}
        css = CSS_AVATAR + f".fonte2{{position:absolute;right:40px;top:120px;font-family:'Montserrat',sans-serif;font-size:28px;color:#fff;background:rgba(0,0,0,.55);padding:6px 14px;border-radius:10px}}"
        dur, cred = banco_videos.montar(segs, cfgv, a.saida, renderizar, css, f"{a.perfil}  ·  Fonte: {fonte}", "#ffd23f")
        open(os.path.splitext(a.saida)[0] + ".txt", "w").write(
            f"{r['manchete_curta']}\n\n" + " ".join(c['fala'] for c in cenas) + f"\n\nFonte: {fonte} — {a.url}\n"
            + (("Vídeos: " + "; ".join(cred) + "\n") if cred else ""))
        print(f"pronto: {a.saida} ({dur:.1f}s, vídeo real) · custo IA ≈ US$ {custo:.3f}")
        return
    if a.avatar:                                            # modo apresentador (ex.: @omundocast)
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import avatar_heygen
        tmp = tempfile.mkdtemp(prefix="nv-")
        imgs = []
        for i, ce in enumerate(cenas[:4]):
            d = os.path.join(tmp, f"i{i}.png"); ci, ok = imagem(ce["imagem"], d); custo += ci
            if ok:
                imgs.append(d)
        v = {"gancho_tela": r["manchete_curta"], "gancho_fala": cenas[0]["fala"],
             "cenas": [{"fala": c["fala"], "tela": c["palavra"]} for c in cenas[1:]],
             "fechamento": (r.get("fechamento") or f"Segue {a.perfil}") + f" Fonte: {fonte}."}
        cfg = {"avatar": json.loads(a.avatar), "voz": a.voz, "perfil": a.perfil}
        dur = avatar_heygen.montar(v, cfg, imgs, a.saida, renderizar, duracao, CSS_AVATAR, a.perfil, "#ffd23f")
        open(os.path.splitext(a.saida)[0] + ".txt", "w").write(
            f"{r['manchete_curta']}\n\n" + " ".join(c['fala'] for c in cenas) + f"\n\nFonte: {fonte} — {a.url}\n")
        shutil.rmtree(tmp, ignore_errors=True)
        print(f"pronto: {a.saida} ({dur:.1f}s, apresentador) · custo IA ≈ US$ {custo:.3f}")
        return
    tmp = tempfile.mkdtemp(prefix="nv-")
    paginas, audios = [], []
    for i, ce in enumerate(cenas):
        mp3 = os.path.join(tmp, f"a{i}.mp3")
        narrar(ce["fala"], a.voz, mp3)
        img = None
        if not a.sem_imagens:
            dest = os.path.join(tmp, f"i{i}.png")
            ci, ok = imagem(ce["imagem"], dest); custo += ci
            img = dest if ok else None
        dur = duracao(mp3) + 0.35
        arq = os.path.join(tmp, f"c{i}.html")
        open(arq, "w").write(cena_html(i, ce, img, a.perfil, fonte, r["manchete_curta"], a.data))
        paginas.append((arq, dur)); audios.append((mp3, dur))
        print(f"  cena {i + 1}: {dur:.1f}s — {ce['palavra']}")
    fim_txt = r.get("fechamento") or f"Segue {a.perfil}"
    mp3 = os.path.join(tmp, "afim.mp3"); narrar(fim_txt, a.voz, mp3)
    dur = duracao(mp3) + 0.8
    arq = os.path.join(tmp, "fim.html"); open(arq, "w").write(fim_html(fim_txt, a.perfil, fonte))
    paginas.append((arq, dur)); audios.append((mp3, dur))
    quadros = os.path.join(tmp, "q"); os.makedirs(quadros)
    n = renderizar(paginas, a.fps, quadros)
    lista = os.path.join(tmp, "audio.txt")
    with open(lista, "w") as f:
        for m, d in audios:
            pad = m.replace(".mp3", "_p.wav")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", m, "-af", f"apad=whole_dur={d}", "-ar", "44100",
                            "-ac", "2", pad], check=True)
            f.write(f"file '{pad}'\n")
    faixa = os.path.join(tmp, "narr.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista, faixa], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(a.fps), "-i", os.path.join(quadros, "q%05d.jpg"),
                    "-i", faixa, "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", a.saida], check=True)
    legenda = os.path.splitext(a.saida)[0] + ".txt"
    open(legenda, "w").write(f"{r['manchete_curta']}\n\n" + " ".join(c['fala'] for c in cenas) +
                             f"\n\nFonte: {fonte} — {a.url}\n{fim_txt}\n")
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"pronto: {a.saida} ({n} quadros, {n / a.fps:.1f}s) · legenda em {legenda} · custo IA ≈ US$ {custo:.3f}")


if __name__ == "__main__":
    main()
