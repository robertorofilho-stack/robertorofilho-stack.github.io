#!/usr/bin/env bash
# Prepara um Mac ou Linux para operar este repositório com Claude Code.
# Idempotente — rode quantas vezes quiser, da raiz do repo:
#
#     bash .claude/bootstrap.sh            # infraestrutura de agente
#     bash .claude/bootstrap.sh --radar    # + dependências do radar (Node 22, Chromium)
#
set -uo pipefail
cd "$(dirname "$0")/.."
ok()    { printf '  ✓ %s\n' "$*"; }
falta() { printf '  ✗ %s\n' "$*"; }
aviso() { printf '  ! %s\n' "$*"; }
PENDENCIAS=0

echo ""
echo "── PROJETO SUPREMO · bootstrap ──"
echo ""

# 1. git e branch
if ! command -v git >/dev/null; then falta "git não encontrado (macOS: xcode-select --install)"; exit 1; fi
BR=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "?")
ok "git · branch atual: $BR"
[ "$BR" = "main" ] && aviso "você está na main — a infraestrutura vive em claude/projeto-supremo-claude-code-epsu7w até o merge: git checkout claude/projeto-supremo-claude-code-epsu7w"

# 2. Claude Code
if command -v claude >/dev/null; then ok "claude CLI $(claude --version 2>/dev/null | head -1)"
else falta "claude CLI ausente → npm install -g @anthropic-ai/claude-code  (ou instalador nativo)"; PENDENCIAS=$((PENDENCIAS+1)); fi

# 3. jq — recomendado para os hooks (há fallback em node/python3, mas jq é o mais rápido)
if command -v jq >/dev/null; then ok "jq"
elif command -v brew >/dev/null; then
  aviso "jq ausente — instalando via Homebrew (usado pelos hooks do cérebro)"
  brew install jq >/dev/null 2>&1 && ok "jq instalado" || aviso "brew install jq falhou; hooks usarão node/python3"
elif command -v node >/dev/null || command -v python3 >/dev/null; then
  ok "jq ausente, mas node/python3 presente — hooks funcionam pelo fallback"
else
  falta "nem jq, nem node, nem python3 — hooks do cérebro ficarão mudos. macOS: brew install jq"; PENDENCIAS=$((PENDENCIAS+1))
fi

# 3b. Portão de soberania do motor (pre-commit): só o Claude Code edita arquivos do motor
git config core.hooksPath .claude/git-hooks && ok "portão do git ativo (soberania do motor)"

# 3c. Índice do Cérebro mestre (quando esta máquina o tem): memória sem ponteiro = involução
# O cofre real fica em ~/.claude/projects/-Users-<user>-Claude/memory — o verificador auto-detecta.
if command -v python3 >/dev/null && [ -n "$(python3 .claude/helpers/cerebro/verificar-indice.py --listar 2>/dev/null)" ]; then
  if python3 .claude/helpers/cerebro/verificar-indice.py --quieto; then
    ok "índice do Cérebro mestre íntegro: $(python3 .claude/helpers/cerebro/verificar-indice.py --listar | tr '\n' ' ')"
  else
    falta "índice do Cérebro mestre com memória órfã — veja acima; restaure a linha, nunca apague o arquivo"; PENDENCIAS=$((PENDENCIAS+1))
  fi
fi

# 3d. Conselho de outros motores (segunda opinião por API): precisa de chave fora do git
if command -v python3 >/dev/null; then
  if OUTC=$(python3 .claude/helpers/conselho/conselho.py --status 2>/dev/null); then ok "$OUTC"
  else aviso "conselho sem chave — OPENROUTER_API_KEY (uma chave, todos os motores) em ~/.config/cerebro/conselho.env; modelo em .claude/helpers/conselho/conselho.env.example"; fi
fi

# 4. Hooks executáveis (git preserva o bit, mas garante)
chmod +x .claude/hooks/*.sh 2>/dev/null && ok "hooks executáveis"

# 5. Teste real do hook do cérebro
if OUT=$(CLAUDE_PROJECT_DIR="$PWD" bash .claude/hooks/carregar-cerebro.sh 2>/dev/null) && [ "${#OUT}" -gt 200 ]; then
  ok "cérebro carrega (${#OUT} bytes de contexto)"
else
  falta "hook do cérebro não produziu saída — verifique jq/node/python3"; PENDENCIAS=$((PENDENCIAS+1))
fi

# 6. Node para o radar (opcional)
if [ "${1:-}" = "--radar" ]; then
  echo ""; echo "── radar ──"
  if command -v node >/dev/null; then
    MAJ=$(node -v | sed 's/v\([0-9]*\).*/\1/'); MIN=$(node -v | sed 's/v[0-9]*\.\([0-9]*\).*/\1/')
    if [ "$MAJ" -gt 22 ] || { [ "$MAJ" -eq 22 ] && [ "$MIN" -ge 6 ]; }; then
      ok "node $(node -v)"; (cd radar && bash setup.sh)
    else
      falta "node $(node -v) é antigo; o radar precisa de ≥ 22.6 → brew install node@22"; PENDENCIAS=$((PENDENCIAS+1))
    fi
  else
    falta "node ausente → brew install node@22"; PENDENCIAS=$((PENDENCIAS+1))
  fi
fi

echo ""
echo "── próximo ──"
echo "  claude                          # abre a sessão; o cérebro carrega sozinho"
echo "  Obsidian → Open folder as vault → $PWD/.claude/cerebro"
[ "${1:-}" != "--radar" ] && echo "  bash .claude/bootstrap.sh --radar   # quando quiser o radar rodando local"
echo ""
[ "$PENDENCIAS" -eq 0 ] && echo "Pronto: 0 pendências." || echo "$PENDENCIAS pendência(s) acima."
