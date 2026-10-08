"""
Premium Atelier render — color depth, glow, camera angles, dress turntable.

  blender --background --python atelier/blender/build_look.py -- \\
    --look garden-sage --out renders/garden-sage.png \\
    --camera three_quarter --turn 35 --glow 1.0
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

CAMERAS = {
    "front": {"loc": (0.0, -4.4, 1.2), "rot": (84, 0, 0), "lens": 50},
    "three_quarter": {"loc": (2.2, -3.8, 1.35), "rot": (78, 0, 28), "lens": 55},
    "side": {"loc": (4.2, -0.3, 1.25), "rot": (85, 0, 88), "lens": 50},
    "low": {"loc": (0.4, -3.6, 0.55), "rot": (72, 0, 6), "lens": 45},
    "detail": {"loc": (-0.95, -2.2, 1.35), "rot": (82, 0, 0), "lens": 70},
}


def parse_args(argv: list[str]) -> argparse.Namespace:
    if "--" in argv:
        argv = argv[argv.index("--") + 1 :]
    else:
        argv = []
    p = argparse.ArgumentParser()
    p.add_argument("--look", default=None)
    p.add_argument("--look-json", default=None, help="Full look JSON override")
    p.add_argument("--palette-json", default=None, help="Coolors board / palette file")
    p.add_argument("--catalog", default=str(Path(__file__).resolve().parents[1] / "catalog"))
    p.add_argument("--out", required=True)
    p.add_argument("--res", type=int, default=1600)
    p.add_argument("--camera", default="three_quarter", choices=list(CAMERAS))
    p.add_argument("--turn", type=float, default=20.0, help="Y-rotation degrees for dress (and suit counter)")
    p.add_argument("--glow", type=float, default=1.0, help="Rim/glow strength 0–2")
    p.add_argument("--dress", default=None, help="Dress silhouette id override")
    p.add_argument("--suit", default=None, help="Suit style id override")
    p.add_argument("--focus", default="party", choices=["party", "dress", "suit"])
    return p.parse_args(argv)


def hex_to_rgba(hex_color: str) -> tuple[float, float, float, float]:
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return (0.75, 0.75, 0.75, 1.0)

    def lin(c: float) -> float:
        return (c / 255.0) ** 2.2

    return (lin(int(h[0:2], 16)), lin(int(h[2:4], 16)), lin(int(h[4:6], 16)), 1.0)


def load_look(catalog_root: Path, look_id: str) -> dict:
    for pack_dir in (catalog_root / "packs").iterdir():
        pack_file = pack_dir / "pack.json"
        if not pack_file.exists():
            continue
        data = json.loads(pack_file.read_text(encoding="utf-8"))
        for look in data.get("looks", []):
            if look["id"] == look_id:
                row = dict(look)
                row["pack"] = data["id"]
                return row
    raise SystemExit(f"Look not found: {look_id}")


def clear_scene(bpy) -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras):
        for item in list(coll):
            coll.remove(item)


def fabric_mat(bpy, name: str, rgba, kind: str = "satin"):
    """Materials tuned so hue reads with depth (sheen / soft SSS / velvet)."""
    m = bpy.data.materials.new(name=name)
    m.use_nodes = True
    nt = m.node_tree
    nodes = nt.nodes
    links = nt.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = rgba

    if kind == "velvet":
        bsdf.inputs["Roughness"].default_value = 0.85
        if "Sheen Weight" in bsdf.inputs:
            bsdf.inputs["Sheen Weight"].default_value = 1.0
            if "Sheen Roughness" in bsdf.inputs:
                bsdf.inputs["Sheen Roughness"].default_value = 0.35
        if "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = 0.15
    elif kind == "chiffon":
        # Soft fabric without heavy transmission (kept color readable)
        bsdf.inputs["Roughness"].default_value = 0.48
        if "Sheen Weight" in bsdf.inputs:
            bsdf.inputs["Sheen Weight"].default_value = 0.35
        if "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = 0.35
    elif kind == "wool":
        bsdf.inputs["Roughness"].default_value = 0.62
        if "Sheen Weight" in bsdf.inputs:
            bsdf.inputs["Sheen Weight"].default_value = 0.25
    else:  # satin — color depth via soft specular + slight subsurface
        bsdf.inputs["Roughness"].default_value = 0.22
        if "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = 0.55
        if "Coat Weight" in bsdf.inputs:
            bsdf.inputs["Coat Weight"].default_value = 0.15
            bsdf.inputs["Coat Roughness"].default_value = 0.1
        if "Subsurface Weight" in bsdf.inputs:
            bsdf.inputs["Subsurface Weight"].default_value = 0.08
            if "Subsurface Radius" in bsdf.inputs:
                bsdf.inputs["Subsurface Radius"].default_value = (
                    max(0.05, rgba[0]),
                    max(0.05, rgba[1]),
                    max(0.05, rgba[2]),
                )

    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return m


def assign(obj, material):
    if obj.data.materials:
        obj.data.materials[0] = material
    else:
        obj.data.materials.append(material)


def parent_keep(child, parent):
    child.parent = parent
    child.matrix_parent_inverse = parent.matrix_world.inverted()


def make_empty(bpy, name: str, loc):
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=loc)
    empty = bpy.context.active_object
    empty.name = name
    return empty


def stand(bpy, x, metal, base_m):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.032, depth=1.08, location=(x, 0, 0.54))
    pole = bpy.context.active_object
    assign(pole, metal)
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.34, depth=0.045, location=(x, 0, 0.022))
    base = bpy.context.active_object
    assign(base, base_m)
    return pole


def resolve_silhouette(catalog_root: Path, dress_id: str | None, suit_id: str | None) -> tuple[str, str]:
    """Map garments.json ids → blender mesh keys."""
    sil, style = dress_id or "a-line", suit_id or "two-piece"
    gpath = catalog_root / "garments.json"
    if not gpath.exists():
        return sil.replace("_", "-"), style.replace("_", "-")
    data = json.loads(gpath.read_text(encoding="utf-8"))
    for d in data.get("dresses", []):
        if d["id"] == sil or d.get("blender") == sil:
            sil = d.get("blender", d["id"])
            break
    for s in data.get("suits", []):
        if s["id"] == style or s.get("blender") == style:
            style = s.get("blender", s["id"])
            break
    return sil.replace("_", "-"), style.replace("_", "-")


def add_dress(bpy, root, dress_hex: str, silhouette: str, form_mat, metal, base_m, glow: float = 1.0):
    x = 0.0
    rgba = hex_to_rgba(dress_hex)
    kind = "velvet" if "velvet" in silhouette else ("chiffon" if "midi" in silhouette or "empire" in silhouette else "satin")
    dress_m = fabric_mat(bpy, "dress", rgba, kind=kind)
    fold = list(rgba)
    fold[0] *= 0.72
    fold[1] *= 0.72
    fold[2] *= 0.72
    fold_m = fabric_mat(bpy, "dress_fold", tuple(fold), kind=kind)
    # lighter fold catch for specular depth
    light = list(rgba)
    light[0] = min(1.0, light[0] * 1.18)
    light[1] = min(1.0, light[1] * 1.18)
    light[2] = min(1.0, light[2] * 1.18)
    light_m = fabric_mat(bpy, "dress_light", tuple(light), kind=kind)

    stand(bpy, x, metal, base_m)

    # neck block — mannequin, not a head
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.065, depth=0.13, location=(x, 0, 1.74))
    neck = bpy.context.active_object
    assign(neck, form_mat)
    parent_keep(neck, root)

    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=0.2, location=(x, 0, 1.5))
    bust = bpy.context.active_object
    bust.scale = (1.05, 0.7, 1.2)
    assign(bust, form_mat)
    parent_keep(bust, root)

    # silhouette geometry
    if silhouette in ("ball-gown", "ball_gown"):
        r_mid, r_hem, hem_z, hem_d = 0.55, 0.95, 0.48, 0.85
    elif silhouette in ("mermaid", "fit-flare", "fit_flare"):
        r_mid, r_hem, hem_z, hem_d = 0.28, 0.7, 0.35, 0.55
    elif silhouette in ("column", "sheath", "slip"):
        r_mid, r_hem, hem_z, hem_d = 0.26, 0.3, 0.55, 0.85
    elif silhouette in ("midi", "midi-a-line"):
        r_mid, r_hem, hem_z, hem_d = 0.42, 0.55, 0.7, 0.45
    elif silhouette in ("empire",):
        r_mid, r_hem, hem_z, hem_d = 0.48, 0.65, 0.55, 0.8
    elif silhouette in ("drop-waist", "drop_waist"):
        r_mid, r_hem, hem_z, hem_d = 0.3, 0.75, 0.42, 0.7
    elif silhouette in ("one-shoulder",):
        r_mid, r_hem, hem_z, hem_d = 0.4, 0.58, 0.55, 0.8
    else:  # a-line default
        r_mid, r_hem, hem_z, hem_d = 0.42, 0.72, 0.5, 0.78

    bpy.ops.mesh.primitive_cone_add(
        vertices=64, radius1=0.27, radius2=0.15, depth=0.4, location=(x, 0, 1.4)
    )
    bodice = bpy.context.active_object
    assign(bodice, dress_m)
    parent_keep(bodice, root)

    if silhouette == "one-shoulder":
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x - 0.16, 0, 1.58))
        strap = bpy.context.active_object
        strap.scale = (0.08, 0.04, 0.16)
        strap.rotation_euler[1] = math.radians(25)
        assign(strap, dress_m)
        parent_keep(strap, root)

    bpy.ops.mesh.primitive_cone_add(
        vertices=64, radius1=r_mid, radius2=0.22, depth=0.5, location=(x, 0, 1.08)
    )
    mid = bpy.context.active_object
    assign(mid, dress_m)
    parent_keep(mid, root)

    bpy.ops.mesh.primitive_cone_add(
        vertices=64, radius1=r_hem, radius2=r_mid * 0.85, depth=hem_d, location=(x, 0, hem_z)
    )
    hem = bpy.context.active_object
    assign(hem, dress_m)
    parent_keep(hem, root)

    # Fold panels — catch light so color depth reads (shadow / mid / highlight)
    mats = (fold_m, dress_m, light_m)
    for i, ox in enumerate((-0.14, 0.0, 0.12)):
        bpy.ops.mesh.primitive_cube_add(
            size=1.0, location=(x + ox, -r_mid * 0.52, 0.88 - i * 0.04)
        )
        panel = bpy.context.active_object
        panel.scale = (0.055 + i * 0.008, 0.012, 0.48)
        panel.rotation_euler[2] = math.radians(-14 + i * 14)
        assign(panel, mats[i])
        parent_keep(panel, root)

    # Soft tinted rim spotlight (no giant glow shell — that hid the dress)
    bpy.ops.object.light_add(type="AREA", location=(x - 0.9, -1.4, 1.6))
    rim_d = bpy.context.active_object
    rim_d.data.energy = 120 * max(0.4, glow)
    rim_d.data.size = 1.2
    rim_d.data.color = (rgba[0], rgba[1], rgba[2])
    rim_d.rotation_euler = (math.radians(70), 0, math.radians(-35))
    parent_keep(rim_d, root)


def add_suit(bpy, root, suit_hex, tie_hex, pocket_hex, pin_hex, form_mat, metal, base_m, style: str, glow: float = 1.0):
    x = 0.0
    suit_m = fabric_mat(
        bpy,
        "suit",
        hex_to_rgba(suit_hex),
        kind="velvet" if "velvet" in style or "tux" in style else "wool",
    )
    tie_m = fabric_mat(bpy, "tie", hex_to_rgba(tie_hex), kind="satin")
    pocket_m = fabric_mat(bpy, "pocket", hex_to_rgba(pocket_hex), kind="satin")
    pin_m = fabric_mat(bpy, "pin", hex_to_rgba(pin_hex), kind="satin")
    shirt_m = fabric_mat(bpy, "shirt", hex_to_rgba("#F7F3EC"), kind="chiffon")

    stand(bpy, x, metal, base_m)
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.065, depth=0.12, location=(x, 0, 1.74))
    neck = bpy.context.active_object
    assign(neck, form_mat)
    parent_keep(neck, root)

    # Jacket — wider if double-breasted
    jx = 0.38 if "double" in style else 0.34
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, 0, 1.36))
    jacket = bpy.context.active_object
    jacket.scale = (jx, 0.19, 0.44)
    assign(jacket, suit_m)
    parent_keep(jacket, root)

    # Waistcoat cue for three-piece
    if "three" in style or "earth" in style or "3p" in style:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, -0.05, 1.28))
        vest = bpy.context.active_object
        vest.scale = (0.26, 0.08, 0.28)
        assign(vest, suit_m)
        parent_keep(vest, root)

    # Lapels
    lapel_rgba = list(hex_to_rgba(suit_hex))
    for i in range(3):
        lapel_rgba[i] *= 0.7
    lapel_m = fabric_mat(bpy, "lapel", tuple(lapel_rgba), kind="satin" if "tux" in style else "wool")
    for side, ox in ((-1, -0.09), (1, 0.09)):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x + ox, -0.11, 1.45))
        lapel = bpy.context.active_object
        lapel.scale = (0.08, 0.03, 0.24)
        ang = 22 if "peak" in style or "tux" in style else 14
        lapel.rotation_euler[2] = math.radians(ang * side)
        assign(lapel, lapel_m)
        parent_keep(lapel, root)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, -0.12, 1.42))
    shirt = bpy.context.active_object
    shirt.scale = (0.09, 0.02, 0.3)
    assign(shirt, shirt_m)
    parent_keep(shirt, root)

    # Tie or bow
    if "tux" in style or "shawl" in style:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, -0.14, 1.5))
        bow = bpy.context.active_object
        bow.scale = (0.1, 0.025, 0.03)
        assign(bow, tie_m)
        parent_keep(bow, root)
    else:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, -0.14, 1.28))
        tie = bpy.context.active_object
        tie.scale = (0.045, 0.02, 0.3)
        assign(tie, tie_m)
        parent_keep(tie, root)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x + 0.17, -0.13, 1.4))
    pocket = bpy.context.active_object
    pocket.scale = (0.055, 0.018, 0.04)
    assign(pocket, pocket_m)
    parent_keep(pocket, root)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.042, location=(x - 0.2, -0.15, 1.48))
    pin = bpy.context.active_object
    assign(pin, pin_m)
    parent_keep(pin, root)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, 0, 0.55))
    pants = bpy.context.active_object
    pants.scale = (0.25, 0.15, 0.5)
    assign(pants, suit_m)
    parent_keep(pants, root)

    for ox in (-0.4, 0.4):
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=24, radius=0.075, depth=0.58, location=(x + ox * 0.55, 0.02, 1.18)
        )
        sleeve = bpy.context.active_object
        sleeve.rotation_euler[1] = math.radians(14 if ox < 0 else -14)
        assign(sleeve, suit_m)
        parent_keep(sleeve, root)

    # Suit rim tint (no opaque glow shell)
    sr = hex_to_rgba(suit_hex)
    bpy.ops.object.light_add(type="AREA", location=(x + 0.9, -1.4, 1.55))
    rim_s = bpy.context.active_object
    rim_s.data.energy = 100 * max(0.4, glow)
    rim_s.data.size = 1.1
    rim_s.data.color = (sr[0], sr[1], sr[2])
    rim_s.rotation_euler = (math.radians(70), 0, math.radians(35))
    parent_keep(rim_s, root)


def setup_premium_studio(bpy, glow: float):
    world = bpy.data.worlds.new("PremiumLinen")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.22, 0.21, 0.195, 1.0)  # soft linen studio
    bg.inputs[1].default_value = 0.55

    # Key — soft large
    bpy.ops.object.light_add(type="AREA", location=(3.2, -2.8, 3.4))
    key = bpy.context.active_object
    key.data.energy = 700
    key.data.size = 3.5
    key.data.color = (1.0, 0.96, 0.9)
    key.rotation_euler = (math.radians(50), 0, math.radians(40))

    # Fill
    bpy.ops.object.light_add(type="AREA", location=(-2.8, -2.0, 2.6))
    fill = bpy.context.active_object
    fill.data.energy = 280
    fill.data.size = 2.8
    fill.data.color = (0.85, 0.9, 1.0)

    # Rim glow — reveals color edge depth
    bpy.ops.object.light_add(type="AREA", location=(0.2, 2.8, 2.2))
    rim = bpy.context.active_object
    rim.data.energy = 350 * max(0.2, glow)
    rim.data.size = 2.2
    rim.data.color = (1.0, 0.92, 0.85)

    # Soft bounce from below
    bpy.ops.object.light_add(type="AREA", location=(0, -1.0, 0.15))
    bounce = bpy.context.active_object
    bounce.data.energy = 80
    bounce.data.size = 4.0
    bounce.rotation_euler = (math.radians(-90), 0, 0)

    # Floor + cyc
    bpy.ops.mesh.primitive_plane_add(size=14, location=(0, 0, 0))
    floor = bpy.context.active_object
    assign(floor, fabric_mat(bpy, "floor", (0.55, 0.52, 0.47, 1), kind="wool"))

    bpy.ops.mesh.primitive_plane_add(size=14, location=(0, 3.0, 3.0))
    wall = bpy.context.active_object
    wall.rotation_euler[0] = math.radians(90)
    assign(wall, fabric_mat(bpy, "cyc", (0.62, 0.59, 0.54, 1), kind="wool"))


def set_camera(bpy, name: str, focus: str):
    cfg = CAMERAS[name]
    loc = list(cfg["loc"])
    if focus == "dress":
        loc[0] = loc[0] - 0.7
    elif focus == "suit":
        loc[0] = loc[0] + 0.7
    bpy.ops.object.camera_add(location=tuple(loc))
    cam = bpy.context.active_object
    cam.rotation_euler = tuple(math.radians(a) for a in cfg["rot"])
    cam.data.lens = cfg["lens"]
    cam.data.dof.use_dof = True
    cam.data.dof.aperture_fstop = 2.8
    bpy.context.scene.camera = cam
    return cam


def palette_map(look: dict) -> dict[str, str]:
    return {s["slot"]: s["hex"] for s in look.get("palette", [])}


def apply_palette_file(look: dict, path: str | None) -> dict:
    if not path:
        return look
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = data.get("palette") or [
        {"slot": s["slot"], "hex": s["hex"], "name": s.get("name", s["slot"])}
        for s in data.get("swatches", [])
    ]
    look = dict(look)
    look["palette"] = rows
    return look


def main() -> None:
    import bpy

    args = parse_args(sys.argv)
    if args.look_json:
        look = json.loads(Path(args.look_json).read_text(encoding="utf-8"))
    elif args.look:
        look = load_look(Path(args.catalog), args.look)
    else:
        raise SystemExit("Provide --look or --look-json")

    look = apply_palette_file(look, args.palette_json)
    colors = palette_map(look)

    clear_scene(bpy)
    setup_premium_studio(bpy, glow=args.glow)

    form_mat = fabric_mat(bpy, "form", hex_to_rgba("#CDB59A"), kind="wool")
    metal = fabric_mat(bpy, "metal", (0.35, 0.35, 0.36, 1), kind="satin")
    base_m = fabric_mat(bpy, "base", (0.12, 0.12, 0.12, 1), kind="wool")

    dress_hex = colors.get("dress", "#9DAE8F")
    suit_hex = colors.get("suit", "#6E6A63")
    tie_hex = colors.get("tie", colors.get("trim", "#C9AE7C"))
    pocket_hex = colors.get("pocket", colors.get("shirt", colors.get("dupatta", "#F4EFE6")))
    pin_hex = colors.get("boutonniere", colors.get("accent", tie_hex))

    sil = args.dress or look.get("dress_id") or "a-line"
    suit_style = args.suit or look.get("suit_id") or "two-piece"
    for g in look.get("garments", []):
        if g.get("slot") == "dress" and not args.dress:
            sil = g.get("silhouette", sil)
        if g.get("slot") == "suit" and not args.suit:
            suit_style = g.get("silhouette", suit_style)
    sil, suit_style = resolve_silhouette(Path(args.catalog), sil, suit_style)

    dress_root = make_empty(bpy, "DRESS_ROOT", (-1.05, 0, 0))
    suit_root = make_empty(bpy, "SUIT_ROOT", (1.05, 0, 0))

    if args.focus in ("party", "dress"):
        add_dress(
            bpy, dress_root, dress_hex, sil, form_mat, metal, base_m, glow=args.glow
        )
        dress_root.rotation_euler[2] = math.radians(args.turn)
    if args.focus in ("party", "suit"):
        add_suit(
            bpy,
            suit_root,
            suit_hex,
            tie_hex,
            pocket_hex,
            pin_hex,
            form_mat,
            metal,
            base_m,
            suit_style,
            glow=args.glow,
        )
        suit_root.rotation_euler[2] = math.radians(-args.turn * 0.6)

    set_camera(bpy, args.camera, args.focus)

    scene = bpy.context.scene
    for engine in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            scene.render.engine = engine
            break
        except TypeError:
            continue

    scene.render.resolution_x = args.res
    scene.render.resolution_y = int(args.res * 0.8)
    scene.render.filepath = str(Path(args.out).resolve())
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    if hasattr(scene.eevee, "taa_render_samples"):
        scene.eevee.taa_render_samples = 160
    if hasattr(scene.eevee, "use_bloom"):
        # Soft bloom only — high intensity washed out garment color
        scene.eevee.use_bloom = args.glow > 0.35
        scene.eevee.bloom_intensity = 0.035 * max(0.4, args.glow)
        scene.eevee.bloom_threshold = 1.05
        if hasattr(scene.eevee, "bloom_radius"):
            scene.eevee.bloom_radius = 3.5
    if hasattr(scene.eevee, "use_soft_shadows"):
        scene.eevee.use_soft_shadows = True
    if hasattr(scene.view_settings, "view_transform"):
        try:
            scene.view_settings.view_transform = "Filmic"
            scene.view_settings.look = "Medium High Contrast"
        except TypeError:
            pass

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.render.render(write_still=True)
    print(
        f"RENDERED {look.get('id', 'custom')} cam={args.camera} turn={args.turn} "
        f"dress={sil} suit={suit_style} -> {args.out}"
    )


if __name__ == "__main__":
    main()
