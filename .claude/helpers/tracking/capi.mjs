// Núcleo do tracking server-side (Meta Conversions API). Funções puras + um handler de Worker.
// Segredos vêm de env (META_PIXEL_ID, META_CAPI_TOKEN, HOTMART_HOTTOK, ALLOWED_ORIGIN) — nunca no git.

const GRAPH = 'v21.0';

export async function sha256(v) {
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(v));
  return [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, '0')).join('');
}

// Normalizações exatamente como a doc da Meta (customer information parameters).
export const norm = {
  em: v => String(v).trim().toLowerCase(),
  ph: (v, ddi = '55') => {
    let d = String(v).replace(/\D/g, '').replace(/^0+/, '');
    if (d.length <= 11) d = ddi + d; // BR sem DDI -> acrescenta 55
    return d;
  },
  name: v => String(v).trim().toLowerCase().replace(/[^\p{L}\p{N}]/gu, ''),
  city: v => String(v).trim().toLowerCase().replace(/[^\p{L}\p{N}]/gu, ''),
  zp: v => String(v).trim().toLowerCase().replace(/[\s-]/g, ''),
  country: v => String(v).trim().toLowerCase().slice(0, 2),
};

export async function buildUserData(u = {}, ctx = {}) {
  const out = {};
  const h = async (k, v) => { if (v) out[k] = [await sha256(v)]; };
  await h('em', u.email && norm.em(u.email));
  await h('ph', u.phone && norm.ph(u.phone));
  if (u.name) {
    const [fn, ...rest] = String(u.name).trim().split(/\s+/);
    await h('fn', norm.name(fn));
    if (rest.length) await h('ln', norm.name(rest[rest.length - 1]));
  }
  await h('ct', u.city && norm.city(u.city));
  await h('st', u.state && norm.city(u.state));
  await h('zp', u.zip && norm.zp(u.zip));
  await h('country', norm.country(u.country || 'br'));
  await h('external_id', u.external_id);
  // NÃO hasheados:
  if (ctx.ip) out.client_ip_address = ctx.ip;
  if (ctx.ua) out.client_user_agent = ctx.ua;
  if (u.fbp) out.fbp = u.fbp;
  if (u.fbc) out.fbc = u.fbc;
  return out;
}

export async function buildEvent({ name, eventId, url, user, custom, time, source = 'website' }, ctx) {
  if (!name || !eventId) throw new Error('event_name e event_id são obrigatórios (dedup)');
  return {
    event_name: name,
    event_time: time || Math.floor(Date.now() / 1000),
    event_id: eventId,
    action_source: source,
    event_source_url: url,
    user_data: await buildUserData(user, ctx),
    ...(custom ? { custom_data: custom } : {}),
  };
}

export async function sendToMeta(events, env, fetchFn = fetch) {
  const r = await fetchFn(
    `https://graph.facebook.com/${GRAPH}/${env.META_PIXEL_ID}/events?access_token=${env.META_CAPI_TOKEN}`,
    { method: 'POST', headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ data: events, ...(env.META_TEST_CODE ? { test_event_code: env.META_TEST_CODE } : {}) }) });
  return { ok: r.ok, status: r.status, body: await r.json().catch(() => ({})) };
}

// Hotmart -> Purchase server-side. Só PURCHASE_APPROVED. event_id = transação (dedup natural).
export async function hotmartToEvent(payload, ctx) {
  if (payload?.event !== 'PURCHASE_APPROVED') return null;
  const d = payload.data || {}, p = d.purchase || {}, b = d.buyer || {};
  return buildEvent({
    name: 'Purchase', eventId: `hotmart_${p.transaction}`, source: 'website',
    time: p.approved_date ? Math.floor(p.approved_date / 1000) : undefined,
    user: { email: b.email, phone: b.checkout_phone || b.phone, name: b.name, external_id: b.email },
    custom: { value: p.price?.value, currency: p.price?.currency_value || 'BRL', order_id: p.transaction },
  }, ctx);
}

const cors = env => ({ 'access-control-allow-origin': env.ALLOWED_ORIGIN || '', 'access-control-allow-headers': 'content-type',
  'access-control-allow-methods': 'POST,OPTIONS' });

export default {
  async fetch(req, env) {
    const path = new URL(req.url).pathname;
    if (req.method === 'OPTIONS') return new Response(null, { headers: cors(env) });
    if (req.method !== 'POST') return new Response('ok');
    const ctx = { ip: req.headers.get('cf-connecting-ip'), ua: req.headers.get('user-agent') };
    const body = await req.json().catch(() => null);
    if (!body) return new Response('bad json', { status: 400 });

    if (path === '/hotmart') {
      if (req.headers.get('x-hotmart-hottok') !== env.HOTMART_HOTTOK) return new Response('forbidden', { status: 403 });
      const ev = await hotmartToEvent(body, ctx);
      if (!ev) return new Response('ignored');
      const res = await sendToMeta([ev], env);
      return Response.json(res, { status: res.ok ? 200 : 502 });
    }
    // /event vindo do navegador (mesmo event_id do fbq para dedup)
    if (req.headers.get('origin') !== env.ALLOWED_ORIGIN) return new Response('forbidden', { status: 403, headers: cors(env) });
    const ev = await buildEvent({ name: body.name, eventId: body.eventId, url: body.url, user: body.user, custom: body.custom }, ctx);
    const res = await sendToMeta([ev], env);
    return Response.json(res, { status: res.ok ? 200 : 502, headers: cors(env) });
  },
};
