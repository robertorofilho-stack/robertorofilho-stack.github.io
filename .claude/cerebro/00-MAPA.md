# 🧠 MAPA — Ponto de entrada

> Vault Obsidian. Abre direto: `File → Open Vault → .claude/cerebro`
> Carregado automaticamente no início de cada sessão pelo hook `carregar-cerebro.sh`.

## Arquivos

| Arquivo | Conteúdo | Quando escrever |
|---|---|---|
| [[01-PERFIL]] | Quem é o operador, objetivos, ativos | Quando algo estrutural muda |
| [[02-MEMORIA]] | Log cronológico de tudo | **Toda sessão com resultado** |
| [[03-ATIVOS]] | Produtos, páginas, funis, conteúdos criados | Ao criar qualquer ativo |
| [[04-PLAYBOOKS]] | O que funcionou e o que não funcionou | Ao descobrir padrão |
| [[05-DECISOES]] | Decisões estratégicas e o porquê | Ao decidir algo relevante |
| [[06-METRICAS]] | Números reais observados | Ao medir qualquer coisa |
| [[APRENDIZADO-PROJETO-SUPREMO]] | Base técnica instalada | Referência |

## Protocolo

**Início de trabalho estratégico:** ler este mapa + o arquivo relevante.
**Fim de sessão com resultado:** gravar em [[02-MEMORIA]] e commitar.

Memória não commitada não existe. O contêiner morre; o repositório permanece.

## ⚠️ Fronteira de segurança

Este repositório é **público** e publica `www.drrobertorodrigues.com`.

**Nunca gravar aqui:**
- Dado de paciente, prontuário, imagem clínica, nome — em nenhuma forma
- Chave de API, token, senha, credencial
- Faturamento, número de clientes, contrato, dado financeiro pessoal
- Produto não lançado ou estratégia sensível a concorrente

### Vault privado (para o que é sensível)

Uma vez, no computador local:

```bash
gh repo create cerebro-privado --private --clone
cd cerebro-privado
mkdir -p financeiro clinico produtos-em-desenvolvimento credenciais
echo "credenciais/" > .gitignore
git add . && git commit -m "inicia cérebro privado" && git push -u origin main
```

Depois, em qualquer sessão: `claude --add-dir ~/cerebro-privado` — o Claude lê os dois vaults,
mas só o público é commitado aqui.
