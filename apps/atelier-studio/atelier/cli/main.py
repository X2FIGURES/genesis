from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from atelier.catalog import (
    CUSTOMS_ROOT,
    all_looks,
    catalog_summary,
    get_look,
    list_packs,
    load_cultures,
    load_garments,
    load_pack,
)
from atelier.palette import GARMENT_SLOTS, Harmony, PaletteBoard

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RENDERS = ROOT / "renders"
BUILD_SCRIPT = ROOT / "atelier" / "blender" / "build_look.py"
CATALOG = ROOT / "atelier" / "catalog"


def find_blender(explicit: str | None) -> str:
    if explicit:
        return explicit
    found = shutil.which("blender")
    if not found:
        raise SystemExit(
            "Blender not found on PATH. Install Blender or pass --blender /path/to/blender"
        )
    return found


def cmd_summary(_: argparse.Namespace) -> int:
    s = catalog_summary()
    cultures = load_cultures()["cultures"]
    print("Atelier Studio — premium local attire catalog")
    print(f"  Cultures registered: {s['cultures_total']}")
    for status, n in sorted(s["cultures_by_status"].items()):
        print(f"    {status}: {n}")
    print(f"  Dress silhouettes: {s['dresses']} · Suit styles: {s['suits']}")
    print(f"  Packs seeded: {', '.join(s['packs']) or '(none)'}")
    print(f"  Looks ready: {s['looks']}")
    print()
    for c in cultures:
        pack = c.get("pack") or "—"
        print(f"  [{c['status']:7}] {c['id']:18} {c['name']}  (pack: {pack})")
    return 0


def cmd_garments(_: argparse.Namespace) -> int:
    g = load_garments()
    print("DRESSES (10 popular wedding / bridesmaid silhouettes)")
    for d in g["dresses"]:
        print(f"  {d['id']:14}  {d['name']:22}  {d['popularity']:20}  {d['why']}")
    print()
    print("SUITS (10 popular groom / groomsmen styles)")
    for s in g["suits"]:
        print(f"  {s['id']:18}  {s['name']:32}  {s['formality']:18}  {s['why']}")
    return 0


def cmd_packs(_: argparse.Namespace) -> int:
    for pack_id in list_packs():
        pack = load_pack(pack_id)
        print(f"{pack_id}: {pack['name']} — {len(pack.get('looks', []))} looks")
        for look in pack.get("looks", []):
            cultures = ", ".join(look.get("culture_ids", []))
            print(f"  - {look['id']:28} {look['name']}  [{cultures}]")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    print(json.dumps(get_look(args.look), indent=2))
    return 0


def board_from_look(look_id: str, harmony: str) -> PaletteBoard:
    look = get_look(look_id)
    return PaletteBoard.from_look_palette(look.get("palette", []), harmony=harmony)


def cmd_palette(args: argparse.Namespace) -> int:
    if args.seed:
        board = PaletteBoard.from_seed(args.seed, args.harmony)
    else:
        board = board_from_look(args.look, args.harmony)
        if args.harmony != "wedding":
            board.regenerate(harmony=args.harmony)
    board.print_board()
    if args.save:
        path = Path(args.save)
        board.save(path)
        print(f"Saved {path}")
    return 0


def cmd_customize(args: argparse.Namespace) -> int:
    """Coolors-style: lock slots, set hexes, regenerate unlocked, save custom look."""
    look = get_look(args.look)
    board = PaletteBoard.from_look_palette(look.get("palette", []), harmony=args.harmony)

    if args.seed:
        board.seed = args.seed
    for item in args.set or []:
        # format slot=#HEX
        if "=" not in item:
            raise SystemExit(f"--set expects slot=#HEX, got {item}")
        slot, hx = item.split("=", 1)
        board.set_slot(slot.strip(), hx.strip(), lock=True)
    for slot in args.lock or []:
        board.lock(slot, True)
    for slot in args.unlock or []:
        board.lock(slot, False)

    if args.regenerate or args.seed or args.harmony != "wedding":
        board.regenerate(harmony=args.harmony, seed=args.seed)
    if args.shuffle:
        board.shuffle_unlocked()

    board.print_board()

    custom = dict(look)
    custom_id = args.as_id or f"{look['id']}-custom"
    custom["id"] = custom_id
    custom["name"] = args.name or f"{look['name']} (custom)"
    custom["palette"] = board.as_palette_rows()
    custom["harmony"] = board.harmony
    custom["seed"] = board.seed
    if args.dress:
        # ensure dress garment silhouette
        garments = list(custom.get("garments", []))
        found = False
        for g in garments:
            if g.get("slot") == "dress":
                g["silhouette"] = args.dress
                found = True
        if not found:
            garments.append(
                {"slot": "dress", "label": "Dress", "silhouette": args.dress, "fabric": "satin"}
            )
        custom["garments"] = garments
        custom["dress_id"] = args.dress
    if args.suit:
        garments = list(custom.get("garments", []))
        found = False
        for g in garments:
            if g.get("slot") == "suit":
                g["silhouette"] = args.suit
                found = True
        if not found:
            garments.append(
                {"slot": "suit", "label": "Suit", "silhouette": args.suit, "fabric": "wool"}
            )
        custom["garments"] = garments
        custom["suit_id"] = args.suit

    CUSTOMS_ROOT.mkdir(parents=True, exist_ok=True)
    look_path = CUSTOMS_ROOT / f"{custom_id}.json"
    palette_path = CUSTOMS_ROOT / f"{custom_id}.palette.json"
    look_path.write_text(json.dumps(custom, indent=2) + "\n", encoding="utf-8")
    board.save(palette_path)
    print(f"Saved custom look {look_path}")
    print(f"Saved palette   {palette_path}")
    return 0


