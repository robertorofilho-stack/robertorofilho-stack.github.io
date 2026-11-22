# Volume — esteira de notícias em vídeo explicado

| Arquivo | Faz |
|---|---|
| `noticia-em-video.py` | 1 link de notícia → vídeo 1080x1920 narrado, estilo colagem, com a fonte na tela + legenda `.txt` |
| `esteira-noticias.py` | Lê RSS (G1, BBC News Brasil, The Guardian, BBC World, Agência Brasil), escolhe as N mais fortes, gera os vídeos, guarda em `pendentes/AAAA-MM-DD/` e (opcional) agenda no Upload-Post |
| `renderizar.cjs` | Desenha os quadros no Chromium (Playwright de Node) |
| `template-em-lote.py` | Aplica moldura PNG do Canva numa pasta inteira de vídeos |
| `pagina-temas.py` | Página de tema fixo → Reels de 20–35 s com GANCHO VISUAL ABSURDO no quadro 0 (método do Diretor de Ganchos), voz da persona, impacto sonoro, legenda; não repete tema |
| `avatar_heygen.py` | Modo apresentador: avatar da HeyGen fala o roteiro inteiro; gancho absurdo, cortes de imagem e textos sobrepostos. `"via":"simulado"` testa sem gastar |
| `paginas/*.json` | Configs prontas: `mentepoder1` (autoajuda), `fala.vovo` (vovó: saúde e vida com bom senso), `omundocast` (esteira de notícias) |
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

## Páginas de tema (cron às 06:20 e 13:20, 3 vídeos por vez)
```cron
20 6,13 * * * cd ~/robertorofilho-stack.github.io/.claude/helpers/volume && NODE_PATH=$(npm root -g) python3 pagina-temas.py --config paginas/mentepoder1.json --quantos 3 >> ~/esteira/mentepoder1.log 2>&1
25 6,13 * * * cd ~/robertorofilho-stack.github.io/.claude/helpers/volume && NODE_PATH=$(npm root -g) python3 pagina-temas.py --config paginas/fala.vovo.json --quantos 3 >> ~/esteira/fala.vovo.log 2>&1
10 6 * * * cd ~/robertorofilho-stack.github.io/.claude/helpers/volume && NODE_PATH=$(npm root -g) python3 esteira-noticias.py --config paginas/omundocast.json --quantos 5 >> ~/esteira/omundocast.log 2>&1
```
O gerador de imagem às vezes recusa (filtro de segurança): o script tenta uma versão simbólica e, se falhar, reaproveita outra imagem do mesmo vídeo.

## Apresentador HeyGen (@fala.vovo = "Maria", @omundocast = "Humberto")
Precisa de `HEYGEN_API_KEY` no ambiente do servidor. O script procura o avatar pelo NOME nos looks privados da conta;
se não achar, ponha `"look_id"` (e `"voice_id"`, se quiser outra voz) no bloco `avatar` da config.
Custo HeyGen (medido 02/10/2026): ~US$ 4,7/min (gêmeo digital 1080p) → Reel de 20–40 s ≈ US$ 1,6–3,1; em 720p e talking photo, menos.
