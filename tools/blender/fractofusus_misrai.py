"""
Procedural low-poly Fractofusus misrai (Ediacaran rangeomorph, Mistaken Point, Newfoundland).

A spindle-shaped frond that lay flat on the deep seafloor: a long central
midline with two rows of rangeomorph branches (frondlets) set alternately on
either side, each frondlet a leaf-like lobe subdivided into smaller ribbed
branchlets (shown as fine rib bands), largest at the middle and shrinking to
the pointed ends. Low relief. Pale pinkish beige with darker frondlet grooves.
Faces -Y (long axis along Y), pivot on the seabed (Fixed).

Output: Assets/Resources/Models/Species/Fractofusus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

LOBE = (0.84, 0.66, 0.58)
LOBE_DARK = (0.50, 0.34, 0.30)
MID = (0.50, 0.36, 0.30)

L = 0.7
N = 9  # frondlets per side


def half_width(y):
    t = y / L
    return 0.24 * max(0.0, 1 - t * t) ** 0.9


def build():
    mb = nh.MeshBuilder()
    mb.add(nh.tube([(0, -L - 0.03, 0.01), (0, 0, 0.025), (0, L + 0.03, 0.01)], [0.0, 0.018, 0.0], sides=6), MID)
    for s in (-1, 1):
        for k in range(N):
            y = -L + (k + 0.5 + (0.5 if s > 0 else 0.0)) * 2 * L / (N + 0.5)
            w = half_width(y)
            if w < 0.03:
                continue
            ln = 2 * L / (N + 0.5) * 0.85
            lobe = nh.uv_ellipsoid((0, 0, 0), (w * 0.6, ln, 0.035), segments=14, rings=6)
            for v in lobe.verts:
                if v.co.z < 0:
                    v.co.z *= 0.2
            # frondlets angle forward-outward
            nh.transform(lobe, Matrix.Rotation(math.radians(30) * s, 4, "Z"))
            centre = Vector((s * w * 0.5, y, 0.012))
            nh.transform(lobe, Matrix.Translation(centre))

            def col(co, n, centre=centre, s=s):
                d = co - centre
                # branchlet ribs running across the lobe
                along = d.x * math.cos(math.radians(30)) * s + d.y * math.sin(math.radians(30))
                rib = 0.5 + 0.5 * math.cos(along * math.tau / 0.028)
                c = nh.lerp(LOBE, LOBE_DARK, 0.8 * nh.smoothstep(0.45, 1.0, rib))
                return nh.lerp(LOBE_DARK, c, nh.smoothstep(-0.3, 0.6, n.z))

            mb.add(lobe, col)
    return ec.ground(mb.to_object("Fractofusus", roughness=0.6))


if __name__ == "__main__":
    ec.export(build, "Fractofusus", fixed=True, views=((35, 40), (0, 80)))
