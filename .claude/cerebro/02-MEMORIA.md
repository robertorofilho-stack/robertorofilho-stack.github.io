# 📓 Memória

> Ordem cronológica inversa — mais recente no topo.
> Formato fixo. Sem prosa: isto é para consulta rápida, não para leitura.

---

## 2026-09

### 2026-09-10 — v4 do índice instalado no mestre; soberania de motor e portão do git

**Instalado por união:** `fundir-indice.py` v4 + `verificar-indice.py` + `testar-fundir.py` em
`~/.claude/helpers/cerebro/`; o v3 foi para `arquivo/fundir-indice-v3-2026-09-10.py`, não apagado.
Prova antes de instalar, sem gravar: 20 testes OK · simulação com os dois índices reais **244/244**
· `verificar-indice`: 0 órfãs. Sync levou os 3 para `claude-config/helpers/cerebro/` (`c96d37e`).

**Silêncio removido:** o `|| true` da linha 77 do `sync-backup.sh` virou log explícito, e o
verificador roda **depois de cada** uma das 4 chamadas do fundir (2 em cada script), com
notificação do macOS em falha — testado com órfã forjada: notificou e logou; índice limpo é mudo.

**Prova em produção:** o primeiro sync com o v4 reescreveu 223 linhas do índice e fechou
**244 → 244 ponteiros, zero perda**. Era exatamente aqui que o v3 comia 4.

**Soberania de motor:** seção nova em `cerebro-master-pacote/governanca/AGENTS.md` e em
`~/.codex/AGENTS.md` — o Codex LÊ `claude-config/**` e `~/.claude/**`, nunca escreve; mudança vai
como proposta em `codex-config/PROPOSTAS-PARA-O-CLAUDE.md`. Simétrico do outro lado.
**Portão:** `pre-commit` local em `cerebro-backup` bloqueia commit em `claude-config/**` sem
`CLAUDECODE`/`CEREBRO_SYNC=1`. Testado: commit cru **bloqueado**, sync real **passou** (`935dc1d`).
O hook mora em `.git/hooks`, não viaja no push — o Mac mini não é afetado.

**Links:** [[00-MAPA]] [[05-DECISOES]]

---

### 2026-09-10 — Índice do Cérebro: fusão por LINK e guarda que recusa perda (fundir-indice.py v4)

**Contexto:** o Mac provou involução em 1 h: `cd7e288` (união, 244 links) → `8328f15` (auto-backup 4 min depois,
240). Reproduzi aqui com o índice real e o script original (`local` pré-união 225 + `repo` unido 244 → v3 grava
**239**, perdendo exatamente `clickmax-plataforma`, `lei-parcela-minima-6-reais`, `projeto-youtube`,
`rede-casa-mapa`). Causa: os 4 vivem em linhas **agrupadas** (ex.: "LEIS SEM NEGOCIAÇÃO" carrega 2 links) e o
v3 deixa a linha do local vencer inteira; e `if t0 in tem: continue` pula linha cujo 1º link já apareceu.
**Feito (satélite, `.claude/helpers/cerebro/` — mesmo caminho do mestre, a ponte é um `cp`):**
- `fundir-indice.py` v4: unidade de fusão = link; local vence texto só quando cobre os mesmos links; superset
  vence; cada lado com link exclusivo → as duas linhas ficam. **Guarda pós-condição independente** (re-lê os
  links do texto de saída): se um ponteiro sumiria, NÃO grava, lista em stderr, exit 2. Escrita atômica.
  `--simular` (só relata) e `--simular-perda X` (prova o guarda). Idempotente.
- `verificar-indice.py`: memória `.md` sem ponteiro no `MEMORY.md` (fora de REVOGADAS) = exit 1; ponteiro
  quebrado = aviso (`--estrito` falha). 25 ms em 246 memórias. Ligado ao `bootstrap.sh` (3c), ao
  `carregar-cerebro.sh` (seção 🔴 só quando há perda) e ao `/manutencao`.
- `testar-fundir.py`: 20 testes (bug real reproduzido em forma sintética, revogadas, vazio, idempotência,
  guarda em disco, CLI, verificador) — passo novo no `saude.yml`.
