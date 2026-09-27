---
name: cacar-produto
description: Caça um infoproduto ou oferta para vender, com pesquisa profunda e evidência real de mercado. Use quando o pedido for "o que eu vendo", "acha um produto", "que nicho entrar", "oportunidade de mercado", ou validar uma ideia de produto. Entrega oportunidades pontuadas com prova de demanda, não opinião.
argument-hint: "[nicho ou 'aberto' para busca livre]"
effort: high
---

# Caçada de produto

**Alvo:** $ARGUMENTS
Se vazio ou "aberto": busca livre, sem restrição de nicho. Neste caso, comece pelo dinheiro — onde há mais anúncio rodando — e não pelo interesse.

## Regra de ouro

O operador **não precisa** de produto ligado à medicina. Qualquer nicho serve. O critério é dinheiro e escala, não afinidade.

Não busque ideias. Busque **evidência de compra**.

---

## Fase 1 — Fan-out (paralelo, obrigatório)

Dispare os subagentes **em paralelo, numa única mensagem**. Serial aqui é desperdício de tempo.

Use `cacador` para as frentes de mercado. Se o nicho for aberto, dispare 3 instâncias em nichos diferentes para comparar.

| Frente | Onde | O que extrair |
|---|---|---|
| Anúncios | Meta Ads Library, TikTok Creative Center | anunciantes ativos, tempo de veiculação, nº de criativos, ângulo, promessa |
| Marketplace | Hotmart, Kiwify, Braip, Monetizze, Gumroad, Udemy, KDP | preço, temperatura, nº de afiliados, avaliações |
| Dor bruta | Reddit, grupos, comentários TikTok/YT/Reels, reviews 1-3★ | **frases literais** das pessoas, com link |
| Demanda | Google Trends, autocomplete, "pessoas também perguntam" | tendência 12 e 24 meses |
| Contra-tese | busca ativa por "saturado", "não funciona mais", "golpe" | as objeções reais |

## Fase 1b — Refletir e buscar de novo (CMU 11-768 aula 10, deep research)

Antes de pontuar, escreva 3 linhas de **REFLECT**: *o que as buscas NÃO responderam? que resultado
parece prova mas mede outra coisa?* Um anúncio rodando prova tráfego, não margem; muitos afiliados provam
comissão, não conversão. Depois rode uma rodada nova de busca **só sobre essas lacunas**. A conclusão fica limitada
ao que foi testado: "promissor em X, não verificado em Y". Nada de "o nicho é ótimo".

## Fase 2 — Filtro

Pontue de 1 a 5 em cada eixo. Mostre a matriz completa, inclusive dos descartados.

Dor · Poder de compra · Prova de mercado · Facilidade de entrega · Escala · Defensabilidade · Risco

**Corte em 24/35.** Não apresente perdedor por educação.

## Fase 3 — Red team

Antes do auditor: o subagente `verificador-citacao` confere se cada número e link sustenta a afirmação (método FACT).
Afirmação sem suporte sai do relatório ou é reescrita no escopo da fonte.

Rode o subagente `auditor` na oportunidade #1. Se ela não sobreviver, promova a #2 e repita.

Uma oportunidade que não passou pelo auditor não vai para o relatório.

## Fase 4 — Relatório

Máximo **3 oportunidades**. Ranqueadas. Para cada uma, o formato completo do `cacador`:
público, dor literal, prova de mercado, ângulo de entrada, produto proposto, funil, projeção honesta, como isso morre, fontes datadas.

## Fase 5 — Fechamento obrigatório

Termine com **exatamente isto**:

```
## Recomendação

**Entrar em:** [uma. só uma.]
**Porque:** [3 linhas]
**Primeiro passo, hoje:** [ação concreta de ≤2 horas]
**Investimento até a primeira venda:** R$ X
**Matar se:** [critério objetivo — "sem venda após R$X em tráfego" ou "CPA acima de R$Y em 7 dias"]
```

Depois grave em `.claude/cerebro/03-ATIVOS.md` e commite.

---

## Proibido

- Entregar sem checar biblioteca de anúncios
- Número sem fonte
- "O nicho de X é grande" — ruído, não análise
- Oportunidade sem ângulo de entrada específico
- Mais de 3 opções (paralisa a decisão)

## Conselho de outros motores — obrigatório antes de entregar

Não perguntar, não esperar pedido: com a recomendação pronta, rodar `/conselho` (helper `.claude/helpers/conselho/conselho.py`) com a tese e os números. Exit 2 (sem chave) → `/adversarial` e a entrega diz "segunda opinião interna". Consenso, divergência e a objeção que sobrevive entram na entrega e em `05-DECISOES`.
