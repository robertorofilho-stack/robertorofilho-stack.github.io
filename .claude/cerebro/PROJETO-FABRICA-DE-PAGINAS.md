# 🏭 Projeto Fábrica de Páginas

> Criado em 23/11/2026 por ordem do operador ("pode criar o Projeto Fábrica de Páginas").
> Páginas de volume no Instagram/TikTok, feitas por automação: vídeo de verdade, narração, gancho forte, postagem diária.
> Código: `.claude/helpers/volume/` (ver `LEIA-ME.md`). Produtos, preços e números de venda: só no mestre privado (§6).

## Páginas

| Conta | Tema | Motor | Ritmo | Estado |
|---|---|---|---|---|
| @omundocast | Notícias do Brasil e do mundo (g1, BBC News Brasil, The Guardian traduzido), fonte na tela | `esteira-noticias.py` + `paginas/omundocast.json` | 5/dia | ✅ testado · ⏳ servidor |
| @fala.vovo | Vovó: saúde com bom senso, golpes, família, casa | `pagina-temas.py` + `paginas/fala.vovo.json` | 3/dia | ✅ testado · ⏳ servidor |
| @mentepoder1 | Autoajuda, autoestima, lei da atração (como mentalidade), motivação | `pagina-temas.py` + `paginas/mentepoder1.json` | 3/dia | ✅ testado · ⏳ servidor |
| @poesia.narrada | Poesia em domínio público, voz masculina suave | `pagina-poesia.py` + `paginas/poesia.json` | 1/dia | ✅ testado · ⏳ criar conta + servidor |
| @falar.detudo | Fofoca e variedades | (a definir) | — | ⏸️ |
| política (direita/esquerda) | — | `esteira-noticias.py` com público | — | ⏸️ pausada pelo operador em 22/11 |

## Padrão de vídeo (decisões do operador)
- **Vídeo de verdade**, nunca foto passando (22/11) — `banco_videos.py`: Pexels → Pixabay → Mixkit → Wikimedia.
- **Sem avatar** (custo HeyGen ≈ R$ 9–17 por vídeo) — código guardado em `avatar_heygen.py`.
- **Narração um pouco mais lenta** (22/11): notícias −5%, mentepoder −12%, vovó −18%, poesia −22%.
- **Gancho** pelo método do Diretor de Ganchos (mestre, 15/11): quadro 0 forte + som em 0,2 s, frase ≤ 7 palavras.
- Fonte sempre citada em notícia; poesia só de autor morto há mais de 70 anos (Lei 9.610/98, art. 41).

## Custos de produção
Notícia ≈ US$ 0,01 (roteiro) · tema ≈ US$ 0,03 · poesia ≈ US$ 0,02 · vídeos de banco = R$ 0 · voz = R$ 0.

## Pendências
- [ ] Instalar no servidor + cron (`helpers/volume/LEIA-ME.md`), com `PEXELS_API_KEY`/`PIXABAY_API_KEY`/`OPENROUTER_API_KEY`
- [ ] Decidir: postar sozinho (Upload-Post 9/12/15/18/21h) ou aprovação manual (padrão atual)
- [ ] Criar @poesia.narrada
- [ ] Produto de cada página (definido no mestre) + link na bio
- [ ] Métricas semanais por página (alcance, seguidores, cliques no link) → [[06-METRICAS]]

## Histórico
[[02-MEMORIA]] de 18/11 a 22/11/2026: Sombra Viral → versão legal · notícia em vídeo · esteira · páginas de tema · avatar
(descartado por custo) · vídeo de verdade · poesia. Relaciona: memória do mestre `fabrica-video-curto-faceless`.
