# 📊 Métricas

> Só número **medido**. Estimativa vai marcada como `(est.)`.
> Número sem fonte não entra aqui.

## Digital

| Métrica | Valor | Data | Fonte |
|---|---|---|---|
| Instagram @robertorodriguesmd | — | — | — |
| TikTok @robertorodriguesmd | — | — | — |
| Tráfego do site | — | — | — |
| Agendamentos via site | — | — | — |

## Produtos

| Produto | Vendas | Receita | CPA | ROAS | Reembolso | Período |
|---|---|---|---|---|---|---|

## Referências de decisão

| Indicador | Faixa | Ação |
|---|---|---|
| ROAS | < 1,5 | matar |
| ROAS | 1,5 – 2,5 | otimizar |
| ROAS | > 3,0 | escalar |
| LTV / CAC | < 3 | negócio frágil |
| Taxa de checkout | < 40% | atrito no checkout |
| Aceite de order bump | < 15% | bump errado |
| Reembolso | > 8% | entrega ou promessa com problema |

## Radar (daemon na `main`)

| Métrica | Valor | Data | Fonte |
|---|---|---|---|
| Sinais brutos por varredura (Trends 19 · HN 29 · SE 0) | 48 | 2026-09-10 15:57Z | run #1 do `radar-lucro` |
| Grupos após deduplicação | 42 | 2026-09-10 | idem |
| Oportunidades acima do corte (≥ 45) | 1 | 2026-09-10 | idem |
| ALTA pendentes (abre issue) | 0 | 2026-09-10 | idem |
| Duração do run | 21 s | 2026-09-10 | Actions |

## Custo de operação (Claude Code na web)

| Métrica | Valor | Data | Fonte |
|---|---|---|---|
| Sessão de infraestrutura (cérebro, radar, CI, soberania, índice v4, merge) | US$ 53,33 | 2026-09-10 | `get_session` (usage) |
| Tokens de saída na sessão | 338 mil | 2026-09-10 | idem |
| Contexto usado / disponível | 335 mil / 1 M | 2026-09-10 | idem |

_Referência para comparar sessões de rotina: devem custar uma fração disto._

## Conselho de outros motores

| Métrica | Valor | Data | Fonte |
|---|---|---|---|
| Crédito OpenRouter restante | US$ 34,66 de 40,00 | 2026-09-10 | `conselho.py --saldo` |
| Rodada de 4 motores (GPT-6 Astra, Grok 4.6, Gemini 3.8 Flash, DeepSeek v4.1) | US$ 0,093 | 2026-09-10 | relatório da rodada |
| Latência por motor | 34 s · 53 s · 15 s · 10 s | 2026-09-10 | idem |
| Motores que responderam | 4/4 | 2026-09-10 | idem |

## Baseline

_Sem baseline não existe melhora — só sensação. Preencher antes da primeira campanha._

## Leads do Google Maps (`leads/`, nuvem do Claude Code, 12/10/2026)

| Métrica | Valor | Data | Fonte |
|---|---|---|---|
| Fichas em modo completo de IP de datacenter (pt e en) | 20/20 vazias (só o link) | 2026-10-12 | `prova-fisio-fortaleza-bruto.csv`, `prova-en-bruto.csv` |
| `fast_mode`, 1 termo ("clínicas de fisioterapia em Fortaleza CE") | 20 negócios em 12 s · telefone 20 · celular 18 · site 13 · sem site 7 | 2026-10-12 | `prova-fast.md` |
| `--redes` sobre os 13 sites | 8 s · Instagram 8 · Facebook 4 · LinkedIn 2 · WhatsApp no site 8 · e-mail 3 | 2026-10-12 | `prova-fast.md` |
| 3 bairros, completo → fallback automático → rápido | 59 únicos em 1m30 · 33 sites · Instagram 19 · Facebook 15 · LinkedIn 10 · WhatsApp no site 17 · e-mail 11 | 2026-10-12 | `prova-bairros.md` |
| Custo por lead | R$ 0 (Docker local; proxy da sessão) | 2026-10-12 | — |
| Comparação: caçador OSM do mestre | ~6% e-mail · ~21% site · ~40% celular | 2026-09-26 | memória do mestre |
| Testes do `leads/` | 37, 0 falhas, ~1,6 s | 2026-10-12 | `leads/testes/testar_leads.py` |

## Conselho e levantamento — organização do Cérebro (13/10/2026)

| Métrica | Valor | Data | Fonte |
|---|---|---|---|
| Conselho (GPT 6.1 sol-pro, Grok 4.7, Gemini 3.8 flash, DeepSeek V4.1 flash) | 4/4 responderam · 4/4 AJUSTAR · 33 s · US$ 0,0509 | 2026-10-13 | `conselho.py --saida` (cópia no mestre) |
| Crédito OpenRouter restante antes da rodada | US$ 20,48 de US$ 40 | 2026-10-13 | `conselho.py --saldo` |
| Mestre: skills / agentes / memórias / leis | 181 · 156 (+12 pastas) · 637 · 45 | 2026-10-13 | levantamento Explore (HEAD 50fba20e) |
| Memórias apontadas pelo índice injetado | 204 de 637 (32 %) · leis 23 de 45 | 2026-10-13 | idem |
| Tabelas de roteamento paralelas | 5 | 2026-10-13 | parecer do Arcanjo |

## Contrato de rota e índice de capacidades (13/10/2026)

| Métrica | Valor | Data | Fonte |
|---|---|---|---|
| Linha de base: missões recentes do TASK_LOG do mestre que nomeiam diretor em "Agentes usados" | **0 de 30** (2 citam "diretor" em algum campo) | 2026-10-13 | TASK_LOG, 30 mais recentes (11–12/10) |
| Índice mestre+satélite | 349 capacidades · 14 diretores · 29 sem domínio · 62 sem gatilho · 10 ponteiros mortos · 51 gatilhos semeados | 2026-10-13 | `RELATORIO-CAPACIDADES.md` |
| Índice do satélite | 30 capacidades (20 skills · 10 subagentes) · 1 sem domínio · 5 sem gatilho | 2026-10-13 | `.claude/RELATORIO-CAPACIDADES.md` |
| Roteador do mestre, bytes injetados por prompt (HOME simulado) | 1º prompt 46,8 KB · 2º 17,3 KB · categorias 64 (antes 73, com 3 tabelas) | 2026-10-13 | teste local do `router-hook.mjs` |
| Testes novos | hook 9 · gerador 6 · 0 falhas | 2026-10-13 | `testar-rota-hook.mjs`, `testar-capacidades.py` |
