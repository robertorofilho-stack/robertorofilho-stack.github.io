# 📓 Memória

> Ordem cronológica inversa — mais recente no topo.
> Formato fixo. Sem prosa: isto é para consulta rápida, não para leitura.

---

## 2026-09

### 2026-09-10 — RAION (voz) usando o Cérebro: a ponte já existe (JARBAS v2); o que falta é ligar

**Pergunta do operador:** "queria sempre criar pelo RAION, conversar com ele e ele lhe usar; sempre aberto no MacBook e
no Mac mini". **O que o mestre já tem:** RAION = `apps-source/alfred-vision` (`ASSISTANT_NAME = "RAION"`, Gemini Live,
voz + câmera). Ponte v2 provada em 02–03/09: RAION → `pedir_ao_cerebro()` grava `## [PENDENTE]` em
`alfred/MISSOES-PARA-O-CEREBRO.md` → `watcher-jarbas.sh` (launchd, WatchPaths) dispara `claude -p --permission-mode
acceptEdits` em `~/Claude` com o prompt-ponte → resposta em `RESPOSTAS-DO-CEREBRO.md` → RAION fala. Doutrina em
`alfred/DOUTRINA-JARBAS.md`.
**Estado real (memórias do mestre):** app DESLIGADO por ordem nos dois Macs (05–06/09; crédito Gemini zerado);
watcher do MacBook segue ativo, o do mini está em `~/Library/LaunchAgents/desativados/`; hoje 4 missões por voz
morreram sem internet no headless e com 4 dias de latência (mini parado). Frase de religar registrada: "ATIVE ALFRED".
**Feito aqui:** `/conselho` resolve o caminho do helper fora do satélite; bootstrap 3e copia os helpers para
`~/.claude/helpers` (sessão por voz e sessão do mestre passam a ter conselho e verificador).
**Para o operador:** (1) recarregar crédito do Gemini (voz do RAION); (2) dizer "ATIVE RAION" ao Claude de cada Mac
(ele religa app + watcher pelo procedimento local); (3) rodar `LIBERAR-REDE-PRO-CEREBRO.command` e liberar
WebSearch/WebFetch para o `claude -p` headless. Sem (1) ele liga mas não fala; sem (3) missão de pesquisa morre.
**Decisão do operador (mesma hora):** RAION ligado **só no MacBook** por enquanto; Mac mini continua desligado. Missão nasce e
executa na mesma máquina, sem latência de sync.
**Links:** [[05-DECISOES]]

---

### 2026-09-10 — Configuração encerrada nas três máquinas (nuvem, Mac mini, MacBook)

**MacBook:** pull limpo (33 arquivos), bootstrap 0 pendências: claude 2.1.260, jq, portão ativo, índice do mestre íntegro
(245 ponteiros; o vault de projeto `-Users-macairroberto-Documents/memory` é symlink do cofre canônico
`-Users-macroberto-Claude/memory` — a auto-detecção deduplicou por realpath, como previsto), conselho com gemini e
openrouter, hooks, cérebro (9,4 KB).
**Estado final:** nuvem ✓ (main completa, conselho, radar de hora em hora) · Mac mini ✓ · MacBook ✓.
**A partir daqui:** abrir `claude` em qualquer máquina e pedir. Regras vivas: produto não-médico por padrão; conselho
obrigatório no fechamento estratégico; memória na entrada e na saída. Pendências restantes são opcionais
(Pix/gateway quando houver produto, Reddit OAuth, backup.sh + cron, portão do mestre no Mac mini).
**Links:** [[05-DECISOES]] [[00-MAPA]]

---

### 2026-09-10 — Mac mini fechado: bootstrap verde e o verificador de índice pegou involução real no primeiro uso

