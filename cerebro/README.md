# Cérebro — Upload-Post + OpenRouter

Duas ferramentas novas para as automações diárias das contas
**Falar de Tudo** (TikTok) e **Vitrine IA** (@vitrineia_):

- **Upload-Post** substitui o Higgsfield na publicação, e passa a publicar no
  Instagram automaticamente (hoje isso é manual).
- **OpenRouter** roda pesquisa, roteiro e legenda em modelo barato, com
  fallback automático para a APIMart se cair.

Vídeo continua no fal.ai. Voz continua no ElevenLabs. Montagem continua no ffmpeg.

---

## Instalação no Mac mini

```bash
# 1. Traga o código para a pasta do cérebro
cd ~/onde/fica/o/cerebro
git clone -b claude/upload-post-openrouter-integration-va0qln \
  https://github.com/robertorofilho-stack/robertorofilho-stack.github.io.git /tmp/cerebro-novo
cp -r /tmp/cerebro-novo/cerebro/* .

# 2. Instale (não apaga nada do que já existe)
bash instalar.sh
```

O `instalar.sh` instala as dependências, cria `logs/` e `AGENDAMENTOS/`,
preserva o `.env` que já existe e roda a bateria de testes offline.

---

## Colar as chaves

As chaves vão para o `.env` **sem apagar as que já estão lá** (o script faz
backup em `.env.bak` antes de mexer):

```bash
python3 configurar_chaves.py --upload-post   up_xxxxxxxxxxxx
python3 configurar_chaves.py --upload-post-user NOME_DO_PERFIL
python3 configurar_chaves.py --openrouter    sk-or-v1-xxxxxxxx
python3 configurar_chaves.py --ver           # confere (mascarado)
```

**Onde pegar cada chave:**

| Ferramenta | Passo a passo |
|---|---|
| Upload-Post | `upload-post.com` → criar conta → painel `app.upload-post.com` → **Manage API Keys** → gerar → em **Social Accounts**, conectar TikTok e Instagram |
| OpenRouter | `openrouter.ai` → entrar com Google → **Credits** → colocar saldo (US$ 10 dura muito) → **Keys** → *Create Key* |

---

## Testar

```bash
python3 testar.py --offline    # sem chave, sem internet — prova a lógica
python3 testar.py --online     # com as chaves — perfis, modelos, fallback
python3 testar.py --online --e2e video.mp4   # ponta a ponta, agenda em 10 min
```

---

## Usar

```bash
# Ver as redes conectadas
python3 uploadpost_client.py perfis

# Publicar agora
python3 uploadpost_client.py publicar video.mp4 "Minha legenda" --redes tiktok,instagram

# Agendar para daqui a 10 minutos
python3 uploadpost_client.py agendar video.mp4 "Minha legenda" --em 10

# Fluxo por pasta (legenda adaptada para cada rede)
python3 agendar.py novo dor-no-joelho
#   → coloque video.mp4 e edite legenda.txt na pasta criada
python3 agendar.py listar
python3 agendar.py 2026-09-07-dor-no-joelho --em 10

# Texto
python3 openrouter_client.py pesquisa "tendências de dor no joelho"
python3 openrouter_client.py roteiro "roteiro de 45s sobre artrose"
python3 openrouter_client.py custos
```

---

## Trocar as automações que já existem

```bash
python3 patch_automacoes.py --pasta ~/caminho/das/automacoes     # só mostra
python3 patch_automacoes.py --pasta ~/caminho/das/automacoes --aplicar
python3 patch_automacoes.py --pasta ~/caminho/das/automacoes --reverter
```

O diagnóstico mostra arquivo e linha de cada ponto que fala com o Higgsfield ou
que usa a APIMart para texto. O `--aplicar` troca só o que é mecanicamente
seguro (imports), faz backup `.bak`, e marca o resto com `# TODO CEREBRO` para
revisão — ele **não** reescreve chamada de API no escuro, porque isso quebra
produção.

No código, a troca é esta:

```python
# ANTES (Higgsfield)
hf.tiktok_publish(video=caminho, caption=texto)

# DEPOIS (Upload-Post)
from uploadpost_client import UploadPostClient
UploadPostClient().publicar_video(caminho, texto, ["tiktok", "instagram"])
```

```python
# ANTES (APIMart para texto)
script = api.chat(f"roteiro sobre {tema}")

# DEPOIS (OpenRouter, com fallback automático para a APIMart)
from openrouter_client import roteiro
script = roteiro(f"roteiro sobre {tema}").texto
```

---

Arquitetura completa, modelos, preços e regras de publicação: **`CLAUDE.md`**.
