#!/usr/bin/env node
// Baixa as fontes da marca do Google Fonts e embute em fontes.css como data URI.
// Roda uma vez. Depois disso a fabrica de carrossel renderiza offline, sempre igual.
// Uso: node fontes.mjs
import { writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const AQUI = dirname(fileURLToPath(import.meta.url));
const UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36';
const API = 'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Manrope:wght@400;500;700;800&display=swap';

// So latin e latin-ext: portugues cabe inteiro e o arquivo fica pequeno.
const SERVE = (faixa) => /U\+0000-00FF/.test(faixa) || /U\+0100-02(AF|BA)/.test(faixa);

const buscar = async (url, tipo = 'text') => {
  const r = await fetch(url, { headers: { 'User-Agent': UA } });
  if (!r.ok) throw new Error(`${r.status} ao buscar ${url}`);
  return tipo === 'buffer' ? Buffer.from(await r.arrayBuffer()) : r.text();
};

const css = await buscar(API);
const blocos = css.split('@font-face').slice(1).map((b) => '@font-face' + b.split('}')[0] + '}');

const saida = [];
let embutidas = 0;
for (const bloco of blocos) {
  const faixa = (bloco.match(/unicode-range:\s*([^;]+);/) || [])[1] || '';
  if (!SERVE(faixa)) continue;
  const url = (bloco.match(/url\((https:[^)]+)\)/) || [])[1];
  if (!url) continue;
  const bytes = await buscar(url, 'buffer');
  saida.push(bloco.replace(/url\(https:[^)]+\)/, `url(data:font/woff2;base64,${bytes.toString('base64')})`));
  embutidas++;
}
if (embutidas === 0) throw new Error('nenhuma fonte embutida — a API do Google mudou de formato');

await writeFile(join(AQUI, 'fontes.css'), `/* gerado por fontes.mjs — nao editar a mao */\n${saida.join('\n')}\n`);
console.log(`fontes.css gravado: ${embutidas} arquivos embutidos`);
