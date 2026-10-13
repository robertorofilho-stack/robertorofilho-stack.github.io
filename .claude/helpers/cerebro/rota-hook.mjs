#!/usr/bin/env node
// ROTA-HOOK — o contrato de roteamento, conferido por código (hook Stop).
//
// Decisão de 13/10/2026 (organizacao-cerebro-diagnostico-e-proposta-13-10): toda missão não-trivial abre a resposta com
//   ROTA: dominio=VENDER | diretor=diretor-de-vendas | capacidades=/scrape,prospeccao-com-agentes | nivel=1
// Este hook lê a última resposta no transcript, procura a linha, valida cada valor contra CAPACIDADES.json
// (domínios + INEDITO, diretores, capacidades) e grava ~/.cache/cerebro/roteamento.jsonl. É a telemetria de
// "o Cérebro nomeou o diretor?" em 100 % das missões — não em 30 amostras.
//
// MODO SOMBRA (padrão): só registra; nunca bloqueia. MODO BLOQUEIO: existe o arquivo ~/.cache/cerebro/rota-bloquear
// (ou ROTA_BLOQUEAR=1) → linha ausente/inválida devolve {"decision":"block","reason":…} UMA vez por missão
// (stop_hook_active=true = já devolvemos; não insistir — anti-loop).
// Fail-open: qualquer erro → sai 0 em silêncio. O hook nunca pode travar uma sessão.
import { existsSync, readFileSync, appendFileSync, mkdirSync, openSync, readSync, fstatSync, closeSync } from 'node:fs';
import { homedir } from 'node:os';
import { join, dirname } from 'node:path';

const HOME = process.env.HOME || homedir();
const CACHE = process.env.XDG_CACHE_HOME ? join(process.env.XDG_CACHE_HOME, 'cerebro') : join(HOME, '.cache', 'cerebro');
const LOG = process.env.CEREBRO_ROTA_LOG || join(CACHE, 'roteamento.jsonl');
const SINAL_BLOQUEIO = join(CACHE, 'rota-bloquear');
const DOMINIOS_PADRAO = ['VENDER', 'CONTEUDO', 'MEDICO', 'EMPRESA', 'CONSTRUIR', 'PENSAR', 'CEREBRO', 'INEDITO'];
const TRIVIAL = /^(ok|blz|beleza|sim|nao|não|valeu|obrigado|vlw|isso|certo|perfeito|top|continue|continua|vai|pode|segue)[\s.!?]*$/i;

function candidatosCapacidades() {
  const c = [];
  if (process.env.CEREBRO_CAPACIDADES) c.push(process.env.CEREBRO_CAPACIDADES);
  if (process.env.CLAUDE_PROJECT_DIR) c.push(join(process.env.CLAUDE_PROJECT_DIR, '.claude', 'CAPACIDADES.json'), join(process.env.CLAUDE_PROJECT_DIR, 'CAPACIDADES.json'));
  c.push(join(HOME, 'Claude', 'cerebro-backup', 'CAPACIDADES.json'), join(HOME, 'cerebro-backup', 'CAPACIDADES.json'), join(HOME, '.claude', 'CAPACIDADES.json'));
  return c;
}

function carregarCapacidades() {
  for (const p of candidatosCapacidades()) {
    try {
      if (!existsSync(p)) continue;
      const j = JSON.parse(readFileSync(p, 'utf8'));
      const caps = Array.isArray(j.capacidades) ? j.capacidades : [];
      return {
        caminho: p,
        dominios: new Set(Object.keys(j.dominios || {}).concat(DOMINIOS_PADRAO)),
        diretores: new Set(caps.filter((x) => x.tipo === 'diretor').map((x) => x.id)),
        ids: new Set(caps.map((x) => x.id)),
      };
    } catch { /* tenta o próximo */ }
  }
  return { caminho: '', dominios: new Set(DOMINIOS_PADRAO), diretores: new Set(), ids: new Set() };
}

// Lê só a cauda do transcript (há transcripts de centenas de MB nesta máquina).
function cauda(caminho, max = 512 * 1024) {
  const fd = openSync(caminho, 'r');
  try {
    const tam = fstatSync(fd).size;
    const n = Math.min(tam, max);
    const buf = Buffer.alloc(n);
    readSync(fd, buf, 0, n, tam - n);
    let s = buf.toString('utf8');
    if (tam > n) s = s.slice(s.indexOf('\n') + 1);     // descarta a linha cortada
    return s;
  } finally { closeSync(fd); }
}

function textoDe(conteudo) {
  if (typeof conteudo === 'string') return conteudo;
  if (!Array.isArray(conteudo)) return '';
  return conteudo.filter((b) => b && b.type === 'text' && typeof b.text === 'string').map((b) => b.text).join('\n');
}

function ultimasMensagens(linhas) {
  let pedido = '', resposta = '';
  for (let i = linhas.length - 1; i >= 0; i--) {
    let o; try { o = JSON.parse(linhas[i]); } catch { continue; }
    const m = o && o.message;
    if (!m) continue;
    if (!resposta && o.type === 'assistant') { resposta = textoDe(m.content); continue; }
    if (resposta && o.type === 'user') {
      const t = textoDe(m.content);
      if (t.trim()) { pedido = t; break; }                 // pula tool_result (content sem bloco de texto)
    }
  }
  return { pedido, resposta };
}

