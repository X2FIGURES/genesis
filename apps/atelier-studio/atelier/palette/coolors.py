"""
Coolors-style palette engine.

- Generate harmonies from a seed hex
- Lock any garment slot and regenerate the rest
- Assign swatches to dress / suit / tie / pocket / boutonniere
"""

from __future__ import annotations

import colorsys
import json
import random
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Iterable

GARMENT_SLOTS = ("dress", "suit", "tie", "pocket", "boutonniere")


class Harmony(str, Enum):
    analogous = "analogous"
    complementary = "complementary"
    split = "split"
    triadic = "triadic"
    tetradic = "tetradic"
    mono = "mono"
    shades = "shades"
    wedding = "wedding"  # soft dress + deeper suit + accent accessories


_HEX_RE = re.compile(r"^#?[0-9a-fA-F]{6}$")


def parse_hex(value: str) -> str:
    v = value.strip()
    if not v.startswith("#"):
        v = "#" + v
    if not _HEX_RE.match(v):
        raise ValueError(f"Invalid hex color: {value}")
    return v.upper()


def hex_to_hsl(hex_color: str) -> tuple[float, float, float]:
    h = parse_hex(hex_color).lstrip("#")
    r, g, b = int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255
    hh, ll, ss = colorsys.rgb_to_hls(r, g, b)
    return hh * 360.0, ss, ll


def hsl_to_hex(h: float, s: float, l: float) -> str:
    h = (h % 360.0) / 360.0
    s = min(1.0, max(0.0, s))
    l = min(1.0, max(0.0, l))
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return "#{:02X}{:02X}{:02X}".format(round(r * 255), round(g * 255), round(b * 255))


def _nudge(h: float, s: float, l: float, dh=0.0, ds=0.0, dl=0.0) -> str:
    return hsl_to_hex(h + dh, s + ds, l + dl)


def generate_harmony(
    seed: str,
    mode: Harmony | str = Harmony.wedding,
    count: int = 5,
) -> list[str]:
    """Return `count` hex colors from a seed, Coolors-style."""
    mode = Harmony(mode)
    h, s, l = hex_to_hsl(seed)
    s = max(0.18, min(0.72, s))
    colors: list[str] = [parse_hex(seed)]

    if mode == Harmony.analogous:
        steps = [-40, -20, 20, 40]
        colors += [_nudge(h, s, l, dh=d, dl=(-0.04 if abs(d) > 25 else 0.02)) for d in steps]
    elif mode == Harmony.complementary:
        colors += [
            _nudge(h, s * 0.9, min(0.92, l + 0.18)),
            _nudge(h + 180, s, l),
            _nudge(h + 180, s * 0.85, min(0.88, l + 0.12)),
            _nudge(h + 180, s * 0.7, max(0.15, l - 0.15)),
        ]
    elif mode == Harmony.split:
        colors += [
            _nudge(h, s, min(0.9, l + 0.12)),
            _nudge(h + 150, s, l),
            _nudge(h + 210, s, l),
            _nudge(h + 180, s * 0.5, min(0.88, l + 0.2)),
        ]
    elif mode == Harmony.triadic:
        colors += [
            _nudge(h + 120, s, l),
            _nudge(h + 240, s, l),
            _nudge(h, s * 0.5, min(0.92, l + 0.2)),
            _nudge(h + 120, s * 0.6, max(0.2, l - 0.1)),
        ]
    elif mode == Harmony.tetradic:
        colors += [
            _nudge(h + 90, s, l),
            _nudge(h + 180, s, l),
            _nudge(h + 270, s, l),
            _nudge(h, s * 0.45, min(0.9, l + 0.15)),
        ]
    elif mode == Harmony.mono:
        colors += [
            _nudge(h, s * 0.7, min(0.95, l + 0.22)),
            _nudge(h, s, min(0.88, l + 0.1)),
            _nudge(h, s * 1.05, max(0.18, l - 0.12)),
            _nudge(h, s * 0.85, max(0.12, l - 0.25)),
        ]
    elif mode == Harmony.shades:
        colors += [
            _nudge(h, s * 0.4, min(0.96, l + 0.28)),
            _nudge(h, s * 0.7, min(0.9, l + 0.12)),
            _nudge(h, s, max(0.2, l - 0.1)),
            _nudge(h, s, max(0.1, l - 0.28)),
        ]
    else:  # wedding — dress soft, suit deeper, accents warm/cool
        colors = [
            _nudge(h, max(0.2, s * 0.75), min(0.78, l + 0.08)),  # dress
            _nudge(h + 12, max(0.15, s * 0.45), max(0.18, l - 0.28)),  # suit
            _nudge(h + 35, min(0.65, s + 0.05), min(0.72, l + 0.02)),  # tie
            _nudge(h, max(0.08, s * 0.25), min(0.94, l + 0.25)),  # pocket
            _nudge(h - 25, s * 0.85, max(0.25, l - 0.05)),  # boutonniere
        ]

    # Dedupe / pad
    out: list[str] = []
    for c in colors:
        if c not in out:
            out.append(c)
    while len(out) < count:
        out.append(_nudge(h, s, l, dh=15 * len(out), dl=-0.05 * (len(out) % 3)))
    return out[:count]


