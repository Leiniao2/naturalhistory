"""
Procedural Plesiosaurus dolichodeirus (Early Jurassic plesiosaur) for the map (Swim style).

The classic long-necked plesiosaur from the Lias of southern England, about 3-3.5 m
long: a small, low, triangular head with a long mouth set with slender, outward-pointing
conical teeth; a very long, slim neck (longer than the trunk); a broad, flattened,
teardrop-shaped trunk with a stiff, flat belly; four large, wing-like flippers of
nearly equal size (fore and hind), held out to the sides as hydrofoils for
"underwater flight"; and a short, tapering tail.

The trunk, neck, head, tail and the four flipper slabs are fused into one seamless
surface (nh_model.MeshBuilder.fuse) and repainted analytically with countershading
(dark olive-grey back with paler blotches, grey flanks, a pale belly) and dark fins.
Colours are speculative. Crisp eyes, nostrils and teeth on top. The flippers are held
level so the map's wing-beat animation (wingBeat / wingRoot) can flap them.

Usage:
  blender --background --python tools/blender/plesiosaurus_dolichodeirus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Plesiosaurus.fbx
Pivot at the body centre, faces -Y, back up (+Z). About 2 units long.
"""

import math
import sys
from pathlib import Path

from mathutils import Vector, noise

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ichthyosaur as ich  # noqa: E402  (shared loft / fin-slab / interpolation tools)

VOXEL = 0.012

BACK = (0.17, 0.18, 0.15)       # dark olive-grey back
FLANK = (0.40, 0.41, 0.37)
BELLY = (0.85, 0.83, 0.74)
BLOTCH = (0.30, 0.31, 0.26)
FIN = (0.13, 0.14, 0.12)
MOUTH = (0.10, 0.06, 0.06)
TOOTH = (0.93, 0.90, 0.80)
EYE = (0.03, 0.03, 0.035)
EYE_RIM = (0.30, 0.28, 0.22)

Y_TIP, Y_END = -1.0, 0.92       # snout tip, tail tip
Y_EYE = -0.925
Y_JAW = -0.865                  # back of the gape

# body profile: small head, long neck, broad flat trunk, short tail
HALF_W = [(-1.0, 0.008), (-0.975, 0.020), (-0.94, 0.032), (-0.90, 0.044), (-0.87, 0.048), (-0.845, 0.038),
          (-0.70, 0.040), (-0.52, 0.054), (-0.40, 0.085), (-0.28, 0.170), (-0.10, 0.235), (0.08, 0.240),
          (0.24, 0.195), (0.38, 0.100), (0.48, 0.050), (0.66, 0.030), (0.82, 0.013), (0.92, 0.007)]
HALF_H_TOP = [(-1.0, 0.006), (-0.975, 0.014), (-0.94, 0.022), (-0.90, 0.032), (-0.87, 0.036), (-0.845, 0.033),
              (-0.70, 0.036), (-0.52, 0.048), (-0.40, 0.068), (-0.28, 0.100), (-0.10, 0.122), (0.08, 0.120),
              (0.24, 0.100), (0.38, 0.068), (0.50, 0.045), (0.70, 0.030), (0.83, 0.014), (0.92, 0.007)]
HALF_H_BOT = [(-1.0, 0.006), (-0.975, 0.014), (-0.94, 0.020), (-0.90, 0.026), (-0.87, 0.030), (-0.845, 0.031),
              (-0.70, 0.034), (-0.52, 0.045), (-0.40, 0.060), (-0.28, 0.085), (-0.10, 0.098), (0.08, 0.096),
              (0.24, 0.080), (0.38, 0.055), (0.50, 0.040), (0.70, 0.026), (0.83, 0.012), (0.92, 0.007)]
CENTER_Z = [(-1.0, 0.090), (-0.88, 0.094), (-0.70, 0.075), (-0.50, 0.040), (-0.32, 0.008), (-0.1, 0.0),
            (0.4, 0.0), (0.92, -0.03)]


