// Folha de conferência: renderiza quadros em tempos escolhidos e monta uma grade.
// Uso: node quadros.mjs aulas/p1-aula1.sync.json saida/folha-p1-aula1.jpg [passo_s]
import { createRequire } from 'node:module'; const { chromium } = createRequire(import.meta.url)('playwright');
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';

const [,, jsonPath, outPath, passoArg] = process.argv;
const passo = Number(passoArg || 4);
const aula = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));
const here = path.dirname(new URL(import.meta.url).pathname);
const tmp = fs.mkdtempSync('/tmp/quadros-');
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
await page.goto('file://' + path.join(here, 'aula.html'));
await page.waitForFunction(() => typeof window.carregarAula === 'function');
await page.evaluate(a => window.carregarAula(a), aula);
await page.evaluate(() => document.fonts.ready);
const tempos = [];
for (let t = 0.6; t < aula.total; t += passo) tempos.push(t);
// garante um quadro no meio de cada cena
for (const c of aula.cenas) tempos.push(c.ini + Math.min(c.dur * 0.6, c.dur - 0.2));
tempos.sort((a, b) => a - b);
let i = 0;
for (const t of tempos) {
  await page.evaluate(tt => window.renderAt(tt), t);
  await page.screenshot({ path: path.join(tmp, `q${String(i++).padStart(3, '0')}.jpg`), type: 'jpeg', quality: 80 });
}
await browser.close();
// grade 3 colunas com ffmpeg tile
const n = i; const cols = 3; const rows = Math.ceil(n / cols);
execFileSync('ffmpeg', ['-y', '-hide_banner', '-loglevel', 'error', '-framerate', '1', '-i', path.join(tmp, 'q%03d.jpg'),
  '-vf', `scale=640:360,tile=${cols}x${rows}:padding=6:margin=6:color=white`, '-frames:v', '1', '-q:v', '3', outPath]);
console.log(`folha ${outPath}: ${n} quadros (passo ${passo}s), tempos: ${tempos.map(t => t.toFixed(1)).join(' ')}`);
