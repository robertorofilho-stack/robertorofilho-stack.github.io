# 📓 Memória

> Ordem cronológica inversa — mais recente no topo.
> Formato fixo. Sem prosa: isto é para consulta rápida, não para leitura.

---

## 2026-11

### 2026-11-14 — Decisão: anúncio da Lia para "conversas" + migrar a Lia para o WhatsApp oficial

**Ordem do operador:** corrigir o anúncio para conversas; ver o valor de passar a Lia para a API oficial da Meta; "faça tudo
automatizado". **Custo apresentado:** taxa Meta R$ 0 (Cloud API direta) · respostas 1.000 grátis/mês, depois ~R$ 0,035
(~R$ 130/mês) · leads de anúncio grátis na janela · servidor já pago. **Bloqueio desta sessão:** conector META em
"needs_reconnect" e Supermetrics sem login Meta → nada alterado no Meta daqui. **Entregue:** missão (anúncio sem mexer em
verba; migração por coexistência com teste antes de desligar a instância antiga) para o Claude do MacBook — fora do repo.
Pendência dele: reconectar o conector META em claude.ai (então a parte A pode ser feita desta sessão).

### 2026-11-13 — Como a Lia vende mais sem punição: pesquisa oficial Meta/WhatsApp + diagnóstico

**Pedido:** "vasculhe tudo… como a Lia pode vender mais sem levar punição, mais leads; me explique fácil".
**Pesquisa (subagente, ~60 links, relatório no scratchpad da sessão, não versionado):** WhatsApp proíbe app não oficial
(FAQ: ban temporário ou permanente) e envio em massa/automático (Termos); Business Policy 23/09/2026: só contatar com opt-in,
empresa só inicia com template aprovado, bot permitido com saída para humano. Caminho oficial = Cloud API (a Evolution v2
tem modo oficial; coexistência mantém o app no mesmo número). Preço Brasil por mensagem entregue: atendimento 1.000 grátis/mês
por número (desde 01/10/2026), utilidade US$ 0,0068, marketing ~R$ 0,32 [SEC]; janela de anúncio clique-para-WhatsApp grátis
(72 h na página comercial × 7 dias na doc técnica — divergem). Limites 250→2.000 (com empresa verificada)→10 mil→100 mil.
Proibição de IA de jan/2026 = só assistente de uso geral; bot de vendas próprio pode. Meta Business Agent: no Brasil, mas
pago nos planos novos e faz menos que a Lia. Otimizar anúncio para compra exige Conversions API com o id do clique, que
só a API oficial entrega. LGPD: consentimento ou legítimo interesse de cliente, com opt-out; ANPD já multou lista de WhatsApp.
**Diagnóstico:** Lia já é só-inbound (lei de 05/10) — certo; risco que sobra é rodar na Evolution não oficial; anúncio
clique-para-WhatsApp do Edita Já otimizado para CLIQUE (o mais fraco). Lista fria antiga: não reaproveitar em canal nenhum.
**Plano recomendado:** (1) trocar o anúncio para otimizar CONVERSAS já; (2) verificar a empresa na Meta; (3) migrar a Lia
para a API oficial no mesmo número (coexistência) — custo ~R$ 130–190/mês; (4) depois, otimização para COMPRA com a Lia
mandando o evento Purchase; (5) leads: Reels + comentário→DM→wa.me (já roda pela Zernio) + anúncio no Status; opt-in
registrado. Conselho de outros motores ainda não rodado. Verba: 5 números do PAINEL + OK do Roberto.

### 2026-11-13 — Veredito: 3 guias oficiais da Meta sobre WhatsApp Business (agente de IA, transmissões, venda)

