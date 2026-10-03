# Notion template build sheet

Build by hand in Notion (or with Grok Bot + Notion access). Embed base URL = your static host + `/docs/` path. Example: `https://<host>/ring.html`. Use `?src=` only if you host state elsewhere on the same origin.

Dark mode workspace. Color callouts match life paths (Trading red, Build green, Learning purple, Money yellow, Family orange, Dreams gray, Bots blue).

## START HERE

1. Full-width image: upload `docs/art/hero_banner.jpg`.
2. One line callout (gray): today's **one question** (edit daily).
3. Toggle **Today** → link to Today page (below).
4. Two-column gallery (stacks on phone), image tiles linking to hub pages:
   - Trading → `art/tile_trade.jpg` → Trading hub
   - Build → `art/tile_build.jpg` → Build hub
   - Learning → `art/tile_learn.jpg` → Learning hub
   - Money → `art/tile_money.jpg` → Money hub
   - Family → `art/tile_family.jpg` → Family hub (plain tile, no personal facts)
   - Dreams → `art/tile_dreams.jpg` → Dreams hub (plain tile)
5. Embed `/graph.html` (~500px tall).
6. Closed toggle **Rules for bots** → link to repo `me/README.md` (for humans: paste summary: one question, short replies, no signals).
7. Closed toggle **How visuals update** → edit `docs/data/state.json` on GitHub or let Grok Bot commit it; widgets read that file.
8. Closed toggle **All pages** → links to every hub + databases list.

## Today page

1. Callout **Morning** → link Money & Kareet hub (3 lines max from `me/daily-rhythm.md`).
2. Callout **Trade 13:00–16:00 Dubai** (red):
   - Embed `header.html` (~180px)
   - Embed `timeline.html` (~160px)
   - Two embeds side by side on desktop: `ring.html` + `ladder.html` (~300px each)
   - Line: Log at **16:15** → link Trade Log database
3. Callout **Build last** (green) → link Build hub.
4. Callout **19:00 micro-lesson** (purple) → link Learning hub.
5. Closed toggle **Sunday only**: 18:00 weekly review · 18:30 Grok Bot outlook (`me/daily-rhythm.md`).

## Trading hub

- Red callout title **Trading**
- Embed `heat.html` (~160px)
- Max 5 lines from `me/trading-system.md` (origin, 1m trigger, 2 trades, 2 losses)
- Links: Session Card Origin Plan, Trade Log, Session Notes, Sessions
- Closed toggles: full rules, glossary terms ([[Origin]], [[Hard close]], [[Clean trade]])

## Build hub

- Green callout **Build**
- 3 lines + links: Tap game, ESP32, The Stack (`me/build.md`)
- Closed toggle: 47-week stack note

## Learning hub

- Purple callout **Learning**
- 3 lines build-first / micro-lesson (`me/learning-approach.md`)
- Link Learning database

## Money hub

- Yellow callout **Money**
- Morning cash bullets (`me/money-and-kareet.md`)
- Link Money & Kareet database
- Closed toggle: Kareet long-term bet

## Family hub

- Orange callout **Family**
- Text only: **(Ndegwa's words)**
- Empty closed toggle for his notes

## Dreams hub

- Gray callout **Dreams**
- Text only: **(Ndegwa's words)**
- Empty closed toggle

## Bots (optional page)

- Blue callout; 4 lines from `me/bot-family.md`
- Closed toggle: model spend rule
