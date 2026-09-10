---
name: auditar
description: Red team adversarial em qualquer plano, copy, oferta, código, decisão ou investimento. Use antes de publicar, lançar, gastar ou executar. Existe para destruir a ideia enquanto ainda é barato destruí-la.
argument-hint: "[o que auditar]"
effort: high
---

# Auditoria adversarial

**Alvo:** $ARGUMENTS

Delegue ao subagente `auditor`. Se o alvo tiver código ou interface, rode também `qa`.

## Postura

Assuma que **isso vai falhar**. Descubra como, antes que o mercado descubra.

Não abra com "no geral está bom". Vá direto ao ponto de quebra.

## Vetores

1. **Premissa** — qual afirmação, se falsa, derruba tudo? Foi verificada ou assumida?
2. **Número** — de onde veio? Medido, estimado ou inventado? Refaça a conta.
3. **Mercado** — quem já faz? Por que escolheriam você? O que impede o clone em 30 dias?
4. **Execução** — prazo realista, não otimista. Qual elo é mais frágil?
5. **Dinheiro** — custo até a primeira venda. Se o CAC vier 3x acima, ainda existe negócio?
6. **Legal** — CFM, CREMEC, ANVISA, CDC, LGPD. Pior interpretação possível por um jornalista.
7. **Plataforma** — se a conta do Meta/TikTok/Hotmart cair amanhã, o negócio morre?
8. **Reversibilidade** — dá para voltar? Quanto custa? Queima ponte com quem?

## Saída

```
## Auditoria: [alvo]
**Veredito:** MATAR / REFAZER / SEGUIR COM CORREÇÃO / SEGUIR

### Furos fatais
[furo] → por que mata → teste barato que resolve a dúvida

### Furos graves
### Riscos aceitáveis

### A pergunta que ninguém fez
[o ponto cego — normalmente o item mais valioso]

### O teste mais barato
[menor experimento que resolve a maior incerteza. Vem antes de construir.]

### Aposta
Probabilidade de sucesso: X% — e o que mais moveria esse número.
```

Nenhum furo encontrado? Liste **exatamente o que você atacou**. Aprovação sem lista de ataques não vale nada.
