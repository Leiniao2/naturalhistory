"""
Procedural Euomphalopterus alatus (a Silurian sea snail, shell about 3-5 cm across,
from the Wenlock reefs of Gotland, Sweden, and England) for map colonies (Fixed).

A low, top-shaped snail with a striking "wing": a thin, flat frill (a selenizone keel)
runs round the outer edge of every whorl and stands out from the shell like the brim
of a hat - "alatus" means winged. The frill probably kept the snail from sinking into
soft mud and made it harder for predators to grip. Low spire, rounded whorls with
fine growth lines, a broad opening underneath with the foot and head peeking out.
Three snails crawling on reef mud; cream shell with reddish-brown flame stripes.
Built with nh_ord_shells.snail_shell plus the frill. Fixed style: pivot on the sea
floor, facing -Y.

Usage:
  blender --background --python tools/blender/euomphalopterus_alatus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/EuomphalopterusAlatus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmesh  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_ord_echino as ec  # noqa: E402
import nh_ord_shells as sh  # noqa: E402

NAME = "EuomphalopterusAlatus"
SHELL = (0.86, 0.78, 0.62)
CORD = (0.60, 0.34, 0.20)
FRILL = (0.92, 0.84, 0.70)
FRILL_DARK = (0.62, 0.40, 0.26)

TURNS, W, SPIRE, SECTION, STEPS = 3.5, 2.4, 0.55, 0.55, 24
SNAILS = ((0.0, -0.05, 200, 1.0), (-0.58, 0.42, 120, 0.75), (0.58, 0.38, 300, 0.7))


def frill(matrix, width=0.9):
    """Thin flat flange round the periphery of every whorl, following the coil."""
    n = int(TURNS * STEPS)
    bm = bmesh.new()
    inner, outer = [], []
    for i in range(n + 1):
        th = i / STEPS * math.tau
        k = W ** ((i - n) / STEPS)
        R = 0.3 * k
        out = Vector((math.cos(th), math.sin(th), 0))
        c = Vector((R * math.cos(th), R * math.sin(th), -SPIRE * R))
        rt = R * SECTION
        inner.append(c + out * rt * 0.85)
        outer.append(c + out * rt * (1.0 + width) + Vector((0, 0, -rt * 0.15)))
    vt = [(bm.verts.new(a), bm.verts.new(b)) for a, b in zip(inner, outer)]
    for i in range(n):
        bm.faces.new([vt[i][0], vt[i][1], vt[i + 1][1], vt[i + 1][0]])
    # give it a little thickness: solidify by duplicating downward
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.012)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    nh.transform(bm, matrix)
    return bm


def build():
    mb = nh.MeshBuilder()
    ec.mud_patch(mb, 1.05, ((0.40, 0.38, 0.33), (0.54, 0.51, 0.45)))
    for x, y, yaw, k in SNAILS:
        m = Matrix.Translation(Vector((x, y, 0.40 * k))) @ Matrix.Rotation(math.radians(yaw), 4, "Z") \
            @ Matrix.Scale(k, 4)
        sh.snail_shell(mb, turns=TURNS, w=W, spire=SPIRE, section=SECTION, cords=5, steps_per_turn=STEPS,
                       shell=SHELL, cord=CORD, band=CORD, matrix=m)
        inv = m.inverted()
        mb.add(frill(m), lambda co, n, inv=inv: nh.lerp(
            FRILL, FRILL_DARK, 0.6 * nh.smoothstep(0.5, 1.0, math.sin(math.atan2((inv @ co).y, (inv @ co).x) * 7))), smooth=False)
    obj = mb.to_object(NAME, roughness=0.55)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, **ec.VIEWS)
