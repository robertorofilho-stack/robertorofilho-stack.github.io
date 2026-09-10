#!/usr/bin/env bash
# Prepara a máquina local para rodar o radar e gerar micro-SaaS.
# Idempotente: pode rodar quantas vezes quiser.
set -euo pipefail
cd "$(dirname "$0")"

echo "── radar-lucro: preparação do ambiente ──"

# Node ≥ 22.6 executa TypeScript direto — sem ts-node, sem build.
if ! command -v node >/dev/null; then
  echo "✗ Node.js não encontrado. Instale a LTS: https://nodejs.org"; exit 1
fi
MAJOR=$(node -v | sed 's/v\([0-9]*\).*/\1/')
if [ "$MAJOR" -lt 22 ]; then
  echo "✗ Node $(node -v) é antigo. Precisa de ≥ 22.6 para executar .ts nativamente."; exit 1
fi
echo "✓ Node $(node -v)"

# Dependências do radar (só Playwright — o resto é Node puro)
npm install --no-audit --no-fund --silent
echo "✓ dependências"

# Navegador para o QA. Pula se já houver Chromium apontado em PW_CHROMIUM.
if [ -z "${PW_CHROMIUM:-}" ] && ! npx playwright install --dry-run chromium >/dev/null 2>&1; then
  npx playwright install chromium
fi
echo "✓ Chromium"

# Vercel CLI para deploy (opcional — só se for publicar)
if ! command -v vercel >/dev/null; then
  npm install -g vercel --silent 2>/dev/null || echo "! vercel CLI não instalado (opcional): npm i -g vercel"
fi

# .env a partir do exemplo, sem sobrescrever o que já existe
if [ ! -f .env ]; then
  cp templates/env.example .env
  echo "✓ .env criado — preencha PIX_KEY, PAYPAL_* e VERCEL_TOKEN quando for publicar"
else
  echo "✓ .env já existe (mantido)"
fi

echo ""
echo "Pronto. Comandos:"
echo "  npm run radar          varredura única"
echo "  npm run radar:watch    loop local a cada hora"
echo "  npm run gerar -- --auto  monta o micro-SaaS da melhor oportunidade"
echo "  npm run qa             ataca o projeto gerado no navegador"
echo ""
echo "Para 24/7 sem máquina ligada: o workflow .github/workflows/radar.yml já roda de hora em hora."
