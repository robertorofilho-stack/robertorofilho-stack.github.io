# Low fee credit card network that merchants didn't charg

Ferramenta que resolve: low fee credit card network that merchants didn't charge a fee for, so I could c

## Origem
Detectado pelo radar em 2026-09-10.
Score **45/100** · urgência **MEDIA**

### A dor, nas palavras de quem a sentiu
> >I wish there was a low fee credit card network that merchants didn't charge a fee for, so I could continue the simplicity of digital payments but opt out of this crazy Visa Infinite rewards accounting boondoggle. This is called "Regulate the max fees" like Europe did, where they still have functioning credit card netw

### Evidência
- https://news.ycombinator.com/item?id=49632952
- https://news.ycombinator.com/item?id=49632403

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
3. **QA** — `node --experimental-strip-types ../../qa.ts low-fee-credit-card-network-that-merchan`
4. **Deploy** — `npx vercel --prod`

## Preço
R$ 19.90 · US$ 3.83 — pagamento único, 3 usos grátis antes do paywall.
