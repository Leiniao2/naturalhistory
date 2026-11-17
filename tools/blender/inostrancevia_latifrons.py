"""
Procedural Inostrancevia latifrons (Late Permian gorgonopsid) for map colonies.

The second, rarer species of the giant gorgonopsian from the same North Dvina beds as
I. alexandri, and the only valid species named by Pravoslavlev. "Latifrons" means broad
forehead: it was larger and more robust than I. alexandri, its skull comparatively lower
and wider, with a broad, flat snout, a much wider parietal (skull-roof) region behind the
eyes bulked by the jaw muscles, and fewer teeth - but the same huge sabre canines.
Built on inostrancevia_alexandri.py (its helpers, sculpting and crisp details are reused
unchanged) with a heavier body: a broader, deeper chest and haunches, thicker limbs set a
little wider, and a low, wide, flat-topped head. Painted greyer and darker than
I. alexandri - smoky olive-brown with broad, broken dark saddle bands, a sooty face and a
buff belly - so the two read apart on the map.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/inostrancevia_latifrons.py -- [--render out.png]

Output: Assets/Resources/Models/Species/InostranceviaLatifrons.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import inostrancevia_alexandri as base  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402

NAME = "InostranceviaLatifrons"

# ---------------------------------------------------------------- colours (set on the base module,
# whose sculpt / detail helpers read them)
base.BACK = (0.33, 0.29, 0.21)       # smoky olive-brown
base.FLANK = (0.56, 0.50, 0.37)      # greyish khaki
base.BELLY = (0.80, 0.74, 0.60)      # buff
base.STRIPE = (0.13, 0.11, 0.08)
base.LEG = (0.42, 0.37, 0.27)
base.MASK = (0.20, 0.17, 0.13)       # sooty face
base.EYE = (0.80, 0.70, 0.22)        # paler yellow eye
BACK, FLANK, BELLY, STRIPE, LEG, MASK = base.BACK, base.FLANK, base.BELLY, base.STRIPE, base.LEG, base.MASK

# ---------------------------------------------------------------- anatomy (heavier, broader)


def _heavier(sections, wk, hk):
    return [(c, a * wk(c[1]), b * hk(c[1])) for c, a, b in sections]


# broader everywhere, deepest gain over the chest and haunches; the tail stays close to the original
base.TORSO = _heavier(
    base.TORSO,
    lambda y: 1.0 + 0.20 * (1.0 - nh.smoothstep(0.5, 0.95, y)),
    lambda y: 1.0 + 0.10 * (1.0 - nh.smoothstep(0.5, 0.95, y)),
)


def _skull(rows):
    """Lower and flatter snout, wider skull, much wider skull roof behind the eyes."""
    out = []
    for y, top, lip, w in rows:
        snout = nh.smoothstep(-0.70, -0.86, y)              # 0 at the back of the skull, 1 on the snout
        top = lip + (top - lip) * (0.97 - 0.17 * snout)     # lower, flat-topped snout
        wk = 1.42 - 0.20 * snout                            # broad forehead / parietal region
        out.append((y, top, lip, w * wk))
    return out


base.SKULL_ROWS = _skull(base.SKULL_ROWS)
base.JAW_ROWS = [(y, t, b, w * (1.30 - 0.14 * nh.smoothstep(-0.70, -0.86, y))) for y, t, b, w in base.JAW_ROWS]
row_at, oriented, loft, densify, profile = base.row_at, base.oriented, base.loft, base.densify, base.profile
EYE_Y, SABRE_Y = base.EYE_Y, base.SABRE_Y


def limbs(b):
    """As I. alexandri, but thicker-boned, more muscular and set a little wider."""
    LEG_DATA = base.LEG_DATA
    k = 1.17
    for s in (-1, 1):
        sh = Vector((s * 0.160, -0.36, 0.48))
        el = Vector((s * 0.232, -0.30, 0.285))
        wr = Vector((s * 0.225, -0.37, 0.065))
        b.add(oriented((s * 0.145, -0.36, 0.47), (0.10, 0.13, 0.15), pitch=-20), LEG)
        b.add(nh.tube([sh, sh.lerp(el, 0.5), el], [0.080 * k, 0.065 * k, 0.052 * k], sides=14), LEG)
        b.add(oriented(el, (0.050 * k, 0.055 * k, 0.052 * k)), LEG)
        b.add(nh.tube([el, el.lerp(wr, 0.45), wr], [0.050 * k, 0.045 * k, 0.032 * k], sides=12), LEG)
        b.add(oriented((s * 0.232, -0.33, 0.20), (0.054, 0.058, 0.082), pitch=15), LEG)
        hand = Vector((s * 0.228, -0.405, 0.024))
        b.add(nh.tube([wr, hand + Vector((0, 0.01, 0.006))], [0.032 * k, 0.03 * k], sides=10), LEG)
        b.add(oriented(hand, (0.046, 0.055, 0.024)), LEG)
        LEG_DATA.append((s, hand, (-32, -15, 0, 15, 32), (0.040, 0.050, 0.056, 0.052, 0.040), 0.014))
        hip = Vector((s * 0.150, 0.33, 0.50))
        kn = Vector((s * 0.205, 0.22, 0.30))
        an = Vector((s * 0.198, 0.38, 0.085))
        b.add(oriented((s * 0.145, 0.30, 0.46), (0.105, 0.19, 0.17), pitch=30), LEG)
        b.add(nh.tube([hip, hip.lerp(kn, 0.5), kn], [0.085 * k, 0.070 * k, 0.052 * k], sides=14), LEG)
        b.add(oriented(kn, (0.052 * k, 0.055 * k, 0.055 * k)), LEG)
        b.add(nh.tube([kn, kn.lerp(an, 0.5), an], [0.052 * k, 0.042 * k, 0.030 * k], sides=12), LEG)
        b.add(oriented((s * 0.205, 0.28, 0.24), (0.054, 0.08, 0.09), pitch=-35), LEG)
        foot = Vector((s * 0.200, 0.34, 0.024))
        b.add(nh.tube([an, foot + Vector((0, 0.012, 0.006))], [0.030 * k, 0.028 * k], sides=10), LEG)
        b.add(oriented(foot, (0.048, 0.062, 0.024)), LEG)
        LEG_DATA.append((s, foot, (-30, -13, 2, 17, 34), (0.045, 0.058, 0.066, 0.060, 0.044), 0.0145))


def body_paint(co, n):
    c = nh.lerp(BELLY, FLANK, nh.smoothstep(-0.7, -0.15, n.z))
    c = nh.lerp(c, BACK, nh.smoothstep(0.15, 0.85, n.z))
    if co.z < 0.30:
        c = nh.lerp(LEG, c, nh.smoothstep(0.12, 0.30, co.z))
    # fewer, broader saddle bands, broken into blotches toward the flanks
    if co.y > -0.50:
        wob = noise.noise(co * 4.0) * 1.8
        band = 0.5 + 0.5 * math.sin(co.y * 19.0 + co.z * 3.0 + wob)
        side = nh.smoothstep(-0.25, 0.3, n.z)
        blot = nh.smoothstep(-0.1, 0.35, noise.noise(co * 9.0) + n.z * 0.6)
        c = nh.lerp(c, STRIPE, 0.72 * nh.smoothstep(0.62, 0.86, band) * side * blot)
    if co.y < -0.55:
        c = nh.lerp(c, MASK, 0.65 * nh.smoothstep(0.0, 0.8, n.z))
        _t, lip, w = row_at(base.SKULL_ROWS, co.y)
        if co.z < lip - 0.004:
            c = nh.lerp(c, BELLY, 0.55 * nh.smoothstep(lip - 0.004, lip - 0.03, co.z))
        c = nh.lerp(c, base.LIP, 0.85 * (1.0 - base.lip_dist(co)))
        e = math.hypot((co.y - EYE_Y) / 0.07, (co.z - (row_at(base.SKULL_ROWS, co.y)[0] - 0.035)) / 0.025)
        c = nh.lerp(c, MASK, 0.6 * (1.0 - nh.smoothstep(0.6, 1.0, e)))
    m = noise.noise(co * 16.0)
    k = (1.0 + 0.08 * m) * (0.95 + 0.08 * (1.0 - nh.smoothstep(0.1, 0.6, noise.cell(co * 65.0))))
    return tuple(max(0.0, x * k) for x in c)


def teeth(mb, surf, jaw_surf):
    """Fewer teeth than I. alexandri: three upper incisors a side and only a couple of post-canines."""
    cone = base.cone
    for y, ln, r in ((-1.008, 0.030, 0.0075), (-0.990, 0.036, 0.0085), (-0.970, 0.033, 0.008)):
        _t, lip, w = row_at(base.SKULL_ROWS, y)
        for sx in (1, -1):
            loc, _n = surf.hit((sx * w * 0.70, y, lip - 0.1), (0, 0, 1))
            if loc is None or loc.z > lip + 0.05:
                continue
            mb.add(cone(loc + Vector((0, 0, 0.006)), Vector((loc.x, y + 0.004, loc.z - ln)), r),
                   base.TOOTH, smooth=False)
    for y in (-0.865, -0.825):
        _t, lip, w = row_at(base.SKULL_ROWS, y)
        for sx in (1, -1):
            loc, _n = surf.hit((sx * w * 0.80, y, lip - 0.1), (0, 0, 1))
            if loc is not None and loc.z < lip + 0.05:
                mb.add(cone(loc + Vector((0, 0, 0.004)), Vector((loc.x, y, loc.z - 0.012)), 0.0048),
                       base.TOOTH, smooth=False)
    up = base.JAW_ROT.to_3x3() @ Vector((0, 0, 1))
    for y, ln, r in ((-0.992, 0.024, 0.0065), (-0.972, 0.028, 0.007), (-0.945, 0.036, 0.009)):
        jt, _jb, jw = row_at(base.JAW_ROWS, y)
        for sx in (1, -1):
            loc, _n = jaw_surf.hit(base.JAW_ROT @ Vector((sx * jw * 0.62, y, jt + 0.1)), -up)
            if loc is None:
                continue
            mb.add(cone(loc - up * 0.006, loc + up * ln + Vector((0, -0.003, 0)), r), base.TOOTH, smooth=False)


def sabres(mb):
    """Same great sabres, a touch heavier, planted at the edge of the broader snout."""
    def col(co, n):
        return nh.lerp(base.TOOTH, base.SABRE_ROOT, nh.smoothstep(0.43, 0.47, co.z))
    for sx in (1, -1):
        _t, lip, w = row_at(base.SKULL_ROWS, SABRE_Y)
        _jt, _jb, jw = row_at(base.JAW_ROWS, SABRE_Y - 0.02)
        x0 = max(w * 0.80, jw + 0.004)
        pts = [Vector((sx * w * 0.70, SABRE_Y, lip + 0.03)),
               Vector((sx * x0, SABRE_Y + 0.002, lip - 0.01)),
               Vector((sx * (x0 + 0.004), SABRE_Y + 0.010, lip - 0.055)),
               Vector((sx * (x0 + 0.002), SABRE_Y + 0.024, lip - 0.100)),
               Vector((sx * x0, SABRE_Y + 0.040, lip - 0.135))]
        mb.add(nh.tube(pts, [0.022, 0.021, 0.017, 0.011, 0.0], sides=10, scale_xy=(1.0, 0.45)), col, smooth=True)


def head_details(mb, surf):
    """Eyes set into the side of the broad head (found on the surface), nostrils on the snout."""
    top, _lip, _w = row_at(base.SKULL_ROWS, EYE_Y)
    for sx in (1, -1):
        loc, _n = surf.hit((sx * 0.6, EYE_Y, top - 0.040), (-sx, 0, 0))
        if loc is None:
            continue
        e = loc + Vector((-sx * 0.006, 0, 0))
        mb.add(nh.ellipsoid(e, (0.019, 0.023, 0.018), subdivisions=2), base.EYE)
        mb.add(nh.ellipsoid(e + Vector((sx * 0.013, -0.003, 0)), (0.006, 0.011, 0.012), subdivisions=2), base.PUPIL)
        t2, _l2, w2 = row_at(base.SKULL_ROWS, -1.006)
        mb.add(nh.ellipsoid((sx * w2 * 0.6, -1.010, t2 - 0.010), (0.007, 0.007, 0.006), subdivisions=1), base.PUPIL)


def build():
    base.LEG_DATA.clear()
    b = nh.MeshBuilder()
    b.add(loft(densify(base.TORSO, 4), sides=24, power=2.1), FLANK)
    b.add(loft(densify(profile(base.SKULL_ROWS), 3), sides=20, power=2.7), FLANK)   # boxier, flat-topped
    b.add(oriented((0, -0.60, 0.53), (0.12, 0.085, 0.095)), FLANK)                   # throat
    for sx in (1, -1):
        b.add(oriented((sx * 0.105, -0.615, 0.595), (0.060, 0.075, 0.062)), FLANK)    # bulky jaw muscles
        _t = row_at(base.SKULL_ROWS, EYE_Y)
        b.add(oriented((sx * _t[2] * 0.72, EYE_Y, _t[0] - 0.036), (0.030, 0.038, 0.022)), FLANK)  # brow
        b.add(oriented((sx * 0.066, SABRE_Y, 0.53), (0.026, 0.036, 0.045)), FLANK)    # sabre root bulge
        b.add(oriented((sx * 0.085, -0.34, 0.50), (0.105, 0.14, 0.15)), FLANK)        # chest
        b.add(oriented((sx * 0.08, 0.30, 0.53), (0.085, 0.15, 0.11)), FLANK)          # heavy haunches
    limbs(b)
    claw_tips = base.toes(b)
    fused = b.fuse(voxel=0.0075, smooth=5, smooth_factor=0.5)
    base.sculpt(fused)
    fused = base.decimate(fused, 20000)

    jb = nh.MeshBuilder()
    jb.add(loft(densify(profile(base.JAW_ROWS, 0.95), 3), sides=18, power=2.5), FLANK)
    jfused = nh.transform(base.decimate(jb.fuse(voxel=0.006, smooth=4, smooth_factor=0.5), 2000), base.JAW_ROT)

    surf, jaw_surf = base.Surface(fused), base.Surface(jfused)
    mb = nh.MeshBuilder()
    teeth(mb, surf, jaw_surf)
    mb.add(fused, body_paint)
    mb.add(jfused, lambda co, n: nh.lerp(body_paint(co, n), BELLY, 0.5 * nh.smoothstep(0.1, -0.7, n.z)))
    mb.add(oriented((0, -0.79, 0.468), (0.070, 0.20, 0.012), pitch=-6, segments=14, rings=6), base.MOUTH)
    sabres(mb)
    head_details(mb, surf)
    base.claws(mb, claw_tips)
    obj = mb.to_object(NAME, roughness=0.65)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, ground=(0.44, 0.38, 0.27), views=((35, 22), (-90, 6), (25, 65)))
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--render" in argv:
        base.render_head(argv[argv.index("--render") + 1])
