#!/usr/bin/env node
import { readFileSync, readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const tokens = JSON.parse(readFileSync(join(root, 'design/tokens.json'), 'utf8'));
const canonical = tokens.cssVars;

function parseRootVars(css) {
  const m = /:root\s*\{([^}]+)\}/i.exec(css);
  if (!m) return null;
  const vars = {};
  for (const part of m[1].split(';')) {
    const line = part.trim();
    if (!line.startsWith('--')) continue;
    const idx = line.indexOf(':');
    if (idx === -1) continue;
    const name = line.slice(2, idx).trim();
    let val = line.slice(idx + 1).trim();
    if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
      val = val.slice(1, -1);
    }
    vars[name] = val.toLowerCase();
  }
  return vars;
}

const htmlDir = join(root, 'docs');
const files = readdirSync(htmlDir).filter((f) => f.endsWith('.html'));
let failed = false;

for (const file of files) {
  const raw = readFileSync(join(htmlDir, file), 'utf8');
  const style = raw.match(/<style[^>]*>([\s\S]*?)<\/style>/i)?.[1] ?? '';
  const vars = parseRootVars(style);
  if (!vars) continue;
  for (const [key, expected] of Object.entries(canonical)) {
    if (!(key in vars)) continue;
    const got = vars[key];
    const want = expected.toLowerCase();
    if (got !== want) {
      console.error(`${file}: --${key} is ${vars[key]}, expected ${expected}`);
      failed = true;
    }
  }
}

if (failed) process.exit(1);
console.log(`check-tokens: ${files.length} html files OK`);
