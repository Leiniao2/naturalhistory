"""
Procedural Babinka prima (Early Ordovician bivalve, Bohemia) for map colonies (Fixed style).

A small, smooth, oval clam about 2 cm long with low, slightly forward-turned beaks and
fine concentric growth lines. It is famous for the inside of its shell: a ring of eight
pairs of separate muscle scars, like those of the single-shelled monoplacophorans, a clue
to how bivalves arose from simpler molluscs. It lived half-buried in the soft sea floor,
pushing itself along with its muscular foot. Shown upright, half sunk in a mound of mud,
foot reaching out. Pale cream with greyish growth bands. Pivot on the sea floor (z = 0),
facing -Y.

Usage:
  blender --background --python tools/blender/babinka_prima.py -- [--render out.png]

Output: Assets/Resources/Models/Species/BabinkaPrima.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Matrix, Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_b2_ordovician_kit as kit  # noqa: E402

NAME = "BabinkaPrima"
SHELL = (0.86, 0.82, 0.70)
BAND = (0.62, 0.60, 0.54)
DARK = (0.32, 0.28, 0.22)
FOOT = (0.88, 0.62, 0.54)
UMBO = Vector((0, -0.12, 0.30))


def outline(a):
    r = 1.0 / math.sqrt((math.cos(a) / 0.52) ** 2 + (math.sin(a) / 0.36) ** 2)
    return r


def build():
    mb = nh.MeshBuilder()
    # mud mound the shell is sunk into
    mound = kit.heightfield_disc(0.9, lambda x, y: 0.03 + 0.17 * math.exp(-((x / 0.32) ** 2 + (y / 0.55) ** 2))
                                 + 0.008 * noise.noise(Vector((x * 9, y * 9, 0))), n_r=18, n_a=48)
    mb.add(mound, lambda co, n: nh.lerp(kit.MUD[0], kit.MUD[1], 0.5 + 0.5 * noise.noise(co * 6)))
    m = Matrix.Translation((0, 0.02, 0.32)) @ Matrix.Rotation(0.12, 4, 'Y')

    def col(co, n, m_inv=m.inverted()):
        p = m_inv @ co
        d = Vector((p.y - UMBO.y, (p.z - UMBO.z) * 1.3)).length
        g = 0.5 + 0.5 * math.sin(d * 60)
        c = nh.lerp(SHELL, BAND, 0.35 * nh.smoothstep(0.7, 1.0, g) + 0.25 * nh.smoothstep(0.35, 0.5, d % 0.5))
        if abs(p.x) < 0.01:
            c = DARK
        return c
    for side in (1, -1):
        bm = kit.valve(outline, 0.15, side=side, peak=(-0.2, 0.75), power=0.6)
        nh.transform(bm, Matrix.Translation((side * 0.004, 0, 0)))
        nh.transform(bm, m)
        mb.add(bm, col)
    # muscular foot pushing into the mud at the front
    mb.add(nh.tube([(0, -0.40, 0.14), (0, -0.56, 0.12), (0, -0.66, 0.08)], [0.07, 0.06, 0.0], sides=10,
                   scale_xy=(0.6, 1.0)), FOOT)
    return kit.finish_fixed(mb, NAME)


if __name__ == "__main__":
    nh.run(build, NAME, **kit.VIEWS)
