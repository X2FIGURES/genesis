#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const file = join(dirname(fileURLToPath(import.meta.url)), '..', 'docs/data/state.json');
let data;
try {
  data = JSON.parse(readFileSync(file, 'utf8'));
} catch (e) {
  console.error('state.json: cannot read or parse:', e.message);
  process.exit(1);
}

function fail(msg) {
  console.error('state.json: ' + msg);
  process.exit(1);
}

if (data.schemaVersion !== 1) fail('schemaVersion must be 1');
if (typeof data.updatedAt !== 'string' || !data.updatedAt) fail('updatedAt must be a non-empty string');
if (typeof data.updatedBy !== 'string') fail('updatedBy must be a string');

const acc = data.account;
if (!acc || typeof acc !== 'object') fail('account object required');
if (typeof acc.start !== 'number' || acc.start < 0) fail('account.start must be a number >= 0');
if (acc.balance !== null && (typeof acc.balance !== 'number' || !isFinite(acc.balance))) {
  fail('account.balance must be null or a finite number');
}
if (typeof acc.goal !== 'number' || acc.goal <= 0) fail('account.goal must be a positive number');
if (!Array.isArray(acc.rungs) || !acc.rungs.every((n) => typeof n === 'number' && n > 0)) {
  fail('account.rungs must be an array of positive numbers');
}

if (!Array.isArray(data.ladder)) fail('ladder must be an array');
for (const row of data.ladder) {
  if (typeof row.balance !== 'number' || typeof row.lot !== 'number') {
    fail('each ladder row needs balance and lot numbers');
  }
}

const sess = data.session;
if (!sess || typeof sess !== 'object') fail('session object required');
const states = new Set(['ready', 'standaside', 'done']);
if (!states.has(sess.state)) fail('session.state must be ready, standaside, or done');
if (typeof sess.tradesTaken !== 'number' || sess.tradesTaken < 0) fail('session.tradesTaken must be >= 0');
if (typeof sess.losses !== 'number' || sess.losses < 0) fail('session.losses must be >= 0');
if (typeof sess.maxTrades !== 'number' || typeof sess.maxLosses !== 'number') {
  fail('session.maxTrades and maxLosses required');
}
if (sess.losses > sess.maxLosses) fail('session.losses must be <= maxLosses');
if (sess.date !== null && typeof sess.date !== 'string') fail('session.date must be null or YYYY-MM-DD string');

const ct = data.cleanTrades;
if (!ct || typeof ct !== 'object') fail('cleanTrades object required');
if (typeof ct.target !== 'number' || ct.target < 1) fail('cleanTrades.target must be >= 1');
if (!Array.isArray(ct.seq) || !ct.seq.every((b) => typeof b === 'boolean')) {
  fail('cleanTrades.seq must be an array of booleans');
}

if (!Array.isArray(data.days)) fail('days must be an array');
const dayRe = /^\d{4}-\d{2}-\d{2}$/;
for (const d of data.days) {
  if (!d || typeof d.date !== 'string' || !dayRe.test(d.date)) fail('days[].date must be YYYY-MM-DD');
  if (typeof d.trades !== 'number' || typeof d.clean !== 'number') fail('days[] needs trades and clean numbers');
}

console.log('check-state: OK');
