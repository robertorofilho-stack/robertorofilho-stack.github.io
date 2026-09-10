#!/usr/bin/env bash
# PreToolUse(Bash) — impede destruição acidental e vazamento de segredo
# em repositório PÚBLICO que serve www.drrobertorodrigues.com
set -uo pipefail

INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // ""')

bloquear() {
  jq -n --arg r "$1" '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: $r
    }
  }'
  exit 0
}

# --- Destruição irreversível ---
case "$CMD" in
  *"rm -rf /"*|*"rm -rf ~"*|*"rm -rf ."[[:space:]]*|*":(){:|:&};:"*)
    bloquear "BLOQUEADO: comando destrutivo de escopo amplo. Especifique o caminho exato." ;;
  *"git push --force"*|*"git push -f"*)
    case "$CMD" in
      *"--force-with-lease"*) ;;
      *) bloquear "BLOQUEADO: force push sem --force-with-lease reescreve histórico alheio. Use --force-with-lease." ;;
    esac ;;
  *"git reset --hard"*origin*|*"git clean -fdx"*)
    bloquear "BLOQUEADO: descarta trabalho não commitado. Confirme com o operador antes." ;;
esac

# --- Vazamento de segredo em commit (repo público) ---
case "$CMD" in
  *"git commit"*|*"git add"*)
    ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"
    ACHADO=$(grep -rIlE \
      '(sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|xoxb-[0-9A-Za-z-]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)' \
      "$ROOT" \
      --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=.claude \
      2>/dev/null | head -5)
    [ -n "$ACHADO" ] && bloquear "BLOQUEADO: possível credencial detectada em: $ACHADO — este repositório é PÚBLICO. Remova antes de commitar."
    ;;
esac

exit 0
