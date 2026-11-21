"""
Procedural Ambonychia radiata (Late Ordovician pterioid bivalve, Cincinnati region) for map
colonies (Fixed style).

A thick, strongly inflated clam about 4 cm tall, taller than long, with a pointed beak
(umbo) at the top front from which strong, rounded ribs fan out over both valves to a
broad, rounded lower margin. It stood upright on its edge, anchored to shells and other
hard bits on the sea floor by a tuft of byssal threads from the front, filtering water
between its gaping valves. Two shells of different sizes on mud. Buff with darker ribs.
Pivot on the sea floor (z = 0), facing -Y.

Usage:
  blender --background --python tools/blender/ambonychia_radiata.py -- [--render out.png]

Output: Assets/Resources/Models/Species/AmbonychiaRadiata.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Matrix, Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_b2_ordovician_kit as kit  # noqa: E402

NAME = "AmbonychiaRadiata"
SHELL = (0.80, 0.70, 0.52)
RIB = (0.56, 0.44, 0.30)
DARK = (0.30, 0.22, 0.15)
BYSSUS = (0.62, 0.52, 0.30)

A_UMBO = math.atan2(0.62, -0.30)
UMBO = Vector((0, -0.24, 0.52))   # (x, y, z) in shell space: commissure plane is y-z


def outline(a):
    r = 1.0 / math.sqrt((math.cos(a) / 0.40) ** 2 + (math.sin(a) / 0.48) ** 2)
    da = math.atan2(math.sin(a - A_UMBO), math.cos(a - A_UMBO))
    return r * (1.0 + 0.45 * math.exp(-(da / 0.30) ** 2)) * (1.0 + 0.10 * math.cos(a + 0.3))


def make(mb, m, seed):
    def col(co, n, m_inv=m.inverted()):
        p = m_inv @ co
        d = Vector((p.y - UMBO.y, p.z - UMBO.z))
        ang = math.atan2(d.x, -d.y)
        rib = 0.5 + 0.5 * math.cos(ang * 26)
        c = nh.lerp(SHELL, RIB, 0.9 * nh.smoothstep(0.45, 0.9, rib) * nh.smoothstep(0.05, 0.25, d.length))
        g = 0.5 + 0.5 * math.sin(d.length * 55)
        c = nh.lerp(c, DARK, 0.15 * nh.smoothstep(0.8, 1.0, g))
        if abs(p.x) < 0.012:
            c = DARK
        return c
    for side in (1, -1):
        bm = kit.valve(outline, 0.24, side=side, peak=(-0.45, 0.62), power=0.55)
        # slight gape
        nh.transform(bm, Matrix.Translation((side * 0.006, 0, 0)))
        nh.transform(bm, m)
        mb.add(bm, col)
    # byssal threads from the front, fanning down to the mud
    rnd = kit.seeded(seed)
    root = m @ Vector((0, -0.30, -0.05))
    for k in range(7):
        tip = Vector((root.x + rnd.uniform(-0.12, 0.12), root.y - rnd.uniform(0.08, 0.22), 0.02))
        mid = root.lerp(tip, 0.5) + Vector((0, 0, 0.03))
        mb.add(nh.tube([root, mid, tip], [0.008, 0.006, 0.004], sides=4), BYSSUS)


def build():
    mb = nh.MeshBuilder()
    kit.mud(mb, 0.85)
    make(mb, Matrix.Translation((0.0, 0.0, 0.45)) @ Matrix.Rotation(0.25, 4, 'Z'), 1)
    make(mb, Matrix.Translation((0.48, 0.30, 0.25)) @ Matrix.Rotation(-0.6, 4, 'Z') @ Matrix.Scale(0.55, 4), 2)
    return kit.finish_fixed(mb, NAME)


if __name__ == "__main__":
    nh.run(build, NAME, **kit.VIEWS)
