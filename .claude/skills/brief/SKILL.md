---
name: brief
description: Briefing diário de inteligência — mercado, cripto, oportunidades, tendências e o que fazer hoje. Use quando pedirem o resumo do dia, panorama, "o que está acontecendo" ou briefing.
argument-hint: "[foco opcional]"
effort: high
---

# Briefing

**Data:** !`date +%Y-%m-%d`
**Foco:** $ARGUMENTS (vazio = panorama completo)

## Coleta — paralela, obrigatória

Dispare tudo numa mensagem só. Serial aqui desperdiça tempo.

| Bloco | Fontes | Filtro |
|---|---|---|
| **Macro** | juro, inflação, banco central, DXY, commodities | só o que move ativo |
| **Cripto** | BTC/ETH, fluxo de ETF, regulação, hack, liquidação | últimas 24-48h |
| **Corporativo** | falência, fusão, aquisição, IPO, demissão em massa | sinal de ciclo |
| **IA/Tech** | lançamento de modelo, API nova, ferramenta relevante | só o que muda a operação |
| **Oportunidade** | anúncio novo escalando, produto subindo em marketplace, tendência de busca | prova de mercado |
| **Medicina** | ANS, CFM, ortopedia, publicação relevante | só o que afeta a prática |

## Saída — máximo 1 tela

```
# Briefing — [data]

## 🔴 Ação hoje
[no máximo 3 itens. Cada um: o fato → por que importa pra você → o que fazer.
 Se não há nada acionável, escreva "nada acionável" e siga. Não invente urgência.]

## 📊 Mercado
[3-5 linhas. Só o que mudou. Sem repetir o que já é sabido.]

## 💰 Oportunidade da semana
[uma. com evidência. anúncio rodando, produto subindo, tendência real.]

## 🧠 Radar
[2-3 itens para acompanhar, sem ação hoje]

## 📌 Pendente do cérebro
[o que ficou aberto em .claude/cerebro/02-MEMORIA.md]
```

## Regras

- **Sem enchimento.** Dia sem notícia relevante: escreva "dia sem sinal" e liste só o pendente. Fabricar urgência destrói a confiança no briefing.
- Todo número com fonte e data
- "Ação hoje" precisa ser executável em menos de 2 horas
- Encerrar lendo `.claude/cerebro/02-MEMORIA.md` para puxar o que ficou pendente