export function extrairRota(texto) {
  const m = /^[ \t>*_]*ROTA\s*:\s*(.+)$/im.exec(texto || '');
  if (!m) return null;
  const campos = {};
  for (const parte of m[1].split(/\s*[|·]\s*/)) {
    const mm = /^\s*([a-zA-Z\u00C0-\u024F_]+)\s*[=:]\s*(.+?)\s*$/.exec(parte.replace(/\*\*/g, ''));
    if (!mm) continue;
    const k = mm[1].toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
    const v = mm[2].replace(/`/g, '').trim();
    if (k.startsWith('domin')) campos.dominios = v.split(/[,/+ ]+/).map((x) => x.trim().toUpperCase().normalize('NFD').replace(/[̀-ͯ]/g, '')).filter(Boolean);
    else if (k.startsWith('diret')) campos.diretor = v.toLowerCase().replace(/^skill\s+/, '');
    else if (k.startsWith('capac') || k.startsWith('ferram')) {
      campos.capacidades = /^nenhum/i.test(v) ? [v]            // "nenhuma, porque …" é UM valor, não uma lista
        : v.split(/[,+]+/).map((x) => x.trim().replace(/^\//, '').replace(/^agent\(.*?=|\)$/g, '')).filter(Boolean);
    }
    else if (k.startsWith('nivel')) campos.nivel = v.replace(/[^0-3]/g, '').slice(0, 1);
  }
  return campos;
}

export function validar(rota, caps) {
  const erros = [];
  if (!rota) return { valida: false, erros: ['linha ROTA ausente'] };
  if (!rota.dominios || !rota.dominios.length) erros.push('sem dominio');
  else for (const d of rota.dominios) if (!caps.dominios.has(d)) erros.push(`dominio desconhecido: ${d}`);
  if (!rota.diretor) erros.push('sem diretor');
  else if (rota.diretor !== 'nenhum' && caps.diretores.size && !caps.diretores.has(rota.diretor)) erros.push(`diretor fora do índice: ${rota.diretor}`);
  if (rota.capacidades && caps.ids.size) {
    for (const c of rota.capacidades) {
      if (/^nenhuma?\b/i.test(c)) continue;
      if (!caps.ids.has(c)) erros.push(`capacidade fora do índice: ${c}`);
    }
  }
  if (rota.nivel === undefined || rota.nivel === '') erros.push('sem nivel');
  return { valida: erros.length === 0, erros };
}

function razao(caps) {
  const dirs = [...caps.diretores].slice(0, 12).join(', ');
  return `Contrato do Cérebro (13/10/2026): abra a resposta com UMA linha\n` +
    `ROTA: dominio=<${[...caps.dominios].join('|')}> | diretor=<nome do índice ou nenhum> | capacidades=<ids do índice ou nenhuma, porque…> | nivel=<0-3>\n` +
    (dirs ? `Diretores conhecidos: ${dirs}.\n` : '') +
    `Pedido fora do mapa: dominio=INEDITO | diretor=diretor-arcanjo e declare a suposição. Depois repita a resposta inteira.`;
}

async function lerStdin() {
  return new Promise((res) => {
    let s = '';
    const t = setTimeout(() => res(s), 2500);
    process.stdin.on('data', (d) => { s += d; });
    process.stdin.on('end', () => { clearTimeout(t); res(s); });
    process.stdin.on('error', () => { clearTimeout(t); res(s); });
  });
}

async function main() {
  let evt = {};
  try { evt = JSON.parse(await lerStdin() || '{}'); } catch { return; }
  const tpath = evt.transcript_path;
  if (!tpath || !existsSync(tpath)) return;
  const { pedido, resposta } = ultimasMensagens(cauda(tpath).split('\n'));
  if (!resposta) return;
  const trivial = pedido.trim().length < 12 || TRIVIAL.test(pedido.trim());
  const caps = carregarCapacidades();
  const rota = extrairRota(resposta);
  const { valida, erros } = trivial && !rota ? { valida: true, erros: ['trivial'] } : validar(rota, caps);
  const bloqueio = !!process.env.ROTA_BLOQUEAR || existsSync(SINAL_BLOQUEIO);
  const registro = {
    ts: new Date().toISOString(), sessao: evt.session_id || '', modo: bloqueio ? 'bloqueio' : 'sombra',
    trivial, presente: !!rota, valida, erros,
    dominios: rota?.dominios || [], diretor: rota?.diretor || '', capacidades: rota?.capacidades || [], nivel: rota?.nivel ?? '',
    pedido: pedido.replace(/\s+/g, ' ').slice(0, 160), indice: caps.caminho ? 'sim' : 'nao', stop_hook_active: !!evt.stop_hook_active,
  };
  try { mkdirSync(dirname(LOG), { recursive: true }); appendFileSync(LOG, JSON.stringify(registro) + '\n'); } catch { /* silêncio */ }
  if (bloqueio && !valida && !trivial && !evt.stop_hook_active) {
    process.stdout.write(JSON.stringify({ decision: 'block', reason: `${razao(caps)}\nFaltou: ${erros.join('; ')}.` }));
  }
}

if (process.argv[1] && /rota-hook\.mjs$/.test(process.argv[1])) {
  main().catch(() => {}).finally(() => process.exit(0));
}