def w(y): return ich.interp(HALF_W, y)
def ht(y): return ich.interp(HALF_H_TOP, y)
def hb(y): return ich.interp(HALF_H_BOT, y)
def zc(y): return ich.interp(CENTER_Z, y)


def section(y, a):
    c, s = math.cos(a), math.sin(a)
    n = 2.0 + 0.6 * nh.smoothstep(-0.42, -0.2, y) * nh.smoothstep(0.5, 0.3, y)   # trunk flatter, boxier
    x = w(y) * math.copysign(abs(c) ** (2.0 / n), c)
    hz = ht(y) if s >= 0 else hb(y)
    return Vector((x, y, zc(y) + hz * math.copysign(abs(s) ** (2.0 / n), s)))


# ---------------------------------------------------------------- flippers

FORE = dict(y=-0.24, length=0.58, chord=0.19, sweep=24.0, droop=6.0, tilt=-4.0)
HIND = dict(y=0.20, length=0.52, chord=0.175, sweep=30.0, droop=8.0, tilt=-4.0)


def wing_outline(length, chord, n=14):
    """Hydrofoil planform (u = chordwise, v = spanwise): a gently convex leading edge,
    a trailing edge that swells behind the root and then sweeps in to a narrow,
    backward-curving pointed tip."""
    lead, trail = [], []
    for i in range(n + 1):
        s = i / n
        c = chord * (1.0 + 0.30 * math.sin(math.pi * min(1.0, s * 1.4))) * max(0.0, 1.0 - s ** 1.8) ** 0.62
        back = 0.14 * length * s ** 2.4          # the tip curls backward
        lead.append((-c * 0.28 + back, s * length))
        trail.append((c * 0.72 + back, s * length))
    tip = (lead[-1][0], length * 1.01)
    return lead[:-1] + [tip] + list(reversed(trail[1:-1])) + [trail[0]]


def flipper(sign, spec):
    sw, dr = math.radians(spec["sweep"]), math.radians(spec["droop"])
    span = Vector((sign * math.cos(sw) * math.cos(dr), math.sin(sw), -math.sin(dr))).normalized()
    cdir = Vector((0.0, 1.0, math.sin(math.radians(spec["tilt"]))))
    cdir = (cdir - span * cdir.dot(span)).normalized()
    nrm = cdir.cross(span).normalized()
    if nrm.z < 0:
        nrm = -nrm
    y = spec["y"]
    origin = Vector((sign * w(y) * 0.78, y - spec["chord"] * 0.2, zc(y) - hb(y) * 0.35))
    pts = wing_outline(spec["length"], spec["chord"])
    th = []
    for u, v in pts:
        t = min(1.0, v / spec["length"])
        lead = 1.0 if u < spec["chord"] * 0.2 + 0.14 * spec["length"] * t ** 2.4 else 0.7
        th.append(max(0.028, 0.065 * (1.0 - 0.65 * t) * lead))
    return ich.fin_slab(pts, th, lambda u, v: (origin + cdir * u + span * v, nrm))


# ---------------------------------------------------------------- colour

def rel_z(p):
    y = max(min(p.y, Y_END), Y_TIP)
    d = p.z - zc(y)
    return d / max(ht(y) if d >= 0 else hb(y), 1e-3)


def outside(p):
    y = max(min(p.y, Y_END), Y_TIP)
    hz = ht(y) if p.z >= zc(y) else hb(y)
    r = math.sqrt((p.x / max(w(y), 1e-3)) ** 2 + ((p.z - zc(y)) / max(hz, 1e-3)) ** 2)
    return max(0.0, r - 1.0) * min(w(y), hz)


def mouth_r(y):
    return -0.15 - 0.05 * nh.smoothstep(Y_TIP, Y_JAW, y)


