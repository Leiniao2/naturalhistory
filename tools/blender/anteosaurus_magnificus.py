"""
Procedural Anteosaurus magnificus (Middle Permian anteosaurid dinocephalian, ~5-6 m) for map
colonies.

The apex predator of the Capitanian Karoo (Tapinocephalus Assemblage Zone, South Africa) and
one of the largest synapsid carnivores ever. A heavy, deep-chested body with the shoulders
carried higher than the hips, stout, semi-sprawling limbs - forelimbs bowed out at the elbow,
hind limbs more upright under the hips - on broad, short-toed, clawed feet, and a relatively
short, thick tail. The huge, long skull (~80 cm) is thickened by pachyostosis: heavy rounded
bosses above the eyes and behind them on the postorbital bar, and the genus' trademark - a
great swollen boss on the jugal (cheek) below each eye, bulging out sideways and curling
upward. The snout tip turns up, carrying big interlocking incisors that jut forward, then a
long canine each side hanging over the lower jaw and a row of smaller cheek teeth. The mouth
is a little open.
Body, legs, head and bosses are fused into one seamless surface and sculpted by displacement:
thick, finely pebbled skin, rugose bone texture over the bosses and a lip groove. Painted
dusky red-brown on the back with darker blotches, tawny on the flanks and pale beneath, the
bosses greyish and pale.
Crisp details on top: incisors, canines, cheek teeth, eyes, nostrils and claws. Helpers are
borrowed from inostrancevia_alexandri.py.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/anteosaurus_magnificus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Anteosaurus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import inostrancevia_alexandri as ino  # noqa: E402  (geometry helpers only)
import bpy  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402

NAME = "Anteosaurus"

BACK = (0.36, 0.21, 0.14)       # dusky red-brown
FLANK = (0.58, 0.42, 0.28)      # tawny
BELLY = (0.82, 0.74, 0.60)
BLOTCH = (0.20, 0.12, 0.08)
LEG = (0.44, 0.30, 0.20)
BOSS = (0.62, 0.56, 0.48)       # pale, greyish thickened bone under thin skin
LIP = (0.12, 0.07, 0.05)
MOUTH = (0.46, 0.18, 0.16)
TOOTH = (0.94, 0.90, 0.78)
CLAW = (0.12, 0.09, 0.07)
EYE = (0.78, 0.50, 0.10)
PUPIL = (0.02, 0.02, 0.02)

loft, densify, oriented, decimate, cone = ino.loft, ino.densify, ino.oriented, ino.decimate, ino.cone
row_at, profile, Surface = ino.row_at, ino.profile, ino.Surface


# ---------------------------------------------------------------- anatomy

def tail_x(y):
    s = max(0.0, (y - 0.40) / 0.7)
    return 0.07 * s * s


# short neck -> high shoulders, deep chest -> heavy barrel -> lower hips -> short thick tail
TORSO = [
    ((0.0, -0.70, 0.680), 0.135, 0.140),
    ((0.0, -0.60, 0.655), 0.180, 0.190),
    ((0.0, -0.45, 0.605), 0.230, 0.245),
    ((0.0, -0.26, 0.570), 0.250, 0.250),
    ((0.0, -0.06, 0.555), 0.252, 0.238),
    ((0.0, 0.14, 0.550), 0.230, 0.212),
    ((0.0, 0.30, 0.545), 0.192, 0.180),
    ((tail_x(0.45), 0.45, 0.505), 0.142, 0.132),
    ((tail_x(0.62), 0.62, 0.430), 0.092, 0.086),
    ((tail_x(0.79), 0.79, 0.345), 0.058, 0.054),
    ((tail_x(0.94), 0.94, 0.265), 0.032, 0.030),
    ((tail_x(1.04), 1.04, 0.215), 0.014, 0.013),
    ((tail_x(1.09), 1.09, 0.195), 0.0, 0.0),
]

# The head is laid out at 1:1 below, then enlarged by HEAD_K about the back of the skull
HEAD_K = 1.3
HEAD_PIVOT = Vector((0.0, -0.66, 0.66))


def hy(y):
    return HEAD_PIVOT.y + (y - HEAD_PIVOT.y) * HEAD_K


def hz(z):
    return HEAD_PIVOT.z + (z - HEAD_PIVOT.z) * HEAD_K


def P(x, y, z):
    return Vector((x * HEAD_K, hy(y), hz(z)))


def R(r):
    return tuple(c * HEAD_K for c in r)


# Long, deep skull; the tooth line sweeps up to the upturned snout tip (y, top, lip z, half width)
SKULL_ROWS = [
    (-0.66, 0.800, 0.580, 0.140),
    (-0.72, 0.828, 0.560, 0.158),   # wide temporal region
    (-0.78, 0.835, 0.548, 0.150),
    (-0.84, 0.820, 0.544, 0.128),   # orbits
    (-0.90, 0.782, 0.545, 0.108),
    (-0.96, 0.752, 0.550, 0.095),
    (-1.01, 0.735, 0.556, 0.086),   # canine region
    (-1.05, 0.722, 0.570, 0.076),
    (-1.09, 0.712, 0.594, 0.064),   # upturned premaxilla
    (-1.12, 0.700, 0.624, 0.046),
    (-1.138, 0.684, 0.650, 0.020),
]
SKULL_ROWS = [(hy(y), hz(t), hz(l), w * HEAD_K) for y, t, l, w in SKULL_ROWS]
JAW_ROWS = [  # lower jaw (y, lip z, bottom z, half width), deep at the chin
    (-0.66, 0.585, 0.480, 0.130),
    (-0.74, 0.562, 0.470, 0.124),
    (-0.84, 0.548, 0.470, 0.108),
    (-0.94, 0.550, 0.474, 0.090),
    (-1.02, 0.560, 0.478, 0.074),
    (-1.07, 0.578, 0.490, 0.060),
    (-1.105, 0.604, 0.515, 0.042),
    (-1.125, 0.624, 0.548, 0.016),
]
JAW_ROWS = [(hy(y), hz(t), hz(b), w * HEAD_K) for y, t, b, w in JAW_ROWS]
HINGE = P(0.0, -0.68, 0.570)
JAW_ROT = Matrix.Translation(HINGE) @ Matrix.Rotation(math.radians(7), 4, "X") @ Matrix.Translation(-HINGE)
EYE_Y, EYE_Z = hy(-0.845), hz(0.752)
CANINE_Y = hy(-1.005)

# pachyostotic bosses: (centre, radii) - used for the shapes, the rugose sculpt and the paint
BOSSES = []
for _sx in (1, -1):
    BOSSES += [
        (P(_sx * 0.082, -0.825, 0.810), R((0.058, 0.082, 0.036))),   # above the eye
        (P(_sx * 0.122, -0.765, 0.790), R((0.046, 0.052, 0.050))),   # postorbital boss
        (P(_sx * 0.040, -0.935, 0.752), R((0.030, 0.060, 0.016))),   # thickened nasal / prefrontal
    ]


def jugal_boss(sx):
    """The swollen jugal boss under the eye: bulges out sideways and curls up at its end."""
    p = [P(sx * 0.105, -0.815, 0.640), P(sx * 0.165, -0.818, 0.648),
         P(sx * 0.205, -0.814, 0.675), P(sx * 0.222, -0.806, 0.725)]
    return [oriented(P(sx * 0.122, -0.815, 0.645), R((0.058, 0.070, 0.052))),
            nh.tube(p, [0.052 * HEAD_K, 0.046 * HEAD_K, 0.037 * HEAD_K, 0.024 * HEAD_K], sides=16),
            oriented(p[-1] + Vector((0, 0, 0.004)), R((0.028, 0.030, 0.028)))]

LEG_DATA = []   # (side, foot centre, toe angles, toe lengths, toe radius)


def body(b):
    b.add(loft(densify(TORSO, 4), sides=26, power=2.15), FLANK)
    b.add(oriented((0, -0.36, 0.44), (0.18, 0.19, 0.15)), FLANK)                 # deep brisket
    b.add(oriented((0, 0.26, 0.58), (0.19, 0.16, 0.17), pitch=-6), FLANK)        # hips
    b.add(oriented((0, -0.67, 0.560), (0.140, 0.10, 0.11)), FLANK)               # throat
    for sx in (1, -1):
        b.add(oriented((sx * 0.12, -0.42, 0.60), (0.11, 0.15, 0.17)), FLANK)     # shoulder bulk
        b.add(oriented(P(sx * 0.105, -0.69, 0.74), R((0.065, 0.08, 0.075))), FLANK)  # jaw muscles


def head(b):
    b.add(loft(densify(profile(SKULL_ROWS), 3), sides=24, power=2.4), FLANK)
    for c, r in BOSSES:
        b.add(oriented(c, r), FLANK)
    for sx in (1, -1):
        for part in jugal_boss(sx):
            b.add(part, FLANK)
        b.add(oriented(P(sx * 0.068, -1.005, 0.600), R((0.030, 0.042, 0.050))), FLANK)   # canine root bulge
        b.add(oriented(P(sx * 0.040, -1.10, 0.665), R((0.030, 0.035, 0.040))), FLANK)      # incisor bulge


def leg(b, pts, radii, foot, foot_r, s, angs, lens, toe_r):
    b.add(nh.tube(pts, radii, sides=16), LEG)
    for p, r in zip(pts[1:-1], radii[1:-1]):
        b.add(oriented(p, (r * 1.08, r * 1.1, r * 1.1)), LEG)
    b.add(nh.tube([pts[-1], Vector(foot) + Vector((0, 0.01, 0.012))], [radii[-1], radii[-1] * 0.95], sides=12), LEG)
    b.add(oriented(foot, foot_r), LEG)
    LEG_DATA.append((s, Vector(foot), angs, lens, toe_r))


def limbs(b):
    for s in (-1, 1):
        # forelimb: semi-sprawling, elbow out, forearm down under it
        leg(b, [Vector((s * 0.22, -0.42, 0.56)), Vector((s * 0.35, -0.37, 0.34)), Vector((s * 0.345, -0.44, 0.10))],
            [0.115, 0.084, 0.064], (s * 0.350, -0.485, 0.032), (0.070, 0.082, 0.032), s,
            (-38, -17, 2, 21, 42), (0.046, 0.058, 0.062, 0.056, 0.042), 0.019)
        b.add(oriented((s * 0.27, -0.41, 0.48), (0.11, 0.13, 0.16), roll=s * -28), LEG)     # upper arm
        b.add(oriented((s * 0.35, -0.39, 0.24), (0.075, 0.075, 0.11)), LEG)                 # forearm
        # hind limb: more upright, knee forward
        leg(b, [Vector((s * 0.19, 0.26, 0.53)), Vector((s * 0.30, 0.15, 0.31)), Vector((s * 0.29, 0.30, 0.10))],
            [0.125, 0.088, 0.066], (s * 0.296, 0.255, 0.032), (0.072, 0.088, 0.032), s,
            (-32, -13, 4, 21, 38), (0.050, 0.062, 0.066, 0.060, 0.046), 0.020)
        b.add(oriented((s * 0.21, 0.24, 0.47), (0.12, 0.18, 0.17), pitch=25), LEG)          # thigh
        b.add(oriented((s * 0.295, 0.22, 0.21), (0.07, 0.085, 0.11), pitch=-25), LEG)       # calf


def toes(b):
    out = []
    for s, palm, angs, lens, r in LEG_DATA:
        for ang, ln in zip(angs, lens):
            a = math.radians(ang)
            d = Vector((s * math.sin(a), -math.cos(a), 0.0))
            base = palm + d * 0.04
            tip = base + d * ln + Vector((0, 0, -0.011))
            b.add(nh.tube([base, base + d * ln * 0.5 + Vector((0, 0, 0.004)), tip], [r, r * 0.9, r * 0.72],
                          sides=8), LEG)
            out.append((tip, d, r))
    return out


# ---------------------------------------------------------------- skin

def boss_weight(co):
    """0..1: how much this point lies on one of the thickened bosses."""
    w = 0.0
    for c, r in BOSSES:
        d = math.sqrt(sum(((co[i] - c[i]) / r[i]) ** 2 for i in range(3)))
        w = max(w, 1.0 - nh.smoothstep(0.75, 1.25, d))
    ax = abs(co.x)
    if hy(-0.88) < co.y < hy(-0.75) and hz(0.58) < co.z < hz(0.80) and ax > 0.13 * HEAD_K:   # jugal boss
        w = max(w, nh.smoothstep(0.13 * HEAD_K, 0.19 * HEAD_K, ax))
    return w


def lip_dist(co):
    if co.y > hy(-0.68) or co.y < hy(-1.14):
        return 1.0
    _t, lip, w = row_at(SKULL_ROWS, co.y)
    if abs(co.x) < w * 0.45:
        return 1.0
    return min(1.0, abs(co.z - lip) / 0.010)


def sculpt(bm):
    bm.normal_update()
    moves = []
    for v in bm.verts:
        co, n = v.co, v.normal
        d = 0.0016 * (1.0 - nh.smoothstep(0.0, 0.5, noise.cell(co * 55.0)))
        d += 0.0014 * noise.noise(co * 22.0)
        bw = boss_weight(co)
        if bw > 0.0:                                     # rugose, pitted bone
            d += 0.004 * bw * (1.0 - nh.smoothstep(0.0, 0.45, noise.cell(co * 38.0)))
        d -= 0.0045 * (1.0 - lip_dist(co))
        if -0.66 < co.y < -0.50 and co.z < 0.70:        # neck folds
            d -= 0.0025 * nh.smoothstep(0.7, 0.95, 0.5 + 0.5 * math.sin(co.y * 70.0 + co.z * 10.0))
        moves.append((v, n * d))
    for v, m in moves:
        v.co += m
    bm.normal_update()


def paint(co, n):
    c = nh.lerp(BELLY, FLANK, nh.smoothstep(-0.65, -0.12, n.z))
    c = nh.lerp(c, BACK, nh.smoothstep(0.15, 0.85, n.z))
    if co.z < 0.30:
        c = nh.lerp(LEG, c, nh.smoothstep(0.10, 0.30, co.z))
    # irregular dark blotches over the back and tail
    if co.y > -0.70:
        blot = noise.noise(co * 6.0) + 0.3 * noise.noise(co * 17.0)
        c = nh.lerp(c, BLOTCH, 0.6 * nh.smoothstep(0.25, 0.5, blot) * nh.smoothstep(-0.2, 0.4, n.z))
    if co.y < -0.64:
        c = nh.lerp(c, BACK, 0.3 * nh.smoothstep(0.2, 0.8, n.z))
        _t, lip, w = row_at(SKULL_ROWS, co.y)
        if co.z < lip - 0.004 and co.y < -0.68:
            c = nh.lerp(c, BELLY, 0.45 * nh.smoothstep(lip - 0.004, lip - 0.03, co.z))
        c = nh.lerp(c, LIP, 0.85 * (1.0 - lip_dist(co)))
        c = nh.lerp(c, BOSS, 0.8 * boss_weight(co))
    k = (1.0 + 0.08 * noise.noise(co * 16.0)) * (0.95 + 0.08 * (1.0 - nh.smoothstep(0.1, 0.6, noise.cell(co * 55.0))))
    return tuple(max(0.0, x * k) for x in c)


# ---------------------------------------------------------------- crisp details

def teeth(mb, surf, jaw_surf):
    # big upper incisors on the upturned premaxilla, jutting forward and down
    for y, ln, r, xk in ((-1.128, 0.040, 0.010, 0.35), (-1.112, 0.046, 0.011, 0.60), (-1.092, 0.046, 0.011, 0.78),
                         (-1.070, 0.040, 0.010, 0.85)):
        y, ln, r = hy(y), ln * HEAD_K, r * HEAD_K
        _t, lip, w = row_at(SKULL_ROWS, y)
        for sx in (1, -1):
            loc, _n = surf.hit((sx * w * xk, y, lip - 0.12), (0, 0, 1))
            if loc is None or loc.z > lip + 0.05:
                continue
            tip = Vector((loc.x, y - ln * 0.45, loc.z - ln * 0.85))
            mb.add(nh.tube([loc + Vector((0, 0, 0.008)), loc.lerp(tip, 0.5), tip], [r, r * 0.8, 0.0], sides=8),
                   TOOTH, smooth=True)
    # long canine each side, hanging outside the lower jaw
    for sx in (1, -1):
        _t, lip, w = row_at(SKULL_ROWS, CANINE_Y)
        _jt, _jb, jw = row_at(JAW_ROWS, CANINE_Y)
        x0 = max(w * 0.78, jw + 0.006)
        k = HEAD_K
        pts = [Vector((sx * w * 0.65, CANINE_Y, lip + 0.025 * k)), Vector((sx * x0, CANINE_Y, lip - 0.01 * k)),
               Vector((sx * (x0 + 0.003), CANINE_Y + 0.006 * k, lip - 0.050 * k)),
               Vector((sx * x0, CANINE_Y + 0.016 * k, lip - 0.090 * k))]
        mb.add(nh.tube(pts, [0.019 * k, 0.018 * k, 0.012 * k, 0.0], sides=10, scale_xy=(1.0, 0.75)),
               TOOTH, smooth=True)
    # cheek teeth
    y = hy(-0.97)
    while y < hy(-0.78):
        _t, lip, w = row_at(SKULL_ROWS, y)
        for sx in (1, -1):
            loc, _n = surf.hit((sx * w * 0.80, y, lip - 0.1), (0, 0, 1))
            if loc is not None and loc.z < lip + 0.05:
                mb.add(cone(loc + Vector((0, 0, 0.004)), Vector((loc.x, y, loc.z - 0.019)), 0.0070), TOOTH, smooth=False)
        y += 0.034
    # lower incisors (forward, interlocking) and a small lower canine
    up = JAW_ROT.to_3x3() @ Vector((0, 0, 1))
    fwd = JAW_ROT.to_3x3() @ Vector((0, -1, 0))
    for y, ln, r, xk in ((-1.112, 0.036, 0.009, 0.45), (-1.095, 0.040, 0.010, 0.66), (-1.075, 0.036, 0.009, 0.75),
                         (-1.045, 0.040, 0.010, 0.72)):
        y, ln, r = hy(y), ln * HEAD_K, r * HEAD_K
        jt, _jb, jw = row_at(JAW_ROWS, y)
        for sx in (1, -1):
            loc, _n = jaw_surf.hit(JAW_ROT @ Vector((sx * jw * xk, y, jt + 0.1)), -up)
            if loc is None:
                continue
            tip = loc + up * ln * 0.85 + fwd * ln * 0.45
            mb.add(nh.tube([loc - up * 0.008, loc.lerp(tip, 0.5), tip], [r, r * 0.8, 0.0], sides=8), TOOTH, smooth=True)


def head_details(mb, surf):
    for sx in (1, -1):
        loc, _n = surf.hit((sx * 0.5, EYE_Y, EYE_Z), (-sx, 0, 0))
        if loc is None:
            continue
        look = Vector((sx, -0.35, 0.15)).normalized()
        c = loc - look * 0.008
        mb.add(nh.ellipsoid(c, (0.020, 0.023, 0.019), subdivisions=2), EYE)
        mb.add(nh.ellipsoid(c + look * 0.014, (0.007, 0.010, 0.012), subdivisions=2), PUPIL)
        loc, _n = surf.hit(P(sx * 0.030, -1.12, 0.9), (0, -0.2, -1))
        if loc is not None:
            mb.add(nh.ellipsoid(loc, (0.010, 0.009, 0.008), subdivisions=1), PUPIL)
    # dark mouth lining between the slightly parted jaws
    mb.add(oriented(P(0, -0.86, 0.542), R((0.070, 0.20, 0.012)), pitch=-4, segments=14, rings=6), MOUTH)


def claws(mb, tips):
    for tip, d, r in tips:
        base = tip - d * 0.008 + Vector((0, 0, 0.006))
        end = tip + d * 0.028 + Vector((0, 0, -0.012))
        mb.add(nh.tube([base, base + d * 0.012, end], [r * 0.72, r * 0.52, 0.0], sides=6), CLAW)


# ---------------------------------------------------------------- build / preview

def build():
    LEG_DATA.clear()
    b = nh.MeshBuilder()
    body(b)
    head(b)
    limbs(b)
    claw_tips = toes(b)
    fused = b.fuse(voxel=0.0090, smooth=5, smooth_factor=0.5)
    sculpt(fused)
    fused = decimate(fused, 20000)

    jb = nh.MeshBuilder()
    jb.add(loft(densify(profile(JAW_ROWS, 0.95), 3), sides=18, power=2.3), FLANK)
    jfused = nh.transform(decimate(jb.fuse(voxel=0.0065, smooth=4, smooth_factor=0.5), 2000), JAW_ROT)

    surf, jaw_surf = Surface(fused), Surface(jfused)
    mb = nh.MeshBuilder()
    teeth(mb, surf, jaw_surf)
    head_details(mb, surf)
    claws(mb, claw_tips)
    mb.add(fused, paint)
    mb.add(jfused, lambda co, n: nh.lerp(paint(co, n), BELLY, 0.5 * nh.smoothstep(0.1, -0.7, n.z)))
    obj = mb.to_object(NAME, roughness=0.6)
    nh.ground_to_zero(obj)
    return obj


def render_head(path):
    scene = bpy.context.scene
    cam = scene.camera
    head_c = P(0.0, -0.92, 0.68)
    out = Path(path)
    for i, off in enumerate((Vector((0.65, -0.65, 0.18)), Vector((-0.80, -0.10, 0.02)), Vector((0.0, -0.95, 0.10)))):
        cam.location = head_c + off * HEAD_K
        cam.rotation_euler = (head_c - cam.location).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = str(out.with_name(f"{out.stem}_head{i}.png"))
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    nh.run(build, NAME, ground=(0.48, 0.40, 0.28), views=((35, 22), (-90, 6), (25, 65)))
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--render" in argv:
        render_head(argv[argv.index("--render") + 1])
