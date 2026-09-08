---
name: nova-pagina
description: >
  Cria uma página nova do site com SEO, Open Graph e schema.org completos desde o
  primeiro byte, seguindo o padrão exato das páginas existentes. Use quando pedirem
  uma nova página de condição, procedimento, artigo ou landing — por exemplo
  "cria a página de tendinite patelar", "quero um artigo sobre menisco discoide",
  "nova landing de infiltração".
---

# Nova página do site

Cria página que já nasce ranqueável, sem retrabalho de SEO depois.

## Regra de ouro: não invente template

O padrão do site vive nas páginas existentes, não em um modelo congelado aqui.
**Sempre comece copiando a página existente mais parecida** e adapte. Isso mantém
header, footer, CSS, tracking e schema sempre em sincronia com o resto do site.

| Tipo de página nova | Copie como base |
|---|---|
| Condição ou procedimento do joelho | `joelho/artrose-do-joelho/index.html` |
| Artigo educativo | `conteudos/dor-no-joelho-ao-subir-escadas/index.html` |
| Página institucional / atendimento | `consulta-particular-ortopedista-fortaleza/index.html` |

## Passos

### 1. Definir a rota

Sempre pasta + `index.html`, URL terminando em `/`. Slug em português, sem acento,
separado por hífen, refletindo o termo que o paciente digita no Google.

```
joelho/tendinite-patelar/index.html   ->  /joelho/tendinite-patelar/
```

### 2. Pesquisar antes de escrever

Antes de redigir, busque como as pessoas realmente pesquisam o tema (WebSearch) e
qual é a evidência atual (MCP do PubMed, se disponível). Base clínica de referência:
Campbell's Operative Orthopaedics, Rockwood and Green's, Insall & Scott Surgery of
the Knee. Não invente número — sem fonte, escreva qualitativamente.

### 3. Copiar e adaptar

Copie o arquivo base e troque, **um por um**:

- `<title>` — até 60 caracteres, termo de busca primeiro, marca depois
- `<meta name="description">` — 120 a 158 caracteres, com o termo e um motivo de clique
- `<link rel="canonical">` — `https://www.drrobertorodrigues.com` + a rota nova
- `og:title`, `og:description`, `og:url` — coerentes com os acima
- `og:image` — imagem existente em `/assets/og/` ou uma nova de 1200×630
- JSON-LD — ajustar `@id`, `name`, `url`, `description`; manter os dados do médico
  (CRM-CE 10806, RQE 12256, TEOT 17765) idênticos aos das outras páginas
- `<h1>` — um por página, diferente do `<title>`, escrito para humano
- navegação e breadcrumb — incluir a página nova no lugar certo

### 4. Escrever o conteúdo

Estrutura que funciona para busca e para paciente com dor:

1. Abertura que nomeia o sintoma como o paciente o descreve
2. O que é, em linguagem direta
3. Por que dói / o que está acontecendo
4. Quando procurar um especialista (critérios claros)
5. Como se avalia
6. Opções de tratamento, do conservador ao cirúrgico
7. FAQ com as perguntas reais de consultório — vira `FAQPage` no JSON-LD
8. CTA de agendamento
9. Aviso: conteúdo educativo, não substitui consulta médica

Frase curta. Sem jargão não explicado. Sem promessa de resultado.

### 5. Passar pelo compliance

Rode o agente `revisor-cfm` no texto final. Ele valida contra a Resolução CFM
2.336/2023. Ajuste o que ele marcar como VEDADO ou RISCO.

### 6. Registrar a página

- Adicionar `<url><loc>` no `sitemap.xml` com `lastmod` de hoje
- Adicionar o link na seção correta do `llms.txt`
- Linkar a página nova a partir de pelo menos uma página existente relevante
  (página órfã não ranqueia)

### 7. Verificar

```bash
python3 scripts/verificar-site.py
```

Só siga para o commit com a saída limpa.
