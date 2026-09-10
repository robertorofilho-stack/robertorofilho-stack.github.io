# 🎓 PROJETO SUPREMO — base técnica instalada

**Data:** 2026-09-10
**Origem:** 7 repositórios open source + documentação oficial de Skills, Subagentes, Hooks e MCP + 3 artigos + metadados de vídeos.

---

## 1. Hierarquia de extensão do Claude Code

A confusão mais comum e mais cara. São quatro coisas diferentes:

| Camada | O que é | Custo de contexto | Quando usar |
|---|---|---|---|
| **CLAUDE.md** | Contexto sempre presente | Alto — carrega **sempre** | Regra que vale para tudo. Manter enxuto. |
| **Skill** | Playbook carregado sob demanda | ~100 tokens parado, corpo só quando invocado | Procedimento repetível |
| **Subagente** | Executor com contexto isolado | Zero no principal | Trabalho ruidoso: pesquisa, revisão, varredura |
| **Hook** | Código determinístico em evento | Zero | Garantia. CLAUDE.md pede; hook **obriga**. |

**A distinção decisiva:** instrução em CLAUDE.md é conselho — o modelo pode ignorar sob pressão de contexto. Hook é código: roda sempre. O que **precisa** acontecer vira hook.

## 2. Divulgação progressiva

Skills carregam só nome + descrição (~100 tokens). O corpo (<5.000 tokens) entra apenas quando o modelo julga relevante. Arquivos de apoio (`reference.md`) entram só quando referenciados.

Consequência prática: **100 skills instaladas custam quase nada parado.** Não há razão para economizar em quantidade de skills — há razão para economizar em CLAUDE.md.

## 3. Loop de erro zero

O padrão que separa "gera código" de "entrega sistema":

```
executar → falhou? → capturar log completo → hipótese → corrigir → executar de novo
```

Sem mecanismo de verificação, o agente escreve código plausível e para. Com Playwright, teste ou CI, ele fecha o ciclo sozinho.

**A regra que muda o comportamento:** "não me relate problema, me relate solução". Só sobe para o humano bloqueio de credencial, permissão ou decisão de negócio — nunca bug.

## 4. Cascata multi-agente

Uma mente que faz tudo produz viés confirmatório: quem escreve o código também o aprova.

```
Arquiteto  → decide antes de existir código
Programador→ implementa
QA         → ataca o que foi feito, em contexto isolado
```

O QA **precisa** de contexto isolado. Quem escreveu não consegue atacar de verdade o que escreveu.

## 5. Encadeamento de MCP

O poder não está em nenhum servidor. Está na cadeia:

`pesquisar → estruturar → banco → código → navegador testa → deploy → anúncio → medir → gravar`

Playwright é a peça que fecha o loop: sem navegador, o agente **imagina** que funciona. Com navegador, ele **vê**.

## 6. Contexto é como leite

Contexto longo degrada qualidade. Não é opinião — é comportamento medido.

Manejo:
- Conversa nova por assunto
- Documento de handoff antes de recomeçar (compactação proativa)
- Subagente para trabalho ruidoso — o ruído fica no contexto dele
- CLAUDE.md enxuto e revisado periodicamente

## 7. Consciência de mercado (Schwartz)

O erro mais caro em copy é abrir no nível errado:

| Nível | Abertura correta |
|---|---|
| Inconsciente | história / dado chocante |
| Consciente do problema | nomear a dor com as palavras dele |
| Consciente da solução | mecanismo único |
| Consciente do produto | diferenciação + prova |
| Mais consciente | oferta direta + urgência real |

## 8. Equação de valor

```
VALOR = (Resultado desejado × Probabilidade percebida) ÷ (Tempo × Esforço)
```

Derrubar o denominador quase sempre é mais barato e mais convincente que inflar o numerador. "Em 11 dias, 20 min por dia" vende mais que "resultado extraordinário".

## 9. Anúncio ativo = prova de lucro

Ninguém queima verba 30 dias no prejuízo. Meta Ads Library e TikTok Creative Center são **públicos**. É a melhor pesquisa de mercado que existe e é gratuita.

## 10. Sinal do algoritmo de vídeo curto

Peso decrescente: retenção em 3s → watch time → **compartilhamento** → salvamento → comentário → like.

Like é a métrica mais fraca. Escrever para compartilhamento e salvamento.

## 11. Automação da automação

