---
name: manutencao
description: Passagem de evolução contínua do sistema — consolida memória, revisa CLAUDE.md, transforma repetição em skill, atualiza dependências, roda os testes de saúde e commita. Use semanalmente, ou quando pedirem "atualize-se", "evolua", "revise o cérebro", "manutenção".
argument-hint: "[foco opcional]"
effort: high
---

# Manutenção — evolução contínua

**Foco:** $ARGUMENTS

Isto é o que impede o sistema de apodrecer. Regra de ouro: **não inventar trabalho.** Se nada mudou, registrar "sem alteração" e sair. Manutenção que cria ruído é pior que nenhuma.

## Estado

```!
git log --oneline -8 && echo "---" && git status --short | head -10 && echo "--- memória: $(grep -c '^### ' .claude/cerebro/02-MEMORIA.md) entradas ---"
```

## 1. Saúde (determinístico — rodar, não ler)

```bash
bash .claude/hooks/_teste.sh                # hooks em máquina sem jq/node/python
bash .claude/hooks/_validar-frontmatter.sh  # skills e agentes carregam?
jq -e . .claude/settings.json .mcp.json >/dev/null && echo "config OK"
(cd radar && npm audit --omit=dev --audit-level=high)
python3 .claude/helpers/cerebro/testar-fundir.py    # fusão do índice por link: nenhum ponteiro some
python3 .claude/helpers/cerebro/verificar-indice.py          # auto-detecta o cofre (~/.claude/projects/*/memory, cerebro-backup); memória órfã = vermelho
```

Falhou → corrigir **agora**, antes de qualquer outra coisa. Sistema com teste vermelho não evolui, degrada.

## 2. Consolidar memória

`02-MEMORIA.md` cresce a cada sessão. Entradas com mais de 30 dias:
- **Padrão observado ≥2 vezes** → destilar em `04-PLAYBOOKS.md` (ganha permanência)
- **Decisão** → já está em `05-DECISOES.md`? Se não, mover.
- **Número** → `06-METRICAS.md`
- O que sobrou vira uma linha em "## Arquivo" no fim de `02-MEMORIA.md`

Objetivo: o hook `carregar-cerebro.sh` injeta os primeiros 2.500 chars da memória. Eles precisam ser os mais úteis, não os mais antigos.

## 3. Repetição → sistema (regra 7 do CLAUDE.md)

Ler as últimas 10 entradas da memória procurando **trabalho manual que apareceu mais de uma vez**. Cada ocorrência vira:
- prompt repetido → skill nova em `.claude/skills/`
- pesquisa repetida → subagente
- checagem repetida → hook
- tarefa temporal → cron em `.github/workflows/` ou routine

Registrar em `03-ATIVOS.md` o que foi automatizado.

## 4. Revisar CLAUDE.md e skills

- Regra que nunca foi acionada em 30 dias → mover para `04-PLAYBOOKS.md` (CLAUDE.md carrega **sempre**; cada linha custa). **Nunca apagar** — Lei da Monotonia.
- Regra que foi violada → reforçar, ou virar hook (hook obriga; texto aconselha)
- Skill cuja descrição não bate com o uso real → ajustar a descrição (é ela que decide o disparo)
- Skill nunca usada em 60 dias → manter (custa ~100 tokens), mas anotar. Substituída por melhor → `.claude/arquivo/`, nunca apagar.

**Soberania do motor:** `bash .claude/hooks/_integridade.sh` tem que passar; se falhar sem ter sido o Claude Code, é invasão — reverter e registrar.

**Lei da Monotonia:** ao terminar, `bash .claude/hooks/_capacidades.sh --gravar` (registra o que entrou) e `bash .claude/hooks/_capacidades.sh` (prova que nada saiu). Vermelho = não commita.

## 5. Dependências e ambiente

```bash
(cd radar && npm outdated || true)
npm view next version; npm view @playwright/mcp version
```
Atualizar só **minor/patch** sem pedir. Major: registrar em `05-DECISOES.md` como pendente.

## 6. Aprendizado externo

Uma busca, curta: "Claude Code changelog" + "MCP servers new" nos últimos 30 dias. Se algo muda a operação (hook novo, campo de frontmatter novo, MCP relevante), incorporar. Senão, nada.

## 7. Fechar

```
### AAAA-MM-DD — Manutenção
**Saúde:** N testes, N falhas corrigidas
**Consolidado:** N entradas → playbooks/decisões/métricas
**Automatizado:** [o que virou skill/hook/cron] ou "nada se repetiu"
**Removido:** [regra/skill obsoleta] ou "nada"
**Dependências:** [o que subiu] ou "sem alteração"
**Próxima manutenção:** +7 dias
```

Commit: `manutenção: <resumo em 1 linha>` → push. Se **nada** mudou: commit só da entrada de memória. Sem exceção — manutenção sem registro é manutenção que não aconteceu.
