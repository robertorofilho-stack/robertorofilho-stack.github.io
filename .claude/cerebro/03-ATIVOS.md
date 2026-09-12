# 🏗️ Ativos

> Tudo que foi construído. Inclusive o que morreu — o padrão do que funciona só aparece com N.

## Infraestrutura

| Ativo | Local | Estado | Data |
|---|---|---|---|
| Site institucional | www.drrobertorodrigues.com | 🟢 no ar | — |
| `llms.txt` (descoberta por IA) | `/llms.txt` | 🟢 no ar | — |
| Infraestrutura de agente | `.claude/` + `CLAUDE.md` | 🟢 ativo | 2026-09-10 |
| Cérebro persistente | `.claude/cerebro/` | 🟢 ativo | 2026-09-10 |
| Paralelo do app Cirurgias feito na nuvem (referência: auditoria 20 fontes, conselho, docs LGPD, módulos) — o app VIVO é do Mac mini | mestre privado: `projetos/cirurgias360/paralelo-nuvem-2026-09-12/` | 🟡 referência (40/40 Playwright, mas duplica o vivo) | 2026-09-12 |
| Hook `_mestre.sh` — atualiza o clone do mestre antes do recall (nuvem) | `.claude/hooks/_mestre.sh` | 🟢 testado ao vivo | 2026-09-12 |
| Radar de oportunidade (5 fontes) | `radar/radar-lucro.ts` | 🟢 testado | 2026-09-10 |
| Gerador de micro-SaaS (Pix + PayPal) | `radar/gerar-saas.ts` + `templates/` | 🟢 testado | 2026-09-10 |
| QA adversarial (Chromium) | `radar/qa.ts` | 🟢 aprovou 12/12 | 2026-09-10 |
| Gerador Pix BR Code (EMV, offline) | `radar/src/pagamento/pix.ts` | 🟢 CRC validado | 2026-09-10 |
| Daemon 24/7 (cron + issue automática) | `.github/workflows/radar.yml` | 🟢 ativo na `main` (cron :17) | 2026-09-10 |
| 17 skills · 9 subagentes · 5 hooks · 5 MCPs | `.claude/` + `.mcp.json` | 🟢 carregando | 2026-09-10 |
| Recall automático (memória relacionada a cada prompt) | `.claude/hooks/recall.sh` | 🟢 38 ms | 2026-09-10 |
| Suíte de testes dos hooks (sem jq/node/python) | `.claude/hooks/_teste.sh` | 🟢 0 falhas | 2026-09-10 |
| Saúde semanal + a cada push (hooks, skills, radar, build, QA) | `.github/workflows/saude.yml` | 🟢 | 2026-09-10 |
| Skill de evolução contínua | `/manutencao` + routine semanal | 🟢 | 2026-09-10 |
| Bootstrap de máquina nova | `.claude/bootstrap.sh` | 🟢 testado | 2026-09-10 |
| Backup fora do GitHub (bundle + config) | `.claude/backup.sh` | 🟢 restauração testada | 2026-09-10 |
| Kit de recuperação | `.claude/KIT-RECUPERACAO.md` + Google Doc | 🟢 | 2026-09-10 |
| Fusão do índice do mestre por link + guarda anti-perda | `.claude/helpers/cerebro/fundir-indice.py` (v4) | 🟢 instalado no mestre (`c96d37e`) · produção 244 → 244 | 2026-09-10 |
| Verificador de memória órfã (bootstrap, sessão, manutenção) | `.claude/helpers/cerebro/verificar-indice.py` | 🟢 auto-detecta o cofre · 25 ms / 246 memórias · 25 testes | 2026-09-10 |
| Soberania de motor (pre-commit + manifesto SHA-256 no CI) | `.claude/git-hooks/pre-commit` + `_integridade.sh` | 🟢 invasão simulada bloqueada | 2026-09-10 |
| Conselho de outros motores (GPT, Grok, Gemini, DeepSeek em paralelo) | `.claude/helpers/conselho/conselho.py` + `/conselho` | 🟢 ativo na nuvem e nos Macs · 1ª rodada 4/4, US$ 0,093 | 2026-09-10 |

## Produtos digitais

| Produto | Nicho | Preço | Estado | Receita | Data |
|---|---|---|---|---|---|
| Exemplo gerado sob demanda (`gerar-saas.ts --fixture`; não versionado — CI regenera) | CSV bancário → resumo mensal de gastos | R$9,90 / US$1,90 | 🧪 esqueleto | R$0 | 2026-09-10 |

_Primeira caçada de infoproduto ainda pendente: `/cacar-produto aberto`._

## Conteúdo

| Peça | Canal | Alcance | Conversão | Data |
|---|---|---|---|---|

## Cemitério

> Ativo morto registrado vale mais que ativo morto esquecido. Aqui mora o aprendizado caro.

| Ativo | Por que morreu | Custo | Lição |
|---|---|---|---|
