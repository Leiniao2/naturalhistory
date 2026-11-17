"""
Procedural Dimetrodon borealis (Early Permian sphenacodont, ~1.7-2 m) for map colonies.

The northernmost Dimetrodon, from the red beds of Prince Edward Island, Canada. It was named
Bathygnathus borealis ("deep jaw") in 1854 from an upper jaw with its teeth - the first
synapsid fossil described - and moved to Dimetrodon in 2015. Only the snout is known, so the
rest follows its relatives: a smaller, slimmer animal than D. grandis (about 1.7-2 m against
~3 m) with a proportionally tall, deep snout and maxilla, the same differentiated teeth and a
sail, here presumed somewhat lower than in the big southern species.
Built on dimetrodon_grandis.py (its helpers, sail, spines, teeth and details are reused
unchanged) with a slimmer trunk and limbs, a deeper, shorter snout and a lower sail. The
model is built at D. grandis' units and then scaled down to its real size relative to it
(SIZE), though the game sizes animals by sizeCm anyway. Painted olive-grey with dark speckled
blotches and a pale throat; the sail is dusky at the base, flushed rust-red, with a pale rim.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/dimetrodon_borealis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/DimetrodonBorealis.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import dimetrodon_grandis as base  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402

NAME = "DimetrodonBorealis"
SIZE = 0.62          # ~1.85 m against D. grandis' ~3 m

# ---------------------------------------------------------------- colours (set on the base module)
base.BACK = (0.31, 0.29, 0.21)       # dark olive
base.FLANK = (0.50, 0.47, 0.35)      # olive-grey
base.BELLY = (0.78, 0.74, 0.60)
base.BAND = (0.13, 0.12, 0.09)
base.LEG = (0.34, 0.32, 0.24)
base.SAIL = (0.74, 0.34, 0.20)       # rust-red membrane
base.SAIL_LOW = (0.30, 0.26, 0.20)
base.SAIL_TOP = (0.88, 0.80, 0.62)
base.SPINE = (0.16, 0.13, 0.10)
base.EYE = (0.86, 0.66, 0.20)
BACK, FLANK, BELLY, BAND, LEG = base.BACK, base.FLANK, base.BELLY, base.BAND, base.LEG

# ---------------------------------------------------------------- anatomy

# a slimmer, lighter trunk (narrower more than shallower); the tail keeps its taper
base.TORSO = [(c, a * (0.84 if c[1] < 0.5 else 0.90), b * 0.94) for c, a, b in base.TORSO]


def _deep_snout(rows):
    """Bathygnathus: a tall, deep snout and maxilla; the tooth line stays where it was."""
    out = []
    for y, top, bot, w in rows:
        k = nh.smoothstep(-0.66, -0.80, y)            # 0 behind the eyes, 1 along the snout
        top += 0.040 * k * (1.0 - 0.55 * nh.smoothstep(-0.89, -0.936, y))
        out.append((y, top, bot, w * (1.0 - 0.06 * k)))
    return out


base.SKULL_ROWS = _deep_snout(base.SKULL_ROWS)
base.JAW_ROWS = [(y, t, b - 0.010 * nh.smoothstep(-0.70, -0.86, y), w) for y, t, b, w in base.JAW_ROWS]


def sail_height(y):
    """Lower crest than D. grandis, a little longer at the front."""
    t = (y - base.SAIL_Y0) / (base.SAIL_Y1 - base.SAIL_Y0)
    if t <= 0.0 or t >= 1.0:
        return 0.0
    s = math.sin(math.pi * t ** 0.9)
    return 0.44 * s ** 0.75


base.sail_height = sail_height
base.N_SPINES = 22
oriented, loft, densify, profile, row_at = base.oriented, base.loft, base.densify, base.profile, base.row_at


def limbs(b):
    """As D. grandis, with slimmer bones and muscles and a slightly narrower sprawl."""
    LEG_DATA = base.LEG_DATA
    k = 0.86
    for s in (-1, 1):
        sh = Vector((s * 0.105, -0.40, 0.29))
        el = Vector((s * 0.305, -0.42, 0.24))
        wr = Vector((s * 0.325, -0.47, 0.035))
        b.add(nh.tube([sh, el], [0.070 * k, 0.052 * k], sides=14), LEG)
        b.add(oriented((s * 0.21, -0.41, 0.27), (0.075, 0.046, 0.046)), LEG)
        b.add(oriented(el, (0.050 * k, 0.050 * k, 0.052 * k)), LEG)
        b.add(nh.tube([el, el.lerp(wr, 0.5) + Vector((s * 0.008, 0, 0)), wr],
                      [0.050 * k, 0.042 * k, 0.032 * k], sides=12), LEG)
        hand = Vector((s * 0.335, -0.50, 0.022))
        b.add(oriented(hand, (0.045, 0.055, 0.022)), LEG)
        LEG_DATA.append((s, hand, (-40, -18, 4, 26, 50), (0.048, 0.062, 0.068, 0.062, 0.044), 0.0115))
        hip = Vector((s * 0.095, 0.18, 0.29))
        kn = Vector((s * 0.325, 0.12, 0.25))
        an = Vector((s * 0.345, 0.20, 0.038))
        b.add(nh.tube([hip, kn], [0.090 * k, 0.058 * k], sides=14), LEG)
        b.add(oriented((s * 0.19, 0.17, 0.28), (0.088, 0.064, 0.060), yaw=-s * 8), LEG)
        b.add(oriented(kn, (0.055 * k, 0.055 * k, 0.058 * k)), LEG)
        b.add(nh.tube([kn, kn.lerp(an, 0.5), an], [0.055 * k, 0.046 * k, 0.034 * k], sides=12), LEG)
        foot = Vector((s * 0.355, 0.17, 0.022))
        b.add(oriented(foot, (0.050, 0.065, 0.022), yaw=-s * 20), LEG)
        LEG_DATA.append((s, foot, (-28, -8, 12, 32, 58), (0.058, 0.076, 0.088, 0.080, 0.054), 0.0125))


def body_paint(co, n):
    c = nh.lerp(BELLY, FLANK, nh.smoothstep(-0.65, -0.15, n.z))
    c = nh.lerp(c, BACK, nh.smoothstep(0.05, 0.75, n.z))
    if co.z < 0.22 and co.y < 0.32:
        c = nh.lerp(LEG, c, nh.smoothstep(0.10, 0.22, co.z) * nh.smoothstep(0.25, 0.10, abs(co.x)))
    # dark speckled blotches instead of D. grandis' transverse bands
    blot = noise.noise(co * 11.0) + 0.35 * noise.noise(co * 30.0)
    c = nh.lerp(c, BAND, 0.65 * nh.smoothstep(0.28, 0.5, blot) * nh.smoothstep(-0.45, 0.2, n.z))
    if co.y < -0.58:
        c = nh.lerp(c, BACK, 0.30 * nh.smoothstep(0.2, 0.8, n.z))
        _t, bot, w = row_at(base.SKULL_ROWS, co.y)
        if co.z < bot + 0.002:
            c = nh.lerp(c, BELLY, 0.55)
        c = nh.lerp(c, base.LIP, 0.8 * (1.0 - nh.smoothstep(0.003, 0.012, abs(co.z - bot - 0.006))) *
                    nh.smoothstep(w * 0.4, w * 0.7, abs(co.x)))
    m = noise.noise(co * 16.0)
    k = (1.0 + 0.1 * m) * (0.94 + 0.1 * (1.0 - nh.smoothstep(0.1, 0.6, noise.cell(co * 60.0))))
    return tuple(max(0.0, x * k) for x in c)


def head_details(mb):
    top, _bot, w = row_at(base.SKULL_ROWS, base.EYE_Y)
    for sx in (1, -1):
        e = Vector((sx * w * 0.84, base.EYE_Y, top - 0.042))
        mb.add(nh.ellipsoid(e, (0.018, 0.022, 0.018), subdivisions=2), base.EYE)
        mb.add(nh.ellipsoid(e + Vector((sx * 0.012, -0.002, 0)), (0.006, 0.010, 0.012), subdivisions=1), base.PUPIL)
        t2, _b2, w2 = row_at(base.SKULL_ROWS, -0.912)
        mb.add(nh.ellipsoid((sx * w2 * 0.66, -0.914, t2 - 0.024), (0.005, 0.008, 0.007), subdivisions=1), base.PUPIL)
    # dark mouth lining between the jaws, kept behind the narrower snout tip
    mb.add(oriented((0, -0.745, 0.302), (0.036, 0.15, 0.010), pitch=-3, segments=14, rings=6), base.MOUTH)


def build():
    base.LEG_DATA.clear()
    b = nh.MeshBuilder()
    b.add(loft(densify(base.TORSO, 4), sides=24, power=2.1), FLANK)
    b.add(loft(densify(profile(base.SKULL_ROWS), 3), sides=20, power=2.5), FLANK)
    b.add(oriented((0, -0.60, 0.37), (0.066, 0.08, 0.075)), FLANK)                   # throat / jaw muscles
    for sx in (1, -1):
        b.add(oriented((sx * 0.056, base.EYE_Y, row_at(base.SKULL_ROWS, base.EYE_Y)[0] - 0.035),
                       (0.028, 0.040, 0.028)), FLANK)
        b.add(oriented((sx * 0.055, -0.58, 0.41), (0.036, 0.06, 0.05)), FLANK)        # temporal muscle
        b.add(oriented((sx * 0.065, -0.40, 0.30), (0.068, 0.10, 0.095)), FLANK)       # chest
        b.add(oriented((sx * 0.06, 0.26, 0.30), (0.05, 0.16, 0.075)), FLANK)          # tail-base muscle
    limbs(b)
    claw_tips = base.toes(b)
    fused = b.fuse(voxel=0.0075, smooth=5, smooth_factor=0.5)
    base.sculpt(fused)
    fused = base.decimate(fused, 16000)

    jb = nh.MeshBuilder()
    jb.add(loft(densify(profile(base.JAW_ROWS, 0.86), 3), sides=16, power=2.3), FLANK)
    jfused = nh.transform(base.decimate(jb.fuse(voxel=0.0055, smooth=4, smooth_factor=0.5), 1600), base.JAW_ROT)

    surf, jaw_surf = base.Surface(fused), base.Surface(jfused)
    mb = nh.MeshBuilder()
    base.teeth(mb, surf, jaw_surf)
    mb.add(fused, body_paint)
    mb.add(jfused, lambda co, n: nh.lerp(body_paint(co, n), BELLY, 0.45 * nh.smoothstep(0.0, -0.8, n.z)))
    mb.add(base.sail_membrane(), base.sail_paint)
    base.spines(mb)
    head_details(mb)
    base.claws(mb, claw_tips)
    obj = mb.to_object(NAME, roughness=0.65)
    nh.ground_to_zero(obj)
    obj.data.transform(Matrix.Scale(SIZE, 4))     # real size relative to D. grandis
    return obj


def render_head(path):
    scene = bpy.context.scene
    cam = scene.camera
    head = Vector((0.0, -0.78, 0.33)) * SIZE
    out = Path(path)
    for i, off in enumerate((Vector((0.42, -0.42, 0.12)), Vector((-0.55, -0.12, 0.02)))):
        cam.location = head + off * SIZE
        cam.rotation_euler = (head - cam.location).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = str(out.with_name(f"{out.stem}_head{i}.png"))
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    nh.run(build, NAME, ground=(0.46, 0.38, 0.26), views=((35, 22), (-90, 6), (25, 65)))
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--render" in argv:
        render_head(argv[argv.index("--render") + 1])
