// Renderiza cenas HTML animadas em quadros JPEG (usado por noticia-em-video.py).
// node renderizar.cjs lista.json pasta_quadros fps   — lista = [[arquivo_html, duracao_s], ...]
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const [lista, pasta, fps] = [JSON.parse(fs.readFileSync(process.argv[2])), process.argv[3], +process.argv[4]];
  const png = process.argv[5] === 'png';  // quadros transparentes para sobrepor ao vídeo do avatar
  const nav = await chromium.launch();
  const pg = await nav.newPage({ viewport: { width: 1080, height: 1920 } });
  let n = 0;
  for (const [arq, dur] of lista) {
    await pg.goto('file://' + arq);
    await pg.waitForTimeout(500);
    await pg.evaluate(() => document.fonts.ready);
    await pg.evaluate(() => document.getAnimations().forEach(a => a.pause()));
    for (let k = 0; k < Math.floor(dur * fps); k++) {
      await pg.evaluate(t => document.getAnimations().forEach(a => (a.currentTime = t)), (k * 1000) / fps);
      await pg.screenshot(png ? { path: path.join(pasta, `q${String(n).padStart(5, '0')}.png`), type: 'png', omitBackground: true }
                             : { path: path.join(pasta, `q${String(n).padStart(5, '0')}.jpg`), type: 'jpeg', quality: 88 });
      n++;
    }
  }
  await nav.close();
  console.log(n);
})().catch(e => { console.error(e); process.exit(1); });
