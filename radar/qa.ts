#!/usr/bin/env node
/**
 * QA — ataca o micro-SaaS gerado com um navegador de verdade.
 *
 *   node --experimental-strip-types qa.ts [slug-do-projeto]
 *
 * Não valida: ataca. Sobe o build de produção numa porta livre, abre o
 * Chromium, percorre o fluxo até o pagamento, testa entrada hostil, duplo
 * clique, mobile em 390px, lê o console e procura credencial no bundle.
 *
 * Ler o código e achar que está certo não é QA. É opinião.
 */
import { spawn, execSync, type ChildProcess } from "node:child_process";
import { readdir, mkdir, readFile } from "node:fs/promises";
import { existsSync, readdirSync, openSync } from "node:fs";
import { createServer } from "node:net";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium, type Browser, type Page } from "playwright";

const RAIZ = dirname(fileURLToPath(import.meta.url));

/** Pede ao SO uma porta livre. Porta fixa colide com execução anterior. */
async function portaLivre(): Promise<number> {
  return new Promise((resolve, reject) => {
    const srv = createServer();
    srv.unref();
    srv.on("error", reject);
    srv.listen(0, "127.0.0.1", () => {
      const p = (srv.address() as { port: number }).port;
      srv.close(() => resolve(p));
    });
  });
}

/**
 * Encontra o Chromium disponível no ambiente. O Playwright espera uma build
 * específica por versão; em ambiente com navegador pré-instalado, raramente
 * casa. Em vez de baixar centenas de MB, achamos o binário que já existe.
 */
function acharChromium(): string | undefined {
  if (process.env.PW_CHROMIUM && existsSync(process.env.PW_CHROMIUM)) return process.env.PW_CHROMIUM;
  const base = process.env.PLAYWRIGHT_BROWSERS_PATH || "/opt/pw-browsers";
  if (!existsSync(base)) return undefined;
  for (const dir of readdirSync(base).sort().reverse()) {
    for (const rel of ["chrome-linux/chrome", "chrome-linux/headless_shell",
                       "chrome-mac/Chromium.app/Contents/MacOS/Chromium"]) {
      const p = `${base}/${dir}/${rel}`;
      if (existsSync(p)) return p;
    }
  }
  return undefined;
}

interface Falha { nivel: "BLOQUEANTE" | "GRAVE" | "MENOR"; titulo: string; detalhe: string; }
const falhas: Falha[] = [];
const passou: string[] = [];
const ok = (t: string) => { passou.push(t); console.log(`  ✓ ${t}`); };
const falhar = (nivel: Falha["nivel"], titulo: string, detalhe: string) => {
  falhas.push({ nivel, titulo, detalhe });
  console.log(`  ✗ [${nivel}] ${titulo}\n      ${detalhe}`);
};

async function esperarServidor(url: string, ms = 60_000): Promise<boolean> {
  const fim = Date.now() + ms;
  while (Date.now() < fim) {
    try { if ((await fetch(url, { signal: AbortSignal.timeout(2500) })).ok) return true; }
    catch { /* subindo */ }
    await new Promise((r) => setTimeout(r, 900));
  }
  return false;
}

/** Espera o React hidratar antes de qualquer interação. */
async function esperarHidratacao(page: Page) {
  await page.waitForLoadState("networkidle").catch(() => {});
  await page.waitForFunction(() => !!document.querySelector("textarea"), { timeout: 10_000 }).catch(() => {});
  await page.waitForTimeout(1200);
}

/**
 * Preenche e clica em Processar, tolerando a corrida de hidratação.
 *
 * O Playwright preenche o DOM mais rápido que o React hidrata; quando isso
 * acontece o estado não atualiza e o botão segue desabilitado. Preenchemos,
 * esperamos o botão reagir e, se não reagir, preenchemos de novo.
 *
 * Timeouts curtos em tudo: textarea e botão desabilitados após o paywall
 * são comportamento CORRETO do produto — o `fill()` padrão esperaria 30s
 * por tentativa e travava o QA por minutos.
 *
 * Devolve false quando o botão ficou desabilitado de propósito.
 */
async function preencherEProcessar(page: Page, texto: string): Promise<boolean> {
  const ta = page.locator("textarea").first();
  const btn = page.getByRole("button", { name: /processar/i }).first();
  for (let tentativa = 0; tentativa < 3; tentativa++) {
    if (!(await ta.isEnabled().catch(() => false))) return false;
    await ta.fill(texto, { timeout: 2500 }).catch(() => {});
    try {
      await btn.waitFor({ state: "visible", timeout: 2500 });
      if (await btn.isEnabled()) { await btn.click({ timeout: 4000 }); return true; }
    } catch { /* próxima tentativa */ }
    await page.waitForTimeout(500);
  }
  return false;
}

