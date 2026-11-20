# Volume — esteira de notícias em vídeo explicado

| Arquivo | Faz |
|---|---|
| `noticia-em-video.py` | 1 link de notícia → vídeo 1080x1920 narrado, estilo colagem, com a fonte na tela + legenda `.txt` |
| `esteira-noticias.py` | Lê RSS (G1, BBC News Brasil, The Guardian, BBC World, Agência Brasil), escolhe as N mais fortes, gera os vídeos, guarda em `pendentes/AAAA-MM-DD/` e (opcional) agenda no Upload-Post |
| `renderizar.cjs` | Desenha os quadros no Chromium (Playwright de Node) |
| `template-em-lote.py` | Aplica moldura PNG do Canva numa pasta inteira de vídeos |
| `esteira-exemplo.json` | Configuração de uma página (copiar 1 por perfil) |

## Instalar no servidor (uma vez)
```bash
pip install --user edge-tts                       # voz pt-BR grátis
npm i -g playwright && npx playwright install chromium   # se ainda não houver Chromium do Playwright
export OPENROUTER_API_KEY=...                     # do cofre; nunca em arquivo versionado
```

## Uma página = um arquivo de configuração
Copie `esteira-exemplo.json`, troque `perfil`, `publico`, `fontes` e `pasta`. Público muda o ENFOQUE, nunca os fatos.

## Rodar todo dia (cron às 06:10, 5 vídeos)
```cron
10 6 * * * cd ~/robertorofilho-stack.github.io/.claude/helpers/volume && NODE_PATH=$(npm root -g) python3 esteira-noticias.py --config ~/esteira/explicadodehoje.json --quantos 5 >> ~/esteira/explicadodehoje.log 2>&1
```
Padrão seguro: `"publicar": {"via": "nenhum"}` → vídeos ficam em `pendentes/` para aprovação.
Automático: `"publicar": {"via": "upload-post", "usuario": "<usuário do Upload-Post>", "plataformas": ["instagram","tiktok"]}`
com `UPLOAD_POST_API_KEY` no ambiente → agenda 9h, 12h, 15h, 18h e 21h.

## Regras (não negociáveis)
- Só fatos da matéria; reescrito com palavras próprias; fonte sempre na tela e na legenda.
- Nenhuma foto da matéria (tem dono): imagens geradas por IA.
- Descarta crime com vítima comum identificável, tragédia com criança e boato.
- Custo: ~US$ 0,20 por vídeo (5/dia ≈ US$ 30/mês por página).