SLOT_LABELS = {
    "dress": "Bridesmaid / party dress",
    "suit": "Suit / jacket",
    "tie": "Tie / bow",
    "pocket": "Pocket square",
    "boutonniere": "Boutonniere",
}


@dataclass
class Swatch:
    slot: str
    hex: str
    locked: bool = False
    name: str = ""

    def to_dict(self) -> dict:
        return {
            "slot": self.slot,
            "hex": self.hex,
            "locked": self.locked,
            "name": self.name or SLOT_LABELS.get(self.slot, self.slot),
        }


@dataclass
class PaletteBoard:
    """Coolors-like board mapped onto garment slots."""

    swatches: list[Swatch] = field(default_factory=list)
    harmony: str = Harmony.wedding.value
    seed: str = "#9DAE8F"

    @classmethod
    def from_look_palette(cls, palette: Iterable[dict], harmony: str = "wedding") -> "PaletteBoard":
        by_slot = {p["slot"]: p for p in palette}
        swatches: list[Swatch] = []
        seed = "#9DAE8F"
        for slot in GARMENT_SLOTS:
            if slot in by_slot:
                hx = parse_hex(by_slot[slot]["hex"])
                if slot == "dress":
                    seed = hx
                swatches.append(
                    Swatch(slot=slot, hex=hx, name=by_slot[slot].get("name", ""))
                )
            else:
                swatches.append(Swatch(slot=slot, hex=seed))
        return cls(swatches=swatches, harmony=harmony, seed=seed)

    @classmethod
    def from_seed(cls, seed: str, harmony: str = "wedding") -> "PaletteBoard":
        colors = generate_harmony(seed, harmony, count=5)
        swatches = [
            Swatch(slot=slot, hex=colors[i], name=SLOT_LABELS[slot])
            for i, slot in enumerate(GARMENT_SLOTS)
        ]
        return cls(swatches=swatches, harmony=harmony, seed=parse_hex(seed))

    def lock(self, slot: str, locked: bool = True) -> None:
        for s in self.swatches:
            if s.slot == slot:
                s.locked = locked
                return
        raise KeyError(slot)

    def set_slot(self, slot: str, hex_color: str, lock: bool = True) -> None:
        hx = parse_hex(hex_color)
        for s in self.swatches:
            if s.slot == slot:
                s.hex = hx
                s.locked = lock
                if slot == "dress":
                    self.seed = hx
                return
        raise KeyError(f"Unknown slot: {slot}. Use one of {GARMENT_SLOTS}")

    def regenerate(self, harmony: str | None = None, seed: str | None = None) -> None:
        if harmony:
            self.harmony = Harmony(harmony).value
        if seed:
            self.seed = parse_hex(seed)
        # Prefer locked dress as seed if present
        for s in self.swatches:
            if s.slot == "dress" and s.locked:
                self.seed = s.hex
                break
        generated = generate_harmony(self.seed, self.harmony, count=5)
        for i, s in enumerate(self.swatches):
            if not s.locked:
                s.hex = generated[i]

    def shuffle_unlocked(self) -> None:
        """Coolors spacebar vibe — slight hue jitter then regenerate unlocked."""
        h, s, l = hex_to_hsl(self.seed)
        self.seed = hsl_to_hex(h + random.uniform(-18, 18), s, l)
        self.regenerate()

    def as_palette_rows(self) -> list[dict]:
        return [
            {"name": s.name or SLOT_LABELS.get(s.slot, s.slot), "hex": s.hex, "slot": s.slot}
            for s in self.swatches
        ]

    def to_dict(self) -> dict:
        return {
            "seed": self.seed,
            "harmony": self.harmony,
            "swatches": [s.to_dict() for s in self.swatches],
            "palette": self.as_palette_rows(),
        }

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "PaletteBoard":
        data = json.loads(path.read_text(encoding="utf-8"))
        board = cls(
            seed=data.get("seed", "#9DAE8F"),
            harmony=data.get("harmony", "wedding"),
            swatches=[],
        )
        for row in data.get("swatches", []):
            board.swatches.append(
                Swatch(
                    slot=row["slot"],
                    hex=parse_hex(row["hex"]),
                    locked=bool(row.get("locked", False)),
                    name=row.get("name", ""),
                )
            )
        if not board.swatches:
            board = cls.from_seed(board.seed, board.harmony)
        return board

    def print_board(self) -> None:
        print(f"Seed {self.seed} · harmony={self.harmony}")
        print("  slot          hex      lock  label")
        for s in self.swatches:
            lock = "LOCK" if s.locked else "----"
            print(f"  {s.slot:12}  {s.hex}  {lock}  {s.name or SLOT_LABELS.get(s.slot, '')}")
