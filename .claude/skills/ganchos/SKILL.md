---
name: ganchos
description: Gera 30 ganchos (hooks) prontos para vídeo curto, anúncio ou headline sobre um tema. Use quando pedirem ganchos, headlines, ideias de abertura, títulos ou "como começar o vídeo".
argument-hint: "[tema]"
---

# 30 ganchos

**Tema:** $ARGUMENTS

Gancho vence nos **3 primeiros segundos** ou não existe. Nada depois dele salva um gancho fraco.

Gere **30**, distribuídos pelos 10 padrões abaixo — 3 de cada. Todos sobre o tema, todos prontos para falar.

## Os 10 padrões

1. **Contradição de autoridade** — "Sou ortopedista e vou te dizer por que a maioria dessas cirurgias não deveria acontecer."
2. **Erro custoso** — "Você faz isso há anos achando que ajuda. Está piorando."
3. **Número específico** — "83% das pessoas com esse estalo no joelho não têm lesão nenhuma."
4. **Bastidor** — "O que médico fala entre médico e não fala pro paciente."
5. **Negação do senso comum** — "Alongar antes de correr não previne lesão. Nunca preveniu."
6. **Pergunta que dói** — "Dói mais ao descer escada do que ao subir? Presta atenção."
7. **Aviso urgente** — "Se você sente isso e tem mais de 40, não ignora."
8. **Comparação inesperada** — "Seu joelho não é uma dobradiça. É por isso que o tratamento falha."
9. **Confissão** — "Já indiquei cirurgia que não precisava. Aprendi assim."
10. **Antes/depois de crença** — "Eu achava que X. Aí li o estudo que mudou minha conduta."

## Formato de saída

Tabela. Sem enrolação.

| # | Padrão | Gancho (fala literal) | Texto na tela | Por que funciona |
|---|---|---|---|---|

## Fechamento obrigatório

```
### Os 3 mais fortes
1. [gancho] — motivo
2. [gancho] — motivo
3. [gancho] — motivo

### O mais arriscado
[gancho] — qual o risco (CFM? backlash?) e vale a pena? Sim ou não.
```

## Filtro

- Máximo 12 palavras por gancho
- Zero aquecimento: "fala pessoal", "hoje eu vou falar sobre" → deletar
- Se não dá para dizer em 3 segundos, não é gancho
- Conteúdo médico: sem promessa de cura, sem pânico, sem atacar colega
