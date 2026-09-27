#!/usr/bin/env bash
# PreCompact — CHECKPOINT COM ÂNCORAS LITERAIS (CMU 11-768 aula 3, "Context Management").
#
# Resumo de resumo apaga restrição ("CUDA 12.4" vira "CUDA recente"). Na fala das aulas 1–3 o mesmo alerta
# apareceu três vezes: a compactação apagou o "não apague" (caso do e-mail apagado) e fez o OpenHands abrir
# "five pull requests for the same functionality". Por isso, antes de compactar, grava FORA do contexto:
#   - o PRIMEIRO pedido (objetivo original) e os 3 últimos, literais;
#   - toda PROIBIÇÃO dita pelo operador, literal;
#   - os EFEITOS EXTERNOS já feitos (push, PR, e-mail, anúncio, deploy…) — para não repetir;
#   - o estado do git e o caminho do histórico completo.
# O carregar-cerebro.sh reinjeta isso quando a sessão volta da compactação.
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
    python3 "$(dirname "$0")/_ancoras.py" "$TR" 2>/dev/null
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
