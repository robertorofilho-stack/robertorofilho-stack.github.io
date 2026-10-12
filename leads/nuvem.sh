#!/usr/bin/env bash
# Sobe o scraper do Google Maps DENTRO de uma sessão do Claude Code na nuvem (contêiner efêmero com proxy próprio).
# No Mac não precisa disto: use `docker compose -f leads/docker-compose.yml up -d`.
#
# O que faz, e só o que falta: (1) liga o daemon do Docker se não estiver rodando; (2) sobe o contêiner com o proxy da
# sessão e o certificado dele (Chromium lê o proxy pelo ambiente; o campo `proxies` do job NÃO serve: exige usuário/senha);
# (3) espera a API responder. Idempotente: rodar duas vezes não cria nada em dobro.
#
#   bash leads/nuvem.sh            → sobe e espera
#   bash leads/nuvem.sh --parar    → derruba o contêiner (o daemon fica)
set -uo pipefail
IMAGEM="${IMAGEM:-gosom/google-maps-scraper:v1.18.1}"
NOME=gmaps
PORTA="${SCRAPER_PORT:-8080}"
CA=/root/.ccr/ca-bundle.crt

if [ "${1:-}" = "--parar" ]; then docker rm -f "$NOME" >/dev/null 2>&1 && echo "contêiner $NOME removido"; exit 0; fi

if ! docker info >/dev/null 2>&1; then
  echo "▶ ligando o daemon do Docker…"
  nohup dockerd --data-root=/var/lib/docker > /tmp/dockerd.log 2>&1 &
  for _ in $(seq 1 40); do docker info >/dev/null 2>&1 && break; sleep 1; done
  docker info >/dev/null 2>&1 || { echo "✗ dockerd não subiu — veja /tmp/dockerd.log"; exit 1; }
fi

if docker ps --format '{{.Names}}' | grep -qx "$NOME"; then
  echo "✓ contêiner $NOME já está de pé"
else
  docker rm -f "$NOME" >/dev/null 2>&1
  ARGS=(-d --name "$NOME" --network host)
  if [ -n "${HTTPS_PROXY:-}" ]; then
    ARGS+=(-e "HTTPS_PROXY=$HTTPS_PROXY" -e "https_proxy=$HTTPS_PROXY" -e "HTTP_PROXY=$HTTPS_PROXY" -e "http_proxy=$HTTPS_PROXY"
           -e "NO_PROXY=${NO_PROXY:-localhost,127.0.0.1}" -e "no_proxy=${NO_PROXY:-localhost,127.0.0.1}")
  fi
  if [ -f "$CA" ]; then
    ARGS+=(-e "SSL_CERT_FILE=$CA" -v "$CA:$CA:ro")
    [ -d /root/.pki ] && ARGS+=(-v /root/.pki:/root/.pki:ro)     # Chromium confia no certificado do proxy pelo NSS
  fi
  echo "▶ subindo $IMAGEM em 127.0.0.1:$PORTA…"
  docker run "${ARGS[@]}" "$IMAGEM" -web -data-folder /gmapsdata -addr "127.0.0.1:$PORTA" >/dev/null || exit 1
fi

for _ in $(seq 1 30); do curl -sf "http://127.0.0.1:$PORTA/api/v1/jobs" >/dev/null 2>&1 && break; sleep 1; done
if curl -sf "http://127.0.0.1:$PORTA/api/v1/jobs" >/dev/null 2>&1; then
  echo "✓ API de pé: http://127.0.0.1:$PORTA/api/v1/jobs → $(curl -s "http://127.0.0.1:$PORTA/api/v1/jobs" | cut -c1-60)"
  echo "  próximo: python3 leads/scrape.py \"<termo com cidade>\" --cidade \"Cidade, UF\" --profundidade 5 --redes"
else
  echo "✗ API não respondeu; logs:"; docker logs "$NOME" 2>&1 | tail -5; exit 1
fi
