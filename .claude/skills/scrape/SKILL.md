---
name: scrape
description: Extrai negócios do Google Maps (nome, telefone, WhatsApp, e-mail, site, Instagram/Facebook/LinkedIn, nota, endereço) com o scraper local gosom/google-maps-scraper e devolve planilha limpa para prospecção no Brasil. Use em "me traz os dentistas de Fortaleza", "lista de clínicas em X", "leads do Google Maps", "sobe o scraper", "/scrape <termo>". Também alimenta a campanha da skill prospeccao-com-agentes do mestre. NÃO é para Instagram/TikTok (isso é Apify no mestre).
argument-hint: "<termo com cidade> [--cidade 'Cidade, UF'] [--rapido] [--por-bairros arquivo] [--redes] [--campanha ~/prospeccao/x]"
effort: medium
---

# /scrape — leads do Google Maps, de graça, na sua máquina

**Pedido:** $ARGUMENTS

O scraper roda num contêiner Docker local (porta 8080, só o seu computador enxerga). Você cria um job
pela API, espera, baixa o CSV, limpa e entrega. Tudo que é determinístico é código em `leads/`;
o seu papel é escolher termo e cidade, rodar, interpretar o resultado e dizer o próximo passo de venda.

## Passo 0 — está de pé?

```bash
curl -s http://localhost:8080/api/v1/jobs
```
`null` ou `[]` = de pé e sem busca. Falhou? `docker compose -f leads/docker-compose.yml up -d`, espere 10 s, tente de novo.
Sem Docker instalado: pare e peça ao operador para abrir o Docker Desktop (docker.com) e esperar ficar verde —
é a única coisa que você não faz por ele. Porta ocupada: `cp leads/.env.example leads/.env` e mude `SCRAPER_PORT`.

## Passo 1 — rodar (uma busca por vez)

```bash
python3 leads/scrape.py "clínicas de fisioterapia em Fortaleza CE" --cidade "Fortaleza, CE" --profundidade 5 --redes
```
- **Cidade dentro do termo** ("… em Fortaleza CE") — o script tira a cidade do termo; `--cidade "Cidade, UF"` quando não houver. Capitais e cidades grandes resolvem sem rede; outras usam Nominatim.
- **Profundidade 5** na primeira vez (≈ 40–60 negócios por termo). Só suba depois que a primeira passou.
- Vários termos no **mesmo job**: `--termo "dentistas em Fortaleza CE" --termo "ortodontia em Fortaleza CE"`, ou `--arquivo leads/exemplos/termos.txt`.
- `--redes` visita o site de cada negócio: Instagram/Facebook/LinkedIn, e-mail e **o WhatsApp do botão do site** (zero token: é regex, não LLM).
  Nunca faça isso com WebFetch um a um — custa milhares de tokens e o script faz de graça.
- `--rapido` = `fast_mode`: ~20 por termo em segundos (nome, telefone, site, nota, endereço). **Na nuvem é o único modo que traz dados**
  (IP de datacenter recebe a ficha vazia); o script cai nele sozinho quando o modo completo devolve fichas vazias. Para passar de 20,
  `--por-bairros leads/exemplos/bairros-fortaleza.txt` (um termo por bairro, no mesmo job). `--sem-email` desliga a visita do scraper aos sites.
- `--de-csv leads/dados/x-bruto.csv --redes` reprocessa/enriquece um CSV bruto já baixado, sem nova busca.
- O poll usa `sleep` dentro do script: rode em **segundo plano** (`run_in_background`) e leia a saída quando avisar.

Saída em `leads/dados/<termo>-<data>.csv` (planilha), `.json` (formato Apify) e `.md` (resumo com os 15 melhores).
Códigos de saída: 1 = erro (argumento, API, download que não é CSV) · 2 = zero resultados (termo sem negócios ou IP limitado; passa em 1–2 h) ·
3 = todas as fichas vazias (modo rápido também vazio, ou `--sem-fallback`). Timeout? O job segue no scraper: retome com `--job <id>`.

## Passo 2 — entregar

Mostre o `.md` (contagens + tabela), diga quantos são **sem site** (candidato direto a oferta de site/presença digital)
e quantos têm celular/WhatsApp. Não despeje o CSV inteiro no chat: mostre 5 linhas e o caminho do arquivo.

## Passo 3 — ponte com o mestre (prospeccao-com-agentes)

Se o operador vai prospectar, grave direto na campanha dele: `--campanha ~/prospeccao/<nicho>` cria `raw/<nome>.json`
no mesmo formato do ator da Apify, e o resto do pipeline do mestre segue igual:
`ranquear.py` (score por avaliações × nota × sem site) → `validar_whatsapp.py` → abordagem. Custo da captura: R$ 0,
contra ~US$ 0,002/lugar na Apify (e o teto de US$ 1/semana que ele tem lá).

## Leis que valem aqui (não são conselho)

1. **⛔ Nunca disparo frio por WhatsApp comum** (lei do mestre, número banido 2× em set/2026). A lista serve para:
   e-mail frio (`mkt-cold-email`), anúncio, ligação, formulário, ou API oficial da Meta com template. Jamais Z-API/Evolution para quem nunca falou com ele.
2. **LGPD:** dado público de empresa, base legal legítimo interesse (art. 7, IX). Quem pedir descadastro sai. **Nunca revender a lista.**
3. **Um job por vez, profundidade baixa.** Jobs grandes seguidos = IP limitado por horas. `--proxies` só para volume de verdade.
4. Isto é dado de empresa, não de paciente. Nada aqui vai para o site médico nem para conteúdo clínico.

## Onde isso roda

| Lugar | Serve para | Limite |
|---|---|---|
| Mac (Docker Desktop) | uso diário, IP residencial (menos bloqueio) | precisa do Docker aberto |
| Mac mini 24/7 | `restart: unless-stopped` + agendamento (`launchd`/cron) | é o "servidor" de verdade do operador |
| Nuvem (sessão do Claude Code) | `bash leads/nuvem.sh` sobe daemon + contêiner com o proxy da sessão; depois é o mesmo `scrape.py` | contêiner efêmero: entregue o CSV ao operador (SendUserFile) antes de fechar |
| GitHub Actions | avulso, sem Mac ligado | IP de datacenter: bloqueio mais provável; não é o caminho principal |

## Origem

- `ep-2026-10-12-0001` — operador trouxe o tutorial da AutomateFlow (kit Mahanaicoach sobre gosom) e perguntou "isso está rodando no servidor?"; subimos o daemon Docker na nuvem, reproduzimos a resposta `null`, descobrimos que `lang` exige 2 letras, que o modo completo volta vazio de IP de datacenter e que o `fast_mode` resolve: 20 clínicas de fisioterapia de Fortaleza em 12 s, 7 sem site, 8 com WhatsApp no site.
- Skill `prospeccao-com-agentes` do mestre (campanhas `~/prospeccao/clinicas` e `~/prospeccao/escritorios`, 2026-08/09): a captura pela Apify tinha teto de US$ 1/semana — esta skill é o motor gratuito que alimenta o mesmo `ranquear.py`.
- Conselho de 2026-09-10 (05-DECISOES): primeiro produto com viés **B2B profissional** — lista de negócio local é o insumo dessa frente.
