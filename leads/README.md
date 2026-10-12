# leads/ — negócios do Google Maps, limpos para prospecção no Brasil

> O que o tutorial da AutomateFlow ensina a montar à mão, aqui já vem montado, em português, com telefone no
> padrão brasileiro, link de WhatsApp, e-mail, redes sociais e uma ponte direta para a máquina de prospecção do Cérebro.
> Motor: [gosom/google-maps-scraper](https://github.com/gosom/google-maps-scraper) (open source, roda na sua máquina, R$ 0 por lead).

## O que você vai montar

Você diz o tipo de negócio e a cidade. Volta uma planilha com nome, telefone, WhatsApp, e-mail, site, Instagram/Facebook/LinkedIn,
nota, número de avaliações, bairro e endereço. Nada sai para a nuvem; não existe conta para criar.

## Antes de começar (uma vez)

1. **Docker Desktop** instalado e aberto (docker.com). Espere o ícone ficar verde.
2. **Terminal** aberto na pasta do repositório.
3. **Claude Code** (opcional, mas é o pulo do gato): com ele aberto na pasta, `/scrape dentistas em Fortaleza CE` faz tudo sozinho.

## Passo a passo

```bash
# 1. subir o scraper na sua máquina (porta 8080, só o seu computador enxerga)
docker compose -f leads/docker-compose.yml up -d

# 2. conferir se está de pé  → resposta esperada: null ou []
curl http://localhost:8080/api/v1/jobs

# 3. primeira busca (profundidade 5 ≈ 40–60 negócios por termo; --redes visita o site de cada um)
python3 leads/scrape.py "dentistas em São Paulo SP" --cidade "São Paulo, SP" --profundidade 5 --redes
```

Saída em `leads/dados/`:

| Arquivo | Para quê |
|---|---|
| `<termo>-<data>.csv` | abrir no Excel / Google Sheets |
| `<termo>-<data>.json` | formato do ator da Apify — a skill `prospeccao-com-agentes` do mestre lê direto |
| `<termo>-<data>.md` | resumo: contagens + os 15 melhores |

Colunas do CSV: `nome, categoria, telefone, telefone_e164, tipo_telefone, whatsapp, emails, site, instagram, facebook, linkedin,
whatsapp_site, nota, avaliacoes, endereco, bairro, cidade, uf, maps, sem_site, sem_redes, place_id, termo`.

### Opções que importam

| Flag | Efeito |
|---|---|
| `--cidade "Fortaleza, CE"` | centro da busca (capitais e cidades grandes do CE resolvem sem rede; o resto via Nominatim) |
| `--termo "..."` (repetível) / `--arquivo termos.txt` | vários termos **num job só** (ex.: `leads/exemplos/termos.txt`) |
| `--profundidade N` | rolagem nos resultados. 5 primeiro; suba depois |
| `--redes` | Instagram, Facebook, LinkedIn, e-mail e **o WhatsApp do botão do site** (regex, zero token de IA) |
| `--rapido` | `fast_mode` do scraper: ~20 por termo em **segundos**, com nome, telefone, site, nota, endereço (sem horário/avaliações detalhadas). **É o modo que funciona de IP de nuvem/datacenter** |
| `--por-bairros "Aldeota,Meireles"` ou arquivo | um termo por bairro, **no mesmo job** — é como o modo rápido passa de 20 para centenas (`leads/exemplos/bairros-fortaleza.txt`) |
| `--sem-email` | modo completo sem o scraper visitar sites atrás de e-mail |
| `--de-csv x-bruto.csv` | reprocessa um CSV bruto já baixado (sem nova busca): dá para enriquecer depois |
| `--campanha ~/prospeccao/clinicas` | grava `raw/<nome>.json` na campanha do mestre; depois é só `ranquear.py` |
| `--motor docker` | sem `compose up`: roda `docker run --rm` uma vez e sai |
| `--proxies http://u:s@host:porta,...` | só para volume de verdade (o scraper exige usuário e senha em proxy HTTP) |
| `--bruto` | guarda também o CSV original de 34 colunas |

Códigos de saída: `2` = zero resultados (termo sem negócios **ou** IP limitado; passa em 1–2 h) · `3` = as fichas vieram vazias
(o Google serviu a página sem dados). **Sem você fazer nada**, quando o modo completo devolve fichas vazias o script refaz em
modo rápido sozinho (`--sem-fallback` desliga isso).

## O jeito Claude (sem digitar comando)

Abra a pasta no Claude Code e peça em português: *"sobe o scraper e me traz as clínicas de fisioterapia de Fortaleza com telefone e site"*.
A skill `/scrape` sabe subir o contêiner, criar a busca em segundo plano, esperar, limpar as duplicadas e te mostrar o resumo.

## Onde isso roda ("isso está rodando no servidor?")

| Lugar | Serve para | Limite |
|---|---|---|
| **Seu Mac** (Docker Desktop) | uso diário; IP residencial é o que menos bloqueia | o Docker precisa estar aberto |
| **Mac mini ligado 24/7** | o servidor de verdade: `restart: unless-stopped` + agendamento (`launchd`/cron) | — |
| **Nuvem (sessão do Claude Code)** | provar, desenvolver, rodar uma busca avulsa | contêiner efêmero: baixe o CSV antes de fechar; IP de datacenter |
| **GitHub Actions** | avulso sem Mac ligado | IP de datacenter, bloqueio mais provável; não é o caminho principal |

Na nuvem do Claude Code: `bash leads/nuvem.sh` faz tudo (liga o daemon, sobe o contêiner com o proxy e o certificado da sessão, espera a API).
Por baixo, o comando que funcionou (Chromium lê o proxy pelo ambiente; o campo `proxies` do job **não** serve porque o scraper exige usuário e senha):

```bash
docker run -d --name gmaps --network host \
  -e HTTPS_PROXY=$HTTPS_PROXY -e https_proxy=$HTTPS_PROXY -e NO_PROXY="$NO_PROXY" -e no_proxy="$NO_PROXY" \
  -e SSL_CERT_FILE=/root/.ccr/ca-bundle.crt \
  -v /root/.ccr/ca-bundle.crt:/root/.ccr/ca-bundle.crt:ro -v /root/.pki:/root/.pki:ro \
  gosom/google-maps-scraper:v1.18.1 -web -data-folder /gmapsdata -addr 127.0.0.1:8080
```

## Prova (rodado de verdade nesta sessão, 12/10/2026)

Nuvem do Claude Code, saída do proxy em IP do Google Cloud (EUA), imagem `v1.18.1`:

| Etapa | Resultado |
|---|---|
| `docker run` + `GET /api/v1/jobs` | `null` em 10 s (igual ao tutorial) |
| Job **completo** (`fast_mode:false`), pt e en | 20 fichas visitadas com "success", **todas sem dados** (só o link). Sonda no Chromium: o Google entrega o bloco `APP_INITIALIZATION_STATE` com 4 KB e sem o nome do negócio para este IP, com qualquer agente de navegador. Não é idioma; é IP de datacenter |
| Job **rápido** (`fast_mode:true`), 1 termo | **20 clínicas em 12 s**: telefone 20/20 (18 celulares), site 13/20, nota e endereço em todas |
| `--redes` (visita aos 13 sites pelo proxy) | 8 s: Instagram 8 · Facebook 4 · LinkedIn 2 · **WhatsApp no botão do site 8** · e-mail 3 · **sem site 7/20 (35%)** |
| 3 bairros (`--por-bairros`), modo completo → **fallback automático** para rápido, ao vivo | **59 clínicas únicas em 1m30**; 33 sites visitados: Instagram 19 · Facebook 15 · LinkedIn 10 · WhatsApp no site 17 · e-mail 11 |
| `--motor docker --rapido` (sem o compose de pé; `docker run --rm` avulso) | 20 pet shops de Fortaleza em **2 s**, telefone 20/20 |
| Campo `proxies` do job com o proxy da sessão | falha: `username and password are required` (o scraper exige credencial em proxy HTTP). Solução: proxy pelo ambiente do contêiner |

No seu Mac (IP residencial) o modo completo tende a funcionar como no tutorial (é o que o autor do kit relata: 60 dentistas em SP).
Na nuvem, use `--rapido` + `--por-bairros`. Em qualquer lugar, o script cai para o modo rápido sozinho quando as fichas vêm vazias.

## Use com cabeça

- **Uma busca por vez, profundidade 5.** Muita coisa junta faz o Google limitar o IP por algumas horas. Passa sozinho, mas atrapalha.
- **E-mail deixa mais lento.** Para achar e-mail o scraper visita o site de cada negócio. Quer velocidade: `--rapido`.
- **Dado de empresa é para você entrar em contato, não para revender lista.** LGPD: base legal é o legítimo interesse
  (art. 7, IX); quem pedir descadastro sai na hora.
- **⛔ Nunca disparo frio por WhatsApp comum.** Lei do Cérebro (número banido duas vezes em setembro/2026). A lista alimenta
  e-mail frio, anúncio, ligação, formulário ou a API oficial da Meta com template aprovado — jamais Z-API/Evolution para quem nunca falou com você.
- Isto é dado de empresa, não de paciente. Nada daqui entra no site médico nem em conteúdo clínico.

## Perguntas rápidas

- **Porta 8080 ocupada?** `cp leads/.env.example leads/.env`, mude `SCRAPER_PORT`, suba de novo. O `scrape.py` lê o mesmo arquivo.
- **Mac com chip Apple não sobe?** Descomente `platform: linux/amd64` no `docker-compose.yml`.
- **`invalid lang`?** A API aceita só código de 2 letras (`pt`), não `pt-BR`.
- **Cidade grande (SP, Rio, BH)?** Um raio de 10 km não cobre. Busque por zona/bairro no termo: "dentistas na Zona Sul São Paulo".
- **Interface e documentação da API:** http://localhost:8080 e http://localhost:8080/api/docs.

## Testes

```bash
python3 leads/testes/testar_leads.py     # só biblioteca padrão; roda também no saude.yml
```

## Créditos

Motor: [gosom/google-maps-scraper](https://github.com/gosom/google-maps-scraper) (MIT). O passo a passo e a ideia da
busca de redes por regex vêm do [kit da Mahanaicoach](https://github.com/Mahanaicoach/google-maps-scraper-kit), reescritos
aqui para o Brasil (telefone, WhatsApp, LGPD, ponte com `prospeccao-com-agentes`).
