#!/usr/bin/env node
/**
 * RADAR-LUCRO — detector de oportunidade de micro-SaaS.
 *
 * Varre fontes públicas em paralelo, cruza dor declarada com termo em alta,
 * pontua e grava oportunidades em dados/oportunidades.json.
 *
 *   node --experimental-strip-types radar-lucro.ts            # varredura única
 *   node --experimental-strip-types radar-lucro.ts --watch    # loop a cada 60min
 *   node --experimental-strip-types radar-lucro.ts --top 5    # só o top N
 *
 * Em produção 24/7, o modo correto NÃO é --watch numa máquina ligada:
 * é o cron do GitHub Actions em .github/workflows/radar.yml — gratuito,
 * sem servidor, com histórico versionado.
 */
import { writeFile, readFile, mkdir } from "node:fs/promises";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

import { coletarTrends } from "./src/fontes/trends.ts";
import { coletarHackerNews } from "./src/fontes/hackernews.ts";
import { coletarStackExchange } from "./src/fontes/stackexchange.ts";
import { coletarReddit } from "./src/fontes/reddit.ts";
import { coletarX } from "./src/fontes/x.ts";
import { agrupar, pontuar } from "./src/pontuacao.ts";
import { LIMITES } from "./src/config.ts";
import { log } from "./src/util.ts";
import type { Oportunidade, ResultadoFonte } from "./src/tipos.ts";

const RAIZ = dirname(fileURLToPath(import.meta.url));
const ARQUIVO = join(RAIZ, "dados", "oportunidades.json");

async function carregarAnteriores(): Promise<Oportunidade[]> {
  try {
    return JSON.parse(await readFile(ARQUIVO, "utf8")) as Oportunidade[];
  } catch {
    return [];
  }
}

async function varrer(): Promise<Oportunidade[]> {
  log("info", "Varredura iniciada");

  // Todas as fontes em paralelo. Uma falhar não derruba as outras.
  const resultados: ResultadoFonte[] = await Promise.all([
    coletarTrends(),
    coletarHackerNews(),
    coletarStackExchange(),
    coletarReddit(),
    coletarX(),
  ]);

  for (const r of resultados) {
    if (r.ok) log("ok", `${r.fonte}: ${r.sinais.length} sinais (${r.duracaoMs}ms)`);
    else log("aviso", `${r.fonte}: ${r.erro}`);
  }

  const sinais = resultados.flatMap((r) => r.sinais);
  log("info", `${sinais.length} sinais brutos`);
  if (sinais.length === 0) return [];

  const grupos = agrupar(sinais);
  log("info", `${grupos.length} grupos após deduplicação`);

  const novas = grupos
    .map(pontuar)
    .filter((o) => o.score >= LIMITES.scoreMinimo)
    .sort((a, b) => b.score - a.score);

  // Mescla com o histórico, preservando estado de quem já foi construída.
  const anteriores = await carregarAnteriores();
  const mapa = new Map(anteriores.map((o) => [o.id, o]));

  for (const nova of novas) {
    const antiga = mapa.get(nova.id);
    if (antiga) {
      // Já conhecida: atualiza score e evidência, preserva o estado.
      mapa.set(nova.id, {
        ...nova,
        estado: antiga.estado,
        produtoSugerido: antiga.produtoSugerido,
        fontes: [...new Set([...antiga.fontes, ...nova.fontes])].slice(0, 12),
      });
    } else {
      mapa.set(nova.id, nova);
    }
  }

  const todas = [...mapa.values()].sort((a, b) => b.score - a.score).slice(0, 300);

  await mkdir(dirname(ARQUIVO), { recursive: true });
  await writeFile(ARQUIVO, JSON.stringify(todas, null, 2), "utf8");

  const altas = todas.filter((o) => o.urgencia === "ALTA" && o.estado === "NOVA");
  log("ok", `${todas.length} oportunidades no arquivo · ${altas.length} ALTA pendentes`);

  return todas;
}

function relatorio(ops: Oportunidade[], topN: number) {
  const top = ops.slice(0, topN);
  console.log("\n" + "━".repeat(72));
  console.log("  RADAR-LUCRO — OPORTUNIDADES");
  console.log("━".repeat(72));

  if (top.length === 0) {
    console.log("\n  Nenhuma oportunidade acima do corte nesta varredura.");
    console.log("  Isso é normal e é o sistema funcionando: sinal fraco não vira produto.\n");
    return;
  }

  for (const [i, o] of top.entries()) {
    const cor = o.urgencia === "ALTA" ? "🔴" : o.urgencia === "MEDIA" ? "🟡" : "⚪";
    console.log(`\n${cor} ${i + 1}. [${o.score}/100 · ${o.urgencia}] ${o.termo}`);
    console.log(`   dor:   ${o.dor.slice(0, 130)}`);
    console.log(
      `   fator: dor ${o.fatores.dorExplicita} · viab ${o.fatores.viabilidade} · ` +
      `vel ${o.fatores.velocidade} · vol ${o.fatores.volume} · rec ${o.fatores.recorrencia}`,
    );
    console.log(`   vol:   ~${o.volumeEstimado.toLocaleString("pt-BR")}`);
    console.log(`   ref:   ${o.fontes[0] ?? "—"}`);
  }

  const altas = ops.filter((o) => o.urgencia === "ALTA" && o.estado === "NOVA");
  console.log("\n" + "━".repeat(72));
  if (altas.length > 0) {
    console.log(`  ${altas.length} oportunidade(s) ALTA aguardando construção.`);
    console.log(`  Próximo passo:  node --experimental-strip-types gerar-saas.ts ${altas[0].id}`);
  } else {
    console.log("  Nenhuma ALTA pendente. Radar segue monitorando.");
  }
  console.log("━".repeat(72) + "\n");
}

const args = process.argv.slice(2);
const topN = Number(args[args.indexOf("--top") + 1]) || 10;

if (args.includes("--watch")) {
  log("info", `Modo contínuo — varredura a cada ${LIMITES.intervaloMin} min. Ctrl+C para parar.`);
  const ciclo = async () => {
    try {
      relatorio(await varrer(), topN);
    } catch (e) {
      log("erro", e instanceof Error ? e.message : String(e));
    }
  };
  await ciclo();
  setInterval(ciclo, LIMITES.intervaloMin * 60_000);
} else {
  relatorio(await varrer(), topN);
}
