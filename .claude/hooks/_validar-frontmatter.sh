#!/usr/bin/env bash
# Skills e subagentes só carregam com frontmatter válido. Arquivo sem '---' na
# linha 1 vira "documentação" em silêncio. Este teste torna o silêncio barulhento.
set -uo pipefail
cd "$(dirname "$0")/.."
F=0
for f in skills/*/SKILL.md; do
  [ "$(head -1 "$f")" = "---" ] && grep -q '^description:' "$f" && echo "  ✓ $f" || { echo "  ✗ $f"; F=$((F+1)); }
done
for f in agents/*.md; do
  [ "$(head -1 "$f")" = "---" ] && grep -q '^name:' "$f" && grep -q '^description:' "$f" && echo "  ✓ $f" || { echo "  ✗ $f"; F=$((F+1)); }
done
echo "FALHAS: $F"; exit $F
