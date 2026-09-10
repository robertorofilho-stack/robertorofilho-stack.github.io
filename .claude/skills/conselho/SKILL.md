---
name: conselho
description: Segunda opinião adversarial de outros motores (GPT, Grok, Gemini, DeepSeek) sobre uma tese, decisão, oferta ou produto — em paralelo, por API, com síntese das divergências. Use antes de fechar qualquer missão estratégica, ou quando pedirem "pergunta para outras IAs", "contra-argumento", "o que o GPT acha", "segunda opinião".
argument-hint: "[tese, decisão ou recomendação a estressar]"
effort: high
---

# Conselho de outros motores

**Tese:** $ARGUMENTS

Modelos de laboratórios diferentes têm pontos cegos diferentes. O conselho pede o **contra-argumento**, nunca a confirmação. A síntese é minha; o veredito é do operador.

## 1. Formular a tese (≤ 200 palavras)

Uma tese estressável tem: a afirmação, o número que a sustenta, a premissa mais frágil e o que já foi decidido. Sem número, o conselho devolve opinião — e opinião não vale o custo.

**Nunca enviar:** dado de paciente, credencial, faturamento. Produto não lançado vai com nome genérico ("curso X para o nicho Y").

## 2. Consultar

```bash
# o helper mora no satélite; fora dele (sessão por voz do RAION em ~/Claude, sessão no mestre) usa a cópia de ~/.claude/helpers
H="${CLAUDE_PROJECT_DIR:-.}/.claude/helpers/conselho"; [ -f "$H/conselho.py" ] || H="$HOME/.claude/helpers/conselho"
python3 "$H/conselho.py" --status                      # chaves prontas? (exit 2 = nenhuma)
python3 "$H/conselho.py" --saldo                       # crédito do OpenRouter antes de gastar (exit 2 = abaixo de US$ 1)
python3 "$H/conselho.py" --tese "<tese>" --contexto "<números e decisões>" --saida /tmp/conselho.md
```

- Exit 2 (sem chave) → rodar `/adversarial` no lugar e dizer explicitamente: *"conselho offline, segunda opinião foi interna"*.
- Nos Macs a chave já existe no cofre `~/.config/vha-vibe-marketing/.env` (chave padrão de LLM do mestre); o helper lê sozinho.
- Na nuvem (Pro/Max) a chave pode estar como **API credential** do ambiente: o proxy assina as requisições e o helper detecta sozinho (`--status` mostra "credencial no proxy da nuvem"). Nada a configurar no código.
- Modo livre (ideias em vez de ataque): `--modo livre`. Forçar modelos: `--modelo openrouter:openai/gpt-5`.
- O helper escolhe o modelo mais novo de cada família e informa custo por chamada quando o provedor publica preço.

## 3. Sintetizar (é aqui que está o valor)

| Objeção | Quantos motores levantaram | Sobrevive aos dados? | Mudança no plano |
|---|---|---|---|

Depois da tabela, três linhas obrigatórias:
1. **Consenso:** o que todos apontaram (é quase certamente real).
2. **Divergência:** onde discordaram e qual lado os dados sustentam.
3. **A objeção que sobrevive:** a única que muda a decisão — e o que fazer com ela.

Custo total da rodada, em US$, na última linha.

## 4. Registrar

Em `.claude/cerebro/05-DECISOES.md`, na decisão correspondente: `**Conselho (data):** consenso · divergência · objeção que sobreviveu · custo`. Sem registro, a rodada foi desperdiçada.

## Quando usar

Fechamento de `/cacar-produto`, `/oferta`, `/lancamento`, `/analise-cripto`, `/nobel` e qualquer decisão que custe dinheiro ou seja difícil de desfazer. Não usar para tarefa operacional — é caro e lento para isso.
