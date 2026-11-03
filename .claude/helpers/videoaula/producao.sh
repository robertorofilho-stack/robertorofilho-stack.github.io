#!/bin/bash
# Linha de produção de uma lista de aulas: sincroniza com a narração, renderiza, mixa e gera folha de conferência.
# Uso: bash producao.sh p1-aula1 p1-aula2 ...   (requer saida/narracao/<id>.mp3)
set -uo pipefail
cd "$(dirname "$0")"
mkdir -p saida/final saida/folhas saida/video
for id in "$@"; do
  ini=$(date +%s)
  if [ ! -s "saida/narracao/$id.mp3" ]; then echo "FALTA narração: $id"; continue; fi
  python3 sincronizar.py "aulas/$id.json" "saida/narracao/$id.mp3" > "aulas/$id.sync.json" 2> "saida/$id.sync.log" || { echo "FALHOU sync $id"; cat "saida/$id.sync.log"; continue; }
  node render.mjs "aulas/$id.sync.json" "saida/video/$id.mp4" 30 > "saida/$id.render.log" 2>&1 || { echo "FALHOU render $id"; tail -5 "saida/$id.render.log"; continue; }
  bash mux.sh "aulas/$id.sync.json" "saida/video/$id.mp4" "saida/narracao/$id.mp3" "saida/final/$id.mp4" || { echo "FALHOU mux $id"; continue; }
  node quadros.mjs "aulas/$id.sync.json" "saida/folhas/$id.jpg" 6 > /dev/null 2>&1
  echo "PRONTO $id em $(( $(date +%s) - ini ))s · $(cat "saida/$id.sync.log" | tr -d '\n')"
done
