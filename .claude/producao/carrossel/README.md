# Fábrica de carrossel

Transforma um arquivo `slides.json` em imagens 1080×1350 prontas para publicar.
Sem Canva, sem arrastar caixinha, sem refazer layout a cada post. Escreve o texto, roda um comando.

```bash
node render.mjs projetos/<pasta>            # gera imagens/01…NN.jpg + preview.html
node render.mjs projetos/<pasta> --png      # PNG sem perda (arquivo ~3x maior)
node render.mjs projetos/<pasta> --preview  # só o HTML, sem abrir o Chromium
```

## Como criar um carrossel novo

1. `cp -r projetos/graphify-numeros-reais projetos/<novo>` e apague `imagens/`
2. Reescreva `slides.json`
3. `node render.mjs projetos/<novo>`
4. As imagens saem em `projetos/<novo>/imagens/`, numeradas na ordem de publicação

## Tipos de slide

| `tipo` | Para quê | Campos |
|---|---|---|
| `capa` | primeiro slide, sem contador | `titulo`, `texto` |
| `carta` | card padrão | `n`, `titulo`, `rotulo`, `texto`, `codigo`, `legenda` |
| `numero` | quando o dado É a mensagem | `n`, `titulo`, `numero`, `texto` |
| `fecho` | último slide | `titulo`, `texto`, `blocos[]`, `fonte` |

Campos comuns: `arquivo` (nome do PNG/JPG), `acao` (CTA do rodapé), `claro` (fundo claro).
Em `meta`: `chapeu` (faixa do topo), `assinatura` (@ do rodapé), `formato` (`[1080,1350]`).
No texto, `*entre asteriscos*` vira **negrito**.

## Verificação automática

O render mede se o texto cabe no slide e **falha com código 2** se estourar, listando quais.
Slide que estoura corta no feed e ninguém percebe antes de publicar — por isso é erro, não aviso.

## Tipografia

`fontes.css` traz Cormorant Garamond + Manrope embutidas em base64 (mesmo sistema visual do site).
Render roda offline e sempre igual. Para regerar: `node fontes.mjs`.

## Dependências

Node ≥ 22 e Playwright. O script acha o Playwright em `radar/node_modules` e usa o Chromium
do ambiente (`/opt/pw-browsers/chromium`, ou `CHROMIUM_BIN=...`). Nada mais para instalar.

## Regra

Número em slide exige fonte primária conferida e datada — o projeto guarda isso em `FATOS.md`,
ao lado do `slides.json`. Post sem esse arquivo é rascunho, não é entrega.
