# Atelier Studio — run on **your** machine

**INTERNAL** desktop app for the team. Opens a native window on **your laptop/desktop** — not a cloud browser tab, not Vercel.

3D Blender mannequins → PNG preview (camera · turn · glow · Coolors palette).

---

## Install on your device (do this once)

### 1. Get the code
```bash
git clone https://github.com/X2FIGURES/genesis.git
cd genesis
git checkout cursor/wedding-theme-visualizer-ec7f
cd apps/atelier-studio
```

### 2. Install Blender 4.x on this same machine
- Mac: https://www.blender.org/download/ or `brew install --cask blender`
- Windows: installer from blender.org (default Program Files path is auto-found)
- Linux: `sudo apt install blender` or blender.org

Optional: `export ATELIER_BLENDER=/full/path/to/blender`

### 3. Setup + launch

**Mac / Linux**
```bash
chmod +x scripts/setup-local.sh scripts/run-atelier.sh Atelier.command
./scripts/setup-local.sh
./scripts/run-atelier.sh
```
Or double-click `Atelier.command` on Mac.

**Windows**
```powershell
.\scripts\setup-local.ps1
.\Atelier.bat
```
Or double-click `Atelier.bat`.

**Check this machine**
```bash
atelier doctor
```

---

## Daily use

```bash
atelier          # opens desktop app
atelier desktop  # same
atelier doctor   # Blender / Tk / deps check
```

In the window: pick a look → lock colors → set camera / turn / glow → **Render mannequins**.

Customs → `customs/` · Renders → `renders/desktop/`

---

## CLI (same engine)

```bash
atelier garments
atelier customize garden-sage --set dress=#9DAE8F --lock dress --regenerate --as-id my-look
atelier render my-look --camera three_quarter --turn 35 --glow 1.2
atelier turntable my-look --focus dress --turns 0,60,120
```

---

## Layout

```
Atelier.command / Atelier.bat   double-click launchers (your device)
scripts/setup-local.sh|.ps1     one-time install on your device
atelier/desktop/                CustomTkinter app
atelier/blender/build_look.py   3D EEVEE mannequin renderer
atelier/palette/                Coolors-style matching
atelier/catalog/                cultures · 10 dresses · 10 suits · packs
```

`apps/wedding-theme` (Next/Vercel) is deprecated.
