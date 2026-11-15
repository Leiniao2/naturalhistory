"""
Procedural red-eyed tree frog (Agalychnis callidryas) for map colonies.

A slender tree frog sitting alert, front legs braced and hind legs folded tight
against the flanks, as if perched on a leaf: one seamless fused body (narrow-waisted
torso tilted nose-up, a broad short head with a rounded snout, raised sockets for
the huge eyes, thin arms, long folded thighs, shins and feet).
Repainted procedurally: bright leaf-green back and limb tops, a thin cream seam
along the sides, cobalt-blue flanks crossed by cream vertical bars, blue inner
thighs and upper arms, orange hands and feet, and a creamy white belly and throat.
Crisp details on top: bulging scarlet eyes with vertical black slit pupils,
nostrils, and long orange fingers and toes ending in round sticky pads.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/agalychnis_callidryas.py -- [--render out.png]

Output: Assets/Resources/Models/Species/RedEyedTreeFrog.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bpy  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402

GREEN = (0.28, 0.68, 0.12)       # leaf green back
GREEN_LIGHT = (0.45, 0.80, 0.20)
SEAM = (0.93, 0.92, 0.72)        # thin cream line between back and flank
BLUE = (0.10, 0.24, 0.72)        # cobalt flanks and inner thighs
BLUE_DEEP = (0.07, 0.14, 0.50)
BAR = (0.95, 0.90, 0.68)         # cream flank bars
BELLY = (0.95, 0.93, 0.82)
ORANGE = (1.00, 0.45, 0.06)      # hands and feet
PAD = (1.00, 0.60, 0.20)
IRIS = (0.86, 0.04, 0.03)
IRIS_DARK = (0.55, 0.02, 0.02)
PUPIL = (0.01, 0.01, 0.01)
NOSTRIL = (0.06, 0.12, 0.04)

EYE_R = 0.034
EYES = [Vector((sx * 0.066, -0.106, 0.136)) for sx in (1, -1)]

FOOTPRINTS = []   # (palm, forward, lengths, spread, radius) for the crisp digits


def rot_x(deg):
    return Matrix.Rotation(math.radians(deg), 4, "X")


# ---------------------------------------------------------------- fused body parts

def body_parts():
    parts = []
    # slender torso, tilted nose-up, narrowing to the waist
    torso = nh.uv_ellipsoid((0, 0, 0), (0.078, 0.15, 0.055), 28, 18,
                            deform=lambda v: 1.0 - 0.10 * max(0.0, v.y) * (1.0 - abs(v.z)))
    nh.transform(torso, rot_x(-16))
    nh.transform(torso, Matrix.Translation((0, 0.03, 0.075)))
    parts.append(torso)
    parts.append(nh.uv_ellipsoid((0, 0.13, 0.06), (0.06, 0.06, 0.045), 18, 12))              # rump
    # broad short head with a rounded snout
    parts.append(nh.uv_ellipsoid((0, -0.10, 0.108), (0.085, 0.07, 0.042), 24, 14))
    parts.append(nh.uv_ellipsoid((0, -0.155, 0.10), (0.058, 0.045, 0.032), 18, 10))
    parts.append(nh.uv_ellipsoid((0, -0.09, 0.075), (0.075, 0.07, 0.035), 18, 10))           # throat
    for sx in (1, -1):
        e = EYES[0] * Vector((sx, 1, 1))
        parts.append(nh.ellipsoid(e + Vector((0, 0.006, -0.012)), (EYE_R * 1.05, EYE_R, EYE_R * 0.9),
                                  subdivisions=3))                                           # eye socket
        # thin arms: shoulder -> elbow (out, back) -> wrist (forward)
        parts.append(nh.tube([(sx * 0.05, -0.065, 0.07), (sx * 0.085, -0.06, 0.045), (sx * 0.092, -0.1, 0.03),
                              (sx * 0.085, -0.14, 0.012)], [0.02, 0.016, 0.013, 0.011], sides=12))
        # folded hind legs: thigh forward to the knee, shin back to the heel, foot forward again
        parts.append(nh.tube([(sx * 0.045, 0.15, 0.06), (sx * 0.09, 0.09, 0.055), (sx * 0.12, 0.02, 0.045)],
                             [0.03, 0.026, 0.018], sides=14))                               # thigh
        parts.append(nh.tube([(sx * 0.12, 0.02, 0.045), (sx * 0.125, 0.09, 0.03), (sx * 0.11, 0.165, 0.018)],
                             [0.018, 0.016, 0.011], sides=12))                              # shin
        parts.append(nh.tube([(sx * 0.11, 0.165, 0.012), (sx * 0.135, 0.11, 0.008), (sx * 0.15, 0.06, 0.006)],
                             [0.011, 0.01, 0.008], sides=10, scale_xy=(1.0, 0.6)))         # foot
    return parts


# ---------------------------------------------------------------- paint

def bars(co):
    """1 on the cream vertical bars along the flank (slanting back toward the belly)."""
    u = co.y + 0.35 * (0.09 - co.z) + 0.004 * noise.noise(co * 60.0)
    t = (u / 0.034) % 1.0
    return 1.0 - nh.smoothstep(0.16, 0.26, abs(t - 0.5))


def paint(co, n):
    ax = abs(co.x)
    is_leg = (ax > 0.085 and co.y > -0.02) or co.y > 0.17 or (ax > 0.07 and co.y < -0.04 and co.z < 0.06)
    c = nh.lerp(GREEN, GREEN_LIGHT, 0.35 + 0.35 * noise.noise(co * 18.0))
    up = n.z
    if not is_leg:
        if co.y < -0.06 and co.z < 0.088 and up < -0.25:        # throat
            return nh.lerp(c, BELLY, nh.smoothstep(-0.25, -0.5, up))
        side = nh.smoothstep(0.35, 0.15, up)                    # flanks below the seam
        belly = nh.smoothstep(-0.35, -0.6, up) * nh.smoothstep(0.095, 0.075, co.z)
        if side > 0.0 and -0.035 < co.y < 0.16:
            flank = nh.lerp(BLUE, BLUE_DEEP, 0.4 * nh.smoothstep(0.2, -0.3, up))
            flank = nh.lerp(flank, BAR, bars(co) * nh.smoothstep(0.3, 0.05, up))
            c = nh.lerp(c, flank, side)
            seam = 1.0 - nh.smoothstep(0.03, 0.08, abs(up - 0.32))
            c = nh.lerp(c, SEAM, 0.85 * seam)
        c = nh.lerp(c, BELLY, belly)
        return c
    # limbs: green on top, blue on the hidden inner and under sides, orange hands and feet
    if co.z < 0.016 or (co.y < -0.12 and co.z < 0.025):
        return ORANGE
    hidden = nh.smoothstep(0.3, -0.2, up)
    if co.y > -0.04:
        inner = nh.smoothstep(0.0, 0.5, -n.x * math.copysign(1, co.x))   # thighs face the flank
        hidden = max(hidden, inner * 0.9)
    c = nh.lerp(c, nh.lerp(BLUE, ORANGE, 0.0 if co.y > -0.04 else 0.4), hidden)
    return c


# ---------------------------------------------------------------- crisp details

def eye(centre, sx):
    out = []
    look = Vector((sx * 0.75, -0.55, 0.38)).normalized()

    def iris(co, n, c=centre):
        # scarlet iris with dark veins and a faint darker ring
        q = (co - c).normalized()
        v = noise.noise((co - c) * 300.0)
        col = nh.lerp(IRIS, IRIS_DARK, 0.6 if v > 0.4 else 0.0)
        return nh.lerp(col, IRIS_DARK, nh.smoothstep(0.6, 0.3, q.dot(look)))
    out.append((nh.uv_ellipsoid(centre, (EYE_R, EYE_R, EYE_R * 0.95), 20, 14), iris))
    # vertical slit pupil on the front of the eye
    side = look.cross(Vector((0, 0, 1))).normalized()
    up = side.cross(look).normalized()
    pup = nh.ellipsoid((0, 0, 0), (0.0045, 0.019, 0.004), subdivisions=2)
    nh.transform(pup, Matrix((side, up, look)).transposed().to_4x4())
    nh.transform(pup, Matrix.Translation(centre + look * (EYE_R * 0.97 - 0.0022)))
    out.append((pup, PUPIL))
    return out


def digits(palm, forward, lengths, spread, radius):
    """Long splayed orange digits with round adhesive pads at the tips."""
    out = []
    n = len(lengths)
    for k, L in enumerate(lengths):
        a = (k / (n - 1) - 0.5) * spread
        d = Matrix.Rotation(a, 3, "Z") @ forward
        p0 = palm + Vector((0, 0, 0.006))
        p1 = p0 + d * L * 0.55 + Vector((0, 0, 0.002))
        p2 = p0 + d * L
        p2.z = radius * 1.1
        out.append((nh.tube([p0, p1, p2], [radius, radius * 0.85, radius * 0.8], sides=8), ORANGE))
        pad = nh.uv_ellipsoid(p2 + d * radius * 0.8, (radius * 1.7, radius * 1.7, radius * 1.05), 8, 5)
        out.append((pad, PAD))
    return out


def details():
    out = []
    for i, sx in enumerate((1, -1)):
        out += eye(EYES[i], sx)
        out.append((nh.ellipsoid((sx * 0.017, -0.19, 0.113), (0.0035, 0.003, 0.002), subdivisions=1), NOSTRIL))
        # four fingers spread wide in front, five long toes beside the folded thigh
        out += digits(Vector((sx * 0.085, -0.145, 0.0)), Vector((sx * 0.15, -1, 0)).normalized(),
                      [0.022, 0.03, 0.034, 0.028], 2.0, 0.0045)
        out += digits(Vector((sx * 0.15, 0.065, 0.0)), Vector((sx * 0.45, -0.9, 0)).normalized(),
                      [0.022, 0.03, 0.04, 0.05, 0.036], 1.7, 0.0042)
    return out


def refine(bm, contrast=0.15):
    """Splits edges that cross a colour boundary, so the flank bars stay crisp."""
    bm.normal_update()
    lum = {}
    for v in bm.verts:
        c = paint(v.co, v.normal)
        lum[v] = c[0] * 0.3 + c[1] * 0.6 + c[2] * 0.1
    edges = [e for e in bm.edges if abs(lum[e.verts[0]] - lum[e.verts[1]]) > contrast]
    bmesh.ops.subdivide_edges(bm, edges=edges, cuts=1, use_grid_fill=True)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.normal_update()


def build():
    body = nh.MeshBuilder()
    for p in body_parts():
        body.add(p, GREEN)
    fused = body.fuse(voxel=0.013, smooth=4, smooth_factor=0.5, max_tris=None)
    refine(fused, 0.15)
    refine(fused, 0.35)
    mb = nh.MeshBuilder()
    mb.add(fused, color=paint)
    for bm, col in details():
        mb.add(bm, col)
    obj = mb.to_object("RedEyedTreeFrog", roughness=0.35)
    nh.ground_to_zero(obj)
    return obj


def closeup(path, target, dist, az, el, lens=60):
    scene = bpy.context.scene
    cam = scene.camera
    cam.data.lens = lens
    a, e = math.radians(az), math.radians(el)
    target = Vector(target)
    cam.location = target + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    nh.run(build, "RedEyedTreeFrog", background=(0.55, 0.60, 0.55), ground=(0.30, 0.42, 0.20),
           views=((35, 25), (-90, 8), (160, 55)))
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--render" in argv:
        out = Path(argv[argv.index("--render") + 1])
        closeup(out.with_name(out.stem + "_head.png"), (0.0, -0.11, 0.1), 0.42, 30, 20)
