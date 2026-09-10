import { UA, LIMITES } from "./config.ts";

export async function buscar(
  url: string,
  init: RequestInit = {},
): Promise<Response> {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), LIMITES.timeoutMs);
  try {
    return await fetch(url, {
      ...init,
      signal: ctrl.signal,
      headers: { "User-Agent": UA, Accept: "*/*", ...(init.headers ?? {}) },
    });
  } finally {
    clearTimeout(t);
  }
}

/** Retry com backoff exponencial. Rede falha; o radar não pode falhar junto. */
export async function comRetry<T>(
  fn: () => Promise<T>,
  tentativas = 3,
): Promise<T> {
  let ultimo: unknown;
  for (let i = 0; i < tentativas; i++) {
    try {
      return await fn();
    } catch (e) {
      ultimo = e;
      if (i < tentativas - 1) {
        await new Promise((r) => setTimeout(r, 2 ** (i + 1) * 1000));
      }
    }
  }
  throw ultimo;
}

export function normalizar(s: string): string {
  return s
    .toLowerCase()
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

/** Extrai o núcleo do que a pessoa quer, a partir da frase de dor. */
export function extrairTermo(texto: string, frase: string): string {
  const i = normalizar(texto).indexOf(normalizar(frase));
  if (i === -1) return texto.slice(0, 60);
  const depois = texto.slice(i + frase.length, i + frase.length + 90);
  return depois
    .replace(/[?!.\n].*$/s, "")
    .replace(/^\s*(that|to|which|para|que|de)\s+/i, "")
    .trim()
    .slice(0, 80);
}

export function limparHtml(s: string): string {
  return s
    .replace(/<[^>]+>/g, " ")
    .replace(/&quot;/g, '"')
    .replace(/&#x27;|&apos;/g, "'")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&nbsp;/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

export function hash(s: string): string {
  let h = 0;
  for (let i = 0; i < s.length; i++) {
    h = (h << 5) - h + s.charCodeAt(i);
    h |= 0;
  }
  return Math.abs(h).toString(36);
}

export function log(nivel: "info" | "ok" | "aviso" | "erro", msg: string) {
  const icone = { info: "·", ok: "✓", aviso: "!", erro: "✗" }[nivel];
  const hora = new Date().toISOString().slice(11, 19);
  console.log(`[${hora}] ${icone} ${msg}`);
}
