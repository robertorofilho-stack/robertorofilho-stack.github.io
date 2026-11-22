#!/usr/bin/env python3
"""Avatar HeyGen falando o roteiro + gancho absurdo e cortes de imagem por cima (usado por pagina-temas e esteira).

Config da página (bloco "avatar"):
  {"via": "heygen", "nome": "Vovó", "look_id": "<opcional>", "voice_id": "<opcional>", "resolucao": "720p"}
- Sem look_id, procura pelo nome nos looks PRIVADOS da conta (GET /v3/avatars/looks?ownership=private).
- Sem voice_id, usa a voz padrão do look.
- Chave: HEYGEN_API_KEY no ambiente (cofre do servidor). Nunca em arquivo versionado.
- "via": "simulado" monta com a foto do avatar parada + voz edge-tts — serve para testar a montagem sem gastar crédito.
Custo HeyGen medido no Cérebro (02/10/2026): ≈ US$ 4,7/min com gêmeo digital 1080p; talking photo ≈ US$ 2,2/min.
Um Reel de 20 s fica perto de US$ 0,75–1,60.
"""
import html, json, os, subprocess, sys, tempfile, time, urllib.request

API = "https://api.heygen.com"


def _req(metodo, rota, corpo=None, timeout=60):
    h = {"X-Api-Key": os.environ["HEYGEN_API_KEY"], "Accept": "application/json"}
    dados = None
    if corpo is not None:
        h["Content-Type"] = "application/json"
        dados = json.dumps(corpo).encode()
    r = urllib.request.Request(API + rota, data=dados, headers=h, method=metodo)
    return json.load(urllib.request.urlopen(r, timeout=timeout))


def achar_look(nome):
    r = _req("GET", "/v3/avatars/looks?ownership=private&limit=100", timeout=120)
    itens = r.get("data", {}).get("looks") or r.get("data") or []
    alvo = nome.lower()
    for it in itens:
        if alvo in (it.get("name") or "").lower() or alvo in (it.get("group_name") or "").lower():
            return it.get("id") or it.get("look_id"), it.get("default_voice_id")
    raise RuntimeError(f"look '{nome}' não encontrado na conta HeyGen (confira o nome no app)")


def gerar_heygen(texto, cfg_av, saida, chave_idem):
    look, voz = cfg_av.get("look_id"), cfg_av.get("voice_id")
    if not look:
        look, voz_padrao = achar_look(cfg_av["nome"]); voz = voz or voz_padrao
    corpo = {"type": "avatar", "avatar_id": look, "script": texto, "aspect_ratio": "9:16",
             "resolution": cfg_av.get("resolucao", "720p")}
    if voz:
        corpo["voice_id"] = voz
    h = {"X-Api-Key": os.environ["HEYGEN_API_KEY"], "Content-Type": "application/json", "Idempotency-Key": chave_idem}
    r = json.load(urllib.request.urlopen(urllib.request.Request(API + "/v3/videos", data=json.dumps(corpo).encode(),
                                                                headers=h), timeout=60))
    vid = (r.get("data") or {}).get("video_id") or r.get("video_id")
    for _ in range(180):                                    # até 30 min
        time.sleep(10)
        st = _req("GET", f"/v3/videos/{vid}").get("data", {})
        if st.get("status") == "completed":
            urllib.request.urlretrieve(st.get("video_url") or st.get("url"), saida); return saida
        if st.get("status") in ("failed", "error"):
            raise RuntimeError(f"HeyGen falhou: {st}")
    raise RuntimeError("HeyGen demorou mais de 30 min")


