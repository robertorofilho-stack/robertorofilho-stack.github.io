# Motor de videoaula (31/10/2026)

Gera videoaulas explicativas com telas animadas (sem clone, sem rosto) a partir de um JSON por aula:
narração por voz de IA (ElevenLabs, trechos separados por `<break time="1.2s" />`) → `sincronizar.py` detecta as pausas
com `ffmpeg silencedetect` e monta a linha do tempo → `render.mjs` renderiza quadro a quadro (`aula.html`, `window.renderAt(t)`,
Playwright + ffmpeg, 1920×1080 30 fps) → `mux.sh` junta a narração com atraso da abertura e normaliza (−14 LUFS) →
`quadros.mjs` gera a folha de conferência → `producao.sh` encadeia tudo. As capas (`capas.mjs`) e a nomeação da entrega (`entregar.sh`) são do produto e ficam só no mestre privado.

Cenas disponíveis em `aula.html`: `titulo`, `card` (frase com palavras entrando), `passos`, `checklist`, `terminal` (digitação),
`navegador`, `pastas`, `celular` (vídeo em pé com gancho, legenda palavra a palavra, nome, zoom, flash), `documento`, `lista`,
`antesdepois`, `medidor`, `colunas`, `premium` (padrão cena A/B), `fim`. Realce: `**teal**`, `__serifa__`.

Formato do JSON de aula: `{id, rotulo, titulo, sub, selo, trechos:[{fala, cena:{tipo,...}, tiles:[...]}]}` (ver `aulas_parte1.py`
no mestre privado; o conteúdo das aulas é produto, não entra aqui).

Medido em 31/10: 1,7× o tempo real por fila (4 vCPU), 4 filas em paralelo; 18 aulas (~16 min) em ~25 min.
Uso: `python3 narrar_prep.py aulas/x.json` → TTS → `bash producao.sh x` → `saida/final/x.mp4`.
Origem: missão do curso "Edita com IA" (31/10/2026), memória em `.claude/cerebro/02-MEMORIA.md`.
