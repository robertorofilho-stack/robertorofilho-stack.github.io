# Convert bank CSV export into a clean monthly spending s

Ferramenta que resolve: convert bank CSV export into a clean monthly spending summary

## Origem
Detectado pelo radar em 2026-09-10.
Score **78/100** · urgência **ALTA**

### A dor, nas palavras de quem a sentiu
> Every month I export the CSV from my bank and spend an hour in a spreadsheet just to see where the money went. Is there a tool that does this in one click?

### Evidência
- https://news.ycombinator.com/item?id=0

## Rodar

```bash
npm install
cp .env.example .env      # opcional: sem .env o paywall roda em sandbox
npm run dev
```

## Antes de publicar

1. **Implementar o núcleo** — o bloco marcado em `app/page.tsx`.
   Todo o resto (paywall, APIs, estilo, deploy) já está pronto.
2. **Preencher `.env`** — `PIX_KEY` para receber via Pix,
   `PAYPAL_CLIENT_ID`/`PAYPAL_SECRET` para receber em dólar.
   Sem eles o app funciona em sandbox e nada quebra.
3. **QA** — `node --experimental-strip-types ../../qa.ts convert-bank-csv-export-into-a-clean-mon`
4. **Deploy** — `npx vercel --prod`

## Preço
R$ 9.90 · US$ 1.90 — pagamento único, 3 usos grátis antes do paywall.
