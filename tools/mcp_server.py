"""FastMCP server: You're Fired! character forge.

Wraps character-creation backends as MCP tools so any MCP client (Claude, etc.)
can design, generate, and install polished chibi 3D characters into the game.

Backends:
  1. `design_character`   — deterministic procedural chibi builder (trimesh -> GLB,
                            PBR materials, zero network, CC0 output)
  2. `hf_space_generate`  — Hugging Face Gradio Space route (TripoSR / Unique3D
                            image-to-3D). Anonymous Spaces enforce GPU quotas and
                            may raise upstream errors; the tool reports them and
                            the caller can fall back to `design_character`.

Run:   fastmcp run tools/mcp_server.py     (or import as a stdio server)
Game:  assets/<name>.glb files are picked up by ASSET_MANIFEST in index.html.
"""
import os
import shutil

from fastmcp import FastMCP

mcp = FastMCP("youre-fired-character-forge")

GAME_DIR = os.environ.get(
    "GAME_DIR",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
)
CHAR_DIR = os.path.join(GAME_DIR, "assets", "characters")
os.makedirs(CHAR_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# procedural chibi builder (trimesh -> GLB)
# ---------------------------------------------------------------------------
def _build_character(spec):
    import trimesh

    def sphere(r):
        return trimesh.creation.icosphere(subdivisions=2, radius=r)

    def capsule(r, h):
        return trimesh.creation.capsule(radius=r, height=h)

    def box(w, h, d):
        return trimesh.creation.box(extents=[w, h, d])

    def PBR(rgb):
        return trimesh.visual.material.PBRMaterial(
            baseColorFactor=[rgb[0] / 255, rgb[1] / 255, rgb[2] / 255, 1.0],
            metallicFactor=0.0,
            roughnessFactor=0.43,
        )

    scene = trimesh.Scene()

    def add(geom, pos, rgb, name):
        g = geom.copy()
        g.apply_translation(pos)
        g.visual = trimesh.visual.TextureVisuals(material=PBR(rgb))
        scene.add_geometry(g, node_name=name, geom_name=name)

    skin = spec.get("skin", (238, 156, 80))
    pants = spec.get("pants", (34, 37, 43))
    shoes = spec.get("shoe", (35, 37, 46))
    add(sphere(0.42), [0, 1.05, 0], skin, "head")
    if spec.get("hair"):
        add(sphere(0.43), [0, 1.2, -0.04], spec["hair"], "hair_dome")
        add(box(0.52, 0.16, 0.3), [0, 1.3, 0.18], spec["hair"], "hair_swoop")
    if spec.get("cap"):
        add(sphere(0.435), [0, 1.24, 0], spec["cap"], "cap_dome")
        add(box(0.4, 0.05, 0.26), [0, 1.12, 0.28], spec["cap"], "cap_brim")
    add(box(0.22, 0.5, 0.24), [0, 0.42, 0], spec.get("shirt", (255, 122, 89)), "torso")
    if spec.get("tie"):
        add(box(0.1, 0.42, 0.05), [0, 0.42, 0.14], (255, 255, 255), "shirt")
        add(box(0.08, 0.44, 0.045), [0, 0.34, 0.15], spec["tie"], "tie_long")
    if spec.get("apron"):
        add(box(0.24, 0.4, 0.05), [0, 0.36, 0.15], spec["apron"], "apron")
    for sx in (-1, 1):
        add(capsule(0.09, 0.3), [0.36 * sx, 0.42, 0], spec.get("shirt", (255, 122, 89)), f"arm{sx}")
        add(sphere(0.11), [0.36 * sx, 0.2, 0], skin, f"hand{sx}")
        add(capsule(0.1, 0.22), [0.14 * sx, 0.11, 0], pants, f"leg{sx}")
        add(box(0.2, 0.09, 0.32), [0.14 * sx, 0.045, 0.05], shoes, f"shoe{sx}")
    if spec.get("glasses"):
        for sx in (-1, 1):
            add(trimesh.creation.torus(major_radius=0.085, minor_radius=0.014),
                [0.14 * sx, 1.1, 0.36], (46, 64, 87), f"glass{sx}")
    if spec.get("jowl"):
        j = sphere(0.2)
        j.apply_scale([1.6, 0.62, 0.85])
        add(j, [0, 0.86, 0.28], skin, "jowl")
    return scene


CHAR_SPECS = {
    "boss": {
        "skin": (238, 156, 80), "hair": (243, 207, 107), "shirt": (38, 43, 61),
        "pants": (34, 37, 43), "shoe": (35, 37, 46), "tie": (214, 60, 46), "jowl": True,
    },
    "colleague": {
        "skin": (232, 180, 140), "hair": (26, 18, 12), "shirt": (255, 107, 107),
        "pants": (46, 64, 87), "shoe": (35, 37, 46), "glasses": True,
    },
    "customer": {
        "skin": (242, 193, 154), "hair": (61, 44, 26), "shirt": (255, 204, 0),
        "pants": (91, 70, 50), "shoe": (35, 37, 46), "cap": (255, 59, 48),
    },
    "complainer": {
        "skin": (217, 168, 108), "hair": (17, 17, 17), "shirt": (112, 193, 179),
        "pants": (57, 64, 75), "shoe": (35, 37, 46), "glasses": True,
    },
    "client": {
        "skin": (232, 180, 140), "hair": (58, 58, 58), "shirt": (44, 49, 64),
        "pants": (34, 37, 43), "shoe": (35, 37, 46), "tie": (138, 31, 107),
    },
}


# ---------------------------------------------------------------------------
# tools
# ---------------------------------------------------------------------------
@mcp.tool
def list_characters() -> dict:
    """List generated/installed character GLB files."""
    out = {}
    for sub in ("", "characters"):
        d = os.path.join(GAME_DIR, "assets", sub)
        if os.path.isdir(d):
            for f in sorted(os.listdir(d)):
                if f.endswith(".glb"):
                    p = os.path.join(d, f)
                    out[os.path.relpath(p, GAME_DIR)] = os.path.getsize(p)
    return {"game_dir": GAME_DIR, "files": out}


@mcp.tool
def design_character(kind: str, name: str) -> dict:
    """Build a chibi character GLB locally with trimesh (CC0, deterministic).

    kind: boss | colleague | customer | complainer | client
    name: output file stem, e.g. 'boss_figurine'
    """
    if kind not in CHAR_SPECS:
        return {"ok": False, "error": f"unknown kind '{kind}'", "kinds": sorted(CHAR_SPECS)}
    import trimesh

    path = os.path.join(CHAR_DIR, f"{name}.glb")
    scene = _build_character(CHAR_SPECS[kind])
    data = scene.export(file_type="glb")
    with open(path, "wb") as f:
        f.write(data)
    return {"ok": True, "path": path, "bytes": len(data),
            "parts": len(scene.geometry), "kind": kind}


@mcp.tool
def hf_space_generate(image_path: str, name: str, space: str = "Wuvin/Unique3D") -> dict:
    """Generate a GLB from an image via a Hugging Face Gradio Space.

    NOTE: anonymous Space calls are quota-limited and may raise upstream
    errors — fall back to `design_character` when they do.
    space: Wuvin/Unique3D | stabilityai/TripoSR
    """
    from gradio_client import Client
    import warnings

    warnings.filterwarnings("ignore")
    if not os.path.isfile(image_path):
        return {"ok": False, "error": f"image not found: {image_path}"}
    try:
        c = Client(space, verbose=False)
        if space == "Wuvin/Unique3D":
            out = c.predict(image_path, True, 0, False, False, 0.1, "std",
                            api_name="/generate3dv2")
            src = out[0]
        else:  # TripoSR
            pre = c.predict(image_path, True, 0.9, api_name="/preprocess")
            out = c.predict(pre, 256, api_name="/generate")
            src = out[1]
        path = os.path.join(CHAR_DIR, f"{name}.glb")
        shutil.copy(src, path)
        return {"ok": True, "path": path, "bytes": os.path.getsize(path), "space": space}
    except Exception as e:
        return {"ok": False, "error": str(e).split("\n")[0][:200],
                "hint": "anonymous Space quota / runtime issue — use design_character instead"}


@mcp.tool
def install_character(name: str, manifest_name: str) -> dict:
    """Install a generated character into the game as assets/<manifest_name>.glb.

    After installing, set the matching ASSET_MANIFEST entry `enabled: true`
    (or add a manifest entry) in index.html and reload the game.
    """
    src = os.path.join(CHAR_DIR, f"{name}.glb")
    if not os.path.isfile(src):
        return {"ok": False, "error": f"not generated yet: {src}"}
    dst = os.path.join(GAME_DIR, "assets", f"{manifest_name}.glb")
    shutil.copy(src, dst)
    return {"ok": True, "installed": dst, "bytes": os.path.getsize(dst),
            "manifest_entry": f"{manifest_name}: {{ url: 'assets/{manifest_name}.glb' }}"}


if __name__ == "__main__":
    mcp.run()
