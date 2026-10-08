# Atelier · Wedding party colors

Next.js app (Vercel) to lock **what bridesmaids and groomsmen wear** —
dress, suit, tie, pocket square, boutonniere. That is the theme.

Lives in the **genesis** monorepo under `apps/wedding-theme`.
GitHub Pages still serves only `/docs` — this app does not affect it.

## Local

```bash
cd apps/wedding-theme
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

Shareable URL params:

| Param | Example | Meaning |
|---|---|---|
| `theme` | `garden-sage` | Active theme id |
| `moment` | `party` \| `bridesmaids` \| `groomsmen` | Who to preview |
| `light` | `daylight` \| `golden` \| `candle` | Lighting |

## Deploy on Vercel

1. Import the **genesis** GitHub repo into Vercel.
2. Set **Root Directory** to `apps/wedding-theme`.
3. Framework preset: Next.js. Build: `npm run build`. Output: default.
4. Deploy. Pages (`docs/`) stays on GitHub Pages unchanged.

## Design

See `DESIGN.md` and the Notion brief **Design Brief · Theme Visualizer App (Vercel)**.

v1 ships illustrated SVG scenes (no stock couples). Theme seed data mirrors the Themes & Palettes Notion DB shape for a later sync.
