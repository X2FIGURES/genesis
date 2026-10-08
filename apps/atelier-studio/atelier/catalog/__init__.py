from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CATALOG_ROOT = Path(__file__).resolve().parent
PACKS_ROOT = CATALOG_ROOT / "packs"


def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_cultures() -> dict[str, Any]:
    return _load_json(CATALOG_ROOT / "cultures.json")


def list_packs() -> list[str]:
    if not PACKS_ROOT.exists():
        return []
    return sorted(
        p.name for p in PACKS_ROOT.iterdir() if (p / "pack.json").exists()
    )


def load_pack(pack_id: str) -> dict[str, Any]:
    path = PACKS_ROOT / pack_id / "pack.json"
    if not path.exists():
        raise FileNotFoundError(f"Unknown pack: {pack_id}")
    return _load_json(path)


def all_looks() -> list[dict[str, Any]]:
    looks: list[dict[str, Any]] = []
    for pack_id in list_packs():
        pack = load_pack(pack_id)
        for look in pack.get("looks", []):
            row = dict(look)
            row["pack"] = pack_id
            looks.append(row)
    return looks


def get_look(look_id: str) -> dict[str, Any]:
    for look in all_looks():
        if look["id"] == look_id:
            return look
    raise KeyError(f"Unknown look: {look_id}")


def catalog_summary() -> dict[str, Any]:
    cultures = load_cultures()["cultures"]
    by_status: dict[str, int] = {}
    for c in cultures:
        by_status[c["status"]] = by_status.get(c["status"], 0) + 1
    return {
        "cultures_total": len(cultures),
        "cultures_by_status": by_status,
        "packs": list_packs(),
        "looks": len(all_looks()),
    }
