"""
Procedural Campanile giganteum (Eocene giant sea snail, Paris Basin and other warm shallow seas
of Europe) for the map (Fixed style). One of the largest sea snails that ever lived: a tall,
slender, turret-shaped shell up to about 1 m long with twenty or more whorls, each crowned
by a spiral row of blunt knobs, and a short siphonal canal at the front of the aperture. It
crawled slowly over sandy sea floors grazing algae and detritus. Shell creamy white with faint
brown spiral bands; soft parts mottled grey-brown.
Modelled crawling: the spire trails behind and slightly up, the foot on the sand.
Faces -Y, pivot on the ground (sole of the foot at z = 0).

Usage:
  blender --background --python tools/blender/campanile_giganteum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/CampanileGiganteum.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmesh  # noqa: E402
from mathutils import Matrix, Vector, noise  # noqa: E402
import nh_model as nh  # noqa: E402

CREAM = (0.90, 0.84, 0.70)
BAND = (0.62, 0.48, 0.32)
SUTURE = (0.40, 0.32, 0.22)
KNOB = (0.96, 0.92, 0.82)
FOOT = (0.48, 0.42, 0.36)
FOOT_DARK = (0.28, 0.24, 0.20)
EYE = (0.03, 0.03, 0.03)

LEN = 1.5        # shell length along its axis
R0 = 0.17        # radius of the body whorl
WHORLS = 18
TILT = math.radians(14)   # spire raised toward the back


def rad(t, a):
    """t = 0 at the aperture end, 1 at the apex; a = angle around the axis."""
    r = R0 * (1.0 - t) ** 0.95 + 0.004
    ph = (t * WHORLS + a / math.tau) % 1.0          # position within the current whorl
    groove = 1.0 - 0.22 * math.exp(-((ph - 0.0) / 0.07) ** 2) - 0.22 * math.exp(-((ph - 1.0) / 0.07) ** 2)
    knob = 0.16 * math.exp(-((ph - 0.72) / 0.11) ** 2) * max(0.0, math.cos(a * 9 + t * 40)) ** 2
    belt = 0.05 * math.exp(-((ph - 0.35) / 0.08) ** 2)
    return r * (groove + knob + belt), ph


def shell():
    bm = bmesh.new()
    nseg, nst = 32, 150
    rings = []
    cols = {}
    for i in range(nst):
        t = i / (nst - 1) * 0.995
        ring = []
        for k in range(nseg):
            a = k / nseg * math.tau
            r, ph = rad(t, a)
            v = bm.verts.new((math.cos(a) * r, t * LEN, math.sin(a) * r))
            cols[v] = (ph, t, a)
            ring.append(v)
        rings.append(ring)
    apex = bm.verts.new((0, LEN, 0))
    cols[apex] = (0.5, 1.0, 0.0)
    front = bm.verts.new((0, -0.02, 0))
    cols[front] = (0.5, 0.0, 0.0)
    for a, b in zip(rings, rings[1:]):
        for k in range(nseg):
            j = (k + 1) % nseg
            bm.faces.new([a[k], a[j], b[j], b[k]])
    for k in range(nseg):
        j = (k + 1) % nseg
        bm.faces.new([front, rings[0][j], rings[0][k]])
        bm.faces.new([apex, rings[-1][k], rings[-1][j]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm, cols


def build():
    mb = nh.MeshBuilder()
    bm, info = shell()

    def col(co, n):
        # recompute from the (untransformed) local position
        t = max(0.0, min(1.0, co.y / LEN))
        a = math.atan2(co.z, co.x)
        _r, ph = rad(t, a)
        c = CREAM
        c = nh.lerp(c, BAND, 0.55 * math.exp(-((ph - 0.45) / 0.08) ** 2))
        c = nh.lerp(c, SUTURE, math.exp(-(min(ph, 1 - ph) / 0.05) ** 2))
        c = nh.lerp(c, KNOB, 0.6 * math.exp(-((ph - 0.72) / 0.08) ** 2))
        c = nh.lerp(c, BAND, 0.15 * max(0.0, noise.noise(Vector((co.x * 8, co.y * 8, co.z * 8)))))
        return c
    # colour in shell space, then place: raise the spire, lift onto the foot
    sb = nh.MeshBuilder()
    sb.add(bm, col)
    shell_bm = sb.bm
    sb.bm = bmesh.new()
    nh.transform(shell_bm, Matrix.Translation(Vector((0, -0.25, 0.19))) @ Matrix.Rotation(TILT, 4, "X"))
    mb.add(shell_bm)

    # aperture: dark opening with a short siphonal canal at the front
    mb.add(nh.ellipsoid((0, -0.27, 0.12), (0.1, 0.03, 0.12), subdivisions=2), (0.30, 0.22, 0.16))
    mb.add(nh.tube([(0.0, -0.24, 0.07), (0.0, -0.33, 0.06), (0.0, -0.4, 0.09)], [0.04, 0.03, 0.025], sides=8),
           CREAM)

    def foot_col(co, n):
        return nh.lerp(FOOT, FOOT_DARK, 0.7 * max(0.0, noise.noise(co * 20.0)))
    mb.add(nh.ellipsoid((0, -0.15, 0.04), (0.14, 0.42, 0.045), subdivisions=3), foot_col)
    mb.add(nh.ellipsoid((0, -0.5, 0.07), (0.08, 0.08, 0.05), subdivisions=2), foot_col)
    for sx in (-1, 1):
        b = Vector((sx * 0.05, -0.54, 0.09))
        t = b + Vector((sx * 0.06, -0.1, 0.05))
        mb.add(nh.tube([tuple(b), tuple(t)], [0.016, 0.006], sides=6), FOOT)
        mb.add(nh.ellipsoid(tuple(b + (t - b) * 0.3 + Vector((sx * 0.012, 0, 0.008))), (0.012,) * 3,
                            subdivisions=1), EYE)
    obj = mb.to_object("CampanileGiganteum", roughness=0.5)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "CampanileGiganteum", background=(0.05, 0.20, 0.26), ground=(0.70, 0.64, 0.50),
           views=((35, 25), (-90, 5), (150, 40)))
