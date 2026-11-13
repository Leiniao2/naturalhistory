"""
Procedural low-poly Actinophrys sol (sun animalcule) for colony instancing.

A frothy golden cell body with a darker nucleus showing through, a clear
contractile vacuole blister, a couple of food vacuoles, and ~48 needle-thin
axopodia radiating evenly in all directions (each with a few tiny beads).
All colour lives in vertex colours so it works with the shared
NaturalHistory/MapFeature material, like the other map props.

Usage:
  blender --background --python tools/blender/actinophrys_sol.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ActinophrysSol.fbx (loaded at runtime by SpeciesColonies)
Size: body radius 0.5, axopod tips reach ~1.6 from centre (pivot at centre).
"""

import math
import random
import sys
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector, Matrix, noise

REPO = Path(__file__).resolve().parents[2]
OUT_DIR = REPO / "Assets" / "Resources" / "Models" / "Species"
OUT_FBX = OUT_DIR / "ActinophrysSol.fbx"

SEED = 7
BODY_RADIUS = 0.5
AXOPOD_COUNT = 64
AXOPOD_LENGTH = (0.9, 1.2)   # beyond the body surface
AXOPOD_BASE_RADIUS = 0.016

# Palette (linear-ish sRGB values, written straight to vertex colours)
BODY_OUTER = (0.93, 0.80, 0.48)  # pale gold ectoplasm
BODY_FOAM = (1.00, 0.93, 0.70)   # bright vacuole froth
BODY_SHADOW = (0.55, 0.36, 0.14) # darker amber between bubbles
AXO_BASE = (0.98, 0.90, 0.66)
AXO_TIP = (0.85, 0.93, 0.95)     # cool, glassy tips
BEAD = (1.00, 0.97, 0.85)
VACUOLE = (0.70, 0.88, 0.95)
FOOD = (0.45, 0.55, 0.25)


def fibonacci_sphere(n, rng):
    pts = []
    golden = math.pi * (3.0 - math.sqrt(5.0))
    for i in range(n):
        y = 1.0 - (i + 0.5) / n * 2.0
        r = math.sqrt(1.0 - y * y)
        theta = golden * i
        v = Vector((math.cos(theta) * r, y, math.sin(theta) * r))
        # slight jitter so it doesn't look machine-made
        v += Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1))) * 0.06
        pts.append(v.normalized())
    return pts


def lerp(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


class MeshBuilder:
    """Collects separate shells into one bmesh with per-loop colours."""

    def __init__(self):
        self.bm = bmesh.new()
        self.col = self.bm.loops.layers.color.new("Col")

    def add_bmesh(self, src, color_fn):
        """Append src bmesh; color_fn(world_co, normal) -> rgb per vertex."""
        vmap = {}
        for v in src.verts:
            nv = self.bm.verts.new(v.co)
            vmap[v] = nv
        for f in src.faces:
            nf = self.bm.faces.new([vmap[v] for v in f.verts])
            nf.smooth = f.smooth
            for loop, sl in zip(nf.loops, f.loops):
                c = color_fn(sl.vert.co, sl.vert.normal)
                loop[self.col] = (c[0], c[1], c[2], 1.0)
        src.free()


def make_body(rng):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=BODY_RADIUS)
    # Frothy, slightly irregular surface: low-frequency wobble + bubbly cells.
    for v in bm.verts:
        n = v.co.normalized()
        wobble = noise.noise(n * 1.6 + Vector((3.1, 0.2, 1.7))) * 0.05
        cells = noise.cell(n * 3.0)  # 0 at cell centres -> soft domes
        bump = (1.0 - min(cells, 1.0)) * 0.02
        v.co = n * (BODY_RADIUS + wobble + bump)
    bm.normal_update()
    for f in bm.faces:
        f.smooth = True

    def color(co, normal):
        n = co.normalized()
        c = noise.cell(n * 5.0)
        froth = max(0.0, 1.0 - c * 1.4)            # bright bubble centres
        base = lerp(BODY_OUTER, BODY_SHADOW, min(1.0, c * 1.2) ** 2)
        return lerp(base, BODY_FOAM, froth * 0.8)

    return bm, color


