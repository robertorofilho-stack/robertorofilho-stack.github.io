#!/usr/bin/env node
// Fabrica de carrossel: slides.json -> PNGs 1080x1350 prontos para publicar.
// Uso: node render.mjs projetos/<pasta>            (PNGs em <pasta>/png/)
//      node render.mjs projetos/<pasta> --preview  (so gera preview.html, sem Chromium)
import { readFile, writeFile, mkdir, readdir, unlink } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join, resolve, basename } from 'node:path';

const AQUI = dirname(fileURLToPath(import.meta.url));
const alvo = process.argv[2];
const soPreview = process.argv.includes('--preview');
const semPerda = process.argv.includes('--png');
const ext = semPerda ? 'png' : 'jpg';
if (!alvo) { console.error('uso: node render.mjs projetos/<pasta> [--preview]'); process.exit(1); }

const pasta = resolve(AQUI, alvo);
const dados = JSON.parse(await readFile(join(pasta, 'slides.json'), 'utf8'));
const [L, A] = dados.meta?.formato ?? [1080, 1350];

const template = await readFile(join(AQUI, 'template.html'), 'utf8');
const fontes = await readFile(join(AQUI, 'fontes.css'), 'utf8').catch(() => {
  console.warn('! fontes.css ausente — rode `node fontes.mjs` para embutir a tipografia da marca');
  return '';
});
const html = template
  .replace('/*FONTES*/', () => fontes)
  .replace('/*DADOS*/ null', () => JSON.stringify(dados));

await writeFile(join(pasta, 'preview.html'), html.replace(
  'if (DADOS) mostrar(0);',
  `document.getElementById('palco').innerHTML = DADOS.slides.map((s,i)=>montar(s,i,DADOS.slides.length)).join('');
   document.body.style.cssText='display:flex;flex-direction:column;align-items:center;gap:24px;padding:24px';`
));
console.log(`preview.html gravado (abra no navegador para ver os ${dados.slides.length} slides)`);
if (soPreview) process.exit(0);

// playwright vive em radar/node_modules neste repo; aceita tambem instalacao local ou global
const carregarPlaywright = async () => {
  const tentativas = ['playwright', resolve(AQUI, '../../../radar/node_modules/playwright/index.mjs')];
  for (const alvo of tentativas) {
    try { return await import(alvo); } catch { /* tenta o proximo */ }
  }
  throw new Error('playwright nao encontrado — rode `npm install` em radar/ ou `npm i playwright` aqui');
};
const { chromium } = await carregarPlaywright();
// o Chromium pre-instalado do ambiente ganha do download do playwright (versoes divergem)
const { existsSync } = await import('node:fs');
const binario = [process.env.CHROMIUM_BIN, '/opt/pw-browsers/chromium'].find((c) => c && existsSync(c));
const navegador = await chromium.launch(binario ? { executablePath: binario } : {});
const pagina = await navegador.newPage({ viewport: { width: L, height: A }, deviceScaleFactor: 1 });
await pagina.setContent(html, { waitUntil: 'load' });
await pagina.evaluate(() => document.fonts.ready);

const destino = join(pasta, 'imagens');
await mkdir(destino, { recursive: true });
for (const f of await readdir(destino).catch(() => [])) if (/\.(png|jpg)$/.test(f)) await unlink(join(destino, f));

const estouros = [];
for (let i = 0; i < dados.slides.length; i++) {
  const s = dados.slides[i];
  await pagina.evaluate((n) => mostrar(n), i);
  await pagina.evaluate(() => document.fonts.ready);
  // QA: o texto cabe? slide com overflow corta no feed e ninguem percebe antes de publicar.
  const medida = await pagina.evaluate(() => {
    const el = document.querySelector('.slide');
    return { alto: el.scrollHeight, corpo: document.querySelector('.corpo').scrollHeight, visivel: document.querySelector('.corpo').clientHeight };
  });
  if (medida.alto > A + 1 || medida.corpo > medida.visivel + 1) estouros.push(`${i + 1} (${s.titulo ?? s.tipo}): conteudo ${medida.corpo}px em ${medida.visivel}px`);
  const nome = `${String(i + 1).padStart(2, '0')}-${(s.arquivo ?? s.tipo)}.${ext}`;
  await pagina.locator('.slide').screenshot({ path: join(destino, nome), ...(semPerda ? {} : { type: 'jpeg', quality: 92 }) });
  console.log(`  ${nome}`);
}
await navegador.close();

if (estouros.length) {
  console.error(`\nX TEXTO ESTOURANDO em ${estouros.length} slide(s) — encurte antes de publicar:`);
  for (const e of estouros) console.error(`  - slide ${e}`);
  process.exit(2);
}
console.log(`\nOK ${dados.slides.length} slides ${L}x${A} em ${basename(pasta)}/imagens/`);
