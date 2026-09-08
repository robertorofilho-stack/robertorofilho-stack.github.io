#!/usr/bin/env bash
# Reconstrói o ambiente de Claude Code deste projeto em qualquer máquina.
#
#   bash scripts/instalar-cerebro.sh            # instala o núcleo
#   bash scripts/instalar-cerebro.sh --headroom # inclui o compressor de contexto
#
# O que é instalado e o que NÃO é está explicado em docs/cerebro/README.md.
set -euo pipefail

azul()  { printf '\033[1;34m%s\033[0m\n' "$*"; }
verde() { printf '\033[1;32m%s\033[0m\n' "$*"; }
alerta(){ printf '\033[1;33m%s\033[0m\n' "$*"; }

COM_HEADROOM=0
[[ "${1:-}" == "--headroom" ]] && COM_HEADROOM=1

azul "== Cérebro do projeto — instalação =="
echo

if ! command -v claude >/dev/null 2>&1; then
  alerta "Claude Code não encontrado no PATH."
  echo "Instale com:  npm install -g @anthropic-ai/claude-code"
  exit 1
fi
echo "Claude Code: $(claude --version)"
echo

# ---------------------------------------------------------------------------
# 1. claude-code-setup — plugin oficial da Anthropic.
#    Lê o projeto e recomenda hooks, skills, subagentes e MCPs que fazem sentido.
# ---------------------------------------------------------------------------
azul "[1/3] claude-code-setup (oficial Anthropic)"
claude plugin marketplace add anthropics/claude-plugins-official 2>/dev/null || true
claude plugin install claude-code-setup@claude-plugins-official || \
  alerta "  já instalado ou indisponível — seguindo"
echo

# ---------------------------------------------------------------------------
# 2. claude-mem — memória entre sessões.
#    ATENÇÃO: grava o que passa pelas sessões em banco local. Se você usar o
#    Claude para redigir laudo ou discutir caso clínico, esse conteúdo entra no
#    banco. Mantenha o trabalho clínico em outra pasta/perfil, fora deste projeto.
# ---------------------------------------------------------------------------
azul "[2/3] claude-mem (memória persistente entre sessões)"
claude plugin marketplace add thedotmack/claude-mem 2>/dev/null || true
claude plugin install claude-mem@thedotmack || \
  alerta "  já instalado ou indisponível — seguindo"
echo

# ---------------------------------------------------------------------------
# 3. task-observer — já versionado em .claude/skills/, carrega sozinho neste
#    projeto. Aqui apenas espelhamos para o nível de usuário, para valer em
#    todos os projetos.
# ---------------------------------------------------------------------------
azul "[3/3] task-observer (aprende seu estilo e melhora suas skills)"
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -d "$RAIZ/.claude/skills/task-observer" ]]; then
  mkdir -p "$HOME/.claude/skills"
  cp -r "$RAIZ/.claude/skills/task-observer" "$HOME/.claude/skills/"
  echo "  copiado para ~/.claude/skills/task-observer"
else
  alerta "  não encontrado em .claude/skills/ — pule ou refaça o clone"
fi
echo

# ---------------------------------------------------------------------------
# Opcional: Headroom — comprime tudo que chega ao modelo. Economiza token.
# Fica no caminho das requisições, por isso é opt-in explícito.
# ---------------------------------------------------------------------------
if [[ $COM_HEADROOM -eq 1 ]]; then
  azul "[extra] headroom (compressão de contexto)"
  if command -v pipx >/dev/null 2>&1; then
    pipx install headroom-ai || alerta "  falhou — instale manualmente"
  else
    python3 -m pip install --user headroom-ai || alerta "  falhou — instale manualmente"
  fi
  echo "  uso:  headroom wrap claude     (roda o Claude Code através do compressor)"
  echo "        headroom doctor          (confere se o proxy está de pé)"
  echo
fi

verde "Pronto."
echo
alerta "NÃO instalado de propósito: OmniRoute."
cat <<'NOTA'
  O OmniRoute roteia suas requisições por centenas de provedores de IA de
  terceiros para driblar o limite de uso. Para um médico isso é um risco real:
  qualquer conteúdo clínico digitado na sessão sairia para operadores
  desconhecidos, sem contrato, sem DPA e sem garantia de descarte — exposição
  direta sob a LGPD (art. 11, dado sensível de saúde).

  Se quiser usar, use em máquina e perfil separados, exclusivamente para
  trabalho não-clínico, nunca neste projeto:
      https://github.com/diegosouzapw/OmniRoute
NOTA
echo
echo "Reinicie o Claude Code para carregar os plugins."
