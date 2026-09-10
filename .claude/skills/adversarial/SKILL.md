---
name: adversarial
description: Debate adversarial Alfa/Ômega — o Construtor propõe, o Auditor tenta destruir com testes reais, repete até 3 rodadas ou até nada quebrar. Use para validar tese técnica, arquitetura, modelo matemático, código crítico ou qualquer proposta onde o custo de estar errado é alto.
argument-hint: "[problema ou proposta a estressar]"
effort: max
---

# Bancada adversarial — Alfa × Ômega

**Problema:** $ARGUMENTS

Quem constrói não consegue atacar de verdade o que construiu. Por isso os dois papéis rodam em **contextos isolados**: `arquiteto` (Alfa) e `qa` + `auditor` (Ômega). Nunca a mesma instância nos dois papéis.

Saída em `adversarial-bench/<slug>/`.

---

## Rodada 1

**Alfa — proposta**
Tese completa: premissas explícitas, mecanismo, equações ou arquitetura, e **código de simulação executável** que demonstra a tese numericamente. Salvar em `alfa-r1.md` + `sim-r1.py` (ou `.ts`).

Sem código que roda, não é proposta — é opinião.

**Ômega — ataque**
Ler o código. **Executar** via shell. Atacar em ordem:
1. Leis físicas / biológicas violadas (termodinâmica, conservação, atenuação, limites de tecido)
2. Premissa não verificada que, se falsa, derruba tudo
3. Unidade, escala, ordem de grandeza — refazer a conta
4. Código sob estresse: entrada extrema, caso de borda, condição inicial diferente
5. Extrapolação indevida (modelo → mundo real, animal → humano, laboratório → produção)
6. O que a proposta **omitiu** — frequentemente o furo principal

Relatório em `omega-r1.md`: cada falha com reprodução, evidência (log/saída), gravidade.

## Rodadas 2 e 3

Alfa lê `omega-rN.md`, corrige tese e código, reapresenta em `alfa-r(N+1).md`. Ômega ataca de novo.

**Parar quando:** Ômega não acha falha lógica nem de runtime, **ou** completou 3 rodadas.

Se após 3 rodadas ainda há falha fatal: a tese **não sobreviveu**. Isso é resultado válido e valioso — mais barato que descobrir em produção.

## Entrega

```
adversarial-bench/<slug>/
├── README.md         veredito + histórico resumido das rodadas
├── alfa-r1.md ... rN
├── omega-r1.md ... rN
├── sim-final.*       só o código que sobreviveu
└── log/              saída real de cada execução
```

`README.md` termina com:

```
## Veredito
SOBREVIVEU / SOBREVIVEU COM RESTRIÇÕES / NÃO SOBREVIVEU

## O que o Ômega atacou e não quebrou
[lista — aprovação sem esta lista não vale nada]

## Restrições declaradas
[condições fora das quais a tese não vale]

## Próximo teste no mundo real
[o experimento mais barato que resolve a maior incerteza restante]
```

## Regras

- Ômega **executa** código. Ler e imaginar não conta.
- Ômega não ameniza. "No geral está bom" é proibido.
- Alfa não descarta crítica sem refutação com dado.
- Tese que exige violar lei conhecida morre na rodada 1, sem apelação.
- Gravar veredito em `.claude/cerebro/05-DECISOES.md`.
