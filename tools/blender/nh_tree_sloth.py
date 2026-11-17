"""
Shared tree sloth builder for the living sloth scripts
(bradypus_tridactylus.py, choloepus_didactylus.py). Builds on nh_model and reuses the
small geometry helpers (oriented ellipsoids, smooth tubes, curved claws, decimation)
of nh_megatherium.py.

Tree sloths spend nearly all their lives hanging in the canopy, but the map shows
groups standing on their tile, so they are posed the way a sloth moves on the
ground: belly almost touching it, the long arms splayed out sideways and reaching
forward with the hooked claws dug in to drag the body along, the shorter hind legs
splayed behind, and the head held up on its neck looking ahead. One seamless fused
body (rounded trunk, neck, small round head with a short or longer snout, long thin
limbs, small hands and feet) is displaced into long, coarse, shaggy hair that hangs
down the flanks and limbs, short on the face; then repainted from a TreeSlothSpec:
coat with darker gaps between the locks and an optional greenish algal tinge, pale
face mask, optional dark eye stripe and pale throat, darker limbs. The long curved
claws (count per limb from the spec), small dark eyes and bare nose are crisp
details.

A TreeSlothSpec holds the proportions and colours; build(spec) returns the object.
Faces -Y, pivot on the ground (z = 0 under the hands, feet and belly), about 1.3
units long with the snout near y = -0.6. Legs reach below the stride hip line
(species.json "mapHip" about 0.35) so they swing when it walks.
"""

import math
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmesh  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_megatherium as meg  # noqa: E402
from mathutils import Vector, noise  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

TAG_COAT = (0.0, 0.0, 0.0)  # region tags painted before fusing (red = bare skin)
TAG_SKIN = (1.0, 0.0, 0.0)

# walking: left-front and right-hind forward (y offsets of the hands/feet)
STRIDE = {"lf": -0.05, "rf": 0.04, "lh": 0.04, "rh": -0.04}


@dataclass
class TreeSlothSpec:
    name: str
    voxel: float = 0.009
    max_tris: int = 6000
    head_r: float = 0.095    # cranium radius
    snout_len: float = 0.05  # how far the muzzle sticks out in front of the face
    snout_r: float = 0.045
    neck_len: float = 0.14
    arm_len: float = 1.0     # forelimb length multiplier (hind limbs fixed)
    fore_claws: int = 3
    hind_claws: int = 3
    claw_len: float = 0.10
    tail: float = 0.0        # stubby tail length (0 = none)
    hair_len: float = 0.022
    # colours
    coat: tuple = (0.45, 0.40, 0.33)
    coat_tip: tuple = (0.62, 0.57, 0.48)
    underfur: tuple = (0.22, 0.19, 0.15)
    algae: tuple = (0.42, 0.46, 0.33)
    algae_k: float = 0.0     # strength of the greenish tinge on the back
    limbs: tuple = (0.36, 0.31, 0.25)
    face: tuple = (0.80, 0.75, 0.64)
    mask: tuple = None       # dark eye stripe colour, None = no stripe
    throat: tuple = None     # pale throat colour, None = like the coat
    skin: tuple = (0.12, 0.10, 0.09)
    claw: tuple = (0.55, 0.50, 0.42)
    claw_tip: tuple = (0.25, 0.22, 0.18)
    eye: tuple = (0.04, 0.03, 0.025)


def head_c(s):
    return Vector((0, -0.30 - s.neck_len - s.head_r * 0.6, 0.33))


# ---------------------------------------------------------------- anatomy

def body(b, s):
    b.add(meg.oriented((0, 0.02, 0.19), (0.17, 0.33, 0.14), pitch=3, segments=24, rings=16), TAG_COAT)  # trunk
    b.add(meg.oriented((0, -0.20, 0.22), (0.15, 0.16, 0.14)), TAG_COAT)                   # chest/shoulders
    b.add(meg.oriented((0, 0.28, 0.19), (0.15, 0.14, 0.13)), TAG_COAT)                    # rump
    h = head_c(s)
    b.add(meg.smooth_tube([(0, -0.24, 0.24), (0, -0.30 - s.neck_len * 0.5, 0.29), (0, h.y + s.head_r * 0.6, h.z - 0.01)],
                          [0.10, 0.085, 0.075], sides=14), TAG_COAT)                        # long neck
    if s.tail > 0:
        b.add(meg.smooth_tube([(0, 0.36, 0.22), (0, 0.36 + s.tail, 0.19)], [0.04, 0.025], sides=10), TAG_COAT)