**O que é (lidos):** (1) **Meta Business Agent** — IA grátis dentro do app WhatsApp Business (Ferramentas → Meta Business
Agent), aprende com catálogo, perfil, site e conversas; responde dúvidas e recomenda produto 24 h; NÃO negocia, NÃO fecha
compra, NÃO processa pagamento — passa para humano; escolhe chats e horários. Em português/R$ → vale no Brasil.
(2) **Business Broadcast** — mesma mensagem para até 2 mil contatos, só quem deu opt-in; 250 envios grátis, depois pago;
métricas de entregue/lido/respondido. (3) **Guia de venda** — anúncio de clique para WhatsApp + Reels (+13% retorno,
−16% custo/resultado em estudo da Meta de 2023) e **otimização de compra**: exige compartilhar eventos de compra pelo app,
marcando a conversa com **etiquetas** de nome padronizado (ex.: pedido pago) ou criando **pedido** no app.
**Cruzamento:** a Lia (vendedora) roda na Evolution API no servidor e já fecha venda com link de checkout → o agente da
Meta faz menos; ligar os dois no mesmo número = resposta dupla. Central da clínica (secretária) é outro número.
**Veredito:** (a) não trocar a Lia; (b) Broadcast com opt-in = jeito oficial de reativar base sem risco de banimento (a
lei "nunca disparo frio" continua); (c) maior ganho: etiqueta de compra nas conversas dos anúncios de clique para
WhatsApp → Meta otimiza para quem compra, não para quem só conversa (testar se a Evolution aplica etiqueta via API);
(d) agente da Meta na central da clínica só para logística (horário, endereço, convênio), nunca dúvida clínica (CFM/LGPD).

### 2026-11-13 — API de Conversões do Meta nos checkouts: missão entregue ao operador (não versionada)

**Pedido:** "Sim" ao item 8 (rastreio navegador + servidor sem duplicar). **Achado:** não precisa de código — o checkout
tem API de Conversões nativa (token na config do pixel); um produto já usa, outros com campanha no ar não. **Entrega:**
missão para o Claude do MacBook (inventário só-leitura → aplicar o token existente pelo painel → conferir fonte
"Navegador e Servidor", desduplicação e EMQ ≥ 6). IDs de conta/pixel/produto ficam fora deste repo público (§6) — a
tentativa de versionar a missão aqui foi barrada pelo classificador, corretamente. Detalhe no mestre.

### 2026-11-13 — Veredito: "AI Marketing Engineer Playbook" (Klint AI, David Roberts — Google Doc)

**O que é:** isca de comentário ("SYSTEM") da Klint (API de contexto social, vende o item 5). 10 sistemas com Claude Code +
GitHub Actions + MCP, todos começando em modo só-relatório: (1) agente de anúncios Meta, (2) SEO programático, (3) vídeo
de anúncio com IA, (4) recriar anúncio do concorrente > 60 dias, (5) influenciadores, (6) ser citado pelo ChatGPT,
(7) página por anúncio, (8) rastreio navegador + servidor sem duplicar, (9) fluxos de e-mail/SMS com 10% de grupo
controle, (10) relatório de segunda escrito por IA.
**Cruzamento com o arsenal:** 1/4 = conector oficial Meta Ads (hoje pedindo nova autorização) + regra dos anúncios §5 + G5
(só o Roberto aprova verba); 2/6/7 = skills `mkt-programmatic-seo`, `mkt-ai-seo`, `mkt-cro` no mestre + `llms.txt` do site;
3 = Higgsfield Ads Studio + clone; 5 = produto da Klint, dispensável. **Lacunas reais:** (8) API de Conversões do Meta com
deduplicação nos checkouts (Cakto) antes de escalar tráfego; (10) relatório semanal automático (Supermetrics + Meta);
(9) fluxos de e-mail de comportamento (o canal hoje é WhatsApp/Lia).
**Próximo passo de receita:** item 8 primeiro — sem rastreio certo, o agente de anúncios aprende com número errado.

### 2026-11-13 — Janela do Mundo publicada + veredito "MotionSites" (RCK060)

**Janela do Mundo:** operador quis "ver as câmeras do mundo todo e tudo que eu possa ver" (produto/automação depois).
Página privada: https://claude.ai/artifact/4gQRuTW4nrfgm7uinyc9jw — Argos Atlas no centro + 28 fontes ao vivo em 8 abas
(câmeras, céu, aviões, navios/portos, clima, terremotos/incêndios, mundo), favoritos no aparelho, relógios. Links conferidos
13/11 (FR24, MarineTraffic e GitHub dão 403 a servidor; abrem no navegador). Excluído de propósito: Insecam (câmera
particular sem senha). Próximo, quando ele pedir: God's Eye View no MacBook / alertas com APIs abertas (adsb.lol, CelesTrak).
**RCK060 (ia.rckbusiness.digital, "RICK I.A" / @pedrorick.ia):** isca grátis "MotionSites — do brief ao site": skill de
Claude para criar página com brief, plano, construção e revisão; pede nome, e-mail, telefone e site. Sem preço visível
(funil para venda depois). Veredito: dispensável — o Cérebro já tem `briefing-de-site` + `criar-site-motion` +
`frontend-design` + `impeccable` (método Vitrine IA). Só valeria baixar para comparar, sem dar o telefone pessoal.

