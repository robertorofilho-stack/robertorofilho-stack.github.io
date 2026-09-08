# CLAUDE.md — Site Dr. Roberto Rodrigues

Instruções operacionais para qualquer sessão de Claude Code neste repositório.

## O que é este projeto

Site institucional do **Dr. Roberto Rodrigues** — ortopedista e cirurgião do joelho em
Fortaleza (CRM-CE 10806 · RQE 12256 · TEOT 17765 · Membro Titular SBOT).

- **Stack:** HTML estático escrito à mão. Sem build system, sem framework, sem dependências.
- **Deploy:** GitHub Pages a partir de `main`. Push na `main` = publicado em produção.
- **Domínio:** `https://www.drrobertorodrigues.com` (ver `CNAME`).
- **Repositório é PÚBLICO.** Tudo que entrar aqui é indexável pelo Google e legível por qualquer pessoa.

Este site é o canal de captação de pacientes. Uma página com SEO quebrado é
consulta perdida. Trate cada alteração com esse peso.

## Regras invioláveis

1. **Nunca commitar dado de paciente.** Nome, imagem, exame, prontuário, laudo,
   relato clínico identificável — nada disso entra neste repositório. Nem em
   comentário, nem em arquivo de rascunho, nem em exemplo. Repositório público + dado
   de saúde = violação de LGPD (art. 11, dado sensível) e risco ético perante o CFM.
2. **Nunca quebrar o JSON-LD.** Cada página carrega `application/ld+json` com
   schema.org. Um JSON inválido derruba o rich result inteiro no Google. O hook
   `.claude/hooks/validar-pagina.py` bloqueia isso automaticamente — se ele reclamar,
   corrija antes de seguir.
3. **Nunca prometer resultado terapêutico.** Publicidade médica no Brasil é regulada
   pela **Resolução CFM 2.336/2023**, em vigor desde 11/03/2024 (revogou a 1.974/2011).
   Proibido: garantia de resultado, "antes e depois", sensacionalismo, autopromoção
   comparativa, exposição de paciente. Use o agente `revisor-cfm` antes de publicar
   qualquer texto novo.
4. **Nunca alterar credenciais.** CRM, RQE, TEOT, telefone e links oficiais aparecem em
   várias páginas e no `llms.txt`. Só mude se o médico pedir explicitamente, e então
   mude em **todos** os lugares de uma vez.
5. **Sempre `lang="pt-BR"`.** Conteúdo em português do Brasil, tom profissional e claro.

## Anatomia obrigatória de uma página

Toda página `.html` precisa de, no mínimo:

```
<html lang="pt-BR">
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>…</title>                                    ≤ 60 caracteres
  <meta name="description" content="…">               120–158 caracteres
  <link rel="canonical" href="https://www.drrobertorodrigues.com/…/">
  og:type · og:site_name · og:locale · og:title · og:description · og:image · og:url
  twitter:card = summary_large_image
  <script type="application/ld+json"> … </script>     JSON válido
```

Toda `<img>` precisa de `alt` descritivo, `width`, `height` e `loading="lazy"`
(exceto a imagem do hero, que usa `loading="eager"` e `fetchpriority="high"`).

Fotos servem em par `.jpg` + `.webp` via `<picture>`, com `<source type="image/webp">` primeiro.

Estrutura de URL: sempre uma pasta com `index.html` dentro, URL terminando em `/`.
Nunca `pagina.html` solto.

## Fluxo de publicação

1. Editar a página.
2. O hook `PostToolUse` valida SEO e JSON-LD sozinho e devolve os erros. Corrigir.
3. Rodar a varredura completa antes do commit:
   `python3 scripts/verificar-site.py`
4. Atualizar `sitemap.xml` (`lastmod`) e `llms.txt` se a página for nova ou mudou de rota.
5. Commit e push. GitHub Pages publica em ~1 minuto.

## Conteúdo médico — padrão de evidência

Quando escrever ou revisar conteúdo clínico:

- **Referências de base:** Campbell's Operative Orthopaedics, Rockwood and Green's
  Fractures in Adults, Insall & Scott Surgery of the Knee. Para evidência recente,
  buscar em PubMed (há MCP do PubMed disponível na conta).
- **Nunca inventar número.** Taxa de sucesso, tempo de recuperação, prevalência —
  só entram com fonte verificável. Sem fonte, escreva qualitativamente.
- **Sempre incluir o disclaimer:** conteúdo educativo, não substitui consulta médica.
- **Linguagem:** explicar para paciente leigo sem infantilizar. Frase curta. Sem jargão
  não explicado. O paciente chega com dor e medo — clareza é acolhimento.

## Skills e agentes deste projeto

| Recurso | Quando usar |
|---|---|
| `/nova-pagina` | Criar página nova com SEO, OG e schema.org completos desde o primeiro byte |
| `/publicar` | Validar tudo, atualizar sitemap e llms.txt, commitar e publicar |
| `revisor-cfm` (agente) | Revisar qualquer texto público contra as normas de publicidade médica |
| `task-observer` (skill) | Observa o trabalho da sessão e propõe melhorias nas skills |

## Task Observer — ativar no início da sessão

No começo de cada sessão de trabalho substancial neste repositório, carregue a skill
`task-observer` e mantenha-a ativa em segundo plano. Ela registra padrões, correções e
decisões desta sessão em `.claude/observacoes/` para virar melhoria de skill depois.
A skill só dispara de forma confiável quando invocada explicitamente — não conte com
o casamento automático por descrição.

## Ambiente

- Sessões remotas (Claude Code na web) rodam em container efêmero: **só o que é
  commitado sobrevive**. Instalação de plugin não persiste — use
  `scripts/instalar-cerebro.sh` para reconstruir o ambiente.
- Não existe `npm install`, `npm test` nem lint configurado. A validação do projeto é
  `python3 scripts/verificar-site.py` — apenas stdlib do Python 3.
