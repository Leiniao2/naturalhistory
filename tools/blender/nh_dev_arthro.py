"""
Shared pieces for the small Devonian land arthropods (palaeocharinus_rhyniensis.py,
attercopus_fimbriunguis.py, devonobius_delta.py, rhyniella_praecursor.py).

  * glossy(): cuticle colour fn - darker underneath, a soft specular highlight.
  * jointed(): a leg/palp from a list of joint points (tapering tube segments with small
    joint knobs).
  * leg(): a walking leg from a hip on the body out to a foot on the ground (z = 0):
    hip -> raised knee -> ankle -> foot, splayed out to the side.
  * plate(): a flattened ellipsoid body plate (tergite, carapace) with an edge tint.
  * finish_ground(): grounds the mesh (z = 0 at the feet) and prints the mapHip estimate.

Ground style: faces -Y, pivot on the ground. About 1-1.6 units long.
"""

import math

from mathutils import Vector

import nh_model as nh

LIGHT_DIR = Vector((-0.45, -0.55, 0.70)).normalized()


def glossy(base, dark=None, shine=(0.60, 0.56, 0.50), gloss=0.4):
    dark = dark or tuple(c * 0.35 for c in base)

    def color(co, n):
        c = nh.lerp(dark, base, nh.smoothstep(-0.5, 0.6, n.z))
        h = max(0.0, n.dot(LIGHT_DIR)) ** 16
        return nh.lerp(c, shine, h * gloss)
    return color


def jointed(mb, pts, radii, color, knob=None, sides=6):
    pts = [Vector(p) for p in pts]
    for i in range(len(pts) - 1):
        mb.add(nh.tube([pts[i], pts[i + 1]], [radii[i], radii[i + 1]], sides=sides), color)
        if knob is not None and 0 < i:
            mb.add(nh.ellipsoid(pts[i], (radii[i] * 1.1,) * 3, 1), knob)


def leg(mb, s, hip, reach, splay, knee_h, r, color, knob=None, tip_color=None):
    """hip: (x>0, y, z) on the body (mirrored by s); reach: forward(-)/back(+) y offset of
    the foot; splay: foot distance out from the midline; knee_h: knee height."""
    hx, hy, hz = hip
    h = Vector((s * hx, hy, hz))
    knee = Vector((s * (hx + (splay - hx) * 0.45), hy + reach * 0.4, knee_h))
    ankle = Vector((s * (hx + (splay - hx) * 0.85), hy + reach * 0.8, knee_h * 0.45))
    foot = Vector((s * splay, hy + reach, 0.0))
    jointed(mb, [h, knee, ankle], [r, r * 0.9, r * 0.7], color, knob)
    mb.add(nh.tube([ankle, foot], [r * 0.7, r * 0.25], sides=5), tip_color or color)


def plate(mb, centre, radii, color, segs=14, rings=7, flat_under=0.6):
    def deform(n):
        return flat_under if n.z < 0 else 1.0
    mb.add(nh.uv_ellipsoid(centre, radii, segs, rings, deform=deform), color)


def finish_ground(mb, name, hip_z, roughness=0.45):
    obj = mb.to_object(name, roughness=roughness)
    nh.ground_to_zero(obj)
    vs = obj.data.vertices
    xs, ys = [v.co.x for v in vs], [v.co.y for v in vs]
    off = Vector((-(min(xs) + max(xs)) / 2, -(min(ys) + max(ys)) / 2, 0))
    for v in vs:
        v.co += off
    top = max(v.co.z for v in vs)
    print(f"{name}: height {top:.3f}, mapHip ~ {hip_z / top:.2f}")
    return obj


GROUND_VIEWS = dict(ground=(0.30, 0.27, 0.19), views=((35, 30), (0, 75), (-90, 10)))
