import assert from 'node:assert/strict';
import { sha256, norm, buildUserData, buildEvent, hotmartToEvent } from './capi.mjs';

// Valores de referência publicados na doc da Meta.
assert.equal(await sha256(norm.em(' John_Smith@gmail.com ')), '62a14e44f765419d10fea99367361a727c12365e2520f32218d505ed9aa0f62f');
assert.equal(await sha256('16505551212'), 'e323ec626319ca94ee8bff2e4c87cf613be6ea19919ed1364124e16807ab3176');
assert.equal(await sha256('us'), '79adb2a2fce5c6ba215fe5f27f532d4e7edbac4b6a5e09e1ef3a08084a904621');
assert.equal(norm.ph('(650)555-1212', '1'), '16505551212');
assert.equal(norm.ph('(85) 99762-4221'), '5585997624221');

const ud = await buildUserData({ email: 'A@b.com', fbp: 'fb.1.1.2', fbc: 'fb.1.1.abc' }, { ip: '1.2.3.4', ua: 'x' });
assert.equal(ud.client_ip_address, '1.2.3.4');          // IP nunca hasheado
assert.equal(ud.fbp, 'fb.1.1.2');                         // fbp/fbc nunca hasheados
assert.match(ud.em[0], /^[0-9a-f]{64}$/);
assert.ok(ud.country);                                    // país sempre presente

await assert.rejects(() => buildEvent({ name: 'Lead' }, {}), /event_id/); // sem event_id = sem dedup = recusa

assert.equal(await hotmartToEvent({ event: 'PURCHASE_CANCELED' }, {}), null);
const ev = await hotmartToEvent({ event: 'PURCHASE_APPROVED', data: { purchase: { transaction: 'HP1', price: { value: 97, currency_value: 'BRL' } }, buyer: { email: 'x@y.com', name: 'Maria da Silva' } } }, {});
assert.equal(ev.event_id, 'hotmart_HP1');
assert.equal(ev.custom_data.value, 97);
console.log('OK — 100% dos testes passaram');
