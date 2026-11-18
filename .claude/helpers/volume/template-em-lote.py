#!/usr/bin/env python3
"""Aplica um template PNG (feito no Canva, 1080x1920) a uma pasta inteira de vídeos — o "Sombra Viral" do Cérebro.

Uso:
  python3 template-em-lote.py --template molde.png --entrada pasta_videos --saida pasta_prontos \
      [--caixa X,Y,L,A] [--legenda "texto fixo"]

--caixa: retângulo onde o vídeo entra no molde (padrão 0,420,1080,1080 = faixa central).
O vídeo é encaixado sem distorcer (preenche a caixa e corta o excesso), o PNG vai POR CIMA
(deixe a janela transparente no Canva) e o áudio original é mantido.

REGRA (lei do Cérebro): só use em vídeo SEU, licenciado, gerado por IA ou com transformação real
(comentário/narração nova). Baixar vídeo de terceiros e repostar = direito autoral + Instagram corta o
alcance de conta agregadora (política de 30/04/2026).
"""
import argparse, os, subprocess, sys

ap = argparse.ArgumentParser()
ap.add_argument("--template", required=True); ap.add_argument("--entrada", required=True)
ap.add_argument("--saida", required=True); ap.add_argument("--caixa", default="0,420,1080,1080")
a = ap.parse_args()
x, y, w, h = map(int, a.caixa.split(","))
os.makedirs(a.saida, exist_ok=True)
videos = sorted(f for f in os.listdir(a.entrada) if f.lower().endswith((".mp4", ".mov", ".m4v", ".webm")))
if not videos:
    sys.exit("nenhum vídeo na pasta de entrada")
ok = 0
for i, f in enumerate(videos, 1):
    destino = os.path.join(a.saida, "pronto_" + os.path.splitext(f)[0] + ".mp4")
    filtro = (f"color=c=black:s=1080x1920[fundo];"
              f"[0:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1[v];"
              f"[fundo][v]overlay={x}:{y}:shortest=1[base];[base][1:v]overlay=0:0[out]")
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", os.path.join(a.entrada, f), "-i", a.template,
           "-filter_complex", filtro, "-map", "[out]", "-map", "0:a?", "-c:v", "libx264", "-preset", "veryfast",
           "-crf", "21", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", destino]
    r = subprocess.run(cmd)
    ok += r.returncode == 0
    print(f"[{i}/{len(videos)}] {'ok ' if r.returncode == 0 else 'ERRO'} {f}")
print(f"{ok}/{len(videos)} vídeos prontos em {a.saida}")