def make_blister(center_dir, radius, rgb, depth=0.75, subdivisions=2):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdivisions, radius=radius)
    for f in bm.faces:
        f.smooth = True
    pos = center_dir.normalized() * BODY_RADIUS * (1.0 + radius * depth)
    bmesh.ops.translate(bm, verts=bm.verts, vec=pos)
    bm.normal_update()
    return bm, (lambda co, n: rgb)


def make_axopod(direction, length, rng):
    """Tapered 4-sided needle from inside the body out to a point, plus beads."""
    bm = bmesh.new()
    sides = 4
    start = BODY_RADIUS * 0.85
    end = BODY_RADIUS + length
    # build in local Z then rotate onto direction
    rot = direction.to_track_quat("Z", "Y").to_matrix().to_4x4()
    twist = Matrix.Rotation(rng.uniform(0, math.pi), 4, "Z")
    xf = rot @ twist

    # slight curve: tips droop sideways a touch
    bend_axis = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), 0)).normalized()
    bend = rng.uniform(0.0, 0.06)

    rings = [(start, AXOPOD_BASE_RADIUS * 1.2),
             (BODY_RADIUS + length * 0.15, AXOPOD_BASE_RADIUS),
             (BODY_RADIUS + length * 0.6, AXOPOD_BASE_RADIUS * 0.55)]
    ring_verts = []
    for z, r in rings:
        t = (z - start) / (end - start)
        off = bend_axis * bend * t * t
        ring = []
        for i in range(sides):
            a = i / sides * math.tau
            p = Vector((math.cos(a) * r + off.x, math.sin(a) * r + off.y, z))
            ring.append(bm.verts.new(xf @ p))
        ring_verts.append(ring)
    tip_off = bend_axis * bend
    tip = bm.verts.new(xf @ Vector((tip_off.x, tip_off.y, end)))

    for a, b in zip(ring_verts, ring_verts[1:]):
        for i in range(sides):
            j = (i + 1) % sides
            bm.faces.new([a[i], a[j], b[j], b[i]])
    last = ring_verts[-1]
    for i in range(sides):
        bm.faces.new([last[i], last[(i + 1) % sides], tip])
    for f in bm.faces:
        f.smooth = True

    # Extrusome beads (tiny octahedra) strung along the axopod
    bead_ts = sorted(rng.uniform(0.25, 0.85) for _ in range(rng.randint(0, 2)))
    for t in bead_ts:
        z = BODY_RADIUS + length * t
        r_ax = AXOPOD_BASE_RADIUS * (1.0 - 0.5 * t)
        br = r_ax * 1.9
        off = bend_axis * bend * ((z - start) / (end - start)) ** 2
        c = Vector((off.x, off.y, z))
        pts = [c + Vector(d) * br for d in
               ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1.6), (0, 0, -1.6))]
        vs = [bm.verts.new(xf @ p) for p in pts]
        px, nx, py, ny, pz, nz = vs
        for a, b in ((px, py), (py, nx), (nx, ny), (ny, px)):
            bm.faces.new([a, b, pz])
            bm.faces.new([b, a, nz])

    bm.normal_update()
    inner = start
    total = end - start

    def color(co, n):
        d = co.length
        if d < BODY_RADIUS * 1.0:
            return AXO_BASE
        t = min(1.0, (d - inner) / total)
        return lerp(AXO_BASE, AXO_TIP, t ** 0.8)

    return bm, color


