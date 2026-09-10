"use client";

import { useState } from "react";
import Paywall from "@/components/Paywall";

const PRECO_BRL = {{PRECO_BRL}};
const PRECO_USD = {{PRECO_USD}};
const LIMITE_GRATIS = 3;

export default function Home() {
  const [entrada, setEntrada] = useState("");
  const [saida, setSaida] = useState<string | null>(null);
  const [usos, setUsos] = useState(0);
  const [liberado, setLiberado] = useState(false);
  const [processando, setProcessando] = useState(false);

  const bloqueado = !liberado && usos >= LIMITE_GRATIS;

  async function processar() {
    if (bloqueado || !entrada.trim()) return;
    setProcessando(true);
    try {
      // ── NÚCLEO DA FERRAMENTA ──────────────────────────────────────────
      // Substitua por: {{DESCRICAO}}
      const resultado = entrada
        .split("\n")
        .filter(Boolean)
        .map((l, i) => `${i + 1}. ${l.trim()}`)
        .join("\n");
      // ──────────────────────────────────────────────────────────────────
      setSaida(resultado);
      setUsos((u) => u + 1);
    } finally {
      setProcessando(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-full max-w-3xl flex-col gap-8 px-5 py-12 sm:py-16">
      <header>
        <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">{{NOME}}</h1>
        <p className="mt-3 text-base text-black/60 dark:text-white/60">{{DESCRICAO}}</p>
        <p className="mt-4 rounded-xl border border-black/10 bg-black/[0.03] px-4 py-3 text-sm text-black/70 dark:border-white/10 dark:bg-white/5 dark:text-white/70">
          <strong className="font-medium">A dor que isso resolve:</strong> {{DOR}}
        </p>
      </header>

      <section className="flex flex-col gap-3">
        <label htmlFor="entrada" className="text-sm font-medium">Entrada</label>
        <textarea
          id="entrada"
          value={entrada}
          onChange={(e) => setEntrada(e.target.value)}
          placeholder="Cole aqui o conteúdo..."
          rows={8}
          disabled={bloqueado}
          className="w-full resize-y rounded-xl border border-black/15 bg-white p-4 font-mono text-sm outline-none transition focus:border-black/40 disabled:opacity-50 dark:border-white/15 dark:bg-white/5 dark:focus:border-white/40"
        />
        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={processar}
            disabled={bloqueado || processando || !entrada.trim()}
            className="rounded-xl bg-black px-5 py-3 font-medium text-white transition hover:opacity-90 disabled:opacity-40 dark:bg-white dark:text-black"
          >
            {processando ? "Processando..." : "Processar"}
          </button>
          <span className="text-sm text-black/50 dark:text-white/50">
            {liberado ? "Acesso completo ✓" : `${Math.max(0, LIMITE_GRATIS - usos)} uso(s) grátis restante(s)`}
          </span>
        </div>
      </section>

      {saida !== null && !bloqueado && (
        <section className="flex flex-col gap-3">
          <label htmlFor="saida" className="text-sm font-medium">Resultado</label>
          <pre id="saida" className="overflow-x-auto rounded-xl border border-black/10 bg-black/[0.03] p-4 font-mono text-sm dark:border-white/10 dark:bg-white/5">
            {saida}
          </pre>
          <button
            onClick={() => navigator.clipboard.writeText(saida)}
            className="self-start rounded-lg border border-black/15 px-4 py-2 text-sm transition hover:bg-black/5 dark:border-white/20 dark:hover:bg-white/10"
          >
            Copiar resultado
          </button>
        </section>
      )}

      {bloqueado && (
        <section className="flex flex-col items-center gap-4 rounded-2xl border border-black/10 bg-black/[0.02] px-5 py-10 dark:border-white/10 dark:bg-white/5">
          <p className="text-center text-sm text-black/60 dark:text-white/60">
            Você usou os {LIMITE_GRATIS} testes grátis. Libere o acesso ilimitado.
          </p>
          <Paywall precoBRL={PRECO_BRL} precoUSD={PRECO_USD} aoLiberar={() => setLiberado(true)} />
        </section>
      )}

      <footer className="mt-auto border-t border-black/10 pt-6 text-xs text-black/40 dark:border-white/10 dark:text-white/40">
        <p>{{NOME}} · construído a partir de demanda real detectada em {{TERMO}}</p>
      </footer>
    </main>
  );
}
