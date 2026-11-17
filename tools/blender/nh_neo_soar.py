"""
Shared soaring bird for the Neogene batch (tag "neo"): Argentavis (a teratorn,
broad condor-like wings with splayed primaries) and Pelagornis (a pelagornithid,
long narrow albatross-like wings and a long bill with bony pseudo-teeth).

Wings spread flat along X (the game flaps them about the body, see wingRoot),
fused body / neck / head / tail, flat wing panels with primary "fingers" and
an optional serrated bill. Faces -Y, pivot at the body centre (flier).
"""

import math
from dataclasses import dataclass

from mathutils import Vector, noise

import nh_model as nh

EYE = (0.55, 0.35, 0.12)
PUPIL = (0.02, 0.02, 0.02)


@dataclass
class Spec:
    name: str
    span: float = 3.0            # wingspan
    chord: float = 0.45          # wing chord at the root
    tip_chord: float = 0.30
    fingers: int = 6             # splayed primaries at the tip (0 = pointed tip)
    finger_len: float = 0.30
    body: tuple = (0.14, 0.42, 0.13)
    neck_len: float = 0.15
    head_r: float = 0.07
    beak_len: float = 0.14
    beak_r: float = 0.035
    hook: float = 0.6
    teeth: int = 0               # pseudo-teeth along each jaw edge
    tail: float = 0.25
    tail_w: float = 0.18
    plumage: tuple = (0.12, 0.10, 0.09)
    under: tuple = (0.30, 0.28, 0.26)
    wing_top: tuple = None
    head_col: tuple = None
    beak_col: tuple = (0.80, 0.75, 0.62)
    voxel: float = 0.014
    max_tris: int = 6000


def wing(s, sx):
    """Flat wing panel along +-X with a swept leading edge; returns (bmesh, finger tubes)."""
    half = s.span / 2
    root = s.body[0] * 0.7
    tipx = half - (s.finger_len if s.fingers else 0)
    le = []   # leading edge from root to tip
    te = []
    n = 8
    for i in range(n + 1):
        t = i / n
        x = root + (tipx - root) * t
        sweep = 0.08 * math.sin(t * math.pi) - 0.10 * t * t
        c = s.chord + (s.tip_chord - s.chord) * t
        le.append(Vector((sx * x, -c * 0.45 + sweep * -1 - 0.0, 0.015 * math.sin(t * math.pi))))
        te.append(Vector((sx * x, c * 0.55 - sweep * 0.5 + (0.03 if (i % 2) else 0) * t, 0.0)))
    outline = le + list(reversed(te))
    if sx < 0:
        outline = list(reversed(outline))
    bm = nh.flat_panel([tuple(p) for p in outline], thickness=0.022)
    tubes = []
    if s.fingers:
        for k in range(s.fingers):
            f = k / max(1, s.fingers - 1)
            y0 = le[-1].y * (1 - f) + te[-1].y * f
            base = Vector((sx * (tipx - 0.03), y0 * 0.85, 0.0))
            ang = math.radians(-25 + 50 * f)
            d = Vector((sx * math.cos(ang), math.sin(ang), 0.05 + 0.08 * (1 - f)))
            L = s.finger_len * (1.0 - 0.35 * abs(f - 0.3))
            tubes.append(nh.tube([tuple(base), tuple(base + d * L)], [s.tip_chord * 0.09, 0.006], sides=6,
                                 scale_xy=(1.0, 0.35)))
    return bm, tubes


def build(s):
    b = nh.MeshBuilder()
    bw, bl, bh = s.body
    b.add(nh.ellipsoid((0, 0, 0), (bw, bl, bh), subdivisions=4), s.plumage)
    nb = Vector((0, -bl * 0.8, bh * 0.15))
    hc = nb + Vector((0, -s.neck_len, bh * 0.15))
    b.add(nh.tube([tuple(nb), tuple(hc)], [bh * 0.7, s.head_r * 0.8], sides=10), s.plumage)
    b.add(nh.ellipsoid(tuple(hc), (s.head_r * 0.85, s.head_r * 1.15, s.head_r)), s.head_col or s.plumage)
    bb = hc + Vector((0, -s.head_r * 0.8, -s.head_r * 0.1))
    pts, rr = [], []
    for i in range(6):
        t = i / 5
        pts.append(tuple(bb + Vector((0, -s.beak_len * t, -s.hook * s.beak_r * 1.5 * nh.smoothstep(0.7, 1.0, t)))))
        rr.append(max(s.beak_r * (1 - 0.5 * t), s.voxel * 0.7))
    b.add(nh.tube(pts, rr, sides=10, scale_xy=(0.8, 1.0)), s.beak_col)
    # wedge tail
    tr = Vector((0, bl * 0.8, 0))
    b.add(nh.flat_panel([tuple(tr + Vector(p)) for p in
                         ((-bw * 0.6, 0, 0), (bw * 0.6, 0, 0), (s.tail_w, s.tail, 0), (-s.tail_w, s.tail, 0))],
                        thickness=0.025), s.plumage)
    fused = b.fuse(voxel=s.voxel, smooth=3, smooth_factor=0.5, max_tris=s.max_tris)
    mb = nh.MeshBuilder()
    col = fused.loops.layers.color.get("Col")
    fused.normal_update()
    for f in fused.faces:
        for l in f.loops:
            c = l[col]
            c = (c[0], c[1], c[2])
            if l.vert.normal.z < -0.3 and abs(l.vert.co.x) < bw * 1.2 and c != s.beak_col:
                c = nh.lerp(c, s.under, 0.5)
            l[col] = (c[0], c[1], c[2], 1.0)
    mb.add(fused)
    wt = s.wing_top or s.plumage

    def wcol(co, n):
        c = wt if n.z >= 0 else s.under
        return nh.lerp(c, nh.lerp(c, (0, 0, 0), 0.4), 0.3 * max(0.0, noise.noise(co * 12)))
    for sx in (-1, 1):
        bm, tubes = wing(s, sx)
        mb.add(bm, wcol, smooth=False)
        for t in tubes:
            mb.add(t, s.plumage)
    if s.teeth:
        for i in range(s.teeth):
            t = 0.12 + 0.8 * i / s.teeth
            p = bb + Vector((0, -s.beak_len * t, -s.beak_r * (1 - 0.5 * t) * 0.85))
            for sx in (-1, 1):
                q = p + Vector((sx * s.beak_r * 0.35, 0, 0))
                mb.add(nh.tube([tuple(q), tuple(q + Vector((0, 0, -s.beak_r * (0.5 if i % 2 else 0.9))))],
                               [s.beak_r * 0.16, 0.0], sides=5), s.beak_col)
    for sx in (-1, 1):
        e = hc + Vector((sx * s.head_r * 0.75, -s.head_r * 0.3, s.head_r * 0.25))
        mb.add(nh.ellipsoid(tuple(e), (s.head_r * 0.18,) * 3, subdivisions=2), EYE)
        mb.add(nh.ellipsoid(tuple(e + Vector((sx * s.head_r * 0.1, -s.head_r * 0.04, 0))), (s.head_r * 0.09,) * 3,
                            subdivisions=1), PUPIL)
    obj = mb.to_object(s.name)
    print(f"{s.name}: span {s.span:.2f}, body half-width {bw:.3f}, wingRoot ~ {bw / (s.span / 2):.2f}")
    return obj


def main(spec):
    nh.run(lambda: build(spec), spec.name, views=((30, 35), (0, 75), (-90, 5)))
