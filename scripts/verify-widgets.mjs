#!/usr/bin/env node
import puppeteer from 'puppeteer-core';
import { createServer } from 'node:http';
import { readFileSync, existsSync } from 'node:fs';
import { join, extname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(fileURLToPath(new URL('.', import.meta.url)), '..', 'docs');
const port = 47243;
const mime = { '.html': 'text/html', '.json': 'application/json', '.jpg': 'image/jpeg' };
const server = createServer((req, res) => {
  const path = req.url.split('?')[0].replace(/^\//, '') || 'index.html';
  const file = join(root, path);
  if (!file.startsWith(root) || !existsSync(file)) {
    res.writeHead(404);
    return res.end();
  }
  res.writeHead(200, { 'Content-Type': mime[extname(file)] || 'text/plain' });
  res.end(readFileSync(file));
});
await new Promise((r) => server.listen(port, '127.0.0.1', r));
const browser = await puppeteer.launch({
  executablePath: process.env.CHROME_PATH || '/usr/local/bin/google-chrome',
  headless: 'new',
  args: ['--no-sandbox'],
});
const page = await browser.newPage();
page.on('pageerror', (e) => {
  throw new Error(`pageerror: ${e.message}`);
});

async function check(url, fn, w, h) {
  await page.setViewport({ width: w, height: h });
  await page.emulateMediaFeatures([{ name: 'prefers-reduced-motion', value: 'reduce' }]);
  await page.goto(`http://127.0.0.1:${port}/${url}`, { waitUntil: 'networkidle0' });
  await fn();
}

await check(
  'ring.html?balance=42&goal=500&start=15&rungs=15,25,40,65,100,160,250,400,500',
  async () => {
    const t = await page.$eval('#bal', (el) => el.textContent);
    if (t !== '$42') throw new Error(`ring param: ${t}`);
  },
  900,
  500,
);

await check(
  'ring.html',
  async () => {
    const t = await page.$eval('#bal', (el) => el.textContent);
    if (t !== '$42') throw new Error(`ring state balance: ${t}`);
  },
  900,
  500,
);

await check(
  'ladder.html',
  async () => {
    const n = await page.$$eval('.rung', (els) => els.length);
    if (n !== 5) throw new Error(`ladder rungs: ${n}`);
  },
  400,
  300,
);

await check(
  'ladder.html?balance=70',
  async () => {
    const now = await page.$eval('.now .bal', (el) => el.textContent);
    if (now !== '$35') throw new Error(`ladder now: ${now}`);
  },
  900,
  500,
);

await check(
  'timeline.html?now=14:30&trades=1&losses=0',
  async () => {
    const hidden = await page.$eval('#now', (el) => el.hidden);
    if (hidden) throw new Error('timeline needle hidden');
  },
  400,
  300,
);

await check(
  'timeline.html?losses=2',
  async () => {
    const out = await page.$eval('#foot', (el) => el.textContent);
    if (!out.includes('Out')) throw new Error(`timeline: ${out}`);
  },
  400,
  300,
);

await check(
  'heat.html?seq=1101',
  async () => {
    const c = await page.$eval('#count', (el) => el.textContent);
    if (c !== '3 / 10 clean') throw new Error(`heat: ${c}`);
  },
  400,
  300,
);

await check(
  'graph.html?focus=trading',
  async () => {
    await page.waitForFunction(() => window.__lifeGraph?.ready);
  },
  900,
  500,
);

await browser.close();
server.close();
console.log('verify-widgets: OK');
