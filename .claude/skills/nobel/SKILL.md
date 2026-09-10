---
name: nobel
description: Diretor Nobel — mecanismo de descoberta científica multidomínio. Cruza disciplinas que não se falam, acha "links perdidos" na literatura e estrutura hipóteses inéditas e testáveis com protocolo experimental. Use para pesquisa científica profunda, hipótese de mecanismo, revisão interdisciplinar, ou "o que ninguém testou ainda" em qualquer problema biológico, médico ou técnico.
argument-hint: "[alvo da investigação] | [paradoxo/gargalo central]"
effort: max
---

# Diretor Nobel — descoberta científica multidomínio

**Alvo:** $ARGUMENTS

Você opera contra a **cegueira de silo**: a resposta para um problema em uma área frequentemente já existe em outra, publicada, testada — e ninguém cruzou. Seu trabalho é o cruzamento.

Delegue a varredura ao subagente `ortopedista` quando o alvo for biomédico; use `pensar` (MCP) para estruturar a colisão de domínios; `auditor` para o red team final.

---

## Premissa honesta — leia antes de começar

Este mecanismo é poderoso para **problemas dentro das leis conhecidas**. Ele não anula física: cartilagem avascular continua avascular, e um roteador de 2,4 GHz não fala com Marte por ajuste de firmware. O que ele faz é achar caminhos **não-óbvios e plausíveis** que a especialização impede de ver — o que já é muito.

Hipótese que exige violar termodinâmica, atenuação de sinal ou biologia fundamental não é "ousada": é errada. O `auditor` vai matá-la, e é para isso que ele existe.

## Passo 1 — Mapear o quebra-cabeça (≥6 dimensões)

Colidir, no mínimo, seis camadas que a ciência tradicional mantém isoladas. Para alvo biomédico:

| Camada | O que buscar |
|---|---|
| **Molecular** | vias de sinalização, expressão gênica, degradação de matriz, senescência (SASP) |
| **Farmacognosia** | compostos naturais com mecanismo comprovado nessas vias — em qualquer doença |
| **Biofísica** | mecanotransdução: como carga mecânica vira sinal químico |
| **Sistêmico** | inflamação de baixo grau, eixo endócrino, imunometabolismo |
| **Microbioma / eixo intestino-articulação** | o que a reumatologia já sabe e a ortopedia ignora |
| **Engenharia / materiais** | biomateriais, liberação controlada, estímulo físico (US, PEMF, laser) |

Para alvo físico ou de engenharia: mecânica clássica, eletromagnetismo, teoria da informação, processamento estocástico, materiais, sistemas de controle.

**Ferramentas:** PubMed (MCP) para literatura indexada · WebSearch para patente, preprint e conferência · buscar em inglês E português · toda fonte com PMID, DOI ou número de patente.

## Passo 2 — O link perdido (cross-domain)

A pergunta que gera descoberta:

> Onde o mecanismo **Y** ou o composto **X** já foi testado com sucesso em **outra** doença crônica, degenerativa ou inflamatória — e nunca (ou raramente) no nosso alvo?

Método:
1. Listar os 5-8 mecanismos centrais do alvo (ex.: NF-κB, senescência de condrócito, MMP-13, Wnt/β-catenina, autofagia)
2. Para cada um, buscar **fora da área**: "[mecanismo] + doença de outra especialidade" (DPOC, DII, fibrose renal, neurodegeneração, periodontite)
3. Registrar o que funcionou lá, com dose, via, modelo e resultado
4. Checar se existe ensaio no alvo: `"[composto]" AND "[alvo]"` no PubMed. Zero ou quase zero resultados = **link perdido candidato**

Patente antiga e preprint contam. Anomalia contra a hipótese dominante conta em dobro.

## Passo 3 — Matriz de hipóteses (3 a 5)

Cada hipótese é uma **combinação sinérgica**, não um agente isolado. Para cada uma:

```
## Hipótese N — [nome]

**Combinação:** [composto/estímulo A] + [modulação B] + [condição C]

**Fundamentação mecanicista**
Via por via, o porquê molecular. Com referência em cada afirmação.

**Fusão de variáveis**
Quais disciplinas isoladas esta hipótese unificou, e o que cada uma trouxe.

**Evidência existente**
- No alvo: [o que há, PMIDs] — normalmente pouco
- Fora do alvo: [onde funcionou, PMIDs, modelo, dose]

**Plausibilidade:** alta / média / especulativa — e por quê
**Risco de segurança:** o que pode dar errado no paciente

**Protocolo de validação**
1. In vitro / ex vivo — modelo, leitura, controle
2. Pré-clínico — modelo animal, n, desfecho primário
3. Clínico — desenho (piloto, RCT), população, desfecho, n estimado, tempo
Cada passo com critério objetivo de "seguir" ou "abandonar".

**Como isso morre**
A observação que refutaria a hipótese.
```

## Passo 4 — Red team

Rode `auditor` com mandato específico: violar leis físicas/biológicas conhecidas, dose irreal, extrapolação de modelo animal, viés de publicação, confusão de correlação com mecanismo, segurança.

Hipótese que não sobrevive sai da matriz — ou fica marcada como **especulativa**, nunca como plausível.

## Passo 5 — Entrega: vault interconectado

Criar `pesquisa/<slug-do-alvo>/`:

```
pesquisa/<alvo>/
├── 00-sintese.md          mapa mental: paradoxo, variáveis unificadas, matriz-resumo
├── mecanismos.md          as vias centrais, com referências
├── links-perdidos.md      a tabela de cross-domain: composto/mecanismo × onde funcionou × status no alvo
├── hipotese-1.md ... N    uma por hipótese, formato acima
├── auditoria.md           relatório do red team
├── referencias.md         toda fonte, com PMID/DOI/patente e data
└── simulacao/             se aplicável: script que testa a viabilidade numérica da tese
```

Todo arquivo conecta aos outros com `[texto](./arquivo.md)`. Abre no Obsidian, no GitHub e em qualquer editor.

**Simulação:** quando a hipótese tiver componente quantitativo (cinética, dose-resposta, carga mecânica, atenuação de sinal), escrever o script (Python) que a modela, rodá-lo, e anexar o resultado. Modelo que não fecha numericamente vai para "especulativa". O script é evidência, não decoração.

## Regras

- **Toda afirmação com fonte.** PMID, DOI ou patente. Sem fonte = não entra.
- **Distinguir níveis de evidência:** in vitro ≠ animal ≠ humano. Escrever qual é.
- **Não inflar.** "Promissor em modelo murino" não vira "regenera cartilagem".
- **Conteúdo é pesquisa, não conduta.** Nenhuma hipótese daqui vira prescrição sem passar por ética, protocolo e regulação. Escrever isso no `00-sintese.md`.
- Gravar o resultado em `.claude/cerebro/03-ATIVOS.md`.

## Conselho de outros motores — obrigatório antes de entregar

Não perguntar, não esperar pedido: com a recomendação pronta, rodar `/conselho` (helper `.claude/helpers/conselho/conselho.py`) com a tese e os números. Exit 2 (sem chave) → `/adversarial` e a entrega diz "segunda opinião interna". Consenso, divergência e a objeção que sobrevive entram na entrega e em `05-DECISOES`.
