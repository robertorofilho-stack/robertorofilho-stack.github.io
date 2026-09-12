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
- 12/09 rodada 2 (Cirurgias360, tese privada): 4/4 responderam, US$ 0,0632 (gpt-6-astra 0,048 · grok-4.6 0,010 · gemini-3.8-flash 0,004 · deepseek-v4.1-flash 0,002; 18–153 s). Veredito 4/4 AJUSTAR.

| Métrica | Valor | Data | Fonte |
|---|---|---|---|
| Crédito OpenRouter restante | US$ 34,66 de 40,00 | 2026-09-10 | `conselho.py --saldo` |
| Rodada de 4 motores (GPT-6 Astra, Grok 4.6, Gemini 3.8 Flash, DeepSeek v4.1) | US$ 0,093 | 2026-09-10 | relatório da rodada |
| Latência por motor | 34 s · 53 s · 15 s · 10 s | 2026-09-10 | idem |
| Motores que responderam | 4/4 | 2026-09-10 | idem |

## Baseline

_Sem baseline não existe melhora — só sensação. Preencher antes da primeira campanha._

## Cirurgias360 — paralelo da nuvem (2026-09-12; o app vivo é o do Mac mini)
- Build Next 16: limpo (17 rotas). Testes de domínio: 12/12. QA Chromium: 40/40 (1ª rodada 4/40 por sanitizador de extensão; 2ª 35/40 por espera de server action; 3ª 39/40 por overflow em 390 px; 4ª 40/40) → 42/42 após o QA adversarial.
- QA adversarial (subagente `qa`, ~193k tokens, 19 min): 1 BLOQUEANTE (server action do Next corta upload em 1 MB → foto de celular dava 500; `bodySizeLimit` resolve), 1 GRAVE (duplo clique duplicava cirurgia), 3 menores. Permissões forjadas, path traversal, upload hostil, XSS, PII em log e corrupção do banco demo: 0 furos.
- Tokens dos subagentes: arquiteto ~84k · auditor ~141k · qa (em curso). Tempo: arquiteto 9 min · auditor 13 min.
- Custo de infra do demo: R$ 0. Piloto estimado: ≈ R$ 150/mês (Supabase Pro + LLM), sem Vercel Pro.
- Custo do erro: ~1 dia de sessão web refazendo o que existia (subagentes ~225k tokens + build). Causa: clone do mestre sem `git pull`. Prevenção: hook `_mestre.sh`.