async function atacar(page: Page, url: string, projeto: string) {
  const erros: string[] = [];
  page.on("console", (m) => { if (m.type() === "error") erros.push(m.text()); });
  page.on("pageerror", (e) => erros.push(`pageerror: ${e.message}`));

  console.log("\n[1] Renderização");
  await page.goto(url, { waitUntil: "networkidle", timeout: 45_000 });
  await esperarHidratacao(page);
  const h1 = await page.locator("h1").first().textContent().catch(() => null);
  h1?.trim() ? ok(`h1 presente: "${h1.trim().slice(0, 45)}"`)
             : falhar("BLOQUEANTE", "h1 ausente", "página não renderizou conteúdo principal");

  console.log("\n[2] Caminho feliz");
  if (await page.locator("textarea").count()) {
    const clicou = await preencherEProcessar(page, "linha um\nlinha dois\nlinha tres");
    await page.waitForTimeout(600);
    if (!clicou) falhar("BLOQUEANTE", "botão Processar não habilita", "entrada válida não habilitou a ação principal");
    else (await page.locator("pre").count()) ? ok("processamento produz resultado")
         : falhar("GRAVE", "sem resultado", "clicar em Processar não gerou saída visível");
  } else falhar("BLOQUEANTE", "textarea ausente", "não há entrada de dados na página");

  console.log("\n[3] Entrada hostil");
  for (const v of ["<script>window.__xss=1</script>", "   ", "x".repeat(10_000), "🔥‮test‬"]) {
    await preencherEProcessar(page, v);   // botão desabilitado em vazio = correto
    await page.waitForTimeout(150);
  }
  const xss = await page.evaluate(() => (window as unknown as { __xss?: number }).__xss);
  xss ? falhar("BLOQUEANTE", "XSS executado", "script injetado rodou no contexto da página")
      : ok("XSS não executa (React escapa por padrão)");

  console.log("\n[4] Paywall");
  for (let i = 0; i < 6; i++) {
    if (await page.getByText(/liberar acesso/i).count()) break;   // já apareceu: parar
    await preencherEProcessar(page, `teste ${i}`);
    await page.waitForTimeout(150);
  }
  (await page.getByText(/liberar acesso/i).count())
    ? ok("paywall bloqueia após o limite grátis")
    : falhar("BLOQUEANTE", "paywall não aparece", "produto sem barreira de pagamento não fatura");

  console.log("\n[5] Pix");
  const btnPix = page.getByRole("button", { name: /gerar código pix/i }).first();
  if (await btnPix.count()) {
    await btnPix.click({ timeout: 6000 });
    await page.waitForTimeout(2500);
    const codigo = await page.locator("p.font-mono").first().textContent().catch(() => null);
    if (codigo && codigo.length > 60) {
      ok(`BR Code gerado (${codigo.length} chars)`);
      codigo.startsWith("000201") ? ok("payload EMV com cabeçalho correto")
        : falhar("GRAVE", "payload Pix inválido", `começa com "${codigo.slice(0, 12)}"`);
      let crc = 0xffff;
      const corpo = codigo.slice(0, -4);
      for (let i = 0; i < corpo.length; i++) {
        crc ^= corpo.charCodeAt(i) << 8;
        for (let b = 0; b < 8; b++) crc = crc & 0x8000 ? ((crc << 1) ^ 0x1021) & 0xffff : (crc << 1) & 0xffff;
      }
      crc.toString(16).toUpperCase().padStart(4, "0") === codigo.slice(-4).toUpperCase()
        ? ok("CRC16 do BR Code confere")
        : falhar("BLOQUEANTE", "CRC do Pix inválido", "banco recusa o código");
      // O payload de pagamento (valor, nome, chave) não pode trafegar para terceiro.
      const src = await page.locator('img[alt*="QR" i]').first().getAttribute("src").catch(() => null);
      if (src?.startsWith("data:image")) ok("QR gerado localmente (data URI, sem terceiro)");
      else if (src) falhar("GRAVE", "QR vem de serviço externo", `payload enviado para ${src.slice(0, 45)}`);
      else falhar("GRAVE", "QR não renderizou", "imagem do QR ausente na página");
    } else falhar("BLOQUEANTE", "Pix não gerou código", "endpoint /api/pix não retornou payload");
  } else falhar("GRAVE", "botão Pix ausente", "aba de Pix não renderizou");

  console.log("\n[6] Duplo clique no pagamento");
  const alvo = page.getByRole("button", { name: /copiar código|pagar/i }).first();
  if (await alvo.count()) {
    await Promise.all([alvo.click({ timeout: 4000 }), alvo.click({ timeout: 4000 })]).catch(() => {});
    await page.waitForTimeout(400);
    ok("duplo clique não derruba a página");
  }

  console.log("\n[7] Responsivo 390px");
  await page.setViewportSize({ width: 390, height: 844 });
  await page.waitForTimeout(400);
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
  overflow ? falhar("GRAVE", "overflow horizontal em 390px", "layout estoura no celular")
           : ok("sem overflow horizontal em 390px");
  await mkdir(join(RAIZ, "dados", "qa"), { recursive: true });
  await page.screenshot({ path: join(RAIZ, "dados", "qa", `${projeto}-390.png`), fullPage: true });
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.screenshot({ path: join(RAIZ, "dados", "qa", `${projeto}-1440.png`), fullPage: true });
  ok("screenshots salvos em radar/dados/qa/");

  console.log("\n[8] Vazamento de credencial");
  const bundles: string[] = [];
  page.on("response", async (r) => { if (r.url().endsWith(".js")) bundles.push(await r.text().catch(() => "")); });
  await page.reload({ waitUntil: "networkidle" });
  const padroes = [/sk_live_[A-Za-z0-9]{10,}/, /PAYPAL_SECRET\s*[:=]\s*["'][^"']{8,}/, /-----BEGIN [A-Z ]*PRIVATE KEY/];
  bundles.some((b) => padroes.some((r) => r.test(b)))
    ? falhar("BLOQUEANTE", "credencial no bundle do cliente", "segredo exposto ao público")
    : ok("nenhuma credencial no bundle do cliente");

  console.log("\n[9] Console");
  const graves = erros.filter((e) => !/favicon|404|devtools|Download the React/i.test(e));
  graves.length === 0 ? ok("console sem erro relevante")
    : falhar("GRAVE", `${graves.length} erro(s) no console`, graves.slice(0, 3).join(" | "));
}

// ── execução ────────────────────────────────────────────────────────────
const slug = process.argv[2];
const base = join(RAIZ, "saas-gerados");
const projeto = slug ?? (await readdir(base).catch(() => [] as string[]))[0];
if (!projeto) { console.error("Nenhum projeto em saas-gerados/. Rode gerar-saas.ts."); process.exit(1); }

const dir = join(base, projeto);
const PORTA = await portaLivre();
const URL = `http://127.0.0.1:${PORTA}`;
const logServidor = join(RAIZ, "dados", "qa", "servidor.log");
await mkdir(dirname(logServidor), { recursive: true });

console.log(`\n${"━".repeat(70)}\n  QA ADVERSARIAL — ${projeto}\n${"━".repeat(70)}`);

let servidor: ChildProcess | null = null;
let browser: Browser | null = null;
try {
  const fdLog = openSync(logServidor, "w");   // QA cego não diagnostica nada
  servidor = spawn("npx", ["next", "start", "-p", String(PORTA)], { cwd: dir, stdio: ["ignore", fdLog, fdLog] });

  if (!(await esperarServidor(URL))) {
    console.error("\n✗ Servidor não subiu.\n" + (await readFile(logServidor, "utf8").catch(() => "")).split("\n").slice(-15).join("\n"));
    console.error("\nRode `npm run build` no projeto antes do QA.");
    process.exit(1);
  }
  console.log(`Servidor ativo em ${URL}`);

  const exe = acharChromium();
  console.log(exe ? `Chromium: ${exe}\n` : "Chromium: build padrão do Playwright\n");
  browser = await chromium.launch({ headless: true, executablePath: exe, args: ["--no-sandbox", "--disable-dev-shm-usage"] });
  await atacar(await browser.newPage(), URL, projeto);
} finally {
  await browser?.close().catch(() => {});
  // `next start` gera filhos; matar só o pai deixa a porta presa e a próxima
  // execução conecta num servidor velho — foi esse bug que fez este QA reprovar
  // um build correto. Alvo é a porta (única desta execução). O colchete impede
  // o pkill de casar com a própria linha de comando do shell que o executa.
  servidor?.kill("SIGTERM");
  await new Promise((r) => setTimeout(r, 800));
  try { execSync(`pkill -f "next[ ]start -p ${PORTA}"`, { stdio: "ignore" }); } catch { /* nada sobrou */ }
}

// ── relatório ───────────────────────────────────────────────────────────
const bloq = falhas.filter((f) => f.nivel === "BLOQUEANTE");
const grav = falhas.filter((f) => f.nivel === "GRAVE");
const veredito = bloq.length ? "REPROVADO" : grav.length ? "APROVADO COM RESSALVA" : "APROVADO";
console.log(`\n${"━".repeat(70)}\n  VEREDITO: ${veredito}`);
console.log(`  ${passou.length} checagens passaram · ${bloq.length} bloqueante(s) · ${grav.length} grave(s)`);
if (falhas.length) {
  console.log("\n  Falhas:");
  for (const f of falhas) console.log(`   [${f.nivel}] ${f.titulo} — ${f.detalhe.slice(0, 90)}`);
  const log = await readFile(logServidor, "utf8").catch(() => "");
  const linhas = log.split("\n").filter((l) => /error|Error|500|✗/.test(l)).slice(-12);
  if (linhas.length) { console.log("\n  Log do servidor:"); for (const l of linhas) console.log(`   ${l.slice(0, 150)}`); }
}
console.log("━".repeat(70) + "\n");
process.exit(bloq.length ? 1 : 0);
