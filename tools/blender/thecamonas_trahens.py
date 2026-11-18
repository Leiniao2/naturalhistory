"""
Procedural low-poly Thecamonas trahens, an apusomonad: a tiny gliding flagellate close to the
common root of amoebae, fungi and animals.

A small oval, flattened cell that glides over the bottom. The top is covered by a smooth, slightly
darker dorsal pellicle, a low shell-like dome; under it a soft, pale ventral margin spreads a
little wider than the shell, with a gently ruffled edge and two short pseudopod lobes pushing out
at the side and rear. At the front a stiff sleeve (the "snout" sheath) juts forward and a little
down, enclosing the short anterior flagellum whose tip just pokes out. The long posterior
flagellum leaves the underside near the rear and trails out flat behind along the ground in a
lazy wave. The round nucleus shows through the pellicle near the front. Warm pale peach-tan, the
sheath darker. Colour is in vertex colours (see nh_model).

Usage:
  blender --background --python tools/blender/thecamonas_trahens.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Thecamonas.fbx
About 1.6 units long from the sleeve tip to the end of the trailing flagellum, ~0.6 wide. Faces
-Y (sleeve first). Pivot at the centre of the bounds (Drift).
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Matrix, Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402

HALF_L = 0.34          # half-length of the cell (Y)
HALF_W = 0.25          # half-width of the cell (X)
DOME_H = 0.13          # height of the pellicle dome
SKIRT = 1.16           # how far the ventral margin spreads past the shell
RUFFLES = 11
SLEEVE_LEN = 0.14
POST_FLAG = 0.70       # length of the trailing flagellum behind the cell

PELLICLE = (0.86, 0.66, 0.50)
PELLICLE_RIM = (0.72, 0.52, 0.38)
VENTRAL = (0.97, 0.84, 0.70)
VENTRAL_EDGE = (0.99, 0.91, 0.80)
NUCLEUS = (0.60, 0.40, 0.28)
NUCLEOLUS = (0.42, 0.26, 0.17)
SHEATH = (0.62, 0.42, 0.29)
SHEATH_TIP = (0.48, 0.30, 0.20)
FLAG = (0.95, 0.88, 0.78)
LOBE = (0.98, 0.88, 0.76)

NUC_C = Vector((0.03, -0.15, 0.0))


def build():
    mb = nh.MeshBuilder()

    # soft pale ventral margin: a flat cushion a little wider than the shell, ruffled at the edge
    def ruffle(n):
        a = math.atan2(n.y, n.x)
        edge = 1.0 - abs(n.z) ** 0.5
        return 1.0 + 0.06 * math.sin(a * RUFFLES + 0.7) * edge + 0.02 * noise.noise(n * 3.0) * edge

    def ventral_col(co, n):
        r = math.hypot(co.x / (HALF_W * SKIRT), co.y / (HALF_L * SKIRT))
        return nh.lerp(VENTRAL, VENTRAL_EDGE, nh.smoothstep(0.7, 1.0, r))

    mb.add(nh.uv_ellipsoid((0, 0.01, -0.04), (HALF_W * SKIRT, HALF_L * SKIRT, 0.07),
                           segments=40, rings=8, deform=ruffle), ventral_col)

    # dorsal pellicle: a smooth low dome, darker, flattened underneath
    def dome(n):
        # slightly egg-shaped in plan: a touch narrower at the front
        k = 1.0 - 0.06 * max(0.0, -n.y)
        return k if n.z > 0 else k * 0.6 + 0.4 * k * (1 + n.z)

    def pellicle_col(co, n):
        c = nh.lerp(PELLICLE_RIM, PELLICLE, nh.smoothstep(0.02, 0.09, co.z))
        return tuple(k * (1.0 + 0.03 * noise.noise(co * 12.0)) for k in c)

    mb.add(nh.uv_ellipsoid((0, 0, 0.0), (HALF_W, HALF_L, DOME_H), segments=32, rings=14, deform=dome),
           pellicle_col)

    # the nucleus shows through as a low, slightly darker lens
    def nucleus_col(co, n):
        d = math.hypot((co.x - NUC_C.x) / 0.09, (co.y - NUC_C.y) / 0.08)
        c = nh.lerp(NUCLEUS, PELLICLE, nh.smoothstep(0.55, 1.0, d) * 0.6)
        return nh.lerp(c, NUCLEOLUS, (1 - nh.smoothstep(0.15, 0.35, d)) * 0.8)

    mb.add(nh.ellipsoid((NUC_C.x, NUC_C.y, 0.096), (0.09, 0.08, 0.022), subdivisions=3,
                        rotation=Matrix.Rotation(math.radians(12), 3, "X")), nucleus_col)  # follows the slope

    # two short pseudopod lobes pushing out of the ventral margin
    for at, rad in (((-0.27, 0.12, -0.04), (0.08, 0.06, 0.035)),
                    ((0.17, 0.33, -0.045), (0.065, 0.075, 0.03))):
        mb.add(nh.ellipsoid(at, rad, subdivisions=2), LOBE)

    # the stiff sleeve ("snout"): a tapering sheath jutting forward and slightly down
    s0 = Vector((0.0, -HALF_L + 0.06, 0.02))
    s1 = Vector((0.0, -HALF_L - SLEEVE_LEN * 0.45, -0.005))
    s2 = Vector((0.005, -HALF_L - SLEEVE_LEN, -0.025))

    def sheath_col(co, n):
        return nh.lerp(SHEATH, SHEATH_TIP, nh.smoothstep(s1.y, s2.y, co.y))

    mb.add(nh.tube([s0, s1, s2], [0.06, 0.04, 0.03], sides=10), sheath_col)
    mb.add(nh.tube([s2 + Vector((0, 0.01, 0)), s2 + Vector((0, -0.012, 0))], [0.034, 0.026], sides=10),
           SHEATH_TIP)  # thickened rim of the opening
    # short anterior flagellum just poking out of the sleeve
    mb.add(nh.tube([s2, s2 + Vector((0.01, -0.06, 0.0)), s2 + Vector((0.035, -0.12, 0.015))],
                   [0.014, 0.011, 0.0], sides=5), FLAG)

    # long posterior flagellum: out of the underside near the rear, trailing flat along the ground
    base = Vector((0.03, HALF_L - 0.06, -0.06))
    ground = -0.085
    pts, radii = [base], [0.017]
    n = 20
    for k in range(1, n + 1):
        u = k / n
        y = HALF_L - 0.02 + POST_FLAG * u
        x = 0.03 + 0.07 * math.sin(u * math.tau * 1.2 + 0.4) * u ** 0.7
        z = nh.lerp((base.z,), (ground,), nh.smoothstep(0.0, 0.15, u))[0]
        pts.append(Vector((x, y, z)))
        radii.append(0.016 * (1.0 - 0.5 * u) if k < n else 0.0)
    mb.add(nh.tube(pts, radii, sides=5), FLAG)

    obj = mb.to_object("Thecamonas", roughness=0.4)
    vs = obj.data.vertices
    mid = Vector([(max(v.co[i] for v in vs) + min(v.co[i] for v in vs)) / 2 for i in range(3)])
    for v in vs:
        v.co -= mid
    return obj


if __name__ == "__main__":
    nh.run(build, "Thecamonas", views=((35, 35), (0, 85), (-90, 10)))
