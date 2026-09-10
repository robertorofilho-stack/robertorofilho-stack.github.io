---
name: saas
description: Constrói um micro-SaaS ou ferramenta web do zero até rodando — arquitetura, banco, código, interface, pagamento, deploy e QA. Use quando o pedido for construir um sistema, app, ferramenta, dashboard ou SaaS.
argument-hint: "[descrição do sistema]"
effort: high
---

# Construção de sistema

**Pedido:** $ARGUMENTS

Cascata multi-agente. **Erro zero: nada é entregue sem ter sido rodado e testado por você.**

---

## Fase 1 — Arquitetura (`arquiteto`)

Stack, modelo de dados, fluxos críticos, superfície de ataque, custo em 3 cenários, ordem de construção, critério de aceite.

**Padrão para produto não validado** (fuja dele só com justificativa escrita):
Next.js na Vercel · Supabase (Postgres + Auth + Storage + RLS) · Edge Functions · Stripe ou Mercado Pago/Asaas para Pix · Resend ou Brevo · PostHog

Custo com 0 usuários precisa ser ~R$0. Se não for, a arquitetura está errada para validar.

## Fase 2 — Banco
Migrations via MCP do Supabase quando disponível. **RLS ligada desde a primeira tabela** — nunca "depois". Índice no que é consultado. Tipos gerados para o front.

## Fase 3 — Código
Construir na ordem do arquiteto. A cada peça terminada: **rodar**. Não acumule código não executado.

- Segredo em variável de ambiente, nunca no bundle do cliente
- Validação no servidor, sempre. Validação só no cliente é decoração.
- Estado de erro e estado vazio em toda tela — não só o caminho feliz
- Mobile primeiro, 390px

## Fase 4 — Loop de erro zero

```
rodar → falhou? → capturar log completo → hipótese → corrigir → rodar de novo
```

**Não reporte problema. Reporte solução.** Só suba para o operador se o bloqueio for de credencial, permissão ou decisão de negócio — nunca um bug.

## Fase 5 — QA (`qa`, portão obrigatório)
Abrir no navegador real. Entrada hostil, estado quebrado, duplo clique no pagamento, 390px, offline, RLS de fato ativa, nenhuma chave vazada no bundle.

Bloqueante aberto = não entrega.

## Fase 6 — Deploy
Deploy real. Retornar a **URL funcionando**. Testar a URL de produção, não só o local — build de produção quebra o que dev não quebra.

## Fase 7 — Entrega

```
# [Sistema]
**URL:** [produção, testada]
**Admin:** [acesso]
**Stack:** [o quê e por quê]
**Custo:** R$X/mês em 0 usuários · R$Y em 1.000

## O que funciona
[testado, item por item]
## O que não funciona ainda
[honesto e específico]
## QA
[veredito + o que foi atacado]
## Próximos passos
## Preciso de você para
[só credencial, domínio, conta de pagamento — nada técnico]
```

---

## Fronteira honesta

O que **não** é automatizável, por design e não por limitação técnica:

- **Abrir conta de pagamento** — Stripe, Mercado Pago e Asaas exigem KYC vinculado a CPF/CNPJ. Identidade não se delega.
- **Validar que alguém quer** — só tráfego real e dinheiro real respondem isso. Código não valida mercado.
- **Contornar captcha ou bloqueio anti-bot** — viola termos de uso e derruba a conta. Não fazemos.

Tudo o mais entre a ideia e a URL em produção: sim.