def build():
    rng = random.Random(SEED)
    random.seed(SEED)
    mb = MeshBuilder()

    body, body_col = make_body(rng)
    mb.add_bmesh(body, body_col)

    # contractile vacuole: one clear blister; food vacuoles: two greenish lumps
    mb.add_bmesh(*make_blister(Vector((0.55, 0.35, 0.75)), 0.16, VACUOLE, depth=0.2))
    mb.add_bmesh(*make_blister(Vector((-0.7, -0.2, 0.5)), 0.09, FOOD, depth=-0.2))
    mb.add_bmesh(*make_blister(Vector((-0.1, -0.8, -0.4)), 0.07, FOOD, depth=-0.2))

    # small half-sunk bubbles give the vacuolated, foamy outline
    for d in fibonacci_sphere(18, rng):
        r = rng.uniform(0.05, 0.085)
        mb.add_bmesh(*make_blister(d, r, lerp(BODY_FOAM, BODY_OUTER, rng.random() * 0.5),
                                   depth=-0.3, subdivisions=1))

    for d in fibonacci_sphere(AXOPOD_COUNT, rng):
        length = rng.uniform(*AXOPOD_LENGTH)
        mb.add_bmesh(*make_axopod(d, length, rng))

    mesh = bpy.data.meshes.new("ActinophrysSol")
    mb.bm.to_mesh(mesh)
    mb.bm.free()

    obj = bpy.data.objects.new("ActinophrysSol", mesh)
    bpy.context.scene.collection.objects.link(obj)

    mat = bpy.data.materials.new("ActinophrysSol")
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    vc = nt.nodes.new("ShaderNodeVertexColor")
    vc.layer_name = "Col"
    nt.links.new(vc.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.35
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.25
        bsdf.inputs["Subsurface Radius"].default_value = (0.3, 0.2, 0.1)
    mesh.materials.append(mat)
    return obj


def export(obj):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.fbx(
        filepath=str(OUT_FBX),
        use_selection=True,
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_UNITS",
        axis_forward="-Z",
        axis_up="Y",
        bake_space_transform=True,
        mesh_smooth_type="FACE",
        colors_type="SRGB",
        add_leaf_bones=False,
        bake_anim=False,
    )
    tris = sum(len(p.vertices) - 2 for p in obj.data.polygons)
    print(f"Exported {OUT_FBX} ({len(obj.data.vertices)} verts, {tris} tris)")


def render_preview(obj, path, colony=False):
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in \
        [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] \
        else "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 900
    scene.render.resolution_y = 900
    scene.render.film_transparent = False
    world = bpy.data.worlds.new("W") if not scene.world else scene.world
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.03, 0.12, 0.16, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0

    if colony:
        rng = random.Random(3)
        for i in range(9):
            dup = obj.copy()
            scene.collection.objects.link(dup)
            dup.location = (rng.uniform(-2.5, 2.5), rng.uniform(-2.5, 2.5), rng.uniform(-0.3, 0.3))
            s = rng.uniform(0.75, 1.15)
            dup.scale = (s, s, s)
            dup.rotation_euler = (rng.uniform(0, 6.3), rng.uniform(0, 6.3), rng.uniform(0, 6.3))

    sun = bpy.data.lights.new("Sun", "SUN")
    sun.energy = 3.0
    so = bpy.data.objects.new("Sun", sun)
    so.rotation_euler = (math.radians(50), math.radians(10), math.radians(30))
    scene.collection.objects.link(so)

    cam = bpy.data.cameras.new("Cam")
    co = bpy.data.objects.new("Cam", cam)
    scene.collection.objects.link(co)
    dist = 13.0 if colony else 5.2
    co.location = (dist * 0.55, -dist * 0.75, dist * 0.6)
    target = Vector((0, 0, 0))
    co.rotation_euler = (target - co.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = co
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    bpy.ops.wm.read_factory_settings(use_empty=True)
    obj = build()
    export(obj)
    if "--render" in argv:
        out = Path(argv[argv.index("--render") + 1])
        render_preview(obj, out)
        if "--colony" in argv:
            render_preview(obj, out.with_name(out.stem + "_colony.png"), colony=True)


if __name__ == "__main__":
    main()
