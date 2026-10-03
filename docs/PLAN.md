# Plan: Notion template system

Planning only. Nothing in this file is built yet unless it says "exists". Facts about Ndegwa come from `me/` (seeded from `me_seed.md`). Anything not there is marked **(Ndegwa's words)** or **(confirm)**.

Build tasks live in [`plan/BUILD_QUEUE.md`](../plan/BUILD_QUEUE.md).

## 1. What we're building

One Notion workspace (the template) and this repo (the code), connected by public https URLs.

- **Notion** holds the pages and databases he types into: START HERE, Session Card Origin Plan, Milestone Tracker $15 to $500, Trade Log, Session Notes, Weekly view, Money & Kareet, Learning, Daily log, Sessions.
- **This repo** holds the visuals (`docs/`), the data they read (`docs/data/`), and the knowledge base a bot reads (`me/`).
- **Notion embeds** the visuals by URL. The visuals never call Notion.

The visualizer is the center. Every Notion screen leads with one visual and a few lines of text, with detail behind closed toggles.

## 2. Visualizer

All visuals are single static HTML files in `docs/`. No build step, no libraries, no network calls except reading files in `docs/data/` from the same origin. Each one must look right at 400x300 and 900x500.

| Visual | File | Status | Notion embed height |
|---|---|---|---|
| Life graph | `graph.html` | exists, reads `data/graph.json` | ~500px |
| Progress ring $15 → $500 | `ring.html` | exists, URL params only | ~300px |
| Lot ladder | `ladder.html` | exists, URL params only | ~300px |
| Session Card header | `header.html` | exists, URL params only | ~180px |
| Trading-session timeline | `timeline.html` | new | ~160px (confirm after build) |
| Clean-trades heat strip | `heat.html` | new | ~160px (confirm after build) |

### 2.1 Existing widgets: what changes

Keep the existing look and every current URL working. The only planned change: when a widget gets no data params, it tries `data/state.json` before it falls back to labelled example data. See section 3.

Two gaps to close:

- The ladder's built-in example (`15:0.01,25:0.01,40:0.02,…`) is not his ladder. His ladder from `me/trading-system.md` is 0.01 ($15-35), 0.02 ($35-75), 0.04 ($75-155), 0.08 ($155-315), 0.16 ($315-635). In URL form: `ladder.html?rungs=15:0.01,35:0.02,75:0.04,155:0.08,315:0.16&balance=…`. Keep the example labelled "example data"; real values come from `state.json` or the URL.
- The README mentions `previews/` and `shot.py`, but neither is in the repo. Replace them with a Node screenshot script (queue task T03).

### 2.2 Trading-session timeline (`timeline.html`)

One horizontal bar for the trading day, in Dubai time with the chart clock (EAT, Dubai −1h) as a second axis. Data from `me/daily-rhythm.md` and `me/trading-system.md`:

- Session block 13:00-16:00 Dubai, with a LOG marker at 16:15.
- London Reversal Box 13:15-14:15 EAT (14:15-15:15 Dubai) as a sub-band.
- A "now" needle, using the browser clock converted to `Asia/Dubai` with `Intl`. No network.
- State chip shared with `header.html`: `ready` / `standaside` / `done`.
- Counters: trades taken out of 2 and losses out of 2. At two losses the bar turns red and reads "Out for the session".

Params: `state`, `trades`, `losses`, `now` (an HH:MM override for testing). The Asia Box (03:00-09:00 EAT) falls outside the session, so it's left off the bar. Add a toggle only if he asks.

### 2.3 Clean-trades heat strip (`heat.html`)

The success metric is 10 clean, by-the-book trades, not wins (`me/glossary.md`). The strip shows:

- One cell per trade, in order: clean (green), not clean (red), empty slot (dim), up to the target. Default target 10.
- One big number: "N / 10 clean".
- A streak line: current run of consecutive clean trades.
- An optional day row, one cell per day for the last 28 days, shaded by clean trades that day. It reads the `days` field.

Params: `clean`, `target`, `seq` (for example `seq=1101` for clean, clean, not clean, clean). Without params it reads `state.json`.

### 2.4 Life graph

Exists. Keep `?focus=<path>`. Planned additions: `?embed=1` to hide the legend and hint for very small embeds, and a `state.json` badge on the Trading hub (for example "4/10 clean"). Its data still comes only from `me/` through `scripts/build-graph.mjs`.

## 3. Data contract: Notion to visuals

### 3.1 Options compared

| Option | How it works | Works with GitHub Pages | Secrets | Verdict |
|---|---|---|---|---|
| A. Manual URL params | He edits the embed URL (`?balance=42`) in Notion | yes | none | Keep as the override, but too many URLs to update by hand |
| B. `docs/data/state.json` in the repo | Grok Bot or he edits one JSON file; every widget reads it | yes, same origin | none in the site; only whoever commits needs repo access | **Recommended** |
| C. Notion public share link | Widgets fetch a published Notion page | no: cross-origin reads are blocked and the HTML is not a stable data format | none | Reject |
| D. Notion API from the browser | Widgets call the Notion API | no | integration token would be public | Reject |

### 3.2 Recommendation: B, with A as override

1. Every data widget reads `data/state.json`, a relative path that works on any static host.
2. A URL param overrides the matching field. Existing embed URLs keep working.
3. If both are missing, show the existing example data with its "example" label.
4. Use `?src=` to point at another JSON file. Not `?state=`, because `header.html` already uses `state`.

Update paths, with no secret in the site:

- **Manual:** edit `docs/data/state.json` in the repo's web editor on a phone, then commit.
- **Grok Bot:** the bot reads the Notion databases with its own Notion access, writes `state.json`, and commits. The bot's credentials stay in the bot, never in `docs/`.
- **Check:** `node scripts/check-state.mjs` validates the file before commit.

Expect a short delay after a commit: GitHub Pages rebuilds, and it may serve cached files for a few minutes. Widgets show `updatedAt`, so stale data is visible.

Privacy: a public Pages site makes `state.json` public, the same as values already in URLs. Commit only numbers he is happy to share. Never commit account IDs, broker names, or notes.

Hosting: this repo does not live on GitHub today. GitHub Pages needs a public GitHub repo with `docs/` on `main` (README "Hosting"). Netlify Drop is the no-GitHub fallback. **(confirm which)**

### 3.3 `docs/data/state.json` (schema v1)

```json
{
  "schemaVersion": 1,
  "updatedAt": "2026-10-05T16:15:00+04:00",
  "updatedBy": "manual",
  "account": { "start": 15, "balance": null, "goal": 500, "rungs": [15, 35, 75, 155, 315, 500] },
  "ladder": [
    { "balance": 15, "lot": 0.01 }, { "balance": 35, "lot": 0.02 }, { "balance": 75, "lot": 0.04 },
    { "balance": 155, "lot": 0.08 }, { "balance": 315, "lot": 0.16 }
  ],
  "session": { "date": null, "state": "ready", "tradesTaken": 0, "losses": 0, "maxTrades": 2, "maxLosses": 2 },
  "cleanTrades": { "target": 10, "seq": [] },
  "days": []
}
```

Rules: `null` means unknown, so the widget says "no data yet" instead of inventing a number. `seq` is a list of booleans in trade order (`true` = clean). `days` items are `{ "date": "YYYY-MM-DD", "trades": n, "clean": n }`. Start 15, goal 500, ladder, 2 trades, and 2 losses come from `me/trading-system.md`. Balance and dates stay `null` until he provides them. Ring rungs here are the ladder bands plus the goal. The ring's built-in example rungs stay as they are.

### 3.4 Notion databases to `state.json`

The databases exist in his workspace. Their property names are not in this repo, so every property below is **proposed (confirm)**. The bot maps whatever names he actually uses.

| Notion database | Proposed properties | Feeds |
|---|---|---|
| Trade Log | Date, Result, Clean (checkbox: by the book), Lot | `cleanTrades.seq`, `days`, `session.tradesTaken`, `session.losses` |
| Sessions | Date, State (ready / standaside / done) | `session.date`, `session.state` |
| Milestone Tracker $15 to $500 | Date, Balance | `account.balance` |
| Session Notes | Date, Note | none; text stays in Notion |
| Daily log | Date, Note | none for v1 |

Writes go one way only: Notion to `state.json`. Visuals never write anything.

## 4. Template package (Notion side)

Ship as a written build sheet (`plan/notion-template.md`, task T15) plus image assets in `docs/art/`. The Notion pages are built by hand or by a bot with his Notion access. This repo cannot create them.

### 4.1 START HERE (master home)

Top to bottom, phone-first, each block a few lines:

1. Hero banner (`docs/art/hero_banner.jpg`), one line under it: the day's one question.
2. **Today** (section 4.2).
3. Life path tiles, one image tile per path, linking to its hub page:
   - Trading → `art/tile_trade.jpg` (exists)
   - Build → `art/tile_build.jpg` (exists)
   - Learning → `art/tile_learn.jpg` (exists)
   - Money → `art/tile_money.jpg` (exists)
   - Family → no art yet. Use a plain orange tile with no imagery. Content is (Ndegwa's words).
   - Dreams → no art yet. Use a plain gray tile with no imagery. Content is (Ndegwa's words).
4. Life graph embed (`graph.html`).
5. Closed toggles: "Rules for bots" (link to `me/README.md`), "How the visuals update" (section 3.2), "All pages".

### 4.2 Today view

One screen, following `me/daily-rhythm.md` (from Mon Oct 5):

1. Morning: make money. Link to Money & Kareet.
2. Trade 13:00-16:00 Dubai: header embed, timeline embed, ring + ladder in two columns (Notion stacks them on phone). Log at 16:15.
3. Build last. Link to the Build hub.
4. 19:00 phone micro-lesson. Link to Learning.
5. Sunday only, in a closed toggle: 18:00 weekly review, 18:30 Grok Bot outlook.

### 4.3 Hub pages

One per path, same shape: color callout title, one visual, at most 5 lines, then closed toggles. Trading's hub uses the heat strip and links to Session Card Origin Plan, Trade Log, Session Notes, and Sessions. Family and Dreams hubs contain only "(Ndegwa's words)" and an empty toggle.

### 4.4 ADHD-friendly rules for every page

- One question or filter per screen.
- At most about 5 lines of text before a visual or a toggle.
- Detail lives in closed toggles.
- Dark mode. Color means the same thing everywhere (section 5).
- Short, near-term timelines only. No far-off roadmaps on home screens.
- No lecture-first content. Learning pages start with the thing to build.

## 5. Design system tokens

Source of truth: `design/tokens.json` (task T01). Widgets stay single-file, so each one keeps an inline `:root` block, and `scripts/check-tokens.mjs` fails if the block drifts from the JSON.

### 5.1 Color

| Token | Hex | Use |
|---|---|---|
| `bg` | `#0f1115` | page background |
| `card` | `#161a22` | card / panel |
| `tile` | `#1b2029` | inner tiles |
| `line` | `#242a36` | borders, dividers |
| `text` | `#eef0f5` | primary text |
| `muted` | `#8d95a8` | labels, secondary |
| `red` | `#ff5c6c` | Trading path; no-trade / survival rules |
| `green` | `#3ddc84` | Build path; setup / plan / clean |
| `purple` | `#a78bfa` | Learning path; review / learning |
| `yellow` | `#ffd166` | Money path; ladder / numbers |
| `blue` | `#4c8dff` | Bots path; milestone / progress |
| `orange` | `#ff8c42` | Family path |
| `gray` | `#9aa3b5` | Dreams path |
| `self` | `#d5dbe8` | profile / self notes in the graph |

Red does two jobs: it is the Trading path color, and inside widgets it means no-trade rules. These existing meanings conflict on purpose. Keep both: path colors are for navigation (tiles, graph, hub titles), and widget colors are for state.

### 5.2 Type, spacing, shape

- Font: `system-ui, -apple-system, "Segoe UI", Roboto, sans-serif`. Numbers use `font-variant-numeric: tabular-nums`.
- Label: 11px, weight 700, uppercase, letter-spacing .14em, `muted`.
- Body: 13px. Small: 12px. Heading: `clamp(18px, 4.6vw, 24px)` weight 800. Big number: `clamp(28px, …, 56px)` weight 800, `yellow`.
- Spacing scale: 4, 6, 8, 10, 12, 14, 16, 24 px.
- Radius: card 16, tile 12, chip 999.
- Motion: ease-out `cubic-bezier(.22,.8,.25,1)`, 0.6-1.6s. Every widget honors `prefers-reduced-motion`.
- Embed sizes to test: 400x300 and 900x500, plus a 390px-wide phone screen.

## 6. Knowledge base (`me/`)

Exists: 12 notes, with read order and rules in `me/README.md`. Graph generated by `scripts/build-graph.mjs`, which fails on broken wikilinks.

Planned:

- `me/notion-map.md`: each Notion page and database to its note, its visual, and its `state.json` field.
- `me/visuals.md`: each embed URL and what its params mean, so a bot can build URLs instead of guessing.
- `updated: YYYY-MM-DD` in frontmatter, so a bot knows how fresh a note is.
- The rules do not change: one question at a time, short replies, no signals or financial advice, trade decisions stay his. Family and Dreams stay "(Ndegwa's words)" until he writes them.

## 7. Done means

- Every visual in section 2 opens from `docs/` on the public host, at both embed sizes, with real data from `state.json` and no console errors.
- Changing one number in `state.json` updates ring, ladder, header, timeline, and heat strip after the host refreshes.
- START HERE and Today are built in Notion from `plan/notion-template.md`, and every embed loads.
- `node scripts/build-graph.mjs`, `node scripts/check-tokens.mjs`, `node scripts/check-state.mjs`, and `node scripts/shots.mjs` all pass.

## 8. Open questions for Ndegwa (one at a time)

1. Which host: GitHub Pages (needs a public GitHub repo) or Netlify?
2. What are the real property names in Trade Log and Milestone Tracker?
3. Does Grok Bot get commit access, or does he edit `state.json` by hand at first?
4. Family and Dreams tiles: plain color, or art he picks?
