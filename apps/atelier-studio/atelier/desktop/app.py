"""
Atelier Studio — internal desktop app (CustomTkinter).

For team use only: pick looks, Coolors-lock palette, shift camera / turn / glow,
render Blender mannequins, judge color depth.
"""

from __future__ import annotations

import subprocess
import threading
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk
from PIL import Image

from atelier.catalog import (
    CUSTOMS_ROOT,
    all_looks,
    get_look,
    list_packs,
    load_garments,
)
from atelier.palette import GARMENT_SLOTS, Harmony, PaletteBoard
from atelier.runtime import blender_hint, find_blender

ROOT = Path(__file__).resolve().parents[2]
BUILD_SCRIPT = ROOT / "atelier" / "blender" / "build_look.py"
CATALOG = ROOT / "atelier" / "catalog"
RENDERS = ROOT / "renders" / "desktop"

# Ivory & Sage — internal product chrome
COLORS = {
    "bg": "#1C1A17",
    "panel": "#26221E",
    "panel2": "#2F2B26",
    "linen": "#E8E2D6",
    "muted": "#A39A8C",
    "sage": "#8FA67E",
    "champagne": "#C9AE7C",
    "danger": "#C47A6A",
}


class AtelierDesktop(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Atelier Studio · Internal")
        self.geometry("1280x820")
        self.minsize(1080, 700)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        self.configure(fg_color=COLORS["bg"])

        self.looks = all_looks()
        self.garments = load_garments()
        self.board: PaletteBoard | None = None
        self.photo: ImageTk.PhotoImage | None = None
        self._rendering = False
        self.slot_vars: dict[str, ctk.StringVar] = {}
        self.lock_vars: dict[str, ctk.BooleanVar] = {}

        self._build_chrome()
        if self.looks:
            self.look_menu.set(self.looks[0]["id"])
            self._load_look(self.looks[0]["id"])

    def _build_chrome(self) -> None:
        header = ctk.CTkFrame(self, fg_color=COLORS["panel"], corner_radius=0, height=64)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(
            header,
            text="ATELIER STUDIO",
            font=ctk.CTkFont(family="Georgia", size=22, weight="bold"),
            text_color=COLORS["linen"],
        ).pack(side="left", padx=24, pady=16)
        ctk.CTkLabel(
            header,
            text="INTERNAL · party attire · color depth",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["muted"],
        ).pack(side="left", padx=(0, 12))
        self.status = ctk.CTkLabel(
            header, text="Ready", font=ctk.CTkFont(size=12), text_color=COLORS["sage"]
        )
        self.status.pack(side="right", padx=24)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=16)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        left = ctk.CTkScrollableFrame(
            body, width=340, fg_color=COLORS["panel"], corner_radius=12
        )
        left.grid(row=0, column=0, sticky="nsw", padx=(0, 12))

        right = ctk.CTkFrame(body, fg_color=COLORS["panel"], corner_radius=12)
        right.grid(row=0, column=1, sticky="nsew")

        # —— Look ——
        ctk.CTkLabel(
            left, text="Look", font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["champagne"]
        ).pack(anchor="w", padx=16, pady=(16, 4))
        look_ids = [look["id"] for look in self.looks]
        self.look_menu = ctk.CTkOptionMenu(
            left,
            values=look_ids or ["(none)"],
            command=self._load_look,
            fg_color=COLORS["panel2"],
            button_color=COLORS["sage"],
            button_hover_color="#7A9468",
            width=300,
        )
        self.look_menu.pack(padx=16, pady=4)
        self.mood_label = ctk.CTkLabel(
            left, text="", wraplength=300, justify="left", text_color=COLORS["muted"], font=ctk.CTkFont(size=12)
        )
        self.mood_label.pack(anchor="w", padx=16, pady=(4, 8))

        # —— Garments ——
        ctk.CTkLabel(
            left, text="Silhouettes", font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["champagne"]
        ).pack(anchor="w", padx=16, pady=(8, 4))
        dresses = [d["id"] for d in self.garments.get("dresses", [])]
        suits = [s["id"] for s in self.garments.get("suits", [])]
        self.dress_menu = ctk.CTkOptionMenu(
            left, values=dresses or ["a-line"], fg_color=COLORS["panel2"], width=300
        )
        self.dress_menu.pack(padx=16, pady=2)
        self.suit_menu = ctk.CTkOptionMenu(
            left, values=suits or ["two-piece"], fg_color=COLORS["panel2"], width=300
        )
        self.suit_menu.pack(padx=16, pady=(2, 8))

        # —— Palette ——
        ctk.CTkLabel(
            left, text="Palette · Coolors", font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["champagne"]
        ).pack(anchor="w", padx=16, pady=(8, 4))
        self.harmony = ctk.CTkOptionMenu(
            left,
            values=[h.value for h in Harmony],
            fg_color=COLORS["panel2"],
            width=300,
        )
        self.harmony.set("wedding")
        self.harmony.pack(padx=16, pady=2)

        self.palette_frame = ctk.CTkFrame(left, fg_color="transparent")
        self.palette_frame.pack(fill="x", padx=12, pady=8)
        for slot in GARMENT_SLOTS:
            row = ctk.CTkFrame(self.palette_frame, fg_color=COLORS["panel2"], corner_radius=8)
            row.pack(fill="x", pady=3)
            self.lock_vars[slot] = ctk.BooleanVar(value=False)
            ctk.CTkCheckBox(
                row, text="", variable=self.lock_vars[slot], width=24, checkbox_width=18, checkbox_height=18
            ).pack(side="left", padx=(8, 0), pady=8)
            ctk.CTkLabel(row, text=slot, width=90, anchor="w", text_color=COLORS["linen"]).pack(
                side="left", padx=4
            )
            var = ctk.StringVar(value="#9DAE8F")
            self.slot_vars[slot] = var
            entry = ctk.CTkEntry(row, textvariable=var, width=90, fg_color=COLORS["bg"])
            entry.pack(side="left", padx=4, pady=8)
            swatch = ctk.CTkFrame(row, width=28, height=28, corner_radius=6, fg_color=var.get())
            swatch.pack(side="right", padx=8, pady=8)
            swatch.pack_propagate(False)
            var.trace_add("write", lambda *_a, s=slot, sw=swatch, v=var: self._tint_swatch(sw, v))

        btn_row = ctk.CTkFrame(left, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=4)
        ctk.CTkButton(
            btn_row, text="Regenerate", width=140, fg_color=COLORS["sage"], command=self._regenerate
        ).pack(side="left", padx=(0, 6))
        ctk.CTkButton(
            btn_row, text="Shuffle", width=140, fg_color=COLORS["panel2"], command=self._shuffle
        ).pack(side="left")

        # —— Camera / turn / glow ——
        ctk.CTkLabel(
            left, text="Camera · Turn · Glow", font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["champagne"]
        ).pack(anchor="w", padx=16, pady=(12, 4))
        self.camera = ctk.CTkOptionMenu(
            left,
            values=["front", "three_quarter", "side", "low", "detail"],
            fg_color=COLORS["panel2"],
            width=300,
        )
        self.camera.set("three_quarter")
        self.camera.pack(padx=16, pady=2)
        self.focus = ctk.CTkOptionMenu(
            left, values=["party", "dress", "suit"], fg_color=COLORS["panel2"], width=300
        )
        self.focus.set("party")
        self.focus.pack(padx=16, pady=2)

        self.turn = ctk.CTkSlider(left, from_=0, to=180, number_of_steps=36, width=300)
        self.turn.set(30)
        self.turn.pack(padx=16, pady=(8, 2))
        self.turn_label = ctk.CTkLabel(left, text="Turn 30°", text_color=COLORS["muted"])
        self.turn_label.pack(anchor="w", padx=16)
        self.turn.configure(command=lambda v: self.turn_label.configure(text=f"Turn {int(float(v))}°"))

        self.glow = ctk.CTkSlider(left, from_=0.2, to=2.0, number_of_steps=36, width=300)
        self.glow.set(1.2)
        self.glow.pack(padx=16, pady=(8, 2))
        self.glow_label = ctk.CTkLabel(left, text="Glow 1.20", text_color=COLORS["muted"])
        self.glow_label.pack(anchor="w", padx=16)
        self.glow.configure(command=lambda v: self.glow_label.configure(text=f"Glow {float(v):.2f}"))

        ctk.CTkButton(
            left,
            text="Render mannequins",
            height=44,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["champagne"],
            text_color=COLORS["bg"],
            hover_color="#B89A68",
            command=self._start_render,
        ).pack(padx=16, pady=(16, 8), fill="x")
        ctk.CTkButton(
            left,
            text="Save custom look",
            height=36,
            fg_color=COLORS["panel2"],
            command=self._save_custom,
        ).pack(padx=16, pady=(0, 20), fill="x")

        # —— Preview ——
        ctk.CTkLabel(
            right,
            text="Render preview",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["linen"],
        ).pack(anchor="w", padx=20, pady=(16, 8))
        self.preview = ctk.CTkLabel(
            right,
            text="Pick a look and hit Render.\nGlow · camera · turn control color depth.",
            text_color=COLORS["muted"],
            fg_color=COLORS["bg"],
            corner_radius=10,
            width=820,
            height=620,
        )
        self.preview.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def _tint_swatch(self, swatch: ctk.CTkFrame, var: ctk.StringVar) -> None:
        hx = var.get().strip()
        if not hx.startswith("#"):
            hx = "#" + hx
        if len(hx) == 7:
            try:
                swatch.configure(fg_color=hx.upper())
            except Exception:
                pass

    def _load_look(self, look_id: str) -> None:
        try:
            look = get_look(look_id)
        except KeyError:
            return
        self.mood_label.configure(text=look.get("mood", ""))
        self.board = PaletteBoard.from_look_palette(look.get("palette", []), harmony=self.harmony.get())
        for s in self.board.swatches:
            if s.slot in self.slot_vars:
                self.slot_vars[s.slot].set(s.hex)
                self.lock_vars[s.slot].set(s.locked)
        dress = look.get("dress_id")
        suit = look.get("suit_id")
        for g in look.get("garments", []):
            if g.get("slot") == "dress":
                dress = g.get("silhouette", dress)
            if g.get("slot") == "suit":
                suit = g.get("silhouette", suit)
        if dress and dress in self.dress_menu.cget("values"):
            self.dress_menu.set(dress)
        if suit and suit in self.suit_menu.cget("values"):
            self.suit_menu.set(suit)
        # show existing render if any
        for candidate in (
            RENDERS / f"{look_id}.png",
            ROOT / "renders" / f"{look_id}.png",
            ROOT / "renders" / "premium" / f"{look_id}-party.png",
        ):
            if candidate.exists():
                self._show_image(candidate)
                break
        self.status.configure(text=f"Loaded {look_id}", text_color=COLORS["sage"])

    def _sync_board_from_ui(self) -> PaletteBoard:
        look_id = self.look_menu.get()
        look = get_look(look_id)
        board = PaletteBoard.from_look_palette(look.get("palette", []), harmony=self.harmony.get())
        for slot in GARMENT_SLOTS:
            hx = self.slot_vars[slot].get().strip()
            locked = bool(self.lock_vars[slot].get())
            try:
                board.set_slot(slot, hx, lock=locked)
            except ValueError:
                pass
        board.harmony = self.harmony.get()
        self.board = board
        return board

    def _regenerate(self) -> None:
        board = self._sync_board_from_ui()
        # preserve locks from UI
        for slot in GARMENT_SLOTS:
            board.lock(slot, bool(self.lock_vars[slot].get()))
            if self.lock_vars[slot].get():
                try:
                    board.set_slot(slot, self.slot_vars[slot].get(), lock=True)
                except ValueError:
                    pass
        board.regenerate(harmony=self.harmony.get())
        for s in board.swatches:
            self.slot_vars[s.slot].set(s.hex)
        self.status.configure(text="Palette regenerated", text_color=COLORS["sage"])

    def _shuffle(self) -> None:
        board = self._sync_board_from_ui()
        for slot in GARMENT_SLOTS:
            board.lock(slot, bool(self.lock_vars[slot].get()))
        board.shuffle_unlocked()
        for s in board.swatches:
            self.slot_vars[s.slot].set(s.hex)
        self.status.configure(text="Shuffled unlocked slots", text_color=COLORS["sage"])

    def _save_custom(self) -> None:
        board = self._sync_board_from_ui()
        look = get_look(self.look_menu.get())
        custom = dict(look)
        custom_id = f"{look['id']}-desktop"
        custom["id"] = custom_id
        custom["name"] = f"{look['name']} (desktop)"
        custom["palette"] = board.as_palette_rows()
        custom["dress_id"] = self.dress_menu.get()
        custom["suit_id"] = self.suit_menu.get()
        garments = list(custom.get("garments", []))
        for slot, sil in (("dress", self.dress_menu.get()), ("suit", self.suit_menu.get())):
            found = False
            for g in garments:
                if g.get("slot") == slot:
                    g["silhouette"] = sil
                    found = True
            if not found:
                garments.append({"slot": slot, "label": slot, "silhouette": sil, "fabric": "satin"})
        custom["garments"] = garments
        CUSTOMS_ROOT.mkdir(parents=True, exist_ok=True)
        path = CUSTOMS_ROOT / f"{custom_id}.json"
        path.write_text(__import__("json").dumps(custom, indent=2) + "\n", encoding="utf-8")
        board.save(CUSTOMS_ROOT / f"{custom_id}.palette.json")
        self.status.configure(text=f"Saved {custom_id}", text_color=COLORS["sage"])
        # refresh look list
        ids = [look["id"] for look in all_looks()]
        if custom_id not in ids:
            ids.append(custom_id)
        self.look_menu.configure(values=ids)
        self.look_menu.set(custom_id)

    def _start_render(self) -> None:
        if self._rendering:
            return
        blender = find_blender()
        if not blender:
            messagebox.showerror("Atelier", f"Blender not found.\n\n{blender_hint()}")
            return
        self._rendering = True
        self.status.configure(text="Rendering…", text_color=COLORS["champagne"])
        board = self._sync_board_from_ui()
        look_id = self.look_menu.get()
        camera = self.camera.get()
        turn = float(self.turn.get())
        glow = float(self.glow.get())
        focus = self.focus.get()
        dress = self.dress_menu.get()
        suit = self.suit_menu.get()

        def worker() -> None:
            try:
                RENDERS.mkdir(parents=True, exist_ok=True)
                out = RENDERS / f"{look_id}_{camera}_t{int(turn)}.png"
                pal_path = RENDERS / f"{look_id}.palette.json"
                board.save(pal_path)
                look = get_look(look_id)
                cmd = [
                    blender,
                    "--background",
                    "--python",
                    str(BUILD_SCRIPT),
                    "--",
                    "--out",
                    str(out),
                    "--res",
                    "1400",
                    "--camera",
                    camera,
                    "--turn",
                    str(turn),
                    "--glow",
                    str(glow),
                    "--focus",
                    focus,
                    "--dress",
                    dress,
                    "--suit",
                    suit,
                    "--catalog",
                    str(CATALOG),
                    "--palette-json",
                    str(pal_path),
                ]
                custom = CUSTOMS_ROOT / f"{look['id']}.json"
                if custom.exists():
                    cmd += ["--look-json", str(custom)]
                else:
                    cmd += ["--look", look["id"]]
                proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
                ok = proc.returncode == 0 and out.exists()
                self.after(0, lambda: self._render_done(ok, out, proc.stderr or proc.stdout))
            except Exception as exc:  # noqa: BLE001
                self.after(0, lambda: self._render_done(False, None, str(exc)))

        threading.Thread(target=worker, daemon=True).start()

    def _render_done(self, ok: bool, path: Path | None, log: str) -> None:
        self._rendering = False
        if ok and path:
            self._show_image(path)
            self.status.configure(text=f"Rendered {path.name}", text_color=COLORS["sage"])
        else:
            self.status.configure(text="Render failed", text_color=COLORS["danger"])
            messagebox.showerror("Atelier render failed", (log or "unknown error")[-1500:])

    def _show_image(self, path: Path) -> None:
        img = Image.open(path).convert("RGBA")
        max_w, max_h = 860, 640
        img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
        self.photo = ctk_img  # keep ref
        self.preview.configure(image=ctk_img, text="")


def run_desktop() -> None:
    packs = list_packs()
    if not packs:
        print("No packs found — check atelier/catalog/packs")
    app = AtelierDesktop()
    app.mainloop()


if __name__ == "__main__":
    run_desktop()
