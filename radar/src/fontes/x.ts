import { buscar } from "../util.ts";
import { FRASES_DOR_EN, FRASES_DOR_PT } from "../config.ts";
import type { Sinal, ResultadoFonte } from "../tipos.ts";

/**
 * X (Twitter).
 *
 * REALIDADE, SEM ROTEIO: desde 2023 a busca do X exige autenticação. Não existe
 * raspagem gratuita e estável. As opções reais são:
 *
 *   a) API oficial — plano Basic, US$ 200/mês, 10 mil tweets/mês de leitura.
 *      Defina X_BEARER_TOKEN no .env e este adaptador liga sozinho.
 *   b) Não usar. HN, Stack Exchange e Reddit entregam sinal de dor comparável
 *      ou melhor, de graça. O X é mais rápido, mas muito mais ruidoso.
 *
 * Sem token, este adaptador retorna vazio de propósito — e diz o porquê.
 * Fingir que raspa X sem credencial seria mentira embutida em código.
 */
export async function coletarX(): Promise<ResultadoFonte> {
  const t0 = Date.now();
  const bearer = process.env.X_BEARER_TOKEN;

  if (!bearer) {
    return {
      fonte: "x", ok: false, sinais: [],
      erro: "X_BEARER_TOKEN ausente. A busca do X exige API paga (Basic, ~US$200/mês). Adaptador inativo — HN e Stack Exchange cobrem o mesmo sinal de graça.",
      duracaoMs: Date.now() - t0,
    };
  }

  const sinais: Sinal[] = [];
  try {
    const frases = [...FRASES_DOR_EN.slice(0, 4), ...FRASES_DOR_PT.slice(0, 2)];
    for (const frase of frases) {
      const q = encodeURIComponent(`"${frase}" -is:retweet lang:en OR lang:pt`);
      const url =
        `https://api.x.com/2/tweets/search/recent?query=${q}` +
        `&max_results=25&tweet.fields=public_metrics,created_at`;

      const r = await buscar(url, { headers: { Authorization: `Bearer ${bearer}` } });
      if (!r.ok) continue;

      const dados = (await r.json()) as {
        data?: Array<{
          id: string; text: string; created_at: string;
          public_metrics?: { like_count: number; retweet_count: number; reply_count: number };
        }>;
      };

      for (const t of dados.data ?? []) {
        const m = t.public_metrics;
        sinais.push({
          fonte: "x",
          termo: t.text.slice(0, 80),
          dor: t.text.slice(0, 320),
          url: `https://x.com/i/status/${t.id}`,
          data: t.created_at,
          engajamento: (m?.like_count ?? 0) + (m?.retweet_count ?? 0) * 3 + (m?.reply_count ?? 0) * 2,
          volumeEstimado: ((m?.like_count ?? 0) + 1) * 30,
        });
      }
      await new Promise((r) => setTimeout(r, 1000));
    }
    return { fonte: "x", ok: true, sinais, duracaoMs: Date.now() - t0 };
  } catch (e) {
    return {
      fonte: "x", ok: false, sinais: [],
      erro: e instanceof Error ? e.message : String(e),
      duracaoMs: Date.now() - t0,
    };
  }
}
