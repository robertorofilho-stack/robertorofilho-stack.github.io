"use client";

import { useState } from "react";

interface Props {
  precoBRL: number;
  precoUSD: number;
  aoLiberar: () => void;
}

type Aba = "pix" | "paypal";

export default function Paywall({ precoBRL, precoUSD, aoLiberar }: Props) {
  const [aba, setAba] = useState<Aba>("pix");
  const [carregando, setCarregando] = useState(false);
  const [pix, setPix] = useState<{ copiaECola: string; qrCodeUrl: string; sandbox: boolean } | null>(null);
  const [copiado, setCopiado] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  async function gerarPix() {
    setCarregando(true); setErro(null);
    try {
      const r = await fetch("/api/pix", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ valor: precoBRL, descricao: "{{NOME}}" }),
      });
      const d = await r.json();
      if (!d.ok) throw new Error(d.erro ?? "falha ao gerar Pix");
      setPix(d);
    } catch (e) {
      setErro(e instanceof Error ? e.message : "erro inesperado");
    } finally {
      setCarregando(false);
    }
  }

  async function pagarPaypal() {
    setCarregando(true); setErro(null);
    try {
      const r = await fetch("/api/paypal", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ valor: precoUSD, moeda: "USD" }),
      });
      const d = await r.json();
      if (!d.ok) throw new Error("falha ao criar ordem");
      if (d.sandbox) { alert("Modo sandbox: pagamento simulado. Acesso liberado."); aoLiberar(); }
      else window.location.href = `https://www.paypal.com/checkoutnow?token=${d.orderId}`;
    } catch (e) {
      setErro(e instanceof Error ? e.message : "erro inesperado");
    } finally {
      setCarregando(false);
    }
  }

  async function copiar() {
    if (!pix) return;
    try {
      await navigator.clipboard.writeText(pix.copiaECola);
      setCopiado(true);
      setTimeout(() => setCopiado(false), 2500);
    } catch { setErro("não foi possível copiar — selecione o texto manualmente"); }
  }

  return (
    <div className="w-full max-w-md rounded-2xl border border-black/10 bg-white p-6 shadow-sm dark:border-white/10 dark:bg-white/5">
      <h2 className="text-lg font-semibold">Liberar acesso completo</h2>
      <p className="mt-1 text-sm text-black/60 dark:text-white/60">
        Pagamento único. Sem assinatura, sem cadastro.
      </p>

      <div className="mt-4 flex gap-1 rounded-lg bg-black/5 p-1 dark:bg-white/10">
        {(["pix", "paypal"] as const).map((a) => (
          <button
            key={a}
            onClick={() => setAba(a)}
            className={`flex-1 rounded-md px-3 py-2 text-sm font-medium transition ${
              aba === a ? "bg-white shadow-sm dark:bg-white/15" : "text-black/60 dark:text-white/60"
            }`}
          >
            {a === "pix" ? `Pix · R$ ${precoBRL.toFixed(2)}` : `PayPal · $${precoUSD.toFixed(2)}`}
          </button>
        ))}
      </div>

      {erro && (
        <p role="alert" className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-950/40 dark:text-red-300">
          {erro}
        </p>
      )}

      {aba === "pix" && (
        <div className="mt-4">
          {!pix ? (
            <button
              onClick={gerarPix}
              disabled={carregando}
              className="w-full rounded-xl bg-black px-4 py-3 font-medium text-white transition hover:opacity-90 disabled:opacity-50 dark:bg-white dark:text-black"
            >
              {carregando ? "Gerando..." : "Gerar código Pix"}
            </button>
          ) : (
            <div className="space-y-3">
              {pix.sandbox && (
                <p className="rounded-lg bg-amber-50 px-3 py-2 text-xs text-amber-800 dark:bg-amber-950/40 dark:text-amber-200">
                  Modo sandbox — defina <code>PIX_KEY</code> no .env para receber de verdade.
                </p>
              )}
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={pix.qrCodeUrl} alt="QR Code Pix" width={280} height={280}
                   className="mx-auto rounded-xl bg-white p-2" />
              <div className="rounded-lg bg-black/5 p-3 dark:bg-white/10">
                <p className="mb-2 text-xs font-medium text-black/50 dark:text-white/50">Copia e Cola</p>
                <p className="break-all font-mono text-[11px] leading-relaxed">{pix.copiaECola}</p>
              </div>
              <button onClick={copiar}
                className="w-full rounded-xl bg-black px-4 py-3 font-medium text-white transition hover:opacity-90 dark:bg-white dark:text-black">
                {copiado ? "Copiado ✓" : "Copiar código"}
              </button>
              <button onClick={aoLiberar}
                className="w-full rounded-xl border border-black/15 px-4 py-2.5 text-sm transition hover:bg-black/5 dark:border-white/20 dark:hover:bg-white/10">
                Já paguei — liberar acesso
              </button>
            </div>
          )}
        </div>
      )}

      {aba === "paypal" && (
        <div className="mt-4">
          <button onClick={pagarPaypal} disabled={carregando}
            className="w-full rounded-xl bg-[#0070ba] px-4 py-3 font-medium text-white transition hover:opacity-90 disabled:opacity-50">
            {carregando ? "Processando..." : `Pagar $${precoUSD.toFixed(2)} com PayPal`}
          </button>
        </div>
      )}

      <p className="mt-4 text-center text-xs text-black/40 dark:text-white/40">
        Pagamento processado por Pix (Banco Central) ou PayPal.
      </p>
    </div>
  );
}
