#!/usr/bin/env bash
# Stop — lembra de persistir a memória se houve trabalho e nada foi gravado.
set -uo pipefail

ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"
cd "$ROOT" 2>/dev/null || { echo '{}'; exit 0; }

MUDOU=$(git status --porcelain 2>/dev/null | grep -v '^.. .claude/cerebro/' | wc -l | tr -d ' ')
CEREBRO=$(git status --porcelain .claude/cerebro/ 2>/dev/null | wc -l | tr -d ' ')

if [ "$MUDOU" -gt 0 ] && [ "$CEREBRO" -eq 0 ]; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "Stop",
      additionalContext: "LEMBRETE: houve trabalho nesta sessão mas .claude/cerebro/ não foi atualizado. Se esta sessão produziu decisão, número, aprendizado ou ativo, grave em .claude/cerebro/02-MEMORIA.md e commite antes de encerrar."
    }
  }'
else
  echo '{}'
fi
exit 0