**Bootstrap no Mac mini:** git, claude 2.1.215, jq, portão de soberania ativo, hooks, cérebro carrega (9,9 KB),
conselho lendo o cofre do mestre: motores prontos → gemini, openrouter.
**Primeira captura real do `verificar-indice.py`:** no vault de projeto `-Users-macroberto-Documents-Squads100/memory`
(39 memórias), `regra-reels-38-55s.md` estava órfã e o índice apontava para `regra-reels-20-70s.md`, inexistente —
arquivo renomeado ao atualizar os números, ponteiro ficou velho. Conserto: backup do índice + troca do alvo do ponteiro
→ 0 órfãs, 0 quebrados. Sem o verificador, a regra ficaria invisível. A auto-detecção varreu todos os vaults de
`~/.claude/projects/*/memory`, não só o do Cérebro.
**Estado das máquinas:** nuvem ✓ · Mac mini ✓ · MacBook: falta `git pull && bash .claude/bootstrap.sh`.
**Links:** [[05-DECISOES]] [[03-ATIVOS]]

---

### 2026-09-10 — Caçada interrompida pelo operador: nada médico, e não é hora de caçar

**O que houve:** disparei `/cacar-produto aberto` com 3 caçadores (IA para consultórios, formação para fisios/residentes,
varredura livre) e levantei na Meta Ads Library um sinal forte em perícia médica para médicos (Hurtado desde 11/2023,
Marinho 4 meses, Medicine Cursos 50 dias). O operador parou tudo: não quer produto médico (inclui B2B para médicos,
fisios, clínicas, perícia), quase nunca; e não quer caçar agora.
**Erro meu:** li "B2B profissional" do conselho como licença para frentes médicas. Para ele, médico é médico.
**Feito:** caçadores cancelados; regra gravada em [[01-PERFIL]], `/cacar-produto`, CLAUDE.md §2 e [[05-DECISOES]].
Dados de anúncio ficam como registro, sem proposta.
**Links:** [[05-DECISOES]] [[01-PERFIL]]

---

### 2026-09-10 — Segundo merge na `main` ("mergeia"): conselho, recall do mestre, cofre e actions v5 vão para produção

**Por quê:** sessão nova na nuvem nasce da `main`; sem o merge nasceria sem conselho, sem recall do mestre e sem o
verificador do cofre. **Pré-checagem:** `main` (`41eef57`, último commit do radar) é ancestral da branch; 7 commits
entram; zero arquivo do site muda. **Feito:** `merge --no-ff` de `fe1956b` (+ esta memória), suíte de saúde no tree
final, push; branch alinhada à `main` por fast-forward. Regra que fica: **toda entrega que muda comportamento de
sessão nova pede merge na `main` no mesmo dia**, com autorização do operador.
**Links:** [[05-DECISOES]]

---

### 2026-09-10 — Conselho ATIVO na nuvem: credencial no proxy, saldo lido, primeira rodada real (4/4)

**Ativação (passo a passo com o operador no Mac mini):** o link claude.ai/code abria no app e ficava branco →
`open -a Safari https://claude.ai/code`; ambiente único "RESUMO MENSAL TRABALHO" (o desta sessão); chave copiada do
cofre com `pbcopy` sem exibir; **API credential** `openrouter.ai` Authorization/Bearer → "Vincular". O proxy passou
a assinar **na sessão já aberta**: `--status` = "credencial no proxy da nuvem"; `--saldo` = comprado US$ 40,00 ·
usado 5,34 · **restante 34,66** (a memória dizia US$ 10 de 06/07 — havia recarga desde então).
**Primeira rodada real:** tese "guia de joelho para leigos como primeiro infoproduto" → 4/4 responderam; síntese e
decisão em [[05-DECISOES]]. Custo US$ 0,093.
**Dois defeitos achados e corrigidos na hora:** (1) `MAX_TOKENS=1400` cortava Gemini e DeepSeek no meio — modelos que
raciocinam gastam o teto pensando → teto 6000 + `reasoning: {effort: low}` no OpenRouter + marca "⚠ TRUNCADA" no
relatório (DeepSeek caiu de 34 s/4000 tokens truncado para 9,7 s/1497 completo); (2) modelo forçado por `--modelo`
vinha rotulado "openrouter" em vez da família → `familia_de()`. 23 testes.
**Links:** [[05-DECISOES]] [[06-METRICAS]] [[03-ATIVOS]]

