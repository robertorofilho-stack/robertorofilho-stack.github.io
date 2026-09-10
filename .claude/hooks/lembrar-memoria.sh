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

# Decisão estratégica nova registrada nesta sessão sem conselho de outros motores? (CLAUDE.md §3)
DEC_NOVA=$(git diff HEAD -- .claude/cerebro/05-DECISOES.md 2>/dev/null | grep -cE '^\+### ' || true)
DEC_CONS=$(git diff HEAD -- .claude/cerebro/05-DECISOES.md 2>/dev/null | grep -cE '^\+.*(Conselho \(|segunda opinião interna)' || true)
if [ "${DEC_NOVA:-0}" -gt 0 ] && [ "${DEC_CONS:-0}" -eq 0 ]; then
  json_hook Stop additionalContext "REGRA §3: decisão estratégica nova em 05-DECISOES sem conselho de outros motores. Antes de encerrar: /conselho com a recomendação (sem chave: /adversarial e anotar 'segunda opinião interna') e registrar consenso/divergência na decisão."
  exit 0
fi

if [ "${MUDOU:-0}" -gt 0 ] && [ "${CEREBRO:-0}" -eq 0 ]; then
  json_hook Stop additionalContext "LEMBRETE: houve trabalho nesta sessão mas .claude/cerebro/ não foi atualizado. Se esta sessão produziu decisão, número, aprendizado ou ativo, grave em .claude/cerebro/02-MEMORIA.md e commite antes de encerrar."
else
  echo '{}'
fi
exit 0
