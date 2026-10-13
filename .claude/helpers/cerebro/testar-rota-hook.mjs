#!/usr/bin/env node
// Testes do rota-hook.mjs: transcript falso + CAPACIDADES.json falso, hook rodado como processo (stdin JSON).
import { mkdtempSync, writeFileSync, readFileSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import assert from 'node:assert/strict';

const AQUI = dirname(fileURLToPath(import.meta.url));
const HOOK = join(AQUI, 'rota-hook.mjs');
const { extrairRota, validar } = await import(HOOK);
const d = mkdtempSync(join(tmpdir(), 'rota-'));
const CAPS = join(d, 'CAPACIDADES.json');
writeFileSync(CAPS, JSON.stringify({
  dominios: { VENDER: {}, PENSAR: {}, INEDITO: {} },
  capacidades: [{ id: 'diretor-de-vendas', tipo: 'diretor' }, { id: 'scrape', tipo: 'skill' }, { id: 'prospeccao-com-agentes', tipo: 'skill' }, { id: 'diretor-arcanjo', tipo: 'diretor' }],
}));

function transcript(pedido, resposta) {
  const p = join(d, `t-${Math.random().toString(36).slice(2)}.jsonl`);
  const linhas = [
    JSON.stringify({ type: 'user', message: { role: 'user', content: pedido } }),
    JSON.stringify({ type: 'assistant', message: { role: 'assistant', content: [{ type: 'tool_use', name: 'Bash' }] } }),
    JSON.stringify({ type: 'user', message: { role: 'user', content: [{ type: 'tool_result', content: 'saida' }] } }),
    JSON.stringify({ type: 'assistant', message: { role: 'assistant', content: [{ type: 'text', text: resposta }] } }),
  ];
  writeFileSync(p, linhas.join('\n') + '\n');
  return p;
}

function rodar(evt, env = {}) {
  const log = join(d, `log-${Math.random().toString(36).slice(2)}.jsonl`);
  const r = spawnSync(process.execPath, [HOOK], { input: JSON.stringify(evt), encoding: 'utf8', env: { ...process.env, CEREBRO_CAPACIDADES: CAPS, CEREBRO_ROTA_LOG: log, ROTA_BLOQUEAR: '', ...env }, timeout: 10000 });
  const linhas = existsSync(log) ? readFileSync(log, 'utf8').trim().split('\n').map((l) => JSON.parse(l)) : [];
  return { status: r.status, stdout: r.stdout, registro: linhas[linhas.length - 1] };
}

let n = 0;
function teste(nome, fn) { fn(); n++; console.log('  ✓', nome); }

teste('extrairRota lê variações de formato', () => {
  const r = extrairRota('Oi.\n**ROTA:** dominio=VENDER | diretor=diretor-de-vendas | capacidades=/scrape, prospeccao-com-agentes | nivel=1\ntexto');
  assert.deepEqual(r.dominios, ['VENDER']); assert.equal(r.diretor, 'diretor-de-vendas');
  assert.deepEqual(r.capacidades, ['scrape', 'prospeccao-com-agentes']); assert.equal(r.nivel, '1');
  const r2 = extrairRota('ROTA: domínios=Vender+Pensar · diretor: Skill diretor-arcanjo · ferramentas: nenhuma, porque é conversa · nível: 0');
  assert.deepEqual(r2.dominios, ['VENDER', 'PENSAR']); assert.equal(r2.diretor, 'diretor-arcanjo'); assert.equal(r2.nivel, '0');
  assert.equal(extrairRota('sem linha nenhuma'), null);
});

teste('validar aceita o certo e acusa o errado', () => {
  const caps = { dominios: new Set(['VENDER', 'INEDITO']), diretores: new Set(['diretor-de-vendas']), ids: new Set(['diretor-de-vendas', 'scrape']) };
  assert.equal(validar({ dominios: ['VENDER'], diretor: 'diretor-de-vendas', capacidades: ['scrape'], nivel: '1' }, caps).valida, true);
  assert.equal(validar({ dominios: ['INEDITO'], diretor: 'diretor-de-vendas', capacidades: ['nenhuma, porque x'], nivel: '1' }, caps).valida, true);
  const v = validar({ dominios: ['FINANCAS'], diretor: 'diretor-inventado', capacidades: ['foo'], nivel: '' }, caps);
  assert.equal(v.valida, false); assert.equal(v.erros.length, 4);
  assert.deepEqual(validar(null, caps).erros, ['linha ROTA ausente']);
});

teste('sombra: registra e nunca bloqueia, mesmo sem ROTA', () => {
  const t = transcript('me traz as clínicas de fisioterapia de Fortaleza', 'Aqui está a lista…');
  const { status, stdout, registro } = rodar({ session_id: 's1', transcript_path: t, stop_hook_active: false });
  assert.equal(status, 0); assert.equal(stdout, '');
  assert.equal(registro.presente, false); assert.equal(registro.valida, false); assert.equal(registro.modo, 'sombra');
  assert.equal(registro.pedido, 'me traz as clínicas de fisioterapia de Fortaleza'); assert.equal(registro.indice, 'sim');
});

teste('sombra: ROTA válida fica registrada como válida', () => {
  const t = transcript('quero vender para dentistas', 'ROTA: dominio=VENDER | diretor=diretor-de-vendas | capacidades=/scrape | nivel=1\n\nSegue…');
  const { registro } = rodar({ session_id: 's2', transcript_path: t });
  assert.equal(registro.presente, true); assert.equal(registro.valida, true); assert.deepEqual(registro.erros, []);
  assert.equal(registro.diretor, 'diretor-de-vendas');
});

teste('bloqueio: sem ROTA devolve decision=block com o vocabulário, uma vez', () => {
  const t = transcript('monta uma oferta para o kit', 'Oferta: …');
  const a = rodar({ session_id: 's3', transcript_path: t, stop_hook_active: false }, { ROTA_BLOQUEAR: '1' });
  const j = JSON.parse(a.stdout);
  assert.equal(j.decision, 'block'); assert.match(j.reason, /ROTA: dominio=/); assert.match(j.reason, /diretor-de-vendas/); assert.match(j.reason, /linha ROTA ausente/);
  const b = rodar({ session_id: 's3', transcript_path: t, stop_hook_active: true }, { ROTA_BLOQUEAR: '1' });
  assert.equal(b.stdout, '');                                       // já devolvemos uma vez: não insiste
  assert.equal(b.registro.stop_hook_active, true);
});

teste('bloqueio: diretor fora do índice também bloqueia; válida passa', () => {
  const t1 = transcript('faz o laudo do paciente', 'ROTA: dominio=MEDICO | diretor=diretor-fantasma | capacidades=laudo | nivel=1\n…');
  const a = rodar({ transcript_path: t1 }, { ROTA_BLOQUEAR: '1' });
  assert.match(JSON.parse(a.stdout).reason, /diretor fora do índice: diretor-fantasma/);
  const t2 = transcript('faz o laudo do paciente', 'ROTA: dominio=INEDITO | diretor=diretor-arcanjo | capacidades=nenhuma, porque não há skill de laudo no índice de teste | nivel=1\n…');
  const b = rodar({ transcript_path: t2 }, { ROTA_BLOQUEAR: '1' });
  assert.equal(b.stdout, ''); assert.equal(b.registro.valida, true);
});

teste('pedido trivial não exige ROTA e não bloqueia', () => {
  const t = transcript('ok', 'Beleza.');
  const a = rodar({ transcript_path: t }, { ROTA_BLOQUEAR: '1' });
  assert.equal(a.stdout, ''); assert.equal(a.registro.trivial, true); assert.deepEqual(a.registro.erros, ['trivial']);
});

teste('fail-open: transcript inexistente, stdin vazio ou JSON quebrado → sai 0 sem saída', () => {
  for (const input of ['', '{nao json', JSON.stringify({ transcript_path: '/nao/existe.jsonl' })]) {
    const r = spawnSync(process.execPath, [HOOK], { input, encoding: 'utf8', env: { ...process.env, CEREBRO_CAPACIDADES: CAPS, CEREBRO_ROTA_LOG: join(d, 'x.jsonl'), ROTA_BLOQUEAR: '1' }, timeout: 10000 });
    assert.equal(r.status, 0); assert.equal(r.stdout, '');
  }
});

teste('sem índice: valida só a forma (não inventa diretor) e registra indice=nao', () => {
  const t = transcript('quero vender para dentistas', 'ROTA: dominio=VENDER | diretor=diretor-qualquer | capacidades=x | nivel=2');
  const vazio = mkdtempSync(join(tmpdir(), 'vazio-'));
  const a = rodar({ transcript_path: t }, { CEREBRO_CAPACIDADES: '/nao/existe.json', CLAUDE_PROJECT_DIR: vazio, HOME: vazio });
  assert.equal(a.registro.indice, 'nao'); assert.equal(a.registro.valida, true);
});

console.log(`rota-hook: ${n} testes OK`);
