---
name: arvore
description: Busca em árvore de pensamentos (MCTS/PUCT + reflexão verbal, estilo LATS) para problema difícil com resposta VERIFICÁVEL — conta, código com teste, restrição checável, quebra-cabeça, plano com critério objetivo. Use quando a primeira resposta costuma errar e existe como checar o resultado. Não use para decisão de gosto nem para ação irreversível.
argument-hint: "[problema] — ou --jogo24 \"a b c d\" para demonstração"
effort: high
---

# Árvore de pensamento

**Problema:** $ARGUMENTS

## Quando usar (e quando não)

| Usar | Não usar |
|---|---|
| Existe **verificador**: teste, conta, regra checável, `saude.yml`, CRC do Pix | Pergunta de opinião/gosto → `/conselho` |
| A 1ª tentativa costuma errar (quebra-cabeça, cálculo encadeado, bug teimoso) | Ação irreversível (pagar, enviar, publicar): explorar = executar |
| Vale gastar 10–40 chamadas por uma resposta certa | Resposta que uma busca no cérebro já dá |

Lição medida em 27/09 (execução real, Jogo 24): o **juiz LLM aprovou com nota 1,0 uma solução errada**.
Só o verificador exato pegou. Por isso: resultado rotulado "aprovada pelo juiz — NÃO verificada" não é
entrega; é hipótese. Sempre que der, escreva o verificador antes (é o que o CS329A chama de gargalo real).

## Executar

```bash
python3 .claude/helpers/pensar/arvore.py --problema "<problema, com o formato esperado de cada passo>" \
  --iter 12 --k 3 --prof 4 --max-chamadas 40 --teto-usd 0.30 --saida /tmp/arvore.md
```

- Custo: teto duro por `--max-chamadas` e `--teto-usd` (padrão US$ 0,30). Rodada típica: US$ 0,003–0,012.
- Motor: OpenRouter pelo transporte do `conselho.py` (cofre do Mac ou credencial do proxy na nuvem).
- Demonstração com verificador exato: `arvore.py --jogo24 "4 7 8 8"`.
- Problema com verificador próprio: importar `arvore.buscar()` num script e passar um motor com
  `verificar(problema, caminho) -> 1.0 | 0.0 | None` e `tem_verificador = True`.

## Entregar

1. O melhor caminho + se foi **verificado** (exato) ou só **julgado** (LLM).
2. As reflexões — os erros que a busca aprendeu a evitar (servem de gotcha para a memória).
3. Custo real e número de chamadas.
4. Se a lição servir de novo: `memoria_viva.py episodio ... --licao "..."`.
