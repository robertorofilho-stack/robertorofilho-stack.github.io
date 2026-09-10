# 🧠 MAPA — Ponto de entrada

> Vault Obsidian. Abre direto: `File → Open Vault → .claude/cerebro`
> Carregado automaticamente no início de cada sessão pelo hook `carregar-cerebro.sh`.

## Arquivos

| Arquivo | Conteúdo | Quando escrever |
|---|---|---|
| [[01-PERFIL]] | Quem é o operador, objetivos, ativos | Quando algo estrutural muda |
| [[02-MEMORIA]] | Log cronológico de tudo | **Toda sessão com resultado** |
| [[03-ATIVOS]] | Produtos, páginas, funis, conteúdos criados | Ao criar qualquer ativo |
| [[04-PLAYBOOKS]] | O que funcionou e o que não funcionou | Ao descobrir padrão |
| [[05-DECISOES]] | Decisões estratégicas e o porquê | Ao decidir algo relevante |
| [[06-METRICAS]] | Números reais observados | Ao medir qualquer coisa |
| [[APRENDIZADO-PROJETO-SUPREMO]] | Base técnica instalada | Referência |
| [`../KIT-RECUPERACAO.md`](../KIT-RECUPERACAO.md) | Perdi tudo → como voltar (cópia no Drive) | Referência |
| `../backup.sh` | Bundle do repo + config pessoal → Drive/iCloud | Rodar 1x, depois cron |
| `../helpers/cerebro/` | `fundir-indice.py` (v4, por link, recusa perda) · `verificar-indice.py` (órfãs) · testes | Mestre presente: rodar no `/manutencao` |

## Protocolo

**Início de trabalho estratégico:** ler este mapa + o arquivo relevante.
**Fim de sessão com resultado:** gravar em [[02-MEMORIA]] e commitar.

Memória não commitada não existe. O contêiner morre; o repositório permanece.

## 💻 Continuar no MacBook (ou em qualquer máquina)

Tudo que existe aqui é **arquivo no repositório** — nada vive na conversa. Clonar = herdar o cérebro inteiro.

```bash
git clone https://github.com/robertorofilho-stack/robertorofilho-stack.github.io.git
cd robertorofilho-stack.github.io
git checkout claude/projeto-supremo-claude-code-epsu7w
bash .claude/bootstrap.sh          # checa git, claude, jq; testa o hook do cérebro
claude                             # o cérebro carrega sozinho no primeiro prompt
```

Já tem o repo? Só `git pull && git checkout claude/projeto-supremo-claude-code-epsu7w`.

**Nunca abriu o Terminal?** Comece pela seção 🖥️ do [kit de recuperação](../KIT-RECUPERACAO.md): onde colar, o que vai aparecer, como saber que deu certo.

| O que | Vem automático? | Detalhe |
|---|---|---|
| CLAUDE.md, 17 skills, 9 subagentes, 5 hooks, cérebro, radar | ✅ | Escopo de projeto: viajam com o clone |
| MCPs de `.mcp.json` (playwright, memoria, pensar, next-devtools, gemini) | ✅ com 1 clique | Na 1ª sessão o Claude Code pede para **aprovar** os servidores do projeto — aceite |
| Conectores da conta (Gmail, Meta Ads, Supabase, Vercel, PubMed…) | ✅ | São da conta claude.ai, não da máquina |
| Radar local (`npm run radar`) | ⚠️ `--radar` | Precisa Node ≥ 22.6 + Chromium: `bash .claude/bootstrap.sh --radar` |
| Cron 24/7 do radar | ❌ até o merge | GitHub Actions só agenda a partir da `main` |
| Esta conversa | ❌ | Contexto de sessão não transfere — **e não precisa**: o que importa está em [[02-MEMORIA]] |

**Vault no Obsidian:** `Open folder as vault` → `.claude/cerebro`. Os `[[wikilinks]]` já funcionam.

**Duas máquinas ao mesmo tempo** (web + Mac): sempre `git pull` antes de começar e commit + push ao terminar. O repositório é a única fonte de verdade; sessão que não commita não existiu.

## 🧠 O Cérebro MESTRE e este satélite

Este vault é o cérebro **público, do site** — um satélite. O **mestre** é `robertorofilho-stack/cerebro-backup`
(privado), vivo desde julho/2026, sincronizado entre MacBook e Mac mini a cada minuto (`sync-backup.sh`).
Nos Macs ele mora em `~/Claude/cerebro-backup` e é espelhado em `~/.claude`. Recuperação dele: `RESTAURAR.md`
dentro do próprio repo (clone → `instalar.sh` → chaves do iCloud `CEREBRO-CHAVES-BACKUP`).

| Conceito | Mestre (cerebro-backup) | Satélite (este repo) | Regra |
|---|---|---|---|
| Constituição | `CEREBRO-CONSTITUICAO.md` + 4 Leis + MOTOR-EXECUCAO | `CLAUDE.md` | mestre vence (§0b) |
| Memória | `claude-config/memory/` (243+, índice `MEMORY.md`) | `02-MEMORIA.md` | negócio → mestre; site/radar → aqui |
| Executores | 7 diretores + 111 skills + squads | 9 subagentes + 17 skills | negócio → diretores; código → `arquiteto`/`qa` |
| Auditoria | `diretor-de-auditoria` (🟢 libera campanha) | `auditor` / `qa` | os dois; o dele fecha |
| Radar | `radar-demanda-validada` (skill) · `RADAR-MAC/` (cripto/B3) | `radar/` (produto → micro-SaaS) | nomes diferentes, funções diferentes |
| Cripto | skill `cripto` + `RADAR-MAC` + Oráculo | `/analise-cripto` | dele é o sistema; o meu é análise pontual |
| Voz / daemon | JARBAS (`alfred/`, launchd) | routine semanal + `saude.yml` | complementares |
| Backup | `sync-backup.sh` + `RESTAURAR.md` | `backup.sh` + kit | os dois |
| Chaves | iCloud `CEREBRO-CHAVES-BACKUP` + `~/.config/vha-vibe-marketing/.env` | `.env` local | nunca em git |

O que o satélite acrescentou que o mestre não tinha: radar de produto + gerador de micro-SaaS com Pix/PayPal
+ QA no Chromium, CI na nuvem (`saude.yml`), `/nobel`, `/adversarial`, e a camada de site.

## ⚠️ Fronteira de segurança

Este repositório é **público** e publica `www.drrobertorodrigues.com`.

**Nunca gravar aqui:**
- Dado de paciente, prontuário, imagem clínica, nome — em nenhuma forma
- Chave de API, token, senha, credencial
- Faturamento, número de clientes, contrato, dado financeiro pessoal
- Produto não lançado ou estratégia sensível a concorrente

### Vault privado (para o que é sensível)

Uma vez, no computador local:

```bash
gh repo create cerebro-privado --private --clone
cd cerebro-privado
mkdir -p financeiro clinico produtos-em-desenvolvimento credenciais
echo "credenciais/" > .gitignore
git add . && git commit -m "inicia cérebro privado" && git push -u origin main
```

Depois, em qualquer sessão: `claude --add-dir ~/cerebro-privado` — o Claude lê os dois vaults,
mas só o público é commitado aqui.
