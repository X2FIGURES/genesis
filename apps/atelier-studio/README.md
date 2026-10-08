# Atelier Studio — premium local attire lab

Python + **Blender** studio you run locally.  
Vast culture catalog · **10 dress** + **10 suit** styles · **Coolors-style** color matching · camera angles · dress turntable · glow for color depth.

`apps/wedding-theme` (Next/Vercel) is deprecated.

## Concept

You are judging **depth of each color on real garment shapes** — not a flat swatch and not a venue mock.

- Mannequin dress + suit  
- Shift **camera** (`front` · `three_quarter` · `side` · `low` · `detail`)  
- **Turn** the dress (`--turn` degrees) or run a full **turntable**  
- Soft **glow / rim light** so satin & velvet read richer  
- **Customize** every slot (dress / suit / tie / pocket / boutonniere) like Coolors: lock, set hex, regenerate unlocked harmonies  

## Setup

```bash
cd apps/atelier-studio
python3 -m pip install -e .
export PATH="$HOME/.local/bin:$PATH"
# Blender 4.x on PATH
```

## Dresses & suits (research-backed starter 10+10)

```bash
atelier garments
```

Dresses: A-line, ball gown, fit & flare, mermaid, drop-waist/basque, empire, sheath/column, bias slip, one-shoulder, midi A-line.  
Suits: two-piece, three-piece, tux peak, tux shawl, midnight tux, linen beach, double-breasted, morning suit, velvet dinner, earth-tone three-piece.

## Coolors-style color matching

```bash
# Harmony from a seed
atelier palette --seed "#D8A9A4" --harmony wedding
atelier palette garden-sage --harmony analogous --save customs/demo.palette.json

# Lock dress color, regenerate the rest, pick silhouettes, save custom look
atelier customize garden-sage \
  --set dress=#9DAE8F \
  --lock dress \
  --harmony wedding \
  --regenerate \
  --dress a-line \
  --suit three-piece \
  --as-id garden-sage-locked

# Harmonies: wedding | analogous | complementary | split | triadic | tetradic | mono | shades
```

## Premium render (glow · camera · turn)

```bash
atelier render garden-sage --camera three_quarter --turn 35 --glow 1.2 --res 1600
atelier render garden-sage-locked --focus dress --camera detail --turn 50 --glow 1.4

# See color depth around the dress (shift camera + turn the garment)
atelier turntable garden-sage --focus dress --glow 1.3
atelier turntable garden-sage --cameras three_quarter,side --turns 0,45,90,135 --glow 1.4
# → renders/turntable/garden-sage/<camera>_tXXX.png
```


## Catalog

```bash
atelier summary          # 30+ cultures (vast; Arab/Western/Asian first packs)
atelier packs
atelier show blush-champagne
atelier render-pack western
atelier render-all
```

## Layout

```
atelier/catalog/cultures.json    vast culture registry
atelier/catalog/garments.json    10 dresses + 10 suits
atelier/catalog/packs/*/         seeded looks
atelier/palette/coolors.py       Coolors-style engine
atelier/blender/build_look.py    premium mannequin renderer
customs/                         your locked palettes + custom looks
renders/                         PNG output
```

Improve from here: swap procedural meshes for commissioned `.blend` garments per silhouette id — CLI flags stay the same.
