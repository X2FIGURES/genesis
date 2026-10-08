"""
Blender script: build mannequin dress + suit for one look and render.

Run (from apps/atelier-studio):
  blender --background --python atelier/blender/build_look.py -- \\
    --look garden-sage --out renders/garden-sage.png
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path


def parse_args(argv: list[str]) -> argparse.Namespace:
    # Blender passes args after "--"
    if "--" in argv:
        argv = argv[argv.index("--") + 1 :]
    else:
        argv = []
    p = argparse.ArgumentParser(description="Render one Atelier look")
    p.add_argument("--look", required=True, help="Look id from catalog packs")
    p.add_argument(
        "--catalog",
        default=str(Path(__file__).resolve().parents[1] / "catalog"),
        help="Path to atelier/catalog",
    )
    p.add_argument("--out", required=True, help="Output PNG path")
    p.add_argument("--engine", default="BLENDER_EEVEE_NEXT", help="Render engine")
    p.add_argument("--res", type=int, default=1280, help="Long-edge resolution")
    return p.parse_args(argv)


def hex_to_rgba(hex_color: str) -> tuple[float, float, float, float]:
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return (0.8, 0.8, 0.8, 1.0)
    r = int(h[0:2], 16) / 255.0
    g = int(h[2:4], 16) / 255.0
    b = int(h[4:6], 16) / 255.0
    # rough sRGB → linear for Blender materials
    def lin(c: float) -> float:
        return c**2.2

    return (lin(r), lin(g), lin(b), 1.0)


def load_look(catalog_root: Path, look_id: str) -> dict:
    packs = catalog_root / "packs"
    for pack_dir in packs.iterdir():
        pack_file = pack_dir / "pack.json"
        if not pack_file.exists():
            continue
        data = json.loads(pack_file.read_text(encoding="utf-8"))
        for look in data.get("looks", []):
            if look["id"] == look_id:
                look = dict(look)
                look["pack"] = data["id"]
                return look
    raise SystemExit(f"Look not found: {look_id}")


def clear_scene(bpy) -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras):
        for item in list(block):
            block.remove(item)


def mat(bpy, name: str, rgba: tuple[float, float, float, float], rough=0.45):
    m = bpy.data.materials.new(name=name)
    m.use_nodes = True
    nodes = m.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = rough
    return m


def add_mannequin_body(bpy, name: str, x: float, skin_rgba):
    """Simple dress-form / torso mannequin (no face — shop style)."""
    bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.7, location=(x, 0, 1.15))
    torso = bpy.context.active_object
    torso.name = f"{name}_torso"
    torso.data.materials.append(mat(bpy, f"{name}_skin", skin_rgba, rough=0.55))

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.16, location=(x, 0, 1.62))
    neck = bpy.context.active_object
    neck.name = f"{name}_neck"
    neck.scale = (0.55, 0.55, 0.7)
    neck.data.materials.append(mat(bpy, f"{name}_skin2", skin_rgba, rough=0.55))

    # stand pole
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.9, location=(x, 0, 0.45))
    pole = bpy.context.active_object
    pole.name = f"{name}_pole"
    pole.data.materials.append(
        mat(bpy, f"{name}_metal", (0.35, 0.35, 0.35, 1.0), rough=0.3)
    )

    bpy.ops.mesh.primitive_cylinder_add(radius=0.28, depth=0.04, location=(x, 0, 0.02))
    base = bpy.context.active_object
    base.name = f"{name}_base"
    base.data.materials.append(
        mat(bpy, f"{name}_base", (0.25, 0.25, 0.25, 1.0), rough=0.4)
    )
    return torso


def add_dress(bpy, x: float, color_hex: str, silhouette: str = "a-line"):
    rgba = hex_to_rgba(color_hex)
    # bodice
    bpy.ops.mesh.primitive_cone_add(
        radius1=0.28, radius2=0.18, depth=0.45, location=(x, 0, 1.25)
    )
    bodice = bpy.context.active_object
    bodice.name = "dress_bodice"
    bodice.data.materials.append(mat(bpy, "dress_bodice", rgba, rough=0.35))

    # skirt — wider for a-line / lehenga feel
    r1 = 0.55 if "lehenga" in silhouette or "a-line" in silhouette else 0.38
    bpy.ops.mesh.primitive_cone_add(
        radius1=r1, radius2=0.26, depth=0.95, location=(x, 0, 0.72)
    )
    skirt = bpy.context.active_object
    skirt.name = "dress_skirt"
    skirt.rotation_euler[0] = math.pi  # point up so wide end is bottom-ish after flip
    # Actually cone with wide at bottom: radius1 bottom in blender is +Z by default depending version
    # Reset: place wide skirt as cylinder scaled
    bpy.data.objects.remove(skirt, do_unlink=True)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.32, depth=0.9, location=(x, 0, 0.7))
    skirt = bpy.context.active_object
    skirt.name = "dress_skirt"
    skirt.scale = (r1 / 0.32, r1 / 0.32, 1.0)
    # flare bottom with shapekey-ish: just scale more in X/Y at lower via two pieces
    skirt.data.materials.append(mat(bpy, "dress_skirt", rgba, rough=0.4))

    bpy.ops.mesh.primitive_cylinder_add(
        radius=r1 * 0.95, depth=0.35, location=(x, 0, 0.28)
    )
    hem = bpy.context.active_object
    hem.name = "dress_hem"
    hem.data.materials.append(mat(bpy, "dress_hem", rgba, rough=0.42))
    return bodice


def add_suit(bpy, x: float, suit_hex: str, tie_hex: str, pocket_hex: str):
    suit = hex_to_rgba(suit_hex)
    tie = hex_to_rgba(tie_hex)
    pocket = hex_to_rgba(pocket_hex)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, 0, 1.15))
    jacket = bpy.context.active_object
    jacket.name = "suit_jacket"
    jacket.scale = (0.28, 0.18, 0.4)
    jacket.data.materials.append(mat(bpy, "suit_jacket", suit, rough=0.5))

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, 0, 0.55))
    pants = bpy.context.active_object
    pants.name = "suit_pants"
    pants.scale = (0.22, 0.14, 0.4)
    pants.data.materials.append(mat(bpy, "suit_pants", suit, rough=0.5))

    # shirt
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, -0.02, 1.28))
    shirt = bpy.context.active_object
    shirt.name = "shirt"
    shirt.scale = (0.12, 0.05, 0.18)
    shirt.data.materials.append(
        mat(bpy, "shirt", hex_to_rgba("#F7F3EC"), rough=0.55)
    )

    # tie
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, -0.08, 1.15))
    tie_obj = bpy.context.active_object
    tie_obj.name = "tie"
    tie_obj.scale = (0.04, 0.02, 0.22)
    tie_obj.data.materials.append(mat(bpy, "tie", tie, rough=0.4))

    # pocket square
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x + 0.12, -0.1, 1.25))
    pk = bpy.context.active_object
    pk.name = "pocket"
    pk.scale = (0.05, 0.015, 0.03)
    pk.data.materials.append(mat(bpy, "pocket", pocket, rough=0.45))

    # boutonniere
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.035, location=(x - 0.14, -0.12, 1.32))
    pin = bpy.context.active_object
    pin.name = "boutonniere"
    pin.data.materials.append(mat(bpy, "boutonniere", tie, rough=0.35))


def setup_world(bpy, look_name: str):
    world = bpy.data.worlds.new("Studio")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.92, 0.89, 0.84, 1.0)  # linen
    bg.inputs[1].default_value = 1.0

    # lights
    bpy.ops.object.light_add(type="AREA", location=(2.5, -2.0, 3.0))
    key = bpy.context.active_object
    key.data.energy = 400
    key.data.size = 2.5
    key.rotation_euler = (math.radians(50), 0, math.radians(35))

    bpy.ops.object.light_add(type="AREA", location=(-2.0, -1.5, 2.2))
    fill = bpy.context.active_object
    fill.data.energy = 180
    fill.data.size = 2.0

    # camera
    bpy.ops.object.camera_add(location=(0, -3.6, 1.2))
    cam = bpy.context.active_object
    cam.rotation_euler = (math.radians(82), 0, 0)
    bpy.context.scene.camera = cam

    # floor
    bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "floor"
    floor.data.materials.append(
        mat(bpy, "floor", (0.88, 0.84, 0.78, 1.0), rough=0.7)
    )


def palette_map(look: dict) -> dict[str, str]:
    out: dict[str, str] = {}
    for swatch in look.get("palette", []):
        out[swatch["slot"]] = swatch["hex"]
    return out


def main() -> None:
    import bpy

    args = parse_args(sys.argv)
    look = load_look(Path(args.catalog), args.look)
    colors = palette_map(look)

    clear_scene(bpy)
    setup_world(bpy, look["name"])

    skin = hex_to_rgba("#E8D5C4")
    dress_hex = colors.get("dress", "#9DAE8F")
    suit_hex = colors.get("suit", "#6E6A63")
    tie_hex = colors.get("tie", colors.get("trim", "#C9AE7C"))
    pocket_hex = colors.get("pocket", colors.get("shirt", "#F4EFE6"))

    sil = "a-line"
    for g in look.get("garments", []):
        if g.get("slot") == "dress":
            sil = g.get("silhouette", "a-line")

    # Left: dress mannequin · Right: suit mannequin
    add_mannequin_body(bpy, "bride_party", -0.85, skin)
    add_dress(bpy, -0.85, dress_hex, silhouette=sil)

    add_mannequin_body(bpy, "groom_party", 0.85, skin)
    add_suit(bpy, 0.85, suit_hex, tie_hex, pocket_hex)

    scene = bpy.context.scene
    # Engine fallback for Blender 4.0 apt build
    engine = args.engine
    if engine not in {"BLENDER_EEVEE", "BLENDER_EEVEE_NEXT", "CYCLES"}:
        engine = "BLENDER_EEVEE"
    try:
        scene.render.engine = engine
    except TypeError:
        scene.render.engine = "BLENDER_EEVEE"

    scene.render.resolution_x = args.res
    scene.render.resolution_y = int(args.res * 0.75)
    scene.render.filepath = str(Path(args.out).resolve())
    scene.render.image_settings.file_format = "PNG"

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    bpy.ops.render.render(write_still=True)
    print(f"RENDERED {look['id']} -> {out_path}")


if __name__ == "__main__":
    main()
