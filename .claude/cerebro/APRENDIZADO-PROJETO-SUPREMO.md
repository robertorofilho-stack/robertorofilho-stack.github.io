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

### 20. O guarda bloqueia quem tenta reescrever o guarda
Reescrever `guarda.sh` via heredoc em bash falhou: o hook PreToolUse leu o comando inteiro, achou o padrão proibido *na definição da própria regra* e negou. Mesma família das lições 14 e 19 — o comando é texto, e texto é escaneado. Hook, regra de firewall, padrão de bloqueio: escrever pela ferramenta de arquivo (Write/Edit), nunca por bash. E validador de teste em arquivo `.py`, não inline: aspas simples do Python dentro de aspas simples do bash produzem código quebrado que parece falha do alvo.

### 21. Portabilidade se testa simulando a máquina alvo, não lendo o código
`jq` ausente e `grep '\|'` só apareceram porque o teste construiu um PATH sem `jq`, sem `node`, sem `python3`. Ler os scripts não teria achado — eles "pareciam" portáveis.

### 22. "Não quero te perder" tem resposta técnica, não emocional
O que o operador chama de "você" são três coisas com três donos: o modelo (Anthropic — não se perde), a personalização (repositório — versionada, clonável, restaurável de bundle) e as credenciais (gerenciador de senhas — a única parte que exige disciplina humana). Confundir os três gera ou pânico ("preciso salvar o Claude no Drive") ou descuido (chave no git). Separar os três é o backup.

### 23. Recall que depende de lembrar não é recall
Instrução "consulte a memória antes de agir" vale enquanto o contexto está fresco. Hook em `UserPromptSubmit` que faz `grep` das palavras-chave do pedido no cérebro vale sempre, custa 38 ms e não tem opinião. Regra 7 aplicada à própria memória: o que precisa acontecer vira código.

### 24. Artefato gerado não vai para o git
O projeto que `gerar-saas.ts` produz é saída, não fonte. Versionado, ele colidiu com a própria fixture no CI ("já existe") e ainda ia divergir do template a cada mudança. Regra: o que um script gera, o `.gitignore` esconde e o CI regenera. E fixture é idempotente por definição — regenerar sem perguntar.

### 25. Cegueira de silo — a minha
Passei um dia inteiro construindo um "cérebro" enquanto o operador já tinha um, maior, privado, fora do meu escopo. A skill `/nobel` fala de cegueira de silo na ciência; eu a pratiquei na engenharia. Regra: infraestrutura nova começa com inventário do que existe — `list_repos`, `~/.claude`, memória local do operador — e a pergunta "isto já existe?" antes da primeira linha. O certo não foi apagar o meu: foi subordiná-lo. Meses de memória e leis valem mais que um dia de código bem testado.

### 26. Involução não vem de quem apaga — vem do sync que "vence a linha inteira"
Ninguém deletou nada e 4 memórias sumiram em 4 minutos: o script de união escolhia a linha vencedora e descartava os links agrupados na perdedora; o `|| true` do sync engolia o erro. Lição em três partes: (1) a unidade de proteção tem que ser o menor item que importa (o link, não a linha); (2) toda ferramenta que grava memória precisa de uma pós-condição **independente** da lógica que gravou — re-ler a saída e comparar com as entradas — e preferir **parar** a gravar com perda; (3) um manifesto de capacidades que cobre skills e hooks mas não cobre o índice deixa a porta mais usada aberta. Reproduzi com os dados reais antes de consertar: sem reprodução, "conserto" é palpite.

### 27. Caminho da outra máquina é hipótese até ser lido no script dela
Liguei o verificador a `~/.claude/memory` porque "é onde a memória fica". No Mac o cofre real é `~/.claude/projects/-Users-macroberto-Claude/memory`, e o `sync-backup.sh` do mestre dizia isso na linha 10 — eu tinha o arquivo aberto e não li o `MEM=`. Um hook apontado para pasta inexistente não falha: fica mudo, que é o pior modo de falhar para um verificador. Regra: caminho de outra máquina se descobre no código dela ou por auto-detecção com `--listar`; e todo verificador precisa de um teste onde o alvo existe E um onde não existe, para provar que ele não está calado por engano.

### 28. Antes de pedir uma chave ao operador, `git grep` no mestre
Mandei o operador criar uma chave do OpenRouter que o Cérebro já tinha desde 06/07, com crédito, no cofre `~/.config/vha-vibe-marketing/.env`, e que três memórias do mestre descrevem como "a chave padrão de LLM dos projetos". Ele me corrigiu em uma linha. É a cegueira de silo (#25) na versão pequena e cotidiana: credencial, conta, assinatura, ferramenta paga. Regra: todo pedido de "crie / assine / compre" ao operador passa antes por `git grep -i <nome> origin/master` no mestre e por `chaves-credenciais.md` / `cofre-env-vibe.md`. O que já existe se lê; o que se lê não se pede.
**Corrigido em código (mesma sessão, depois da bronca):** o `recall.sh` não alcançava o mestre na nuvem (só procurava em `~/Claude/cerebro-backup`; o clone estava em `../cerebro-backup`) — agora procura ao lado do projeto; e ganhou um recall de credenciais: pedido com "chave / conta / assinatura / crédito / comprar" injeta a lista de chaves que já existem no cofre do mestre, só nomes. Testado com o pedido real: `cofre-env-vibe.md`, `llm-padrao-openrouter.md` e `OPENROUTER_API_KEY` aparecem antes de eu responder. Lição virou hook, como manda o #19: instrução é conselho; hook é lei.