def head(b, s):
    h, r = head_c(s), s.head_r
    b.add(meg.oriented(tuple(h), (r, r * 0.95, r * 0.9)), TAG_COAT)                         # round cranium
    b.add(meg.oriented(tuple(h + Vector((0, -r * 0.55, -r * 0.15))), (r * 0.8, r * 0.5, r * 0.7)), TAG_COAT)  # flat face
    tip = h + Vector((0, -r * 0.85 - s.snout_len, -r * 0.3))
    b.add(meg.smooth_tube([tuple(h + Vector((0, -r * 0.6, -r * 0.2))), tuple(tip)],
                          [s.snout_r * 1.1, s.snout_r * 0.85], sides=12), TAG_COAT)          # muzzle
    b.add(meg.oriented(tuple(tip + Vector((0, -s.snout_r * 0.35, 0.004))), (s.snout_r * 0.75, s.snout_r * 0.45,
                                                                             s.snout_r * 0.6)), TAG_SKIN)  # bare nose


def fore_limb(b, out, s, sx):
    """Long arm splayed out and reaching forward, hand on the ground with claws hooked in."""
    L = s.arm_len
    st = STRIDE["lf" if sx < 0 else "rf"]
    sh = Vector((sx * 0.12, -0.20, 0.24))
    el = Vector((sx * (0.12 + 0.24 * L), -0.25 - 0.06 * L, 0.22))
    wr = Vector((sx * (0.14 + 0.30 * L), -0.30 - 0.22 * L + st, 0.05))
    b.add(meg.smooth_tube([tuple(sh), tuple(el), tuple(wr)], [0.06, 0.045, 0.035], sides=12), TAG_COAT)
    hc = wr + Vector((0, -0.03, -0.015))
    b.add(meg.oriented(tuple(hc), (0.035, 0.045, 0.025)), TAG_COAT)                         # small hand
    claws(out, s, hc, sx, s.fore_claws, s.claw_len)


def hind_limb(b, out, s, sx):
    st = STRIDE["lh" if sx < 0 else "rh"]
    hip = Vector((sx * 0.11, 0.26, 0.20))
    kn = Vector((sx * 0.30, 0.30, 0.20))
    an = Vector((sx * 0.34, 0.20 + st, 0.045))
    b.add(meg.smooth_tube([tuple(hip), tuple(kn), tuple(an)], [0.065, 0.045, 0.035], sides=12), TAG_COAT)
    fc = an + Vector((0, -0.035, -0.015))
    b.add(meg.oriented(tuple(fc), (0.035, 0.05, 0.025)), TAG_COAT)                          # foot
    claws(out, s, fc, sx, s.hind_claws, s.claw_len * 0.8)


def claws(out, s, c, sx, count, length):
    """Long hooked claws from the front of the hand: forward, then curving down and back."""
    for i in range(count):
        t = (i - (count - 1) / 2) / max(count - 1, 1)
        base = c + Vector((t * 0.035, -0.035, 0.02))
        out.append((meg.claw(base, (t * 0.25 + sx * 0.08, -0.9, 0.25), length, 0.009, 120, (1.0, 0.0, 0.0), sides=5),
                    base))


# ---------------------------------------------------------------- sculpt + paint

def strand(co):
    u = noise.noise(Vector((co.x * 70.0, co.y * 70.0, co.z * 8.0)))
    f = noise.noise(Vector((co.x * 180.0, co.y * 180.0, co.z * 22.0)))
    return max(0.0, min(1.0, 0.5 + 0.7 * u + 0.3 * f))


def shaggy(bm, w, s):
    """Long coarse hair hanging down from the back and limbs; short on the face, none on the nose."""
    bm.normal_update()
    h = head_c(s)
    moves = {}
    for v in bm.verts:
        fur = 1.0 - nh.smoothstep(0.2, 0.6, w[v])
        if fur <= 0.0:
            continue
        co, n = v.co.copy(), v.normal.copy()
        rel = co - h
        face = nh.smoothstep(-0.2, -0.75, rel.normalized().y) * (1.0 - nh.smoothstep(s.head_r * 1.1, s.head_r * 1.6,
                                                                                      rel.length))
        ground = 1.0 - nh.smoothstep(0.02, 0.08, co.z)
        amt = s.hair_len * fur * (1.0 - 0.85 * face) * (1.0 - 0.7 * ground)
        pat = strand(co)
        d = n * amt * (0.4 + 0.9 * pat) + Vector((0, 0, -1)) * amt * 0.5 * pat * max(0.0, 0.3 - n.z)
        moves[v] = d
    for v, d in moves.items():
        v.co += d
    for _ in range(2):
        bmesh.ops.smooth_vert(bm, verts=list(moves.keys()), factor=0.4, use_axis_x=True, use_axis_y=True,
                              use_axis_z=True)
    for v in bm.verts:
        v.co.z = max(v.co.z, 0.0)
    bm.normal_update()


