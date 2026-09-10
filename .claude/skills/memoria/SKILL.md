---
name: memoria
description: Lê ou grava o cérebro persistente do operador (vault Obsidian em .claude/cerebro). Use no início de trabalho estratégico para carregar contexto, e no fim para gravar decisão, número, aprendizado ou ativo criado.
argument-hint: "[ler | gravar <conteúdo> | buscar <termo>]"
---

# Cérebro

**Comando:** $ARGUMENTS

O contêiner é efêmero. **O repositório é a memória.** Sessão que não grava é sessão desperdiçada.

## Estado atual

```!
ls -la .claude/cerebro/ 2>/dev/null && echo "---" && tail -40 .claude/cerebro/02-MEMORIA.md 2>/dev/null
```

## Modos

**`ler`** (padrão sem argumento)
Ler `00-MAPA.md` e os arquivos relevantes ao trabalho em curso. Resumir em ≤10 linhas: quem é, onde está, o que está em jogo, decisões abertas.

**`gravar <conteúdo>`**
Anexar em `.claude/cerebro/02-MEMORIA.md`, no topo da seção do mês:

```markdown
### AAAA-MM-DD — [título curto]
**Contexto:** por que isso aconteceu
**Decisão/Resultado:** o que foi decidido ou produzido
**Número:** qualquer métrica real observada
**Aprendizado:** o que muda daqui pra frente
**Próximo passo:** ação concreta pendente
**Links:** [[03-ATIVOS]] [[05-DECISOES]]
```

Se for **ativo criado** (produto, página, funil, conteúdo) → também em `03-ATIVOS.md`
Se for **decisão estratégica** → também em `05-DECISOES.md`
Se for **número de negócio** → também em `06-METRICAS.md`

Depois: `git add .claude/cerebro && git commit` e push. **Memória não commitada não existe.**

**`buscar <termo>`**
`grep -ri "<termo>" .claude/cerebro/` e sintetizar o que achou.

## Regras

- Wikilinks `[[arquivo]]` — o vault abre direto no Obsidian
- Data ISO sempre: `AAAA-MM-DD`
- **Nunca gravar aqui:** dado de paciente, chave, senha, faturamento, contrato. Repositório público. Isso vai para o vault privado — ver `00-MAPA.md`.
- Sem prosa. Memória é para consulta rápida, não para leitura.
