# Tracking server-side (método FOP, reconstruído de fontes públicas)

Fonte do método: página pública de venda do MCT + docs oficiais da Meta (CAPI). O conteúdo pago do curso NÃO foi acessado.

Arquitetura: navegador (fbq + `client.js`) -> Worker (`capi.mjs`) -> Meta CAPI; Hotmart -> `/hotmart` -> Purchase.
Regras que a Meta cobra: `event_id` igual nos dois canais + mesmo `event_name` (janela 48h); PII com SHA-256 após normalizar;
IP, user agent, fbp e fbc SEM hash; `country` sempre; `external_id` consistente.

Testes: `node testar.mjs` (confere hashes contra os valores publicados pela Meta).
Deploy: `wrangler deploy` com secrets `META_PIXEL_ID`, `META_CAPI_TOKEN`, `HOTMART_HOTTOK`, `ALLOWED_ORIGIN` (nunca no git).
Validar: `META_TEST_CODE` + aba "Testar eventos" do Events Manager antes de ligar em produção.
Pendente: persistência em Supabase, dashboard, escolha dos 9 eventos por funil.
