#!/usr/bin/env bash
# CÓPIA DE SEGURANÇA fora do GitHub — para o cenário "perdi tudo".
#
# O que salva:
#   1. o repositório inteiro, TODAS as branches e todo o histórico (git bundle)
#   2. a configuração pessoal do Claude Code (~/.claude e ~/.claude.json)
# O que NÃO salva, de propósito: .env e qualquer chave. Chave mora em gerenciador
# de senhas (1Password/Bitwarden/iCloud Keychain), nunca em backup em texto.
#
# Destino: pasta sincronizada (Google Drive / iCloud) se existir, senão ~/Backups.
#   bash .claude/backup.sh                 # destino automático
#   bash .claude/backup.sh /caminho/x      # destino explícito
#
# Restaurar em máquina nova:
#   git clone projeto-supremo-AAAAMMDD.bundle robertorofilho-stack.github.io
#   tar xzf claude-pessoal-AAAAMMDD.tgz -C ~
set -uo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
DATA=$(date +%Y%m%d-%H%M)

destino_auto() {
  for d in "$HOME"/Library/CloudStorage/GoogleDrive-*/"My Drive" \
           "$HOME/Google Drive/My Drive" "$HOME/Google Drive" \
           "$HOME/Library/Mobile Documents/com~apple~CloudDocs" \
           "$HOME/Dropbox" "$HOME/OneDrive"; do
    [ -d "$d" ] && { echo "$d/Backups-Claude"; return; }
  done
  echo "$HOME/Backups/Claude"
}
DEST="${1:-$(destino_auto)}"; mkdir -p "$DEST" || { echo "✗ não consegui criar $DEST"; exit 1; }
echo "── backup → $DEST ──"

# 1. Repositório: bundle com tudo (restaurável com git clone)
( cd "$REPO" && git bundle create "$DEST/projeto-supremo-$DATA.bundle" --all 2>/dev/null ) \
  && echo "  ✓ repo (todas as branches): projeto-supremo-$DATA.bundle" \
  || echo "  ✗ git bundle falhou"

# 2. Config pessoal do Claude Code (sem transcrições, sem cache — ficam gigantes)
if [ -d "$HOME/.claude" ] || [ -f "$HOME/.claude.json" ]; then
  tar czf "$DEST/claude-pessoal-$DATA.tgz" -C "$HOME" \
    --exclude='.claude/projects' --exclude='.claude/cache' --exclude='.claude/todos' \
    --exclude='.claude/statsig' --exclude='.claude/shell-snapshots' \
    $( [ -d "$HOME/.claude" ] && echo ".claude" ) $( [ -f "$HOME/.claude.json" ] && echo ".claude.json" ) 2>/dev/null \
    && echo "  ✓ config pessoal: claude-pessoal-$DATA.tgz" || echo "  ! config pessoal: nada ou erro (ok se nunca personalizou)"
fi

# 3. Manter só os 8 mais recentes de cada tipo
for pref in projeto-supremo claude-pessoal; do
  ls -1t "$DEST"/$pref-* 2>/dev/null | tail -n +9 | while read -r f; do rm -f "$f"; done
done

echo ""
echo "  Restaurar:  git clone \"$DEST/projeto-supremo-$DATA.bundle\" robertorofilho-stack.github.io"
echo "  Automático toda noite (macOS/Linux):  crontab -e  →"
echo "    0 21 * * * /bin/bash \"$REPO/.claude/backup.sh\" >> \"$HOME/backup-claude.log\" 2>&1"
echo "  Chaves (.env, tokens): gerenciador de senhas. Nunca aqui."
