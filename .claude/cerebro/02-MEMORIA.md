# 📓 Memória

> Ordem cronológica inversa — mais recente no topo.
> Formato fixo. Sem prosa: isto é para consulta rápida, não para leitura.

---

## 2026-09

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
