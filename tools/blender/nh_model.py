"""
Shared helpers for the procedural species models in tools/blender/.

Each species script builds its shells as bmeshes, colours them per vertex with
MeshBuilder.add(), then calls nh_model.run(build, "ModelName"). All colour lives
in vertex colours (the "Col" layer) so the FBX works with the shared
NaturalHistory/MapFeature material, like the other map props.

Conventions (SpeciesColonies relies on them):
  * Blender units, Z up. Animals face -Y (Blender's "front").
  * Ground/water animals: pivot at the lowest point that touches the surface
    (feet, float waterline), so z = 0 sits on the tile.
  * Micro-organisms, fliers and swimmers: pivot at the body centre.
  * Absolute size doesn't matter (SpeciesColonies rescales from the mesh
    bounds) but keep the longest dimension around 1-2 units.
  * Keep it light: roughly 1-5k triangles for small animals, the map shows many of them.
    Large animals (shown bigger, in smaller groups) may use ~15-25k.
  * Organic bodies: build overlapping parts, then MeshBuilder.fuse() them into one
    seamless surface; add crisp details (eyes, teeth, claws) afterwards.

Usage from a species script:
  blender --background --python tools/blender/<species>.py -- [--render out.png]
"""

import math
import sys
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector, Matrix

REPO = Path(__file__).resolve().parents[2]
OUT_DIR = REPO / "Assets" / "Resources" / "Models" / "Species"


def lerp(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(len(a)))


def smoothstep(e0, e1, x):
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


class MeshBuilder:
    """Collects separate shells into one bmesh with per-loop colours."""

    def __init__(self):
        self.bm = bmesh.new()
        self.col = self.bm.loops.layers.color.new("Col")

    def add(self, src, color=None, smooth=True):
        """Append (and free) src. color: rgb tuple, fn(co, normal) -> rgb, or None to keep
        src's own "Col" layer (e.g. the result of fuse())."""
        src.normal_update()
        src_col = src.loops.layers.color.get("Col") if color is None else None
        fn = color if callable(color) else (lambda co, n, c=color: c)
        vmap = {v: self.bm.verts.new(v.co) for v in src.verts}
        for f in src.faces:
            try:
                nf = self.bm.faces.new([vmap[v] for v in f.verts])
            except ValueError:  # duplicate face
                continue
            nf.smooth = smooth
            for loop, sl in zip(nf.loops, f.loops):
                c = sl[src_col] if src_col is not None else fn(sl.vert.co, sl.vert.normal)
                loop[self.col] = (c[0], c[1], c[2], 1.0)
        src.free()

    def fuse(self, voxel=0.015, smooth=6, smooth_factor=0.5, max_tris=None):
        """Merges every shell added so far into ONE seamless surface and returns it as a bmesh
        (this builder is emptied). Use it for organic bodies: add the torso, neck, head, legs,
        tail... as overlapping primitives, fuse() them, then add the fused result plus the
        crisp details (eyes, teeth, claws, whiskers) to a fresh MeshBuilder.

          voxel:  remesh resolution in model units (smaller = more detail, more triangles)
          smooth: Laplacian-ish smoothing passes to soften the voxel steps and blend the joins
          max_tris: decimate down to roughly this many triangles (None = keep everything)

        Colours are copied from the nearest point on the original shells, so paint the parts
        as usual; boundaries between differently coloured parts stay where the parts met (a
        little soft). For crisp markings, repaint the result procedurally instead:
        mb.add(fused, color=lambda co, n: ...)."""
        from mathutils.bvhtree import BVHTree
        src = self.bm
        src.normal_update()
        bmesh.ops.triangulate(src, faces=src.faces)
        col = self.col
        src.faces.ensure_lookup_table()
        tree = BVHTree.FromBMesh(src)  # hit indices follow src.faces order

        mesh = bpy.data.meshes.new("_fuse_src")
        src.to_mesh(mesh)
        obj = bpy.data.objects.new("_fuse_src", mesh)
        bpy.context.scene.collection.objects.link(obj)
        rem = obj.modifiers.new("remesh", "REMESH")
        rem.mode = "VOXEL"
        rem.voxel_size = voxel
        rem.adaptivity = 0.0
        if smooth:
            sm = obj.modifiers.new("smooth", "SMOOTH")
            sm.factor = smooth_factor
            sm.iterations = smooth
        if max_tris:
            dec = obj.modifiers.new("decimate", "DECIMATE")
            dec.decimate_type = "COLLAPSE"
            # ratio is refined below once we know the remeshed triangle count
            dec.ratio = 1.0
        dg = bpy.context.evaluated_depsgraph_get()
        if max_tris:
            obj.modifiers["decimate"].show_viewport = False
            dg.update()
            n = sum(len(p.vertices) - 2 for p in obj.evaluated_get(dg).data.polygons)
            obj.modifiers["decimate"].ratio = min(1.0, max_tris / max(n, 1))
            obj.modifiers["decimate"].show_viewport = True
            dg.update()
        out = bmesh.new()
        out.from_mesh(obj.evaluated_get(dg).to_mesh())
        obj.evaluated_get(dg).to_mesh_clear()
        bpy.data.objects.remove(obj)
        bpy.data.meshes.remove(mesh)

        # colour each new vertex from the nearest original surface point (barycentric blend)
        vert_col = {}
        for v in out.verts:
            hit, _n, idx, _d = tree.find_nearest(v.co)
            if idx is None:
                vert_col[v] = (0.5, 0.5, 0.5)
                continue
            f = src.faces[idx]
            ls = f.loops
            a, b, c = (l.vert.co for l in ls)
            w = _barycentric(hit, a, b, c)
            vert_col[v] = tuple(sum(w[k] * ls[k][col][i] for k in range(3)) for i in range(3))
        out_col = out.loops.layers.color.new("Col")
        for f in out.faces:
            f.smooth = True
            for l in f.loops:
                c = vert_col[l.vert]
                l[out_col] = (c[0], c[1], c[2], 1.0)
        src.free()
        self.bm = bmesh.new()
        self.col = self.bm.loops.layers.color.new("Col")
        return out

    def to_object(self, name, roughness=0.6):
        mesh = bpy.data.meshes.new(name)
        self.bm.normal_update()
        self.bm.to_mesh(mesh)
        self.bm.free()
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.scene.collection.objects.link(obj)

        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        nt = mat.node_tree
        bsdf = nt.nodes.get("Principled BSDF")
        vc = nt.nodes.new("ShaderNodeVertexColor")
        vc.layer_name = "Col"
        nt.links.new(vc.outputs["Color"], bsdf.inputs["Base Color"])
        bsdf.inputs["Roughness"].default_value = roughness
        mesh.materials.append(mat)
        return obj


