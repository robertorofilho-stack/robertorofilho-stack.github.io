#!/usr/bin/env python3
"""assistir-video.py — Diretor de Aprendizado: assiste vídeo do YouTube NA NUVEM, sem baixar nada.

Por que existe: o YouTube bloqueia IP de datacenter (yt-dlp, Jina, Invidious — ver transcrever-youtube.sh),
mas o Gemini lê a URL do YouTube pelo lado do Google. Via OpenRouter (proxy injeta a chave) funciona da nuvem.
Medido em 03/10/2026: 2/2 vídeos (19 e 25 min). Custo: Gemini 2.5 Pro ≈ US$ 1,15 por 25 min de vídeo
(~385k tokens de vídeo); Flash custa ~1/8. 502 transitório acontece: o script tenta de novo e cai para Flash.

Uso:
  assistir-video.py <url|id> [--modelo pro|flash] [--pergunta "texto"] [--saida arquivo.md]
Limite honesto: é a leitura do Gemini, não transcrição literal. Número citado no vídeo → conferir em outra fonte.
"""
import argparse, json, os, re, sys, time, urllib.request, urllib.error

MODELOS = {"pro": "google/gemini-2.5-pro", "flash": "google/gemini-2.5-flash"}
PERGUNTA = ("Assista o vídeo inteiro e devolva em português: (1) resumo fiel em 10-15 tópicos com os passos "
            "EXATOS ensinados (ferramentas, serviços, preços, configurações, números citados, com minutagem); "
            "(2) qual produto/oferta o autor vende, se houver; (3) afirmações exageradas ou duvidosas. "
            "Não invente: se não ouviu, diga que não ouviu.")

def vid_id(alvo):
    m = re.search(r"(?:v=|youtu\.be/|shorts/|embed/)([\w-]{11})", alvo)
    return m.group(1) if m else alvo

def titulo(vid):
    try:
        u = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={vid}&format=json"
        d = json.load(urllib.request.urlopen(u, timeout=20))
        return f"{d['title']} — {d['author_name']}"
    except Exception:
        return vid

def assistir(vid, modelo, pergunta):
    corpo = {"model": modelo, "messages": [{"role": "user", "content": [
        {"type": "text", "text": pergunta},
        {"type": "video_url", "video_url": {"url": f"https://www.youtube.com/watch?v={vid}"}}]}]}
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(corpo).encode(),
                                 headers={"Content-Type": "application/json",
                                          **({"Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"]}
                                             if os.environ.get("OPENROUTER_API_KEY") else {})})
    r = json.load(urllib.request.urlopen(req, timeout=590))
    return r["choices"][0]["message"]["content"], r.get("usage", {})

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("alvo"); ap.add_argument("--modelo", default="pro", choices=MODELOS)
    ap.add_argument("--pergunta", default=PERGUNTA); ap.add_argument("--saida")
    a = ap.parse_args()
    vid = vid_id(a.alvo)
    ordem = [a.modelo, a.modelo] + (["flash"] if a.modelo != "flash" else [])
    for i, m in enumerate(ordem):
        try:
            texto, uso = assistir(vid, MODELOS[m], a.pergunta)
            break
        except urllib.error.HTTPError as e:
            print(f"tentativa {i+1} ({m}): HTTP {e.code} {e.read()[:200]!r}", file=sys.stderr)
            time.sleep(4)
    else:
        sys.exit("falhou em todas as tentativas")
    saida = f"# {titulo(vid)}\n\n`{vid}` · modelo {MODELOS[m]} · custo US$ {uso.get('cost', '?')}\n\n{texto}\n"
    if a.saida:
        open(a.saida, "w").write(saida)
    print(saida)

if __name__ == "__main__":
    main()
