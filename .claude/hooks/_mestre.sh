#!/usr/bin/env bash
# Localiza o Cérebro mestre (cerebro-backup) e, NA NUVEM, atualiza o clone antes de qualquer busca.
# Aprendizado #30 (12/09/2026): o clone do mestre na nuvem é uma foto. Sem `git pull` antes do recall, a sessão web
# não viu que o Mac mini já tinha construído e publicado o app Cirurgias, e refez tudo. Clone de ontem = cegueira de silo.
# Só roda em Linux (nuvem/CI). Nos Macs quem sincroniza é o sincronizar.sh do próprio mestre — nunca puxar por baixo dele.
# Portável: bash 3.2, sem jq. Nunca falha o hook: se a rede não responder, segue com o que tem e avisa.

mestre_dir() {
  local proj="${CLAUDE_PROJECT_DIR:-$(pwd)}" cand
  for cand in "${CEREBRO_PRIVADO:-}" "$HOME/Claude/cerebro-backup" "$HOME/cerebro-backup" \
              "$(dirname "$proj")/cerebro-backup" "/home/user/cerebro-backup"; do
    [ -n "$cand" ] && [ -d "$cand/claude-config/memory" ] && { printf '%s' "$cand"; return 0; }
  done
  return 1
}

# atualizar_mestre_nuvem [intervalo_min]  → imprime uma linha de estado (para o contexto) e devolve 0 sempre.
# Com intervalo, só puxa se o último pull tiver mais de N minutos (recall roda a cada prompt; não bater no GitHub à toa).
atualizar_mestre_nuvem() {
  local intervalo="${1:-0}" dir stamp agora antes depois
  [ "$(uname -s 2>/dev/null)" = "Linux" ] || return 0
  dir="$(mestre_dir)" || return 0
  [ -d "$dir/.git" ] || return 0
  command -v git >/dev/null 2>&1 || return 0
  stamp="/tmp/cerebro-mestre-pull.stamp"
  if [ "$intervalo" -gt 0 ] && [ -f "$stamp" ]; then
    agora=$(date +%s); antes=$(stat -c %Y "$stamp" 2>/dev/null || echo 0)
    [ $((agora - antes)) -lt $((intervalo * 60)) ] && return 0
  fi
  antes=$(git -C "$dir" rev-parse --short HEAD 2>/dev/null)
  if timeout 25 git -C "$dir" pull -q --ff-only origin master >/dev/null 2>&1; then
    depois=$(git -C "$dir" rev-parse --short HEAD 2>/dev/null)
    touch "$stamp"
    if [ "$antes" != "$depois" ]; then
      printf '🔄 MESTRE ATUALIZADO (%s → %s): %s commit(s) novos dos Macs. Releia o índice antes de decidir.\n' \
        "$antes" "$depois" "$(git -C "$dir" rev-list --count "$antes..$depois" 2>/dev/null || echo '?')"
    fi
  else
    printf '⚠️ MESTRE NÃO ATUALIZADO (rede/ff-only): clone pode estar VELHO (%s). O que os Macs fizeram desde então é invisível aqui.\n' "$antes"
  fi
  return 0
}
