#!/usr/bin/env bash
# LEI DA MONOTONIA — capacidade só entra, nunca sai.
#
# Compara o inventário vivo (skills, subagentes, hooks, workflows, sistemas)
# com o manifesto .claude/CAPACIDADES.txt.
#   bash _capacidades.sh            → FALHA se algo do manifesto sumiu (involução)
#   bash _capacidades.sh --gravar   → acrescenta ao manifesto o que é novo; nunca remove
set -uo pipefail
cd "$(dirname "$0")/../.."
MAN=.claude/CAPACIDADES.txt
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT

atual() {
  for d in .claude/skills/*/;   do [ -f "$d/SKILL.md" ] && echo "skill:$(basename "$d")"; done
  for f in .claude/agents/*.md; do echo "agente:$(basename "$f" .md)"; done
  for f in .claude/hooks/*.sh;  do case "$(basename "$f")" in _*) ;; *) echo "hook:$(basename "$f" .sh)";; esac; done
  for f in .github/workflows/*.yml; do echo "workflow:$(basename "$f" .yml)"; done
  for f in .claude/helpers/*/*.py; do [ -f "$f" ] && echo "helper:$(basename "$f" .py)"; done
  [ -f radar/radar-lucro.ts ] && echo "sistema:radar-lucro"
  [ -f radar/gerar-saas.ts ]  && echo "sistema:gerador-micro-saas"
  [ -f radar/qa.ts ]          && echo "sistema:qa-adversarial"
  [ -f radar/src/pagamento/pix.ts ] && echo "sistema:pix-brcode"
  for s in .claude/bootstrap.sh .claude/backup.sh .claude/KIT-RECUPERACAO.md .claude/cerebro/00-MAPA.md; do
    [ -f "$s" ] && echo "operacao:$(basename "$s")"
  done
}
atual | sort -u > "$T/atual"

if [ "${1:-}" = "--gravar" ]; then
  { [ -f "$MAN" ] && grep -v '^#' "$MAN"; cat "$T/atual"; } | sort -u > "$T/novo"
  { echo "# Manifesto de capacidades — Lei da Monotonia: só cresce. Atualize com: bash .claude/hooks/_capacidades.sh --gravar"
    cat "$T/novo"; } > "$MAN"
  echo "✓ manifesto: $(grep -vc '^#' "$MAN") capacidades registradas"
  exit 0
fi

[ -f "$MAN" ] || { echo "✗ sem manifesto — rode: bash .claude/hooks/_capacidades.sh --gravar"; exit 1; }
grep -v '^#' "$MAN" | sort -u > "$T/man"
SUMIU=$(comm -23 "$T/man" "$T/atual")
NOVO=$(comm -13 "$T/man" "$T/atual")
[ -n "$NOVO" ] && { echo "novas capacidades fora do manifesto (registre com --gravar):"; echo "$NOVO" | sed 's/^/  + /'; }
if [ -n "$SUMIU" ]; then
  echo "✗ INVOLUÇÃO DETECTADA — capacidades do manifesto que sumiram:"; echo "$SUMIU" | sed 's/^/  - /'
  echo "  Regra: substituir = adicionar o melhor e arquivar em .claude/arquivo/. Apagar é proibido."
  exit 1
fi
echo "✓ monotonia: $(wc -l < "$T/man" | tr -d ' ') capacidades presentes, nenhuma perdida"
