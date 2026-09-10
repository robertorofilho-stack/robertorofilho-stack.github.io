---
name: laudo
description: Gera documentos médicos ortopédicos — laudo, relatório, justificativa de cirurgia para convênio, resposta a glosa ou negativa, atestado, parecer. Use para qualquer documento clínico formal.
argument-hint: "[tipo de documento + caso]"
effort: high
---

# Documento médico

**Pedido:** $ARGUMENTS

Delegue ao subagente `ortopedista`.

## Assinatura padrão

```
Dr. Roberto Rodrigues de Oliveira Filho
Médico Ortopedista e Traumatologista
CRM-CE 10806 · RQE 12256 · TEOT 17765
Membro Titular da SBOT
```

## Antes de escrever

Se faltar dado clínico essencial, **liste o que falta e escreva o documento com marcadores `[PREENCHER: ...]`**. Não invente achado clínico. Nunca.

---

## Laudo / relatório médico

```
IDENTIFICAÇÃO          nome, idade, documento
HISTÓRIA CLÍNICA       início, evolução, tratamentos prévios e resposta
EXAME FÍSICO           achados objetivos, testes específicos nomeados
EXAMES COMPLEMENTARES  achados de imagem, correlacionados com a clínica
HIPÓTESE DIAGNÓSTICA   com CID-10
CONDUTA                proposta terapêutica
JUSTIFICATIVA TÉCNICA  com referência (Insall & Scott / Campbell / AAOS)
PROGNÓSTICO
```

## Justificativa de cirurgia / autorização de convênio

**O leitor é um auditor médico procurando motivo para negar.** Escreva para fechar essa porta.

Elementos obrigatórios — a falta de qualquer um é motivo padrão de glosa:

1. **Falha do conservador documentada** — o que foi feito, por quanto tempo, com qual resultado. "Fisioterapia por 12 semanas sem melhora funcional sustentada" — não "tratamento conservador sem sucesso".
2. **Achado objetivo correlacionado** — exame físico **e** imagem apontando para o mesmo diagnóstico
3. **Diretriz que sustenta a indicação** — AAOS, SBOT, ESSKA, ou referência de livro-texto
4. **CID-10 e código TUSS corretos** — erro aqui é glosa automática
5. **Materiais justificados individualmente** — cada OPME com indicação técnica própria
6. **Consequência da não autorização** — progressão de dano, perda funcional, agravamento. Explicitada.

## Resposta a glosa ou negativa

Tom técnico e firme. Sem emoção, sem ameaça — evidência e norma.

1. Reafirmar o diagnóstico com os achados objetivos
2. Endereçar **o motivo específico** da negativa, ponto a ponto
3. Citar o dispositivo: Rol da ANS, RN vigente, Diretriz de Utilização (DUT)
4. Referência técnica que sustenta
5. Consequência clínica documentada da manutenção da negativa

## Regras absolutas

- **Toda afirmação clínica relevante com fonte:** `[Insall & Scott, cap. X]`, `[PMID: ...]`, `[AAOS CPG 2023]`
- Nunca inventar exame, achado, data ou evolução
- Linguagem técnica, defensável em auditoria e em juízo
- Sem promessa de resultado
- Quando a evidência for controversa (menisco degenerativo, PRP, viscossuplementação): **declarar a controvérsia** e justificar a conduta no caso concreto
