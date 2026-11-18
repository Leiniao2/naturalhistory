"""
Procedural Tulerpeton curtum for the map: a Late Devonian (Famennian, about 365 million
years ago) tetrapod from Andreyevka in the Tula region of Russia; about a metre long.

Known from a partial skeleton with well-preserved limbs: unlike the paddle-limbed
Acanthostega and Ichthyostega, its limbs were relatively slender and strong, with a sturdy
shoulder girdle, so it was probably better at moving on land. Both the hand and the foot
had six digits. It lived in a shallow coastal lagoon; here it is reconstructed with a
broad, flat skull and eyes on top, a low body and a long tail with a low fin fold.

Built with nh_car_tetrapod (six toes per foot, longer legs held higher than the
Carboniferous Pederpes) plus a low fin fold along the top and bottom of the tail.
Colours are unknown: grey-green with dark blotches and a pale belly.

Usage:
  blender --background --python tools/blender/tulerpeton_curtum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Tulerpeton.fbx (Ground: pivot on the ground,
facing -Y).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmesh  # noqa: E402
from mathutils import Vector  # noqa: E402

import nh_car_tetrapod as tp  # noqa: E402

FIN = (0.30, 0.26, 0.17)
FIN_EDGE = (0.62, 0.56, 0.38)


def tail_fins(sp, spine):
    """Low fin folds above and below the tail, as thin strips."""
    out = []
    s0, s1 = spine.s_trunk + sp.tail_len * 0.15, spine.s_end * 0.995
    n = 24
    for sign, hmax in ((1, 0.045), (-1, 0.028)):
        bm = bmesh.new()
        col = bm.loops.layers.color.new("Col")
        base, edge = [], []
        for i in range(n):
            t = i / (n - 1)
            s = s0 + (s1 - s0) * t
            p = spine.at(s)
            rz = spine.rz(s)
            h = hmax * (min(1.0, t * 4.0) * (1.0 - t) ** 0.5) + 0.002
            z0 = p.z + sign * rz * 0.8
            base.append(Vector((p.x, p.y, z0)))
            edge.append(Vector((p.x, p.y + 0.006, z0 + sign * (rz * 0.2 + h))))
        th = 0.0025
        rows = []
        for pts in (base, edge):
            rows.append([(bm.verts.new(q + Vector((th, 0, 0))), bm.verts.new(q - Vector((th, 0, 0)))) for q in pts])
        for i in range(n - 1):
            for k, c in ((0, FIN), (1, FIN)):
                quad = [rows[0][i][k], rows[0][i + 1][k], rows[1][i + 1][k], rows[1][i][k]]
                f = bm.faces.new(quad if k == 0 else list(reversed(quad)))
                for lp in f.loops:
                    cc = FIN_EDGE if lp.vert in (rows[1][i][k], rows[1][i + 1][k]) else c
                    lp[col] = (cc[0], cc[1], cc[2], 1.0)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        out.append((bm, None))
    return out


SPEC = tp.Spec(
    name="Tulerpeton",
    head_len=0.17, head_w=0.070, head_h=0.026, snout=0.50,
    neck_len=0.03, neck_r=0.055,
    trunk_len=0.42, trunk_r=0.072, trunk_h=0.72,
    tail_len=0.55, tail_r=0.036, tail_fin=1.5, tail_curve=0.14,
    leg_r=0.016, front=(0.075, 0.080), hind=(0.085, 0.085), foot=0.042, toes=6,
    back=(0.30, 0.29, 0.18), flank=(0.50, 0.48, 0.32), belly=(0.84, 0.78, 0.58),
    pattern="blotches", pattern_col=(0.10, 0.10, 0.06), pattern_scale=0.8,
    head_col=(0.33, 0.31, 0.20), iris=(0.80, 0.62, 0.18), eye_r=0.012, eye_at=0.58, eye_up=0.75,
    teeth=9, tooth_len=0.006, lateral_line=True,
    voxel=0.006, max_tris=6000,
    extra=[tail_fins],
)

if __name__ == "__main__":
    tp.run(SPEC)
