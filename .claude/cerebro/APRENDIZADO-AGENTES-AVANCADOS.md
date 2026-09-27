# 🎓 Agentes, memória e auto-melhoria — destilação de fronteira (27/09/2026)

> Método do Diretor de Aprendizado (Fase 0→4) + protocolo ARCANJO (execução real, conclusão proporcional à prova).
> Pedido do operador: "aprenda tudo, instale tudo, evolua". Aprendido, auditado, instalado e **medido**.
> Ver [[APRENDIZADO-PROJETO-SUPREMO]] · [[03-ATIVOS]] · [[05-DECISOES]]

## Fase 0 — o que já estava estudado (não reestudar)

- **Stanford CS329A** já foi destilado em 03/09 (9/9 aulas, 14 técnicas, TOP 5 upgrades) — no mestre:
  `aprendizado-stanford/DESTILACAO-STANFORD.md`. Aqui só entra o que o curso ganhou depois: aulas de
  *Open-Ended Evolution* (ADAS, AI Scientist, AlphaEvolve) e *Augmenting Agents with Memory* (MemGPT, Cartridges).
- **Codex** já tem `ferramentas/cerebro-evolucao` (SQLite FTS5, episódio → lição → avaliação pareada → promoção).
  Não duplicado: o que se instalou aqui é o lado Claude (recall ranqueado + grafo associativo + busca em árvore).

## Fase 1 — os cursos, verificados (fontes acessadas em 27/09/2026)

| Curso | Veredito | Por quê |
|---|---|---|
| **CMU 11-768 AI Agents** (Neubig, Fried) — cmu-agents.com | 🥇 o mais atual (Fall 2026) | Aulas 1–8 gravadas no YouTube; memória/skills (MemGPT, Agent Workflow Memory, ReasoningBank, SkillsBench), RL (ReST, GRPO), deep research, e ainda vêm Tree Search e Critic Models |
| **Stanford CS329A** (Chowdhery, Mirhoseini) | 🥈 já dominado | Série de 9 vídeos publicada em ago/2026 |
| **Berkeley CS294/194-280 Advanced LLM Agents** (Dawn Song) | 🥈 o mais "fronteira" público | Raciocínio, memória e planejamento (Yu Su), AlphaProof, prova formal |
| **DeepLearning.AI Agent Memory** (Oracle) | 🔧 engenharia aplicada | 1h57; memory manager, memória de ferramentas, extração/consolidação/write-back. Útil, não é pesquisa |
| **NUS-ISS Architecting Agentic AI** | ❌ não é fronteira | Curso executivo de 4 dias: RAG, LangChain, AutoGen |

Nenhum curso público equivalente confirmado em MIT, ETH, Oxford, Tsinghua, KAIST ou Tóquio. Denso em memória: workshop MemAgents (ICLR 2026).

## Fase 2 — auditoria do material colado (o código foi executado, não lido)

**Veredito geral:** as Partes 1–2 (MCTS, memória episódica/semântica, consolidação, decaimento) são a fronteira real,
com bugs. A partir de "memória holográfica", H.E.V.E.N., S.E.P.H.I.R.O.T.H. e N.E.X.U.S., é **teatro**: vocabulário
de física aplicado a números aleatórios. Medido, não opinado:

| Afirmação | Teste (`auditar_nexus`, 100 pulsos) | Resultado |
|---|---|---|
| "ressoa com a frequência do problema" | vetores de fase aleatória, sem relação com o conteúdo | ressonância esperada ≈ 55,9 com limiar 20 → **tudo "ressoa" sempre**; estímulo zero = nada |
| "cria código que nenhum humano escreveria" | comparar os híbridos | todo híbrido é **o mesmo molde fixo**; saída = `len(texto) × 2,71828` |
| "morte digital seleciona o mais apto" | energia após 100 pulsos | 102 nós, energia 150 → 32.728, **zero mortes** → não há seleção |
| "espaço de Hilbert / quântico" | — | produto interno de numpy. "Holográfico" de verdade é HRR (Plate 1995): recuperação ruidosa, sem ganho medido em agente |
| `exec()` do código auto-gerado | — | risco de segurança sem verificador; a versão segura já existe: skill/hook como arquivo + git + `saude.yml` |

