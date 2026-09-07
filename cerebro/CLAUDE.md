# Cérebro — arquitetura das automações

> Este arquivo documenta a pasta `cerebro/`. Se você já tem um `CLAUDE.md` na
> raiz do Mac mini, **cole a seção "Divisão de responsabilidades" abaixo nele**
> em vez de substituir o arquivo inteiro.

---

## Divisão de responsabilidades

| Serviço | Papel | Situação |
|---|---|---|
| **OpenRouter** | **Texto**: pesquisa, roteiro, legenda. Fallback automático se cair. | **ATIVO** — entrada principal |
| **APIMart** | **Vídeo e voz** + **backup de texto** quando o OpenRouter falha | **ATIVO** |
| **Upload-Post** | **Publicação e agendamento** em TikTok, Instagram, YouTube, LinkedIn e outras | **ATIVO** — entrada principal |
| **fal.ai** | Geração de vídeo | **ATIVO** (sem mudança) |
| **ElevenLabs** | Narração | **ATIVO** (sem mudança) |
| **ffmpeg** | Montagem local | **ATIVO** (sem mudança) |
| **Higgsfield** | Publicação | **DESATIVADO** — manter a chave no `.env`, **não usar** |

Regra curta: **texto → OpenRouter** (cai para APIMart), **vídeo/voz → APIMart,
fal.ai e ElevenLabs**, **publicação → Upload-Post**. Higgsfield não entra em
nenhum fluxo novo.

---

## Fluxo diário (11h)

```
pesquisa  ── openrouter_client.pesquisar()  → google/gemini-3.8-flash
roteiro   ── openrouter_client.roteiro()    → anthropic/claude-sonnet-5
vídeo     ── fal.ai            (via apimart_client)   [sem mudança]
voz       ── ElevenLabs        (via apimart_client)   [sem mudança]
montagem  ── ffmpeg local                             [sem mudança]
legenda   ── openrouter_client.legenda()    → anthropic/claude-sonnet-5
publicação── uploadpost_client.publicar_video()  → TikTok + Instagram
```

Se o OpenRouter estiver fora do ar, as três etapas de texto caem sozinhas no
`apimart_client` e o dia não para.

---

## Modelos e custo

IDs conferidos em `openrouter.ai/api/v1/models` em **2026-09-07**.

| Tarefa | Modelo | US$/1M entrada | US$/1M saída |
|---|---|---:|---:|
| pesquisa / resumo | `google/gemini-3.8-flash` | 0,75 | 3,75 |
| roteiro | `anthropic/claude-sonnet-5` | 2,00 | 10,00 |
| legenda | `anthropic/claude-sonnet-5` | 2,00 | 10,00 |
| trivial | `openai/gpt-5-nano` | 0,05 | 0,40 |

Trocar modelo **sem mexer no código** — basta o `.env`:

```
OPENROUTER_MODELO_PESQUISA=google/gemini-3.1-flash-lite   # 3x mais barato
OPENROUTER_MODELO_TRIVIAL=openai/gpt-oss-20b              # o mais barato de todos
```

Aliases que acompanham sozinhos o modelo mais novo (o preço pode mudar sem
aviso): `~google/gemini-flash-latest`, `~anthropic/claude-sonnet-latest`.

Cada chamada grava uma linha em `logs/custos.jsonl`. Para ver o acumulado:

```bash
python3 openrouter_client.py custos
```

---

## Regras fixas de publicação

**TikTok** (definido em `TIKTOK_PADRAO`, dentro de `uploadpost_client.py` —
mudar lá muda as duas automações de uma vez):

- `privacy_level=PUBLIC_TO_EVERYONE` — público
- `disable_comment=False`, `disable_duet=False`, `disable_stitch=False` — tudo liberado
- `is_aigc=True` — marcado como conteúdo gerado por IA
- `post_mode=DIRECT_POST` — publica direto, sem passar por rascunho

**Todas as redes**: `is_ai_generated=True` (disclosure de IA onde a rede aceita).

Publicação automática sem revisão está autorizada pelo dono do sistema.

---

## Arquivos

| Arquivo | O que faz |
|---|---|
| `uploadpost_client.py` | Publica, agenda, lista perfis, consulta status. Retry 3x, log em `logs/publicacao.log` |
| `openrouter_client.py` | Pesquisa/roteiro/legenda com fallback para APIMart e custo por chamada |
| `agendar.py` | Lê `AGENDAMENTOS/<pasta>`, adapta a legenda por rede e agenda |
| `configurar_chaves.py` | Grava chave no `.env` sem apagar as outras (com backup) |
| `patch_automacoes.py` | Acha e troca os pontos de Higgsfield/APIMart-texto nas automações |
| `testar.py` | Bateria offline (sem chave) e online (com chave) |
| `instalar.sh` | Instala dependências, cria pastas e roda a bateria offline |

---

## Comandos do dia a dia

```bash
# Instalação (uma vez)
bash instalar.sh
python3 configurar_chaves.py --upload-post SUA_CHAVE
python3 configurar_chaves.py --openrouter SUA_CHAVE

# Conferir
python3 uploadpost_client.py perfis          # redes conectadas
python3 openrouter_client.py modelos         # modelos e preços
python3 testar.py --online                   # bateria real

# Publicar / agendar
python3 agendar.py novo minha-ideia
python3 agendar.py listar
python3 agendar.py minha-ideia --em 10
python3 uploadpost_client.py agendar video.mp4 "Legenda" --em 10

# Custos
python3 openrouter_client.py custos
```

---

## Segurança

- Chave **nunca** entra no código. Só no `.env`, que está no `.gitignore`.
- `configurar_chaves.py` faz backup (`.env.bak`) e deixa o `.env` em modo `600`.
- Chave nunca é impressa inteira na tela — sempre mascarada.
