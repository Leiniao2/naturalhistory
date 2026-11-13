"""
Procedural low-poly Amoeba proteus for colony instancing.

One fluid, flattened cell: the outline is the outermost surface of a smooth
union of a lumpy body and a handful of blunt, slightly curving pseudopods
(signed-distance shapes), found by sphere-tracing inwards from a dense
icosphere and then decimated to budget. Granular blue-grey endoplasm fades to
a clear ectoplasm rim at the pseudopod tips; a discoid nucleus, food vacuoles
and a contractile vacuole bulge just through the upper surface so they read
with an opaque material.

Usage:
  blender --background --python tools/blender/amoeba.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Amoeba.fbx
Size: ~2 units across, ~0.4 thick; pivot at the body centre.
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402

import bpy  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Matrix, Vector, noise  # noqa: E402

SEED = 11
TARGET_TRIS = 2500

BODY_RADII = Vector((0.36, 0.33, 0.19))
BLEND = 0.12  # smooth-union radius between body and pseudopods

# Pseudopods as top-down polylines of (x, y, radius); the cell crawls toward -Y.
# Some branch off others so the outline stays irregular rather than star-like.
PSEUDOPODS = [
    [(0.00, -0.15, 0.17), (0.05, -0.52, 0.145), (-0.02, -0.80, 0.135)],  # leading lobe
    [(0.05, -0.46, 0.11), (0.25, -0.62, 0.10), (0.36, -0.70, 0.10)],     # branch off the leader
    [(-0.18, -0.12, 0.14), (-0.44, -0.30, 0.115), (-0.60, -0.34, 0.11)],
    [(0.18, 0.00, 0.13), (0.48, -0.05, 0.11), (0.64, 0.03, 0.105)],
    [(-0.20, 0.10, 0.13), (-0.44, 0.19, 0.115)],
    [(0.14, 0.20, 0.11), (0.31, 0.38, 0.09), (0.36, 0.52, 0.09)],
    [(-0.02, 0.22, 0.15), (-0.06, 0.42, 0.135)],                           # blunt trailing uroid
]

ENDOPLASM = (0.42, 0.50, 0.56)
GRANULE = (0.27, 0.32, 0.37)
ECTOPLASM = (0.80, 0.88, 0.92)
NUCLEUS = (0.40, 0.40, 0.48)
FOOD = [(0.40, 0.50, 0.20), (0.52, 0.42, 0.22), (0.34, 0.46, 0.26)]
CONTRACTILE = (0.74, 0.90, 0.97)
CRYSTAL = [(0.86, 0.88, 0.84), (0.32, 0.36, 0.40)]


def smin(a, b, k):
    h = max(k - abs(a - b), 0.0) / k
    return min(a, b) - h * h * k * 0.25


def sd_ellipsoid(p, r):
    q = Vector((p.x / r.x, p.y / r.y, p.z / r.z))
    return (q.length - 1.0) * min(r)


def sd_capsule(p, a, b, r):
    pa, ba = p - a, b - a
    h = max(0.0, min(1.0, pa.dot(ba) / ba.dot(ba)))
    return (pa - ba * h).length - r


def build_pseudopods():
    """Tapered capsule segments (a, b, radius_a, radius_b); tips droop slightly onto the substrate."""
    segs = []
    for pod in PSEUDOPODS:
        pts = [(Vector((x, y, -0.03 * i)), r) for i, (x, y, r) in enumerate(pod)]
        for (a, ra), (b, rb) in zip(pts, pts[1:]):
            segs.append((a, b, ra, rb))
    return segs


SEGMENTS = build_pseudopods()


def sdf(p):
    wob = noise.noise(p * 3.0 + Vector((5.2, 1.3, 0.7))) * 0.035
    d = sd_ellipsoid(p, BODY_RADII) + wob
    for a, b, ra, rb in SEGMENTS:
        # flatten pseudopods vertically like the body
        q = Vector((p.x, p.y, p.z * 1.5))
        ab = b - a
        h = max(0.0, min(1.0, (q - a).dot(ab) / ab.dot(ab)))
        r = ra + (rb - ra) * h
        d = smin(d, ((q - a) - ab * h).length / 1.2 - r / 1.2, BLEND)
    return d


def ray_surface(direction, start=2.2):
    """Outermost surface point along `direction` from the origin (sphere-trace inwards)."""
    t = start
    for _ in range(200):
        d = sdf(direction * t)
        if d < 0.0015:
            break
        t -= max(d * 0.8, 0.002)
        if t <= 0.01:
            break
    return direction * t


def top_height(x, y):
    """z of the upper surface above (x, y)."""
    z = 1.0
    for _ in range(120):
        d = sdf(Vector((x, y, z)))
        if d < 0.001:
            break
        z -= max(d * 0.8, 0.001)
    return z


def pod_extent(co):
    """0 inside the main body, rising toward 1 at the pseudopod tips."""
    q = Vector((co.x / BODY_RADII.x, co.y / BODY_RADII.y, 0.0))
    return nh.smoothstep(1.1, 2.5, q.length)


def make_cell():
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=5, radius=1.0)
    for v in bm.verts:
        v.co = ray_surface(v.co.normalized())
    bm.normal_update()

    # decimate to budget with a temporary object, then take the evaluated mesh back
    mesh = bpy.data.meshes.new("tmp")
    bm.to_mesh(mesh)
    bm.free()
    tmp = bpy.data.objects.new("tmp", mesh)
    bpy.context.scene.collection.objects.link(tmp)
    mod = tmp.modifiers.new("dec", "DECIMATE")
    mod.ratio = TARGET_TRIS / len(mesh.polygons)
    dg = bpy.context.evaluated_depsgraph_get()
    out = bmesh.new()
    out.from_mesh(tmp.evaluated_get(dg).to_mesh())
    bpy.data.objects.remove(tmp)
    bpy.data.meshes.remove(mesh)

    def color(co, n):
        grain = noise.noise(co * 22.0)
        col = nh.lerp(ENDOPLASM, GRANULE, nh.smoothstep(0.1, 0.5, grain) * 0.7)
        # streaming bands of denser granules flowing toward the pseudopods
        stream = noise.noise(Vector((co.x * 4.0, co.y * 2.5, co.z)) + Vector((2.0, 7.0, 1.0)))
        col = nh.lerp(col, GRANULE, max(0.0, stream) * 0.4)
        # clear hyaline ectoplasm at the pseudopod tips and around the lower rim
        rim = max(pod_extent(co) * 1.15, nh.smoothstep(0.7, 1.0, 1.0 - abs(n.z)) * 0.3)
        return nh.lerp(col, ECTOPLASM, min(1.0, rim))

    return out, color


def blister(x, y, radii, rgb, sink=0.55, subdivisions=2):
    """Flattened sphere poking through the upper surface at (x, y)."""
    z = top_height(x, y) - radii[2] * sink
    return nh.ellipsoid((x, y, z), radii, subdivisions=subdivisions), rgb


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()
    mb.add(*make_cell())

    # discoid nucleus, slightly off-centre
    mb.add(*blister(0.10, 0.05, (0.12, 0.10, 0.045), NUCLEUS, sink=0.6))
    # contractile vacuole near the trailing uroid
    mb.add(*blister(-0.05, 0.36, (0.08, 0.08, 0.05), CONTRACTILE, sink=0.5))
    # food vacuoles (ingested algae) scattered through the endoplasm
    for x, y in ((-0.17, -0.06), (0.22, -0.22), (-0.26, 0.16), (0.03, -0.40), (0.30, 0.16), (-0.36, -0.26)):
        r = rng.uniform(0.045, 0.065)
        mb.add(*blister(x, y, (r, r, r * 0.75), rng.choice(FOOD), sink=0.65))
    # tiny crystals and granules give the endoplasm its grainy look
    placed = 0
    while placed < 30:
        x, y = rng.uniform(-0.6, 0.6), rng.uniform(-0.7, 0.5)
        p = Vector((x, y, 0.0))
        if sdf(p) > -0.06 or pod_extent(p) > 0.6:
            continue
        r = rng.uniform(0.010, 0.018)
        bm, col = blister(x, y, (r, r, r * 1.3), rng.choice(CRYSTAL), sink=0.3, subdivisions=0)
        nh.transform(bm, Matrix.Translation(Vector((x, y, 0))) @ Matrix.Rotation(rng.uniform(0, 3.1), 4, "Z")
                     @ Matrix.Translation(Vector((-x, -y, 0))))
        mb.add(bm, col, smooth=False)
        placed += 1

    return mb.to_object("Amoeba", roughness=0.4)


if __name__ == "__main__":
    nh.run(build, "Amoeba", views=((35, 30), (0, 80)))
