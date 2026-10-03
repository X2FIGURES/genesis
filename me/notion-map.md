---
id: notion-map
title: Notion map
path: self
hub: false
summary: Notion pages and databases mapped to repo files and state.json fields.
---

Notion holds the typed data. This repo holds visuals and `docs/data/state.json`. One-way sync: Notion → state.json (Grok Bot or hand edit). Visuals never write back.

## Pages (names only in repo)

| Notion page | Repo / visual |
|---|---|
| START HERE | `plan/notion-template.md` build sheet |
| Session Card Origin Plan | [[Trading]] · `header.html`, `timeline.html` |
| Milestone Tracker $15 to $500 | `account.balance`, `account.rungs` in state.json |
| Trade Log | `cleanTrades.seq`, `session.tradesTaken`, `session.losses`, `days` |
| Session Notes | text stays in Notion |
| Weekly view | [[Daily rhythm]] |
| Money & Kareet | [[Money]] |
| Learning | [[Learning]] |
| Daily log | [[Daily rhythm]] |
| Sessions | `session.state`, `session.date` |

## state.json fields

- `account.start`, `account.balance`, `account.goal`, `account.rungs` → [[Trading]] ring and ladder
- `ladder[]` → real lot ladder (see [[Trading]] lot ladder)
- `session.*` → header and timeline
- `cleanTrades.*` → heat strip and graph badge on [[Trading]]

Database property names are in `docs/data/notion-config.json` as **(confirm)**. Update that file when Notion columns are known.
