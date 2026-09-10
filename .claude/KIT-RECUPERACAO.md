# 🧠 KIT DE RECUPERAÇÃO — PROJETO SUPREMO

> Se o Mac morreu, se comprou máquina nova, se o GitHub sumiu: este documento devolve tudo.
> Cópia viva: `.claude/KIT-RECUPERACAO.md` no repositório · cópia no Google Drive: https://docs.google.com/document/d/1m1dDhwvhOU9JJRd56I4-pslTtQAhCyXChJfKUuHTsqk/edit

## 🖥️ Para quem nunca abriu o Terminal — leia isto primeiro

Os comandos deste kit rodam no **Terminal** do Mac. Não dentro do Claude Code, não no navegador, não no ChatGPT. O Claude Code é o **último** comando da lista — ele é aberto *pelo* Terminal.

1. Aperte **⌘ + Espaço**, digite `Terminal`, Enter. Abre uma janela com um cursor piscando.
2. Cole **uma linha por vez**, aperte Enter e **espere terminar** (o cursor volta a piscar numa linha nova) antes de colar a próxima.
3. O que pode aparecer no caminho:
   - Uma janela pedindo para instalar as *"ferramentas de linha de comando"* (Xcode Command Line Tools) → **Instalar**. Demora alguns minutos. Depois cole o mesmo comando de novo.
   - `claude: command not found` → o Claude Code não está instalado. Cole `curl -fsSL https://claude.ai/install.sh | bash`, espere, **feche e reabra o Terminal**, rode `claude` de novo. (Precisa de macOS 13 ou mais novo e de um plano Pro/Max/Team.)
   - Uma página do navegador pedindo login → entre com a **mesma conta do claude.ai** — é ela que traz os conectores e as preferências.
   - Pergunta se confia na pasta e nos servidores MCP do projeto → **Sim**.
4. Como saber que deu certo: o `bootstrap.sh` mostra `✓ cérebro carrega (… bytes)`. Dentro do `claude`, pergunte **"Quem sou eu e o que está pendente?"** — a resposta tem que vir com o seu perfil e a lista de decisões em aberto.
5. Travou em qualquer ponto: copie tudo o que apareceu na tela e cole numa sessão do Claude (web ou Mac) com "isso apareceu quando rodei X".

Alternativa sem Terminal: o app Claude para Mac (claude.com/download) inclui o Claude Code com interface gráfica — mas o repositório ainda precisa ser clonado uma vez, e o Terminal é o caminho que este kit garante.

## O que é "o cérebro" e onde cada parte mora

| Parte | Onde vive | Pode perder? |
|---|---|---|
| **O modelo** (Claude) | Anthropic | Não. Não está na sua máquina. |
| **Constituição, 17 skills, 9 subagentes, 5 hooks, memória, radar** | GitHub: `robertorofilho-stack/robertorofilho-stack.github.io` — **é o cérebro inteiro** | Só se o GitHub e todas as suas cópias sumirem. Por isso o bundle. |
| **Conectores** (Gmail, Meta Ads, Supabase, Vercel, PubMed, Canva…) | Conta claude.ai | Não. Vivem na conta, não na máquina. |
| **Preferências** (o texto sobre quem você é e o que quer) | Conta claude.ai → Configurações | Não. |
| **Chaves** (`.env`: PIX_KEY, PAYPAL, VERCEL_TOKEN, REDDIT…) | **Só na sua máquina** (gitignore) | **SIM.** Única coisa que exige backup separado → gerenciador de senhas. |
| Config pessoal `~/.claude` | Sua máquina | Sim, se um dia personalizar. `backup.sh` cobre. |

**Princípio:** tudo que importa vive no repositório. A máquina é descartável.

## Máquina nova — 5 comandos

```bash
git clone https://github.com/robertorofilho-stack/robertorofilho-stack.github.io.git
cd robertorofilho-stack.github.io
git checkout claude/projeto-supremo-claude-code-epsu7w   # até o merge na main
bash .claude/bootstrap.sh
claude
```

Na primeira sessão: aceitar os servidores MCP do projeto (1 clique). Pronto — o cérebro carrega sozinho no primeiro prompt.

Depois: `cp radar/templates/env.example radar/.env` e preencher com as chaves do gerenciador de senhas.

## GitHub sumiu (conta, repo, tudo)

Você tem o bundle no Google Drive / iCloud (`Backups-Claude/projeto-supremo-DATA.bundle`):

```bash
git clone ~/Google\ Drive/My\ Drive/Backups-Claude/projeto-supremo-DATA.bundle robertorofilho-stack.github.io
cd robertorofilho-stack.github.io && git checkout claude/projeto-supremo-claude-code-epsu7w
```

Depois crie um repositório novo no GitHub e `git remote set-url origin <novo>` + `git push --all`.

## Manter o backup vivo

- **Automático:** `bash .claude/backup.sh` uma vez, depois a linha de `crontab` que ele imprime.
- **Segunda cópia no GitHub** (opcional): repositório privado espelho — `git remote add espelho <url-privada> && git push espelho --all`.

## Como o sistema se mantém sozinho

| Mecanismo | Quando | O que faz |
|---|---|---|
| `carregar-cerebro.sh` | início de toda sessão | injeta perfil, memória, decisões abertas |
| `recall.sh` | **cada prompt** | busca no cérebro o que já foi feito sobre o tema e injeta |
| `lembrar-memoria.sh` | fim da sessão | cobra a gravação da memória |
| `guarda.sh` | cada comando | bloqueia destruição e vazamento de chave |
| `saude.yml` | segunda + cada push | testa hooks, skills, radar, template, QA; abre issue se quebrar |
| `radar.yml` | de hora em hora (após merge) | caça oportunidade, abre issue em ALTA |
| `/manutencao` | semanal (routine) | consolida memória, transforma repetição em skill, atualiza dependências |

## Contatos de referência

Repositório: https://github.com/robertorofilho-stack/robertorofilho-stack.github.io
Branch de trabalho: `claude/projeto-supremo-claude-code-epsu7w`
Vault Obsidian: `.claude/cerebro/` · Mapa: `.claude/cerebro/00-MAPA.md`
