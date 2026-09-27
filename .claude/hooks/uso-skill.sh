#!/usr/bin/env bash
# PostToolUse(Skill) — REGISTRO DE USO DE SKILL + poda estilo TroVE (CMU 11-768 aula 4, "Memory and Skills").
#
# Skill que ninguém usa só ocupa contexto e confunde a escolha. Cada chamada da ferramenta Skill vira uma
# linha em ~/.cache/cerebro/uso-skills.jsonl (fora do repo). O relatório lista uso por skill e as candidatas
# a ARQUIVO pela regra do TroVE: usos < ½·log10(n total de usos). Nunca apaga — Lei da Monotonia.
#
#   uso-skill.sh              (hook) lê o JSON do PostToolUse no stdin e registra
#   uso-skill.sh --relatorio  imprime o uso e as candidatas a arquivo (roda no /manutencao)
set -uo pipefail
. "$(dirname "$0")/_json.sh"
LOG="${XDG_CACHE_HOME:-$HOME/.cache}/cerebro/uso-skills.jsonl"
ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"

if [ "${1:-}" = "--relatorio" ]; then
  [ -f "$LOG" ] || { echo "sem registro de uso ainda ($LOG)"; exit 0; }
  N=$(wc -l < "$LOG" | tr -d ' ')
  echo "Uso de skills — $N chamadas registradas em $LOG"
  sed -n 's/.*"skill":"\([^"]*\)".*/\1/p' "$LOG" | sort | uniq -c | sort -rn | sed 's/^/  /'
  LIMIAR=$(awk -v n="$N" 'BEGIN{ printf "%.2f", 0.5*log(n)/log(10) }')
  echo "Limiar TroVE (½·log10 n): $LIMIAR usos — candidatas a ARQUIVO (nunca apagar; revisar no /manutencao):"
  for d in "$ROOT"/.claude/skills/*/; do
    s=$(basename "$d")
    u=$(grep -c "\"skill\":\"$s\"" "$LOG" 2>/dev/null || true)
    awk -v u="${u:-0}" -v l="$LIMIAR" 'BEGIN{ exit !(u < l) }' && echo "  - $s ($u usos)"
  done
  exit 0
fi

ENTRADA=""
[ -t 0 ] || IFS= read -r -d '' -t 2 ENTRADA 2>/dev/null || true
SK=$(printf '%s' "$ENTRADA" | json_get_field tool_input.skill 2>/dev/null | tr -cd 'A-Za-z0-9_:.-')
if [ -n "$SK" ]; then
  mkdir -p "$(dirname "$LOG")" 2>/dev/null
  printf '{"ts":"%s","skill":"%s"}\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$SK" >> "$LOG" 2>/dev/null
fi
echo '{}'
exit 0
