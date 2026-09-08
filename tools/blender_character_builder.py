# Blender character builder — Overcooked-style chibi chefs (CC0 output).
# Run:  blender --background --python tools/blender_character_builder.py
# Builds one chef per VARIANT palette (see VARIANTS) and exports GLB files to
# assets/characters/. Reference: Ref/Nintendo_Profile_Buck_v01 (Overcooked chef).
#
# Conventions: character faces -Y in Blender -> exports facing +Z in three.js.
import bpy
import math
import os

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "assets", "characters")

# ---------------------------------------------------------------- palette --
PALETTE = {
    "skin_tan": (0.91, 0.62, 0.35, 1),
    "skin_light": (0.95, 0.76, 0.55, 1),
    "skin_orange": (0.89, 0.5, 0.22, 1),
    "hair_brown": (0.28, 0.16, 0.08, 1),
    "hair_gold": (0.95, 0.8, 0.35, 1),
    "hair_black": (0.06, 0.05, 0.05, 1),
    "hair_gray": (0.55, 0.55, 0.56, 1),
    "white": (0.97, 0.97, 0.95, 1),
    "cream": (0.94, 0.92, 0.85, 1),
    "red": (0.92, 0.16, 0.12, 1),
    "coral": (1.0, 0.42, 0.42, 1),
    "mustard": (1.0, 0.8, 0.0, 1),
    "mint": (0.44, 0.76, 0.7, 1),
    "navy": (0.18, 0.25, 0.34, 1),
    "slate": (0.27, 0.35, 0.44, 1),
    "dark": (0.12, 0.12, 0.15, 1),
    "nose_red": (0.85, 0.2, 0.14, 1),
    "mouth_dark": (0.35, 0.08, 0.07, 1),
    "purple": (0.54, 0.12, 0.42, 1),
    "gold": (1.0, 0.8, 0.0, 1),
    "blush_c": (1.0, 0.6, 0.55, 1),
    "cap_red": (0.92, 0.16, 0.12, 1),
}

VARIANTS = {
    # the reference character: Overcooked chef
    "chef": dict(skin="skin_light", body="red", hair="hair_brown", hat="white",
                 apron=True, nose="nose_red", grin=True, scarf=True),
    # the boss: navy suit, oversized striped tie, golden wave-ridge swoop,
    # orange tan, huge toothy grin, furrowed brows, jowls
    "boss": dict(skin="skin_orange", body="navy", hair="hair_gold", hat=None,
                 tie="red", nose="nose_red", jowl=True, grin="big", suit=True,
                 furrow=True, pin=True),
    # L1 office colleague: coral, bob hair, glasses, lanyard
    "colleague": dict(skin="skin_tan", body="coral", hair="hair_black", hat=None,
                      glasses=True, lanyard=True, smile=True),
    # L2 fast-food customer: mustard, red cap, blush
    "customer": dict(skin="skin_tan", body="mustard", hair="hair_black", hat="cap_red",
                     blush=True, smile=True),
    # L3 complainer: mint, gray hair, glasses
    "complainer": dict(skin="skin_tan", body="mint", hair="hair_gray", hat=None,
                       glasses=True, smile=True),
    # L4 luxury client: navy suit, purple tie
    "client": dict(skin="skin_tan", body="navy", hair="hair_black", hat=None,
                   tie="purple", suit=True, smile=True),
}

# ---------------------------------------------------------------- helpers --
def clear_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def make_mat(name, rgba, rough=0.45):
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = 0.0
    return mat