def run_blender_render(args: argparse.Namespace, look_id: str | None = None) -> int:
    look_id = look_id or args.look
    look = get_look(look_id)
    blender = find_blender(getattr(args, "blender", None))
    out = Path(args.out) if getattr(args, "out", None) else DEFAULT_RENDERS / f"{look['id']}.png"
    out.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        blender,
        "--background",
        "--python",
        str(BUILD_SCRIPT),
        "--",
        "--out",
        str(out),
        "--res",
        str(getattr(args, "res", 1600)),
        "--camera",
        getattr(args, "camera", "three_quarter"),
        "--turn",
        str(getattr(args, "turn", 20)),
        "--glow",
        str(getattr(args, "glow", 1.0)),
        "--focus",
        getattr(args, "focus", "party"),
        "--catalog",
        str(CATALOG),
    ]

    custom_look = CUSTOMS_ROOT / f"{look['id']}.json"
    custom_pal = CUSTOMS_ROOT / f"{look['id']}.palette.json"
    if custom_look.exists():
        cmd += ["--look-json", str(custom_look)]
    else:
        cmd += ["--look", look["id"]]
    if custom_pal.exists():
        cmd += ["--palette-json", str(custom_pal)]
    if getattr(args, "dress", None):
        cmd += ["--dress", args.dress]
    if getattr(args, "suit", None):
        cmd += ["--suit", args.suit]
    if getattr(args, "palette", None):
        cmd += ["--palette-json", args.palette]

    print("Running:", " ".join(cmd))
    proc = subprocess.run(cmd, check=False)
    if proc.returncode == 0:
        print(f"Wrote {out}")
    return proc.returncode


def cmd_render(args: argparse.Namespace) -> int:
    return run_blender_render(args)


def cmd_turntable(args: argparse.Namespace) -> int:
    """Render dress from several turn angles + cameras — see color depth."""
    look = get_look(args.look)
    out_dir = DEFAULT_RENDERS / "turntable" / look["id"]
    out_dir.mkdir(parents=True, exist_ok=True)
    if getattr(args, "turns", None):
        turns = [int(x.strip()) for x in args.turns.split(",") if x.strip()]
    else:
        turns = [0, 30, 60, 90, 120, 150, 180]
    cameras = args.cameras.split(",") if args.cameras else ["three_quarter", "front", "side"]
    rc = 0
    for cam in cameras:
        for turn in turns:
            ns = argparse.Namespace(
                look=args.look,
                out=str(out_dir / f"{cam}_t{turn:03d}.png"),
                blender=args.blender,
                res=args.res,
                camera=cam,
                turn=float(turn),
                glow=args.glow,
                focus=args.focus,
                dress=args.dress,
                suit=args.suit,
                palette=args.palette,
            )
            code = run_blender_render(ns)
            if code != 0:
                rc = code
    print(f"Turntable frames in {out_dir}")
    return rc


def cmd_render_pack(args: argparse.Namespace) -> int:
    pack = load_pack(args.pack)
    rc = 0
    for look in pack.get("looks", []):
        ns = argparse.Namespace(
            look=look["id"],
            out=str(DEFAULT_RENDERS / args.pack / f"{look['id']}.png"),
            blender=args.blender,
            res=args.res,
            camera=args.camera,
            turn=args.turn,
            glow=args.glow,
            focus="party",
            dress=None,
            suit=None,
            palette=None,
        )
        code = run_blender_render(ns)
        if code != 0:
            rc = code
    return rc


