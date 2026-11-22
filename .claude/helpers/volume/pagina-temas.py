#!/usr/bin/env python3
"""Página de tema fixo (autoajuda, vovó, curiosidades…) → Reels curtos com GANCHO VISUAL ABSURDO no quadro 0.

Uso:
  python3 pagina-temas.py --config mentepoder1.json [--quantos 3] [--so-roteiro]

Método (Diretor de Ganchos, METODO-SUPREMO 15/11): quadro 0 com imagem impossível/surreal + impacto sonoro em 0,2 s;
camada 1 (0–1,5 s) ataque com ≤ 7 palavras na tela; camada 2 (1,5–3 s) torção; entrega até o fim; recompensa cumprida;
Reel de 11 a 25 s; famílias variam entre vídeos (Curiosidade · Contraste · Emoção · Desafio · Demonstração).

Config (exemplos em paginas/): perfil, persona, voz, tom ("pitch"/"rate" do edge-tts), temas (lista), estilo visual,
regras extras, pasta, publicar (igual à esteira-noticias). Estado em pasta/estado.json evita repetir tema/gancho.
Custo: ~US$ 0,01 roteiro + ~US$ 0,04 por imagem (3 imagens/vídeo ≈ US$ 0,13).
"""
import argparse, datetime, html, importlib.util, json, os, random, re, shutil, subprocess, sys, tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
_sp = importlib.util.spec_from_file_location("nv", os.path.join(AQUI, "noticia-em-video.py"))
nv = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(nv)