def _barycentric(p, a, b, c):
    v0, v1, v2 = b - a, c - a, p - a
    d00, d01, d11 = v0.dot(v0), v0.dot(v1), v1.dot(v1)
    d20, d21 = v2.dot(v0), v2.dot(v1)
    den = d00 * d11 - d01 * d01
    if abs(den) < 1e-12:
        return (1.0, 0.0, 0.0)
    v = (d11 * d20 - d01 * d21) / den
    w = (d00 * d21 - d01 * d20) / den
    u = 1.0 - v - w
    # clamp to the triangle and renormalise
    u, v, w = max(u, 0.0), max(v, 0.0), max(w, 0.0)
    t = u + v + w or 1.0
    return (u / t, v / t, w / t)


# ---------------------------------------------------------------- primitives

def transform(bm, matrix):
    bmesh.ops.transform(bm, matrix=matrix, verts=bm.verts)
    return bm


def ellipsoid(center=(0, 0, 0), radii=(1, 1, 1), subdivisions=3, rotation=None, deform=None):
    """Icosphere scaled to radii. deform(v_unit) -> radial multiplier, applied before scaling."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdivisions, radius=1.0)
    for v in bm.verts:
        n = v.co.normalized()
        k = deform(n) if deform else 1.0
        v.co = Vector((n.x * radii[0], n.y * radii[1], n.z * radii[2])) * k
    if rotation is not None:
        transform(bm, rotation.to_4x4() if hasattr(rotation, "to_4x4") else rotation)
    transform(bm, Matrix.Translation(Vector(center)))
    return bm


def uv_ellipsoid(center=(0, 0, 0), radii=(1, 1, 1), segments=16, rings=10, deform=None):
    """UV sphere version (cleaner silhouettes for elongated bodies). deform(v_unit) -> multiplier."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segments, v_segments=rings, radius=1.0)
    for v in bm.verts:
        n = v.co.normalized()
        k = deform(n) if deform else 1.0
        v.co = Vector((n.x * radii[0], n.y * radii[1], n.z * radii[2])) * k
    transform(bm, Matrix.Translation(Vector(center)))
    return bm