### 2026-11-13 — Argos Atlas (PDF VibeHub/Fabiano) + skill nova `/veredito`

**Pedido:** PDF "Argos Atlas: 200 mil câmeras, aviões, navios e satélites ao vivo" + "e esse?".
**O que é:** site (argosatlas.com, domínio de 23/05/2026) que junta dado público num globo: câmeras de trânsito/webcams
(1.116 no Brasil; 470 em Santos), aviões (adsb.lol, OpenSky), navios (AIS), satélites (CelesTrak), portos (IMF PortWatch).
Grátis com conta; planos em euro (44,99 a 10.499/ano); API/MCP só no plano empresa; termos proíbem raspar e seguir pessoa.
**Não confundir:** o ARGOS do Cérebro é outro (sensor de presença por Wi-Fi com ESPectre, memórias `argos-*`).
**Veredito:** nada a instalar nem assinar. Serve como (1) pauta de vídeo de curiosidade para @falar.detudo (globo ao vivo,
sem pessoa identificável, crédito da fonte); (2) modelo de negócio a estudar: dado público agregado + freemium — encaixa
no radar de micro-SaaS se aparecer nicho brasileiro com quem pague. Para a conta médica: irrelevante.
**Skill nova:** `/veredito` (repetição 7× desde 03/10: "e esse?") — ler → recall → conferir (incl. Brasil) → filtro do
operador → 4 blocos → gravar. Origem cita os 7 episódios.

### 2026-11-13 — x402 (HTTP 402: agente de IA paga o site em USDC): real e sério, mas sem receita para o operador hoje

**Pedido:** "e esse?" (guia longo colado, com exemplo oficial, conta de taxas, regras BR e 9 prompts).
**Fato:** protocolo aberto (Coinbase mai/2025 → x402 Foundation na Linux Foundation abr/2026; Visa, Mastercard, Google,
Stripe, Cloudflare). Volume pequeno e concentrado: texto colado = US$ 1,64 mi em 30 dias (x402scan, 05/11), mediana por
vendedor US$ 0,50/mês, top 10 = 62%; outras fontes (jul/2026) falam em US$ 24 mi/30 dias, com ~metade suspeita de
lavagem de volume (Forkast) → números divergem; nenhum deles é mercado grande. Monetization Gateway da Cloudflare: só EUA.
No Brasil: receber USDC = criptoativo (Bens e Direitos ≥ R$ 5 mil; DeCripto > R$ 35 mil/mês fora de exchange BR; stablecoin
e carteira autocustodiada = câmbio, Res. BCB 521).
**Veredito:** não implementar. O operador não tem recurso que agente pague (dado exclusivo, API); a US$ 0,001 a taxa come
tudo. Reabrir quando existir um dado/API própria de valor (ex.: radar de oportunidades) e volume real. O que copiar é o
FORMATO do material (guia profundo com teste próprio datado + conta + 9 prompts) como infoproduto/isca.

### 2026-11-13 — MiroFish (enxame de agentes que "prevê" reação a ideia): avaliado → NÃO instalar como decisor

**Pedido:** "que acha desse?" (README colado: semente → milhares de agentes → relatório + conversar com agentes).
**Fato:** github.com/666ghj/MiroFish, ~85,5 mil estrelas, AGPL-3.0, motor OASIS (CAMEL-AI), exige LLM (formato OpenAI;
OpenRouter serve) + **Zep Cloud** (memória; não temos chave). README: "alto consumo, comece com < 40 rodadas". **Nenhum
benchmark de acerto publicado**; teste da WPP Research (1 dia, S&P 500): o enxame deu o mesmo que 1 chamada simples ao
mesmo modelo; nº de agentes não controlável; custo por rodada não publicado; resultados variam entre execuções.
Não estava na memória (0 de 1.058 arquivos do mestre).
**Veredito:** brinquedo de cenário, não previsão. Persona sintética não compra — o sinal do sistema continua sendo anúncio
rodando > 30 dias + pagamento real na pré-venda (CLAUDE.md §5). Para "onde a ideia quebra" já temos `/conselho` (4 motores,
centavos) e `/auditar`. Mesma lição de 27/09: medir antes de adotar (N.E.X.U.S. = ruído).
**Se o operador quiser testar:** 1 backtest num caso com resultado real conhecido (ex.: lançamento do curso de edição),
teto de US$ 5, comparado com `/conselho`; só adota se acertar onde o conselho errou.