**Prova no índice real (origin/master):** cenário do incidente → 243/243 preservados dos dois lados, saída
idêntica nos dois arquivos, `fundir(X,X)==X`; cenário de hoje (`44718ea` 244 × `b10a61e` 239) → 0 perdas em
qualquer ordem de argumentos; guarda no real → exit 2 e arquivos intactos; verificador → 0 órfãs (as 3 sem
ponteiro estão em REVOGADAS), 1 quebrado (caminho `../../../CEREBRO-MASTER-PACOTE/…`).
**Limite honesto:** o mestre só fica protegido quando o Claude do Mac copiar os 3 arquivos para
`~/.claude/helpers/cerebro/` e trocar o `|| true` do `sync-backup.sh` por log — prompt entregue.
**Também:** rebase limpo de `24108b7` (soberania de motor) sobre os 3 commits do Mac; ponte verificada no
mestre (128 skills, 9 agentes em `agents-user/`, `satelite-projeto-supremo.md`, linha 33 do índice).
**Links:** [[05-DECISOES]] [[03-ATIVOS]] [[APRENDIZADO-PROJETO-SUPREMO]] #26

---

### 2026-09-10 — União satélite → Cérebro executada (e prova de que a involução é real)

**Feito:** memória `satelite-projeto-supremo.md` gravada no cofre do mestre (+1 linha no índice,
seção SETUP) com o inventário do satélite, a precedência (Constituição, 4 Leis, gate G5 e diretores
vencem; capacidades somam) e a tabela de equivalências do [[00-MAPA]].
**União:** 17 skills + 9 subagentes copiados com `cp -n` (nunca sobrescreve) para `~/.claude`:
111→128 skills, 143→152 agentes, **zero colisões** (a `cripto` já virava `analise-cripto`).
`_capacidades.sh`: ✓ 40 capacidades, nenhuma perdida. Sync: commit `44718ea` no origin.

**Achado grave:** os 4 links que eu tinha restaurado às 10:28 **sumiram de novo até as 11:17** —
`clickmax-plataforma`, `lei-parcela-minima-6-reais`, `projeto-youtube`, `rede-casa-mapa`.
O `sync-backup.sh` reescreveu o índice com a cópia do cofre e o bug do `fundir-indice.py`
(vence a LINHA inteira, não o link) engoliu os agrupados. Restaurados; agora 244 no índice.
**Isto é involução acontecendo em uma hora** — exatamente o que a Lei da Monotonia proíbe.
Os arquivos `.md` nunca sumiram; some só o ponteiro no índice, então a memória fica órfã e invisível.

**Próximo passo (agora prioritário):** consertar `fundir-indice.py` para fundir **por link dentro
da linha** e falhar alto quando descartar um link. Enquanto não consertar, todo sync entre os 2
Macs pode apagar ponteiro de memória em silêncio.

**Links:** [[00-MAPA]] [[05-DECISOES]]

---

### 2026-09-10 — Descoberta do Cérebro mestre e unificação (satélite ⊂ mestre)

**Contexto:** no primeiro prompt do MacBook, o Claude local inspecionou `~/Claude/cerebro-backup` e fundiu
o índice dos dois Macs (243 memórias, zero perda). Eu não sabia que existia: repo privado, fora do escopo.
**Resultado:** CLAUDE.md §0b (mestre vence) + 4 Leis e gate G5 copiadas · `recall.sh` busca no mestre
quando presente · `carregar-cerebro.sh` avisa · `/cripto` → `/analise-cripto` · mapa de equivalências em
[[00-MAPA]] · kit com os dois sistemas.
**Aprendizado:** construí em silo por falta de visibilidade. Regra nova: antes de construir infraestrutura,
`list_repos` e perguntar "o que já existe?". Ver [[APRENDIZADO-PROJETO-SUPREMO]] #25.
**Próximo passo:** o Claude do Mac registra o satélite na memória do mestre (prompt entregue ao operador).
**Links:** [[05-DECISOES]] [[00-MAPA]]

---

### 2026-09-10 — Cérebro dos 2 Macs diverge: conserto e limitação do fundir-indice

**Contexto:** SessionStart avisou conflito em `claude-config/memory/MEMORY.md`. Air estava
**3 commits à frente e 52 atrás** do mini em `cerebro-backup`. Merge abortado, árvore limpa —
parecia resolvido, não estava. Só o índice conflitava (3 hunks).

**Correção:** `fundir-indice.py` (união por link) → 239 memórias, +37 recuperadas.

