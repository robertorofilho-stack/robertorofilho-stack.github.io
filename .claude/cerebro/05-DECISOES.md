# ⚖️ Decisões

> Decisão registrada é decisão que não se refaz do zero. Anotar o **porquê** importa mais
> que anotar o quê — é o porquê que envelhece bem ou mal.

## Tomadas

### 2026-09-10 — Cérebro público separado de cérebro privado
**Contexto:** o repositório do site é público e serve o domínio médico.
**Decisão:** metodologia e playbooks ficam aqui; dado de paciente, financeiro,
credencial e produto não lançado vão para repositório privado separado.
**Alternativa rejeitada:** vault único. Risco inaceitável — dado de paciente em repositório
público é infração ética e de LGPD, não é "descuido".
**Reversível?** Sim, mas o vazamento não. Assimetria decide.

### 2026-09-10 — Infraestrutura de agente no repositório, não em prompt
**Contexto:** conhecimento passado em conversa se perde ao fim da sessão.
**Decisão:** método vira arquivo versionado que carrega sozinho.
**Porquê:** conversa evapora, arquivo compõe. Cada sessão futura começa no topo, não no zero.

### 2026-09-10 — Fronteira legal das "formas de renda autônoma"
**Contexto:** operador propôs 7 mecanismos de renda via agente.
**Decisão:** construir só os legítimos (grants, bug bounty, fábrica de micro-SaaS). Recusar:
crowdfunding em massa por e-mail não solicitado, sorteios com simulação de IP residencial,
"gêmeos digitais" em pesquisa remunerada, registro de domínio de marca alheia para revenda.
**Porquê:** os quatro são spam/fraude/violação de termos ou cybersquatting. Para um médico com
CRM ativo, o ganho é de centavos e a perda é a licença + processo por estelionato (art. 171 CP).
Assimetria decide. Não é moralismo: é conta.
**Reversível?** A decisão sim. A reputação não.

### 2026-09-10 — Fontes do radar: HTTP estruturado, não navegador
**Decisão:** Google Trends RSS + HN Algolia + Stack Exchange via HTTP; Playwright só no QA.
**Porquê:** endpoint estruturado é 10x mais rápido e não quebra quando o DOM muda.
X exige API paga; Reddit exige OAuth — adaptadores prontos, ligam com credencial.

### 2026-09-10 — Daemon 24/7 = GitHub Actions, não máquina ligada
**Porquê:** gratuito em repo público, sem VPS, histórico versionado, issue automática em ALTA.
`--watch` local existe, mas é o plano B.

### 2026-09-10 — Limites do que o agente NÃO automatiza, por design
Abrir conta em gateway (KYC), validar mercado (só dinheiro real valida), contornar captcha,
"resolver" impossibilidade física (roteador civil → Marte, cartilagem avascular → regeneração
sistêmica por firmware). Skill `/nobel` acha caminhos não-óbvios **dentro** das leis conhecidas.

### 2026-09-10 — Onde o cérebro mora (resposta ao "não quero te perder")
**Decisão:** três lugares, três estratégias — (1) o modelo: Anthropic, nada a fazer; (2) tudo que
foi construído: o repositório no GitHub, e **só** ele — nada de valor fica só na máquina;
(3) chaves: gerenciador de senhas, nunca em git nem em backup em texto.
Cópia fora do GitHub: `backup.sh` (git bundle + config pessoal) para Drive/iCloud, cron noturno.
Kit de recuperação em texto no repo e como Google Doc: https://docs.google.com/document/d/1_beo1wEmov2yDu9VJX9QRyGdyIDeIs6vpgkuhRI65nU/edit
**Porquê:** máquina é descartável por design. Se comprar o M5/M6, são 5 comandos.
**Alternativa rejeitada:** salvar "o Claude" no Drive como arquivo único — não existe esse objeto;
o que existe é repositório + conta + chaves, cada um com seu lugar.

### 2026-09-10 — Recall automático como hook, não como regra
**Decisão:** `recall.sh` em `UserPromptSubmit` busca no cérebro as palavras-chave de cada pedido
e injeta o que já foi feito/decidido. **Porquê:** "lembrar de procurar" é conselho; hook é lei.
O operador pediu que nenhuma missão ignore o que já existe — isso só se garante por código.

### 2026-09-10 — Manutenção semanal automática (routine + saude.yml)
**Decisão:** `saude.yml` (determinístico, grátis) toda segunda e a cada push; routine no claude.ai
dispara `/manutencao` (julgamento: consolidar memória, repetição → skill, dependências).
**Custo:** uma sessão semanal. Pausar: lista de routines em claude.ai → desativar.

