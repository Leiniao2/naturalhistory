"""
Procedural jaguar (Panthera onca) for map colonies, high-detail version.

A stocky, heavily muscled cat caught mid-stride with the head carried low: deep
barrel chest, thick neck, powerful shoulders and haunches, short sturdy legs on
broad toed paws, and the jaguar's massive, round head with a broad muzzle,
heavy cheeks and small rounded ears. The tail is comparatively short and
hangs in a loose curve. Overlapping anatomy is fused into one seamless surface
with a faint fur texture displaced into it (no decimation, so the voxel grid
stays even and the coat pattern stays sharp).
Repainted procedurally: golden-yellow coat with large broken-ring rosettes that
enclose a darker centre and one to three black dots, solid spots on the head,
neck and legs, a white belly and throat with big black blotches, white muzzle,
black lip line, black ear backs with a pale spot, and dark rings toward the
black-tipped tail.
Crisp details on top: yellow-amber eyes with round pupils, pink-brown nose
leather, whiskers and claws.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/panthera_onca.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Jaguar.fbx
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

COAT = (0.84, 0.60, 0.24)        # golden yellow
COAT_DEEP = (0.74, 0.46, 0.16)   # richer orange inside rosettes and along the back
COAT_SIDE = (0.90, 0.72, 0.42)   # paler lower flanks
WHITE = (0.93, 0.90, 0.82)       # belly, throat, inner legs, muzzle
SPOT = (0.06, 0.04, 0.03)        # black markings
NOSE = (0.42, 0.24, 0.21)
EYE = (0.80, 0.62, 0.18)
PUPIL = (0.02, 0.02, 0.01)
LIP = (0.08, 0.05, 0.04)
WHISKER = (0.95, 0.93, 0.88)
CLAW = (0.80, 0.76, 0.68)

VOXEL = 0.029

CLAW_TIPS = []
EYES = []         # eye centres on the face, found once the body is fused
EYE_NORMALS = []


# ---------------------------------------------------------------- anatomy

def front_leg(b, x, stride):
    """Shoulder blade, heavy triceps, thick forearm and a broad paw; stride moves the paw along y."""
    b.add(nh.tube([(x * 0.85, -0.32, 0.77), (x * 1.05, -0.44, 0.52)], [0.08, 0.085], sides=12,
                  scale_xy=(0.55, 1.0)), COAT)                                          # shoulder blade
    b.add(nh.ellipsoid((x * 1.10, -0.44, 0.46), (0.10, 0.12, 0.13)), COAT)              # triceps
    b.add(nh.tube([(x * 1.08, -0.47, 0.52), (x, -0.40, 0.31)], [0.11, 0.09], sides=12), COAT)  # upper arm
    wrist = Vector((x, -0.44 + stride, 0.11))
    b.add(nh.tube([(x, -0.40, 0.33), (x, -0.42 + stride * 0.5, 0.22), tuple(wrist)], [0.09, 0.074, 0.058],
                  sides=12), COAT)                                                      # forearm
    b.add(nh.ellipsoid((x * 1.03, -0.41 + stride * 0.3, 0.27), (0.075, 0.08, 0.09)), COAT)  # forearm muscle
    paw(b, wrist + Vector((0, -0.035, 0)), 0.098)


def hind_leg(b, x, stride):
    """Powerful haunch, thigh, gaskin, hock and paw."""
    b.add(nh.ellipsoid((x * 0.9, 0.40, 0.53), (0.13, 0.20, 0.21)), COAT)               # haunch
    b.add(nh.ellipsoid((x * 1.04, 0.33, 0.37), (0.105, 0.13, 0.14)), COAT)             # thigh muscle
    knee = Vector((x * 1.03, 0.28, 0.30))
    hock = Vector((x * 1.03, 0.50 + stride * 0.5, 0.18))
    ankle = Vector((x, 0.44 + stride, 0.09))
    b.add(nh.tube([tuple(knee), tuple(hock)], [0.09, 0.055], sides=12), COAT)          # gaskin
    b.add(nh.ellipsoid((x * 1.03, 0.40 + stride * 0.2, 0.25), (0.065, 0.09, 0.08)), COAT)  # calf
    b.add(nh.tube([tuple(hock), tuple(ankle)], [0.05, 0.047], sides=10), COAT)        # metatarsus
    paw(b, ankle + Vector((0, -0.05, 0)), 0.085)


def paw(b, center, r):
    b.add(nh.ellipsoid((center.x, center.y, 0.056), (r, r * 1.12, 0.06)), COAT)
    # four toes in an arc across the front, slightly apart so the voxel surface keeps the gaps
    for a in (-0.78, -0.26, 0.26, 0.78):
        tx = center.x + math.sin(a) * r * 1.05
        ty = center.y - math.cos(a) * r * 1.0 - 0.035
        b.add(nh.ellipsoid((tx, ty, 0.036), (0.033, 0.039, 0.038)), COAT)
        d = Vector((math.sin(a) * 0.4, -1.0, 0.0)).normalized()
        CLAW_TIPS.append((Vector((tx, ty, 0.03)) + d * 0.036, d))


def torso(b):
    b.add(nh.ellipsoid((0, -0.22, 0.55), (0.235, 0.36, 0.26), subdivisions=4), COAT)   # deep barrel chest
    b.add(nh.ellipsoid((0, 0.12, 0.55), (0.20, 0.32, 0.20), subdivisions=4), COAT)    # loin
    b.add(nh.ellipsoid((0, 0.04, 0.40), (0.16, 0.28, 0.10)), COAT)                    # belly
    b.add(nh.ellipsoid((0, 0.40, 0.57), (0.20, 0.21, 0.19), subdivisions=4), COAT)    # croup
    b.add(nh.tube([(0, -0.38, 0.63), (0, -0.56, 0.69), (0, -0.70, 0.73)], [0.19, 0.175, 0.15], sides=14),
          COAT)                                                                      # thick short neck
    b.add(nh.ellipsoid((0, -0.52, 0.52), (0.14, 0.14, 0.14)), COAT)                   # chest / dewlap


def head(b):
    b.add(nh.ellipsoid((0, -0.775, 0.80), (0.165, 0.165, 0.152), subdivisions=4), COAT)  # massive round cranium
    b.add(nh.tube([(-0.095, -0.895, 0.845), (0, -0.925, 0.865), (0.095, -0.895, 0.845)], [0.034, 0.04, 0.034],
                  sides=10), COAT)                                                      # brow
    for s in (-1, 1):
        b.add(nh.ellipsoid((s * 0.12, -0.86, 0.745), (0.085, 0.10, 0.075)), COAT)      # heavy cheeks
        b.add(nh.ellipsoid((s * 0.05, -1.025, 0.695), (0.062, 0.06, 0.054)), COAT)     # whisker pads
    b.add(nh.tube([(0, -0.87, 0.85), (0, -0.975, 0.80), (0, -1.05, 0.755)], [0.07, 0.066, 0.054], sides=12,
                  scale_xy=(1.3, 0.8)), COAT)                                           # broad muzzle
    b.add(nh.tube([(0, -0.81, 0.675), (0, -0.985, 0.648)], [0.085, 0.056], sides=12), COAT)  # heavy jaw
    b.add(nh.ellipsoid((0, -1.0, 0.628), (0.05, 0.045, 0.036)), COAT)                  # chin


def ears(b):
    for s in (-1, 1):
        b.add(nh.ellipsoid((s * 0.128, -0.735, 0.915), (0.05, 0.026, 0.05)), COAT)


def tail(b):
    """Short for a big cat: hangs from the croup in a loose curve, tip lifted."""
    pts = [(0, 0.54, 0.62), (0, 0.70, 0.57), (0.02, 0.84, 0.44), (0.05, 0.92, 0.30), (0.08, 0.95, 0.19),
           (0.11, 0.93, 0.12)]
    b.add(nh.tube(pts, [0.062, 0.05, 0.043, 0.039, 0.036, 0.034], sides=12), COAT)
    b.add(nh.ellipsoid((0.115, 0.925, 0.11), (0.036, 0.036, 0.04)), COAT)


TAIL_PTS = [Vector(p) for p in ((0, 0.54, 0.62), (0, 0.70, 0.57), (0.02, 0.84, 0.44), (0.05, 0.92, 0.30),
                                (0.08, 0.95, 0.19), (0.11, 0.93, 0.12))]


def tail_param(p):
    """(distance from the tail axis, 0..1 position along it) for the nearest tail segment."""
    best, best_t, acc = 1e9, 0.0, 0.0
    lens = [(b - a).length for a, b in zip(TAIL_PTS, TAIL_PTS[1:])]
    total = sum(lens)
    for (a, b), L in zip(zip(TAIL_PTS, TAIL_PTS[1:]), lens):
        ab = b - a
        t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared))
        d = (p - (a + ab * t)).length
        if d < best:
            best, best_t = d, (acc + t * L) / total
        acc += L
    return best, best_t


# ---------------------------------------------------------------- coat pattern

def rosette(p, freq, seed):
    """Dark amount (0..1) and 'inside a rosette' amount of a jaguar rosette field at p."""
    q = p * freq + Vector((seed, seed * 0.37, seed * 0.71))
    dist, pts = noise.voronoi(q, distance_metric="DISTANCE")
    d1, d2 = dist[0], dist[1]
    c = pts[0]
    h = noise.noise(c * 1.91) * 0.5 + 0.5            # per-cell random value
    r = 0.40 + 0.08 * h                              # ring radius (cells are ~1 apart)
    wob = 0.06 * noise.noise(q * 2.2)
    ring = 1.0 - nh.smoothstep(0.08, 0.15, abs(d1 + wob - r))
    ring *= nh.smoothstep(0.05, 0.12, d2 - d1)       # gap between neighbouring rosettes
    # broken ring: blotchy gaps around it
    ring *= nh.smoothstep(-0.35, -0.1, noise.noise(q * 2.6 + Vector((7.1, 2.3, 5.9))))
    inside = 1.0 - nh.smoothstep(r - 0.12, r - 0.04, d1 + wob)
    # one to three dots inside the bigger rosettes
    dots = 0.0
    if h > 0.25:
        n_dots = 1 + int(h * 2.99)
        for k in range(n_dots):
            ang = k * 2.4 + h * 9.0
            off = Vector((math.cos(ang), math.sin(ang), math.cos(ang * 1.7))) * (0.0 if n_dots == 1 else 0.14)
            dd = (q - (c + off)).length
            dots = max(dots, 1.0 - nh.smoothstep(0.07, 0.13, dd))
    return max(ring, dots), inside


def solid_spots(p, freq, size, seed):
    q = p * freq + Vector((seed, seed * 0.5, seed * 0.25))
    dist, pts = noise.voronoi(q, distance_metric="DISTANCE")
    h = noise.noise(pts[0] * 2.7) * 0.5 + 0.5
    r = size * (0.6 + 0.6 * h)
    wob = 0.08 * noise.noise(q * 2.0)
    return 1.0 - nh.smoothstep(r - 0.07, r + 0.05, dist[0] + wob)


def paint(co, n):
    p = co
    # regions
    is_head = nh.smoothstep(-0.66, -0.74, p.y) * nh.smoothstep(0.58, 0.64, p.z)
    tail_d, tail_t = tail_param(p)
    is_tail = 1.0 if (tail_d < 0.075 and p.y > 0.6) else 0.0
    leg = nh.smoothstep(0.36, 0.26, p.z) if is_tail == 0 else 0.0
    under = nh.smoothstep(-0.25, -0.7, n.z) * nh.smoothstep(0.5, 0.42, p.z)
    throat = nh.smoothstep(-0.1, -0.55, n.z) * nh.smoothstep(-0.5, -0.6, p.y) * nh.smoothstep(0.78, 0.68, p.z)
    inner = 0.0
    if p.z < 0.5:
        # inner faces of the legs (facing the body's midline)
        inner = nh.smoothstep(0.15, 0.55, -n.x * math.copysign(1, p.x)) * nh.smoothstep(0.1, 0.16, abs(p.x))

    # base: golden, richer along the back, paler toward the belly
    c = nh.lerp(COAT_SIDE, COAT, nh.smoothstep(-0.3, 0.3, n.z))
    c = nh.lerp(c, COAT_DEEP, 0.55 * nh.smoothstep(0.6, 0.95, n.z) * nh.smoothstep(0.55, 0.7, p.z))
    c = nh.lerp(c, COAT_DEEP, 0.12 * max(0.0, noise.noise(p * 7.0)))
    white = min(1.0, under + throat + inner * 0.8)
    if p.z < 0.11:   # paws stay golden underneath
        white *= 0.3
    c = nh.lerp(c, WHITE, white)

    # markings
    if is_tail:
        # spots near the root turning into dark rings, black tip
        ring = 0.5 + 0.5 * math.sin(tail_t * 32.0 + 0.6 * noise.noise(p * 12.0))
        rings = nh.smoothstep(0.55, 0.75, tail_t) * nh.smoothstep(0.7, 0.85, ring)
        spots = solid_spots(p, 22.0, 0.32, 4.0) * (1.0 - nh.smoothstep(0.5, 0.7, tail_t))
        dark = max(rings, spots, nh.smoothstep(0.88, 0.93, tail_t))
        c = nh.lerp(c, SPOT, dark)
    elif is_head > 0.5:
        # small solid spots, densest on the crown and cheeks; clear muzzle and chin
        muzzle = nh.smoothstep(-0.99, -1.025, p.y) * nh.smoothstep(0.73, 0.71, p.z)
        chin = nh.smoothstep(0.685, 0.655, p.z) * nh.smoothstep(-0.9, -0.95, p.y)
        c = nh.lerp(c, WHITE, max(muzzle, chin) * 0.9)
        spot = solid_spots(p, 34.0, 0.3, 1.0) * (1.0 - max(muzzle, chin))
        c = nh.lerp(c, SPOT, spot)
        # dark eye-liner with pale fur just below each eye
        for e in EYES:
            q = p - e
            r = Vector((q.x, q.y, q.z * 1.35)).length
            if r < 0.05:
                c = nh.lerp(c, nh.lerp(WHITE, COAT, 0.4), nh.smoothstep(-0.01, -0.03, q.z) * (1 - nh.smoothstep(0.035, 0.05, r)))
                c = nh.lerp(c, SPOT, 1.0 - nh.smoothstep(0.034, 0.042, r))
        # black lip line under the whisker pads
        if p.y < -0.93 and 0.643 < p.z < 0.668 and abs(p.x) < 0.11:
            c = nh.lerp(c, LIP, 0.85)
        # ear backs black with a pale central spot
        if p.z > 0.88 and abs(p.x) > 0.075 and n.y > 0.1:
            e = Vector((abs(p.x) - 0.128, p.y + 0.725, p.z - 0.925)).length
            c = SPOT if e > 0.02 else nh.lerp(WHITE, COAT, 0.3)
    else:
        if leg > 0.5 or white > 0.5:
            # solid spots on the legs; big black blotches on the white belly
            freq = 19.0 if white < 0.5 else 10.0
            spot = solid_spots(p, freq, 0.3 if white < 0.5 else 0.33, 2.0 + white)
            c = nh.lerp(c, SPOT, spot)
        else:
            # rosettes on the body, smaller on the neck and shoulders; a line of spots down the spine
            freq = 9.0 if p.y > -0.45 else 11.5
            dark, inside = rosette(p, freq, 3.0)
            c = nh.lerp(c, COAT_DEEP, 0.75 * inside)
            c = nh.lerp(c, SPOT, dark)
            if abs(p.x) < 0.05 and n.z > 0.8:
                c = nh.lerp(c, SPOT, solid_spots(Vector((p.x * 3.0, p.y, p.z)), 16.0, 0.36, 9.0))
    return c


def fur_displace(co, n):
    if co.z < 0.04:
        return 0.0
    return 0.0018 * noise.noise(co * 40.0) + 0.001 * noise.noise(Vector((co.x * 80.0, co.y * 25.0, co.z * 80.0)))


# ---------------------------------------------------------------- crisp details

class Surface:
    def __init__(self, bm):
        self.tree = BVHTree.FromBMesh(bm)

    def hit(self, origin, direction):
        """First surface point along a ray (falls back to the nearest point)."""
        loc, normal, _i, _d = self.tree.ray_cast(Vector(origin), Vector(direction).normalized())
        if loc is None:
            loc, normal, _i, _d = self.tree.find_nearest(Vector(origin))
        return loc, normal


def find_eyes(surf):
    EYES.clear()
    EYE_NORMALS.clear()
    for s in (-1, 1):
        p, n = surf.hit((s * 0.066, -0.7, 0.818), (s * 0.1, -1, 0))
        EYES.append(p)
        EYE_NORMALS.append(n)


def on_head(p):
    return p.y < -0.68 and p.z > 0.6


def refine(bm, contrasts=(0.15,)):
    """Splits edges that cross a colour boundary so the coat pattern stays crisp without
    raising the resolution everywhere (rosettes are mostly on flat flanks)."""
    first = True               # the face is small and busy: split all of it once
    for contrast in contrasts:
        bm.normal_update()
        cols = {v: paint(v.co, v.normal) for v in bm.verts}
        lum = {v: c[0] * 0.3 + c[1] * 0.6 + c[2] * 0.1 for v, c in cols.items()}
        edges = [e for e in bm.edges if e.calc_length() > VOXEL * 0.35
                 and (abs(lum[e.verts[0]] - lum[e.verts[1]]) > contrast or (first and on_head(e.verts[0].co)))]
        first = False
        bmesh.ops.subdivide_edges(bm, edges=edges, cuts=1, use_grid_fill=True)
        bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.normal_update()


def details(mb, surf):
    for s in (-1, 1):
        # yellow-amber eyes set into the face under the brow, with round pupils
        e = EYES[0 if s < 0 else 1]
        look = (EYE_NORMALS[0 if s < 0 else 1] * 0.4 + Vector((s * 0.15, -1, 0.05))).normalized()
        mb.add(nh.ellipsoid(tuple(e - look * 0.014), (0.026, 0.026, 0.02), subdivisions=3), EYE)
        mb.add(nh.ellipsoid(tuple(e + look * 0.0075), (0.0105, 0.0105, 0.0115), subdivisions=2), PUPIL)
        # whiskers fanning out from the pads
        for k in range(4):
            a = math.radians(-16 + k * 10)
            start, n = surf.hit((s * 0.07, -0.85, 0.69 + k * 0.011), (0, -1, 0))
            end = start + Vector((s * math.cos(a) * 0.17, 0.06, math.sin(a) * 0.05))
            mb.add(nh.tube([tuple(start - n * 0.004), tuple(end)], [0.0025, 0.0], sides=3), WHISKER)
    # nose leather: broad and flat on the end of the muzzle
    p, n = surf.hit((0, -0.85, 0.77), (0, -1, -0.1))
    mb.add(nh.ellipsoid(tuple(p + Vector((0, 0.004, 0))), (0.034, 0.012, 0.019), subdivisions=2,
                        deform=lambda v: 1.0 - 0.35 * max(0.0, -v.z)), NOSE)
    # claws peeking out of the toe fur
    for tip, d in CLAW_TIPS:
        base = tip - d * 0.01
        mb.add(nh.tube([base, tip + d * 0.012 + Vector((0, 0, -0.016))], [0.007, 0.0], sides=6), CLAW)


def build():
    CLAW_TIPS.clear()
    b = nh.MeshBuilder()
    torso(b)
    # walking: left-front and right-hind forward
    front_leg(b, -0.15, -0.12)
    front_leg(b, 0.15, 0.10)
    hind_leg(b, -0.16, 0.08)
    hind_leg(b, 0.16, -0.10)
    head(b)
    ears(b)
    tail(b)
    fused = b.fuse(voxel=VOXEL, smooth=5, smooth_factor=0.5)
    fused.normal_update()
    for v in fused.verts:
        v.co += v.normal * fur_displace(v.co, v.normal)
    fused.normal_update()

    surf = Surface(fused)
    find_eyes(surf)
    refine(fused)
    mb = nh.MeshBuilder()
    mb.add(fused, color=paint)
    details(mb, surf)
    obj = mb.to_object("Jaguar")
    nh.ground_to_zero(obj)
    return obj


def closeup(path, target, dist, az, el, lens=60):
    """Extra render aimed at `target` (after nh.run set up the scene and camera)."""
    scene = bpy.context.scene
    cam = scene.camera
    cam.data.lens = lens
    a, e = math.radians(az), math.radians(el)
    target = Vector(target)
    cam.location = target + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    nh.run(build, "Jaguar", ground=(0.32, 0.40, 0.22), views=((35, 25), (-90, 8), (20, 65)))
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--render" in argv:
        out = Path(argv[argv.index("--render") + 1])
        closeup(out.with_name(out.stem + "_head.png"), (0, -0.85, 0.78), 0.9, 35, 15)
