#!/usr/bin/env python3
"""Vídeo de verdade em cada cena (sem foto passando): busca clipe gratuito e monta o Reel com narração e textos.

Fontes, nesta ordem: Pexels (PEXELS_API_KEY) → Pixabay (PIXABAY_API_KEY) → Mixkit (sem chave) → Wikimedia Commons (sem chave; só reserva).
Pexels e Pixabay: uso comercial gratuito, sem atribuição obrigatória. Wikimedia: licença livre por arquivo (CC) — a
legenda do post recebe o crédito automaticamente quando ele for usado.

montar(segmentos, cfg, saida, renderizar, css, perfil, destaque)
  segmentos = [{"tipo": "gancho"|"cena"|"fim", "fala": str, "tela": str, "busca": "2-4 English keywords"}]
  cfg: voz, rate, pitch (edge-tts), pausa (s entre trechos, padrão 0.45)
Devolve (duração, créditos) — créditos só quando a fonte exige.
"""
import html, json, os, random, re, shutil, subprocess, tempfile, urllib.parse, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (cerebro-volume)"}


def _get(url, headers=None, timeout=40):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={**UA, **(headers or {})}),
                                            timeout=timeout))


def _pexels(q, usados):
    k = os.environ.get("PEXELS_API_KEY")
    if not k:
        return None
    r = _get("https://api.pexels.com/videos/search?" + urllib.parse.urlencode(
        {"query": q, "orientation": "portrait", "per_page": 15, "size": "medium"}), {"Authorization": k})
    for v in r.get("videos", []):
        if v["id"] in usados or v.get("duration", 0) < 4:
            continue
        arqs = sorted([f for f in v["video_files"] if f.get("height", 0) >= 1280 and f.get("width", 0) < f.get("height", 0)],
                      key=lambda f: f["height"])
        if arqs:
            usados.add(v["id"]); return arqs[0]["link"], None
    return None


def _pixabay(q, usados):
    k = os.environ.get("PIXABAY_API_KEY")
    if not k:
        return None
    r = _get("https://pixabay.com/api/videos/?" + urllib.parse.urlencode({"key": k, "q": q, "per_page": 20, "safesearch": "true"}))
    for v in r.get("hits", []):
        if v["id"] in usados or v.get("duration", 0) < 4:
            continue
        for tam in ("large", "medium"):
            f = v["videos"].get(tam) or {}
            if f.get("url"):
                usados.add(v["id"]); return f["url"], None
    return None


def _mixkit(q, usados):
    """Mixkit (licença livre para uso comercial, sem chave): página de busca por palavra."""
    slug = re.sub(r"[^a-z0-9]+", "-", q.lower()).strip("-")
    h = urllib.request.urlopen(urllib.request.Request(f"https://mixkit.co/free-stock-video/{slug}/", headers=UA),
                               timeout=30).read().decode("utf-8", "ignore")
    ids = list(dict.fromkeys(re.findall(r"assets\.mixkit\.co/videos/(\d+)/", h)))
    random.shuffle(ids)
    for i in ids:
        if ("mk", i) in usados:
            continue
        for res in ("1080", "720"):
            url = f"https://assets.mixkit.co/videos/{i}/{i}-{res}.mp4"
            try:
                urllib.request.urlopen(urllib.request.Request(url, headers={**UA, "Range": "bytes=0-100"}), timeout=20)
                usados.add(("mk", i)); return url, None
            except Exception:
                continue
    return None


def _wikimedia(q, usados):
    r = _get("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
        "action": "query", "format": "json", "generator": "search", "gsrnamespace": 6, "gsrlimit": 15,
        "gsrsearch": f"{q} filetype:video", "prop": "imageinfo", "iiprop": "url|size|extmetadata"}))
    paginas = sorted((r.get("query") or {}).get("pages", {}).values(), key=lambda p: p.get("index", 99))
    for p in paginas:
        ii = (p.get("imageinfo") or [{}])[0]
        if p["pageid"] in usados or not ii.get("url") or ii.get("height", 0) < 360 or (ii.get("duration") or 9) < 3:
            continue
        meta = ii.get("extmetadata", {})
        autor = re.sub(r"<[^>]+>", "", (meta.get("Artist") or {}).get("value", "")).strip()[:60]
        lic = (meta.get("LicenseShortName") or {}).get("value", "")
        usados.add(p["pageid"])
        return ii["url"], f"{p['title'].replace('File:', '')} — {autor or 'Wikimedia Commons'} ({lic})"
    return None


