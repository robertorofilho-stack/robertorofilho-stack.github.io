import { buscar, comRetry, limparHtml, normalizar } from "../util.ts";
import { RUIDO, CATEGORIAS_ALVO, GEOS } from "../config.ts";
import type { Sinal, ResultadoFonte } from "../tipos.ts";

/**
 * Google Trends — feed RSS público de buscas em alta.
 * Endpoint validado e estável: retorna termo + tráfego aproximado + notícias.
 *
 * Limite honesto: o RSS não expõe variação percentual nem filtro de categoria.
 * O que fazemos é usar o tráfego aproximado como proxy de volume e filtrar
 * ruído (esporte, celebridade, novela) por vocabulário.
 */
export async function coletarTrends(): Promise<ResultadoFonte> {
  const t0 = Date.now();
  const sinais: Sinal[] = [];

  try {
    for (const geo of GEOS) {
      const r = await comRetry(() =>
        buscar(`https://trends.google.com/trending/rss?geo=${geo}`)
      );
      if (!r.ok) continue;
      const xml = await r.text();

      for (const bloco of xml.split("<item>").slice(1)) {
        const termo = limparHtml(bloco.match(/<title>(.*?)<\/title>/s)?.[1] ?? "");
        if (!termo) continue;

        const n = normalizar(termo);
        if (RUIDO.some((r) => n.includes(r))) continue;
        if (termo.length < 3 || termo.length > 60) continue;

        const trafego = bloco.match(/<ht:approx_traffic>(.*?)<\/ht:approx_traffic>/)?.[1] ?? "0";
        const volume = parseInt(trafego.replace(/[^\d]/g, ""), 10) || 0;

        const noticias = [...bloco.matchAll(/<ht:news_item_title>(.*?)<\/ht:news_item_title>/gs)]
          .map((m) => limparHtml(m[1]))
          .join(" · ");

        const data = bloco.match(/<pubDate>(.*?)<\/pubDate>/)?.[1] ?? "";

        // Sinal só interessa se o contexto tocar tecnologia, negócio ou utilidade.
        const contexto = normalizar(`${termo} ${noticias}`);
        const relevante = CATEGORIAS_ALVO.some((c) => contexto.includes(c));

        sinais.push({
          fonte: "google-trends",
          termo,
          dor: noticias.slice(0, 240) || `Termo em alta: ${termo}`,
          url: `https://trends.google.com/trends/explore?q=${encodeURIComponent(termo)}&geo=${geo}`,
          data: data ? new Date(data).toISOString() : new Date().toISOString(),
          engajamento: relevante ? volume * 2 : volume,
          volumeEstimado: volume,
        });
      }
    }

    return { fonte: "google-trends", ok: true, sinais, duracaoMs: Date.now() - t0 };
  } catch (e) {
    return {
      fonte: "google-trends", ok: false, sinais: [],
      erro: e instanceof Error ? e.message : String(e),
      duracaoMs: Date.now() - t0,
    };
  }
}