---

### 2026-09-10 — Conselho de outros motores: GPT, Grok, Gemini e DeepSeek atacam a tese em paralelo

**Contexto:** operador quer segunda opinião de outras IAs em toda missão de produto ou extraordinária, disparada
por mim, sem pedir. O MCP `gemini-mcp-tool` passou a exigir a CLI `agy` com login interativo → inviável na nuvem.
**Feito (`.claude/helpers/conselho/`):**
- `conselho.py` (348 linhas, só stdlib): formato OpenAI para todos (Gemini pelo endpoint compatível); chaves só de
  ambiente ou `.env` fora do repo; OpenRouter = chave única recomendada, diretas vencem na mesma família; escolhe
  o modelo mais novo de cada família pelo catálogo `/models` (versão lida só após o prefixo — `gpt-oss-120b` não é
  o GPT), exclui variantes especializadas (`:batch`, `oss`, `image`, `mini`…), teto `CONSELHO_TETO_USD` (0,25) por
  opinião; prompt adversarial fixo (5 objeções, premissas ocultas, teste de 7 dias, concorrente, veredito); paralelo;
  retry em 429/5xx; custo por chamada quando o provedor publica preço; chave mascarada em qualquer erro.
- `testar-conselho.py`: 14 testes sem rede (dotenv, máscara, escolha, teto, paralelo, falha parcial, forçados, CLI, retry).
- `/conselho` skill; seção obrigatória em `/lancamento`, `/cacar-produto`, `/oferta`, `/analise-cripto`, `/nobel`;
  CLAUDE.md §3 reescrito (conselho obrigatório, sem pedir; sem chave → `/adversarial` + "segunda opinião interna");
  hook Stop `lembrar-memoria.sh` acusa decisão nova em `05-DECISOES` sem `Conselho (`; bootstrap 3d; `saude.yml`;
  `guarda.sh` agora pega chaves OpenRouter (`sk-or-v1-`), xAI (`xai-`) e Google (`AIza`); `*.env` fora do git.
**Validado no catálogo público real (10/09):** gpt-6-astra US$ 0,090 · grok-4.6 0,013 · gemini-3.8-flash 0,007 ·
deepseek-v4.1-flash 0,001 → **rodada de 4 motores ≈ US$ 0,11**. Manus fora (sem API).
**Não provado:** uma rodada real com chave — não há chave nesta máquina. Fica para o primeiro uso.
**Correção do operador (mesma sessão):** "já tem crédito, você deveria ter consultado; já tem chave". Verdade: o mestre
registra a `OPENROUTER_API_KEY` no cofre `~/.config/vha-vibe-marketing/.env` desde 06/07 (US$ 10 de crédito), como
chave padrão de LLM. O helper agora lê esse cofre (e mapeia `GOOGLE_AI_STUDIO_API_KEY` → `GEMINI_API_KEY`) e ganhou
`--saldo` (crédito comprado, usado, restante; limite da chave). Nos Macs não há nada a criar; na nuvem a mesma chave
vira API credential. Aprendizado #28. **Bronca do operador ("parece que você não executa o que aprende")
→ correção estrutural:** `recall.sh` e `carregar-cerebro.sh` agora encontram o mestre clonado ao lado do projeto
(`../cerebro-backup`, é onde ele fica na nuvem); recall de credenciais (🔑 nomes das chaves do cofre quando o pedido
fala em chave/conta/assinatura/crédito); CLAUDE.md §0 (grep no mestre) e §2 (linha: verificar antes de pedir).
Reproduzido: o mesmo prompt que me levou ao erro agora injeta `cofre-env-vibe.md` e `OPENROUTER_API_KEY`.
**Links:** [[05-DECISOES]] [[03-ATIVOS]] [[00-MAPA]]