def cmd_render_all(args: argparse.Namespace) -> int:
    rc = 0
    for pack_id in list_packs():
        ns = argparse.Namespace(
            pack=pack_id,
            blender=args.blender,
            res=args.res,
            camera=args.camera,
            turn=args.turn,
            glow=args.glow,
        )
        code = cmd_render_pack(ns)
        if code != 0:
            rc = code
    for look in all_looks():
        src = DEFAULT_RENDERS / look["pack"] / f"{look['id']}.png"
        dst = DEFAULT_RENDERS / f"{look['id']}.png"
        if src.exists():
            shutil.copy2(src, dst)
    return rc


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="atelier",
        description="Premium local Blender wedding attire studio (Coolors palettes · vast cultures)",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("summary", help="Vast catalog overview")
    s.set_defaults(func=cmd_summary)

    s = sub.add_parser("garments", help="List 10 dresses + 10 suits")
    s.set_defaults(func=cmd_garments)

    s = sub.add_parser("packs", help="List seeded packs/looks")
    s.set_defaults(func=cmd_packs)

    s = sub.add_parser("show", help="Show look JSON")
    s.add_argument("look")
    s.set_defaults(func=cmd_show)

    s = sub.add_parser("palette", help="Coolors-style harmony from seed or look")
    s.add_argument("look", nargs="?", default=None)
    s.add_argument("--seed", default=None)
    s.add_argument(
        "--harmony",
        default="wedding",
        choices=[h.value for h in Harmony],
    )
    s.add_argument("--save", default=None)
    s.set_defaults(func=cmd_palette)

    s = sub.add_parser(
        "customize",
        help="Lock/set garment slots, regenerate unlocked (Coolors), save custom look",
    )
    s.add_argument("look")
    s.add_argument("--harmony", default="wedding", choices=[h.value for h in Harmony])
    s.add_argument("--seed", default=None)
    s.add_argument("--set", action="append", help="slot=#HEX (repeatable)", default=[])
    s.add_argument("--lock", action="append", choices=list(GARMENT_SLOTS), default=[])
    s.add_argument("--unlock", action="append", choices=list(GARMENT_SLOTS), default=[])
    s.add_argument("--regenerate", action="store_true")
    s.add_argument("--shuffle", action="store_true", help="Jitter seed + regen unlocked")
    s.add_argument("--dress", default=None, help="Dress silhouette id from garments.json")
    s.add_argument("--suit", default=None, help="Suit style id from garments.json")
    s.add_argument("--as-id", default=None)
    s.add_argument("--name", default=None)
    s.set_defaults(func=cmd_customize)

    def add_render_flags(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("--out", default=None)
        sp.add_argument("--blender", default=None)
        sp.add_argument("--res", type=int, default=1600)
        sp.add_argument(
            "--camera",
            default="three_quarter",
            choices=["front", "three_quarter", "side", "low", "detail"],
        )
        sp.add_argument("--turn", type=float, default=25.0, help="Dress rotation degrees")
        sp.add_argument("--glow", type=float, default=1.15)
        sp.add_argument("--focus", default="party", choices=["party", "dress", "suit"])
        sp.add_argument("--dress", default=None)
        sp.add_argument("--suit", default=None)
        sp.add_argument("--palette", default=None, help="Path to palette JSON")

    s = sub.add_parser("render", help="Premium mannequin render")
    s.add_argument("look")
    add_render_flags(s)
    s.set_defaults(func=cmd_render)

    s = sub.add_parser("turntable", help="Multi-angle + turn frames to judge color depth")
    s.add_argument("look")
    s.add_argument("--blender", default=None)
    s.add_argument("--res", type=int, default=1200)
    s.add_argument("--glow", type=float, default=1.2)
    s.add_argument("--focus", default="dress", choices=["party", "dress", "suit"])
    s.add_argument("--cameras", default="three_quarter,front,side")
    s.add_argument(
        "--turns",
        default="0,30,60,90,120,150,180",
        help="Comma-separated Y-rotation degrees",
    )
    s.add_argument("--dress", default=None)
    s.add_argument("--suit", default=None)
    s.add_argument("--palette", default=None)
    s.set_defaults(func=cmd_turntable)

    s = sub.add_parser("render-pack", help="Render a pack")
    s.add_argument("pack")
    s.add_argument("--blender", default=None)
    s.add_argument("--res", type=int, default=1400)
    s.add_argument("--camera", default="three_quarter")
    s.add_argument("--turn", type=float, default=25)
    s.add_argument("--glow", type=float, default=1.15)
    s.set_defaults(func=cmd_render_pack)

    s = sub.add_parser("render-all", help="Render every seeded look")
    s.add_argument("--blender", default=None)
    s.add_argument("--res", type=int, default=1400)
    s.add_argument("--camera", default="three_quarter")
    s.add_argument("--turn", type=float, default=25)
    s.add_argument("--glow", type=float, default=1.15)
    s.set_defaults(func=cmd_render_all)

    return p


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.cmd == "palette" and not args.look and not args.seed:
        parser.error("palette needs a look or --seed")
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
