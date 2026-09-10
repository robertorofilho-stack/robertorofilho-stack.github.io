#!/usr/bin/env bash
# Stop — lembra de persistir a memória se houve trabalho e nada foi gravado.
#
# Portável: bash 3.2 (macOS), sem jq obrigatório (cadeia em _json.sh).
set -uo pipefail
. "$(dirname "$0")/_json.sh"

ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"
cd "$ROOT" 2>/dev/null || { echo '{}'; exit 0; }

MUDOU=$(git status --porcelain 2>/dev/null | grep -v '^.. .claude/cerebro/' | wc -l | tr -d ' ')
CEREBRO=$(git status --porcelain .claude/cerebro/ 2>/dev/null | wc -l | tr -d ' ')

if [ "${MUDOU:-0}" -gt 0 ] && [ "${CEREBRO:-0}" -eq 0 ]; then
  json_hook Stop additionalContext "LEMBRETE: houve trabalho nesta sessão mas .claude/cerebro/ não foi atualizado. Se esta sessão produziu decisão, número, aprendizado ou ativo, grave em .claude/cerebro/02-MEMORIA.md e commite antes de encerrar."
else
  echo '{}'
fi
exit 0