**Bugs nas partes sérias (corrigidos no que foi instalado):**
1. MCTS: `prior = exp(logprob)` de uma frase inteira ≈ 0 → a exploração morre. Certo: normalizar entre irmãos.
2. MCTS: `√(visitas do pai)` = 0 na primeira descida → nenhuma exploração. Certo: √(N+1).
3. MCTS: avaliava o pai depois de expandir. LATS avalia **os filhos**.
4. Consolidação SQL: `(1.0 - match[1]) < 0.15` usa `confidence_score` como se fosse distância → funde memórias não relacionadas. Certo: `SELECT embedding <=> q AS dist`.
5. Cypher: `(e2)-[:CHRONO_NEXT]->(e1)` aponta para trás no tempo.
6. Decaimento aplicado **multiplicando o banco todo dia** com Δt desde o último acesso → decai em dobro, e o expurgo apaga (viola a Lei da Monotonia). Certo: calcular na leitura e arquivar em vez de apagar.
7. Hebb `W += η·R` sem limite → explode. Certo: saturado, `w += η(1−w)`.
8. Confiança `+0,05` por acesso → cresce sem relação com acerto. Certo: média Beta `(sucessos+1)/(usos+2)`.

## Fase 3 — cruzamento com o Cérebro

| Técnica (referência real) | Estado antes | Agora |
|---|---|---|
| Recuperação recência×importância×relevância (Generative Agents, 2023) | 🔧 grep sem ranking | ✅ `memoria_viva.py buscar`, no recall de **cada** prompt |
| Associação por grafo / PageRank personalizado (HippoRAG, 2024) | 🆕 os 1.559 links entre memórias não eram usados | ✅ traz o vizinho associado (↔) que não tem a palavra |
| Hebb saturado sobre co-uso com sucesso | 🆕 | ✅ `episodio`. Não há benchmark publicado de Hebb em agente LLM: é aposta de engenharia e está declarada como aposta |
| Buffer episódico + reflexão verbal (Reflexion, ExpeL, LATS) | 🔧 02-MEMORIA manual | ✅ `episodio --licao`; `consolidar` só promove lição repetida (≥2) |
| Decaimento de Ebbinghaus | 🆕 | ✅ calculado na leitura; `frias` lista para arquivar, nunca apaga |
| LLM-MCTS / LATS com verificador | 🆕 | ✅ `arvore.py` + `/arvore` |
| Estagnação → mais temperatura + outro domínio | 🆕 | ✅ dentro do `arvore.py` (versão real da "entropia controlada") |
| Red × Blue em co-evolução | ✅ já existe | `auditor`/`qa`/`/adversarial` — quem escreve não aprova |
| Auto-modificação do próprio código | ✅ já existe, em versão segura | §7: repetição vira skill/hook, o CI é a função de aptidão. É o desenho da Darwin Gödel Machine: variante só fica se passar no teste |
| Evolução de prompt (GEPA, Promptbreeder) | ⏳ não instalado | Exige um conjunto de avaliação com nota real. Os candidatos são o eval do Stanford T11 e o `/cacar-produto`. Sem avaliação, vira teatro |

## Fase 4 — virou ativo (e foi medido)

| Ativo | Teste | Medição real |
|---|---|---|
| `.claude/helpers/cerebro/memoria_viva.py` | 19 testes | 424 memórias · 1.559 links · busca em 108 ms com cache (545 ms sem) · recall completo em 215 ms |
| `.claude/helpers/pensar/arvore.py` + `/arvore` | 15 testes | Jogo 24 ao vivo (OpenRouter): 3 resolvidos com prova exata (4 7 8 8 · 1 5 5 5 · 2 3 5 12), 1 impossível corretamente **não** declarado (1 1 1 1), 1 falha (3 3 8 8). US$ 0,003–0,012 por rodada |
| `recall.sh` | `_teste.sh` 0 falhas | numa pergunta sobre o gargalo da campanha, o 1º resultado foi a memória de preço de mercado do dia |

**A lição mais cara da sessão (virou teste de regressão):** na 1ª execução real, o **juiz LLM deu nota 1,0 a um
Jogo 24 errado** (o passo reusava um número já consumido), e a busca declarou "solução verificada". Houve três
correções: passo estrito, poda exata dos números restantes, e a regra de que o juiz nunca fecha sozinho quando existe
verificador. Sem verificador, o rótulo é "aprovada pelo juiz — NÃO verificada". É a tese do CS329A provada em
casa: **o gargalo é verificar, não gerar.**

## O que NÃO presta (honestidade)

