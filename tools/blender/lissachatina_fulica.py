"""
Procedural giant African land snail (Lissachatina fulica) for map colonies.

An adult crawling: a tall, conical, right-handed (dextral) shell of seven
convex whorls swept along a logarithmic helicospiral, carried tilted back over
the body - chestnut-brown with dark reddish-brown zig-zag "flame" streaks
following the growth lines, darker sutures and a paler, creamy apex. The long
fused foot is grey-brown with a finely reticulated (grooved) skin and a paler
sole fringe, rising at the front into the head with two long eye-stalks (dark
eyes at the tips) and two short lower tentacles; a fleshy mantle collar fills
the aperture where the body leaves the shell.
Faces -Y, pivot on the ground (sole at z = 0). Slither gait on the map.

Usage:
  blender --background --python tools/blender/lissachatina_fulica.py -- [--render out.png]

Output: Assets/Resources/Models/Species/GiantAfricanSnail.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ammonite as am  # noqa: E402
from mathutils import Matrix, Vector, noise  # noqa: E402

SHELL = (0.52, 0.34, 0.16)        # chestnut-brown
SHELL_LIGHT = (0.72, 0.55, 0.32)
FLAME = (0.25, 0.12, 0.06)        # dark reddish-brown streaks
SUTURE = (0.20, 0.12, 0.07)
APEX = (0.86, 0.76, 0.58)         # pale creamy early whorls
LIP = (0.82, 0.74, 0.66)          # thin pale outer lip
SKIN = (0.50, 0.44, 0.37)         # grey-brown foot
SKIN_DARK = (0.33, 0.28, 0.23)
SKIN_PALE = (0.68, 0.62, 0.53)    # sole fringe
EYE = (0.05, 0.04, 0.04)

# helicospiral: whorl expansion per turn, radius/height of the coil axis path, tube size
W = 1.36
K = math.log(W) / math.tau
WHORLS = 7.0
COIL_A = 1.0      # distance of the whorl centre from the axis
COIL_H = 4.8      # drop of the whorl centre along the axis
TUBE_STRETCH = 1.3   # whorl cross-section elongated along the axis
SHELL_SCALE = 0.0145  # coil units -> model units
SHELL_TILT = -48      # degrees: apex leans back over the tail
SHELL_SPIN = 165      # degrees about the shell axis: turns the aperture down onto the foot
SHELL_POS = Vector((0.0, 0.08, 0.075))  # where the lowest point of the body whorl sits
N_PHI = 16
PER_TURN = 30


def tube_r(g):
    """Tube radius so each whorl just overlaps the previous one."""
    gap = (1 - 1 / W) * math.hypot(COIL_A, COIL_H)
    return 1.22 * g * gap / (1 + 1 / W)


def shell():
    """Swept helicospiral shell; returns (bm, base_point) in shell space (apex at the origin, axis -Z)."""
    rings, cols = [], []
    t_end = WHORLS * math.tau
    t0 = -0.0
    steps = int(WHORLS * PER_TURN)
    g_end = math.exp(K * t_end)
    for i in range(steps + 1):
        t = t0 + (t_end - t0) * i / steps
        g = math.exp(K * t)
        a = -t                                       # clockwise seen from the apex: dextral
        radial = Vector((math.cos(a), math.sin(a), 0.0))
        c = radial * (COIL_A * g) + Vector((0, 0, -COIL_H * g))
        r = tube_r(g)
        turn = t / math.tau
        # flames: zig-zag dark streaks along the growth lines, irregularly spaced
        streak_phase = t * 4.2 + 1.7 * math.sin(t * 0.9) + 2.5 * noise.noise(Vector((t * 0.7, 0.3, 1.1)))
        ring, ring_c = [], []
        for k in range(N_PHI):
            phi = k / N_PHI * math.tau
            off = radial * (math.cos(phi) * r) + Vector((0, 0, math.sin(phi) * r * TUBE_STRETCH))
            ring.append((c + off).to_tuple())
            # suture: the parts of the whorl that tuck against its neighbours above and below
            up = math.sin(phi)
            near_suture = nh.smoothstep(0.55, 0.9, abs(up)) * nh.smoothstep(-0.2, 0.3, -math.cos(phi) * 0 + 1)
            zig = math.sin(streak_phase + up * 1.6)
            flame = nh.smoothstep(0.2, 0.55, zig)
            col = nh.lerp(SHELL, SHELL_LIGHT, 0.35 + 0.35 * math.cos(phi))   # paler on the whorl shoulder
            col = nh.lerp(col, FLAME, flame * 0.95)
            col = nh.lerp(col, SUTURE, near_suture * 0.7)
            col = nh.lerp(APEX, col, nh.smoothstep(0.6, 2.6, turn))         # creamy apex whorls
            if i == steps - 1:
                col = LIP
            elif i == steps:
                col = SKIN  # the cap reads as the body filling the aperture
            ring_c.append(col)
        rings.append(ring)
        cols.append(ring_c)
    bm = am.grid_mesh(rings, cols, cap_start=True, cap_end=True)
    return bm, g_end


def to_model(bm):
    nh.transform(bm, Matrix.Scale(SHELL_SCALE, 4))
    nh.transform(bm, Matrix.Rotation(math.radians(SHELL_SPIN), 4, "Z"))
    nh.transform(bm, Matrix.Rotation(math.radians(SHELL_TILT), 4, "X"))
    low = min(bm.verts, key=lambda v: v.co.z).co.copy()
    cy = sum(v.co.y for v in bm.verts) / len(bm.verts)
    nh.transform(bm, Matrix.Translation(SHELL_POS - Vector((0, cy, low.z))))
    return bm


# ---------------------------------------------------------------- fused body

def body_parts():
    parts = []
    # long foot, flattened, tapering to a pointed tail behind the shell
    foot = [(0, 0.62, 0.025), (0, 0.50, 0.04), (0, 0.32, 0.05), (0, 0.12, 0.055), (0, -0.10, 0.055),
            (0, -0.28, 0.055), (0, -0.40, 0.06)]
    parts.append(nh.tube(foot, [0.0, 0.035, 0.06, 0.075, 0.078, 0.072, 0.065], sides=14, scale_xy=(1.2, 0.95)))
    # neck and head rising slightly at the front
    neck = [(0, -0.26, 0.08), (0, -0.40, 0.11), (0, -0.50, 0.12), (0, -0.56, 0.105)]
    parts.append(nh.tube(neck, [0.07, 0.066, 0.058, 0.045], sides=12, scale_xy=(1.1, 1.0)))
    parts.append(nh.ellipsoid((0, -0.54, 0.075), (0.06, 0.05, 0.045), subdivisions=2))  # snout / mouth lobe
    # mantle collar bulging out of the aperture
    parts.append(nh.ellipsoid((0.0, -0.02, 0.11), (0.09, 0.15, 0.06), subdivisions=2))
    return parts


def skin(co, n):
    side = nh.smoothstep(0.9, 0.1, n.z)
    c = nh.lerp(SKIN, SKIN_DARK, 0.35 * max(0.0, n.z))
    # reticulated skin: a net of fine grooves between flat tubercles
    v = abs(noise.noise(co * 55.0)) + 0.5 * abs(noise.noise(co * 120.0))
    c = nh.lerp(c, SKIN_DARK, nh.smoothstep(0.05, 0.0, v) * 0.6 + 0.15 * max(0.0, noise.noise(co * 20.0)))
    # pale fringe along the edge of the sole
    return nh.lerp(c, SKIN_PALE, nh.smoothstep(0.03, 0.012, co.z) * side)


def furrows(bm):
    bm.normal_update()
    for v in bm.verts:
        if v.co.z < 0.015:
            continue
        g = abs(noise.noise(v.co * 55.0))
        v.co -= v.normal * 0.004 * nh.smoothstep(0.12, 0.0, g)
    bm.normal_update()


def tentacles():
    out = []
    for sx in (-1, 1):
        # long upper eye-stalks, splayed and swept up and forward
        base = Vector((sx * 0.025, -0.52, 0.13))
        pts = [base, base + Vector((sx * 0.02, -0.05, 0.08)), base + Vector((sx * 0.05, -0.10, 0.16)),
               base + Vector((sx * 0.065, -0.14, 0.215))]
        out.append((nh.tube(pts, [0.016, 0.011, 0.009, 0.008], sides=6), SKIN))
        out.append((nh.ellipsoid(pts[-1] + Vector((sx * 0.004, -0.006, 0.006)), (0.014, 0.014, 0.014),
                                 subdivisions=2), SKIN_DARK))
        out.append((nh.ellipsoid(pts[-1] + Vector((sx * 0.008, -0.013, 0.01)), (0.007, 0.007, 0.007),
                                 subdivisions=1), EYE))
        # short lower tentacles pointing forward and down
        b2 = Vector((sx * 0.03, -0.575, 0.08))
        out.append((nh.tube([b2, b2 + Vector((sx * 0.025, -0.04, -0.012)), b2 + Vector((sx * 0.035, -0.06, -0.025))],
                            [0.011, 0.008, 0.006], sides=5), SKIN))
    return out


def build():
    body = nh.MeshBuilder()
    for p in body_parts():
        body.add(p, SKIN)
    fused = body.fuse(voxel=0.011, smooth=5, smooth_factor=0.5, max_tris=3200)
    for v in fused.verts:            # flat creeping sole
        if v.co.z < 0.004:
            v.co.z = 0.004
    furrows(fused)

    mb = nh.MeshBuilder()
    mb.add(fused, skin)
    for bm, c in tentacles():
        mb.add(bm, c)
    sh, _ = shell()
    mb.add(to_model(sh))
    obj = mb.to_object("GiantAfricanSnail", roughness=0.35)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "GiantAfricanSnail", ground=(0.40, 0.42, 0.28), views=((40, 22), (-90, 6), (90, 10), (20, 65)))
