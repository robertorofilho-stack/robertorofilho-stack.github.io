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

### 2026-09-10 — Conselho de outros motores: segunda opinião obrigatória, disparada por mim, por API
**Contexto:** operador quer que eu peça contra-argumento a outras IAs (GPT, Grok, Gemini, Manus…) em toda missão de
produto ou extraordinária, sem ele precisar mandar. O MCP do Gemini exige CLI nova com login interativo e não roda na nuvem.
**Decisão:** um helper por API, formato OpenAI para todos (Gemini pelo endpoint compatível), com OpenRouter como
chave única recomendada e chaves diretas aceitas. Prompt adversarial fixo (objeções, premissas ocultas, teste de 7
dias, concorrente, veredito). O gatilho é estrutural: regra §3, seção obrigatória nas 5 skills estratégicas, hook Stop
que acusa decisão nova sem conselho. Manus fora: sem API, automação por navegador é frágil e fere termos.
**Custo medido (catálogo público do OpenRouter, 3k in + 1,2k out):** US$ 0,001 a 0,013 por opinião → rodada de 4
motores custa centavos. **Rejeitado:** integração por IA (quatro contas, quatro faturas) e o MCP como caminho principal.

### 2026-09-10 — Primeiro infoproduto: o guia de joelho para leigos NÃO é o primeiro produto pago (Conselho 4/4)
**Tese testada:** guia digital de artrose/dor no joelho para leigos, R$ 97–197, vendido por Instagram/TikTok, em vez de
produto não-médico em nicho maior.
**Conselho (10/09, GPT-6 Astra · Grok 4.6 · Gemini 3.8 Flash · DeepSeek v4.1, US$ 0,093):** consenso 4/4 — morre na
aquisição: CAC frio R$ 80–200 > preço; "guia" é conteúdo com substituto gratuito; CFM/CREMEC + políticas de anúncio
de saúde derrubam conversão e criam risco assimétrico ao CRM; público com artrose (55+) não é quem compra
infoproduto no Instagram (25–45). Vereditos: AJUSTAR ×3, MATAR ×1. **Divergência:** o que fazer no lugar —
não-médico primeiro (Grok, DeepSeek) · isca gratuita + serviço de alto ticket (Gemini) · pré-venda para validar antes de
produzir (GPT). **Convergência escondida:** produto para **profissionais** (fisio, educador físico, residente),
R$ 500–3.000, sem leigo. **Ressalva a verificar:** GPT afirma que a Res. CFM 2.336/2023 permite "antes e depois"
educativo sob condições — conferir o texto antes de mudar o §6 do CLAUDE.md.
**Decisão:** (1) conteúdo de joelho = isca gratuita e autoridade; (2) primeiro produto pago sai do `/cacar-produto
aberto` com viés não-médico ou B2B profissional; (3) todo teste = página de pré-venda, ≤ R$ 350 em 7 dias, métrica é
pagamento ou clique no checkout. Relatório completo entregue ao operador (não versionado: estratégia, §6).

### 2026-09-10 — Produto é NÃO-médico por padrão; médico só quando o operador disser
**Contexto:** na primeira caçada, três frentes eram médicas ou para profissionais de saúde (IA para consultórios, formação
para fisios, perícia médica), seguindo a "convergência" do conselho. O operador cortou: "não quero produtos médicos,
quase nunca quero algo médico, quando for algo médico eu digo, pare de procurar".
**Decisão:** frente médica (inclui B2B para médicos, fisios, clínicas e perícia) fica fora de caçada, oferta e lançamento
até ele dizer a palavra. Registrado em [[01-PERFIL]], no `/cacar-produto` e no CLAUDE.md §2. Os achados de perícia
médica (3 anunciantes com 50 dias a 3 anos de anúncio) ficam arquivados aqui como dado, não como proposta.
**Também:** ele não quer caçar produto agora. `/cacar-produto` só quando pedido.

### 2026-09-12 — Cirurgias360: o paralelo da nuvem vira referência; o app vivo é o do Mac; o clone se atualiza por hook
**Contexto:** ordem de validar/aprimorar/construir o app de gestão cirúrgica. Executei tudo e verifiquei (40/40 Playwright) sem ver
que o Mac mini já tinha construído e publicado o app em 10–11/09 com dados reais — meu clone do mestre era de 10/09.
**Decisão:** (1) o paralelo NÃO entra em `apps-source/`; vai para `projetos/cirurgias360/paralelo-nuvem-2026-09-12/` com README
"não é o app", pela Lei da Monotonia (nada se apaga) e para não confundir os Macs; (2) o que soma ao app vivo é auditoria regulatória
(20 fontes), conselho 4/4, minutas LGPD e módulos candidatos; (3) a causa vira código: `_mestre.sh` puxa o mestre antes do recall.
**Conselho (GPT, Grok, Gemini, DeepSeek — 4/4 AJUSTAR sobre a tese do paralelo):** aceito — recebimento se mede aos 90 dias, não 30;
medir tempo da secretária por pedido; "f" do art. 11 pode não cobrir a secretária. Divergência registrada: "compliance é overengineering
para 2 usuários" — não aceito (dado de saúde real exige o mínimo legal). Nota: o app vivo já roda com dados reais por decisão dele
(10/09) e ele já decidiu vender como assinatura (11/09) — as premissas "fictício primeiro" e "zero SaaS" do paralelo caíram.
**Alternativa rejeitada:** publicar o paralelo como segundo app ou apagá-lo.

