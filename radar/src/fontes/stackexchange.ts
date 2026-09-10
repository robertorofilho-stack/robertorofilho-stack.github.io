import { buscar, comRetry, limparHtml } from "../util.ts";
import { LIMITES } from "../config.ts";
import type { Sinal, ResultadoFonte } from "../tipos.ts";

/**
 * Stack Exchange API. Gratuita: 300 requisições/dia sem chave, 10.000 com chave.
 * Define STACKEXCHANGE_KEY no .env para subir o limite.
 *
 * Pergunta sem resposta aceita e com muita visualização = dor real sem solução.
 * É o sinal mais limpo de lacuna de ferramenta que existe.
 */
export async function coletarStackExchange(): Promise<ResultadoFonte> {
  const t0 = Date.now();
  const sinais: Sinal[] = [];
  const desde = Math.floor(Date.now() / 1000) - LIMITES.janelaDias * 86400;
  const chave = process.env.STACKEXCHANGE_KEY ? `&key=${process.env.STACKEXCHANGE_KEY}` : "";

  const buscas = [
    { site: "stackoverflow", q: "tool to convert" },
    { site: "stackoverflow", q: "how to automate" },
    { site: "softwarerecs", q: "tool" },
    { site: "webapps", q: "alternative" },
  ];

  try {
    for (const b of buscas) {
      const url =
        `https://api.stackexchange.com/2.3/search/advanced` +
        `?order=desc&sort=votes&q=${encodeURIComponent(b.q)}` +
        `&site=${b.site}&pagesize=20&fromdate=${desde}&filter=withbody${chave}`;

      const r = await comRetry(() => buscar(url, { headers: { "Accept-Encoding": "gzip" } }));
      if (!r.ok) continue;

      const dados = (await r.json()) as {
        items?: Array<{
          title: string; body?: string; link: string; score: number;
          view_count: number; answer_count: number; is_answered: boolean;
          creation_date: number;
        }>;
      };

      for (const it of dados.items ?? []) {
        // Pergunta já respondida não é lacuna de mercado.
        if (it.is_answered && it.answer_count > 2) continue;
        if (it.view_count < 50) continue;

        sinais.push({
          fonte: "stackexchange",
          termo: limparHtml(it.title).slice(0, 80),
          dor: limparHtml(it.body ?? it.title).slice(0, 320),
          url: it.link,
          data: new Date(it.creation_date * 1000).toISOString(),
          engajamento: it.score * 3 + Math.floor(it.view_count / 100),
          volumeEstimado: it.view_count,
        });
      }
      await new Promise((r) => setTimeout(r, 400));
    }

    return { fonte: "stackexchange", ok: true, sinais, duracaoMs: Date.now() - t0 };
  } catch (e) {
    return {
      fonte: "stackexchange", ok: false, sinais: [],
      erro: e instanceof Error ? e.message : String(e),
      duracaoMs: Date.now() - t0,
    };
  }
}
