---
name: publicar
description: >
  Publica alterações do site com segurança: valida SEO e JSON-LD de todas as páginas,
  sincroniza sitemap.xml e llms.txt, revisa compliance e faz o commit. Use quando
  pedirem para publicar, subir, colocar no ar, fazer deploy ou commitar mudanças
  do site.
disable-model-invocation: true
---

# Publicar o site

`main` é produção. Push aqui vai ao ar em ~1 minuto via GitHub Pages. Não pule etapas.

## Sequência

### 1. Ver o que mudou

```bash
git status --short
git diff --stat
```

Se houver arquivo inesperado no diff, pare e pergunte antes de seguir.

### 2. Barreira de privacidade

Antes de qualquer commit, confirme que **nenhum** arquivo alterado contém:

- nome, imagem, exame, laudo ou relato clínico de paciente identificável
- telefone pessoal que não seja o comercial já público `(85) 99762-4221`
- token, chave de API, credencial ou `.env`

O repositório é **público**. Um commit com dado de paciente é violação de LGPD
(art. 11 — dado sensível de saúde) e não se apaga do histórico do Git com um
`git rm` depois. Na dúvida, não commite.

### 3. Validar as páginas

```bash
python3 scripts/verificar-site.py
```

Precisa terminar com "Site limpo". Se acusar problema, corrija — não publique
com aviso pendente. O que ele checa: SEO/OG obrigatórios, JSON-LD válido,
canonical correto, `alt` de imagem, links internos quebrados, sitemap nos dois
sentidos e links do `llms.txt`.

### 4. Sincronizar o sitemap

```bash
python3 scripts/atualizar-sitemap.py --conferir   # ver o que muda
python3 scripts/atualizar-sitemap.py              # aplicar
```

Ele só mexe no `lastmod` das páginas que o git aponta como alteradas — nada de
carimbar o site inteiro com a data de hoje, o que degrada a confiança do crawler.

### 5. Atualizar o llms.txt

Se entrou, saiu ou mudou de rota alguma página, ajuste `llms.txt` à mão na seção
correta. É o arquivo que os buscadores com IA leem para entender o site.
O `verificar-site.py` acusa link morto ali, mas não adiciona link novo sozinho.

### 6. Compliance, se houve texto novo

Se o diff inclui texto voltado ao público, rode o agente `revisor-cfm` antes de
publicar. Resolução CFM 2.336/2023.

### 7. Commit

Mensagem em português, no imperativo, dizendo o efeito — não o arquivo:

```
Adiciona página de tendinite patelar com FAQ e schema
Corrige canonical da página de prótese do joelho
Atualiza convênios aceitos
```

```bash
git add -A
git commit -m "<mensagem>"
git push -u origin <branch>
```

### 8. Conferir no ar

Aguarde ~1 minuto e confirme que a URL responde e que o conteúdo novo aparece.
Para páginas novas, vale pedir indexação no Google Search Console.

## Se algo quebrar em produção

```bash
git revert <hash>   # reverte o commit ruim e mantém o histórico
git push
```

Nunca reescreva o histórico da `main`.
