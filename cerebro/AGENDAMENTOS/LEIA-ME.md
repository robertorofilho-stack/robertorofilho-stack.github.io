# AGENDAMENTOS

Uma subpasta = um post.

## Como usar

1. Copie `_exemplo-copie-esta-pasta` com um nome novo, ou rode:

       python3 agendar.py novo dor-no-joelho-corredor

2. Coloque na pasta:
   - `video.mp4` (um só), **ou** as imagens (`foto1.jpg`, `foto2.jpg`… = carrossel)
   - `legenda.txt` — a legenda base, em português. A primeira linha é o gancho.
   - `config.json` — opcional (redes, horário, fuso).

3. Confira o que está pendente:

       python3 agendar.py listar

4. Agende:

       python3 agendar.py dor-no-joelho-corredor --em 10        # daqui a 10 min
       python3 agendar.py dor-no-joelho-corredor --data "amanha 11:00"
       python3 agendar.py todos --em 60                          # tudo que está pendente
       python3 agendar.py dor-no-joelho-corredor --seco          # simula, não envia

## O que acontece por baixo

- A legenda base é reescrita para **cada rede** pelo Claude Sonnet 5
  (gancho curto no TikTok, valor + pergunta no Instagram, tom profissional no
  LinkedIn, 280 caracteres no X…). Se o modelo falhar, usa a legenda base
  cortada no limite da rede — o post nunca morre por causa da legenda.
- O TikTok sai sempre **público**, com **comentário/duet/stitch liberados** e
  **marcado como conteúdo gerado por IA**.
- Depois de agendar, a pasta ganha um `.publicado.json` com o que foi enviado,
  o custo das legendas e a resposta da API. Isso impede republicar por engano
  (use `--forcar` se quiser mesmo repetir).
