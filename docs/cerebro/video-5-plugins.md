# "5 plugins de Claude Code" — transcrição e mapa do vídeo

**Autor:** Isaac Cardoso — [@isaque.prod](https://www.instagram.com/isaque.prod/)
**Formato:** vertical 720×1280, 90 s, português
**Analisado em:** setembro de 2026

Áudio transcrito com ElevenLabs Scribe v1 (confiança de idioma: 99,0% pt-BR);
telas lidas a partir de 45 frames extraídos a cada 2 segundos.

---

## Transcrição integral

> Este plugin grátis acabou de matar o limite de uso do Claude Code. Eu vou te mostrar
> cinco plugins nesse vídeo e esse aqui é só o primeiro.
>
> Ele se chama **OmniRoute** e conecta o seu Claude Code a mais de duzentos provedores
> de IA gratuitos. Quando o seu limite de uso acaba, ele troca sozinho para o próximo
> melhor modelo. Isso dá 1,6 bilhão de tokens de graça.
>
> O segundo é o **claude-mem**, que ele transfere a memória de uma sessão para outra.
> Então ele passa a lembrar dos seus projetos, dos seus arquivos, sem você precisar
> ficar explicando tudo de novo.
>
> O terceiro é o **Headroom**. Ele fica entre você e o modelo de inteligência
> artificial e só deixa passar aquilo que realmente importa, ele comprime o resto.
> Você tem o mesmo resultado gastando bem menos token.
>
> E o quarto é o **Claude Code Setup**. Ele é um plugin oficial da Anthropic. Ele lê o
> seu projeto inteiro e recomenda quais gatilhos, skills, subagentes e conexões MCPs
> que fazem sentido ali pro seu projeto. E tira tudo aquilo que é enfeite ou que é lixo.
>
> E por último, o **Task Observer**. Ele observa como você trabalha dentro do seu
> Claude, aprende todo o seu estilo e vai melhorando as suas outras skills em segundo
> plano.
>
> Comenta "pacote", que eu te mando o link de cada uma com alguns detalhes a mais.
> Meu nome é Isaac Cardoso e todo dia eu te mostro o que a IA está fazendo no mundo e
> nos negócios. Então já me segue aqui pra não perder nenhuma novidade.

---

## Dados mostrados nas telas

Números que aparecem em tela e não são ditos no áudio:

| Tela | Texto |
|---|---|
| OmniRoute | "124+ provedores de IA" · "357 provedores · 90+ de graça" · "1,6 BILHÃO tokens de graça" · "o teto sai do caminho" |
| claude-mem | "sessão que fecha → sessão que abre" · "o contexto atravessa junto com você" |
| Headroom | "o que sai de você → o que chega no modelo" · "ele comprime · menos tokens" |
| Claude Code Setup | "varredura do repositório · 13% do projeto" · lista: Gatilhos, Skills, Sub-agentes, Conexões MCP · "fica só o que serve ao projeto" |
| Task Observer | "ele olha você trabalhar · o seu estilo" · "skill 01 v1→v2 … em segundo plano" · "ele reescreve enquanto você nem olha" |

---

## Repositórios reais

Verificados um a um. O vídeo não mostra links; foram localizados por busca.

| # | Plugin | Repositório | Instalação |
|---|---|---|---|
| 1 | OmniRoute | [diegosouzapw/OmniRoute](https://github.com/diegosouzapw/OmniRoute) | gateway local em `localhost:20128/v1` |
| 2 | claude-mem | [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) | `/plugin marketplace add thedotmack/claude-mem` |
| 3 | Headroom | [headroomlabs-ai/headroom](https://github.com/headroomlabs-ai/headroom) | `pip install headroom-ai` |
| 4 | Claude Code Setup | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | `/plugin install claude-code-setup@claude-plugins-official` |
| 5 | Task Observer | [rebelytics/one-skill-to-rule-them-all](https://github.com/rebelytics/one-skill-to-rule-them-all) | copiar a skill para `.claude/skills/` |

---

## O que o vídeo não diz

Três coisas materiais ficaram de fora, e uma delas é decisiva:

1. **"Provedor gratuito" não é grátis.** O custo é o conteúdo que você manda. Para
   quem lida com dado de saúde, isso é um problema de LGPD, não de economia.
   Ver o veredito completo em [`README.md`](README.md).
2. **O "1,6 bilhão de tokens"** é a soma dos free tiers de centenas de provedores,
   não uma cota única e utilizável de ponta a ponta.
3. **Task Observer não dispara sozinho** de forma confiável. Precisa ser invocado no
   início da sessão — o próprio autor da skill documenta isso.

O plugin de maior retorno real é o **quarto** (oficial da Anthropic), que é
justamente o menos chamativo do vídeo.
