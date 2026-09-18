# Graphify — checagem dos números

> Tudo abaixo foi conferido na **fonte primária** (arquivos do próprio repositório, em `raw.githubusercontent.com`)
> em **18/09/2026**. Nada aqui vem de blog, thread ou print.
> Repositório: `Graphify-Labs/graphify`, branch `v8`. `BENCHMARKS.md` atualizado em **05/07/2026**.

## Veredito do rascunho original

| # | O que o rascunho dizia | Veredito | O que a fonte diz |
|---|---|---|---|
| 1 | "116.800 estrelas" | ⚠️ **desatualizado** | **119.340** estrelas (API do GitHub, 18/09/2026, 20h05 UTC). O repo nasceu em 03/04/2026 — o número anda rápido, sempre datar |
| 2 | "licença Apache-2.0" | ✅ **certo** | `LICENSE` = Apache License 2.0. A página do GitHub ainda lista "Apache-2.0, MIT" — o relicenciamento é recente |
| 3 | "roda local sem consumir crédito de modelo pra construir o grafo" | ✅ **certo, com ressalva omitida** | README: `\| Graph build \| LLM credits \| **0** \|`. Ressalva: vale para **código** (tree-sitter, local). **Docs, PDF e imagem são enviados a um modelo**; vídeo/áudio são transcritos localmente (faster-whisper) |
| 4 | "o número de 70% que circula não está no README" | ✅ **certo — e é pior que isso** | Não existe **nenhum** número de economia de token no README. E o que circula não é 70%: é **70x**. Nasceu em blog (mindstudio.ai, 01/05/2026), que não cita benchmark — atribui "ao mecanismo" |
| 5 | "ganho de acurácia de 70,8% para 82,0%, ~140 mil tokens por consulta" | ✅ **certo, faltou o essencial** | `BENCHMARKS.md`: "from 70.8% (a grep and read baseline) to 82.0%, at about 140K tokens per query" — em ERPNext (~1M linhas). **n = 6 perguntas.** Métrica = *key-fact coverage* com crédito parcial: `(covered + 0.5·partial) / total` |
| 6 | "45,3% de acurácia no LOCOMO e 76% no LongMemEval-S" | ✅ **certo, faltou o contexto** | LOCOMO (n=300): graphify 45,3% — **supermemory faz 49,7%** (mas 11x o custo de ingest: US$ 15,67 vs US$ 1,40). graphify lidera em recall@10 (0,497). LongMemEval-S (n=50): 76% — **empatado com dense RAG** (76%), que é baseline comum |
| 7 | "acurácia e economia de token são promessas diferentes; ele mede a primeira" | ⚠️ **quase** | O BENCHMARKS **também** fala de token: empilhar o repositório inteiro no contexto custa "roughly 20x the tokens for lower coverage". O que não existe é a promessa "economiza 70%" |
| 8 | "em projeto de dez arquivos o grafo não tem o que resolver" | ✅ **sustentado por fonte independente** | Review da wavect.io (16/07/2026, revisto 02/09/2026): "It is not an automatic productivity win for a small repository" |

## O que ninguém posta (e devia)

1. **n = 6.** O headline de código (70,8% → 82,0%) sai de **seis perguntas**. É sinal, não prova. A própria review independente aponta: *"the code-intelligence sample is only six questions"*.
2. **Harness próprio.** mem0 e supermemory rodam como adaptadores dentro do harness do graphify. A favor: um só modelo para todos (Kimi K2.6), orçamento idêntico, e o juiz foi validado às cegas contra um segundo juiz (**90,6% de concordância, kappa de Cohen 0,81**) — mais disclosure que a média do setor. Ainda assim: números autopublicados.
3. **Cobertura ≠ acerto.** 82,0% é cobertura de fatos-chave com meio ponto para resposta parcial, não "acertou 82% das perguntas".
4. **Zero crédito é do código.** Corpus só de código roda offline, sem chave de API. Repositório misto com docs/PDF precisa de backend (Gemini, Kimi, Claude, OpenAI, DeepSeek, Ollama ou Bedrock) — ou `--code-only`.
5. **Benchmark tem validade.** `BENCHMARKS.md` está congelado em 05/07/2026; o repositório continuou a andar.

## Fontes

| Fonte | Tipo | Data |
|---|---|---|
| `README.md` (branch `v8`) | primária | lida em 18/09/2026 |
| `BENCHMARKS.md` (branch `v8`) | primária | atualizada em 05/07/2026 |
| `LICENSE` (branch `v8`) | primária | lida em 18/09/2026 |
| API do GitHub — 119.340 estrelas, 11.534 forks | primária | 18/09/2026 |
| wavect.io — *Graphify Review 2026* | independente, crítica | 16/07/2026 (revisto 02/09/2026) |
| mindstudio.ai — *…Cuts Large Codebase Costs by 70x* | origem do número que circula | 01/05/2026 |

## Como refazer a checagem

```bash
curl -s https://raw.githubusercontent.com/Graphify-Labs/graphify/v8/README.md     | grep -n "%"
curl -s https://raw.githubusercontent.com/Graphify-Labs/graphify/v8/BENCHMARKS.md | grep -n "70.8\|82.0\|140K\|n=\|judge"
```
