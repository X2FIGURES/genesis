"""Coolors-style palette matching for garment slots."""

from .coolors import (
    GARMENT_SLOTS,
    SLOT_LABELS,
    Harmony,
    PaletteBoard,
    generate_harmony,
    hex_to_hsl,
    hsl_to_hex,
    parse_hex,
)

__all__ = [
    "GARMENT_SLOTS",
    "SLOT_LABELS",
    "Harmony",
    "PaletteBoard",
    "generate_harmony",
    "hex_to_hsl",
    "hsl_to_hex",
    "parse_hex",
]