## Em aberto

- [ ] **App Cirurgias (VIVO, do Mac mini)** — pendências registradas lá: Apps Script na conta da secretária; novo link de acesso dela (o de 11/09 venceu 12/09 08h51); testar IA com documento real; 35 cirurgias sem lado; advogado para o plano de assinatura. Do paralelo da nuvem, fundir no app vivo: auditoria 20 fontes (6 pontos novos para o advogado), métrica de recebimento aos 90 dias, medir tempo da secretária por pedido.
- [ ] **Gravação Plaud de 11/09 "Oráculo de Autoconhecimento (Mapa Vivo)"** — ideia não-médica esperando o fluxo PROJETO CLAUDE (validar → esteira). Candidata a próxima missão de produto.

- [ ] **Primeiro nicho de infoproduto** — só quando o operador pedir; **não-médico** (B2B profissional de saúde também conta como médico para ele); guia de joelho para leigos NÃO é o primeiro produto pago
- [x] **Vault privado** — já existia: `cerebro-backup` (privado, sincronizado nos 2 Macs)
- [x] **Meta Ads conectado** — a busca na Ads Library pelo MCP exige conta de anúncio ativa e funcionou (10/09)
- [ ] **Gateway de pagamento definido** — Hotmart/Kiwify (mais simples) vs Stripe+Asaas (mais margem, mais trabalho)
- [ ] **PIX_KEY preenchida em `radar/.env`** — sem ela o paywall roda em sandbox
- [x] **Mergear branch na `main`** — feito 10/09 (`merge --no-ff`, autorizado com "mergeia"); radar 24/7 ativo
- [x] **Chave Gemini** — superada pelo **conselho de outros motores** (`/conselho`, por API); o MCP do Gemini passou a exigir CLI nova com login e ficou como opcional no Mac
- [x] **Conselho na nuvem** — credencial `openrouter.ai` no ambiente RESUMO MENSAL TRABALHO (10/09); `conselho saldo` = US$ 34,66 restantes; primeira rodada real feita (US$ 0,093, 4/4)
- [ ] **Reddit OAuth** — dobra as fontes de dor do radar
- [ ] **Rodar `bash .claude/backup.sh` no Mac uma vez** + linha de crontab que ele imprime
- [ ] **Chaves no cofre iCloud `CEREBRO-CHAVES-BACKUP`** (convenção do mestre) — PIX, PayPal, Vercel, Reddit
- [x] **`fundir-indice.py` v4 + `verificar-indice.py` no mestre** — instalados pelo Claude do Mac (`c96d37e`), prova 244 → 244
- [x] **Regra READ-ONLY do Codex no mestre** — seção nos dois AGENTS.md + portão pre-commit (`935dc1d`)
- [ ] **RAION sempre ligado, SÓ no MacBook por enquanto** (decisão 10/09; Mac mini fica desligado) — passos do operador no MacBook, nesta ordem: (1) `git pull && bash .claude/bootstrap.sh`; (2) `python3 ~/.claude/helpers/conselho/conselho.py --saldo` — Gemini HTTP 200 = crédito OK, **não pagar** (mestre: recarregado em 07/09, HTTP 200); só com 429 abrir aistudio.google.com/billing; (3) opcional e dele: ligar recarga automática + limite mensal no mesmo painel (estava desligada em 06/09; o mestre avisa que cai de novo no meio de missão); (4) rede para o `claude -p` headless (`LIBERAR-REDE-PRO-CEREBRO.command` + WebSearch/WebFetch); (5) "ATIVE RAION" ao Claude de lá (app; o vigia do MacBook já está ativo)
- [ ] **Portão do mestre no Mac mini** — vive em `.git/hooks` (não viaja); no mini: recriar o hook ou versionar via `core.hooksPath`
- [x] **Bootstrap do satélite no Mac mini** — 10/09: portão, hooks, índice e conselho ativos; órfã do vault Squads100 consertada
- [x] **Bootstrap do satélite no MacBook** — 10/09: pull limpo (33 arquivos), 0 pendências; índice do mestre íntegro (245 ponteiros), conselho com gemini e openrouter
