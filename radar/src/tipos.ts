export type Urgencia = "ALTA" | "MEDIA" | "BAIXA";

/** Sinal bruto capturado de uma fonte, antes de virar oportunidade. */
export interface Sinal {
  fonte: "google-trends" | "hackernews" | "stackexchange" | "reddit" | "x";
  termo: string;
  /** A dor, no texto original de quem escreveu. Matéria-prima da copy. */
  dor: string;
  url: string;
  data: string;          // ISO
  engajamento: number;   // pontos, votos, respostas — normalizado por fonte
  volumeEstimado: number;
}

/** Oportunidade consolidada e pontuada. */
export interface Oportunidade {
  id: string;
  termo: string;
  dor: string;
  volumeEstimado: number;
  urgencia: Urgencia;
  score: number;          // 0-100
  fatores: Fatores;
  fontes: string[];       // URLs de evidência
  amostras: string[];     // frases literais dos usuários
  detectadoEm: string;    // ISO
  produtoSugerido?: string;
  estado: "NOVA" | "EM_CONSTRUCAO" | "PUBLICADA" | "DESCARTADA";
}

export interface Fatores {
  velocidade: number;   // o termo está subindo?
  dorExplicita: number; // alguém pediu uma ferramenta com todas as letras?
  volume: number;       // quanta gente?
  viabilidade: number;  // dá para resolver numa página?
  recorrencia: number;  // apareceu em fontes independentes?
}

export interface ResultadoFonte {
  fonte: string;
  ok: boolean;
  sinais: Sinal[];
  erro?: string;
  duracaoMs: number;
}
