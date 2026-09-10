import { buscar, comRetry, extrairTermo, limparHtml } from "../util.ts";
import { FRASES_DOR_EN, FRASES_DOR_PT, LIMITES, UA } from "../config.ts";
import type { Sinal, ResultadoFonte } from "../tipos.ts";

/**
 * Reddit. Duas estratégias, nesta ordem:
 *
 *  1. API OAuth oficial — gratuita, 100 req/min, estável. É o caminho correto.
 *     Crie um app em https://www.reddit.com/prefs/apps (tipo "script") e
 *     preencha REDDIT_CLIENT_ID e REDDIT_CLIENT_SECRET no .env.
 *
 *  2. Endpoint .json público — sem credencial. Funciona em IP residencial,
 *     mas o Reddit bloqueia IP de datacenter. Em GitHub Actions ou VPS,
 *     costuma falhar. É fallback, não plano principal.
 *
 * Subreddits escolhidos por densidade de dor comercializável.
 */
const SUBS = [
  "SomebodyMakeThis", "AppIdeas", "SaaS", "Entrepreneur",
  "smallbusiness", "webdev", "productivity", "NoStupidQuestions",
  "brasil", "empreendedorismo",
];

async function token(): Promise<string | null> {
  const id = process.env.REDDIT_CLIENT_ID;
  const secret = process.env.REDDIT_CLIENT_SECRET;
  if (!id || !secret) return null;

  const r = await buscar("https://www.reddit.com/api/v1/access_token", {
    method: "POST",
    headers: {
      Authorization: `Basic ${Buffer.from(`${id}:${secret}`).toString("base64")}`,
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: "grant_type=client_credentials",
  });
  if (!r.ok) return null;
  return ((await r.json()) as { access_token?: string }).access_token ?? null;
}

export async function coletarReddit(): Promise<ResultadoFonte> {
  const t0 = Date.now();
  const sinais: Sinal[] = [];
  const tk = await token().catch(() => null);

  const base = tk ? "https://oauth.reddit.com" : "https://www.reddit.com";
  const headers: Record<string, string> = tk
    ? { Authorization: `Bearer ${tk}`, "User-Agent": "radar-lucro/1.0 by u/roberto" }
    : { "User-Agent": UA };

  const frases = [...FRASES_DOR_EN.slice(0, 6), ...FRASES_DOR_PT.slice(0, 3)];
  const desde = Date.now() - LIMITES.janelaDias * 86400_000;

  try {
    for (const sub of SUBS) {
      const url = `${base}/r/${sub}/new.json?limit=50`;
      const r = await comRetry(() => buscar(url, { headers })).catch(() => null);
      if (!r?.ok) continue;

      const ct = r.headers.get("content-type") ?? "";
      if (!ct.includes("json")) continue; // bloqueio devolve HTML

      const dados = (await r.json()) as {
        data?: { children?: Array<{ data: Record<string, unknown> }> };
      };

      for (const c of dados.data?.children ?? []) {
        const p = c.data as {
          title?: string; selftext?: string; permalink?: string;
          score?: number; num_comments?: number; created_utc?: number;
        };
        const texto = limparHtml(`${p.title ?? ""} ${p.selftext ?? ""}`);
        if (texto.length < 40) continue;
        if ((p.created_utc ?? 0) * 1000 < desde) continue;

        const frase = frases.find((f) => texto.toLowerCase().includes(f));
        if (!frase) continue;

        sinais.push({
          fonte: "reddit",
          termo: extrairTermo(texto, frase),
          dor: texto.slice(0, 320),
          url: `https://reddit.com${p.permalink ?? ""}`,
          data: new Date((p.created_utc ?? 0) * 1000).toISOString(),
          engajamento: (p.score ?? 0) + (p.num_comments ?? 0) * 2,
          volumeEstimado: ((p.score ?? 0) + 1) * 50,
        });
      }
      await new Promise((r) => setTimeout(r, 600));
    }

    if (!tk && sinais.length === 0) {
      return {
        fonte: "reddit", ok: false, sinais: [],
        erro: "Reddit bloqueia IP de datacenter sem OAuth. Defina REDDIT_CLIENT_ID e REDDIT_CLIENT_SECRET no .env.",
        duracaoMs: Date.now() - t0,
      };
    }
    return { fonte: "reddit", ok: true, sinais, duracaoMs: Date.now() - t0 };
  } catch (e) {
    return {
      fonte: "reddit", ok: false, sinais: [],
      erro: e instanceof Error ? e.message : String(e),
      duracaoMs: Date.now() - t0,
    };
  }
}
