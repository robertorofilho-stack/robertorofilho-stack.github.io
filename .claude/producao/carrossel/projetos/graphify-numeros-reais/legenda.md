# Publicação — pronto para copiar

**Formato:** carrossel 11 slides · 1080×1350 · `imagens/01…11`
**Ordem:** os arquivos já estão numerados. Sobe na ordem.

---

## Legenda (copiar daqui)

O número que todo mundo repete sobre o Graphify não está no README.

Fui conferir na fonte: 119 mil estrelas, Apache-2.0, e o grafo realmente é construído sem gastar crédito de modelo — está na tabela do repositório, "LLM credits: 0". Isso é verdade, com um asterisco: vale para código. Docs, PDF e imagem passam por um modelo.

O que não é verdade é a manchete.

Não existe nenhum número de economia de token no README. Nenhum. O "70" que circula não é 70% — é 70x — e saiu de um blog de maio, que não cita benchmark nenhum.

O que está publicado é outra coisa: cobertura de fatos-chave subindo de 70,8% para 82,0% num repositório de um milhão de linhas, a cerca de 140 mil tokens por consulta. Número bom. Com uma letra miúda que ninguém posta: são seis perguntas. Seis. Rodadas no harness do próprio projeto.

E nos testes de memória: 45,3% no LOCOMO — onde o supermemory faz 49,7%, cobrando 11x mais para ingerir — e 76% no LongMemEval-S, empatado com um RAG denso comum.

A ferramenta é boa. A promessa que colaram nela é que não é.

Acertar mais e gastar menos são promessas diferentes. Confundir as duas é como escolher exame pelo folder do laboratório.

O teste que decide em cinco minutos: faça a mesma pergunta difícil sobre o seu código, com e sem o grafo. Compare a resposta e os tokens. Uma pergunta já mostra se serve para você.

Checado em 18/09/2026, no README e no BENCHMARKS.md do repositório. Salva para conferir antes de adotar.

---

## Isca de comentário (fixar no primeiro comentário)

> Qual número você já repetiu sem ter aberto a fonte? Eu começo: eu achava que era 70% de economia. Não é — e não está escrito em lugar nenhum do repositório.

## Hashtags (9 — suficiente; mais que isso não ajuda)

#graphify #claudecode #devtools #opensource #github #engenhariadesoftware #ia #programacao #knowledgegraph

---

## Ganchos alternativos para a capa (testar por 3 dias cada)

1. **O número que todo mundo repete não está no README** ← em uso
2. **119 mil estrelas e uma promessa que o repositório nunca fez**
3. **Não é 70%. É 70x. E não saiu do repositório.**
4. **O benchmark que todo mundo cita tem seis perguntas. Seis.**

> O gancho 4 é o mais forte para público técnico — polêmico e verificável.
> O 1 é o mais seguro para público misto.

---

## Reels / TikTok — 38 s (mesmo material, outro formato)

**0–3s (gancho, close, sem intro):**
"O número que todo mundo repete sobre o Graphify não está no README. Eu fui conferir."

**3–10s:**
"119 mil estrelas. Apache-2.0. E é verdade que constrói o grafo sem gastar crédito de modelo — está na tabela: LLM credits, zero. Para código."

**10–20s:**
"O que não existe é o '70'. Não tem nenhum número de economia de token no README. E o que circula não é 70 por cento — é setenta vezes. Saiu de um blog. Sem benchmark."

**20–30s:**
"O que está publicado: cobertura de 70,8 para 82 por cento, num repositório de um milhão de linhas. Bom número. Com seis perguntas. Seis."

**30–38s (fechamento + CTA):**
"A ferramenta é boa. A manchete é que não é. Faz a mesma pergunta com e sem o grafo e compara. Uma pergunta decide."

**Legenda do vídeo:** Fui na fonte antes de repetir. Checado em 18/09/2026.
**Texto na tela (fixo):** 70x ≠ 70% · n = 6

---

## Antes de publicar

- [ ] Reconferir as estrelas: `curl -s https://api.github.com/repos/Graphify-Labs/graphify | grep stargazers` — se passou de 120 mil, trocar o slide 1 e rodar `node render.mjs projetos/graphify-numeros-reais`
- [ ] Publicar em dia útil, 12h ou 19h (conteúdo técnico rende melhor no horário de almoço e no fim do expediente)
- [ ] Responder os 10 primeiros comentários em até 1h — é o que decide o alcance