def buscar(q, usados):
    """Tenta a busca completa e depois versões mais curtas, em cada fonte."""
    tentativas = [q] + ([" ".join(q.split()[:2])] if len(q.split()) > 2 else []) + [q.split()[0]]
    for fonte in (_pexels, _pixabay, _mixkit, _wikimedia):
        for t in tentativas:
            try:
                achado = fonte(t, usados)
            except Exception:
                achado = None
            if achado:
                return achado
    return None


def _dur(arq):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", arq],
                                capture_output=True, text=True).stdout.strip() or 0)


def _narrar(texto, cfg, mp3):
    subprocess.run(["edge-tts", "--voice", cfg.get("voz", "pt-BR-AntonioNeural"), f"--rate={cfg.get('rate', '-5%')}",
                    f"--pitch={cfg.get('pitch', '+0Hz')}", "--text", texto, "--write-media", mp3],
                   check=True, capture_output=True)


def _clipe(url, dur, destino, tmp, i, lento=False):
    bruto = os.path.join(tmp, f"b{i}")
    urllib.request.urlretrieve(url, bruto)
    total = _dur(bruto)
    ini = max(0.0, min(total - dur - 0.1, total * 0.2)) if total > dur + 0.5 else 0
    vel = "setpts=1.6*PTS," if lento else ""            # gancho em câmera lenta = impacto
    fonte_dur = dur / 1.6 if lento else dur
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ini:.2f}", "-stream_loop", "-1", "-i", bruto, "-t",
                    f"{fonte_dur:.2f}", "-an", "-vf",
                    f"{vel}scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,"
                    "eq=contrast=1.06:saturation=1.1", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                    "-pix_fmt", "yuv420p", "-t", f"{dur:.2f}", destino], check=True)


FONTE_POESIA = "@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@1,500;1,600&display=swap');"
CSS_TXT = """
.verso{position:absolute;left:80px;right:80px;top:50%;transform:translateY(-50%);text-align:center;
 font-family:'Cormorant Garamond',serif;font-style:italic;font-size:70px;line-height:1.3;color:#fffaf0;
 text-shadow:0 2px 18px rgba(0,0,0,.9);animation:surge 1.4s ease-out both}
.poema-tit{position:absolute;left:80px;right:80px;top:42%;text-align:center;font-family:'Cormorant Garamond',serif;
 font-style:italic;font-size:96px;line-height:1.1;color:#fff;text-shadow:0 2px 20px #000;animation:surge 1.6s ease-out both}
.poema-tit small{display:block;font-size:54px;margin-top:30px;color:#f3d9a4}
@keyframes surge{from{opacity:0;filter:blur(6px)}to{opacity:1;filter:none}}
.lg{position:absolute;left:70px;right:70px;bottom:170px;text-align:center;font-family:'Montserrat',sans-serif;font-size:48px;
 line-height:1.25;color:#fff;text-shadow:0 3px 0 #000,0 0 24px rgba(0,0,0,.95)}
.sombra{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.35) 0%,rgba(0,0,0,0) 30%,rgba(0,0,0,0) 55%,rgba(0,0,0,.6) 100%)}
html,body{background:transparent!important}
"""