### 2026-11-13 — Reel "sua empresa dentro do ChatGPT" (Dfn8aFvtHaG): novidade real, mas ainda não vale como serviço no Brasil

**Pedido:** link de Reel (assistido com `assistir-video.py`, Gemini Pro).
**O vídeo (66 s, "Matheus"):** gancho "tá dormindo no ponto" → página da OpenAI "Introducing Businesses in ChatGPT" →
Business Hub → buscar empresa → "Create" → perfil (sobre, contato, horário) → "venda esse serviço para outras empresas";
CTA = link nos comentários + seguir. Chama de "ChatGPT Business" e "agente" (impreciso: é perfil; agente é outra coisa).
**Fato (busca, 13/11):** "Businesses in ChatGPT" lançado em beta em 10/11/2026; reivindicar é grátis; exige site e
verificação; **Business Agents só EUA**; **comércio local só reivindica fichas já existentes nos EUA**; sem lista oficial de
países e há relato de pedido fora dos EUA indo para lista de espera (fontes secundárias; conferir na ajuda da OpenAI).
**Para o operador:** (1) reivindicar o perfil "Dr. Roberto Rodrigues" com o site drrobertorodrigues.com — grátis, ele faz
(login dele); casa com o `llms.txt` que o site já tem; (2) vender "sua empresa no ChatGPT" pela Vitrine IA **ainda não**:
para negócio local brasileiro não funciona hoje → no máximo lista de espera; (3) formato do Reel = mesmo molde do Pedrão
(urgência + tela passo a passo + link).

### 2026-11-08 — "Personal Finance" da Anthropic (conectar banco): não serve no Brasil; o caminho é o Belvo MCP

**Pedido:** "Personal finance" = "atualização da Anthropic que conecta o banco".
**Fato (3 fontes, 05/11/2026):** beta "Personal Finance" no Claude, liga contas por **Plaid**, só leitura, até 24 meses de
transações, **só EUA**, planos pagos (TechCrunch, 9to5Mac, Yahoo Finance). Bancos brasileiros não entram.
**Para o operador (Brasil):** conector **Belvo MCP** no diretório do Claude (oficial desde ~15/10/2026, segundo a Let's
Money; não conferido na fonte da Belvo) lê contas via **Open Finance Brasil** — saldo, transações, renda; só leitura.
Alternativas: Open Finance Data MCP (Cumbuca, instituição de pagamento autorizada). Estado: nenhum conector financeiro
instalado na conta; instalar é ação do operador em claude.ai → Conectores.
**Regra:** dado financeiro pessoal nunca entra neste repo público (§6) — análise vai para o Cérebro privado ou fica no chat.

### 2026-11-08 — Diretor de Aprendizado: vídeo do Pedrão da Licitação + Cérebro passa a assistir Instagram na nuvem

**Pedido:** link de post do Instagram + "Assiste".
**Capacidade nova:** `assistir-video.py` aceita Instagram: página pública `/embed/captioned/` → URL do mp4 no CDN (sem
login) → ffmpeg 480p/15fps → Gemini via OpenRouter como data URL. Medido: 90 s, Pro US$ 0,08 · Flash US$ 0,01; os dois deram
os mesmos números. O arquivo veio da branch `claude/diretor-aprendizado-videos-1003`, que **nunca foi fundida na main**
(lá estão as memórias de 03/10: SEMDOR, grade 3x, migração do mini) → fundir quando o operador autorizar.
**O vídeo (Demw4amATon, 17/10/2026, @pedraodalicitacao, 90 s):** gancho "vender pro governo como se você tivesse 10 anos" →
tela do PNCP (dispensa, UF=SP, palavra-chave) → lâmpada de projetor Epson ELPLP80, Franca-SP, R$ 941/un × R$ 293 no Mercado
Livre, 5 un., "uns R$ 3 mil" → "o cadastro fica pra outro vídeo" → aula grátis ("saiba mais"). Nada novo de método: o
perfil inteiro já foi estudado e auditado em 13–14/09 (`missao-pedrao-licitacao-vendas-governo`, DESTILACAO-PEDRAO.md).
Esse mesmo exemplo já tinha sido conferido em set: vencedor só 1,4% abaixo do estimado (em outros casos dele, 45–49%).
Não conferido hoje: o PNCP não responde a acesso da nuvem (resposta vazia).
**O que serve ao operador:** o FORMATO (tutorial de tela de 90 s → número real → lacuna "fica pra outro vídeo" → isca) para
os Reels SEMDOR e infoprodutos. Negócio: o kit "IA aplicada a compras públicas" (Arcanjo, 06/10) segue travado pelo CNPJ
da Vitrine IA — esse é o passo que gera receita no tema governo.

