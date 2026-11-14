"""
Procedural chimpanzee (Pan troglodytes) for map colonies.

An adult knuckle-walking on all fours: long, powerful arms that lift the
shoulders well above the hips so the back slopes down to the rump, short bent
legs on flat, grasping feet with a splayed big toe, and the hands curled so the
weight rests on the backs of the fingers. One seamless fused body (torso,
shoulders, arms, legs, neck, head with heavy brow ridge, protruding muzzle and
big sticking-out ears) with shaggy black hair displaced into the surface, then
repainted: coarse black coat with faint brown sheen, and bare pinkish-tan skin
on the face, ears, hands and feet. Crisp details on top: deep-set brown eyes
under the brow, nostrils, mouth line and fingernails.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/pan_troglodytes.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Chimpanzee.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Matrix, Vector, noise  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

FUR = (0.045, 0.040, 0.037)       # coarse black hair
FUR_SHEEN = (0.15, 0.12, 0.10)    # brownish highlights on the guard hairs
SKIN = (0.80, 0.62, 0.52)         # bare pinkish-tan face, ears, hands, feet
SKIN_DARK = (0.60, 0.44, 0.37)    # creases, brow, around the eyes
LIP = (0.66, 0.50, 0.44)
EYE = (0.24, 0.13, 0.06)
PUPIL = (0.02, 0.015, 0.01)
NOSTRIL = (0.12, 0.08, 0.07)
NAIL = (0.55, 0.47, 0.42)

TAG_FUR = (0.0, 0.0, 0.0)         # region tags painted before fusing (red = bare skin)
TAG_SKIN = (1.0, 0.0, 0.0)

VOXEL = 0.0115
MAX_TRIS = 11000

HEAD_C = Vector((0.0, -0.52, 0.70))
HEAD_S = 1.15  # head scale


def h(x, y, z):
    """Point relative to the head centre (head-local units, scaled by HEAD_S)."""
    return HEAD_C + Vector((x, y, z)) * HEAD_S


def hr(*r):
    return tuple(v * HEAD_S for v in r)


# ---------------------------------------------------------------- fused body parts

def body_parts():
    parts = []
    # torso: deep chest at the shoulders, slimmer waist, rounded rump lower down
    torso = [(0, -0.30, 0.64), (0, -0.20, 0.64), (0, -0.05, 0.60), (0, 0.12, 0.55), (0, 0.27, 0.50), (0, 0.34, 0.47)]
    parts.append((nh.tube(torso, [0.17, 0.205, 0.19, 0.165, 0.16, 0.10], sides=18, scale_xy=(1.0, 1.08)), TAG_FUR))
    parts.append((nh.ellipsoid((0, -0.20, 0.60), (0.20, 0.17, 0.19), subdivisions=3), TAG_FUR))   # chest
    parts.append((nh.ellipsoid((0, 0.26, 0.47), (0.16, 0.13, 0.15), subdivisions=3), TAG_FUR))    # rump
    for sx in (-1, 1):
        # muscular shoulders and shaggy upper back
        parts.append((nh.ellipsoid((sx * 0.15, -0.22, 0.68), (0.10, 0.12, 0.10), subdivisions=3), TAG_FUR))
    parts.append((nh.ellipsoid((0, -0.14, 0.72), (0.15, 0.20, 0.07), subdivisions=3), TAG_FUR))
    # short thick neck, head carried low and forward
    parts.append((nh.tube([(0, -0.28, 0.68), (0, -0.40, 0.70), h(0, 0.04, -0.01)], [0.12, 0.10, 0.09], sides=14), TAG_FUR))
    parts += head_parts()
    for sx in (-1, 1):
        parts += arm(sx)
        parts += leg(sx)
    return parts


def head_parts():
    p = []
    # rounded, low cranium sitting behind the brow
    p.append((nh.ellipsoid(h(0, 0.03, 0.03), hr(0.105, 0.115, 0.10), subdivisions=3), TAG_FUR))
    # bare face plate
    p.append((nh.ellipsoid(h(0, -0.065, -0.005), hr(0.083, 0.06, 0.08), subdivisions=3), TAG_SKIN))
    # heavy brow ridge, a continuous shelf over both eyes
    p.append((nh.tube([h(-0.085, -0.075, 0.045), h(-0.042, -0.118, 0.056), h(0, -0.122, 0.052),
                       h(0.042, -0.118, 0.056), h(0.085, -0.075, 0.045)],
                      [0.024, 0.029, 0.027, 0.029, 0.024], sides=10, scale_xy=(1.0, 0.8)), TAG_SKIN))
    # protruding muzzle: broad upper lip, flat nose, jutting chin
    p.append((nh.ellipsoid(h(0, -0.13, -0.058), hr(0.068, 0.065, 0.052), subdivisions=3), TAG_SKIN))
    p.append((nh.ellipsoid(h(0, -0.18, -0.062), hr(0.054, 0.035, 0.042), subdivisions=3), TAG_SKIN))
    p.append((nh.ellipsoid(h(0, -0.15, -0.108), hr(0.05, 0.05, 0.03), subdivisions=3), TAG_SKIN))
    # cheeks with a short fringe of hair at the sides of the face
    for sx in (-1, 1):
        p.append((nh.ellipsoid(h(sx * 0.07, -0.04, -0.05), hr(0.04, 0.06, 0.055), subdivisions=2), TAG_FUR))
        # big round ears standing out from the sides of the head
        ear = nh.ellipsoid((0, 0, 0), hr(0.016, 0.045, 0.052), subdivisions=3,
                           deform=lambda v: 1.0 - 0.25 * max(0.0, -v.x * 0.0 + v.y) ** 2)
        nh.transform(ear, Matrix.Rotation(math.radians(sx * -28), 4, "Z"))
        nh.transform(ear, Matrix.Translation(h(sx * 0.118, 0.025, 0.012)))
        p.append((ear, TAG_SKIN))
    return p


def arm(sx):
    """Long straight arm; the hand is curled into a fist resting on its finger knuckles."""
    x = sx * 0.18
    pts = [(x * 0.9, -0.22, 0.66), (x * 1.08, -0.25, 0.42), (x * 1.12, -0.27, 0.26), (x * 1.1, -0.30, 0.12)]
    p = [(nh.tube(pts, [0.075, 0.062, 0.055, 0.042], sides=12), TAG_FUR),
         (nh.ellipsoid((x * 1.1, -0.255, 0.30), (0.065, 0.07, 0.11), subdivisions=2), TAG_FUR)]  # hairy forearm
    hx, hy = x * 1.1, -0.31
    # back of the hand facing forward, fingers folded under: knuckle pads on the ground
    p.append((nh.ellipsoid((hx, hy, 0.075), (0.05, 0.035, 0.05), subdivisions=3), TAG_SKIN))
    p.append((nh.ellipsoid((hx, hy + 0.012, 0.03), (0.055, 0.045, 0.028), subdivisions=3), TAG_SKIN))
    for i in range(4):
        t = (i - 1.5) / 1.5
        p.append((nh.ellipsoid((hx + t * 0.032, hy - 0.012, 0.025), (0.017, 0.02, 0.022), subdivisions=2), TAG_SKIN))
    # thumb tucked against the inner side
    p.append((nh.tube([(hx - sx * 0.04, hy + 0.0, 0.07), (hx - sx * 0.055, hy - 0.02, 0.035)], [0.016, 0.012],
                      sides=6), TAG_SKIN))
    return p


def leg(sx):
    """Short bent leg: thigh forward, knee bent, shin back to a flat, grasping foot."""
    x = sx * 0.13
    pts = [(x, 0.28, 0.46), (x * 1.25, 0.16, 0.28), (x * 1.3, 0.26, 0.12), (x * 1.3, 0.25, 0.06)]
    p = [(nh.ellipsoid((x * 0.95, 0.24, 0.40), (0.085, 0.12, 0.12), subdivisions=3), TAG_FUR),   # thigh
         (nh.tube(pts, [0.075, 0.06, 0.05, 0.042], sides=12), TAG_FUR)]
    fx, fy = x * 1.32, 0.19
    p.append((nh.ellipsoid((fx, fy, 0.03), (0.048, 0.10, 0.032), subdivisions=3), TAG_SKIN))
    for i in range(4):
        t = i / 3.0
        p.append((nh.ellipsoid((fx + sx * (0.005 + t * 0.03), fy - 0.10 + t * 0.01, 0.018), (0.013, 0.025, 0.016),
                               subdivisions=2), TAG_SKIN))
    # opposable big toe splayed toward the midline
    p.append((nh.tube([(fx - sx * 0.035, fy - 0.03, 0.025), (fx - sx * 0.07, fy - 0.08, 0.018)], [0.017, 0.013],
                      sides=6), TAG_SKIN))
    return p


# ---------------------------------------------------------------- sculpt + paint

def skin_weight(bm):
    """Per-vertex 0..1 bare-skin weight from the fused region tags."""
    col = bm.loops.layers.color["Col"]
    w = {}
    for f in bm.faces:
        for l in f.loops:
            w[l.vert] = l[col][0]
    return w


def shaggy(bm, w):
    """Coarse hair: streaky displacement on the coat, longest on the shoulders and forearms."""
    bm.normal_update()
    moves = []
    for v in bm.verts:
        fur = 1.0 - nh.smoothstep(0.2, 0.6, w[v])
        if fur <= 0 or v.co.z < 0.05:
            moves.append(0.0)
            continue
        co, n = v.co, v.normal
        long = 1.0 + 1.2 * nh.smoothstep(0.55, 0.75, co.z) * nh.smoothstep(0.0, -0.25, co.y)  # shoulder cape
        streak = noise.noise(Vector((co.x * 55.0, co.y * 55.0, co.z * 14.0)))
        moves.append(fur * long * (0.003 + 0.004 * streak + 0.002 * noise.noise(co * 90.0)))
    for v, d in zip(bm.verts, moves):
        v.co += v.normal * d
    bm.normal_update()


def paint(bm, w):
    col = bm.loops.layers.color["Col"]
    for f in bm.faces:
        for l in f.loops:
            co, n = l.vert.co, l.vert.normal
            s = nh.smoothstep(0.35, 0.65, w[l.vert])
            hair = nh.lerp(FUR, FUR_SHEEN, max(0.0, noise.noise(Vector((co.x * 60, co.y * 60, co.z * 18)))) * 0.8)
            hair = nh.lerp(hair, FUR_SHEEN, 0.25 * max(0.0, n.z))
            skin = nh.lerp(SKIN, SKIN_DARK, 0.25 + 0.25 * noise.noise(co * 40.0))
            rel = co - HEAD_C
            if rel.length < 0.23:
                # darker skin on the brow and around the eyes, paler muzzle
                if rel.z > 0.0 and rel.y < -0.05:
                    skin = nh.lerp(skin, SKIN_DARK, 0.45)
                if rel.z < -0.04:
                    skin = nh.lerp(skin, SKIN, 0.6)
            c = nh.lerp(hair, skin, s)
            l[col] = (c[0], c[1], c[2], 1.0)


# ---------------------------------------------------------------- crisp details

def details(tree):
    out = []

    def snap(p):
        hit, normal, _i, _d = tree.find_nearest(Vector(p))
        return hit, normal

    for sx in (-1, 1):
        # deep-set eyes under the brow
        hit, n = snap(h(sx * 0.037, -0.16, 0.014))
        e = hit - n * 0.004
        out.append((nh.ellipsoid(e, hr(0.017, 0.012, 0.014), subdivisions=2), EYE))
        out.append((nh.ellipsoid(e + n * 0.011, (0.008, 0.005, 0.008), subdivisions=1), PUPIL))
        # nostrils on the flat nose
        hit, n = snap(h(sx * 0.013, -0.22, -0.035))
        out.append((nh.ellipsoid(hit + n * 0.002, (0.008, 0.005, 0.006), subdivisions=1), NOSTRIL))
    # mouth: a long line across the wide muzzle
    line = []
    for t in (-1, -0.5, 0, 0.5, 1):
        hit, n = snap(h(t * 0.05, -0.23, -0.088 + 0.012 * t * t))
        line.append(hit + n * 0.002)
    out.append((nh.tube(line, [0.004, 0.0055, 0.006, 0.0055, 0.004], sides=5), (0.20, 0.12, 0.10)))
    # pale lower lip
    hit, n = snap(h(0, -0.20, -0.105))
    out.append((nh.ellipsoid(hit + n * 0.002, (0.038, 0.012, 0.01), subdivisions=2), LIP))
    # toenails on the big toes
    for sx in (-1, 1):
        hit, n = snap((sx * 0.13 * 1.32 - sx * 0.072, 0.105, 0.03))
        out.append((nh.ellipsoid(hit + n * 0.003, (0.009, 0.009, 0.004), subdivisions=1), NAIL))
    return out


def build():
    body = nh.MeshBuilder()
    for bm, tag in body_parts():
        body.add(bm, tag)
    fused = body.fuse(voxel=VOXEL, smooth=5, smooth_factor=0.5, max_tris=MAX_TRIS)
    fused.normal_update()
    w = skin_weight(fused)
    shaggy(fused, w)
    paint(fused, w)
    tree = BVHTree.FromBMesh(fused)
    mb = nh.MeshBuilder()
    extra = details(tree)
    mb.add(fused)
    for bm, c in extra:
        mb.add(bm, c)
    obj = mb.to_object("Chimpanzee", roughness=0.8)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Chimpanzee", ground=(0.40, 0.48, 0.28), views=((35, 20), (-90, 8), (10, 10), (20, 60)))
