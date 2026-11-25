# 📘 Playbooks

> O que funciona. Extraído de resultado observado, não de teoria.
> Regra: só entra aqui depois de ter sido testado ao menos uma vez.

## Validado por evidência externa

### Anúncio ativo há mais de 30 dias = prova de lucro
Ninguém queima verba 30 dias no prejuízo. É o sinal mais confiável e mais barato de mercado
que existe — e é público (Meta Ads Library, TikTok Creative Center).
Aplicação: nunca propor produto sem checar biblioteca de anúncios primeiro.

### Front-end paga o tráfego, back-end é o lucro
Quem tenta lucrar no produto de entrada não escala. Perde no leilão para quem aceita
empatar na entrada e lucra no bump e no upsell.

### Gancho é 90% do vídeo curto
Retenção nos 3 primeiros segundos decide tudo. Nenhum conteúdo bom depois salva
gancho ruim. Compartilhamento e salvamento pesam mais que like.

### Garantia forte aumenta conversão mais do que custa em reembolso
Quase sempre. Testar antes de assumir o contrário.

### Loop de verificação mata alucinação
Entregar sem rodar é apostar. Abrir no navegador, rodar o teste, checar a saída real —
custa minutos e economiza retrabalho de horas.

## Aprendido na operação

_A preencher com resultado real._

| Padrão | Evidência | Data |
|---|---|---|

## Antipadrões

### Pesquisa rasa é a falha mais cara
Uma busca, uma fonte, nenhuma contradição procurada = conclusão errada com cara de certeza.
Mínimo: 3 fontes independentes + busca ativa por quem discorda.

### Otimizar sem medir é superstição
Todo funil tem UM gargalo dominante. Mexer em qualquer outra coisa é desperdício.

### Volume sem encaixe queima o nome
Vale para grants, para parceria e para pitch. Dez propostas genéricas marcam você
como ruído. As bancas se falam.

## Clone do Roberto (vídeo ou foto) — 25/11/2026
- **Antes de gerar qualquer clone: ler `governanca/RECEITA-VIDEO-CLONE.md` no mestre.** Só o método oficial (LEI 29/10).
  Higgsfield Soul/Element/Intone, HeyGen foto e Nano Banana NÃO são o clone dele, mesmo estando na conta.
- Na nuvem o clone não roda (chave APIMart no Keychain, Seed-VC no servidor). Fazer pacote de passagem no mestre
  (`bridges/PASSAGEM-*`: roteiros.txt no formato do `gerar_dia.py` + fotos + legenda + MISSAO.md) e dar ao operador 1 comando.

## Vídeo-notícia premium SEM clone, na nuvem — 25/11/2026
- Gancho "a última conversa": mensagem/fala real da pessoa numa tela de celular no quadro 0 + SFX de notificação. Nunca inventar mensagem.
- Esteira pronta no mestre: `projetos/video-noticia-sem-clone/` (copiar a pasta, trocar falas/cenas/overlay). QA = folha de 24 quadros antes de entregar.
- Voz brasileira na nuvem sem chave: Edge TTS `pt-BR-AntonioNeural` via `msedge-tts` no sandbox do Higgsfield (grátis). As vozes do Higgsfield são americanas. ElevenLabs (Nassif/Cristian) só com a chave do cofre do Mac.
- Pedido feito do celular: não depender de comando no Mac; resolver na nuvem e entregar o arquivo.
