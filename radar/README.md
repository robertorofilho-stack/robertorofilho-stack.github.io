# radar-lucro

Detector de oportunidade de micro-SaaS + gerador de produto com paywall + QA adversarial.

```
sinal público ──► radar-lucro.ts ──► oportunidades.json ──► gerar-saas.ts ──► projeto Next.js
                  (5 fontes, paralelo)   (pontuado)           (Pix + PayPal)      │
                                                                                   ▼
                                                              qa.ts ◄── build ◄── npm install
                                                        (Chromium ataca)
                                                                │
                                                                ▼
                                                          vercel --prod
```

## Rodar

```bash
cd radar && ./setup.sh          # uma vez
npm run radar                   # varredura → dados/oportunidades.json
npm run gerar -- --auto         # monta o micro-SaaS da melhor oportunidade
npm run qa                      # ataca no navegador: XSS, paywall, Pix, 390px, console, bundle
```

24/7 sem máquina ligada: `.github/workflows/radar.yml` roda de hora em hora e abre issue quando surge oportunidade **ALTA**.

## Fontes — o que responde de verdade

| Fonte | Estado | Como |
|---|---|---|
| Google Trends | ✅ gratuito | RSS público de buscas em alta (BR + US). Sem % de variação nem categoria — o RSS não expõe; filtramos ruído por vocabulário. |
| Hacker News | ✅ gratuito | API Algolia, busca por frases de dor nos últimos 7 dias. Melhor fonte de dor técnica pagante. |
| Stack Exchange | ✅ gratuito | 300 req/dia sem chave. Pergunta sem resposta aceita e com muita visualização = lacuna. |
| Reddit | ⚠️ precisa OAuth | Bloqueia IP de datacenter. Crie app em reddit.com/prefs/apps e preencha `REDDIT_CLIENT_ID/SECRET`. |
| X (Twitter) | ❌ pago | Busca exige API Basic (~US$200/mês). Adaptador pronto; liga com `X_BEARER_TOKEN`. HN + SE cobrem o mesmo sinal de graça. |

**Por que HTTP e não Playwright para as fontes:** endpoint estruturado é 10x mais rápido e não quebra quando o DOM muda. Playwright fica onde é insubstituível — o QA que abre o produto gerado e tenta quebrá-lo.

## Pontuação

Cinco fatores, pesos: dor explícita 30% · viabilidade em 1 página 25% · velocidade 20% · volume 15% · recorrência entre fontes 10%.

**Trava de realidade:** tendência sem ninguém pedindo ferramenta fica travada em 30. "Lionel Messi" em alta não é demanda por SaaS — é notícia. Esse foi o primeiro bug que o sistema encontrou em si mesmo.

## Pagamento

- **Pix:** BR Code EMV gerado offline (`src/pagamento/pix.ts`), CRC16 validado contra vetor canônico. QR como data URI local — o payload nunca sai para terceiro. Cai direto na conta da chave.
- **PayPal:** ordem via API v2. Sandbox automático sem credencial.
- Sem `.env`, tudo roda em modo sandbox funcional. Preencher chaves = produção, sem mudar código.

## O que este sistema NÃO faz — por design

- Não abre conta em gateway (KYC é vinculado a CPF/CNPJ — identidade não se delega)
- Não valida mercado (só tráfego e dinheiro real fazem isso; código não)
- Não contorna captcha nem simula "IP residencial" (viola termos, derruba conta)
- Não escreve a lógica de negócio da ferramenta — monta todo o resto e marca onde ela entra

## Expectativa honesta

50 ferramentas/semana é irreal. 1-2/semana com qualidade é agressivo e sustentável. A maioria fará R$0 — isso é o modelo funcionando. Receita residual aparece por volta da 15ª-20ª tentativa. O ativo que compõe não é nenhuma ferramenta: é a velocidade, o domínio e a lista.
