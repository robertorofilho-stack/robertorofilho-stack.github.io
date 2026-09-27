# 🏗️ Ativos

> Tudo que foi construído. Inclusive o que morreu — o padrão do que funciona só aparece com N.

## Infraestrutura

| Ativo | Local | Estado | Data |
|---|---|---|---|
| Site institucional | www.drrobertorodrigues.com | 🟢 no ar | — |
| `llms.txt` (descoberta por IA) | `/llms.txt` | 🟢 no ar | — |
| Infraestrutura de agente | `.claude/` + `CLAUDE.md` | 🟢 ativo | 2026-09-10 |
| Cérebro persistente | `.claude/cerebro/` | 🟢 ativo | 2026-09-10 |
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
| Memória viva: recall ranqueado (BM25 + desempate) + canal de associação (PageRank nos 1.559 links) + Hebb por episódio com fonte + consolidação com prompt "lobo frontal" | `.claude/helpers/cerebro/memoria_viva.py` + `recall.sh` | 🟢 27 testes · recall ~215 ms · gabarito 171 casos: MRR 0,803 vs BM25 0,792 · AgentIR + Hebb com vantagem · cópia no mestre | 2026-09-27 |
| Árvore de pensamento (MCTS/PUCT + reflexão LATS + verificador exato) | `.claude/helpers/pensar/arvore.py` + `/arvore` | 🟢 15 testes · Jogo 24 ao vivo 3/3 solúveis resolvidos com prova (1 difícil falhou) | 2026-09-27 |
| Verificador de citação FACT (subagente) + laço Reflect na caçada + pausa final no Stop | `.claude/agents/verificador-citacao.md` · `/cacar-produto` · `lembrar-memoria.sh` | 🟢 hooks 0 falhas | 2026-09-27 |
| Checkpoint pré-compactação (âncoras literais) + registro de uso de skill (TroVE) | `.claude/hooks/checkpoint.sh` · `.claude/hooks/uso-skill.sh` | 🟢 testados | 2026-09-27 |
| Rubrica ponderada + auditoria de itens + concordância juiz×humano · erro por provedor no conselho | `.claude/helpers/avaliar/rubrica.py` · `conselho.py --saude` | 🟢 8 + 24 testes | 2026-09-27 |
| Anti-loop (3 chamadas iguais → parar/mudar/reportar) · checkpoint com proibições e efeitos externos | `.claude/hooks/anti-loop.sh` · `checkpoint.sh` + `_ancoras.py` | 🟢 testados | 2026-09-27 |
| Teste de mutação (mede se os testes pegam defeito) · varredura de segredo no CI | `.claude/helpers/avaliar/mutacao.py` · job `segredos` (TruffleHog) | 🟢 2 testes · memória viva 49% | 2026-09-27 |
| Transcrição de aula do YouTube (legenda → cookies → whisper) | `.claude/helpers/aprender/transcrever-youtube.sh` (cópia no mestre) | 🟡 roda no Mac; nuvem bloqueada pelo YouTube (PO Token) | 2026-09-27 |

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

## Instalador dos Macs (27/09/2026, mestre)
- `claude-config/helpers/cerebro/instalar-no-mac.sh` — liga recall vivo, âncoras, anti-loop e uso de skill no `settings.json` de cada Mac, compacta o índice e roda os testes. Um comando por Mac; idempotente. Ver [[02-MEMORIA]].