Feito duas vezes → vira sistema na terceira. Prompt repetido vira skill. Pesquisa repetida vira subagente. Checagem repetida vira hook.

É assim que a capacidade compõe em vez de estagnar.

---

## Fontes

| Fonte | O que rendeu |
|---|---|
| ComposioHQ/awesome-claude-skills | Estrutura de SKILL.md, divulgação progressiva, taxonomia de skills |
| ykdojo/claude-code-tips (49 dicas) | Manejo de contexto, handoff, worktrees, verificação, automação em camadas |
| luongnv89/claude-howto | Arquitetura em 10 módulos, padrões de workflow, estrutura de hooks |
| modelcontextprotocol/servers | Servidores de referência, formato de configuração |
| wong2/awesome-mcp-servers | Catálogo por categoria: navegador, banco, busca, memória |
| All-Hands-AI/OpenHands | Modelo de agente autônomo em container, protocolo ACP |
| Docs oficiais (Skills/Subagentes/Hooks/MCP) | **Especificação exata** — o que tornou os arquivos válidos em vez de plausíveis |
| nocodestartup.io | Panorama no-code: Supabase, Bubble, n8n, Lovable, FlutterFlow, Xano |
| Vídeos (metadados) | Confirmação de padrões: OpenCode, Claude Code Masterclass, Meta L7 tips |

**Limite honesto:** YouTube bloqueia IP de nuvem. Título, canal e duração foram obtidos de 3 vídeos; transcrição, de nenhum. O conteúdo conceitual desses vídeos veio do texto que o operador colou e da documentação oficial — que é fonte mais confiável que transcrição de vídeo, de todo modo.

---

## Sessão 2 — do método à máquina

### 12. O loop de erro zero só existe quando há um verificador externo
Sete bugs encontrados na própria construção, nenhum por leitura de código — todos por **execução**: build, teste de CRC, navegador real, log de servidor. Sem Playwright e sem rodar, o agente entrega código plausível e para. Verificador externo é o que transforma "gerar" em "entregar".

### 13. QA cego não diagnostica
`stdio: "ignore"` no servidor escondeu um `EADDRINUSE` por três rodadas. O QA reprovava um build correto porque conectava num servidor órfão da rodada anterior. Log capturado + porta dinâmica resolveram. Regra: **todo processo que o QA sobe tem log gravado**.

### 14. `pkill -f` casa com a própria linha de comando
`pkill -f "next start"` derrubou o shell que o executava (exit 144) porque o padrão aparecia na cmdline do próprio shell. `next[ ]start` casa com o alvo e não consigo mesmo. Bug silencioso, difícil de ver, clássico.

### 15. Sinal de tendência ≠ demanda
O radar pontuou "lionel messi" acima de uma dor real de mercado na primeira rodada. Volume de busca por notícia não é demanda por ferramenta. Tendência é acelerador; dor explícita é o motor. A trava está no código.

### 16. Payload de pagamento não sai para terceiro
QR via `api.qrserver.com` enviava o BR Code (com valor, nome e chave do recebedor) para um serviço externo. Geração local com `qrcode` como data URI: zero dependência, zero vazamento. Pequeno detalhe, grande princípio.

### 17. Nome de pacote vindo de prompt precisa ser verificado no registro
`@google/mcp-server-gemini` → 404. `@modelcontextprotocol/server-puppeteer` → descontinuado. Dois de quatro pacotes do `.mcp.json` sugerido não existiam ou estavam mortos. `npm view <pacote> version` antes de instalar qualquer coisa que veio de texto.

### 18. Fronteira legal é engenharia, não moral
Das 7 fontes de renda propostas, 4 eram fraude ou violação de termos. Para um profissional licenciado, o risco não é "pode dar errado" — é "o ganho esperado é negativo". Recusar não é limitação do agente; é a análise de risco funcionando.

### 19. No Bash tool, o comando inteiro É a cmdline — inclusive o heredoc
Um `pkill -f 'qa[.]ts'` na primeira linha de um comando que continha `cat > qa.ts <<'EOF' …` matou o shell antes de escrever o arquivo: o regex casou com o texto "qa.ts" dentro do heredoc. O colchete protege só se o padrão não aparecer **em nenhum outro lugar** do comando. Regra: matar processo por campo exato do `ps` (`awk '$2=="next-server"'`), nunca por regex sobre a cmdline, e nunca no mesmo comando que escreve arquivo.
