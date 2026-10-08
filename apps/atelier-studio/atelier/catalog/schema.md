# Catalog schema (vast by design)

The studio is an **open inventory**, not a three-culture app.

```
cultures.json          → every culture/region we may ever cover (registry)
packs/<id>/pack.json   → one content pack (can hold many looks)
  looks[].json fields  → one wearable theme on mannequins
```

## Culture registry
Any culture can be `planned` | `seeded` | `ready`.  
Arab / Western / Asian packs are the **first to fill**, not the ceiling.

## Look (one row in a pack)
- `id`, `name`, `mood`
- `culture_ids[]` — links into the vast registry
- `garments[]` — mannequin slots: dress | suit | robe | tunic | cape | wrap | …
- `palette[]` — named hex mapped to a garment `slot`
- `accessories[]` — tie, pocket, boutonniere, cap, slippers, jewelry…
- `notes` — fabric / occasion cues

## Garment slot
Open string + known presets. New cultural garments = new slot names, not a schema rewrite.
