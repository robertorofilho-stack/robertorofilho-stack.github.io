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

# Aprendizado #30: na nuvem, puxar o mestre ANTES de ler — clone de ontem esconde o que os Macs fizeram hoje.
. "$(dirname "$0")/_mestre.sh"
MESTRE_PULL="$(atualizar_mestre_nuvem 0)"
for cand in "${CEREBRO_PRIVADO:-}" "$HOME/Claude/cerebro-backup" "$HOME/cerebro-backup" \
            "$(dirname "${CLAUDE_PROJECT_DIR:-$(pwd)}")/cerebro-backup" "/home/user/cerebro-backup"; do
  if [ -n "$cand" ] && [ -d "$cand/.git" ]; then
    CTX+="### ⚠️ CÉREBRO MESTRE presente nesta máquina: $cand"$'\n'
    [ -n "$MESTRE_PULL" ] && CTX+="$MESTRE_PULL"$'\n'
    CTX+="Constituição, 4 Leis, MOTOR-EXECUCAO (gate G5) e diretores dele VENCEM este satélite (CLAUDE.md §0b). "
    CTX+="Índice: claude-config/memory/MEMORY.md · Missões por voz: alfred/MISSOES-PARA-O-CEREBRO.md"$'\n\n'
    # Índice do mestre: memória sem ponteiro é invisível (involução). Só fala se houver problema.
    ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"
    # Sem caminho fixo: o cofre real fica em ~/.claude/projects/-Users-<user>-Claude/memory (auto-detecção).
    if command -v python3 >/dev/null 2>&1; then
      PERDA=$(python3 "$ROOT/.claude/helpers/cerebro/verificar-indice.py" --quieto 2>/dev/null | head -12)
      [ -n "$PERDA" ] && CTX+="### 🔴 ÍNDICE DO MESTRE COM PERDA (verificar-indice.py)"$'\n'"$PERDA"$'\n'"Restaure a linha no MEMORY.md (git log -p). Nunca apague o arquivo."$'\n\n'
    fi
    break
  fi
done
CTX+="**Regra:** ao fim de qualquer trabalho que produza decisão, número, aprendizado ou ativo — gravar em .claude/cerebro/02-MEMORIA.md e commitar. Sessão que não grava é sessão perdida."

json_hook SessionStart additionalContext "$CTX"
