#!/usr/bin/env bash
# SOBERANIA DO MOTOR — arquivos do motor Claude Code só mudam pelo Claude Code.
#
# Manifesto de hashes: .claude/INTEGRIDADE.sha256 (SHA-256 de cada arquivo protegido).
#   bash _integridade.sh            → verifica: falha se algo protegido mudou, sumiu ou apareceu
#                                     sem o manifesto acompanhar
#   bash _integridade.sh --gravar   → regrava o manifesto (o pre-commit faz isso quando quem
#                                     commita é o Claude Code)
# Memória (.claude/cerebro/) NÃO entra no manifesto — muda toda sessão; é protegida no
# pre-commit por caminho e pela Lei da Monotonia.
set -uo pipefail
cd "$(dirname "$0")/../.."
MAN=.claude/INTEGRIDADE.sha256
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT

hash_cmd() { if command -v sha256sum >/dev/null 2>&1; then sha256sum; else shasum -a 256; fi; }

protegidos() {
  {
    for f in CLAUDE.md .mcp.json .claude/settings.json .claude/CAPACIDADES.txt \
             .claude/bootstrap.sh .claude/backup.sh .claude/KIT-RECUPERACAO.md .claude/MCP-ARSENAL.md; do
      [ -f "$f" ] && echo "$f"; done
    find .claude/hooks .claude/skills .claude/agents .claude/git-hooks -type f 2>/dev/null
    find .github/workflows -type f -name '*.yml' 2>/dev/null
    find radar -type f \( -name '*.ts' -o -name '*.tsx' -o -name '*.mjs' -o -name '*.json' -o -name '*.tpl' \
         -o -name '*.sh' -o -name '*.css' -o -name '*.md' \) \
         -not -path 'radar/node_modules/*' -not -path 'radar/saas-gerados/*' -not -path 'radar/dados/*' 2>/dev/null
  } | grep -v "^$MAN$" | sort -u
}

protegidos | while IFS= read -r f; do hash_cmd < "$f" | awk -v f="$f" '{print $1"  "f}'; done | sort -k2 > "$T/atual"

if [ "${1:-}" = "--gravar" ]; then
  { echo "# SOBERANIA DO MOTOR — hashes dos arquivos do motor Claude Code. Regravado só pelo Claude Code."
    cat "$T/atual"; } > "$MAN"
  echo "✓ manifesto de integridade: $(wc -l < "$T/atual" | tr -d ' ') arquivos protegidos"
  exit 0
fi

[ -f "$MAN" ] || { echo "✗ sem manifesto — rode: bash .claude/hooks/_integridade.sh --gravar"; exit 1; }
grep -v '^#' "$MAN" | sort -k2 > "$T/man"
MUDOU=$(join -j 2 -o 1.1,2.1,0 "$T/man" "$T/atual" 2>/dev/null | awk '$1!=$2{print $3}')
SUMIU=$(comm -23 <(awk '{print $2}' "$T/man") <(awk '{print $2}' "$T/atual"))
NOVO=$(comm -13 <(awk '{print $2}' "$T/man") <(awk '{print $2}' "$T/atual"))
if [ -n "$MUDOU$SUMIU$NOVO" ]; then
  echo "✗ SOBERANIA DO MOTOR VIOLADA — arquivo do motor alterado sem passar pelo Claude Code:"
  [ -n "$MUDOU" ] && echo "$MUDOU" | sed 's/^/  ~ modificado: /'
  [ -n "$SUMIU" ] && echo "$SUMIU" | sed 's/^/  - removido:   /'
  [ -n "$NOVO"  ] && echo "$NOVO"  | sed 's/^/  + criado:     /'
  echo "  Se foi o Claude Code: bash .claude/hooks/_integridade.sh --gravar e commite o manifesto junto."
  echo "  Se foi outro agente (Codex/ChatGPT) ou edição manual: reverter, e registrar no cérebro."
  exit 1
fi
echo "✓ integridade: $(wc -l < "$T/man" | tr -d ' ') arquivos do motor intactos"
