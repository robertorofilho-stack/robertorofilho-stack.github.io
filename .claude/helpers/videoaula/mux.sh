#!/bin/bash
# Junta vídeo mudo + narração (atrasada pela abertura), normaliza para -14 LUFS e exporta MP4 final.
# Uso: bash mux.sh aulas/p1-aula1.sync.json saida/p1-aula1.video.mp4 saida/narracao/p1-aula1.mp3 saida/final/p1-aula1.mp4
set -euo pipefail
SYNC="$1"; VIDEO="$2"; AUDIO="$3"; OUT="$4"
ABERTURA_MS=$(python3 -c "import json,sys; print(int(round(json.load(open(sys.argv[1]))['abertura']*1000)))" "$SYNC")
mkdir -p "$(dirname "$OUT")"
ffmpeg -y -hide_banner -loglevel error -i "$VIDEO" -i "$AUDIO" \
  -filter_complex "[1:a]adelay=${ABERTURA_MS}|${ABERTURA_MS},apad,loudnorm=I=-14:TP=-1:LRA=11[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart "$OUT"
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")
LUFS=$(ffmpeg -hide_banner -i "$OUT" -af ebur128=peak=true -f null - 2>&1 | grep -E "I:\s+-?[0-9.]+ LUFS" | tail -1 | sed -E 's/.*I:\s+(-?[0-9.]+) LUFS.*/\1/')
echo "ok $OUT · ${DUR}s · ${LUFS} LUFS · $(du -h "$OUT" | cut -f1)"
