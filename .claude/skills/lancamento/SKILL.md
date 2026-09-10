---
name: lancamento
description: Pipeline completo de lançamento de infoproduto, do zero à venda — pesquisa, oferta, copy, página, funil, criativos, anúncios e tracking. Use quando o pedido for "lança um produto", "cria o funil completo", "monta tudo" ou "quero vender X". Orquestra todos os subagentes.
argument-hint: "[produto/nicho, ou 'aberto' para caçar]"
effort: high
---

# Pipeline de lançamento

**Alvo:** $ARGUMENTS

Esta skill vai do nada até material pronto para publicar. **Não pare no meio para pedir aprovação de etapa.** Execute as 7 fases, verifique, entregue. Perguntas ficam para o fim.

---

## Fase 0 — Contexto
Ler `.claude/cerebro/00-MAPA.md` e `03-ATIVOS.md`. Não recomeçar o que já existe.

## Fase 1 — Pesquisa (paralelo)
Se o alvo for "aberto" ou não validado → rode `/cacar-produto` inteiro.
Se já houver produto definido → `cacador` só para mapear concorrência, anúncios ativos e a linguagem real da dor.

**Saída:** avatar preciso, 10 frases literais de dor com link, 3 concorrentes com oferta e preço, ângulo de entrada.

## Fase 2 — Oferta
Rode `/oferta`. Promessa, mecanismo único com nome, stack de valor, 3 faixas de preço, garantia, urgência real, escada de produtos.

**Portão:** rode `auditor`. Se a oferta não sobreviver, corrija antes de escrever uma linha de copy. Copy boa em oferta ruim é dinheiro queimado.

## Fase 3 — Copy (paralelo)
Dispare `copychief` para todas as peças ao mesmo tempo:

- VSL / carta de vendas (`/vsl`)
- Página de vendas — headline, bullets, prova, FAQ, CTA
- 5 e-mails de sequência (isca → aquecimento → oferta → objeção → última chamada)
- 10 anúncios (5 dor, 5 desejo)
- Página de captura + página de obrigado

## Fase 4 — Criativos (paralelo)
`viral` gera: 10 roteiros de vídeo curto (5 anúncio, 5 orgânico) + 30 ganchos (`/ganchos`) + 5 conceitos de estático com copy pronta.

## Fase 5 — Construção
`arquiteto` decide a stack (padrão: estático ou Next na Vercel + Supabase + gateway com Pix).
`funil` constrói: **páginas em HTML/CSS/JS reais**, checkout, order bump, upsell, tracking (Pixel Meta + CAPI server-side com deduplicação por `event_id`, GA4, TikTok Pixel), UTMs em tudo, automação de e-mail.

Não descreva o funil. **Construa os arquivos.**

## Fase 6 — QA (portão obrigatório)
Rode `qa`. Abrir no navegador de verdade. Testar:
fluxo completo até o pagamento · duplo clique no botão de compra · 390px · offline no meio · evento de conversão disparando · nenhuma chave no bundle do cliente.

**Reprovou? Corrija e rode de novo.** Não entregue com bloqueante aberto.

## Fase 7 — Plano de mídia
Estrutura de campanha, verba de teste, públicos, regra de corte, escala.
Regra padrão: matar criativo com CPA 2x acima do alvo após 3x o ticket em gasto.

---

## Entrega final

```
# Lançamento: [produto]

## Resumo executivo
Público · promessa · preço · CPA máximo · vendas para break-even

## Ativos prontos (com caminho de arquivo)
[ ] Página de captura      → caminho
[ ] Página de vendas       → caminho
[ ] VSL (roteiro)          → caminho
[ ] 5 e-mails              → caminho
[ ] 10 anúncios            → caminho
[ ] 10 roteiros de vídeo   → caminho
[ ] Tracking configurado   → caminho
[ ] Relatório de QA        → veredito

## Cronograma até a primeira venda
D+0 · D+1 · D+3 · D+7 — cada dia com a ação específica

## Números
Investimento até a 1ª venda: R$
CPA alvo: R$ · Ticket: R$ · Margem: %
Break-even: N vendas

## Matar se
[critério objetivo, com número e prazo]

## Riscos (do auditor)
## Decisões que preciso de você
[só aqui. só o que realmente exige o operador — pagamento, domínio, gravação.]
```

Grave em `.claude/cerebro/03-ATIVOS.md` e commite.

## Conselho de outros motores — obrigatório antes de entregar

Não perguntar, não esperar pedido: com a recomendação pronta, rodar `/conselho` (helper `.claude/helpers/conselho/conselho.py`) com a tese e os números. Exit 2 (sem chave) → `/adversarial` e a entrega diz "segunda opinião interna". Consenso, divergência e a objeção que sobrevive entram na entrega e em `05-DECISOES`.