def paint(bm, s):
    col = bm.loops.layers.color["Col"]
    w = meg.skin_weight(bm)
    h, r = head_c(s), s.head_r
    vc = {}
    for v in bm.verts:
        co, n = v.co, v.normal
        pat = strand(co)
        c = nh.lerp(s.underfur, s.coat, nh.smoothstep(0.15, 0.55, pat))
        c = nh.lerp(c, s.coat_tip, 0.5 * nh.smoothstep(0.55, 0.95, pat))
        # darker limbs away from the trunk
        limb = nh.smoothstep(0.17, 0.28, abs(co.x)) if co.z < 0.3 else 0.0
        c = nh.lerp(c, s.limbs, 0.7 * limb)
        if s.algae_k > 0:
            c = nh.lerp(c, s.algae, s.algae_k * max(0.0, n.z) * (0.6 + 0.4 * noise.noise(co * 12.0)))
        rel = co - h
        # pale throat running down the underside of the neck
        if s.throat is not None and rel.y > -r * 0.3 and co.y < -0.16 and n.z < 0.1:
            c = nh.lerp(c, s.throat, 0.85 * nh.smoothstep(0.1, -0.5, n.z) * nh.smoothstep(h.z + 0.02, h.z - 0.06, co.z))
        # pale face
        if rel.length < r * 1.6:
            front = nh.smoothstep(-0.1, -0.6, rel.normalized().y)
            c = nh.lerp(c, s.face, 0.9 * front * (1.0 - nh.smoothstep(r * 1.05, r * 1.4, rel.length)))
            # dark stripe from the eye back toward the ear
            if s.mask is not None:
                ez = h.z + r * 0.05
                ez = ez + max(0.0, rel.y + r * 0.6) * 0.25  # rising slightly toward the ear
                band = nh.smoothstep(r * 0.42, r * 0.22, abs(co.z - ez))
                side = nh.smoothstep(r * 0.18, r * 0.32, abs(rel.x))
                back = nh.smoothstep(r * 0.9, r * 0.4, rel.y)
                c = nh.lerp(c, s.mask, 0.95 * band * side * back)
        c = nh.lerp(c, s.skin, nh.smoothstep(0.35, 0.65, w[v]))
        vc[v] = c
    for f in bm.faces:
        for l in f.loops:
            c = vc[l.vert]
            l[col] = (c[0], c[1], c[2], 1.0)


def details(tree, s):
    out = []
    h, r = head_c(s), s.head_r
    for sx in (-1, 1):
        hit, n, _i, _d = tree.find_nearest(h + Vector((sx * r * 0.42, -r * 0.9, r * 0.05)))
        out.append((nh.ellipsoid(hit + n * 0.001, (r * 0.13, r * 0.10, r * 0.12), subdivisions=2), s.eye))
        if s.mask is not None:
            # dark stripe from the eye back toward the ear, laid on the fur (crisper than vertex paint)
            pts = []
            for k in range(6):
                u = k / 5
                q = h + Vector((sx * r * (0.42 + 0.5 * u), -r * (0.9 - 0.85 * u), r * (0.05 + 0.18 * u)))
                hit, n, _i, _d = tree.find_nearest(q)
                pts.append(hit + n * 0.0015)
            out.append((nh.tube(pts, [r * 0.24, r * 0.25, r * 0.23, r * 0.20, r * 0.14, 0.0], sides=6,
                                scale_xy=(1.0, 0.3)), s.mask))
    return out


def build(spec):
    s = spec
    b = nh.MeshBuilder()
    cl = []
    body(b, s)
    head(b, s)
    for sx in (-1, 1):
        fore_limb(b, cl, s, sx)
        hind_limb(b, cl, s, sx)
    fused = b.fuse(voxel=s.voxel, smooth=5, smooth_factor=0.5)
    w = meg.skin_weight(fused)
    shaggy(fused, w, s)
    fused = meg.decimate(fused, s.max_tris)
    paint(fused, s)
    tree = BVHTree.FromBMesh(fused)
    extra = details(tree, s)
    mb = nh.MeshBuilder()
    mb.add(fused)
    for bm, c in extra:
        mb.add(bm, c)
    for bm, base in cl:
        def fn(co, n, b0=Vector(base), L=s.claw_len):
            return nh.lerp(s.claw, s.claw_tip, nh.smoothstep(0.1 * L, 0.9 * L, (co - b0).length))
        mb.add(bm, fn)
    obj = mb.to_object(s.name, roughness=0.9)
    nh.ground_to_zero(obj)
    return obj
