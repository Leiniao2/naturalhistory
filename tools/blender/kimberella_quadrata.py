"""
Procedural Kimberella quadrata (Ediacaran slug-like bilaterian) for map colonies.

An elongated oval animal gliding over the microbial mat: a stiff, raised, non-mineralised
dorsal "shell" (mantle) with fine concentric growth banding and a low median keel, ringed by
a broad, soft margin zone of transverse muscle bands that ends in a crenulated, frilly skirt.
At the front a muscular proboscis reaches out and down from under the shell to a small
head carrying a fan of tiny hooked teeth - the scratcher thought to have raked the fan-shaped
Kimberichnus grooves into the mat. Warm tan-brown shell, paler pinkish frill.
The body is one polar heightfield (top) over a flat creeping sole; proboscis and teeth are
crisp separate shells. Faces -Y, pivot at the body centre (Swim style), seen mostly from above.

Usage:
  blender --background --python tools/blender/kimberella_quadrata.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Kimberella.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_fish as nf  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

A, B = 0.36, 0.62       # half-width (X) and half-length (Y) of the body outline
SHELL_R = 0.74          # where the stiff shell gives way to the soft margin zone
SHELL_H = 0.20          # shell dome height
FRILLS = 34             # crenulations around the margin
SEGS = FRILLS * 3       # segments around (three per crenulation)
SOLE_Z = -0.035

SHELL = (0.60, 0.40, 0.22)       # warm tan-brown mantle
SHELL_LIGHT = (0.78, 0.60, 0.40)
BAND = (0.40, 0.25, 0.13)        # concentric growth bands
MARGIN = (0.78, 0.58, 0.48)      # soft muscular margin zone
MARGIN_DARK = (0.56, 0.38, 0.30)
FRILL = (0.90, 0.72, 0.64)       # pale pinkish frill edge
SOLE = (0.62, 0.48, 0.40)
PROBOSCIS = (0.72, 0.50, 0.42)
HEAD = (0.62, 0.40, 0.33)
TOOTH = (0.92, 0.86, 0.70)


def ring_radii():
    """Radial stations: a few on the dome, denser through the margin zone and frill."""
    dome = [SHELL_R * (i / 18) ** 0.8 for i in range(18)]   # 2 stations per growth band
    return dome + [SHELL_R - 0.012, SHELL_R + 0.015, 0.80, 0.85, 0.895, 0.935, 0.97, 1.0]


def outline(theta):
    """Unit outline (x, y) at angle theta (theta = -90 deg is the front, -Y): an egg, a little
    narrower at the front; the crenulated frill waves the outer edge in and out."""
    c, s = math.cos(theta), math.sin(theta)
    narrow = 1.0 - 0.13 * max(0.0, -s)
    return c * A * narrow, s * B


def frill_wave(theta):
    return math.cos(theta * FRILLS)


def height(r, theta):
    """Top surface height at polar station (r, theta)."""
    c, s = math.cos(theta), math.sin(theta)
    if r <= SHELL_R:
        t = r / SHELL_R
        h = SHELL_H * (1.0 - t ** 2.3) ** 0.55 + 0.035
        # concentric growth banding: shallow steps on the dome
        h -= 0.007 * (0.5 + 0.5 * math.cos(t * 8.0 * math.tau)) * t
        # low median keel along the length
        h += 0.018 * math.exp(-(c * t / 0.12) ** 2) * (1.0 - t ** 3)
        # the front of the shell rises a touch, where the proboscis tucks under
        h += 0.02 * max(0.0, -s) * t
        return h
    t = (r - SHELL_R) / (1.0 - SHELL_R)            # 0 at the shell rim, 1 at the frill edge
    h = 0.035 * (1.0 - t) ** 1.3
    h += 0.018 * frill_wave(theta) * nh.smoothstep(0.3, 1.0, t)   # crenulated ruffle
    return h


def top_color(r, theta, co):
    c_, s_ = math.cos(theta), math.sin(theta)
    if r <= SHELL_R + 0.005:
        t = r / SHELL_R
        c = nh.lerp(SHELL_LIGHT, SHELL, nh.smoothstep(0.0, 0.9, t))
        band = 0.5 + 0.5 * math.cos(t * 8.0 * math.tau)
        c = nh.lerp(c, BAND, nh.smoothstep(0.55, 1.0, band) * 0.6 * nh.smoothstep(0.1, 0.3, t))
        c = nh.lerp(c, SHELL_LIGHT, math.exp(-(c_ * t / 0.07) ** 2) * 0.4)   # pale keel
        c = nh.lerp(c, BAND, nh.smoothstep(0.93, 1.0, t) * 0.7)              # dark shell rim
        k = 1.0 + 0.08 * noise.noise(co * 18.0)
        return tuple(min(1.0, x * k) for x in c)
    t = (r - SHELL_R) / (1.0 - SHELL_R)
    # transverse muscle bands: radial stripes through the margin zone
    stripe = 0.5 + 0.5 * frill_wave(theta)
    c = nh.lerp(MARGIN, MARGIN_DARK, stripe * 0.4 * (1.0 - nh.smoothstep(0.7, 1.0, t)))
    return nh.lerp(c, FRILL, nh.smoothstep(0.55, 1.0, t))


def body():
    bm = bmesh.new()
    vcol = {}
    rs = ring_radii()
    rings = []
    for i, r in enumerate(rs):
        if i == 0:
            v = bm.verts.new((0.0, 0.0, height(0.0, 0.0)))
            vcol[v] = top_color(0.0, 0.0, v.co)
            rings.append([v])
            continue
        ring = []
        for k in range(SEGS):
            th = -math.pi / 2 + k / SEGS * math.tau
            ox, oy = outline(th)
            # the frill edge itself scallops in and out
            rr = r * (1.0 + 0.018 * frill_wave(th) * nh.smoothstep(0.9, 1.0, r))
            co = Vector((ox * rr, oy * rr, height(r, th)))
            v = bm.verts.new(co)
            vcol[v] = top_color(r, th, co)
            ring.append(v)
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        for k in range(SEGS):
            j = (k + 1) % SEGS
            if len(a) == 1:
                bm.faces.new([a[0], b[k], b[j]])
            else:
                bm.faces.new([a[k], b[k], b[j], a[j]])
    # flat creeping sole tucked just inside the frill
    sole = []
    for k in range(SEGS):
        th = -math.pi / 2 + k / SEGS * math.tau
        ox, oy = outline(th)
        v = bm.verts.new((ox * 0.95, oy * 0.95, SOLE_Z))
        vcol[v] = SOLE
        sole.append(v)
    edge = rings[-1]
    for k in range(SEGS):
        j = (k + 1) % SEGS
        bm.faces.new([edge[k], sole[k], sole[j], edge[j]])
    centre = bm.verts.new((0.0, 0.0, SOLE_Z))
    vcol[centre] = SOLE
    for k in range(SEGS):
        bm.faces.new([sole[(k + 1) % SEGS], sole[k], centre])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm, vcol


def proboscis(mb):
    """Muscular proboscis reaching forward and down from under the front of the shell, ending in
    a small head with a fan of hooked teeth that rake the mat."""
    y0 = -B * 0.80
    pts = [(0.0, y0 + 0.10, 0.03), (0.0, y0 - 0.01, 0.028), (0.0, y0 - 0.065, 0.012),
           (0.0, y0 - 0.11, -0.006), (0.0, y0 - 0.14, -0.018)]
    mb.add(nh.tube(pts, [0.095, 0.088, 0.078, 0.068, 0.060], sides=14, scale_xy=(1.0, 0.62)), PROBOSCIS)
    # annular wrinkles where the proboscis extends
    for k, t in enumerate((0.25, 0.45, 0.65)):
        p = Vector(pts[1]).lerp(Vector(pts[3]), t)
        r = 0.083 - 0.016 * t
        mb.add(nh.tube([p + Vector((0, 0.006, 0)), p - Vector((0, 0.006, 0))], [r, r], sides=12,
                       scale_xy=(1.0, 0.64)), nh.lerp(PROBOSCIS, HEAD, 0.6))
    tip = Vector(pts[-1])
    mb.add(nh.ellipsoid(tip + Vector((0, -0.018, -0.006)), (0.078, 0.042, 0.034), subdivisions=2), HEAD)
    # a fan of small teeth along the front-lower lip, curving down toward the mat
    n = 7
    for k in range(n):
        a = math.radians(-55 + 110 * k / (n - 1))
        base = tip + Vector((math.sin(a) * 0.055, -0.018 - math.cos(a) * 0.036, -0.022))
        out = Vector((math.sin(a), -math.cos(a), 0.0))
        mb.add(nh.tube([base, base + out * 0.018 + Vector((0, 0, -0.012)), base + out * 0.026 + Vector((0, 0, -0.030))],
                       [0.008, 0.005, 0.0], sides=4), TOOTH)


def build():
    mb = nh.MeshBuilder()
    bm, vcol = body()
    nf.add_colored(mb, bm, vcol)
    proboscis(mb)
    obj = mb.to_object("Kimberella", roughness=0.5)
    # pivot at the body centre: centre the thickness on z = 0
    zs = [v.co.z for v in obj.data.vertices]
    mid = (min(zs) + max(zs)) / 2
    for v in obj.data.vertices:
        v.co.z -= mid
    return obj


if __name__ == "__main__":
    nh.run(build, "Kimberella", background=(0.05, 0.14, 0.18), views=((30, 40), (0, 85), (-90, 12), (35, 20)))
