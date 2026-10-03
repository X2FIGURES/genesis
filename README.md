# Life system

**GitHub Pages:** The site is served from the `docs/` folder (deploy from branch `main`, folder `/docs`). Base URL: **https://x2figures.github.io/genesis/** — open [index.html](https://x2figures.github.io/genesis/index.html) for the hub. Widgets and pages use paths relative to that base, for example `graph.html`, `ring.html`, `ladder.html`, `header.html`, `timeline.html`, and `heat.html`.

Static notes and pages for Ndegwa. `/me` is the source of truth a bot should read. `docs/` is a static site: the life graph plus the trading widgets. No build step to view them.

- `docs/graph.html` is the knowledge graph. It loads `docs/data/graph.json`. Open `docs/graph.html?focus=trading` (or `build`, `learning`, `money`, `family`, `dreams`, `bots`) to center that hub.
- `me/README.md` is the bot manual: read order, one question at a time, short replies, no signals or financial advice, trade decisions stay his.
- After editing notes, regenerate the graph from the repo root: `node scripts/build-graph.mjs`

## Notion widgets (static, dark mode)

Three single-file HTML widgets. Inline CSS + JS only: no libraries, no network calls, no tracking, no storage.
Each fits ~400px (phone) to ~900px (laptop) wide, respects `prefers-reduced-motion`, and follows the colour code:
red = no-trade/survival rules · green = setup/plan · blue = milestone/progress · purple = review/learning · yellow = ladder/numbers.
Background `#0f1115`, card `#161a22`.

All data comes from URL query params. Nothing is stored; change the URL to change the numbers.
Anything that appears without params is **example data** and is labelled as such on the widget.

## ring.html - account progress ring ($15 -> $500)
Blue animated ring with milestone ticks, big yellow `$balance`, "N% of $goal", and "$X to the next rung".

| Param | Default | Meaning |
|---|---|---|
| `balance` | `15` | current balance |
| `goal` | `500` | ring = 100% |
| `start` | `15` | starting balance (shown as "Started at ... +$X so far") |
| `rungs` | `15,25,40,65,100,160,250,400,500` (example default, labelled "Rungs: example default") | comma-separated balances; drawn as ticks, used for "next rung" |

Example: `ring.html?balance=42&goal=500&start=15&rungs=15,25,40,65,100,160,250,400,500`
Ticks are placed linearly (rung/goal), so early rungs sit close together near the top.

## ladder.html - lot ladder
Tiles per rung: **NOW** (yellow, pulsing glow), **NEXT** (blue), completed (green tick), locked (dim). Hover/tap/focus a tile to see its detail line.

| Param | Default | Meaning |
|---|---|---|
| `balance` | `15` | current balance; NOW = highest rung with balance >= rung |
| `rungs` | example: `15:0.01,25:0.01,40:0.02,65:0.03,100:0.05,160:0.08,250:0.12,400:0.20` (labelled "example data") | `balance:lot` pairs, comma-separated |

Example: `ladder.html?balance=70&rungs=15:0.01,40:0.02,65:0.03,100:0.05`
The default lot sizes are placeholders, not advice; put your real ladder in the URL.

## header.html - Session Card header strip
Title, status chip, three trigger tiles (15m = zone, 5m = entry zone, 1m = ONLY trigger; the 1m tile is emphasised), and a "30-second calm check" button.
Calm check: breathing circle expands 4s, contracts 6s, three cycles, countdown from 30, then shows "Held 1m origin? No = no trade." (red) with a Close button.
The calm check covers the strip while it runs, so no extra height is needed.

| Param | Values |
|---|---|
| `state` | `ready` (green, READY) · `standaside` (red, NEWS - STAND ASIDE) · `done` (purple, Done for the session). Default `ready`; unknown values fall back to `ready`. |

Example: `header.html?state=standaside`
Height: about 135px at 640px+ wide, about 165px on a phone-width embed. Set the Notion embed height to about 180px.

## Embed URLs

Serve `docs/` as a static site. There is no build step. These paths are relative to the repo root; append the query parameters already described above.

- `docs/index.html` links to the graph and the three widgets.
- `docs/graph.html?focus=trading` — `focus` hub id; `embed=1` hides chrome for small embeds.
- `docs/ring.html` — reads `data/state.json`; override with `balance`, `goal`, `start`, `rungs`. Example: `ring.html?balance=42&goal=500&start=15&rungs=15,25,40,65,100,160,250,400,500` (~300px).
- `docs/ladder.html` — reads state; override `balance`, `rungs` (`balance:lot`). Example URL still works (~300px).
- `docs/header.html?state=standaside` — `state` or session from state (~180px).
- `docs/timeline.html?now=14:30&trades=1&losses=0` — session bar Dubai time (~160px).
- `docs/heat.html?seq=1101` — clean-trade strip (~160px).

All data widgets accept `?src=data/state.json` (default). URL params override state. With no params and no state file, ring/ladder show labelled example data; timeline/header use defaults.

## Hosting
Nothing is deployed from here. Pick one:

**GitHub Pages**: put the three files in a repo's `docs/` folder, then Settings -> Pages -> Source: "Deploy from a branch", branch `main`, folder `/docs`. URLs look like `https://<user>.github.io/<repo>/ring.html`. GitHub Pages serves over https and allows iframing, so Notion can embed it. Use a public repo (or a plan that supports private Pages).
Anyone with the URL can open it, and the numbers you put in the query string are visible in it. Use only values you are happy to share, or leave the params off and edit them in the Notion embed URL.

**Netlify Drop**: drag the folder onto https://app.netlify.com/drop to get an https URL.

## Embedding in Notion
1. In Notion, type `/embed` (or paste the full URL with params on an empty line).
2. Paste the https URL, e.g. `https://<user>.github.io/<repo>/ring.html?balance=42`, and choose **Create embed**.
3. Drag the embed's edges to size it. Suggested heights: ring ~300px, ladder ~300px, header ~180px.
4. To update numbers, edit the embed's URL (the `...` menu -> Edit link / replace the block URL). The page is static and does not fetch live data.

Notion needs an https URL that does not send `X-Frame-Options: DENY` or a restrictive `frame-ancestors`; GitHub Pages and Netlify are fine. `file://` or `http://localhost` will not embed.

## Local preview / tests
From the repo root (needs `npm install` once):

```bash
npm run shots
```

Saves PNGs under `previews/` (git-ignored) at 400×300 and 900×500. Fails on console errors. Serve `docs/` over http for manual checks; `file://` will not load `data/state.json` on some browsers.

```bash
npm run check:tokens
npm run check:state
npm run build:graph
```
