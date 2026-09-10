import { NextResponse } from "next/server";

export const runtime = "nodejs";

const BASE =
  process.env.PAYPAL_ENV === "live"
    ? "https://api-m.paypal.com"
    : "https://api-m.sandbox.paypal.com";

async function token(): Promise<string | null> {
  const id = process.env.PAYPAL_CLIENT_ID;
  const secret = process.env.PAYPAL_SECRET;
  if (!id || !secret) return null;

  const r = await fetch(`${BASE}/v1/oauth2/token`, {
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

/**
 * POST /api/paypal — cria a ordem de pagamento.
 * Sem credencial, devolve ordem simulada para o fluxo ser testável.
 */
export async function POST(req: Request) {
  const { valor = 4.9, moeda = "USD" } = (await req.json().catch(() => ({}))) as {
    valor?: number; moeda?: string;
  };

  const tk = await token().catch(() => null);
  if (!tk) {
    return NextResponse.json({
      ok: true,
      sandbox: true,
      orderId: `SANDBOX-${Date.now().toString(36).toUpperCase()}`,
      aviso: "MODO SANDBOX — defina PAYPAL_CLIENT_ID e PAYPAL_SECRET no .env.",
    });
  }

  const r = await fetch(`${BASE}/v2/checkout/orders`, {
    method: "POST",
    headers: { Authorization: `Bearer ${tk}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      intent: "CAPTURE",
      purchase_units: [
        { amount: { currency_code: moeda, value: valor.toFixed(2) } },
      ],
    }),
  });

  const dados = (await r.json()) as { id?: string };
  return NextResponse.json({ ok: r.ok, sandbox: false, orderId: dados.id });
}
