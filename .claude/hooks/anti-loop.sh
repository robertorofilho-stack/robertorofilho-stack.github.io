#!/usr/bin/env bash
# PostToolUse — ANTI-LOOP (CMU 11-768 aula 9, fala: o RL no fim do pós-treino é o que tirou os loops e repetições
# dos modelos; sem acesso a pesos, o laço tem de ser pego no próprio agente).
#
# Guarda a assinatura (ferramenta + entrada) das últimas 8 chamadas da sessão em ~/.cache/cerebro. Se a MESMA
# chamada aparece 3 vezes nas últimas 8, injeta um aviso: parar, mudar de estratégia, ou reportar o bloqueio.
# Em site real (Meta Ads, Hotmart), repetir ação dá banimento — aula 7: "you get banned".
set -uo pipefail
. "$(dirname "$0")/_json.sh"

ENTRADA=""
[ -t 0 ] || IFS= read -r -d '' -t 2 ENTRADA 2>/dev/null || true
[ -n "$ENTRADA" ] || { echo '{}'; exit 0; }
SID=$(printf '%s' "$ENTRADA" | json_get_field session_id 2>/dev/null | tr -cd 'A-Za-z0-9_-')
NOME=$(printf '%s' "$ENTRADA" | json_get_field tool_name 2>/dev/null)
ARG=$(printf '%s' "$ENTRADA" | json_get_field tool_input 2>/dev/null)
case "$NOME" in Read|Grep|Glob|TodoWrite|TaskUpdate|TaskList|TaskGet|"") echo '{}'; exit 0;; esac   # leitura repetida é normal

if command -v shasum >/dev/null 2>&1; then H=$(printf '%s|%s' "$NOME" "$ARG" | shasum | cut -c1-16)
else H=$(printf '%s|%s' "$NOME" "$ARG" | sha1sum | cut -c1-16); fi

DIR="${XDG_CACHE_HOME:-$HOME/.cache}/cerebro"; mkdir -p "$DIR" 2>/dev/null
LOG="$DIR/loop-${SID:-sem-sessao}.txt"
{ tail -n 7 "$LOG" 2>/dev/null; echo "$H"; } > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"
N=$(grep -c "^$H\$" "$LOG" 2>/dev/null || echo 0)

if [ "${N:-0}" -ge 3 ]; then
  json_hook PostToolUse additionalContext "⚠ ANTI-LOOP: a mesma chamada ($NOME) já rodou $N vezes nas últimas 8. Repetir não vai mudar o resultado. PARE e escolha: (1) mudar de estratégia de verdade (outra ferramenta, outro caminho, ler o erro inteiro), (2) buscar na memória um episódio parecido, (3) recomeçar num subagente LIMPO com um plano curto — erro no contexto gera mais erro (CMU 11-768 aula 6), ou (4) reportar o bloqueio ao operador com a saída real. Em site real (Meta Ads, Hotmart), ação de escrita repetida pode banir a conta — uma tentativa só."
  exit 0
fi
echo '{}'
exit 0
