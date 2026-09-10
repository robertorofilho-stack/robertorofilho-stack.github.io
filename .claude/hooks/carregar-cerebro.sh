#!/usr/bin/env bash
# SessionStart — injeta o cérebro persistente no contexto da sessão.
# O contêiner é efêmero; o repositório é a memória.
#
# Portável: bash 3.2 (macOS), BSD ou GNU grep/head, sem jq obrigatório.
set -uo pipefail
. "$(dirname "$0")/_json.sh"

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
  # -E (ERE): a alternância '\|' do grep GNU não existe no BSD grep do macOS.
  CTX+="### Decisões em aberto"$'\n'"$(grep -A3 -iE 'aberto|pendente|\[ \]' "$DIR/05-DECISOES.md" 2>/dev/null | head -c 1200)"$'\n\n'
fi

CTX+="**Regra:** ao fim de qualquer trabalho que produza decisão, número, aprendizado ou ativo — gravar em .claude/cerebro/02-MEMORIA.md e commitar. Sessão que não grava é sessão perdida."

json_hook SessionStart additionalContext "$CTX"
