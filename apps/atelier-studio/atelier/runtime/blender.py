"""Cross-platform Blender discovery for local installs."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


def blender_hint() -> str:
    if sys.platform == "darwin":
        return (
            "Install Blender from https://www.blender.org/download/ "
            "or `brew install --cask blender`, then re-open Atelier."
        )
    if sys.platform.startswith("win"):
        return (
            "Install Blender from https://www.blender.org/download/ "
            "and ensure blender.exe is on PATH (or keep the default Program Files install)."
        )
    return (
        "Install Blender 4.x (`sudo apt install blender` or from blender.org) "
        "and ensure `blender` is on PATH."
    )


def _windows_candidates() -> list[Path]:
    roots = []
    for key in ("ProgramFiles", "ProgramFiles(x86)", "LOCALAPPDATA"):
        raw = os.environ.get(key)
        if raw:
            roots.append(Path(raw) / "Blender Foundation")
    out: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for child in sorted(root.glob("Blender *"), reverse=True):
            exe = child / "blender.exe"
            if exe.exists():
                out.append(exe)
    return out


def _macos_candidates() -> list[Path]:
    return [
        Path("/Applications/Blender.app/Contents/MacOS/Blender"),
        Path.home() / "Applications/Blender.app/Contents/MacOS/Blender",
    ]


def _linux_candidates() -> list[Path]:
    return [
        Path("/usr/bin/blender"),
        Path("/usr/local/bin/blender"),
        Path("/snap/bin/blender"),
        Path.home() / ".local/bin/blender",
    ]


def find_blender(explicit: str | None = None) -> str | None:
    """Return path to Blender binary, or None if missing."""
    if explicit:
        p = Path(explicit).expanduser()
        return str(p) if p.exists() else None

    env = os.environ.get("ATELIER_BLENDER") or os.environ.get("BLENDER")
    if env:
        p = Path(env).expanduser()
        if p.exists():
            return str(p)

    which = shutil.which("blender") or shutil.which("Blender")
    if which:
        return which

    candidates: list[Path]
    if sys.platform == "darwin":
        candidates = _macos_candidates()
    elif sys.platform.startswith("win"):
        candidates = _windows_candidates()
    else:
        candidates = _linux_candidates()

    for path in candidates:
        if path.exists():
            return str(path)
    return None
