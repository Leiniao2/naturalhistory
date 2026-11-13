"""
Procedural low-poly giant panda (Ailuropoda melanoleuca) for map colonies.

A chunky, fluffy bear standing on three legs, its right front paw raised to
hold a bamboo stalk up to its mouth, head lowered and turned toward it.
White body with a slight shoulder hump and a soft fur-noise silhouette; the
black shoulder saddle wraps under the chest into the front legs; the black hind
legs flow up into rounded haunches. The face has a white snout with a black
nose and mouth line, tilted teardrop eye patches and round black ears. Paws are
rounded with toe pads and pale claw tips.

The body is cut along flat planes (bisect) where the markings change, so the
black/white edges are clean lines instead of vertex-colour blur or sawteeth.

Usage:
  blender --background --python tools/blender/giant_panda.py -- [--render out.png]

Output: Assets/Resources/Models/Species/GiantPanda.fbx (faces -Y, pivot on the ground)
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Euler, Matrix, Vector, noise  # noqa: E402

WHITE = (0.95, 0.94, 0.89)
WHITE_UNDER = (0.78, 0.76, 0.70)  # shaded, slightly dingy belly and inner legs
SNOUT = (0.97, 0.96, 0.92)
BLACK = (0.06, 0.06, 0.07)
PAD = (0.16, 0.14, 0.14)
CLAW = (0.80, 0.76, 0.66)
NOSE = (0.02, 0.02, 0.02)
MOUTH = (0.10, 0.08, 0.08)
EYE = (0.16, 0.10, 0.07)
GLINT = (0.95, 0.95, 0.95)
BAMBOO = (0.38, 0.64, 0.20)
BAMBOO_NODE = (0.58, 0.72, 0.30)
LEAF = (0.22, 0.52, 0.14)

BODY_C = Vector((0.0, 0.04, 0.46))
BODY_R = (0.31, 0.46, 0.30)
RUMP_C = Vector((0.0, 0.27, 0.45))
RUMP_R = (0.29, 0.26, 0.28)

SADDLE_HALF = 0.12
SADDLE_SLANT = 0.35   # the band leans back toward the spine
HAUNCH_TOP = 0.36     # hind quarters are black below this height...
HAUNCH_FRONT = 0.17   # ...and behind this point

HEAD_C = Vector((0.02, -0.60, 0.60))
HEAD_TURN = 20        # degrees toward the raised paw (+X)
HEAD_DIP = 8         # degrees nose-down


def fur(v, amount=1.0, seed=0.0):
    """Radial multiplier for a fluffy, slightly lumpy silhouette."""
    o = Vector((seed, seed * 1.7, seed * 0.3))
    return 1.0 + amount * (0.035 * noise.noise(v * 2.3 + o) + 0.015 * noise.noise(v * 6.0 + o))


def white_shade(co, n):
    # warm white on top, shading to a dingier cream on the belly and inner legs
    return nh.lerp(WHITE_UNDER, WHITE, nh.smoothstep(0.22, 0.52, co.z))


# ---------------------------------------------------------------- body + markings

def saddle_centre(z):
    return -0.20 + (z - BODY_C.z) * SADDLE_SLANT


def cut(bm, co, no):
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    bmesh.ops.bisect_plane(bm, geom=geom, plane_co=co, plane_no=no)
    return bm


def cut_markings(bm):
    no = Vector((0, 1, -SADDLE_SLANT)).normalized()
    for off in (-SADDLE_HALF, SADDLE_HALF):
        cut(bm, Vector((0, saddle_centre(BODY_C.z) + off, BODY_C.z)), no)
    cut(bm, Vector((0, HAUNCH_FRONT, 0)), Vector((0, 1, 0)))
    return cut(bm, Vector((0, 0, HAUNCH_TOP)), Vector((0, 0, 1)))


def body_deform(v):
    # shoulder hump: a rise over the front of the back
    hump = math.exp(-((v.y + 0.5) ** 2 + v.x ** 2 * 2.0) / 0.12) * max(0.0, v.z) * 0.10
    belly = 0.04 * max(0.0, -v.z)
    return fur(v, seed=1.0) + 0.05 * max(0.0, v.z) + hump - belly


def body_shell():
    return cut_markings(nh.ellipsoid(BODY_C, BODY_R, subdivisions=4, deform=body_deform))


def rump_shell():
    return cut_markings(nh.ellipsoid(RUMP_C, RUMP_R, subdivisions=3, deform=lambda v: fur(v, seed=4.0)))


def split(make, inside):
    """Two copies of a shell: faces whose centre passes inside(c) vs the rest."""
    parts = []
    for keep_inside in (True, False):
        bm = make()
        drop = [f for f in bm.faces if inside(f.calc_center_median()) != keep_inside]
        bmesh.ops.delete(bm, geom=drop, context="FACES")
        parts.append(bm)
    return parts


def is_black(c):
    saddle = abs(c.y - saddle_centre(c.z)) < SADDLE_HALF
    haunch = c.z < HAUNCH_TOP and c.y > HAUNCH_FRONT
    return saddle or haunch


# ---------------------------------------------------------------- legs + paws

def add_paw(mb, pos, heading=Vector((0, -1, 0)), toes=True):
    """Rounded paw on the ground at pos, with toe pads and claw tips toward heading."""
    side = heading.cross(Vector((0, 0, 1))).normalized()
    mb.add(nh.ellipsoid(pos + heading * 0.035 + Vector((0, 0, 0.05)), (0.10, 0.125, 0.06), subdivisions=2,
                        deform=lambda v: 1.0 - 0.25 * max(0.0, -v.z) ** 3), BLACK)
    if not toes:
        return
    for i in range(4):
        t = (i - 1.5) / 1.5
        toe = pos + heading * (0.135 - 0.02 * t * t) + side * (t * 0.062) + Vector((0, 0, 0.04))
        mb.add(nh.ellipsoid(toe, (0.026, 0.026, 0.024), subdivisions=1), PAD)
        tip = toe + heading * 0.04 + Vector((0, 0, -0.02))
        mb.add(nh.tube([toe + heading * 0.012, tip], [0.010, 0.0], sides=4), CLAW)


def add_standing_leg(mb, x, y, rear):
    if rear:
        pts = [(x * 0.6, y, 0.52), (x, y + 0.03, 0.36), (x, y + 0.03, 0.24), (x, y + 0.01, 0.14), (x, y - 0.01, 0.07)]
        radii = [0.13, 0.15, 0.13, 0.10, 0.09]
    else:
        pts = [(x * 0.6, y, 0.55), (x * 1.02, y, 0.38), (x * 1.04, y - 0.02, 0.27), (x, y - 0.02, 0.15), (x, y - 0.03, 0.07)]
        radii = [0.12, 0.14, 0.115, 0.088, 0.085]
    mb.add(nh.tube(pts, radii, sides=10), BLACK)
    add_paw(mb, Vector((x, y - 0.03, 0.0)))


def add_shoulder(mb, sx):
    # black shoulder mass so the front leg grows out of the saddle instead of a hard rim
    c = Vector((sx * 0.16, -0.25, 0.40))
    mb.add(nh.ellipsoid(c, (0.13, 0.14, 0.16), subdivisions=2, deform=lambda v: fur(v, 0.2, seed=5 + sx)), BLACK)


def add_haunch(mb, sx):
    # rounded black thigh that flows from the hind leg up over the hip
    c = Vector((sx * 0.175, 0.31, 0.36))
    mb.add(nh.ellipsoid(c, (0.13, 0.19, 0.18), subdivisions=2, deform=lambda v: fur(v, 0.3, seed=7 + sx)), BLACK)


def add_raised_arm(mb):
    """Right front leg lifted, forearm angled up, paw curled round the bamboo."""
    shoulder = Vector((0.12, -0.25, 0.52))
    elbow = Vector((0.25, -0.42, 0.25))
    wrist = Vector((0.25, -0.64, 0.38))
    mb.add(nh.tube([shoulder, Vector((0.20, -0.33, 0.38)), elbow, wrist], [0.12, 0.13, 0.105, 0.08], sides=10), BLACK)
    paw = wrist + Vector((-0.01, -0.05, 0.04))
    mb.add(nh.ellipsoid(paw, (0.07, 0.075, 0.085), subdivisions=3), BLACK)
    # pale claw tips curled round the stalk
    for i in range(3):
        c = paw + Vector((-0.045, -0.035 + i * 0.03, 0.03 - i * 0.01))
        mb.add(nh.tube([c, c + Vector((-0.03, -0.01, -0.01))], [0.009, 0.0], sides=4), CLAW)
    return paw


# ---------------------------------------------------------------- head

def head_matrix():
    return (Matrix.Translation(HEAD_C)
            @ Matrix.Rotation(math.radians(HEAD_TURN), 4, "Z")
            @ Matrix.Rotation(math.radians(HEAD_DIP), 4, "X"))


def add_head(mb, m):
    """Head parts built facing -Y around the origin, then moved by m."""
    def put(bm, color):
        mb.add(nh.transform(bm, m), color)

    put(nh.ellipsoid((0, 0, 0), (0.25, 0.22, 0.215), subdivisions=4, deform=lambda v: fur(v, 0.5, seed=9)), WHITE)
    # fluffy cheeks widen the face
    for sx in (-1, 1):
        put(nh.ellipsoid((sx * 0.12, -0.07, -0.07), (0.13, 0.12, 0.11), subdivisions=3,
                         deform=lambda v: fur(v, 0.6, seed=11 + sx)), WHITE)
    # snout: a short rounded muzzle
    put(nh.ellipsoid((0, -0.17, -0.07), (0.105, 0.11, 0.085), subdivisions=3), SNOUT)
    # nose: wide, flat-topped, slightly triangular
    put(nh.ellipsoid((0, -0.272, -0.035), (0.048, 0.03, 0.028), subdivisions=2,
                     deform=lambda v: 1.0 - 0.3 * max(0.0, -v.z) * abs(v.x)), NOSE)
    # mouth line: philtrum down from the nose, then a curve out to each side
    put(nh.tube([(0, -0.279, -0.06), (0, -0.276, -0.095)], [0.007, 0.007], sides=4), MOUTH)
    for sx in (-1, 1):
        put(nh.tube([(0, -0.276, -0.095), (sx * 0.03, -0.268, -0.108), (sx * 0.06, -0.245, -0.098)],
                    [0.007, 0.007, 0.004], sides=4), MOUTH)
    # ears: round, cupped slightly forward
    for sx in (-1, 1):
        put(nh.ellipsoid((sx * 0.17, 0.04, 0.17), (0.08, 0.045, 0.075), subdivisions=2,
                         rotation=Euler((math.radians(-15), 0, math.radians(sx * -20))).to_matrix()), BLACK)
    # eye patches: tilted teardrops drooping toward the cheeks, eyes with a glint
    for sx in (-1, 1):
        rot = Euler((math.radians(-15), math.radians(sx * -35), math.radians(sx * 22))).to_matrix()
        put(nh.ellipsoid((sx * 0.092, -0.175, 0.035), (0.075, 0.03, 0.055), subdivisions=2, rotation=rot,
                         deform=lambda v: 1.0 + 0.3 * max(0.0, -v.z)), BLACK)
        put(nh.ellipsoid((sx * 0.088, -0.203, 0.045), (0.02, 0.012, 0.02), subdivisions=2), EYE)
        put(nh.ellipsoid((sx * 0.082, -0.214, 0.052), (0.007, 0.004, 0.007), subdivisions=1), GLINT)


# ---------------------------------------------------------------- bamboo

def add_bamboo(mb, grip, mouth):
    """Upright stalk held in the paw, passing the mouth corner, with a leafy top
    above head height so it reads from the map camera."""
    bottom = grip + Vector((0.01, 0.01, -0.12))
    side = mouth + Vector((0.07, 0.0, 0.0))
    top = side + Vector((0.04, 0.03, 0.34))
    pts = [bottom, grip, side, top]
    mb.add(nh.tube(pts, [0.022, 0.023, 0.022, 0.018], sides=7), BAMBOO)
    for a, b, t in ((1, 2, 0.5), (2, 3, 0.45)):
        p = pts[a].lerp(pts[b], t)
        d = (pts[b] - pts[a]).normalized() * 0.012
        mb.add(nh.tube([p - d, p + d], [0.028, 0.028], sides=7), BAMBOO_NODE)
    for k, (az, el) in enumerate(((20, 35), (100, 20), (170, 40), (250, 25), (320, 45))):
        a, e = math.radians(az), math.radians(el)
        leaf_dir = Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e)))
        w = leaf_dir.cross(Vector((0, 0, 1))).normalized() * 0.03
        base = top - Vector((0, 0, 0.03 * (k % 2)))
        mid = base + leaf_dir * 0.08
        mb.add(nh.flat_panel([base, mid + w, base + leaf_dir * 0.2, mid - w], thickness=0.006), LEAF)


def build():
    mb = nh.MeshBuilder()

    for make in (body_shell, rump_shell):
        black, white = split(make, is_black)
        mb.add(black, BLACK)
        mb.add(white, white_shade)

    add_standing_leg(mb, -0.17, -0.26, rear=False)
    for sx in (-1, 1):
        add_standing_leg(mb, sx * 0.19, 0.31, rear=True)
        add_haunch(mb, sx)
        add_shoulder(mb, sx)
    paw = add_raised_arm(mb)

    # Tail: a white tuft
    mb.add(nh.ellipsoid((0, 0.54, 0.50), (0.065, 0.055, 0.065), subdivisions=2,
                        deform=lambda v: fur(v, 2.0, seed=3)), WHITE)

    m = head_matrix()
    add_head(mb, m)
    add_bamboo(mb, paw + Vector((-0.01, -0.02, 0.0)), m @ Vector((0.06, -0.24, -0.10)))

    obj = mb.to_object("GiantPanda")
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "GiantPanda", ground=(0.32, 0.45, 0.22), views=((35, 25), (-90, 8), (20, 60), (-30, 15)))
