# Arsenal MCP

## Ativos em `.mcp.json` (sem chave — funcionam de imediato)

| Servidor | Poder | Para quê |
|---|---|---|
| **playwright** | Controle real de navegador | Testar o que foi construído, raspar site com JS, screenshot, checar responsivo. É o que fecha o loop de erro zero. |
| **memoria** | Grafo de conhecimento persistente | Entidades e relações entre projetos, produtos, pessoas. Complementa o vault em Markdown. |
| **pensar** | Raciocínio sequencial estruturado | Problema com muitos caminhos e revisão de hipótese |
| **fetch** | Busca de URL bruta | Quando o WebFetch padrão não basta |

## Já conectados na conta (não precisam de `.mcp.json`)

**Infra e publicação:** GitHub · Vercel · Supabase · Wix · Shopify
**Marketing:** Meta Ads (campanha, catálogo, pixel, biblioteca de anúncios) · Brevo · Supermetrics · Zapier
**Criação:** Canva · ElevenLabs (voz, imagem, vídeo) · Higgsfield (vídeo, TikTok, preditor de viralização) · HeyGen HyperFrames
**Operação:** Gmail · Google Calendar · Google Drive · Notion
**Medicina:** PubMed (busca, metadados, texto completo)

Esse conjunto já cobre a cadeia inteira: pesquisar → decidir → construir → testar → publicar → anunciar → medir.

## Para adicionar quando houver chave de API

```bash
# Raspagem profunda com saída estruturada
claude mcp add --scope project --env FIRECRAWL_API_KEY=xxx \
  --transport stdio firecrawl -- npx -y firecrawl-mcp

# Busca semântica feita para IA
claude mcp add --scope project --env EXA_API_KEY=xxx \
  --transport stdio exa -- npx -y exa-mcp-server

# Chrome real, com sessão logada
claude mcp add --scope project --transport stdio chrome \
  -- npx -y chrome-devtools-mcp@latest
```

## Encadeamento — onde está o poder real

Nenhum servidor isolado vale muito. A cadeia vale:

```
WebSearch / fetch      → pesquisa
        ↓
pensar                 → estrutura a decisão
        ↓
Supabase               → banco, migrations, RLS
        ↓
Write / Edit           → código
        ↓
playwright             → abre o navegador e testa de verdade
        ↓
Vercel                 → deploy
        ↓
Meta Ads               → campanha no ar
        ↓
Supermetrics           → mede o resultado
        ↓
memoria + cerebro      → grava o aprendizado
```

Uma cadeia, uma entrega. É o que separa "gerar código" de "entregar sistema no ar".

## Permissões

Este `settings.json` não define allowlist de permissões de propósito — essa é uma escolha do operador.
Para reduzir prompts de permissão com segurança, rode `/fewer-permission-prompts`, que analisa
o uso real e propõe uma lista sob medida. Alternativa: `Shift+Tab` alterna o modo automático na sessão.