def gerar_simulado(texto, cfg_av, saida, voz_edge):
    """Foto do avatar + voz edge-tts: mesma duração e formato, custo zero — para testar a montagem."""
    tmp = tempfile.mkdtemp(prefix="av-")
    mp3 = os.path.join(tmp, "v.mp3")
    subprocess.run(["edge-tts", "--voice", voz_edge, "--text", texto, "--write-media", mp3], check=True, capture_output=True)
    foto = cfg_av.get("foto_teste")
    entrada = ["-loop", "1", "-i", foto] if foto else ["-f", "lavfi", "-i", "color=c=0x334455:s=720x1280"]
    subprocess.run(["ffmpeg", "-v", "error", "-y", *entrada, "-i", mp3, "-vf",
                    "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,zoompan=z='1+0.0006*on':d=1:s=720x1280",
                    "-r", "30", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", saida], check=True)
    return saida


def montar(v, cfg, imgs, saida, renderizar, duracao, css, perfil, destaque):
    """Base = avatar falando tudo; por cima: gancho absurdo (0–1,6 s), corte de imagem no início de cada cena,
    texto de tela, e CTA no fim. Tempos de cada trecho proporcionais ao número de caracteres falados."""
    falas = [v["gancho_fala"]] + [c["fala"] for c in v["cenas"]] + [v["fechamento"]]
    texto = " ".join(falas)
    tmp = tempfile.mkdtemp(prefix="mt-")
    base = os.path.join(tmp, "avatar.mp4")
    av = cfg["avatar"]
    if av.get("via") == "heygen":
        gerar_heygen(texto, av, base, f"{perfil}-{abs(hash(texto)) % 10**12}")
    else:
        gerar_simulado(texto, av, base, cfg.get("voz", "pt-BR-AntonioNeural"))
    total = duracao(base)
    pesos = [len(f) for f in falas]; soma = sum(pesos)
    tempos = [total * p / soma for p in pesos]
    telas = [v["gancho_tela"]] + [c.get("tela", "") for c in v["cenas"]] + [v["fechamento"]]
    paginas = []
    def pagina(corpo):
        return (f"<!doctype html><html><head><meta charset='utf-8'><style>{css}</style><style>"
                "html,body{background:transparent!important}.chip{position:absolute;left:0;right:0;bottom:250px;"
                "text-align:center;font-family:'Montserrat',sans-serif;font-size:72px;color:#fff;line-height:1.08;padding:0 70px;"
                "text-shadow:0 5px 0 #000,0 0 30px rgba(0,0,0,.9);animation:sobe .4s .05s ease-out both}"
                "</style></head>"
                f"<body style='--destaque:{destaque}'><div class='perfil'>{html.escape(perfil)}</div>{corpo}</body></html>")
    for i, (dur, tela) in enumerate(zip(tempos, telas)):
        img = imgs[i % len(imgs)] if imgs else None
        if i == 0:      # gancho: imagem absurda tela cheia 1,6 s, depois o avatar com a frase no topo
            corte = min(1.6, dur * 0.7)
            a = os.path.join(tmp, "g1.html")
            open(a, "w").write(pagina(f"<div class='treme'><div class='fundo' style=\"background-image:url('file://{img}');"
                                      f"--dur:{corte}s\"></div></div><div class='escuro'></div><div class='flash'></div>"
                                      f"<div class='gancho'>{html.escape(tela)}</div>"))
            b = os.path.join(tmp, "g2.html")
            open(b, "w").write(pagina(f"<div class='gancho' style='top:180px;font-size:92px;animation:none'>"
                                      f"{html.escape(tela)}</div>"))
            paginas += [(a, corte), (b, dur - corte)]
        elif i == len(tempos) - 1:   # CTA
            a = os.path.join(tmp, "fim.html")
            open(a, "w").write(pagina(f"<div class='chip' style='font-family:Anton,sans-serif;font-size:84px;"
                                      f"text-transform:uppercase'>{html.escape(tela)}</div>"))
            paginas.append((a, dur))
        else:           # cena: corte de imagem 2,2 s, depois volta o avatar com o texto de tela
            corte = min(2.2, dur * 0.55)
            a = os.path.join(tmp, f"c{i}a.html")
            open(a, "w").write(pagina(f"<div class='fundo' style=\"background-image:url('file://{img}');--dur:{corte}s\">"
                                      f"</div><div class='escuro'></div><div class='tela'>{html.escape(tela)}</div>"))
            b = os.path.join(tmp, f"c{i}b.html")
            open(b, "w").write(pagina(f"<div class='chip'>{html.escape(tela)}</div>"))
            paginas += [(a, corte), (b, dur - corte)]
    quadros = os.path.join(tmp, "q"); os.makedirs(quadros)
    renderizar(paginas, 30, quadros, png=True)
    boom = os.path.join(tmp, "boom.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                    "aevalsrc='0.9*sin(2*PI*(55+400*exp(-12*t))*t)*exp(-5*t)':s=44100:d=0.6", "-ac", "2", boom], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", base, "-framerate", "30", "-i", os.path.join(quadros, "q%05d.png"),
                    "-i", boom, "-filter_complex",
                    "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[b];"
                    "[b][1:v]overlay=0:0:shortest=0[v];[0:a][2:a]amix=inputs=2:duration=first:normalize=0[a]",
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "160k", "-t", f"{total:.2f}", "-movflags", "+faststart", saida], check=True)
    return total
