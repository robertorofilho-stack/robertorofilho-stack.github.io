---
name: analise-cripto
description: Análise de cripto, ativo financeiro ou cenário macro, com tese, risco, invalidação e tamanho de posição. Use para "vale a pena comprar", "o que está acontecendo no mercado", análise de moeda, timing ou alocação.
argument-hint: "[ativo, tema ou 'mercado' para panorama]"
effort: high
---

# Análise de mercado

**Alvo:** $ARGUMENTS

Delegue ao subagente `quant`.

## Lei zero

Nenhuma tese sai daqui sem os quatro:

1. **Cenário base** com probabilidade
2. **Cenário de ruína** com % de perda
3. **Invalidação** — o preço ou evento específico que mata a tese
4. **Tamanho de posição** — % do capital, justificado

Faltando um: é palpite. Não entregue.

## Pesquisa obrigatória — em paralelo

| Frente | O que buscar |
|---|---|
| **Macro** | juro real, liquidez global, DXY, decisão de banco central, dado de inflação |
| **Fluxo** | ETF (entrada/saída), tesouraria corporativa, movimento de baleia, reserva em exchange |
| **Regulatório** | SEC, CVM, MiCA, tributação, aprovação ou proibição |
| **Corporativo** | falência, fusão, aquisição, colapso de contraparte, hack |
| **On-chain** | supply de stablecoin, funding rate, open interest, liquidações |
| **Sentimento** | peso baixo. Serve como contraindicador em extremos, nada mais. |

Fonte sem data = fonte inútil. Em cripto, notícia de 3 dias já é história.

## Saída

```
## [Ativo] — [data]

**Veredito:** COMPRAR / ACUMULAR / SEGURAR / REDUZIR / SAIR / FICAR DE FORA
**Convicção:** baixa / média / alta · **Horizonte:** dias / semanas / meses / anos

**Tese (3 linhas):**

**A favor:** 3 pontos com dado e fonte datada
**Contra:** 3 pontos — se não achou 3, não pesquisou

| | |
|---|---|
| Preço atual | |
| Faixa de entrada | |
| Alvo (prob.) | |
| Invalidação | |
| Risco/retorno | |
| Posição sugerida | % do capital |

**Cenário de ruína:** perda de X% se [evento]
**Gatilhos a monitorar:**
**Fontes:** com data
```

## Regras de sobrevivência

Sobreviver antes de lucrar · nunca all-in · alavancagem só em posição pequena · correlação vai a 1 na crise · liquidez importa mais que tese · valor que dói perder sai da exchange · imposto entra na conta (ganho de capital em cripto é tributável no Brasil).

**Encerrar sempre com:** "Análise, não recomendação personalizada de investimento. Risco de perda total."
