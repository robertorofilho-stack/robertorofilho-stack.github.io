# O cérebro deste projeto

Como o ambiente de Claude Code deste repositório está montado, o que foi instalado,
o que foi deliberadamente deixado de fora e por quê.

Origem: análise do vídeo **"5 plugins de Claude Code"** de Isaac Cardoso
([@isaque.prod](https://www.instagram.com/isaque.prod/)), setembro de 2026.
Transcrição integral em [`video-5-plugins.md`](video-5-plugins.md).

---

## Por que existe um "cérebro" versionado

Sessões de Claude Code na web rodam em container efêmero. Plugin instalado numa
sessão **morre com ela**. O que sobrevive é o que está commitado.

Por isso o ambiente inteiro vive no repositório:

| Caminho | O que faz |
|---|---|
| `CLAUDE.md` | Regras que toda sessão neste repo carrega automaticamente |
| `.claude/settings.json` | Liga o hook de validação e bloqueia leitura de arquivos sensíveis |
| `.claude/hooks/validar_pagina.py` | Barra SEO e JSON-LD quebrados na hora da edição |
| `.claude/skills/nova-pagina/` | Cria página nova já ranqueável |
| `.claude/skills/publicar/` | Valida, sincroniza e publica com segurança |
| `.claude/skills/task-observer/` | Observa o trabalho e propõe melhorias de skill |
| `.claude/agents/revisor-cfm.md` | Revisa texto público contra a CFM 2.336/2023 |
| `scripts/verificar-site.py` | Varredura completa antes de publicar |
| `scripts/atualizar-sitemap.py` | Sincroniza `sitemap.xml` sem carimbar o site todo |
| `scripts/instalar-cerebro.sh` | Reconstrói o ambiente em qualquer máquina |

Reconstruir tudo em uma máquina nova:

```bash
bash scripts/instalar-cerebro.sh
```

---

## Os 5 plugins do vídeo — o que é real e o que serve aqui

Todos os cinco existem de verdade. O valor de cada um, porém, é bem diferente.

### 1. OmniRoute — **não instalado, por decisão**

[github.com/diegosouzapw/OmniRoute](https://github.com/diegosouzapw/OmniRoute) ·
gateway MIT, ~352 provedores, endpoint único em `localhost:20128/v1`.

Funciona como anunciado: quando a cota acaba, ele cai para outro provedor. O
"1,6 bilhão de tokens de graça" é a soma dos free tiers de todos eles.

**O problema para este caso específico:** "provedor gratuito" significa um
terceiro desconhecido recebendo o conteúdo da sessão, sem contrato, sem acordo de
tratamento de dados e sem garantia de descarte. Muitos free tiers pagam-se
justamente treinando modelo com o que passa por ali.

Para um médico, qualquer conteúdo clínico digitado numa sessão roteada assim vira
exposição de dado pessoal sensível de saúde sob a **LGPD (Lei 13.709/2018, art. 11)**,
além de risco ético perante o CFM. O ganho é economia de token; a perda potencial é
o registro profissional. A conta não fecha.

**Se ainda quiser usar:** máquina separada, perfil separado, exclusivamente para
trabalho não-clínico, nunca neste repositório.

### 2. claude-mem — **instalado**

[github.com/thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) ·
v13.24.1

Captura o que acontece na sessão, comprime e reinjeta o contexto relevante na
sessão seguinte. Banco vetorial local (Chroma, embeddings locais via ONNX), sem
chamada externa. Entrega o que promete: parar de reexplicar o projeto toda vez.

**Cuidado de uso:** o banco guarda o que passou pelas sessões. Se você usar o
Claude para redigir laudo ou discutir caso, isso entra no banco local. Mantenha
trabalho clínico em outra pasta e outro perfil, fora deste projeto.

### 3. Headroom — **instalado, opt-in**

[github.com/headroomlabs-ai/headroom](https://github.com/headroomlabs-ai/headroom) ·
v0.37.0, `pip install headroom-ai`

Comprime saída de ferramenta, log e arquivo antes de chegar ao modelo. O ganho
divulgado (60–95% em JSON, ~20% em código) é plausível para saída repetitiva.

Fica no caminho das requisições — por isso é `--headroom` no instalador, e não
padrão. Uso: `headroom wrap claude`.

Para **este** repositório o ganho é modesto: são 25 páginas HTML, contexto pequeno.
Vale para projetos grandes, não tanto para este site.

### 4. claude-code-setup — **instalado. O de maior retorno.**

Plugin oficial da Anthropic, do marketplace `claude-plugins-official`.

Lê o projeto e recomenda hooks, skills, subagentes e MCPs que fazem sentido — e
manda tirar o que é enfeite. Foi rodado neste repositório; metade do que existe
em `.claude/` saiu dessa análise.

Rodar de novo quando o projeto mudar de forma:

```
/claude-code-setup:claude-automation-recommender
```

### 5. Task Observer — **instalado**

[github.com/rebelytics/one-skill-to-rule-them-all](https://github.com/rebelytics/one-skill-to-rule-them-all)
· CC BY 4.0

Meta-skill: observa a sessão, capta padrões, correções e decisões, e transforma
isso em melhoria das outras skills. Versionado em `.claude/skills/task-observer/`.

Não dispara sozinho de forma confiável — precisa ser invocado no início da sessão.
Por isso o `CLAUDE.md` manda carregá-lo.

---

## O que foi construído além do vídeo

O vídeo entrega ferramentas genéricas. O que faz diferença aqui é o que foi feito
em cima delas, para este site:

**Hook de validação (`validar_pagina.py`).** Roda a cada edição de `.html`. Checa
título, meta description, canonical correto para a rota, os cinco campos Open Graph,
`lang="pt-BR"`, viewport, `alt` em toda imagem e — o mais importante — se o
`application/ld+json` é JSON válido. Um JSON-LD quebrado derruba o rich result da
página inteira no Google, e é invisível a olho nu. Testado: 25/25 páginas reais
passam sem falso positivo; 6/6 defeitos plantados são capturados.

**Varredura completa (`verificar-site.py`).** Além do acima, confere links internos
quebrados, `sitemap.xml` nos dois sentidos (página no sitemap que não existe, e
página que existe fora do sitemap) e links mortos no `llms.txt`.

**Sincronizador de sitemap (`atualizar-sitemap.py`).** Só carimba `lastmod` nas
páginas que o git aponta como alteradas. Carimbar o site inteiro com a data de hoje
a cada publicação degrada a confiança do crawler.

**Agente `revisor-cfm`.** Revisa texto público contra a Resolução CFM 2.336/2023,
em vigor desde 11/03/2024 — que **revogou** a 1.974/2011. Isso importa: muito
material de marketing médico ainda aplica a norma velha e trava o que hoje é
permitido (selfie, preço de consulta, forma de pagamento, desconto sem venda casada).
O agente foi escrito para não ser mais restritivo do que a norma é, e para nunca
citar número de artigo sem conferir na fonte oficial.

---

## Fontes

- Transcrição do vídeo: [`video-5-plugins.md`](video-5-plugins.md)
- [Marketplace oficial de plugins da Anthropic](https://github.com/anthropics/claude-plugins-official)
- [Documentação de plugins do Claude Code](https://code.claude.com/docs/en/discover-plugins)
- [Resolução CFM 2.336/2023 — portal oficial](https://publicidademedica.cfm.org.br/)
- [Resolução CFM 2.336/2023 — texto integral (PDF)](https://sistemas.cfm.org.br/normas/arquivos/resolucoes/BR/2023/2336_2023.pdf)
- [LGPD — Lei 13.709/2018](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)
