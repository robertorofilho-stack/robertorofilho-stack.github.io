#!/usr/bin/env bash
# PreCompact — CHECKPOINT COM ÂNCORAS LITERAIS (CMU 11-768 aula 3, "Context Management").
#
# Resumo de resumo apaga restrição ("CUDA 12.4" vira "CUDA recente"). Antes de compactar, grava FORA do
# contexto o que não pode ser parafraseado: os últimos pedidos do operador (literais), a branch, o que está
# sem commit e os últimos commits. O carregar-cerebro.sh reinjeta isso quando a sessão volta da compactação.
# Guarda em ~/.cache (fora do repositório: os pedidos podem conter assunto privado).
#
# Portável: bash 3.2, python3 opcional (sem python o checkpoint sai só com o estado do git).
set -uo pipefail
. "$(dirname "$0")/_json.sh"

ENTRADA=""
[ -t 0 ] || IFS= read -r -d '' -t 2 ENTRADA 2>/dev/null || true
SID=$(printf '%s' "$ENTRADA" | json_get_field session_id 2>/dev/null | tr -cd 'A-Za-z0-9_-')
TR=$(printf '%s' "$ENTRADA" | json_get_field transcript_path 2>/dev/null)
DIR="${XDG_CACHE_HOME:-$HOME/.cache}/cerebro"
mkdir -p "$DIR" 2>/dev/null && chmod 700 "$DIR" 2>/dev/null
ARQ="$DIR/checkpoint-${SID:-sem-sessao}.md"
ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"

{
  echo "## ⚓ CHECKPOINT PRÉ-COMPACTAÇÃO — âncoras literais ($(date '+%Y-%m-%d %H:%M'))"
  echo "Isto NÃO é resumo: é texto exato gravado antes da compactação. Vale mais que o resumo em caso de conflito."
  echo
  if [ -n "$TR" ] && [ -f "$TR" ] && command -v python3 >/dev/null 2>&1; then
    echo "### Últimos pedidos do operador (literais)"
    python3 - "$TR" <<'PY' 2>/dev/null
import json, sys
pedidos = []
for linha in open(sys.argv[1], encoding="utf-8", errors="replace"):
    try:
        j = json.loads(linha)
    except ValueError:
        continue
    if j.get("type") != "user":
        continue
    c = (j.get("message") or {}).get("content")
    if isinstance(c, list):   # resultado de ferramenta vem como lista; pedido humano vem como texto
        c = " ".join(p.get("text", "") for p in c if isinstance(p, dict) and p.get("type") == "text")
    c = (c or "").strip()
    if c and not c.startswith(("<system-reminder", "[SYSTEM NOTIFICATION", "<task-notification", "<local-command")):
        pedidos.append(c)
for p in pedidos[-3:]:
    print("> " + p[:1500].replace("\n", "\n> ") + "\n")
PY
  fi
  if git -C "$ROOT" rev-parse --git-dir >/dev/null 2>&1; then
    echo "### Estado do repositório"
    echo "- branch: \`$(git -C "$ROOT" branch --show-current 2>/dev/null)\`"
    SUJO=$(git -C "$ROOT" status --porcelain 2>/dev/null | head -20)
    if [ -n "$SUJO" ]; then echo "- SEM COMMIT (trabalho em curso):"; printf '%s\n' "$SUJO" | sed 's/^/    /'; else echo "- árvore limpa"; fi
    echo "- últimos commits:"; git -C "$ROOT" log --oneline -5 2>/dev/null | sed 's/^/    /'
  fi
} > "$ARQ.tmp" 2>/dev/null && mv "$ARQ.tmp" "$ARQ" && chmod 600 "$ARQ" 2>/dev/null

echo '{}'
exit 0
