---
name: veredito
description: Veredito rápido e verificado sobre uma novidade que o operador manda — vídeo, Reel, PDF, guia, repositório, ferramenta, protocolo, recurso novo de IA ("e esse?", "que acha desse?", "assiste", "olha isso"). Responde se serve para ELE, com prova, e o que fazer ou não fazer.
argument-hint: "[link, PDF ou texto colado]"
effort: medium
---

# Veredito de novidade

**Alvo:** $ARGUMENTS

O operador manda novidades em sequência. Ele não quer resumo: quer saber **se isso põe dinheiro ou autoridade no
bolso dele, agora**, e o que fazer.

## Passos (nesta ordem)
1. **Ler o alvo inteiro.** Vídeo do YouTube ou Instagram → `python3 .claude/helpers/aprender/assistir-video.py <url>`
   (Flash para checagem barata, Pro para transcrição). PDF → Read com páginas. Repositório → README + estrelas, licença,
   data do último commit, dependências pagas.
2. **Recall antes de opinar.** `grep -ril "<nome>"` no satélite e em `../cerebro-backup/claude-config/memory` (clone
   esparso basta). Se já foi estudado, dizer isso e não reestudar. Nome parecido ≠ mesmo projeto (ex.: Argos Atlas × ARGOS
   do Cérebro).
3. **Conferir as afirmações que decidem** em fonte independente (WebSearch). Números do autor são do autor: marcar
   divergência entre fontes. Disponibilidade no **Brasil** é pergunta obrigatória (muita novidade é só EUA).
4. **Julgar pelo filtro do operador:** gera receita, autoridade médica ou automação real? Ele já tem algo que faz isso
   (inventário do mestre)? Custo, risco legal/CFM/LGPD, Receita/BCB quando envolver cripto.
5. **Responder em 4 blocos:** o que é (conferido) · a verdade sem anestesia · o que fazer (ou não) · o que copiar (formato,
   modelo de negócio). Fontes no fim, com link.
6. **Gravar** uma entrada curta em `.claude/cerebro/02-MEMORIA.md` com veredito e motivo, e commitar.

## Regras
- Persona sintética, enxame de agentes e "previsão" sem backtest não decidem nada; o sinal é anúncio > 30 dias e pagamento.
- Não instalar código de terceiro só porque apareceu; se valer teste, propor teste com teto de gasto e critério de adoção.
- Ação que exige login/conta do operador: dizer exatamente onde clicar; não pedir senha.

## Origem
Episódios reais de 03/10–13/11/2026 que repetiram o mesmo trabalho (02-MEMORIA):
- 03/10 — 2 vídeos do YouTube ("Maestros da IA", VPS Oracle): recomendação sem recall custou bronca → passo 2.
- 08/11 — Reel do Pedrão da Licitação: já estudado em 13/09; exemplo do vídeo já auditado → passo 2 e 3.
- 08/11 — "Personal Finance" da Anthropic: só EUA; caminho brasileiro era o Belvo MCP → pergunta do Brasil no passo 3.
- 13/11 — Reel "empresa no ChatGPT": novidade real, mas fora do alcance de negócio local brasileiro.
- 13/11 — MiroFish: sem benchmark; teste independente igual a 1 chamada simples → regra de persona sintética.
- 13/11 — x402: protocolo sério, receita mediana US$ 0,50/mês; números divergentes entre fontes.
- 13/11 — Argos Atlas (PDF VibeHub): agregador de dado público; nome igual a projeto do Cérebro.