def tube(points, radii, sides=8, cap_start=True, cap_end=True, scale_xy=None):
    """Tapered tube through `points` with a radius per point (0 = pointed end).
    scale_xy: optional (sx, sy) to flatten the cross-section (e.g. a flat tail)."""
    bm = bmesh.new()
    pts = [Vector(p) for p in points]
    rings = []
    prev_side = None
    for i, (p, r) in enumerate(zip(pts, radii)):
        if i == 0:
            fwd = (pts[1] - pts[0]).normalized()
        elif i == len(pts) - 1:
            fwd = (pts[-1] - pts[-2]).normalized()
        else:
            fwd = (pts[i + 1] - pts[i - 1]).normalized()
        # parallel-transport a side vector to avoid twisting
        if prev_side is None:
            ref = Vector((0, 0, 1)) if abs(fwd.z) < 0.9 else Vector((1, 0, 0))
            side = fwd.cross(ref).normalized()
        else:
            side = (prev_side - fwd * prev_side.dot(fwd)).normalized()
        prev_side = side
        up = side.cross(fwd).normalized()
        sx, sy = scale_xy if scale_xy else (1.0, 1.0)
        if r <= 1e-6:
            rings.append([bm.verts.new(p)])
            continue
        ring = []
        for k in range(sides):
            a = k / sides * math.tau
            ring.append(bm.verts.new(p + side * math.cos(a) * r * sx + up * math.sin(a) * r * sy))
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        if len(a) == 1 and len(b) == 1:
            continue
        if len(a) == 1:
            for k in range(sides):
                bm.faces.new([a[0], b[k], b[(k + 1) % sides]])
        elif len(b) == 1:
            for k in range(sides):
                bm.faces.new([a[k], a[(k + 1) % sides], b[0]])
        else:
            for k in range(sides):
                j = (k + 1) % sides
                bm.faces.new([a[k], a[j], b[j], b[k]])
    if cap_start and len(rings[0]) > 1:
        bm.faces.new(list(reversed(rings[0])))
    if cap_end and len(rings[-1]) > 1:
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def flat_panel(outline, thickness=0.01):
    """Thin extruded slab from a closed XY outline (list of (x, y, z) points) - wings, fins."""
    bm = bmesh.new()
    top = [bm.verts.new(Vector(p) + Vector((0, 0, thickness * 0.5))) for p in outline]
    bot = [bm.verts.new(Vector(p) - Vector((0, 0, thickness * 0.5))) for p in outline]
    bm.faces.new(top)
    bm.faces.new(list(reversed(bot)))
    n = len(outline)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([top[i], bot[i], bot[j], top[j]])
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def ground_to_zero(obj):
    """Shift the mesh so its lowest vertex sits at z = 0 (pivot on the ground)."""
    zmin = min(v.co.z for v in obj.data.vertices)
    for v in obj.data.vertices:
        v.co.z -= zmin


# ---------------------------------------------------------------- export / preview

def export_fbx(obj, name):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"{name}.fbx"
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.fbx(
        filepath=str(path), use_selection=True,
        apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS",
        axis_forward="-Z", axis_up="Y", bake_space_transform=True,
        mesh_smooth_type="FACE", colors_type="SRGB",
        add_leaf_bones=False, bake_anim=False,
    )
    tris = sum(len(p.vertices) - 2 for p in obj.data.polygons)
    print(f"Exported {path} ({len(obj.data.vertices)} verts, {tris} tris)")
    return tris


def _engine():
    ids = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
    return "BLENDER_EEVEE" if "BLENDER_EEVEE" in ids else "BLENDER_EEVEE_NEXT"


def render_preview(obj, path, background=(0.03, 0.12, 0.16), ground=None,
                   views=((35, 25), (-90, 8)), size=800):
    """Renders `obj` from each (azimuth°, elevation°) view to path_<i>.png.
    ground: optional rgb for a floor plane at z = 0. Azimuth 0 looks at the model's front (-Y)."""
    scene = bpy.context.scene
    scene.render.engine = _engine()
    scene.render.resolution_x = scene.render.resolution_y = size
    world = scene.world or bpy.data.worlds.new("W")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (*background, 1)

    if ground is not None:
        bpy.ops.mesh.primitive_plane_add(size=50, location=(0, 0, 0))
        plane = bpy.context.active_object
        m = bpy.data.materials.new("Ground")
        m.use_nodes = True
        m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*ground, 1)
        plane.data.materials.append(m)

    sun = bpy.data.lights.new("Sun", "SUN")
    sun.energy = 3.0
    so = bpy.data.objects.new("Sun", sun)
    so.rotation_euler = (math.radians(45), math.radians(10), math.radians(-35))
    scene.collection.objects.link(so)

    corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    center = sum(corners, Vector()) / 8
    radius = max((c - center).length for c in corners)
    cam = bpy.data.cameras.new("Cam")
    cam.lens = 50
    co = bpy.data.objects.new("Cam", cam)
    scene.collection.objects.link(co)
    scene.camera = co

    out = Path(path)
    for i, (az, el) in enumerate(views):
        a, e = math.radians(az), math.radians(el)
        d = radius * 2.9
        co.location = center + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * d
        co.rotation_euler = (center - co.location).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = str(out.with_name(f"{out.stem}_{i}.png"))
        bpy.ops.render.render(write_still=True)


def run(build, name, **preview):
    """Factory-reset, build() -> obj, export, and optionally render (--render out.png)."""
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    bpy.ops.wm.read_factory_settings(use_empty=True)
    obj = build()
    export_fbx(obj, name)
    if "--render" in argv:
        render_preview(obj, argv[argv.index("--render") + 1], **preview)