### 2026-09-10 — O Cérebro mestre já existia; este repo vira satélite
**Contexto:** ao abrir o MacBook, o Claude local foi direto a `~/Claude/cerebro-backup` — repositório
privado com 2.717 arquivos, 111 skills, 7 diretores, 243 memórias, JARBAS, MOTOR-EXECUCAO. Fora do escopo
desta sessão; eu construí em silo.
**Decisão:** o mestre vence (CLAUDE.md §0b). Este repo governa site + radar de produto. Memória de negócio
vai para o mestre. `/analise-cripto` renomeada para `/analise-cripto` (a `cripto` pessoal dele silenciaria a minha).
`recall.sh` passa a buscar também nas memórias do mestre quando ele existir na máquina.
**Porquê:** meses de memória, leis e gates financeiros não se substituem por um dia de construção.
**Não fiz:** nada dentro do `cerebro-backup` — só leitura. O lado privado é registrado pelo Claude do Mac.

### 2026-09-10 — Lei da Monotonia (resposta a "não decaia, sempre evoluir")
**Contexto:** o operador temeu que subordinar o satélite ao mestre fosse regressão, e afirmou que "o de hoje"
é o mais evoluído. Fato: os dois Macs rodam o mesmo mestre (243 memórias, leis, gates); o de hoje tem 1 dia.
**Decisão:** não há "principal". Um Cérebro, dois repositórios. Precedência é de LEIS (segurança financeira e
ética); capacidade é por UNIÃO e só cresce. Manifesto `CAPACIDADES.txt` + `_capacidades.sh` no CI: capacidade
que some = vermelho. Arquivar em vez de apagar.
**Porquê:** o medo dele é legítimo — sistemas de IA regridem por esquecimento silencioso. A resposta é teste,
não promessa.

### 2026-09-10 — Soberania de motor (Codex/ChatGPT lê, nunca escreve nos arquivos do Claude Code)
**Contexto:** o Codex está ligado ao Cérebro (`codex-config/`, `~/.codex/AGENTS.md`) e escreve na mesma máquina.
O operador não quer outro motor editando os arquivos do motor Claude Code.
**Decisão:** cada motor é dono dos seus arquivos; todos leem tudo. Garantia em código: pre-commit que bloqueia
commit de arquivo do motor sem `CLAUDECODE`; manifesto SHA-256 verificado no CI; regra simétrica — este agente
não edita `codex-config/`/`~/.codex/`.
**Limite honesto:** o portão vale onde `core.hooksPath` foi ativado (bootstrap). Edição que escape é DETECTADA
no CI, não impedida. No mestre, o mesmo mecanismo precisa ser instalado pelo Claude do Mac (prompt entregue).

### 2026-09-10 — Índice de memória: a unidade de fusão é o link, e perda de ponteiro é erro fatal
**Contexto:** o `fundir-indice.py` v3 do mestre fundia por linha ("local vence a linha") e o sync dos 2 Macs
apagou 4 ponteiros em 4 minutos, em silêncio (`|| true`). Arquivo sem ponteiro no índice é memória invisível.
**Decisão:** (1) fusão por **link**: todo link de qualquer entrada tem que estar na saída, sempre; texto é
secundário (local vence só quando cobre os mesmos links; empate assimétrico = as duas linhas ficam).
(2) **Guarda pós-condição independente da fusão**: recusa gravar e sai com 2 se um ponteiro sumiria — o
sistema prefere parar a involuir. (3) Verificador de órfãs roda no bootstrap, no início de sessão e no
`/manutencao`; `saude.yml` roda os testes. (4) Nunca "flake", nunca `|| true` em ferramenta que grava memória.
**Alternativa rejeitada:** só consertar o v3 no mestre. Sem teste no CI e sem verificador independente, o
próximo refactor repete o bug sem ninguém ver.

## Em aberto

- [ ] **Primeiro nicho de infoproduto** — aguarda `/cacar-produto aberto`
- [x] **Vault privado** — já existia: `cerebro-backup` (privado, sincronizado nos 2 Macs)
- [ ] **Meta Ads / Supermetrics conectados à conta real de anúncio?**
- [ ] **Gateway de pagamento definido** — Hotmart/Kiwify (mais simples) vs Stripe+Asaas (mais margem, mais trabalho)
- [ ] **PIX_KEY preenchida em `radar/.env`** — sem ela o paywall roda em sandbox
- [ ] **Mergear branch na `main`** — o cron do radar só ativa a partir da main
- [ ] **Chave Gemini** (`GEMINI_API_KEY`) — MCP configurado, inerte sem a chave
- [ ] **Reddit OAuth** — dobra as fontes de dor do radar
- [ ] **Rodar `bash .claude/backup.sh` no Mac uma vez** + linha de crontab que ele imprime
- [ ] **Chaves no cofre iCloud `CEREBRO-CHAVES-BACKUP`** (convenção do mestre) — PIX, PayPal, Vercel, Reddit
- [x] **`fundir-indice.py` v4 + `verificar-indice.py` no mestre** — instalados pelo Claude do Mac (`c96d37e`), prova 244 → 244
- [x] **Regra READ-ONLY do Codex no mestre** — seção nos dois AGENTS.md + portão pre-commit (`935dc1d`)
- [ ] **Portão do mestre no Mac mini** — vive em `.git/hooks` (não viaja); no mini: recriar o hook ou versionar via `core.hooksPath`
