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
for l in C.UTF-8 C.utf8 pt_BR.UTF-8 pt_BR.utf8 en_US.UTF-8 en_US.utf8; do
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

# Cérebro MESTRE (privado, cerebro-backup), se existir nesta máquina: busca nos
# arquivos de memória individuais e devolve só os NOMES (a substância fica lá;
# o índice MEMORY.md já é injetado pelos hooks do próprio Cérebro).
MESTRE=""
PROJ="${CLAUDE_PROJECT_DIR:-$(pwd)}"
# Na nuvem o mestre fica clonado AO LADO do projeto (../cerebro-backup); nos Macs, em ~/Claude/cerebro-backup.
for cand in "${CEREBRO_PRIVADO:-}" "$HOME/Claude/cerebro-backup" "$HOME/cerebro-backup" \
            "$(dirname "$PROJ")/cerebro-backup" "/home/user/cerebro-backup"; do
  [ -n "$cand" ] && [ -d "$cand/claude-config/memory" ] && { MESTRE="$cand/claude-config/memory"; break; }
done
MEMS=""
if [ -n "$MESTRE" ]; then
  while IFS= read -r kw; do
    [ -n "$kw" ] || continue
    R=$(grep -rliF -- "$kw" "$MESTRE"/*.md 2>/dev/null | grep -v '/MEMORY.md$' | head -4)
    [ -n "$R" ] && MEMS+="$R"$'\n'
  done <<< "$KWS"
  # Nome + linha `description:` — ela é o ESTADO atual ("RESOLVIDO dd/mm", "ATIVO"); o corpo é histórico.
  # Aprendizado #29: só o nome fez o agente repetir um bloqueio de 06/09 que o mestre já dava por resolvido em 07/09.
  MEMS=$(printf '%s' "$MEMS" | awk 'NF && !seen[$0]++' | head -10 | while IFS= read -r f; do
    d=$(sed -n 's/^description: *//p' "$f" 2>/dev/null | head -1 | tr -d '"' | cut -c1-150)
    printf '%s%s\n' "${f#"$MESTRE"/}" "${d:+ — $d}"
  done)
fi

# Pedido que cheira a chave, conta, assinatura ou compra: listar o que JÁ EXISTE no cofre do mestre
# (só NOMES de variáveis; valores nunca saem do cofre). Aprendizado #28: o que já existe não se pede.
CHAVES=""
if [ -n "$MESTRE" ] && printf '%s' "$PROMPT" | grep -qiE 'chave|api.?key|token|credencial|senha|login|conta|assinatura|cr.{1,2}dito|comprar|assinar|cadastr'; then
  CHAVES=$(cat "$MESTRE"/chaves-credenciais.md "$MESTRE"/cofre-env-vibe.md "$MESTRE"/llm-padrao-openrouter.md 2>/dev/null \
    | grep -oE '\b[A-Z][A-Z0-9]*(_[A-Z0-9]+)*_(API_KEY|TOKEN|SECRET|KEY|SECRET_KEY|CLIENT_ID|VOICE_ID)\b' | sort -u | tr '\n' ' ')
fi

# Pedido que cheira a pagar, recarregar ou comprar: ESTADO VIVO de crédito/conta segundo o mestre (description = estado).
# Aprendizado #29: memória antiga não prova falta de crédito — a prova é HTTP (`conselho.py --saldo`) ou a memória mais nova.
ESTADOS=""
if [ -n "$MESTRE" ] && printf '%s' "$PROMPT" | grep -qiE 'cr.{1,2}dito|saldo|recarg|pagar|pagamento|comprar|assinar|assinatura|billing|cobran'; then
  ESTADOS=$(grep -liE '^description:.*(cr.{1,2}dito|saldo|billing|recarg|assinatura|pagamento|cobran)' "$MESTRE"/*.md 2>/dev/null | head -8 \
    | while IFS= read -r f; do
        printf '%s — %s\n' "$(basename "$f")" "$(sed -n 's/^description: *//p' "$f" | head -1 | tr -d '"' | cut -c1-170)"
      done)
fi

[ -n "$ACHADOS$MEMS$CHAVES$ESTADOS" ] || { echo '{}'; exit 0; }

TXT="🧠 MEMÓRIA RELACIONADA — busca automática por: $(printf '%s' "$KWS" | tr '\n' ' ')"$'\n\n'
[ -n "$ACHADOS" ] && TXT+="Satélite (.claude/cerebro):"$'\n'"$ACHADOS"$'\n\n'
[ -n "$MEMS" ] && TXT+="CÉREBRO MESTRE (privado) — abrir antes de decidir:"$'\n'"$MEMS"$'\n\n'
[ -n "$CHAVES" ] && TXT+="🔑 CHAVES QUE JÁ EXISTEM no cofre do mestre (~/.config/vha-vibe-marketing/.env; nomes, valores só lá): $CHAVES"$'\n'"NÃO pedir ao operador para criar, assinar ou comprar o que já existe. Ler chaves-credenciais.md e cofre-env-vibe.md antes de responder."$'\n\n'
[ -n "$ESTADOS" ] && TXT+="💳 ESTADO VIVO de crédito/conta segundo o mestre (a description é o estado atual; o corpo do arquivo é histórico):"$'\n'"$ESTADOS"$'\n'"Antes de mandar pagar ou recarregar: python3 .claude/helpers/conselho/conselho.py --saldo (OpenRouter + sonda HTTP da chave Gemini). Só pedir dinheiro com HTTP 429 ou saldo real na mão."$'\n\n'
TXT+="Antes de construir: conferir .claude/cerebro/03-ATIVOS.md — não reconstruir o que existe. "
TXT+="Escolher skill/subagente do arsenal antes de improvisar. Ao terminar: gravar em 02-MEMORIA.md."

json_hook UserPromptSubmit additionalContext "$TXT"
