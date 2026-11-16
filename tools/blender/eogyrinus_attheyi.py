"""
Procedural Eogyrinus attheyi (Late Carboniferous embolomere, ~4.5 m) for the map (Swim style).

A long, slender, crocodile- or eel-like aquatic tetrapod of the coal-swamp waters. The
body is lofted as one tube from the long, low, triangular skull (flat-topped, with the
eyes set high about two thirds of the way back and a narrow rounded snout) through a
long, slim trunk to a very long, deep, laterally flattened swimming tail that makes up
about half the length. Four small sprawling limbs are held folded back against the
flanks, as when swimming. Limbs, feet and the raised orbits are fused onto the body,
then the surface is sculpted by displacement: faint costal grooves down the flanks
marking the many vertebrae, the pitted dermal bone and the lateral-line sensory grooves
of the skull roof, the lip line, and a fine scaly skin. Repainted procedurally: olive-
brown back with darker irregular blotches, paler flanks, a yellowish belly with rows of
chevron-shaped ventral scales. Crisp details on top: low fleshy fin folds above and
below the tail, rows of sharp conical teeth along both jaws (larger fangs near the front),
toes, eyes and nostrils.
The body is left straight: on the map the shader (MapFeatureFlap.cginc, ApplyUndulate)
swims it with a travelling wave.

Usage:
  blender --background --python tools/blender/eogyrinus_attheyi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Eogyrinus.fbx
Pivot at the body centre, faces -Y, back up (+Z). About 2 units long.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy  # noqa: E402
import bmesh  # noqa: E402
import nh_model as nh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

NAME = "Eogyrinus"
VOXEL = 0.0105

# Body profile along Y (snout at -Y): half-width, half-height, centre height.
KEY_Y = [-1.00, -0.975, -0.94, -0.89, -0.83, -0.78, -0.74, -0.70, -0.62, -0.48, -0.32, -0.16, -0.04, 0.06,
         0.18, 0.32, 0.48, 0.64, 0.80, 0.92, 1.00]
KEY_W = [0.018, 0.026, 0.034, 0.044, 0.056, 0.066, 0.070, 0.068, 0.072, 0.080, 0.084, 0.082, 0.074, 0.060,
         0.048, 0.040, 0.033, 0.025, 0.017, 0.010, 0.004]
KEY_H = [0.012, 0.016, 0.020, 0.024, 0.029, 0.034, 0.040, 0.048, 0.056, 0.064, 0.068, 0.067, 0.064, 0.064,
         0.068, 0.068, 0.062, 0.051, 0.036, 0.020, 0.006]
KEY_Z = [-0.012, -0.010, -0.008, -0.005, -0.002, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000,
         0.000, 0.004, 0.006, 0.006, 0.005, 0.004, 0.003, 0.002]
SNOUT = -1.00
HEAD_BACK = -0.745

# Palette
BACK = (0.30, 0.28, 0.15)        # olive-brown
BACK_LIGHT = (0.42, 0.39, 0.22)
BLOTCH = (0.17, 0.15, 0.08)
FLANK = (0.46, 0.41, 0.24)
BELLY = (0.74, 0.67, 0.45)       # yellowish
SCALE_LINE = (0.52, 0.46, 0.29)
SKULL = (0.36, 0.33, 0.19)
GROOVE = (0.12, 0.11, 0.06)
LIP = (0.10, 0.09, 0.05)
FIN = (0.40, 0.36, 0.20)
FIN_EDGE = (0.24, 0.21, 0.11)
FOOT = (0.40, 0.36, 0.21)
TOOTH = (0.88, 0.84, 0.70)
EYE = (0.58, 0.48, 0.15)
PUPIL = (0.02, 0.02, 0.015)


def interp(ys, vs, y):
    if y <= ys[0]:
        return vs[0]
    if y >= ys[-1]:
        return vs[-1]
    for i in range(len(ys) - 1):
        if ys[i] <= y <= ys[i + 1]:
            t = (y - ys[i]) / (ys[i + 1] - ys[i])
            t = t * t * (3 - 2 * t) * 0.5 + t * 0.5  # soften the kinks
            return vs[i] + (vs[i + 1] - vs[i]) * t
    return vs[-1]


def W(y):
    return interp(KEY_Y, KEY_W, y)


def H(y):
    return interp(KEY_Y, KEY_H, y)


def CZ(y):
    return interp(KEY_Y, KEY_Z, y)


def section_power(y):
    if y < HEAD_BACK:
        return 3.0   # flat-topped, flat-bottomed skull
    if y > 0.05:
        return 2.0   # oval, laterally flattened tail
    return 2.4


def ring_point(y, a, w, h, z, p):
    u, v = math.cos(a), math.sin(a)
    ex = 2.0 / p
    px = w * math.copysign(abs(u) ** ex, u)
    pz = z + h * math.copysign(abs(v) ** ex, v) * (0.85 if v < 0 and y < HEAD_BACK else 1.0)
    return Vector((px, y, pz))


def body_loft(sides=40):
    """One closed tube from the rounded snout tip to the tail tip."""
    bm = bmesh.new()
    rings = []
    r = W(SNOUT)
    tip_y = SNOUT - r * 0.9
    rings.append([bm.verts.new(Vector((0, tip_y, CZ(SNOUT))))])
    for phi_deg in (72, 52, 32, 14):         # rounded snout tip
        phi = math.radians(phi_deg)
        y = SNOUT - r * 0.9 * math.sin(phi)
        rings.append([bm.verts.new(ring_point(y, k / sides * math.tau, r * math.cos(phi),
                                              H(SNOUT) * math.cos(phi) ** 0.45, CZ(SNOUT), 3.0))
                      for k in range(sides)])
    y = SNOUT
    while y < 1.0:
        rings.append([bm.verts.new(ring_point(y, k / sides * math.tau, W(y), H(y), CZ(y), section_power(y)))
                      for k in range(sides)])
        y += 0.010
    rings.append([bm.verts.new(Vector((0, 1.012, CZ(1.0))))])
    for a, b in zip(rings, rings[1:]):
        if len(a) == 1:
            for k in range(sides):
                bm.faces.new([a[0], b[(k + 1) % sides], b[k]])
        elif len(b) == 1:
            for k in range(sides):
                bm.faces.new([a[k], a[(k + 1) % sides], b[0]])
        else:
            for k in range(sides):
                j = (k + 1) % sides
                bm.faces.new([a[k], a[j], b[j], b[k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


# ---------------------------------------------------------------- limbs

TOES = []      # (base, direction, length, radius)


def limbs(body):
    """Small limbs folded back along the flanks, as when swimming."""
    for s in (-1, 1):
        for (y, z), scale, n_toes in (((-0.655, -0.030), 1.0, 4), ((0.0, -0.030), 1.15, 5)):
            sh = Vector((s * W(y) * 0.75, y, z))
            elbow = sh + Vector((s * 0.052, 0.048, -0.024)) * scale
            wrist = elbow + Vector((s * 0.008, 0.078, -0.008)) * scale
            body.add(nh.tube([sh, elbow], [0.026 * scale, 0.020 * scale], sides=12), FLANK)
            body.add(nh.ellipsoid(elbow, (0.020 * scale,) * 3, subdivisions=2), FLANK)
            body.add(nh.tube([elbow, wrist], [0.019 * scale, 0.015 * scale], sides=10, scale_xy=(1.0, 0.8)), FLANK)
            hand = wrist + Vector((s * 0.006, 0.022, -0.002)) * scale
            body.add(nh.ellipsoid(hand, (0.022 * scale, 0.026 * scale, 0.008 * scale), subdivisions=2), FOOT)
            for k in range(n_toes):
                a = math.radians(-30 + 60 * k / (n_toes - 1)) * s
                d = Vector((math.sin(a) + s * 0.25, math.cos(a), -0.05)).normalized()
                L = (0.028 + 0.012 * math.sin(math.pi * (k + 0.5) / n_toes)) * scale
                TOES.append((hand + d * 0.016 * scale, d, L, 0.0055 * scale))


def head_mounds(body):
    for s in (-1, 1):
        y = -0.855
        body.add(nh.ellipsoid((s * 0.030, y, CZ(y) + H(y) - 0.004), (0.016, 0.022, 0.010), subdivisions=3), SKULL)


# ---------------------------------------------------------------- sculpt / paint

def frac(x):
    return x - math.floor(x)


def jaw_z(y):
    back = nh.smoothstep(-0.83, HEAD_BACK, y)
    return CZ(y) - 0.18 * H(y) - 0.10 * H(y) * back   # gape line dips slightly toward the jaw joint


def lip_dist(co):
    y = co.y
    if y > HEAD_BACK + 0.005 or abs(co.x) < W(y) * 0.5:
        return 1.0
    return min(1.0, abs(co.z - jaw_z(y)) / 0.0045)


def lateral_line(co):
    """Sensory canal grooves of the skull roof: supraorbital (between eye and nostril) and a
    jugal canal curving below the orbit toward the back of the skull. 0..1."""
    y = co.y
    if y > HEAD_BACK + 0.01:
        return 0.0
    t = (y - SNOUT) / (HEAD_BACK - SNOUT)
    g = 0.0
    xs = 0.012 + 0.020 * t                      # supraorbital canal, top of the skull
    g = max(g, math.exp(-((abs(co.x) - xs) / 0.0035) ** 2) * (co.z > CZ(y) + H(y) * 0.6)
            * nh.smoothstep(0.08, 0.15, t) * (1.0 - nh.smoothstep(0.55, 0.62, t)))
    zj = CZ(y) + H(y) * (0.15 + 0.25 * t)       # infraorbital/jugal canal, side of the skull
    g = max(g, math.exp(-((co.z - zj) / 0.0035) ** 2) * (abs(co.x) > W(y) * 0.75)
            * nh.smoothstep(0.1, 0.2, t) * (1.0 - nh.smoothstep(0.92, 1.0, t)))
    return g


def sculpt(bm):
    bm.normal_update()
    col = bm.loops.layers.color.get("Col") or bm.loops.layers.color.new("Col")
    disp, paint = {}, {}
    for vert in bm.verts:
        co, n = vert.co.copy(), vert.normal.copy()
        y = co.y
        h = max(H(y), 1e-3)
        v = (co.z - CZ(y)) / h
        coarse = noise.noise(co * 6.0 + Vector((2.3, 0.4, 1.1)))
        fine = noise.noise(co * 70.0)
        d = 0.0012 * fine
        head = y < HEAD_BACK
        if head and n.z > 0.45:                                    # pitted dermal bone
            dist, _p = noise.voronoi(co * 70.0, distance_metric="DISTANCE")
            d -= 0.0022 * (1.0 - nh.smoothstep(0.0, 0.35, dist[0]))
        ll = lateral_line(co)
        d -= 0.0025 * ll
        ld = lip_dist(co)
        d -= 0.0035 * (1.0 - ld)
        # costal grooves: one per vertebra down the flanks, fading on the tail
        costal = 0.0
        if -0.70 < y < 0.85 and abs(v) < 0.8:
            ph = frac((y + 0.70) / 0.034)
            costal = (1.0 - nh.smoothstep(0.0, 0.18, min(ph, 1.0 - ph))) * (1.0 - nh.smoothstep(0.5, 0.8, abs(v)))
            costal *= 1.0 - 0.6 * nh.smoothstep(0.2, 0.85, y)
            d -= 0.0018 * costal
        disp[vert] = n * d

        # ---- colour
        top = nh.smoothstep(-0.1, 0.6, n.z + 0.15 * coarse)
        belly = nh.smoothstep(-0.35, -0.7, n.z + 0.1 * coarse)
        c = nh.lerp(FLANK, BACK, top)
        c = nh.lerp(c, BACK_LIGHT, 0.3 * max(0.0, noise.noise(co * 14.0)) * top)
        blotch = nh.smoothstep(0.05, 0.35, noise.noise(co * Vector((9.0, 4.5, 9.0)) + Vector((5.0, 0, 0))))
        c = nh.lerp(c, BLOTCH, 0.85 * blotch * nh.smoothstep(-0.4, 0.3, n.z))
        c = nh.lerp(c, GROOVE, 0.35 * costal)
        if head:
            c = nh.lerp(c, SKULL, 0.45 * top)
            c = nh.lerp(c, GROOVE, 0.7 * ll)
            if co.z < jaw_z(y) - 0.003 and abs(co.x) > W(y) * 0.4:
                c = nh.lerp(c, BELLY, 0.45)                       # paler lower jaw
        if ld < 1.0:
            c = nh.lerp(c, LIP, 0.85 * (1.0 - ld))
        c = nh.lerp(c, BELLY, belly)
        if belly > 0.0 and -0.72 < y < 0.30:
            # chevron rows of ventral scales pointing forward
            ph = frac((y + 0.9 * abs(co.x)) / 0.018)
            line = 1.0 - nh.smoothstep(0.0, 0.16, min(ph, 1.0 - ph))
            c = nh.lerp(c, SCALE_LINE, 0.6 * line * belly)
        k = 0.92 + 0.16 * (0.5 + 0.5 * fine)
        paint[vert] = (c[0] * k, c[1] * k, c[2] * k)
    for vert, dv in disp.items():
        vert.co += dv
    bm.normal_update()
    for f in bm.faces:
        f.smooth = True
        for l in f.loops:
            c = paint[l.vert]
            l[col] = (c[0], c[1], c[2], 1.0)
    return bm


# ---------------------------------------------------------------- crisp details

class Surface:
    def __init__(self, bm):
        self.tree = BVHTree.FromBMesh(bm)

    def hit(self, origin, direction):
        loc, normal, _i, _d = self.tree.ray_cast(Vector(origin), Vector(direction).normalized())
        if loc is None:
            loc, normal, _i, _d = self.tree.find_nearest(Vector(origin))
        return loc, normal


def fin_fold(base_fn, height_fn, y0, y1, steps, thickness, up=1):
    """Thin, low fleshy fin fold rooted inside the tail along base_fn(y), reaching height_fn(y)."""
    bm = bmesh.new()
    rows = []
    for i in range(steps + 1):
        y = y0 + (y1 - y0) * i / steps
        b = base_fn(y)
        tip = b + Vector((0, 0.25, up)).normalized() * max(height_fn(y), 0.002)
        x_off = Vector((thickness * 0.5, 0, 0))
        rows.append([bm.verts.new(b - x_off), bm.verts.new(tip - x_off * 0.3),
                     bm.verts.new(tip + x_off * 0.3), bm.verts.new(b + x_off)])
    for a, b in zip(rows, rows[1:]):
        for k in range(4):
            j = (k + 1) % 4
            bm.faces.new([a[k], a[j], b[j], b[k]])
    bm.faces.new(list(reversed(rows[0])))
    bm.faces.new(rows[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def col(co, n):
        rel = abs(co.z - base_fn(co.y).z) / max(height_fn(co.y), 0.004)
        c = nh.lerp(FIN, FIN_EDGE, nh.smoothstep(0.55, 1.0, rel))
        return nh.lerp(c, BLOTCH, 0.4 * nh.smoothstep(0.1, 0.45, noise.noise(co * 9.0)))
    return bm, col


def fins(mb):
    def top(y):
        return Vector((0, y, CZ(y) + H(y) * 0.8))

    def bottom(y):
        return Vector((0, y, CZ(y) - H(y) * 0.8))

    def dorsal_h(y):
        return 0.032 * nh.smoothstep(0.08, 0.42, y) * (1.0 - nh.smoothstep(0.85, 1.0, y)) + 0.002

    def ventral_h(y):
        return 0.024 * nh.smoothstep(0.25, 0.55, y) * (1.0 - nh.smoothstep(0.86, 1.0, y)) + 0.002

    for base, hf, y0, steps, up in ((top, dorsal_h, 0.02, 60, 1), (bottom, ventral_h, 0.20, 48, -1)):
        bm, col = fin_fold(base, hf, y0, 0.995, steps, 0.007, up=up)
        mb.add(bm, col)


def teeth(mb, surf):
    """Sharp conical teeth along both jaws, upper pointing down, lower up, interleaved."""
    y = -0.985
    k = 0
    while y < HEAD_BACK - 0.03:
        fang = math.exp(-((y + 0.955) / 0.012) ** 2) + 0.7 * math.exp(-((y + 0.90) / 0.012) ** 2)
        for s in (-1, 1):
            for upper in (True, False):
                yy = y + (0.0 if upper else 0.0085)
                z = jaw_z(yy) + (0.0025 if upper else -0.0025)
                loc, nrm = surf.hit((s * (W(yy) + 0.1), yy, z), (-s, 0, 0))
                if loc is None:
                    continue
                out = Vector((nrm.x, nrm.y, 0)).normalized() if abs(nrm.x) + abs(nrm.y) > 1e-3 else Vector()
                L = 0.009 + 0.008 * fang + 0.0015 * noise.noise(loc * 80.0)
                down = Vector((0, 0, -1 if upper else 1))
                base = loc - out * 0.0015
                mb.add(nh.tube([base, base + down * L + out * 0.0015 + Vector((0, 0.002, 0))],
                               [0.0028 + 0.0012 * fang, 0.0], sides=5), TOOTH)
        y += 0.017
        k += 1


def eyes(mb, surf):
    for s in (-1, 1):
        loc, nrm = surf.hit((s * 0.033, -0.858, 0.3), (0, 0, -1))
        look = Vector((s * 0.8, -0.2, 0.6)).normalized()
        c = loc - look * 0.003

        def eye_col(co, n, c=c, look=look):
            d = (co - c).normalized()
            k = d.dot(look)
            if k > 0.84:
                return PUPIL
            if k > 0.05:
                return nh.lerp(EYE, (0.30, 0.22, 0.06), nh.smoothstep(0.6, 0.84, k))
            return (0.08, 0.07, 0.04)
        mb.add(nh.ellipsoid(c, (0.010, 0.012, 0.009), subdivisions=3), eye_col)
        # nostrils near the snout tip
        loc, _n = surf.hit((s * 0.012, SNOUT + 0.018, 0.3), (0, 0, -1))
        if loc is not None:
            mb.add(nh.ellipsoid(loc + Vector((0, 0, 0.0005)), (0.0028, 0.0036, 0.0016), subdivisions=2), PUPIL)


def toes(mb):
    for base, d, L, r in TOES:
        tip = base + d * L + Vector((0, 0, -0.002))
        mb.add(nh.tube([base, base + d * L * 0.5, tip], [r, r * 0.85, r * 0.45], sides=6), FOOT)


def drop_islands(bm, min_verts=200):
    """Removes stray voxel fragments (e.g. where the tail tip gets thinner than a voxel)."""
    seen = set()
    for start in bm.verts:
        if start in seen:
            continue
        part, stack = [], [start]
        seen.add(start)
        while stack:
            v = stack.pop()
            part.append(v)
            for e in v.link_edges:
                o = e.other_vert(v)
                if o not in seen:
                    seen.add(o)
                    stack.append(o)
        if len(part) < min_verts:
            bmesh.ops.delete(bm, geom=part, context="VERTS")


def centre(obj):
    """Pivot at the body centre (Swim style)."""
    vs = obj.data.vertices
    mid = Vector([(max(v.co[i] for v in vs) + min(v.co[i] for v in vs)) * 0.5 for i in range(3)])
    for v in vs:
        v.co -= mid


def build():
    TOES.clear()
    body = nh.MeshBuilder()
    body.add(body_loft(), FLANK)
    limbs(body)
    head_mounds(body)
    fused = body.fuse(voxel=VOXEL, smooth=4, smooth_factor=0.5)
    drop_islands(fused)
    fused = sculpt(fused)

    surf = Surface(fused)
    mb = nh.MeshBuilder()
    fins(mb)
    toes(mb)
    teeth(mb, surf)
    eyes(mb, surf)
    mb.add(fused)
    obj = mb.to_object(NAME, roughness=0.5)
    centre(obj)
    return obj


def render_extra(obj, path):
    """Head close-up, using the camera and light set up by nh.render_preview."""
    scene = bpy.context.scene
    cam = scene.camera
    target = Vector((0, -0.87, 0.0))
    for i, (az, el, dist) in enumerate(((38, 25, 0.45), (-80, 6, 0.42))):
        a, e = math.radians(az), math.radians(el)
        cam.location = target + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist
        cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
        out = Path(path)
        scene.render.filepath = str(out.with_name(f"{out.stem}_head{i}.png"))
        bpy.ops.render.render(write_still=True)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    bpy.ops.wm.read_factory_settings(use_empty=True)
    obj = build()
    nh.export_fbx(obj, NAME)
    if "--render" in argv:
        path = argv[argv.index("--render") + 1]
        nh.render_preview(obj, path, background=(0.10, 0.13, 0.09), views=((35, 25), (-90, 5), (0, 80)))
        render_extra(obj, path)


if __name__ == "__main__":
    main()
