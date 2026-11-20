// SPDX-License-Identifier: MPL-2.0
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import zlib from 'node:zlib';
import { webcrypto } from 'node:crypto';

const html = fs.readFileSync(new URL('../docs/index.html', import.meta.url), 'utf8');
const core = html.split('/* ---- core ---- */')[1].split('/* ---- fine core ---- */')[0];
const api = new Function('crypto', 'CompressionStream', 'DecompressionStream', 'Response', 'TextEncoder', 'TextDecoder', 'URL',
  core + '; return { makeSeb, readSeb, plistDoc, toViewForm, sha256hex };')(
  webcrypto, CompressionStream, DecompressionStream, Response, TextEncoder, TextDecoder, URL);
const schema = JSON.parse(html.match(/const SCHEMA = (\{.*?\});\n/s)[1]);

const entries = [
  ['startURL', 'https://docs.google.com/forms/d/e/ABC/viewform?a=1&b=2'],
  ['browserViewMode', 1], ['allowWlan', false], ['batteryChargeThresholdLow', 0.2, 'float'],
  ['permittedProcesses', [{ active: true, os: 1, title: 'Calc', arguments: [{ active: true, argument: '-a "b"' }] }]],
];

test('file in chiaro: gzip + plist / plain file: gzip + plist', async () => {
  const bytes = await api.makeSeb(entries, null);
  const { xml, enc } = await api.readSeb(new Uint8Array(bytes), null);
  assert.equal(enc, false);
  assert.match(xml, /<key>startURL<\/key>\s*<string>[^<]*a=1&amp;b=2<\/string>/);
  assert.match(xml, /<real>0\.2<\/real>/);
});

test('file cifrato: prefisso pswd e giro completo / encrypted file round trip', async () => {
  const bytes = await api.makeSeb(entries, 'Pässword1');
  assert.equal(zlib.gunzipSync(Buffer.from(bytes)).subarray(0, 4).toString(), 'pswd');
  const { xml, enc } = await api.readSeb(new Uint8Array(bytes), 'Pässword1');
  assert.equal(enc, true);
  assert.match(xml, /Calc/);
});

test('password errata o mancante / wrong or missing password', async () => {
  const bytes = new Uint8Array(await api.makeSeb(entries, 'giusta'));
  await assert.rejects(api.readSeb(bytes, 'sbagliata'), { code: 'password' });
  await assert.rejects(api.readSeb(bytes, null), { code: 'need-password' });
});

test('link di modifica convertito in viewform / edit link becomes viewform', () => {
  assert.equal(api.toViewForm('https://docs.google.com/forms/d/XYZ/edit'), 'https://docs.google.com/forms/d/XYZ/viewform');
  const pub = 'https://docs.google.com/forms/d/e/ABC/viewform?usp=publish-editor';
  assert.equal(api.toViewForm(pub), pub);
});

test('hash SHA-256 della password di uscita / quit password hash', async () => {
  assert.equal(await api.sha256hex('EsciDaQuestoModulo!'), 'ba6a952c180bffae9eccffb098e910e2b5945300169757b4fb9ea8bbe5f63020');
});

test('schema coerente / schema is consistent', () => {
  const tabs = new Set(schema.tabs.map((t) => t[0]));
  const seen = new Set();
  for (const e of schema.items) {
    assert.ok(tabs.has(e.tab), `scheda sconosciuta ${e.tab} per ${e.k}`);
    assert.ok(!seen.has(e.k), `chiave duplicata ${e.k}`);
    seen.add(e.k);
    assert.ok(['bool', 'int', 'float', 'string', 'pw'].includes(e.t), `tipo ${e.t} per ${e.k}`);
    if (e.o) assert.ok(e.o.length >= 2, `opzioni di ${e.k}`);
  }
  for (const k of ['startURL', 'browserViewMode', 'newBrowserWindowByLinkPolicy', 'allowWlan', 'hashedQuitPassword', 'hideWiFiControls'])
    assert.ok(seen.has(k), `manca ${k}`);
  assert.ok(schema.items.some((e) => e.p === 'm'), 'nessuna impostazione solo Mac');
  assert.ok(schema.items.some((e) => e.p === 'w'), 'nessuna impostazione solo Windows');
  assert.ok(tabs.has('res') && tabs.has('proc'), 'schede res/proc mancanti');
});