### 2026-11-03 — Curso de edição com IA: produzido na nuvem (31/10), passado ao Mac e à venda desde 01/11

**Pedido (31/10):** "terminar tudo; curso em vídeo, passo a passo didático, prompts prontos, pasta para baixar; urgente"; depois
"um comando para o cérebro do MacBook assumir"; depois "atualize a memória e veja como está" (03/11).
**Feito na nuvem (31/10):** 18 videoaulas explicativas sem clone (telas animadas + narração por voz de IA, 1 take por aula),
2 pacotes do aluno, capas, 7 textos da Mesa do Marketing, auditoria red-team com 15 achados aplicados, remendo idempotente da
atendente de WhatsApp (modo lista de espera / modo venda), runbook da plataforma e memória para o mestre. Motor de videoaula
reutilizável para qualquer curso (ver `03-ATIVOS`).
**Passagem nuvem → Mac:** 5 ZIPs + `assumir.sh` (acha os ZIPs em Downloads, instala motor/atendente/memória no mestre, abre o
Claude do Mac com `MISSAO-MAC.md`; idempotente, testado em sandbox com nome "(1).zip"). Push ao mestre: negado duas vezes pelo
classificador; feito só depois de autorização por escrito do operador, em branch de passagem, nunca master. A sessão do Mac
puxou pelo branch e seguiu.
**Feito no Mac/servidor (01–02/11, por outra sessão):** versão 2 para público geral (telas reais, exemplo de negócio comum,
10 narrações refeitas), produção movida para o servidor, 2 produtos criados na plataforma de checkout com área de membros
(9 aulas cada + pacote), atendente publicada em modo venda a partir da base viva, aviso à lista de espera com ordem explícita.
**Conferido hoje da nuvem:** os dois checkouts respondem e mostram Pix e cartão em até 10x, sem boleto (prints no chat).
A memória da missão não estava no índice do mestre (ficou dentro da pasta de passagem) → gravada em branch próprio do mestre.
A sessão do Mac caiu por login expirado em 02/11.
**Lições:** (1) base viva da atendente ≠ arquivo do git: publicar a partir do banco, nunca do arquivo defasado; (2) passagem
entre sessões = branch de passagem + script idempotente + arquivo de missão, e a mensagem entre sessões só passa com o cartão
de confiança aprovado pelo operador; (3) avisar lista por filtro de palavra pega quem queria outra coisa (1 aviso errado) →
filtrar pelo pedido registrado; (4) garantia = 7 dias, lei do operador desde 01/11, nunca propor mais; (5) o classificador
barra push "como meio", ativação de produto e envio de WhatsApp: pedir a palavra do operador, não contornar.
Detalhe de preço, links, entrega e pendências fica no mestre (§6).

## 2026-10

### 2026-10-31 — Curso de edição com IA: status urgente, nada à venda, Lia em lista de espera

**Pedido:** "como está o curso de edição? já está à venda? gente falando com a Lia depois da divulgação no Instagram."
**Fontes:** mestre privado (clonado, só leitura), Drive, Gmail, conselho de 4 motores (`/conselho`, US$ 0,04).
**Achado:** o pacote de texto do curso existe no mestre (29/10), mas nada está em plataforma, sem link, sem área de membros,
16 de 17 aulas não gravadas, e a base viva da atendente de WhatsApp não tinha uma linha sobre o curso. Divulgação saiu
antes de existir passo de venda.
**Conselho 4/4 AJUSTAR:** pré-venda de conteúdo não gravado morta (CDC 30/35/37/49); vender só o que existe; atendente
corrigida hoje; segundo curso "para qualquer profissão" = mesma oferta com segunda porta, não produto novo.
**Entregue (no Drive, pasta "Curso Edita com IA — missão 31-10", e para o mestre):** relatório de status com plano de 7 dias
e roteiro de execução; script idempotente que insere a seção do curso na base da atendente (modo lista de espera / modo venda,
testado 357 → 407 linhas); parecer dos 4 motores; memória para o índice do mestre. Push ao mestre a partir da nuvem foi
negado pelo classificador → o Claude do Mac copia.
**Lição (vira regra):** nenhum CTA público ("comenta X", "chama no WhatsApp") sem três coisas prontas: produto criado,
link de checkout e atendente instruída. Detalhe de preço/oferta fica no mestre (§6: produto não lançado não entra aqui).

