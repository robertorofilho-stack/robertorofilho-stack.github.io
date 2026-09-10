# ⚖️ Decisões

> Decisão registrada é decisão que não se refaz do zero. Anotar o **porquê** importa mais
> que anotar o quê — é o porquê que envelhece bem ou mal.

## Tomadas

### 2026-09-10 — Cérebro público separado de cérebro privado
**Contexto:** o repositório do site é público e serve o domínio médico.
**Decisão:** metodologia e playbooks ficam aqui; dado de paciente, financeiro,
credencial e produto não lançado vão para repositório privado separado.
**Alternativa rejeitada:** vault único. Risco inaceitável — dado de paciente em repositório
público é infração ética e de LGPD, não é "descuido".
**Reversível?** Sim, mas o vazamento não. Assimetria decide.

### 2026-09-10 — Infraestrutura de agente no repositório, não em prompt
**Contexto:** conhecimento passado em conversa se perde ao fim da sessão.
**Decisão:** método vira arquivo versionado que carrega sozinho.
**Porquê:** conversa evapora, arquivo compõe. Cada sessão futura começa no topo, não no zero.

## Em aberto

- [ ] **Primeiro nicho de infoproduto** — aguarda `/cacar-produto aberto`
- [ ] **Vault privado criado?** — comando em [[00-MAPA]]
- [ ] **Meta Ads / Supermetrics conectados à conta real de anúncio?**
- [ ] **Gateway de pagamento definido** — Hotmart/Kiwify (mais simples) vs Stripe+Asaas (mais margem, mais trabalho)
