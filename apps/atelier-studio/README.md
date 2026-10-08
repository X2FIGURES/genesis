# Atelier Studio — internal desktop attire lab

**INTERNAL** Python + **Blender** desktop app for the team.  
Vast culture catalog · **10 dress** + **10 suit** styles · **Coolors-style** color matching · camera angles · dress turn · glow for color depth.

`apps/wedding-theme` (Next/Vercel) is deprecated. This is not a localhost web product — open the desktop window.

## Desktop app (primary)

```bash
cd apps/atelier-studio
python3 -m pip install -e .
# needs: Blender 4.x on PATH, python3-tk
export PATH="$HOME/.local/bin:$PATH"
atelier desktop
```

In the window:

1. Pick a **look** (Western / Arab / Asian packs)
2. Lock / edit hex slots (dress · suit · tie · pocket · boutonniere)
3. Regenerate / shuffle unlocked (Coolors)
4. Set **camera**, **turn**, **glow**, dress + suit silhouettes
5. **Render mannequins** → preview pane shows the PNG

Customs save under `customs/`. Renders under `renders/desktop/`.

## CLI (same engine)

```bash
atelier summary
atelier garments
atelier packs
atelier customize garden-sage --set dress=#9DAE8F --lock dress --regenerate --dress a-line --suit three-piece --as-id garden-sage-locked
atelier render garden-sage --camera three_quarter --turn 35 --glow 1.2
atelier turntable garden-sage --focus dress --turns 0,60,120 --glow 1.3
```

## Layout

```
atelier/desktop/app.py       INTERNAL CustomTkinter app
atelier/catalog/             cultures · garments · packs
atelier/palette/coolors.py   Coolors-style engine
atelier/blender/build_look.py  mannequin renderer
customs/                     locked palettes + custom looks
renders/desktop/             desktop PNG output
```

Improve from here: swap procedural meshes for commissioned `.blend` garments per silhouette id — desktop + CLI flags stay the same.
