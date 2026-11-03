// Renderiza uma aula (JSON com cenas já sincronizadas) para MP4, quadro a quadro, via Playwright + ffmpeg.
// Uso: node render.mjs aulas/p1-aula1.sync.json saida/p1-aula1.mp4 [fps]
import { createRequire } from 'node:module'; const { chromium } = createRequire(import.meta.url)('playwright');
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const [,, jsonPath, outPath, fpsArg] = process.argv;
const FPS = Number(fpsArg || 30);
const aula = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));
const total = aula.total;
const nFrames = Math.ceil(total * FPS);
const here = path.dirname(new URL(import.meta.url).pathname);

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
await page.goto('file://' + path.join(here, 'aula.html'));
await page.waitForFunction(() => typeof window.carregarAula === 'function');
await page.evaluate(a => window.carregarAula(a), aula);
await page.evaluate(() => document.fonts.ready);

const ff = spawn('ffmpeg', ['-y', '-hide_banner', '-loglevel', 'error',
  '-f', 'image2pipe', '-framerate', String(FPS), '-vcodec', 'mjpeg', '-i', '-',
  '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', '-r', String(FPS),
  '-movflags', '+faststart', outPath]);
ff.stderr.on('data', d => process.stderr.write(d));
const done = new Promise((res, rej) => { ff.on('close', c => c === 0 ? res() : rej(new Error('ffmpeg saiu com ' + c))); });

const t0 = Date.now();
for (let i = 0; i < nFrames; i++) {
  const t = i / FPS;
  await page.evaluate(tt => window.renderAt(tt), t);
  const buf = await page.screenshot({ type: 'jpeg', quality: 90, animations: 'disabled', caret: 'hide' });
  if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  if (i % (FPS * 10) === 0) process.stderr.write(`  ${path.basename(outPath)}: ${t.toFixed(0)}s/${total.toFixed(0)}s (${((Date.now() - t0) / 1000).toFixed(0)}s)\n`);
}
ff.stdin.end();
await done;
await browser.close();
console.log(`ok ${outPath} ${nFrames} quadros em ${((Date.now() - t0) / 1000).toFixed(0)}s`);
