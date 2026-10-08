# Atelier Studio (local)

Local **Python + Blender** wedding attire studio.

Not a Vercel/Next app. You run it on your machine to lock **what the wedding party wears** on **mannequins**, across a **vast** culture catalog.

## Stack choice

| Option | Verdict |
|---|---|
| **Python + Blender** | **Chosen.** Blender’s API is Python. Garments + mannequins + renders live here. |
| Rust | No win for Blender pipelines. |
| Next.js / Vercel | Deprioritized. Client share links can come later. |

## Vast, not three cultures

`atelier/catalog/cultures.json` is an **open registry** (dozens of cultures: Maghreb, Gulf, Yoruba, Korean, Latin American, Sikh…).

Arab / Western / Asian are only the **first packs with looks filled**. More packs get added as Lauren/research seeds them — the studio does not cap at three.

## First seeded packs

- `western` — bridesmaid dress + groomsman suit looks  
- `arab` — takchita / jabador / Gulf ivory-gold  
- `asian` — South Asian pastel & jewel, Chinese red-gold, Korean hanbok  

## Setup

Needs Blender on PATH (4.0+).

```bash
cd apps/atelier-studio
python3 -m pip install -e .
```

## Commands

```bash
# How big is the catalog?
atelier summary

# What can we render today?
atelier packs

# Inspect one look
atelier show garden-sage

# Render mannequins (dress left, suit right) → PNG
atelier render garden-sage
atelier render moroccan-takchita-henna --out renders/henna.png

# Render a whole pack
atelier render-pack western
```

Renders land in `renders/`.

## Add a culture later

1. Add a row to `cultures.json` (`status: planned`).  
2. Create `catalog/packs/<id>/pack.json` with looks.  
3. Set culture `status: seeded` and `pack`.  
4. `atelier render <look-id>`.

No app rewrite required — the studio is the inventory + Blender pipeline.