PEDIDO = """Você é o DIRETOR DE GANCHOS + roteirista de uma página de Instagram/TikTok.
Página: {perfil} — persona: {persona}. Tom: {tom_texto}.
Escreva {n} Reels DIFERENTES entre si, em português do Brasil, sobre estes temas (um tema por vídeo, escolha os mais
fortes e ainda não usados): {temas}
Já usados (NÃO repetir tema nem gancho): {usados}

MÉTODO OBRIGATÓRIO:
- Quadro 0 = IMAGEM ABSURDA/IMPOSSÍVEL, fotorrealista e cinematográfica, que faz o dedo parar (surpresa visual), ligada ao
  tema por metáfora. Ex.: "uma mulher segurando o próprio reflexo que saiu do espelho", "um homem com a cabeça aberta e
  um jardim florescendo dentro". Sem texto na imagem, sem pessoa famosa, sem sangue/gore, sem nudez. Para o gerador não recusar: evite rosto humano realista em close e evite corpo machucado; prefira
  silhueta de costas, mãos, objetos gigantes, natureza impossível, escala absurda (ex.: "uma xícara de chá do tamanho de
  um prédio no meio da cidade", "um relógio derretendo sobre uma cama", "uma porta aberta no meio do oceano").
- As 3 imagens do vídeo (gancho + 2 cenas) são DIFERENTES entre si.
- Texto na tela do gancho: no máximo 7 palavras, contraste forte. Fala do gancho: no máximo 12 palavras.
- Cada vídeo usa UMA família diferente: Curiosidade, Contraste, Emoção, Desafio, Demonstração.
- Corpo: 2 ou 3 falas de no máximo 16 palavras cada que ENTREGAM o que o gancho prometeu (sem enrolar, sem mistério esticado).
- Fechamento: ação concreta (salvar, mandar para alguém, comentar uma palavra). Total falado 15 a 25 segundos (no máximo 65 palavras somando tudo).
- {regras}
Devolva APENAS JSON: {{"videos":[{{"tema":"...","familia":"...","gancho_tela":"...","gancho_fala":"...",
"imagem_gancho":"prompt em inglês da imagem absurda","busca_gancho":"2 a 4 palavras em inglês para achar um VÍDEO real de
banco de imagens com movimento forte e surpreendente (ex.: 'lightning storm slow motion', 'wave crashing rocks')",
"cenas":[{{"fala":"...","tela":"até 6 palavras","imagem":"prompt em inglês, mesma estética","busca":"2 a 4 palavras em inglês
para achar um vídeo real de banco de imagens que mostre a cena (pessoas, natureza, cidade, objetos)"}}],"fechamento":"...","legenda":"legenda do post com 3 a 5 hashtags"}}]}}"""

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Anton&family=Montserrat:wght@800&family=Caveat:wght@700&display=swap');
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;overflow:hidden;background:#000}
.fundo{position:absolute;inset:-6%;background-size:cover;background-position:center;animation:zoom var(--dur) linear both}
.escuro{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.15) 0%,rgba(0,0,0,.05) 40%,rgba(0,0,0,.75) 100%)}
.flash{position:absolute;inset:0;background:#fff;animation:flash .35s ease-out both;pointer-events:none}
.treme{position:absolute;inset:0;animation:treme .45s .05s both}
.gancho{position:absolute;left:60px;right:60px;top:300px;text-align:center;font-family:'Anton',sans-serif;font-size:118px;
 line-height:1.02;color:#fff;text-transform:uppercase;text-shadow:0 6px 0 #000,0 0 40px rgba(0,0,0,.8);
 animation:bate .35s .15s cubic-bezier(.2,1.8,.4,1) both}
.gancho em{font-style:normal;color:var(--destaque)}
.tela{position:absolute;left:70px;right:70px;top:1180px;text-align:center;font-family:'Montserrat',sans-serif;font-size:84px;
 line-height:1.08;color:#fff;text-shadow:0 5px 0 #000,0 0 30px rgba(0,0,0,.9);animation:sobe .45s .1s ease-out both}
.leg{position:absolute;left:70px;right:70px;bottom:150px;text-align:center;font-family:'Montserrat',sans-serif;font-size:44px;
 line-height:1.25;color:#fff;background:rgba(0,0,0,.55);padding:20px 28px;border-radius:18px}
.perfil{position:absolute;left:0;right:0;top:70px;text-align:center;font-family:'Montserrat',sans-serif;font-size:36px;
 color:rgba(255,255,255,.9);text-shadow:0 2px 8px #000}
.fim{position:absolute;left:70px;right:70px;top:700px;text-align:center;font-family:'Anton',sans-serif;font-size:96px;line-height:1.05;
 color:#fff;text-transform:uppercase;text-shadow:0 6px 0 #000;animation:bate .4s .1s cubic-bezier(.2,1.8,.4,1) both}
.fim small{display:block;font-family:'Montserrat',sans-serif;font-size:50px;margin-top:40px;color:var(--destaque);text-transform:none}
@keyframes zoom{from{transform:scale(1.18)}to{transform:scale(1)}}
@keyframes flash{from{opacity:1}to{opacity:0}}
@keyframes treme{0%{transform:translate(0,0)}20%{transform:translate(-18px,10px)}40%{transform:translate(16px,-12px)}
 60%{transform:translate(-10px,8px)}80%{transform:translate(6px,-4px)}100%{transform:translate(0,0)}}
@keyframes bate{from{transform:scale(2.6);opacity:0}to{transform:scale(1);opacity:1}}
@keyframes sobe{from{transform:translateY(60px);opacity:0}to{transform:none;opacity:1}}
"""


def pg(img, miolo, legenda, perfil, dur, destaque, flash=False):
    fundo = f"<div class='fundo' style=\"background-image:url('file://{img}');--dur:{dur}s\"></div>" if img else ""
    return (f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body style='--destaque:{destaque}'>"
            f"<div class='treme'>{fundo}</div><div class='escuro'></div>{'<div class=flash></div>' if flash else ''}"
            f"<div class='perfil'>{html.escape(perfil)}</div>{miolo}"
            f"{'<div class=leg>' + html.escape(legenda) + '</div>' if legenda else ''}</body></html>")


def destacar(t):
    """Última palavra do gancho na cor de destaque."""
    p = html.escape(t).split()
    return " ".join(p[:-1] + [f"<em>{p[-1]}</em>"]) if len(p) > 1 else html.escape(t)


def imagem_foto(prompt, destino, estilo):
    """Gera a imagem; se o filtro de segurança do modelo recusar, tenta de novo com versão simbólica, sem rosto humano."""
    import urllib.error
    tentativas = [prompt, "symbolic surreal still life, no human faces, no people, objects and nature only: " + prompt]
    r = None
    for t in tentativas:
        try:
            r = nv.openrouter({"model": "google/gemini-2.5-flash-image", "modalities": ["image", "text"],
                               "messages": [{"role": "user", "content": f"Vertical 9:16 photorealistic cinematic image, "
                                             f"{estilo}, dramatic lighting, high detail, no text, no letters, no "
                                             "watermark: " + t}]})
            if "choices" not in r:
                print(f"    imagem sem resposta: {str(r.get('error', r))[:160]}", file=sys.stderr); r = None; continue
            if r["choices"][0]["message"].get("images"):
                break
        except urllib.error.HTTPError as e:
            print(f"    imagem recusada ({e.code}), tentando versão simbólica", file=sys.stderr)
    if not r:
        return 0, False
    ims = r["choices"][0]["message"].get("images") or []
    if not ims:
        return 0, False
    import base64
    open(destino, "wb").write(base64.b64decode(ims[0]["image_url"]["url"].split(",", 1)[1]))
    return r.get("usage", {}).get("cost", 0) or 0, True


def narrar(texto, cfg, mp3):
    subprocess.run(["edge-tts", "--voice", cfg.get("voz", "pt-BR-AntonioNeural"), f"--rate={cfg.get('rate', '+0%')}",
                    f"--pitch={cfg.get('pitch', '+0Hz')}", "--text", texto, "--write-media", mp3],
                   check=True, capture_output=True)


def impacto(destino, dur=0.6):
    """Som de impacto sintético no 0,0–0,2 s (sem música de terceiros)."""
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                    f"aevalsrc='0.9*sin(2*PI*(55+400*exp(-12*t))*t)*exp(-5*t)':s=44100:d={dur}", "-ac", "2", destino],
                   check=True)


def fazer_video(v, cfg, saida):
    custo, tmp = 0.0, tempfile.mkdtemp(prefix="pt-")
    estilo, dest = cfg.get("estilo", "moody cinematic"), cfg.get("destaque", "#ffd23f")
    partes = [("gancho", v["gancho_fala"], v["imagem_gancho"], v["gancho_tela"])] + \
             [("cena", c["fala"], c["imagem"], c.get("tela", "")) for c in v["cenas"]]
    imgs = []
    for i, (_, _, prompt, _) in enumerate(partes[:3] if cfg.get("visual", "video") != "video" else []):  # noqa              # 3 imagens: gancho + 2 de apoio (economia)
        d = os.path.join(tmp, f"i{i}.png"); c, ok = imagem_foto(prompt, d, estilo); custo += c
        imgs.append(d if ok else None)
    if cfg.get("visual", "video") == "video":               # padrão (22/11): vídeo de verdade de banco gratuito
        import banco_videos
        segs = [{"tipo": "gancho", "fala": v["gancho_fala"], "tela": v["gancho_tela"], "busca": v.get("busca_gancho", "")}]
        segs += [{"tipo": "cena", "fala": c["fala"], "tela": c.get("tela", ""), "busca": c.get("busca", "")} for c in v["cenas"]]
        segs.append({"tipo": "fim", "fala": v["fechamento"], "tela": v["fechamento"], "busca": v.get("busca_gancho", "")})
        dur, cred = banco_videos.montar(segs, cfg, saida, nv.renderizar, CSS, cfg["perfil"], dest)
        txt = v.get("legenda", "") + (("\n\n" + cfg["aviso"]) if cfg.get("aviso") else "")
        if cred:
            txt += "\n\nVídeos: " + "; ".join(cred)
        open(saida[:-4] + ".txt", "w").write(txt + "\n")
        shutil.rmtree(tmp, ignore_errors=True)
        return dur, custo
    if cfg.get("avatar"):                                   # apresentador HeyGen falando, imagens como cortes
        import avatar_heygen
        boas = [x for x in imgs if x]
        if not boas:
            raise RuntimeError("nenhuma imagem gerada")
        dur = avatar_heygen.montar(v, cfg, boas, saida, nv.renderizar, nv.duracao, CSS, cfg["perfil"], dest)
        open(saida[:-4] + ".txt", "w").write(v.get("legenda", "") + (("\n\n" + cfg["aviso"]) if cfg.get("aviso") else "") + "\n")
        shutil.rmtree(tmp, ignore_errors=True)
        return dur, custo
    paginas, audios = [], []
    for i, (tipo, fala, _, tela) in enumerate(partes):
        mp3 = os.path.join(tmp, f"a{i}.mp3"); narrar(fala, cfg, mp3)
        dur = nv.duracao(mp3) + (0.45 if tipo == "gancho" else 0.25)
        boas = [x for x in imgs if x]
        if not boas:
            raise RuntimeError("nenhuma imagem gerada")
        img = imgs[i] if i < len(imgs) and imgs[i] else boas[i % len(boas)]
        miolo = (f"<div class='gancho'>{destacar(tela)}</div>" if tipo == "gancho"
                 else f"<div class='tela'>{html.escape(tela)}</div>")
        arq = os.path.join(tmp, f"c{i}.html")
        open(arq, "w").write(pg(img, miolo, fala if tipo != "gancho" else "", cfg["perfil"], round(dur, 2), dest,
                                flash=(tipo == "gancho")))
        paginas.append((arq, dur)); audios.append((mp3, dur))
    mp3 = os.path.join(tmp, "afim.mp3"); narrar(v["fechamento"], cfg, mp3)
    dur = nv.duracao(mp3) + 0.7
    arq = os.path.join(tmp, "fim.html")
    open(arq, "w").write(pg(next(x for x in imgs if x), f"<div class='fim'>{html.escape(v['fechamento'])}<small>{html.escape(cfg['perfil'])}"
                            "</small></div>", "", cfg["perfil"], round(dur, 2), dest))
    paginas.append((arq, dur)); audios.append((mp3, dur))
    quadros = os.path.join(tmp, "q"); os.makedirs(quadros)
    n = nv.renderizar(paginas, 30, quadros)
    lista = os.path.join(tmp, "audio.txt")
    with open(lista, "w") as f:
        for m, d in audios:
            w = m.replace(".mp3", "_p.wav")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", m, "-af", f"apad=whole_dur={d}", "-ar", "44100", "-ac", "2",
                            w], check=True)
            f.write(f"file '{w}'\n")
    voz = os.path.join(tmp, "voz.wav"); boom = os.path.join(tmp, "boom.wav"); impacto(boom)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista, voz], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "30", "-i", os.path.join(quadros, "q%05d.jpg"), "-i", voz,
                    "-i", boom, "-filter_complex", "[1:a]adelay=250|250[v];[v][2:a]amix=inputs=2:duration=first:normalize=0[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", saida], check=True)
    open(saida[:-4] + ".txt", "w").write(v.get("legenda", "") + (("\n\n" + cfg["aviso"]) if cfg.get("aviso") else "") + "\n")
    shutil.rmtree(tmp, ignore_errors=True)
    return n / 30, custo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True); ap.add_argument("--quantos", type=int, default=3)
    ap.add_argument("--so-roteiro", action="store_true")
    a = ap.parse_args()
    cfg = json.load(open(os.path.expanduser(a.config)))
    pasta = os.path.expanduser(cfg["pasta"]); os.makedirs(pasta, exist_ok=True)
    est_arq = os.path.join(pasta, "estado.json")
    estado = json.load(open(est_arq)) if os.path.exists(est_arq) else {"usados": []}
    temas = cfg["temas"][:]; random.shuffle(temas)
    r = nv.openrouter({"model": "google/gemini-2.5-pro", "response_format": {"type": "json_object"},
                       "messages": [{"role": "user", "content": PEDIDO.format(
                           perfil=cfg["perfil"], persona=cfg["persona"], tom_texto=cfg.get("tom_texto", ""),
                           n=a.quantos, temas="; ".join(temas), usados="; ".join(estado["usados"][-60:]) or "nenhum",
                           regras=cfg.get("regras", ""))}]}, timeout=300)
    bruto = re.sub(r"^```(json)?|```$", "", r["choices"][0]["message"]["content"].strip(), flags=re.M)
    videos = json.loads(bruto)["videos"][:a.quantos]
    custo = r.get("usage", {}).get("cost", 0) or 0
    hoje = datetime.date.today().isoformat()
    destino = os.path.join(pasta, "pendentes", hoje); os.makedirs(destino, exist_ok=True)
    json.dump(videos, open(os.path.join(destino, f"roteiros-{datetime.datetime.now():%H%M}.json"), "w"),
              ensure_ascii=False, indent=1)
    for i, v in enumerate(videos):
        print(f"• [{v.get('familia')}] {v['gancho_tela']} — {v['tema']}")
        if a.so_roteiro:
            continue
        nome = re.sub(r"[^a-z0-9]+", "-", v["gancho_tela"].lower())[:40].strip("-") or f"video-{i}"
        mp4 = os.path.join(destino, f"{datetime.datetime.now():%H%M}-{i + 1:02d}-{nome}.mp4")
        try:
            dur, c = fazer_video(v, cfg, mp4); custo += c
            estado["usados"].append(f"{v['tema']} | {v['gancho_tela']}")
            json.dump(estado, open(est_arq, "w"), ensure_ascii=False, indent=1)
            print(f"  pronto {dur:.1f}s → {mp4}")
        except Exception as e:
            print(f"  ERRO: {e}", file=sys.stderr)
    print(f"custo IA ≈ US$ {custo:.3f}")


if __name__ == "__main__":
    main()
