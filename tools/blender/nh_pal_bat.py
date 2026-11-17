"""
Parametric early bat in flight for the Paleogene species in tools/blender/
(icaronycteris_index.py, palaeochiropteryx_tupaiodon.py).

Furred body and head with big ears, wings spread flat in the XY plane as thin
membranes stretched between arm and finger bones (slightly scalloped trailing edge),
a clawed thumb on the leading edge, hind legs and a tail with an optional tail
membrane. Faces -Y, pivot at the body centre (Swarm), wingspan along X.
"""

import math
from dataclasses import dataclass

from mathutils import Vector, noise

import nh_model as nh

EYE = (0.02, 0.02, 0.02)


@dataclass
class Spec:
    name: str
    span: float = 1.0           # half-span (wing tip x)
    chord: float = 0.42         # wing depth near the body
    body: tuple = (0.07, 0.17, 0.065)
    head_r: float = 0.06
    snout: float = 0.05
    ear: float = 0.07
    tail: float = 0.25
    tail_membrane: float = 0.6  # 0 = free tail, 1 = fully enclosed
    fur: tuple = (0.42, 0.32, 0.22)
    belly: tuple = (0.6, 0.5, 0.38)
    membrane: tuple = (0.22, 0.17, 0.14)
    bone: tuple = (0.15, 0.11, 0.09)
    voxel: float = 0.008


def wing_outline(s, sx):
    """Closed outline of one wing in XY (leading edge from the shoulder to the tip, back along the
    trailing edge scalloped between the finger tips, to the ankle)."""
    S, C = s.span, s.chord
    lead = [(0.06, -0.06), (0.30 * S, -0.13), (0.48 * S, -0.15), (0.75 * S, -0.10), (S, -0.02)]
    tips = [(S, -0.02), (0.80 * S, 0.20 * C / 0.42), (0.55 * S, 0.40 * C / 0.42), (0.30 * S, 0.42 * C / 0.42),
            (0.08, 0.20)]
    trail = []
    for (x0, y0), (x1, y1) in zip(tips, tips[1:]):
        for k in range(4):
            t = k / 4
            sc = math.sin(t * math.pi) * 0.05
            trail.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t - sc))
    trail.append(tips[-1])
    pts = lead + trail[1:]
    return [(sx * x, y, 0.0) for x, y in pts]


def build(s):
    b = nh.MeshBuilder()
    bx, by, bz = s.body
    b.add(nh.ellipsoid((0, 0.02, 0), s.body, subdivisions=3), s.fur)
    hc = Vector((0, -by - s.head_r * 0.5, 0.01))
    b.add(nh.ellipsoid(tuple(hc), (s.head_r, s.head_r * 1.1, s.head_r * 0.9)), s.fur)
    b.add(nh.ellipsoid(tuple(hc + Vector((0, -s.head_r - s.snout * 0.4, -0.01))), (s.head_r * 0.5, s.snout, s.head_r * 0.45)),
          s.fur)
    for sx in (-1, 1):
        e0 = hc + Vector((sx * s.head_r * 0.55, 0.0, s.head_r * 0.5))
        b.add(nh.tube([tuple(e0), tuple(e0 + Vector((sx * s.ear * 0.4, s.ear * 0.3, s.ear)))],
                      [s.ear * 0.45, s.voxel * 1.2], sides=8, scale_xy=(1.0, 0.5)), s.fur)
    # tail and legs
    t0 = Vector((0, by, 0))
    t1 = t0 + Vector((0, s.tail, -0.01))
    b.add(nh.tube([tuple(t0), tuple(t1)], [0.012, s.voxel * 1.1], sides=6), s.fur)
    for sx in (-1, 1):
        hip = Vector((sx * bx * 0.6, by * 0.7, 0))
        foot = hip + Vector((sx * 0.08, 0.12, -0.01))
        b.add(nh.tube([tuple(hip), tuple(foot)], [0.014, 0.01], sides=6), s.fur)
    fused = b.fuse(voxel=s.voxel, smooth=4, smooth_factor=0.5)

    def paint(co, n):
        c = nh.lerp(s.belly, s.fur, nh.smoothstep(-0.4, 0.3, n.z))
        return nh.lerp(c, tuple(x * 0.8 for x in s.fur), 0.3 * max(0.0, noise.noise(co * 40)))

    mb = nh.MeshBuilder()
    mb.add(fused, color=paint)
    for sx in (-1, 1):
        out = wing_outline(s, sx)
        if sx < 0:
            out = list(reversed(out))
        mem = nh.flat_panel(out, thickness=0.006)
        for v in mem.verts:   # gentle dihedral and billow
            x = abs(v.co.x)
            v.co.z += 0.06 * x - 0.03 * math.sin(min(1.0, x / s.span) * math.pi)
        mb.add(mem, s.membrane, smooth=False)
        # arm and finger bones along the membrane
        sh = Vector((sx * 0.06, -0.06, 0))
        wr = Vector((sx * 0.48 * s.span, -0.15, 0))
        for p in (sh, wr):
            p.z = 0.06 * abs(p.x) - 0.03 * math.sin(min(1.0, abs(p.x) / s.span) * math.pi) + 0.005
        bones = [(sh, wr)]
        for tx, ty in ((s.span, -0.02), (0.80 * s.span, 0.20 * s.chord / 0.42), (0.55 * s.span, 0.40 * s.chord / 0.42)):
            tp = Vector((sx * tx, ty, 0))
            tp.z = 0.06 * tx - 0.03 * math.sin(min(1.0, tx / s.span) * math.pi) + 0.005
            bones.append((wr, tp))
        for a, c in bones:
            mb.add(nh.tube([tuple(a), tuple(c)], [0.009, 0.004], sides=5), s.bone)
        # thumb claw
        mb.add(nh.tube([tuple(wr), tuple(wr + Vector((0, -0.05, 0.01)))], [0.008, 0.0], sides=5), s.bone)
    if s.tail_membrane > 0:
        L = s.tail * s.tail_membrane
        mem = nh.flat_panel([(-s.body[0] * 0.6 - 0.08, s.body[1] * 0.7 + 0.12, 0), (0, s.body[1] + L, 0),
                             (s.body[0] * 0.6 + 0.08, s.body[1] * 0.7 + 0.12, 0), (0, s.body[1] * 0.6, 0)],
                            thickness=0.005)
        mb.add(mem, s.membrane, smooth=False)
    for sx in (-1, 1):
        mb.add(nh.ellipsoid(tuple(hc + Vector((sx * s.head_r * 0.6, -s.head_r * 0.65, s.head_r * 0.25))), (0.012,) * 3,
                            subdivisions=1), EYE)
    obj = mb.to_object(s.name)
    return obj


def main(spec):
    nh.run(lambda: build(spec), spec.name, background=(0.10, 0.14, 0.20), views=((0, 70), (35, 25), (180, 40)))
