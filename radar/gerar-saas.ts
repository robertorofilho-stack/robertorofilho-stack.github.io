#!/usr/bin/env node
/**
 * GERAR-SAAS — transforma uma oportunidade detectada em projeto Next.js
 * completo, com paywall Pix + PayPal e modo sandbox funcional.
 *
 *   node --experimental-strip-types gerar-saas.ts <id-da-oportunidade>
 *   node --experimental-strip-types gerar-saas.ts --auto     # pega a melhor ALTA
 *   node --experimental-strip-types gerar-saas.ts --listar
 *
 * O que ele NÃO faz, e por quê: não escreve a lógica de negócio da ferramenta.
 * Ele monta todo o esqueleto — projeto, estilo, paywall, APIs, deploy — e deixa
 * um bloco marcado em app/page.tsx onde entra o núcleo. Esse bloco é curto e
 * específico da dor; é o pedaço que exige julgamento, não repetição.
 */
import { readFile, writeFile, mkdir, cp } from "node:fs/promises";
import { existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import type { Oportunidade } from "./src/tipos.ts";
import { log } from "./src/util.ts";

const RAIZ = dirname(fileURLToPath(import.meta.url));
const ARQUIVO = join(RAIZ, "dados", "oportunidades.json");
const TEMPLATES = join(RAIZ, "templates");
const DESTINO_BASE = join(RAIZ, "saas-gerados");

function slug(s: string): string {
  return s
    .toLowerCase()
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 40) || "ferramenta";
}

/**
 * Torna texto vindo de fonte externa seguro para ser injetado tanto em
 * texto JSX quanto em string literal de JS.
 *
 * Motivo concreto: comentário do Hacker News começa com ">" (citação).
 * Injetado cru em JSX, quebra o parser do Turbopack e o build inteiro falha.
 * Chaves quebram JSX; aspas e crase quebram string literal.
 */