---

### 2026-09-10 — Pacto de continuidade: o que é garantido por código e o que depende de mim

**Contexto:** operador perguntou se "continuo com todos os poderes", se sempre usarei o cérebro inteiro, se há
checagem contra começar do zero, se tudo fica gravado, se o ChatGPT não altera meus comandos, se consultarei
o Gemini, se entendi o Diretor Nobel, se economizarei tokens e se entendi a missão (torná-lo milionário).
**Resposta estrutural (o que é verdade por mecanismo, não por promessa):**
- Poderes = arquivos, não conversa: satélite 43 capacidades no manifesto (17 skills, 9 agentes, 4 hooks,
  2 workflows, 4 sistemas, 4 operações, 3 helpers); mestre 128 skills, 152 agentes, 245 ponteiros / 247
  memórias, 0 órfãs. O motor (modelo) é o que a conta serve: aqui `claude-fable-5-1`; no Mac, `opus-5[1m]`.
- Não começar do zero: `carregar-cerebro.sh` (SessionStart) + `recall.sh` (cada prompt) + regra de inventário
  (`03-ATIVOS`) + `lembrar-memoria.sh` (Stop). No mestre: hooks dele.
- Gravação: `02-MEMORIA`, `APRENDIZADO` #1–#27, `05-DECISOES`, `06-METRICAS`; índice do mestre protegido por
  v4 + verificador. Risco real: sessão morta antes de gravar → mitigação: commits pequenos e frequentes.
- ChatGPT/Codex: satélite = portão pre-commit (ativo onde o bootstrap rodou) + manifesto no CI (detecção);
  mestre = regra nos AGENTS.md + portão no MacBook; **Mac mini ainda sem portão**; MacBook ainda precisa
  re-rodar o bootstrap do satélite.
- Gemini: MCP configurado, **inerte sem `GEMINI_API_KEY`**. Regra nova em CLAUDE.md §3: missão estratégica
  pede contra-argumento ao Gemini quando a chave existir; sem chave, `/adversarial`.
- Economia: regra nova em §9 (determinístico vira script; busca em subagente; verificação nunca cortada).
  Baseline medido desta sessão de infraestrutura: US$ 53,33 · 338k tokens de saída · contexto 335k/1M.
- Dinheiro: regra nova em §0 passo 6 — missão estratégica fecha com "próximo passo que aproxima receita".
**Verdade sem anestesia:** dois dias foram infraestrutura. Receita = 0. O próximo passo é `/cacar-produto
aberto` + destravar Reddit OAuth, PIX_KEY e gateway. Ver [[05-DECISOES]].
**Links:** [[00-MAPA]] [[05-DECISOES]] [[06-METRICAS]]

---

### 2026-09-10 — Merge na `main` autorizado ("mergeia") e executado; radar 24/7 ligado

