---
id: visuals
title: Visuals
path: self
hub: false
summary: Embed URLs for every static visual in docs/.
---

Every visual is a file under `docs/`. Serve that folder over https. Append query params to override `docs/data/state.json`. Use `?src=` for another JSON file on the same host.

| Visual | File | Suggested height | Params |
|---|---|---|---|
| Life graph | `graph.html` | ~500px | `focus` (hub id), `embed=1` |
| Progress ring | `ring.html` | ~300px | `balance`, `goal`, `start`, `rungs` |
| Lot ladder | `ladder.html` | ~300px | `balance`, `rungs` as `balance:lot` |
| Session header | `header.html` | ~180px | `state` = ready / standaside / done |
| Session timeline | `timeline.html` | ~160px | `state`, `trades`, `losses`, `now=HH:MM` |
| Clean trades | `heat.html` | ~160px | `clean`, `target`, `seq` (e.g. `1101`) |

Shared data: `docs/data/state.json` (schema v1). Regenerate the graph from notes with `node scripts/build-graph.mjs`. Notion property names for the bot live in `docs/data/notion-config.json` as **(confirm)** until updated.

See [[Trading]], [[Daily rhythm]], and [[Glossary]] for what the numbers mean. Bots must not invent values; see [[How to work with me]].