def body_color(p, n):
    y = p.y
    r = rel_z(p)
    wob = noise.noise(Vector((y * 6.0, p.x * 3.0, 0.4))) * 0.10
    line = -0.18 + wob
    col = nh.lerp(BELLY, FLANK, nh.smoothstep(line - 0.10, line + 0.10, r))
    col = nh.lerp(col, BACK, nh.smoothstep(line + 0.25, line + 0.70, r))
    # paler blotches scattered over the back
    b = noise.noise(p * 11.0 + Vector((5.0, 2.0, 1.0)))
    col = nh.lerp(col, BLOTCH, nh.smoothstep(0.30, 0.50, b) * 0.6 * nh.smoothstep(line, line + 0.4, r))
    # flippers: dark, with the colour fading in from the body
    yc = max(min(y, Y_END), Y_TIP)
    col = nh.lerp(col, FIN, max(nh.smoothstep(0.012, 0.035, outside(p)),
                                nh.smoothstep(0.9, 1.05, abs(p.x) / max(w(yc), 1e-3)) * nh.smoothstep(-0.35, -0.2, y)))
    # mouth line along the head
    if y < Y_JAW + 0.01:
        d = abs(r - mouth_r(y))
        col = nh.lerp(col, MOUTH, (1.0 - nh.smoothstep(0.06, 0.14, d)) * nh.smoothstep(Y_JAW + 0.01, Y_JAW - 0.01, y))
    return col


def skin_detail(bm):
    bm.normal_update()
    for v in bm.verts:
        y = v.co.y
        if y < Y_JAW + 0.01 and outside(v.co) < 0.01:
            d = abs(rel_z(v.co) - mouth_r(y))
            v.co -= v.normal * (1.0 - nh.smoothstep(0.0, 0.10, d)) * 0.0025
        v.co += v.normal * noise.noise(v.co * 32.0) * 0.0006


# ---------------------------------------------------------------- build

def teeth(mb):
    """Slender conical teeth splaying outward from the front of both jaws."""
    for sg in (-1, 1):
        for k in range(7):
            t = k / 6
            y = Y_TIP + 0.012 + t * 0.075
            r = mouth_r(y)
            x = sg * w(y) * 0.92
            z = zc(y) + (ht(y) if r >= 0 else hb(y)) * r
            ln = 0.022 - 0.010 * t
            for up in (1, -1):   # upper and lower teeth, alternating along the jaw
                yy = y + (0.005 if up < 0 else 0.0)
                base = Vector((x, yy, z + up * 0.002))
                tip = base + Vector((sg * ln * 0.55, -ln * 0.15, -up * ln * 0.75))
                mb.add(nh.tube([base, tip], [0.0035, 0.0], sides=5), TOOTH)


def build():
    parts = nh.MeshBuilder()
    grey = (0.5, 0.5, 0.5)
    parts.add(ich.loft(Y_TIP, Y_END, 170, 36, section), grey)
    for sg in (-1, 1):
        parts.add(flipper(sg, FORE), grey)
        parts.add(flipper(sg, HIND), grey)
    fused = parts.fuse(voxel=VOXEL, smooth=6, smooth_factor=0.5, max_tris=19000)
    skin_detail(fused)

    mb = nh.MeshBuilder()
    mb.add(fused, body_color)
    for sg in (-1, 1):
        # eyes set high on the skull, looking out and a little up
        c = Vector((sg * w(Y_EYE) * 0.80, Y_EYE, zc(Y_EYE) + ht(Y_EYE) * 0.50))
        mb.add(nh.ellipsoid(c, (0.013, 0.016, 0.012), subdivisions=2), EYE_RIM)
        mb.add(nh.ellipsoid(c + Vector((sg * 0.004, -0.001, 0.002)), (0.011, 0.013, 0.010), subdivisions=2), EYE)
        # nostrils just in front of the eyes
        y = Y_EYE - 0.030
        mb.add(nh.ellipsoid((sg * w(y) * 0.45, y, zc(y) + ht(y) * 0.92), (0.004, 0.007, 0.003), subdivisions=1), MOUTH)
    teeth(mb)
    obj = mb.to_object("Plesiosaurus", roughness=0.5)
    ich.centre(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Plesiosaurus", background=(0.05, 0.18, 0.24),
           views=((35, 25), (-90, 4), (20, 70), (25, 12), (180, -40)))