**Aprendizado (novo, não estava documentado):** a limitação do `fundir-indice.py` é maior do que
o docstring diz. Ele funde **por link**, mas a unidade que vence é a **linha inteira**. Linha do
índice que agrupa vários links com " · " e cujo link-âncora existe nos dois lados: vence a linha
local e **os links extras do outro lado somem silenciosamente** — sem aviso, sem contador.
Aconteceu com 4: `clickmax-plataforma`, `lei-parcela-minima-6-reais`, `projeto-youtube`,
`rede-casa-mapa`. Reinseridos à mão.

**Verificação:** diff de conjuntos de links dos dois lados contra o fundido — **0 perdidos de
cada lado**, 243 memórias. Commit `cd7e288`, `master` alinhado ao origin.

**Número:** 159 linhas (Air) + 133 (mini) → 243 memórias indexadas.

**Próximo passo:** o `fundir-indice.py` deveria fundir **por link dentro da linha**, não escolher
a linha inteira — ou no mínimo imprimir os links descartados em stderr. Hoje ele reporta sucesso
enquanto perde memória. Vale consertar antes do próximo sync entre máquinas.

**Links:** [[05-DECISOES]] · índice em `cerebro-backup/claude-config/memory/MEMORY.md`

---

### 2026-09-10 — Primeiro CI vermelho: artefato gerado versionado colidiu com a fixture

**Contexto:** `saude.yml` disparou sozinho no push. `infraestrutura` verde (hooks, frontmatter,
JSON no Ubuntu do GitHub). `radar` vermelho em 1 s: "saas-gerados/… já existe".
**Causa:** commitei o projeto gerado; em CI o destino já existia e o gerador recusou.
**Correção:** `radar/saas-gerados/` fora do git (artefato, não fonte); `--fixture` idempotente
(remove e regenera); `recall.sh` ignora notificações de sistema.
**Aprendizado:** o sistema de saúde pegou um erro meu na primeira execução — é para isso que existe.
Ver [[APRENDIZADO-PROJETO-SUPREMO]] #24.
**Links:** [[03-ATIVOS]]

---

### 2026-09-10 — Persistência total: recall, saúde, manutenção, backup e kit

**Contexto:** operador: "não quero te perder; quero que use todo o cérebro em cada missão e que
esteja sempre se atualizando". Resposta em código, não em promessa.

**Decisão/Resultado:**
- `recall.sh` (UserPromptSubmit): a cada prompt, extrai palavras-chave e injeta o que o cérebro
  já sabe — 1.441 chars em 38 ms no teste. Determinístico.
- `_teste.sh` + `_validar-frontmatter.sh`: suíte que simula máquina sem jq/node/python. 0 falhas.
- `saude.yml`: toda segunda + a cada push na infra — hooks, skills, config, radar (audit, fixture,
  build, QA no Chromium, varredura). Abre issue se quebrar.
- `/manutencao` + routine semanal: consolida memória, repetição → skill, dependências, changelog.
- `backup.sh`: git bundle (todas as branches) + `~/.claude` → Drive/iCloud. Restauração testada:
  16 skills, 2 branches.
- `KIT-RECUPERACAO.md` no repo e como Google Doc no Drive do operador.
- CLAUDE.md §0 "Protocolo de missão": recall → inventário → arsenal → executar → gravar.
- `gerar-saas.ts --fixture`: CI não depende de o radar achar oportunidade. Build + QA 13/13.

**Número:** 5 hooks, 17 skills, 2 workflows, 3 scripts de operação. Backup: 5,4 MB.

**Aprendizado:** "salvar o Claude" não é um arquivo — é repositório (tudo que foi construído) +
conta (conectores, preferências) + gerenciador de senhas (chaves). Cada um com seu backup.
Ver [[05-DECISOES]].

**Próximo passo:** no Mac: clone → bootstrap → `bash .claude/backup.sh` → crontab. Mergear na main
quando quiser o cron do radar.

**Links:** [[00-MAPA]] [[03-ATIVOS]] [[05-DECISOES]]

---

### 2026-09-10 — Portabilidade para o MacBook garantida e testada

**Contexto:** operador perguntou se o cérebro estaria no Mac. Auditoria achou 2 bugs que
degradariam em silêncio no macOS: hooks exigiam `jq` (não vem no Mac) e `grep 'a\|b'`
(extensão GNU, BSD grep ignora).

**Decisão/Resultado:** `_json.sh` com cadeia jq → node → python3 → `{}`; `grep -E`.
Testado simulando máquina sem jq, sem node e sem nada: 13 checagens, 0 falhas.
`.claude/bootstrap.sh` — um comando prepara qualquer máquina e testa o hook do cérebro.
Seção "Continuar no MacBook" em [[00-MAPA]].