def montar(segmentos, cfg, saida, renderizar, css, perfil, destaque):
    tmp = tempfile.mkdtemp(prefix="bv-")
    usados, creditos, pausa = set(), [], float(cfg.get("pausa", 0.45))
    paginas, faixas, clipes = [], [], []
    for i, s in enumerate(segmentos):
        mp3 = os.path.join(tmp, f"a{i}.mp3"); _narrar(s["fala"], cfg, mp3)
        dur = _dur(mp3) + s.get("pausa", pausa) + (0.5 if s["tipo"] == "gancho" else 0)
        achado = buscar(s.get("busca") or s["tela"], usados) or (buscar("city timelapse", usados) if i == 0 else None)
        clip = os.path.join(tmp, f"v{i}.mp4")
        if achado:
            _clipe(achado[0], dur, clip, tmp, i, lento=(s["tipo"] in ("gancho", "verso", "titulo")))
            if achado[1]:
                creditos.append(achado[1])
        elif clipes:
            shutil.copy(clipes[-1], clip)                      # repete o anterior se nada for achado
        else:
            raise RuntimeError("nenhum vídeo encontrado para o gancho")
        clipes.append(clip)
        # camada de texto transparente
        if s["tipo"] == "titulo":                               # poesia: título e autor
            corpo = (f"<div class='sombra' style='background:rgba(0,0,0,.45)'></div><div class='poema-tit'>"
                     f"{html.escape(s['tela'])}<small>{html.escape(s.get('autor', ''))}</small></div>")
        elif s["tipo"] == "verso":                              # poesia: estrofe na tela, sem legenda duplicada
            versos = "<br>".join(html.escape(x) for x in s["tela"].split("\n"))
            corpo = f"<div class='sombra' style='background:rgba(0,0,0,.38)'></div><div class='verso'>{versos}</div>"
        elif s["tipo"] == "gancho":
            corpo = ("<div class='flash'></div><div class='sombra'></div>"
                     f"<div class='gancho'>{html.escape(s['tela'])}</div>")
        elif s["tipo"] == "fim":
            corpo = (f"<div class='sombra'></div><div class='fim'>{html.escape(s['tela'])}"
                     f"<small>{html.escape(perfil)}</small></div>")
        else:
            corpo = (f"<div class='sombra'></div><div class='tela'>{html.escape(s['tela'])}</div>"
                     f"<div class='lg'>{html.escape(s['fala'])}</div>")
        arq = os.path.join(tmp, f"t{i}.html")
        open(arq, "w").write(f"<!doctype html><html><head><meta charset='utf-8'><style>{FONTE_POESIA}{css}{CSS_TXT}</style></head>"
                             f"<body style='--destaque:{destaque}'><div class='perfil'>{html.escape(perfil)}</div>"
                             f"{corpo}</body></html>")
        paginas.append((arq, dur)); faixas.append((mp3, dur))
    # trilha visual: clipes em sequência
    lista = os.path.join(tmp, "v.txt")
    open(lista, "w").write("".join(f"file '{c}'\n" for c in clipes))
    base = os.path.join(tmp, "base.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", base], check=True)
    # narração com pausas
    la = os.path.join(tmp, "a.txt")
    with open(la, "w") as f:
        for m, d in faixas:
            w = m[:-4] + ".wav"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", m, "-af", f"apad=whole_dur={d}", "-ar", "44100", "-ac", "2", w],
                           check=True)
            f.write(f"file '{w}'\n")
    voz = os.path.join(tmp, "voz.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", la, voz], check=True)
    boom = os.path.join(tmp, "boom.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                    "aevalsrc='0.9*sin(2*PI*(55+400*exp(-12*t))*t)*exp(-5*t)':s=44100:d=0.6", "-ac", "2", boom], check=True)
    quadros = os.path.join(tmp, "q"); os.makedirs(quadros)
    renderizar(paginas, 30, quadros, png=True)
    total = sum(d for _, d in faixas)
    if cfg.get("musica") == "suave":                        # trilha própria sintetizada (sem direito autoral)
        boom = os.path.join(tmp, "pad.wav")
        acorde = "+".join(f"0.05*sin(2*PI*{f}*t)" for f in (130.8, 196.0, 261.6, 329.6))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                        f"aevalsrc='({acorde})*(0.75+0.25*sin(2*PI*0.08*t))':s=44100:d={total + 1:.1f}",
                        "-af", f"lowpass=f=900,afade=t=in:d=2,afade=t=out:st={max(total - 2.5, 0):.1f}:d=2.5", "-ac", "2", boom],
                       check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", base, "-framerate", "30", "-i", os.path.join(quadros, "q%05d.png"),
                    "-i", voz, "-i", boom, "-filter_complex",
                    "[0:v][1:v]overlay=0:0[v];[2:a]adelay=300|300[n];[n][3:a]amix=inputs=2:duration=first:normalize=0[a]",
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "160k", "-t", f"{total:.2f}", "-movflags", "+faststart", saida], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    return total, creditos