- Mexer em pesos (GRPO, DAPO, SFT, RLEF de treino): o Cérebro roda Claude por API e não tem gradiente. Vale o equivalente inferencial.
- pgvector/Neo4j para 424 memórias: é infraestrutura sem ganho. BM25 + grafo de links resolve em 108 ms e roda sem servidor. Reavaliar a partir de ~10 mil memórias ou quando houver busca multimodal.
- "Consciência sintética", "três linhas temporais", "compilador vivo": não existem como engenharia.

## Próximo passo que aproxima receita

Nenhum destes ativos vende sozinho. Eles deixam mais barato e mais certo o trabalho que vende. Os três usos
mais diretos:
1. **`/cacar-produto aberto`**, a pendência nº 1. O `memoria_viva` agora traz para dentro da caçada os números reais de campanha que vivem no mestre privado.
2. **Pricing e oferta com `/arvore`** sempre que houver verificador numérico, por exemplo a conta de margem e payback do gate G5 (N1–N5).
3. **Registrar episódio** ao fim de cada missão de venda. Sem isso, as sinapses não aprendem e o motor fica só com o ranking.

---

## Fase 5 — CMU 11-768 lido na íntegra e instalado (27/09, tarde)

Os vídeos estão bloqueados na nuvem: o YouTube pede PO Token para IP de datacenter. Testei os clientes default, mweb, tv,
android_vr, ios e web_safari, além de Jina, youtubetranscript, Invidious e Piped. Por isso a fonte foram os
**10 PDFs oficiais de slides** (666 páginas), a melhor fonte segundo o método do Diretor, Fase 1A. A fala das aulas vem
pela missão JARBAS no Mac mini (`transcrever-youtube.sh`). A ficha completa está no mestre:
`ESTUDO/fichas/cmu-11-768-agentes.md`.

| Técnica da aula | Instalado em | Medição / prova |
|---|---|---|
| Menos memória é melhor (aula 4, ReasoningBank: 1 experiência 49,7 contra 4 experiências 44,4) | recall: prompt sem palavra-chave nem transcript não injeta nada; palavras de conversa ignoradas; índices `MEMORY*.md` fora do grafo (eram hub em toda busca) | "ok, pode seguir" → saída vazia; ponteiros mantidos em k=8 (recall 0,936 contra 0,901 com k=5), porque o achado vale para experiência inteira, não para ponteiro de 1 linha |
| Buscar com o raciocínio atual (aula 10, AgentIR) | `memoria_viva.py buscar --transcript/--contexto`; `recall.sh` passa o `transcript_path` | a pergunta vaga "e agora, próximo passo?" passou a trazer `diretor-aprendizado` em vez de ruído |
| Verificar citação lendo a fonte (aula 10, FACT) | agente `verificador-citacao` + trava em `/cacar-produto` e `cacador` | conteúdo médico só com 100% SUSTENTA |
| Plan → Search → Reflect → Search again (aula 10) | `/cacar-produto` Fase 1b + `cacador` | conclusão limitada ao que foi testado |
| "You just signaled task completion. Let's pause and think again." (aula 5, Test-Time Interaction) | `lembrar-memoria.sh` (Stop): bloqueia **uma vez** se há trabalho não commitado | testado: bloqueia → segunda passagem libera (`stop_hook_active`) → stdin vazio não trava |
| Vantagem relativa (aula 9, GRPO: Â = r − média) | `hebb()`: o sucesso esperado quase não reforça, a surpresa reforça | teste: o 50º sucesso seguido muda menos que 1/10 do primeiro |
| Falha vira estratégia (aula 4, ReasoningBank: 46,5 → 49,7 com falhas) | prompt lobo frontal ganhou o campo `evitar` | — |

**Bug achado pelo teste novo:** com `vagas_assoc=0`, os vizinhos completavam as vagas que sobravam. Corrigido.
**Avaliação final (gabarito, 171 casos):** BM25 puro MRR 0,792 · recall@5 0,901 → pilha calibrada **0,803 · 0,906**.
**Testes:** memória viva 27 · árvore 15.

**Ainda não instalado (próxima rodada, na ordem):**
1. Checkpoint com âncoras literais no PreCompact (aula 3).
2. Rubrica ponderada auditada (aula 10).
3. Log de uso de skill com poda estilo TroVE (aula 4).
4. Calibrar o juiz LLM contra gabarito humano (79% contra 80% de concordância entre especialistas) e registrar a taxa de erro por provedor no conselho (aula 2: até 15,1%).
5. Levar o `memoria_viva` para o hook de recall do Mac.
