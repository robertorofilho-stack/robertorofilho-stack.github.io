import { NextResponse } from "next/server";
import QRCode from "qrcode";
import { gerarBRCode } from "@/lib/pix";

export const runtime = "nodejs";

/**
 * POST /api/pix — devolve o Copia e Cola e o QR Code.
 *
 * Sem PIX_KEY no .env, entra em MODO SANDBOX: gera um código estruturalmente
 * válido com chave de demonstração, para o fluxo ser testável de imediato.
 * Basta preencher PIX_KEY para virar produção — nenhuma linha de código muda.
 */
export async function POST(req: Request) {
  try {
    const { valor, descricao } = (await req.json().catch(() => ({}))) as {
      valor?: number; descricao?: string;
    };

    const chave = process.env.PIX_KEY?.trim();
    const sandbox = !chave;

    const codigo = gerarBRCode({
      chave: chave || "sandbox@exemplo.com.br",
      nomeRecebedor: process.env.PIX_BENEFICIARY_NAME || "SANDBOX",
      cidade: process.env.PIX_CITY || "FORTALEZA",
      valor: typeof valor === "number" && valor > 0 ? valor : undefined,
      descricao: descricao?.slice(0, 40),
      txid: `T${Date.now().toString(36).toUpperCase()}`,
    });

    // QR gerado localmente, como data URI. Nenhuma dependência externa e,
    // mais importante, o payload de pagamento nunca sai para um terceiro.
    const qrCodeUrl = await QRCode.toDataURL(codigo, {
      width: 280,
      margin: 1,
      errorCorrectionLevel: "M",
      color: { dark: "#000000", light: "#ffffff" },
    });

    return NextResponse.json({
      ok: true,
      sandbox,
      copiaECola: codigo,
      qrCodeUrl,
      aviso: sandbox
        ? "MODO SANDBOX — defina PIX_KEY no .env para receber de verdade."
        : null,
    });
  } catch (e) {
    return NextResponse.json(
      { ok: false, erro: e instanceof Error ? e.message : "falha ao gerar Pix" },
      { status: 500 },
    );
  }
}
