# Build queue

Small tasks for a coding model, run one at a time, in order. The full design is in [`docs/PLAN.md`](../docs/PLAN.md).

Rules for every task:

- Change only the files listed. No libraries, no build step, no network calls beyond same-origin `docs/data/`.
- Existing embed URLs must keep working the same way.
- Don't invent facts about Ndegwa. Use `me/` or leave the value `null` or "(Ndegwa's words)".
- Check at 400x300 and 900x500. Respect `prefers-reduced-motion`.
- Commit each task on its own: `T0x: <what>`.

## Foundation

**T01: Design tokens file**
Files: `design/tokens.json`.
Do: Write the colors, type, spacing, radius, and motion values from PLAN section 5 as JSON.
Accept: valid JSON. Every hex in PLAN 5.1 is present. Path ids match `paths` in `docs/data/graph.json`.

**T02: Token drift check**
Files: `scripts/check-tokens.mjs`.
Do: For each `docs/*.html`, parse the `:root{…}` block and compare every `--name` that exists in `tokens.json`.
Accept: `node scripts/check-tokens.mjs` exits 0 on the current repo. Changing one hex in a widget makes it exit 1 and name the file and token.

**T03: Screenshot script**
Files: `scripts/shots.mjs`, `package.json` (dev dependency `puppeteer-core` only), README "Local preview" section.
Do: Serve `docs/` locally and save PNGs of every widget at 400x300 and 900x500 into `previews/` (git-ignored). Fail on console errors.
Accept: one command produces 2 PNGs per widget. README no longer mentions `shot.py`.

**T04: `state.json` with real known values**
Files: `docs/data/state.json`.
Do: Write schema v1 exactly as in PLAN 3.3. Unknown values stay `null`.
Accept: valid JSON. Ladder matches `me/trading-system.md`. No balance or date is invented.

**T05: State validator**
Files: `scripts/check-state.mjs`.
Do: Check `schemaVersion === 1`, field types, that `session.state` is ready / standaside / done, that `losses <= maxLosses`, that `seq` holds booleans, and that dates are `YYYY-MM-DD`.
Accept: passes on T04's file. Each broken field gives a clear message and exit 1.

**T06: Shared state loader snippet**
Files: `design/state-loader.js`, which is a reference snippet to copy, not a script to load.
Do: Write a small function, `loadState(defaults) → Promise<{data, source}>`. It reads `?src=` (default `data/state.json`), uses `fetch` with `cache: 'no-store'`, and resolves to `source: 'example'` on any failure.
Accept: under 40 lines, no dependencies. Its README note says to copy it inline into each widget.

## Existing widgets read `state.json`

Precedence in every widget: URL param, then `state.json`, then labelled example.

**T07: Ring reads state**
Files: `docs/ring.html`.
Do: Inline the loader. Map `account.balance/start/goal/rungs`. When `balance` is `null`, show "no data yet" instead of `$0`. The footer shows the source ("Rungs from URL", "From state.json · updated <date>", or "Rungs: example default").
Accept: `ring.html?balance=42&goal=500&start=15&rungs=15,25,40,65,100,160,250,400,500` renders exactly as before. With no params it shows `state.json` values. With the file missing it shows the old example.

**T08: Ladder reads state**
Files: `docs/ladder.html`.
Do: Map `ladder[]` and `account.balance`.
Accept: the old example URL is unchanged. With no params it shows the 5 real rungs. `?balance=70` with state shows NOW at $35.

**T09: Header reads state**
Files: `docs/header.html`.
Do: Map `session.state`. The `?state=` param still wins. When `losses >= maxLosses`, show the existing `done` chip. Don't add new chips or text.
Accept: all 3 states plus the unknown-value fallback behave as before. The calm check is untouched.

## New visuals

**T10: Timeline widget**
Files: `docs/timeline.html`.
Do: Build PLAN 2.2 with tokens copied inline: the 13:00-16:00 Dubai block, LOG at 16:15, the London Reversal Box 14:15-15:15 Dubai (13:15-14:15 EAT), a Dubai/EAT dual axis, a now needle, and trades and losses counters out of 2.
Params: `state`, `trades`, `losses`, `now=HH:MM`.
Accept: `?now=14:30&trades=1&losses=0` puts the needle inside the box. `?losses=2` shows "Out for the session" in red. Fits 400x160 without overlap.

**T11: Heat strip widget**
Files: `docs/heat.html`.
Do: Build PLAN 2.3: trade cells up to the target, an "N / 10 clean" count, the current clean streak, and an optional 28-day row from `days`.
Params: `clean`, `target`, `seq` (for example `1101`).
Accept: `?seq=1101` shows 3/10 clean with a streak of 1. With no data it shows 10 dim cells and "no trades logged yet". Fits 400x160.

**T12: Graph embed mode and badge**
Files: `docs/graph.html`.
Do: `?embed=1` hides the legend and hint. Show a small "N/10 clean" badge near the Trading hub from `state.json`. If the file is missing, show no badge.
Accept: `?focus=trading` still centers Trading. No console errors when `state.json` is absent.

**T13: Index lists every visual**
Files: `docs/index.html`, `README.md` "Embed URLs".
Do: Add timeline and heat. List each widget's params and its suggested Notion embed height.
Accept: every link on the index opens at a relative path.

## Knowledge base and Notion package

**T14: `me/visuals.md` and `me/notion-map.md`**
Files: those two notes, plus a link line in `me/README.md`.
Do: Write PLAN section 6 content. Use only page names from `me/` and properties marked "(confirm)".
Accept: `node scripts/build-graph.mjs` passes with no broken links. Both notes appear in `graph.json`.

**T15: Notion build sheet**
Files: `plan/notion-template.md`.
Do: Write step-by-step block lists for START HERE, Today, and each hub page from PLAN section 4. Give exact embed URLs, tile image paths, and the toggles each page needs. Family and Dreams say "(Ndegwa's words)".
Accept: someone can build the pages in Notion from this sheet alone. It lists no personal facts outside `me/`.

**T16: Family and Dreams tiles**
Files: `docs/art/tile_family.jpg`, `docs/art/tile_dreams.jpg`, or an SVG equivalent.
Do: Wait until Ndegwa answers PLAN 8 question 4. Until then, make plain color tiles (orange `#ff8c42`, gray `#9aa3b5`) with the word only and no imagery.
Accept: same aspect ratio as the existing tiles. Nothing implies facts about his family or dreams.

## Publish

**T17: Publish `docs/`**
Do: Follow Ndegwa's hosting answer (PLAN 8 question 1). Turn on Pages from `main` `/docs`, or use Netlify Drop.
Accept: every widget opens over https and embeds in a Notion test page.

**T18: End-to-end check**
Do: Change `account.balance` in `state.json`, commit, and wait for the host to refresh.
Accept: ring, ladder, and graph badge show the new value. All 4 scripts (`build-graph`, `check-tokens`, `check-state`, `shots`) pass. Every item in PLAN section 7 is checked.
