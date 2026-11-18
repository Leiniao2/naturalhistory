"""
Procedural low-poly Entamoeba histolytica trophozoite, the amoeba of amoebic dysentery.

An irregular, flattened amoeboid cell crawling toward -Y on one broad, rounded pseudopod of clear,
glassy ectoplasm; the rest of the cell is granular grey-lavender endoplasm with a few lumpy
bulges and a blunt trailing uroid. Through the upper surface show the round nucleus (pale, with a
beaded rim of peripheral chromatin and a small central karyosome dot) and four ingested red blood
cells, small red biconcave discs each in its own pale food vacuole: the tell-tale sign of the
invasive form. Colour is in vertex colours (see nh_model).

Usage:
  blender --background --python tools/blender/entamoeba_histolytica.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Entamoeba.fbx
About 1.6 units across, ~0.4 thick. Faces -Y (the pseudopod leads). Pivot at the cell centre (Drift).
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bmesh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Matrix, Vector, noise  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

import nh_model as nh  # noqa: E402

SEED = 5
RADIUS = 0.56          # mean outline radius of the cell body
THICK = 0.20           # half-thickness of the endoplasm mass
LOBE_DIR = math.radians(-100)   # the advancing pseudopod, a little to the left of -Y
LOBE = 0.40            # how far the pseudopod reaches beyond the body
LOBE_WIDTH = 0.95      # angular half-width (radians) of the broad lobe
TARGET_TRIS = 1300     # the cell surface is decimated to about this

ENDO = (0.58, 0.52, 0.70)
GRANULE = (0.40, 0.35, 0.52)
ECTO = (0.86, 0.91, 0.95)
NUC = (0.80, 0.78, 0.86)
CHROMATIN = (0.30, 0.26, 0.40)
VACUOLE = (0.82, 0.76, 0.86)
RBC = (0.80, 0.12, 0.12)
RBC_DIMPLE = (0.60, 0.07, 0.08)

# (x, y) of the nucleus and the food vacuoles holding red cells
NUC_AT = (0.10, 0.08)
RBC_AT = [(-0.26, 0.02), (0.30, -0.16), (-0.08, 0.34), (0.32, 0.30)]


def angdiff(a, b):
    return math.atan2(math.sin(a - b), math.cos(a - b))


def lobe(a):
    """0..1 how far into the advancing pseudopod a direction a (radians, in XY) points."""
    return math.exp(-abs(angdiff(a, LOBE_DIR) / LOBE_WIDTH) ** 3 * 1.6)


def outline(a):
    r = RADIUS * (1.0 + 0.12 * noise.noise(Vector((math.cos(a) * 1.8, math.sin(a) * 1.8, 3.3))))
    r += 0.10 * math.exp(-(angdiff(a, math.radians(20)) / 0.30) ** 2)    # small side bulges
    r += 0.08 * math.exp(-(angdiff(a, math.radians(170)) / 0.25) ** 2)
    r += 0.09 * math.exp(-(angdiff(a, math.radians(80)) / 0.22) ** 2)    # blunt trailing uroid
    r -= 0.07 * math.exp(-(angdiff(a, math.radians(130)) / 0.2) ** 2)    # a notch beside it
    lb = lobe(a)
    # the advancing edge is broad and gently scalloped
    return r + LOBE * lb * (1.0 + 0.10 * math.sin(a * 9.0 + 2.2))


def make_cell():
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=5, radius=1.0)
    for v in bm.verts:
        n = v.co.normalized()
        a = math.atan2(n.y, n.x)
        h = math.hypot(n.x, n.y)
        r = outline(a)
        lb = lobe(a)
        # the endoplasm mass is thick in the middle; the hyaline pseudopod thins to a flat sheet
        thick = THICK * (1.0 - 0.45 * lb * h ** 2)
        z = n.z * thick * (1.0 + 0.08 * noise.noise(Vector((n.x * 3, n.y * 3, 1.7))))
        z += 0.03 * (1 - h ** 2) * (1 - lb)    # slight dome
        v.co = Vector((n.x * r, n.y * r, z))
    bm = decimate(bm, TARGET_TRIS)

    def color(co, nrm):
        a = math.atan2(co.y, co.x)
        rad = math.hypot(co.x, co.y) / outline(a)
        grain = noise.noise(co * 26.0)
        c = nh.lerp(ENDO, GRANULE, nh.smoothstep(0.05, 0.5, grain) * 0.8)
        stream = noise.noise(Vector((co.x * 4, co.y * 4, co.z)) + Vector((4.0, 1.0, 2.0)))
        c = nh.lerp(c, GRANULE, max(0.0, stream) * 0.35)
        # clear ectoplasm: the whole advancing lobe, plus a thin glassy rim round the cell
        body_edge = RADIUS * (0.92 + 0.12 * noise.noise(co * 4.0 + Vector((0.5, 2.0, 0.0)))) / outline(a)
        ecto = lobe(a) * nh.smoothstep(body_edge - 0.05, body_edge + 0.05, rad)
        ecto = max(ecto, nh.smoothstep(0.86, 0.98, rad) * 0.85)
        return nh.lerp(c, ECTO, min(1.0, ecto))

    return bm, color


def decimate(bm, tris):
    """Collapse-decimates bm to about `tris` triangles (via a temporary object)."""
    mesh = bpy.data.meshes.new("_dec")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("_dec", mesh)
    bpy.context.scene.collection.objects.link(obj)
    mod = obj.modifiers.new("dec", "DECIMATE")
    mod.ratio = tris / sum(len(p.vertices) - 2 for p in mesh.polygons)
    dg = bpy.context.evaluated_depsgraph_get()
    out = bmesh.new()
    out.from_mesh(obj.evaluated_get(dg).to_mesh())
    obj.evaluated_get(dg).to_mesh_clear()
    bpy.data.objects.remove(obj)
    bpy.data.meshes.remove(mesh)
    out.normal_update()
    return out


def biconcave(radius, thick):
    """A red blood cell: a disc with a thick rim and a dimpled middle, lying in XY."""
    bm = nh.uv_ellipsoid((0, 0, 0), (radius, radius, thick), segments=12, rings=7)
    for v in bm.verts:
        s = math.hypot(v.co.x, v.co.y) / radius
        v.co.z *= 0.35 + 0.65 * s ** 2 + 0.3 * math.sin(math.pi * s)
    return bm


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()
    cell, cell_col = make_cell()
    cell.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(cell)

    def top(x, y):
        hit = tree.ray_cast(Vector((x, y, 1.0)), Vector((0, 0, -1)))
        return hit[0].z if hit[0] is not None else 0.0

    mb.add(cell, cell_col)

    # nucleus: a pale disc with a beaded dark rim and a dot of karyosome in the middle
    nx, ny = NUC_AT
    nr = 0.13
    nz = top(nx, ny)

    def nuc_col(co, n):
        d = math.hypot(co.x - nx, co.y - ny) / nr
        c = nh.lerp(NUC, CHROMATIN, nh.smoothstep(0.62, 0.8, d) * (0.7 + 0.3 * math.cos(
            9 * math.atan2(co.y - ny, co.x - nx))))
        return nh.lerp(c, CHROMATIN, 1 - nh.smoothstep(0.16, 0.24, d))

    mb.add(nh.uv_ellipsoid((nx, ny, nz - 0.02), (nr, nr, 0.055), segments=20, rings=10), nuc_col)

    # ingested red cells, each in a pale food vacuole, tilted at random
    for x, y in RBC_AT:
        z = top(x, y)
        vr = rng.uniform(0.108, 0.118)
        mb.add(nh.uv_ellipsoid((x, y, z - vr * 0.3), (vr, vr, vr * 0.5), segments=12, rings=6), VACUOLE)
        disc = biconcave(0.078, 0.028)
        nh.transform(disc, Matrix.Translation(Vector((x, y, z + 0.015)))
                     @ Matrix.Rotation(rng.uniform(0, math.tau), 4, "Z")
                     @ Matrix.Rotation(rng.uniform(0.1, 0.3), 4, "X"))

        def rbc_col(co, n, x=x, y=y):
            d = math.hypot(co.x - x, co.y - y) / 0.078
            return nh.lerp(RBC_DIMPLE, RBC, nh.smoothstep(0.25, 0.65, d))

        mb.add(disc, rbc_col)

    # a few darker granules and small vacuoles in the endoplasm
    placed = 0
    while placed < 14:
        x, y = rng.uniform(-0.5, 0.5), rng.uniform(-0.4, 0.5)
        if math.hypot(x, y) > 0.45 or min(math.hypot(x - a, y - b) for a, b in RBC_AT + [NUC_AT]) < 0.17:
            continue
        r = rng.uniform(0.022, 0.036)
        mb.add(nh.ellipsoid((x, y, top(x, y) - r * 0.5), (r, r, r * 0.8), subdivisions=0),
               rng.choice([GRANULE, (0.76, 0.72, 0.82)]))
        placed += 1

    return mb.to_object("Entamoeba", roughness=0.4)


if __name__ == "__main__":
    nh.run(build, "Entamoeba", views=((35, 35), (0, 80), (-110, 12)))
