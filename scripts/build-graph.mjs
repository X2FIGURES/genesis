#!/usr/bin/env node
// Read me/*.md (except README.md) and write docs/data/graph.json.
import { readFileSync, writeFileSync, readdirSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const meDir = join(root, 'me');
const outFile = join(root, 'docs', 'data', 'graph.json');

const PATHS = [
  { id: 'trading', label: 'Trading', color: '#ff5c6c' },
  { id: 'build', label: 'Build', color: '#3ddc84' },
  { id: 'learning', label: 'Learning', color: '#a78bfa' },
  { id: 'money', label: 'Money', color: '#ffd166' },
  { id: 'family', label: 'Family', color: '#ff8c42' },
  { id: 'dreams', label: 'Dreams', color: '#9aa3b5' },
  { id: 'bots', label: 'Bots', color: '#4c8dff' },
  { id: 'self', label: 'Self', color: '#d5dbe8' },
];
const PATH_IDS = new Set(PATHS.map((p) => p.id));

function slug(value) {
  return String(value)
    .normalize('NFKD')
    .toLowerCase()
    .replace(/&/g, ' and ')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

function parseFrontmatter(raw) {
  if (!raw.startsWith('---\n')) return { data: {}, body: raw };
  const end = raw.indexOf('\n---\n', 4);
  if (end === -1) throw new Error('Unclosed frontmatter');
  const data = {};
  for (const line of raw.slice(4, end).split('\n')) {
    if (!line.trim()) continue;
    const m = /^([A-Za-z0-9_-]+):\s*(.*)$/.exec(line);
    if (!m) throw new Error(`Bad frontmatter line: ${line}`);
    let value = m[2].trim();
    if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    }
    if (value === 'true') value = true;
    else if (value === 'false') value = false;
    data[m[1]] = value;
  }
  return { data, body: raw.slice(end + 5) };
}

function plain(markdown) {
  return markdown
    .replace(/<!--[\s\S]*?-->/g, '')
    .replace(/\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|([^\]]+))?\]\]/g, (_, target, alias) => (alias || target).trim())
    .replace(/^#{1,6}\s+/gm, '')
    .replace(/[*_`]/g, '')
    .replace(/[ \t]+\n/g, '\n')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

function wikilinks(markdown) {
  const found = [];
  const re = /\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]/g;
  let match;
  while ((match = re.exec(markdown))) found.push(match[1].trim());
  return found;
}

function splitBody(body) {
  const preamble = [];
  const sections = [];
  let current = null;
  for (const line of body.split('\n')) {
    const heading = /^##\s+(.+)$/.exec(line);
    if (heading) {
      if (current) sections.push(current);
      current = { title: heading[1].trim(), lines: [] };
    } else if (current) current.lines.push(line);
    else preamble.push(line);
  }
  if (current) sections.push(current);
  return { preamble: preamble.join('\n'), sections };
}

function sectionPath(lines, fallback) {
  const text = lines.join('\n');
  const comment = /<!--\s*path:\s*([a-z0-9_-]+)\s*-->/i.exec(text);
  return comment ? comment[1].toLowerCase() : fallback;
}

const files = readdirSync(meDir)
  .filter((name) => name.endsWith('.md') && name !== 'README.md')
  .sort();

const nodes = [];
const usedIds = new Set();
const byKey = new Map();

function claim(node, keys) {
  nodes.push(node);
  usedIds.add(node.id);
  for (const key of keys) {
    const folded = key.trim().toLowerCase();
    if (!folded || byKey.has(folded)) continue;
    byKey.set(folded, node.id);
  }
}

function uniqueId(base) {
  let id = base || 'note';
  let n = 2;
  while (usedIds.has(id)) {
    id = `${base}-${n}`;
    n += 1;
  }
  return id;
}

const parsed = files.map((name) => {
  const raw = readFileSync(join(meDir, name), 'utf8');
  const { data, body } = parseFrontmatter(raw);
  if (!data.title || !data.path) throw new Error(`${name} needs title and path`);
  if (!PATH_IDS.has(data.path)) throw new Error(`${name} has unknown path ${data.path}`);
  const id = uniqueId(data.id || slug(name.replace(/\.md$/, '')));
  const { preamble, sections } = splitBody(body);
  return { name, data, id, preamble, sections };
});

for (const file of parsed) {
  claim(
    {
      id: file.id,
      title: file.data.title,
      path: file.data.path,
      hub: file.data.hub === true,
      summary: file.data.summary || '',
      note: plain(file.preamble),
      source: `me/${file.name}`,
    },
    [file.id, file.data.title, slug(file.data.title)],
  );
}

const sectionOwners = [];
for (const file of parsed) {
  for (const section of file.sections) {
    const path = sectionPath(section.lines, file.data.path);
    if (!PATH_IDS.has(path)) throw new Error(`${file.name} section "${section.title}" has unknown path ${path}`);
    const id = uniqueId(slug(section.title));
    const node = {
      id,
      title: section.title,
      path,
      hub: false,
      summary: '',
      note: plain(section.lines.join('\n')),
      source: `me/${file.name}#${section.title}`,
    };
    claim(node, [id, section.title, slug(section.title)]);
    sectionOwners.push({ parent: file.id, id, raw: section.lines.join('\n') });
  }
}

function resolveLink(label, from) {
  const folded = label.trim().toLowerCase();
  if (byKey.has(folded)) return byKey.get(folded);
  const slugged = slug(label);
  if (byKey.has(slugged)) return byKey.get(slugged);
  throw new Error(`Unresolved wikilink [[${label}]] in ${from}`);
}

const edgeSet = new Set();
const edges = [];
function addEdge(source, target) {
  if (!source || !target || source === target) return;
  const key = source < target ? `${source}\0${target}` : `${target}\0${source}`;
  if (edgeSet.has(key)) return;
  edgeSet.add(key);
  edges.push({ source, target });
}

for (const file of parsed) {
  for (const label of wikilinks(file.preamble)) addEdge(file.id, resolveLink(label, file.name));
}
for (const section of sectionOwners) {
  addEdge(section.parent, section.id);
  for (const label of wikilinks(section.raw)) addEdge(section.id, resolveLink(label, section.id));
}

for (const node of nodes) {
  if (!node.note) throw new Error(`Node ${node.id} has an empty note`);
  const degree = edges.filter((edge) => edge.source === node.id || edge.target === node.id).length;
  if (degree === 0) throw new Error(`Node ${node.id} has no links`);
}

const family = nodes.find((node) => node.id === 'family');
const dreams = nodes.find((node) => node.id === 'dreams');
if (!family || !family.note.includes("(Ndegwa's words)")) throw new Error('Family must stay marked (Ndegwa\'s words)');
if (!dreams || !dreams.note.includes("(Ndegwa's words)")) throw new Error('Dreams must stay marked (Ndegwa\'s words)');

nodes.sort((a, b) => a.id.localeCompare(b.id));
edges.sort((a, b) => a.source.localeCompare(b.source) || a.target.localeCompare(b.target));

const graph = {
  generatedFrom: 'me/',
  paths: PATHS,
  nodes,
  edges,
};

mkdirSync(dirname(outFile), { recursive: true });
writeFileSync(outFile, `${JSON.stringify(graph, null, 2)}\n`);
console.log(`wrote ${nodes.length} nodes and ${edges.length} edges to ${outFile}`);
