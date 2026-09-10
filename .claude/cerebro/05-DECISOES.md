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
Kit de recuperação em texto no repo e como Google Doc: https://docs.google.com/document/d/1hWNPGgofuoILMBhq-TYa77McR5nrogbR3R90tjAKCG0/edit
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

## Em aberto

- [ ] **Primeiro nicho de infoproduto** — aguarda `/cacar-produto aberto`
- [ ] **Vault privado criado?** — comando em [[00-MAPA]]
- [ ] **Meta Ads / Supermetrics conectados à conta real de anúncio?**
- [ ] **Gateway de pagamento definido** — Hotmart/Kiwify (mais simples) vs Stripe+Asaas (mais margem, mais trabalho)
- [ ] **PIX_KEY preenchida em `radar/.env`** — sem ela o paywall roda em sandbox
- [ ] **Mergear branch na `main`** — o cron do radar só ativa a partir da main
- [ ] **Chave Gemini** (`GEMINI_API_KEY`) — MCP configurado, inerte sem a chave
- [ ] **Reddit OAuth** — dobra as fontes de dor do radar
- [ ] **Rodar `bash .claude/backup.sh` no Mac uma vez** + linha de crontab que ele imprime
- [ ] **Chaves no gerenciador de senhas** (PIX, PayPal, Vercel, Reddit) — antes de preencher qualquer `.env`