def prim(kind, name, size, loc, rot=(0, 0, 0), mat=None, smooth=True, subsurf=2):
    """Create a primitive mesh, apply subsurf + material, return the object."""
    if kind == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(segments=28, ring_count=16, radius=1,
                                             location=loc)
    elif kind == "cube":
        bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    elif kind == "cylinder":
        bpy.ops.mesh.primitive_cylinder_add(vertices=28, radius=1, depth=1, location=loc)
    elif kind == "torus":
        bpy.ops.mesh.primitive_torus_add(major_radius=1, minor_radius=0.3,
                                         major_segments=28, minor_segments=12,
                                         location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    obj.rotation_euler = rot
    if subsurf:
        mod = obj.modifiers.new("Subsurf", 'SUBSURF')
        mod.levels = 1
        mod.render_levels = subsurf
    if smooth:
        for p in obj.data.polygons:
            p.use_smooth = True
    if mat:
        obj.data.materials.append(mat)
    return obj


def parent_to(root, child):
    child.parent = root
    child.matrix_parent_inverse = root.matrix_world.inverted()


# ------------------------------------------------------------ character ----
def build_character(kind):
    clear_scene()
    v = VARIANTS[kind]
    root = bpy.data.objects.new(f"NPC_{kind}", None)
    bpy.context.scene.collection.objects.link(root)

    def mat(key):
        return make_mat(f"{kind}_{key}", PALETTE[key])

    skin = mat(v["skin"])
    body_m = mat(v["body"])

    # ---- body: plump rounded torso (Overcooked egg) ----
    prim("sphere", f"{kind}_body", (0.42, 0.34, 0.4), (0, 0, 0.5), mat=body_m)
    # ---- floating mitten hands (no arms, Overcooked style) ----
    hand_m = mat("white") if kind == "chef" else skin
    prim("sphere", f"{kind}_handL", (0.1, 0.1, 0.12), (-0.5, -0.06, 0.55), mat=hand_m)
    prim("sphere", f"{kind}_handR", (0.1, 0.1, 0.12), (0.5, -0.06, 0.55), mat=hand_m)
    # ---- feet ----
    prim("cube", f"{kind}_footL", (0.2, 0.3, 0.12), (-0.16, -0.04, 0.06), mat=mat("dark"))
    prim("cube", f"{kind}_footR", (0.2, 0.3, 0.12), (0.16, -0.04, 0.06), mat=mat("dark"))

    if v.get("suit"):
        # white shirt V + stubby suit arms with white cuffs
        prim("cube", f"{kind}_shirt", (0.22, 0.1, 0.3), (0, -0.3, 0.68), mat=mat("white"))
        for sx in (-1, 1):
            prim("sphere", f"{kind}_arm{sx}", (0.1, 0.1, 0.17), (0.47 * sx, -0.02, 0.5),
                 rot=(0, 0, sx * 0.5), mat=body_m)
            prim("sphere", f"{kind}_cuff{sx}", (0.075, 0.075, 0.075), (0.55 * sx, -0.05, 0.4),
                 mat=mat("white"))
            prim("sphere", f"{kind}_hand{sx}", (0.095, 0.095, 0.11), (0.6 * sx, -0.08, 0.31),
                 mat=skin)
    if kind == "boss":
        # oversized red tie with gold diagonal stripes
        prim("cube", f"{kind}_tie", (0.13, 0.06, 0.55), (0, -0.36, 0.55), mat=mat("red"))
        for i in range(3):
            prim("cube", f"{kind}_stripe{i}", (0.14, 0.07, 0.05),
                 (0, -0.38, 0.68 - i * 0.14), rot=(0, math.radians(38), 0), mat=mat("gold"))
        prim("cube", f"{kind}_flagpin", (0.05, 0.025, 0.035), (-0.12, -0.33, 0.72),
             mat=mat("red"))

    if v.get("apron"):
        apron_m = mat("white") if kind == "chef" else mat("cream")
        prim("cube", f"{kind}_apron", (0.52, 0.12, 0.52), (0, -0.3, 0.48), mat=apron_m)
        for i, bz in enumerate((0.6, 0.42)):
            prim("cylinder", f"{kind}_btn{i}", (0.035, 0.035, 0.03), (0, -0.32, bz),
                 mat=mat("dark"))

    if v.get("scarf"):
        prim("torus", f"{kind}_scarf", (0.26, 0.26, 0.09), (0, 0, 0.86), mat=mat("red"))
        prim("sphere", f"{kind}_scarf_knot", (0.11, 0.08, 0.07), (0, -0.26, 0.8), mat=mat("red"))

    # ---- head: big chibi sphere ----
    prim("sphere", f"{kind}_head", (0.5, 0.46, 0.47), (0, 0, 1.32), mat=skin)
    for sx in (-1, 1):
        prim("sphere", f"{kind}_ear{sx}", (0.09, 0.06, 0.1), (0.47 * sx, 0, 1.3), mat=skin)

    # ---- mouth ----
    if v.get("grin"):
        prim("sphere", f"{kind}_mouth", (0.24, 0.09, 0.14), (0, -0.38, 1.08), mat=mat("mouth_dark"))
        prim("cube", f"{kind}_teeth", (0.3, 0.05, 0.08), (0, -0.44, 1.14), mat=mat("white"))
    elif v.get("grin") == "big":
        prim("sphere", f"{kind}_mouth", (0.26, 0.1, 0.15), (0, -0.4, 1.08), mat=mat("mouth_dark"))
        prim("cube", f"{kind}_teeth", (0.34, 0.06, 0.11), (0, -0.45, 1.15), mat=mat("white"))
        prim("cube", f"{kind}_lip", (0.28, 0.04, 0.05), (0, -0.42, 1.0), mat=skin)
    else:
        prim("sphere", f"{kind}_mouth", (0.1, 0.05, 0.05), (0, -0.44, 1.12), mat=mat("mouth_dark"))

    # ---- nose ----
    nose_m = mat(v["nose"]) if v.get("nose") in PALETTE else skin
    prim("sphere", f"{kind}_nose", (0.1, 0.09, 0.09), (0, -0.44, 1.28), mat=nose_m)

    # ---- eyes: white ovals + dark pupils + highlights ----
    for sx in (-1, 1):
        prim("sphere", f"{kind}_eyeW{sx}", (0.085, 0.06, 0.11), (0.19 * sx, -0.4, 1.44),
             mat=mat("white"))
        prim("sphere", f"{kind}_eyeP{sx}", (0.045, 0.035, 0.045), (0.2 * sx, -0.44, 1.43),
             mat=mat("dark"))
        prim("sphere", f"{kind}_eyeH{sx}", (0.016, 0.014, 0.016), (0.23 * sx, -0.46, 1.46),
             mat=mat("white"))

    # ---- furrowed golden brows ----
    if v.get("furrow"):
        for sx in (-1, 1):
            prim("cube", f"{kind}_brow{sx}", (0.17, 0.05, 0.045), (0.18 * sx, -0.4, 1.54),
                 rot=(0, 0, sx * 0.35), mat=mat("hair_gold"))

    # ---- hair ----
    if v.get("hair"):
        hm = mat(v["hair"])
        if kind == "boss":
            # iconic swoop: dome + forward flip + layered wave ridges
            prim("sphere", f"{kind}_hairDome", (0.47, 0.46, 0.4), (0, 0.05, 1.5), mat=hm)
            prim("sphere", f"{kind}_hairFlip", (0.52, 0.26, 0.2), (0.02, -0.34, 1.6),
                 rot=(-0.45, 0, 0.12), mat=hm)
            for i, off in enumerate((-0.14, 0.0, 0.14, 0.28)):
                ridge = prim("sphere", f"{kind}_hairRidge{i}",
                             (0.44 - i * 0.05, 0.13, 0.11),
                             (off * 0.5, -0.16 + i * 0.03, 1.64 - i * 0.045),
                             rot=(-0.4, 0, off * 0.25), mat=hm)
                del ridge
            for sx in (-1, 1):
                prim("sphere", f"{kind}_hairSide{sx}", (0.15, 0.16, 0.26),
                     (0.45 * sx, 0.02, 1.4), mat=hm)
            prim("sphere", f"{kind}_hairBack", (0.4, 0.32, 0.36), (0, 0.12, 1.36), mat=hm)
        elif kind == "colleague":
            prim("sphere", f"{kind}_hairBob", (0.5, 0.46, 0.3), (0, 0.03, 1.5), mat=hm)
        elif kind == "chef":
            prim("sphere", f"{kind}_hairFront", (0.4, 0.16, 0.18), (0, -0.28, 1.56), mat=hm)
        else:
            prim("sphere", f"{kind}_hairTop", (0.44, 0.42, 0.22), (0, 0.02, 1.6), mat=hm)
            prim("sphere", f"{kind}_hairFront", (0.34, 0.16, 0.14), (0, -0.3, 1.56), mat=hm)

    # ---- headwear ----
    if v.get("hat") == "white":
        prim("cylinder", f"{kind}_hatBand", (0.34, 0.34, 0.18), (0, 0, 1.68), mat=mat("white"))
        prim("sphere", f"{kind}_hatPuffL", (0.3, 0.24, 0.26), (-0.22, 0.0, 1.9), mat=mat("white"))
        prim("sphere", f"{kind}_hatPuffM", (0.32, 0.26, 0.3), (0, -0.06, 2.0), mat=mat("white"))
        prim("sphere", f"{kind}_hatPuffR", (0.3, 0.24, 0.26), (0.22, 0.0, 1.9), mat=mat("white"))
    elif v.get("hat") == "cap_red":
        prim("sphere", f"{kind}_capDome", (0.47, 0.47, 0.3), (0, 0, 1.6), mat=mat("cap_red"))
        prim("cube", f"{kind}_capBrim", (0.4, 0.3, 0.05), (0, -0.4, 1.55), mat=mat("cap_red"))

    # ---- glasses ----
    if v.get("glasses"):
        for sx in (-1, 1):
            prim("torus", f"{kind}_glass{sx}", (0.1, 0.1, 0.018), (0.19 * sx, -0.42, 1.42),
                 mat=mat("slate"), rot=(math.pi / 2, 0, 0))
        prim("cube", f"{kind}_glassBridge", (0.08, 0.02, 0.02), (0, -0.43, 1.43),
             mat=mat("slate"))

    # ---- lanyard + badge ----
    if v.get("lanyard"):
        for sx in (-1, 1):
            prim("cube", f"{kind}_strap{sx}", (0.05, 0.03, 0.26), (0.07 * sx, -0.26, 0.68),
                 rot=(0, 0.2 * sx, 0), mat=mat("slate"))
        prim("cube", f"{kind}_badge", (0.12, 0.03, 0.15), (0, -0.3, 0.5), mat=mat("white"))
        prim("cube", f"{kind}_badgeDot", (0.06, 0.035, 0.03), (0, -0.31, 0.53), mat=mat("red"))

    # ---- blush ----
    if v.get("blush"):
        for sx in (-1, 1):
            prim("sphere", f"{kind}_blush{sx}", (0.07, 0.04, 0.05), (0.3 * sx, -0.34, 1.22),
                 mat=mat("blush_c"))

    # ---- boss jowls ----
    if v.get("jowl"):
        for sx in (-1, 1):
            prim("sphere", f"{kind}_jowl{sx}", (0.12, 0.08, 0.09), (0.16 * sx, -0.3, 1.08),
                 mat=skin)

    # parent everything to the root (head first so reparenting others is simple)
    parent_to(root, bpy.data.objects[f"{kind}_head"])
    for obj in bpy.data.objects:
        if obj.name.startswith(kind):
            parent_to(root, obj)
    return root


# --------------------------------------------------------------- export ----
def export_glb(root, kind):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        if obj.name.startswith(kind) or obj.name == f"NPC_{kind}":
            obj.select_set(True)
    bpy.context.view_layer.objects.active = root
    out = os.path.join(OUT_DIR, f"{kind}.glb")
    os.makedirs(OUT_DIR, exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', use_selection=True,
                              export_apply=True)
    return out


# ---------------------------------------------------------------- render ----
def render_preview(kind):
    scene = bpy.context.scene
    cam_data = bpy.data.cameras.new("PreviewCam")
    cam = bpy.data.objects.new("PreviewCam", cam_data)
    bpy.context.scene.collection.objects.link(cam)
    cam.location = (1.9, -2.6, 1.9)
    cam.rotation_euler = (math.radians(70), 0, math.radians(36))
    scene.camera = cam
    sun_data = bpy.data.lights.new("Sun", 'SUN')
    sun_data.energy = 2.2
    sun_data.color = (1.0, 0.94, 0.83)
    sun = bpy.data.objects.new("Sun", sun_data)
    sun.rotation_euler = (math.radians(50), 0, math.radians(30))
    bpy.context.scene.collection.objects.link(sun)
    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.75, 0.82, 0.9, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.45

    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 24
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 560
    scene.render.resolution_y = 700
    scene.render.filepath = os.path.join(OUT_DIR, f"preview_{kind}.png")
    bpy.ops.render.render(write_still=True)


# ----------------------------------------------------------------- main ----
def main():
    only = os.environ.get("BLENDER_ONLY_KIND")
    kinds = [only] if only else list(VARIANTS)
    for kind in kinds:
        root = build_character(kind)
        out = export_glb(root, kind)
        size = os.path.getsize(out)
        print(f"[builder] exported {kind}: {out} ({size} bytes)")
        if os.environ.get("BLENDER_RENDER"):
            render_preview(kind)
            print(f"[builder] preview: {os.path.join(OUT_DIR, f'preview_{kind}.png')}")


main()