## 2026-09

### 2026-09-27 — Aprendizado de fronteira em agentes: estudado, auditado, instalado e MEDIDO

**Pedido:** "aprenda tudo, instale tudo" (material colado com MCTS, memória vetorial/grafo, N.E.X.U.S., links de cursos).
**Fontes:** Stanford CS329A já estava dominado (Fase 0, não reestudado); CMU 11-768 lido na íntegra pelos slides
(10 aulas, 666 págs.); Berkeley e DeepLearning.AI verificados; NUS descartado (não é fronteira).
**Instalado:** `memoria_viva.py` (recall ranqueado + associação + AgentIR + Hebb com vantagem + episódio com fonte +
consolidação "lobo frontal" + avaliação), `arvore.py` + `/arvore`, `verificador-citacao`, laço Reflect na caçada,
pausa final no Stop, `transcrever-youtube.sh`. Tudo copiado no mestre (`559fdad`) + missão JARBAS (`ccf5302`).
**Números:** gabarito 171 casos — BM25 MRR 0,792 → calibrado 0,803; v0 com associação no score 0,740 (rejeitada).
Jogo 24 ao vivo 3/3 solúveis com prova exata, 1 difícil falhou, 1 impossível corretamente não declarado. Conselho 4/4
AJUSTAR, US$ 0,0185. Testes: memória 27 · árvore 15 · hooks 0 falhas.
**Lições:** (1) juiz LLM deu 1,0 a solução errada → só verificador exato fecha, e juiz nunca ensina sinapse;
(2) a pilha "óbvia" perdia do BM25 até ser medida — medir antes de adotar; (3) N.E.X.U.S./S.E.P.H.I.R.O.T.H.
executados = ruído aleatório; (4) YouTube bloqueia nuvem → Mac; (5) hook que lê stdin precisa de prazo (`read -t`).
**Pendências:** 83 memórias órfãs no índice do mestre (pré-existentes, provável compactação de hoje — corrigir nas
duas cópias, nos Macs); índice do mestre em 25,7 KB (acima do corte ~24,4 KB); próxima rodada da CMU (PreCompact,
rubrica, uso de skill, calibrar juiz).
**Fim da tarde — rodada final:** instaladas as 4 técnicas restantes da CMU: checkpoint PreCompact com âncoras literais,
`rubrica.py` (nota ponderada + auditoria + concordância juiz×humano), `uso-skill.sh` (TroVE) e `conselho.py --saude`
(erro por provedor). Falso alarme de 83 órfãs era defeito do `verificar-indice.py` (não lia `MEMORY-ARQUIVO.md`), agora
corrigido: 0 órfãs. Suíte: 100 testes Python + hooks 0 falhas · 56 capacidades.
**Noite — a fala das aulas:** Mac mini transcreveu as 9 aulas (103.823 palavras; só a rota de cookies do Chrome
funcionou; o `git pull` abriu o vim e travou o operador → gotcha no mestre). 3 agentes destilaram a fala. Instalado:
checkpoint com proibições e efeitos externos, piso de relevância no recall (7/7 prompts certos), anti-loop, parada
"sem sinal" na árvore, provedor no conselho, `mutacao.py` (41% → 49%), TruffleHog no CI, regras de navegador e de
origem de skill. A mutação achou um bug nela mesma (bytecode do mutante reaproveitado). 117 testes · 59 capacidades.
**Decisões do operador ("faça tudo", 27/09 noite):** (1) merge na `main`; (2) índice do mestre compactado nas duas
cópias pelo `compactar-indice.py` (comando entregue ao operador no Mac mini; na simulação, 11 entradas de jun–set →
`MEMORY-ARQUIVO.md`, 0 ponteiro perdido — AGUARDA confirmação "COMPACTADO OK"); (3) `/cacar-produto aberto` disparado; (4) regra "skill só com `## Origem`" no §7 do CLAUDE.md.
**Links:** [[APRENDIZADO-AGENTES-AVANCADOS]] [[03-ATIVOS]] [[05-DECISOES]]

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
