/** Configuração central do radar. Ajuste aqui, não no código das fontes. */

export const UA =
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 " +
  "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36";

/** Frases que indicam alguém procurando ferramenta que não existe (ou é ruim). */
export const FRASES_DOR_EN = [
  "is there a tool",
  "is there an app",
  "looking for a tool",
  "anyone know a tool",
  "how do i convert",
  "alternative to",
  "wish there was a",
  "does anyone have a script",
  "need to automate",
  "any tool that can",
  "why is there no",
  "manually doing this",
];

export const FRASES_DOR_PT = [
  "existe algum site para",
  "alguém conhece um app",
  "como eu converto",
  "ferramenta para",
  "alternativa para",
  "preciso automatizar",
  "site que faça",
  "tem algum programa que",
];

/** Termos que qualificam o sinal como tecnologia / negócio / utilitário. */
export const CATEGORIAS_ALVO = [
  "api", "app", "tool", "software", "saas", "automation", "automate",
  "convert", "converter", "generator", "calculator", "dashboard",
  "spreadsheet", "csv", "json", "pdf", "invoice", "ai", "llm", "prompt",
  "chrome extension", "workflow", "integration", "webhook", "scraper",
  "ferramenta", "planilha", "automação", "gerador", "conversor", "relatório",
];

/** Ruído puro: notícia, esporte, celebridade. Sinal de trends que não serve. */
export const RUIDO = [
  // pt
  "jogo", "futebol", "campeonato", "novela", "bbb", "morreu", "morte",
  "acidente", "eleicao", "eleição", "filme", "serie", "série", "clima",
  "tempo", "resultado", "escalacao", "escalação", "libertadores",
  "brasileirao", "brasileirão", "loteria", "mega-sena", "horoscopo",
  "horóscopo", "signo", "sorteio", "falecimento",
  // en
  "vs", "standings", "playoff", "playoffs", "nfl", "nba", "mlb", "nhl",
  "fifa", "premier league", "champions", "score", "highlights", "trailer",
  "episode", "season", "box office", "awards", "grammy", "oscar", "concert",
  "tour dates", "weather", "hurricane", "earthquake", "election", "obituary",
  "died", "dead", "arrested", "lawsuit", "divorce", "dating", "net worth",
  "stock price", "lottery", "powerball", "horoscope", "birthday",
];

export const LIMITES = {
  /** Score mínimo para gravar como oportunidade. */
  scoreMinimo: 45,
  /** Score a partir do qual a urgência é ALTA e o build é disparado. */
  scoreAlta: 70,
  /** Janela de busca de dor, em dias. */
  janelaDias: 7,
  /** Timeout por requisição. */
  timeoutMs: 25_000,
  /** Intervalo do modo --watch, em minutos. */
  intervaloMin: 60,
};

export const GEOS = ["BR", "US"];
