#!/usr/bin/env bash
# UserPromptSubmit — RECALL AUTOMÁTICO.
#
# Extrai as palavras-chave do pedido, procura no cérebro o que já foi feito,
# decidido ou aprendido sobre elas, e injeta antes da execução. Determinístico:
# não depende de o agente "lembrar de procurar". Roda em cada prompt.
#
# Portável: bash 3.2, sem jq obrigatório (cadeia em _json.sh).
set -uo pipefail
. "$(dirname "$0")/_json.sh"

ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"; DIR="$ROOT/.claude/cerebro"
[ -d "$DIR" ] || { echo '{}'; exit 0; }

PROMPT=$(json_get_field prompt)
[ "${#PROMPT}" -ge 12 ] || { echo '{}'; exit 0; }       # "ok", "/brief" etc.: nada a lembrar
case "$PROMPT" in                                        # notificação de sistema não é pedido
  "[SYSTEM NOTIFICATION"*|*"<task-notification>"*|*"<wake "*|*"<webhook-payload>"*) echo '{}'; exit 0;;
esac

# Locale UTF-8 para [:alpha:] enxergar acento (em CI costuma ser POSIX)
for l in C.UTF-8 pt_BR.UTF-8 en_US.UTF-8; do
  if locale -a 2>/dev/null | grep -qix "$l"; then export LC_ALL="$l"; break; fi
done

STOP='porque|tambem|também|quando|sempre|mesmo|agora|depois|antes|sobre|entre|muito|muita|muitos|todos|todas|outro|outra|outros|coisa|coisas|fazer|preciso|quero|queria|gostaria|favor|please|should|would|could|about|there|their|which|where|these|those|thing|things|really|something|anything|everything|projeto|sistema|arquivo|codigo|código|claude|cerebro|cérebro|memoria|memória|ainda|apenas|entao|então|vamos|podem|precisa|precisamos|fazendo|criar|criando|novos|novas|dessa|desse|nesse|nessa|nossa|nosso|melhor|maior|forma|através|atraves|assim|aquilo|aquele|aquela|explique|explica|resposta|pergunta|entendeu|importante|possivel|possível|inclusive|exemplo|apenas'

KWS=$(printf '%s\n' "$PROMPT" | tr '[:upper:]' '[:lower:]' \
  | grep -oE '[[:alpha:]]{6,}' 2>/dev/null \
  | grep -vxE "$STOP" | awk '!seen[$0]++' | head -8)
[ -n "$KWS" ] || { echo '{}'; exit 0; }

ACHADOS=""
while IFS= read -r kw; do
  [ -n "$kw" ] || continue
  R=$(grep -rniF -m 3 -- "$kw" "$DIR"/*.md 2>/dev/null | head -3)
  [ -n "$R" ] && ACHADOS+="$R"$'\n'
done <<< "$KWS"

ACHADOS=$(printf '%s' "$ACHADOS" | awk 'NF && !seen[$0]++' | head -24 \
  | sed "s#^$DIR/##" | cut -c1-170)
[ -n "$ACHADOS" ] || { echo '{}'; exit 0; }

TXT="🧠 MEMÓRIA RELACIONADA — busca automática no cérebro por: $(printf '%s' "$KWS" | tr '\n' ' ')"$'\n\n'
TXT+="$ACHADOS"$'\n\n'
TXT+="Antes de construir: conferir .claude/cerebro/03-ATIVOS.md — não reconstruir o que existe. "
TXT+="Escolher skill/subagente do arsenal antes de improvisar. Ao terminar: gravar em 02-MEMORIA.md."

json_hook UserPromptSubmit additionalContext "$TXT"
