import { buscar, comRetry, extrairTermo, limparHtml } from "../util.ts";
import { FRASES_DOR_EN, LIMITES } from "../config.ts";
import type { Sinal, ResultadoFonte } from "../tipos.ts";

/**
 * Hacker News via API do Algolia. Gratuita, sem autenticação, sem limite prático.
 *
 * A melhor fonte de dor técnica pagante que existe aberta: o público do HN
 * constrói software, tem cartão corporativo e reclama em texto pesquisável.
 */
export async function coletarHackerNews(): Promise<ResultadoFonte> {
  const t0 = Date.now();
  const sinais: Sinal[] = [];
  const desde = Math.floor(Date.now() / 1000) - LIMITES.janelaDias * 86400;

  try {
    for (const frase of FRASES_DOR_EN) {
      const url =
        `https://hn.algolia.com/api/v1/search?query=${encodeURIComponent(`"${frase}"`)}` +
        `&tags=(comment,story)&hitsPerPage=20` +
        `&numericFilters=${encodeURIComponent(`created_at_i>${desde}`)}`;

      const r = await comRetry(() => buscar(url));
      if (!r.ok) continue;

      const dados = (await r.json()) as {
        hits?: Array<{
          objectID: string; comment_text?: string; title?: string; story_title?: string;
          points?: number; num_comments?: number; created_at?: string;
        }>;
      };

      for (const h of dados.hits ?? []) {
        const texto = limparHtml(h.comment_text ?? h.title ?? "");
        if (texto.length < 30) continue;

        const termo = extrairTermo(texto, frase);
        if (termo.length < 6) continue;

        sinais.push({
          fonte: "hackernews",
          termo,
          dor: texto.slice(0, 320),
          url: `https://news.ycombinator.com/item?id=${h.objectID}`,
          data: h.created_at ?? new Date().toISOString(),
          engajamento: (h.points ?? 0) + (h.num_comments ?? 0) * 2,
          volumeEstimado: ((h.points ?? 0) + 1) * 100,
        });
      }
      await new Promise((r) => setTimeout(r, 350)); // gentileza com a API
    }

    return { fonte: "hackernews", ok: true, sinais, duracaoMs: Date.now() - t0 };
  } catch (e) {
    return {
      fonte: "hackernews", ok: false, sinais: [],
      erro: e instanceof Error ? e.message : String(e),
      duracaoMs: Date.now() - t0,
    };
  }
}
