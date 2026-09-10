import { normalizar, hash } from "./util.ts";
import { CATEGORIAS_ALVO, FRASES_DOR_EN, FRASES_DOR_PT, LIMITES } from "./config.ts";
import type { Sinal, Oportunidade, Fatores, Urgencia } from "./tipos.ts";

/** Palavras que indicam solução possível em UMA página, sem backend pesado. */
const VIAVEL_PAGINA_UNICA = [
  "convert", "converter", "generate", "generator", "calculate", "calculator",
  "format", "formatter", "validate", "compress", "resize", "extract",
  "parse", "merge", "split", "rename", "translate", "summarize", "count",
  "conversor", "gerador", "calculadora", "formatar", "extrair", "juntar",
];

/** Palavras que indicam escopo grande demais para a janela de 72h. */
const INVIAVEL = [
  "crm", "erp", "marketplace", "social network", "video editor",
  "operating system", "compiler", "database engine", "blockchain",
  "real time collaboration", "mobile app store",
];

function pontuarVelocidade(sinais: Sinal[]): number {
  const temTrends = sinais.some((s) => s.fonte === "google-trends");
  const agora = Date.now();
  const maisRecente = Math.min(
    ...sinais.map((s) => (agora - new Date(s.data).getTime()) / 86400_000),
  );
  let p = 0;
  if (temTrends) p += 40;              // o termo está subindo em busca
  if (maisRecente < 1) p += 40;        // dor de menos de 24h
  else if (maisRecente < 3) p += 25;
  else if (maisRecente < 7) p += 10;
  return Math.min(100, p + Math.min(20, sinais.length * 4));
}

function pontuarDorExplicita(sinais: Sinal[]): number {
  const texto = normalizar(sinais.map((s) => `${s.termo} ${s.dor}`).join(" "));
  const frases = [...FRASES_DOR_EN, ...FRASES_DOR_PT];
  const achadas = frases.filter((f) => texto.includes(normalizar(f))).length;
  // Pedido explícito por ferramenta vale mais que menção genérica.
  return Math.min(100, achadas * 30);
}

function pontuarVolume(sinais: Sinal[]): number {
  const vol = sinais.reduce((a, s) => a + s.volumeEstimado, 0);
  const eng = sinais.reduce((a, s) => a + s.engajamento, 0);
  // Escala logarítmica: a diferença entre 100 e 1.000 importa mais
  // que entre 100.000 e 1.000.000.
  return Math.min(100, Math.log10(vol + eng * 10 + 1) * 22);
}

function pontuarViabilidade(sinais: Sinal[]): number {
  const texto = normalizar(sinais.map((s) => `${s.termo} ${s.dor}`).join(" "));
  if (INVIAVEL.some((i) => texto.includes(i))) return 10;
  const viavel = VIAVEL_PAGINA_UNICA.filter((v) => texto.includes(v)).length;
  const tech = CATEGORIAS_ALVO.filter((c) => texto.includes(c)).length;
  return Math.min(100, 30 + viavel * 25 + tech * 8);
}

function pontuarRecorrencia(sinais: Sinal[]): number {
  const fontes = new Set(sinais.map((s) => s.fonte)).size;
  // Duas fontes independentes valem muito mais que dez sinais de uma só.
  return Math.min(100, fontes * 45 + Math.min(10, sinais.length));
}

/** Agrupa sinais por similaridade de termo, para não contar a mesma dor 5x. */
export function agrupar(sinais: Sinal[]): Sinal[][] {
  const grupos: Sinal[][] = [];

  for (const s of sinais) {
    const palavras = new Set(
      normalizar(s.termo).split(" ").filter((w) => w.length > 3),
    );
    if (palavras.size === 0) continue;

    const grupo = grupos.find((g) => {
      const outras = new Set(
        normalizar(g[0].termo).split(" ").filter((w) => w.length > 3),
      );
      const comuns = [...palavras].filter((w) => outras.has(w)).length;
      return comuns >= Math.min(2, Math.min(palavras.size, outras.size));
    });

    if (grupo) grupo.push(s);
    else grupos.push([s]);
  }
  return grupos;
}

export function pontuar(grupo: Sinal[]): Oportunidade {
  const fatores: Fatores = {
    velocidade: pontuarVelocidade(grupo),
    dorExplicita: pontuarDorExplicita(grupo),
    volume: pontuarVolume(grupo),
    viabilidade: pontuarViabilidade(grupo),
    recorrencia: pontuarRecorrencia(grupo),
  };

  // Pesos: dor explícita e viabilidade decidem se vira produto.
  // Velocidade decide se vira produto AGORA.
  let score = Math.round(
    fatores.dorExplicita * 0.30 +
    fatores.viabilidade  * 0.25 +
    fatores.velocidade   * 0.20 +
    fatores.volume       * 0.15 +
    fatores.recorrencia  * 0.10,
  );

  // TRAVA DE REALIDADE — corrige o erro mais caro deste sistema.
  //
  // Sem esta trava, um termo em alta no Google Trends ("lionel messi",
  // "mlb standings") pontua alto por volume e velocidade e ultrapassa uma
  // dor real de mercado. Volume de busca por notícia NÃO é demanda por
  // ferramenta. Ninguém compra um SaaS de "lionel messi".
  //
  // Regra: sem alguém pedindo explicitamente uma ferramenta, não existe
  // oportunidade — existe assunto. Tendência é o acelerador, nunca o motor.
  const soTendencia = grupo.every((s) => s.fonte === "google-trends");
  if (fatores.dorExplicita === 0) score = Math.min(score, 25);
  if (soTendencia) score = Math.min(score, 30);

  // Escopo grande demais para 72h: rebaixa mesmo com dor forte.
  if (fatores.viabilidade <= 10) score = Math.min(score, 35);

  const urgencia: Urgencia =
    score >= LIMITES.scoreAlta ? "ALTA" : score >= LIMITES.scoreMinimo ? "MEDIA" : "BAIXA";

  const principal = [...grupo].sort((a, b) => b.engajamento - a.engajamento)[0];

  return {
    id: hash(normalizar(principal.termo)),
    termo: principal.termo,
    dor: principal.dor,
    volumeEstimado: grupo.reduce((a, s) => a + s.volumeEstimado, 0),
    urgencia,
    score,
    fatores,
    fontes: [...new Set(grupo.map((s) => s.url))].slice(0, 8),
    amostras: [...new Set(grupo.map((s) => s.dor.slice(0, 200)))].slice(0, 5),
    detectadoEm: new Date().toISOString(),
    estado: "NOVA",
  };
}
