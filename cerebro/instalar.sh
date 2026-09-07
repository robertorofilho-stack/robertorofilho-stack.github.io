#!/usr/bin/env bash
# instalar.sh — instala o Cerebro novo (Upload-Post + OpenRouter) no Mac mini.
# Nao apaga nada do que ja existe. Nao toca no .env a nao ser para acrescentar.
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$AQUI"

echo "=============================================="
echo " Cerebro — instalacao Upload-Post + OpenRouter"
echo "=============================================="
echo

# 1. Python
if ! command -v python3 >/dev/null 2>&1; then
  echo "ERRO: python3 nao encontrado. Instale com: brew install python3"
  exit 1
fi
echo "[1/5] Python: $(python3 --version)"

# 2. Dependencias
echo "[2/5] Instalando dependencias..."
python3 -m pip install --quiet --upgrade -r requirements.txt
echo "      requests instalado."

# 3. Pastas
echo "[3/5] Criando pastas..."
mkdir -p logs AGENDAMENTOS
touch logs/publicacao.log logs/custos.jsonl
echo "      logs/ e AGENDAMENTOS/ prontos."

# 4. .env
echo "[4/5] Verificando .env..."
ENV_ALVO=""
for c in "$AQUI/.env" "$AQUI/../.env"; do
  if [ -f "$c" ]; then ENV_ALVO="$c"; break; fi
done
if [ -z "$ENV_ALVO" ]; then
  cp .env.exemplo .env
  chmod 600 .env
  ENV_ALVO="$AQUI/.env"
  echo "      Criado $ENV_ALVO a partir do modelo."
else
  echo "      Usando o .env que ja existe: $ENV_ALVO (nada foi apagado)."
fi

faltando=()
for k in UPLOAD_POST_API_KEY OPENROUTER_API_KEY; do
  if ! grep -qE "^${k}=.+" "$ENV_ALVO" 2>/dev/null; then faltando+=("$k"); fi
done

# 5. Teste offline
echo "[5/5] Rodando a bateria offline (sem chaves, sem internet)..."
echo
python3 testar.py --offline || { echo; echo "ERRO: a bateria offline falhou. Nao siga adiante."; exit 1; }

echo
echo "=============================================="
if [ ${#faltando[@]} -gt 0 ]; then
  echo " FALTA COLAR AS CHAVES:"
  for k in "${faltando[@]}"; do echo "   - $k"; done
  echo
  echo " Upload-Post:  https://app.upload-post.com  -> Manage API Keys"
  echo "   python3 configurar_chaves.py --upload-post SUA_CHAVE"
  echo "   python3 configurar_chaves.py --upload-post-user NOME_DO_PERFIL"
  echo
  echo " OpenRouter:   https://openrouter.ai/settings/keys"
  echo "   python3 configurar_chaves.py --openrouter SUA_CHAVE"
else
  echo " Chaves presentes. Rode o teste real:"
  echo "   python3 testar.py --online"
fi
echo "=============================================="
