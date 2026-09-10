---
name: tendencia
description: Detecta uma tendência em ascensão e converte em ferramenta web monetizável em 24-72h. Use para "fábrica de micro-SaaS", aproveitar trend, criar ferramenta rápida, ou transformar demanda emergente em produto.
argument-hint: "[área a monitorar, ou 'varrer' para busca aberta]"
effort: high
---

# Tendência → ferramenta → receita

**Alvo:** $ARGUMENTS

Tese: quando um termo explode, existe uma janela curta em que a demanda cresce mais rápido que a oferta de soluções. Quem coloca uma ferramenta simples nessa janela captura receita residual.

**Portfólio, não aposta.** A maioria vai render zero. O modelo só funciona no agregado: 20 tentativas, 2-3 acertos que pagam as 17 falhas.

---

## Fase 1 — Detecção

| Fonte | Sinal |
|---|---|
| Google Trends | breakout, +200% em 7-30 dias |
| Autocomplete + "pessoas também perguntam" | intenção de tarefa ("como fazer X", "conversor de X") |
| X / Reddit / Hacker News | reclamação repetida sobre falta de ferramenta |
| Product Hunt | o que sobe e o que os comentários dizem que falta |
| Changelog de API grande | mudança que quebra fluxo de muita gente = demanda instantânea |
| App Store / Chrome Web Store | busca alta, oferta ruim (avaliações baixas) |

**Filtro de qualificação — os quatro juntos:**
1. É uma **tarefa**, não um assunto. ("conversor de X" sim, "notícia sobre X" não)
2. Alguém **já paga** por algo parecido
3. Dá para resolver com **uma página** e nenhum login complexo
4. Não depende de API cara ou de licença

Falhou em um: descarte. Existem outras tendências.

## Fase 2 — Decisão (30 min, máximo)

```
Termo · Crescimento · Concorrentes atuais e qualidade deles
Tarefa exata que a ferramenta faz
Por que a solução atual é ruim
Preço: grátis com limite → R$9-29 avulso ou R$19-49/mês
Tempo de construção estimado
```

**Passou de 3 dias de construção? Reduza o escopo ou descarte.** A janela fecha.

## Fase 3 — Construção
Rode `/saas`. Escopo mínimo viável de verdade:
- Uma página, uma função, resultado em menos de 10 segundos
- Uso grátis limitado, pagamento para remover o limite (Pix + cartão)
- Sem cadastro no caminho grátis — cadastro mata conversão em ferramenta de utilidade

## Fase 4 — Indexação e distribuição

Verdade sobre SEO: **Google leva de dias a semanas, não horas.** Quem prometer indexação em horas está mentindo. Por isso a distribuição inicial não vem do Google:

- Publicar onde a dor foi detectada — a thread do Reddit, o comentário no X, o fórum
- Product Hunt, Hacker News (Show HN), Indie Hackers
- Título e H1 casando exatamente com o termo de busca
- Schema.org, OG tags, sitemap, `llms.txt` (ferramenta descoberta por IA é canal novo e subexplorado)
- Submeter ao Search Console no dia do deploy

## Fase 5 — Medir e cortar

Após **14 dias**:

| Resultado | Ação |
|---|---|
| Zero tráfego | matar, arquivar o código, seguir |
| Tráfego sem venda | testar preço uma vez; se não resolver, matar |
| Venda acontecendo | investir: mais funcionalidade, SEO, anúncio |

Manter ferramenta morta custa atenção — o recurso mais escasso. **Matar rápido é a habilidade central deste modelo.**

---

## Expectativa honesta

- 50 ferramentas por semana é irreal. **1-2 por semana** com qualidade é sustentável e já é agressivo.
- A maior parte fará R$0. Isso é o modelo funcionando, não falhando.
- Receita residual real aparece por volta da 15ª-20ª ferramenta, não da terceira.
- O ativo composto não é nenhuma ferramenta: é o **domínio, a lista de e-mails e a velocidade** que você acumula.

Registre cada tentativa em `.claude/cerebro/03-ATIVOS.md`, inclusive as mortas. O padrão do que funciona só aparece com N.
