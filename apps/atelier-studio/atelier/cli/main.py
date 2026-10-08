from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from atelier.catalog import (
    all_looks,
    catalog_summary,
    get_look,
    list_packs,
    load_cultures,
    load_pack,
)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RENDERS = ROOT / "renders"
BUILD_SCRIPT = ROOT / "atelier" / "blender" / "build_look.py"
CATALOG = ROOT / "atelier" / "catalog"


def cmd_summary(_: argparse.Namespace) -> int:
    s = catalog_summary()
    cultures = load_cultures()["cultures"]
    print("Atelier Studio — vast catalog")
    print(f"  Cultures registered: {s['cultures_total']}")
    for status, n in sorted(s["cultures_by_status"].items()):
        print(f"    {status}: {n}")
    print(f"  Packs seeded: {', '.join(s['packs']) or '(none)'}")
    print(f"  Looks ready to render: {s['looks']}")
    print()
    print("Cultures (registry):")
    for c in cultures:
        pack = c.get("pack") or "—"
        print(f"  [{c['status']:7}] {c['id']:18} {c['name']}  (pack: {pack})")
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
    look = get_look(args.look)
    print(json.dumps(look, indent=2))
    return 0


def find_blender(explicit: str | None) -> str:
    if explicit:
        return explicit
    found = shutil.which("blender")
    if not found:
        raise SystemExit(
            "Blender not found on PATH. Install Blender or pass --blender /path/to/blender"
        )
    return found


def cmd_render(args: argparse.Namespace) -> int:
    look = get_look(args.look)
    blender = find_blender(args.blender)
    out = Path(args.out) if args.out else DEFAULT_RENDERS / f"{look['id']}.png"
    out.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        blender,
        "--background",
        "--python",
        str(BUILD_SCRIPT),
        "--",
        "--look",
        look["id"],
        "--catalog",
        str(CATALOG),
        "--out",
        str(out),
        "--res",
        str(args.res),
    ]
    print("Running:", " ".join(cmd))
    proc = subprocess.run(cmd, check=False)
    if proc.returncode != 0:
        return proc.returncode
    print(f"Wrote {out}")
    return 0


def cmd_render_pack(args: argparse.Namespace) -> int:
    pack = load_pack(args.pack)
    rc = 0
    for look in pack.get("looks", []):
        ns = argparse.Namespace(
            look=look["id"],
            out=str(DEFAULT_RENDERS / args.pack / f"{look['id']}.png"),
            blender=args.blender,
            res=args.res,
        )
        code = cmd_render(ns)
        if code != 0:
            rc = code
    return rc


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="atelier",
        description="Local Blender wedding attire studio (vast culture catalog)",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("summary", help="Show vast catalog size + culture registry")
    s.set_defaults(func=cmd_summary)

    s = sub.add_parser("packs", help="List seeded packs and looks")
    s.set_defaults(func=cmd_packs)

    s = sub.add_parser("show", help="Show one look as JSON")
    s.add_argument("look")
    s.set_defaults(func=cmd_show)

    s = sub.add_parser("render", help="Render one look with Blender mannequins")
    s.add_argument("look")
    s.add_argument("--out", default=None)
    s.add_argument("--blender", default=None)
    s.add_argument("--res", type=int, default=1280)
    s.set_defaults(func=cmd_render)

    s = sub.add_parser("render-pack", help="Render every look in a pack")
    s.add_argument("pack", choices=["western", "arab", "asian"])
    s.add_argument("--blender", default=None)
    s.add_argument("--res", type=int, default=1024)
    s.set_defaults(func=cmd_render_pack)

    return p


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
