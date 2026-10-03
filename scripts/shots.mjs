#!/usr/bin/env node
import { createServer } from 'node:http';
import { readFileSync, mkdirSync, existsSync } from 'node:fs';
import { join, extname, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import puppeteer from 'puppeteer-core';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const docs = join(root, 'docs');
const outDir = join(root, 'previews');
const port = 47241;

const allPages = [
  { file: 'graph.html', query: '' },
  { file: 'graph.html', query: '?focus=trading', suffix: '-focus' },
  { file: 'ring.html', query: '?balance=42&goal=500&start=15&rungs=15,25,40,65,100,160,250,400,500' },
  { file: 'ring.html', query: '', suffix: '-state' },
  { file: 'ladder.html', query: '?balance=70&rungs=15:0.01,40:0.02,65:0.03,100:0.05' },
  { file: 'ladder.html', query: '', suffix: '-state' },
  { file: 'header.html', query: '?state=standaside' },
  { file: 'timeline.html', query: '?now=14:30&trades=1&losses=0' },
  { file: 'heat.html', query: '?seq=1101' },
  { file: 'index.html', query: '' },
];
const pages = allPages.filter((p) => existsSync(join(docs, p.file)));

const mime = {
  '.html': 'text/html',
  '.json': 'application/json',
  '.jpg': 'image/jpeg',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
};

function serve(req, res) {
  const path = req.url.split('?')[0].replace(/^\//, '') || 'index.html';
  const file = join(docs, path);
  if (!file.startsWith(docs) || !existsSync(file)) {
    res.writeHead(404);
    res.end('not found');
    return;
  }
  const ext = extname(file);
  res.writeHead(200, { 'Content-Type': mime[ext] || 'application/octet-stream' });
  res.end(readFileSync(file));
}

mkdirSync(outDir, { recursive: true });

const server = createServer(serve);
await new Promise((r) => server.listen(port, '127.0.0.1', r));

const browser = await puppeteer.launch({
  executablePath: process.env.CHROME_PATH || '/usr/local/bin/google-chrome',
  headless: 'new',
  args: ['--no-sandbox', '--disable-gpu'],
});

const errors = [];
for (const size of [{ w: 400, h: 300 }, { w: 900, h: 500 }]) {
  const page = await browser.newPage();
  page.on('pageerror', (e) => errors.push(e.message));
  page.on('console', (msg) => {
    if (msg.type() === 'error' && !/404/i.test(msg.text())) errors.push(msg.text());
  });
  await page.setViewport({ width: size.w, height: size.h, deviceScaleFactor: 1 });
  for (const p of pages) {
    const base = p.file.replace('.html', '');
    const name = `${base}${p.suffix || ''}-${size.w}x${size.h}.png`;
    const url = `http://127.0.0.1:${port}/${p.file}${p.query}`;
    try {
      await page.goto(url, { waitUntil: 'networkidle0', timeout: 15000 });
      if (p.file === 'graph.html') {
        await page.waitForFunction(() => window.__lifeGraph && window.__lifeGraph.ready, { timeout: 8000 }).catch(() => {});
        await new Promise((r) => setTimeout(r, 400));
      }
      await page.screenshot({ path: join(outDir, name) });
      console.log('wrote', name);
    } catch (e) {
      errors.push(`${name}: ${e.message}`);
    }
  }
  await page.close();
}

await browser.close();
server.close();

if (errors.length) {
  console.error('shots failed:\n' + errors.join('\n'));
  process.exit(1);
}
console.log('shots: OK');