function textoSeguro(s: string): string {
  return s
    .replace(/\s+/g, " ")
    .replace(/[<>{}]/g, "")
    .replace(/["`\\]/g, "'")
    .trim();
}

function titulo(s: string): string {
  const t = textoSeguro(s).slice(0, 55);
  return t.charAt(0).toUpperCase() + t.slice(1);
}

async function carregar(): Promise<Oportunidade[]> {
  if (!existsSync(ARQUIVO)) {
    log("erro", "dados/oportunidades.json não existe. Rode o radar primeiro.");
    process.exit(1);
  }
  return JSON.parse(await readFile(ARQUIVO, "utf8")) as Oportunidade[];
}

/** Substitui os marcadores {{X}} em todo arquivo de texto do projeto. */
async function substituir(caminho: string, vars: Record<string, string>) {
  let s = await readFile(caminho, "utf8");
  for (const [k, v] of Object.entries(vars)) {
    s = s.replaceAll(`{{${k}}}`, v);
  }
  await writeFile(caminho, s, "utf8");
}

async function gerar(op: Oportunidade) {
  const nome = titulo(op.termo);
  const s = slug(op.termo);
  const destino = join(DESTINO_BASE, s);

  if (existsSync(destino)) {
    log("aviso", `${destino} já existe. Apague antes de regenerar.`);
    process.exit(1);
  }

  log("info", `Gerando "${nome}" em saas-gerados/${s}`);
  await mkdir(destino, { recursive: true });

  // Preço por viabilidade: ferramenta mais simples, preço menor.
  const precoBRL = op.fatores.viabilidade > 70 ? 9.9 : op.fatores.viabilidade > 45 ? 19.9 : 29.9;
  const precoUSD = Math.round((precoBRL / 5.2) * 100) / 100;

  const vars = {
    NOME: textoSeguro(nome),
    SLUG: s,
    DESCRICAO: textoSeguro(`Ferramenta que resolve: ${op.termo}`),
    DOR: textoSeguro(op.dor.slice(0, 200)),
    TERMO: textoSeguro(op.fontes[0] ?? "sinal público"),
    PRECO_BRL: precoBRL.toFixed(2),
    PRECO_USD: precoUSD.toFixed(2),
  };

  // Copia a árvore de templates e renomeia os .tpl
  for (const [origem, alvo] of [
    ["app", "app"], ["components", "components"], ["lib", "lib"],
    ["next.config.mjs", "next.config.mjs"], ["postcss.config.mjs", "postcss.config.mjs"],
    ["package.json.tpl", "package.json"], ["tsconfig.json.tpl", "tsconfig.json"],
    ["env.example", ".env.example"],
  ] as const) {
    await cp(join(TEMPLATES, origem), join(destino, alvo), { recursive: true });
  }

  // Substitui marcadores em todos os arquivos de texto
  const alvos = [
    "app/page.tsx", "app/layout.tsx", "components/Paywall.tsx",
    "package.json", "app/api/pix/route.ts",
  ];
  for (const a of alvos) await substituir(join(destino, a), vars);

  await writeFile(join(destino, ".gitignore"),
    "node_modules/\n.next/\n.env\n.env.local\n.vercel/\nout/\n", "utf8");

  await writeFile(join(destino, "README.md"), `# ${nome}

${vars.DESCRICAO}

## Origem
Detectado pelo radar em ${op.detectadoEm.slice(0, 10)}.
Score **${op.score}/100** · urgência **${op.urgencia}**

### A dor, nas palavras de quem a sentiu
> ${op.dor.slice(0, 400)}

### Evidência
${op.fontes.map((f) => `- ${f}`).join("\n")}

## Rodar

\`\`\`bash
npm install
cp .env.example .env      # opcional: sem .env o paywall roda em sandbox
npm run dev
\`\`\`

## Antes de publicar

1. **Implementar o núcleo** — o bloco marcado em \`app/page.tsx\`.
   Todo o resto (paywall, APIs, estilo, deploy) já está pronto.
2. **Preencher \`.env\`** — \`PIX_KEY\` para receber via Pix,
   \`PAYPAL_CLIENT_ID\`/\`PAYPAL_SECRET\` para receber em dólar.
   Sem eles o app funciona em sandbox e nada quebra.
3. **QA** — \`node --experimental-strip-types ../../qa.ts ${s}\`
4. **Deploy** — \`npx vercel --prod\`

## Preço
R$ ${precoBRL.toFixed(2)} · US$ ${precoUSD.toFixed(2)} — pagamento único, ${3} usos grátis antes do paywall.
`, "utf8");

  // Marca a oportunidade como em construção
  const todas = await carregar();
  const i = todas.findIndex((o) => o.id === op.id);
  if (i >= 0) {
    todas[i].estado = "EM_CONSTRUCAO";
    todas[i].produtoSugerido = nome;
    await writeFile(ARQUIVO, JSON.stringify(todas, null, 2), "utf8");
  }

  console.log(`
${"━".repeat(70)}
  📦  PROJETO GERADO
${"━".repeat(70)}
  Nome:      ${nome}
  Pasta:     radar/saas-gerados/${s}
  Preço:     R$ ${precoBRL.toFixed(2)} · US$ ${precoUSD.toFixed(2)}
  Pagamento: Pix (BR Code offline) + PayPal — sandbox ativo sem .env
  Origem:    score ${op.score}/100 · ${op.urgencia}

  Próximos passos:
    cd radar/saas-gerados/${s} && npm install && npm run dev
    → implementar o núcleo no bloco marcado em app/page.tsx
    → node --experimental-strip-types radar/qa.ts ${s}
    → npx vercel --prod
${"━".repeat(70)}
`);
}

const args = process.argv.slice(2);
const todas = await carregar();

if (args.includes("--listar") || args.length === 0) {
  console.log("\nOportunidades disponíveis:\n");
  for (const o of todas.slice(0, 20)) {
    console.log(`  ${o.id.padEnd(10)} [${String(o.score).padStart(3)}/100 ${o.urgencia.padEnd(5)}] ${o.estado.padEnd(14)} ${o.termo.slice(0, 55)}`);
  }
  console.log(`\nGerar:  node --experimental-strip-types gerar-saas.ts <id>`);
  console.log(`Auto:   node --experimental-strip-types gerar-saas.ts --auto\n`);
} else if (args.includes("--auto")) {
  const alvo = todas.find((o) => o.urgencia === "ALTA" && o.estado === "NOVA")
            ?? todas.find((o) => o.estado === "NOVA");
  if (!alvo) { log("aviso", "Nenhuma oportunidade nova. Rode o radar."); process.exit(0); }
  await gerar(alvo);
} else {
  const alvo = todas.find((o) => o.id === args[0]);
  if (!alvo) { log("erro", `Oportunidade "${args[0]}" não encontrada.`); process.exit(1); }
  await gerar(alvo);
}