**Aprendizado:** o próprio `guarda.sh` bloqueou o comando que reescrevia o `guarda.sh` —
o texto do padrão proibido estava no heredoc. Arquivo de hook se escreve pela ferramenta
de arquivo, não por bash. Ver [[APRENDIZADO-PROJETO-SUPREMO]] #20.

**Próximo passo:** no Mac: clone → checkout da branch → `bash .claude/bootstrap.sh` → `claude`.

**Links:** [[00-MAPA]] [[05-DECISOES]]

---

### 2026-09-10 — Radar de lucro + fábrica de micro-SaaS construídos e testados

**Contexto:** Operador pediu "Modo Daemon": varrer mercado, detectar dor, gerar micro-SaaS
com Pix + PayPal, testar no navegador, publicar. Sem intervenção humana.

**Decisão/Resultado:** Construído `radar/` completo e **provado de ponta a ponta**:
radar (5 fontes) → oportunidades.json → gerar-saas → Next 16 + Tailwind 4 → build →
QA adversarial no Chromium → APROVADO (12 checagens). Pix EMV com CRC validado contra
vetor canônico `29B1` + conferência independente em Python. Daemon 24/7 = GitHub Actions
cron (`.github/workflows/radar.yml`), não máquina ligada.

**Número:** 1ª varredura real: 44 sinais brutos → 38 grupos → 1 oportunidade acima do corte
(HN, score 45, MÉDIA). Google Trends RSS, HN Algolia e Stack Exchange respondem de graça.
Reddit bloqueia IP de datacenter (precisa OAuth). X exige API paga (~US$200/mês).

**Aprendizado — bugs que o sistema achou em si mesmo (loop de erro zero funcionando):**
1. Tendência sem dor pontuava acima de dor real ("lionel messi" 46 vs dor HN 45) → trava de realidade
2. next@15.1.0 tinha CVE → template sobe para 16.3.4, 0 vulnerabilidades
3. `>` de citação do HN quebrava JSX no build → sanitizador no gerador
4. QR via serviço externo vazava payload de pagamento → geração local (data URI)
5. Playwright preenchia antes do React hidratar → helper que espera hidratação
6. Porta fixa colidia com servidor órfão → QA conectava no build velho → porta dinâmica
7. `pkill -f "next start"` matava o próprio shell (auto-match) → padrão `next[ ]start`

**Veredito das 7 "formas de renda" propostas:** grants ✅, bug bounty ✅ (difícil), fábrica
de micro-SaaS ✅ (construída). Crowdfunding em massa ❌ (spam/fraude), sorteios com IP
residencial ❌ (fraude), gêmeos digitais em pesquisa paga ❌ (fraude), sniper de domínio
de marca ❌ (cybersquatting). Para médico com CRM, a assimetria é brutal: o ganho é pequeno
e a perda é a licença. Ver [[05-DECISOES]].

**Próximo passo:** preencher `radar/.env` (PIX_KEY) e rodar `npm run gerar -- --auto` numa
oportunidade ALTA quando o cron detectar. Implementar o núcleo da ferramenta no bloco marcado.

**Links:** [[03-ATIVOS]] [[04-PLAYBOOKS]] [[05-DECISOES]] [[APRENDIZADO-PROJETO-SUPREMO]]

---

### 2026-09-10 — PROJETO SUPREMO: infraestrutura de agente instalada

**Contexto:** Repositório do site médico não tinha nenhuma infraestrutura de agente.
Toda sessão começava do zero, sem memória, sem playbook, sem verificação.

**Decisão/Resultado:** Construída a camada completa de agente sobre o repositório:
CLAUDE.md como constituição operacional · 9 subagentes especializados ·
14 skills executáveis · 3 hooks (memória, guarda, lembrete) · arsenal MCP ·
este vault de memória persistente.

**Número:** 0 → 28 arquivos de infraestrutura. Base técnica extraída de 7 repositórios
e da documentação oficial de Skills, Subagentes, Hooks e MCP.

**Aprendizado:** O ganho real não veio de "aprender" conteúdo — veio de transformar
método em arquivo que carrega sozinho toda sessão. Conhecimento em conversa evapora;
conhecimento em arquivo compõe.

**Próximo passo:** Rodar `/cacar-produto aberto` para a primeira caçada real de infoproduto.

**Links:** [[APRENDIZADO-PROJETO-SUPREMO]] [[04-PLAYBOOKS]] [[05-DECISOES]]

---