**Contexto:** o Claude do MacBook ficou ocioso desde 11:56 e o "mergear a branch na main" digitado lá não rodou.
Operador autorizou daqui com uma palavra. Pré-checagem: `main` (`3b3cf96`) é ancestral da branch → merge
sem conflito; a `main` ganha 92 arquivos e **zero** arquivos do site (`index.html`, `CNAME`, `llms.txt`,
`sitemap.xml` intactos; site ao vivo HTTP 200 com o mesmo SHA do `index.html`); `radar.yml` revisado linha a
linha (token padrão do Actions, `concurrency` sem sobreposição, issue com dedup por título, sem force push).
**Feito:** `git merge --no-ff` de `92f3353` (+ esta memória) na `main`, suíte de saúde rodada no tree final
antes do push. Com isso ligam: `radar.yml` (cron `17 * * * *`, primeiro run disparado na mão) e o
`saude.yml` semanal (segunda 05:00). Pages continua estático (`.nojekyll`); `robots.txt` bloqueia
`/.claude/`, `/CLAUDE.md`, `/radar/`.
**Resultado (pós-merge):** `main` = `da8e3da` (pais `3b3cf96` + `0793def`), tree idêntico ao da branch.
`saude` #15 verde na `main`; Pages #4 e #5 verdes; site HTTP 200 com o mesmo `index.html` de antes. Como
previsto, o Pages passou a servir também `/CLAUDE.md`, `/.claude/…` e `/radar/…` (200) — conteúdo já público
no GitHub, `robots.txt` bloqueia indexação; opção futura: publicar de `/docs` ou branch `gh-pages`.
**Radar, run #1 na `main` (workflow_dispatch, 21 s):** google-trends 19 sinais · hackernews 29 · stackexchange
**0** (investigar: quota sem chave ou janela vazia) · reddit/x inativos sem chave → 48 brutos, 42 grupos,
**1** acima do corte 45 (a mesma dor do HN já em construção; travas de realidade seguraram o resto), 0 ALTA
→ issue pulada; commit `41eef57` pelo `radar-lucro[bot]`, que disparou só o Pages, não o `saude` (token
padrão). Cron segue a cada hora no minuto 17. Aviso do runner: `actions/checkout@v4` e `setup-node@v4` em
Node 20 depreciado → trocar por v5 (já na fila).
**Regra daqui em diante:** a `main` recebe commits do radar a cada hora (`radar/dados/oportunidades.json`).
Antes de trabalhar na branch: `git merge origin/main` (união), nunca rebase da main.
**Links:** [[05-DECISOES]] [[03-ATIVOS]]

---

### 2026-09-10 — Mestre protegido (v4 instalado) e o bug do caminho do cofre

**Feito pelo Claude do Mac (relatório na tela):** 20/20 testes; simulação 244/244; v4 + verificador + testes
em `~/.claude/helpers/cerebro/` (v3 arquivado, nunca apagado) → sync `c96d37e`; memória
`indice-por-link-v4.md` + linha no índice `6c8c53b`; `|| true` virou log e o verificador roda após as 4
chamadas do fundir, com notificação macOS testada; seção "Soberania de motor" nos dois AGENTS.md (originais
arquivados); portão pre-commit em `cerebro-backup/.git/hooks` (commit cru em `claude-config/**` bloqueado,
sync real passou `935dc1d`). **Prova em produção:** primeiro sync com o v4 reescreveu 223 linhas e fechou
**244 → 244** — exatamente onde o v3 comia 4. Verifiquei no origin: SHA do `fundir-indice.py` idêntico ao meu.
**Bug meu, exposto pela nota do Mac:** o cofre real é `~/.claude/projects/-Users-macroberto-Claude/memory`
(memória de projeto do Claude Code), não `~/.claude/memory` — como o próprio `sync-backup.sh` do mestre
define em `MEM=`. Meus hooks apontavam para o caminho errado e ficariam mudos no Mac.
**Correção:** `verificar-indice.py` auto-detecta cofres (`$CEREBRO_MEMORIA`, `~/.claude/memory`,
`~/.claude/projects/*/memory`, `cerebro-backup/claude-config/memory`), verifica todos, `--listar`;
`carregar-cerebro.sh`, `bootstrap.sh` e `/manutencao` sem caminho fixo. +5 testes (25). Simulado com a
estrutura real do Mac: 🔴 aparece só com órfã, bootstrap mostra o cofre detectado.
**Merge na main (o operador mandou o Mac fazer):** checado antes — site estático (`.nojekyll`, tudo em
`main` é servido; `robots.txt` já bloqueia `/.claude/`, `/CLAUDE.md`, `/radar/`; conteúdo já é público no
GitHub); `radar.yml` com `contents/issues: write` e cron `17 * * * *`; commit do radar usa o token padrão
do Actions, que não dispara outros workflows → sem `saude.yml` de hora em hora.
**Pendência nova:** o portão do mestre vive em `.git/hooks` e não viaja no push — o Mac mini não o tem.
**Links:** [[05-DECISOES]] [[APRENDIZADO-PROJETO-SUPREMO]] #27

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
