#!/usr/bin/env bash
# SessionStart — injeta o cérebro persistente no contexto da sessão.
# O contêiner é efêmero; o repositório é a memória.
set -uo pipefail

DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}/.claude/cerebro"
[ -d "$DIR" ] || { echo '{}'; exit 0; }

CTX="## CÉREBRO CARREGADO (.claude/cerebro/)"$'\n\n'

for f in 00-MAPA.md 01-PERFIL.md; do
  [ -f "$DIR/$f" ] && CTX+="### $f"$'\n'"$(head -c 3000 "$DIR/$f")"$'\n\n'
done

if [ -f "$DIR/02-MEMORIA.md" ]; then
  CTX+="### Memória recente (últimas entradas)"$'\n'"$(head -c 2500 "$DIR/02-MEMORIA.md")"$'\n\n'
fi

if [ -f "$DIR/05-DECISOES.md" ]; then
  CTX+="### Decisões em aberto"$'\n'"$(grep -A3 -i 'aberto\|pendente\|\[ \]' "$DIR/05-DECISOES.md" 2>/dev/null | head -c 1200)"$'\n\n'
fi

CTX+="**Regra:** ao fim de qualquer trabalho que produza decisão, número, aprendizado ou ativo — gravar em .claude/cerebro/02-MEMORIA.md e commitar. Sessão que não grava é sessão perdida."

jq -n --arg c "$CTX" '{
  hookSpecificOutput: {
    hookEventName: "SessionStart",
    additionalContext: $c
  }
}'
