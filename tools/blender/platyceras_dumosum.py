"""
Procedural Platyceras dumosum (Devonian sea snail, eastern North America) for the map
(Fixed style).

A cap-shaped, loosely coiled snail about 4 cm across: barely more than one whorl that
flares quickly into a wide, irregular aperture, its shell set with long hollow spines.
Platyceras snails lived perched on the cups of crinoids, over the crinoid's anus, feeding on
its waste for their whole adult life; fossils are often found still in place. Here one sits
on the calyx of a short-stalked crinoid with its arms folded. Cream shell with rusty spines
(colour conjectural). Built with nh_ord_echino.py.

Usage:
  blender --background --python tools/blender/platyceras_dumosum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Platyceras.fbx (pivot on the sea floor, z = 0)
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Matrix, Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_ord_echino as ec  # noqa: E402

SHELL = (0.86, 0.78, 0.60)
CORD = (0.66, 0.54, 0.38)
SPINE = (0.62, 0.36, 0.20)
CRINOID = (0.56, 0.44, 0.52)
CRINOID_DARK = (0.36, 0.26, 0.34)



def coil(t):
    """Centre line of the shell: a loose, fast-expanding spiral in the XZ plane, from the
    apex (t = 0, curled over the top) to the aperture (t = 1, opening downwards)."""
    phi = 1.7 * math.pi * (1.0 - t)
    R = 0.36 * math.exp(2.4 * (t - 1.0))
    return Vector((R * math.cos(phi), 0.0, R * math.sin(phi))), 0.22 * math.exp(2.2 * (t - 1.0)), phi


def shell_color(co, n):
    k = 0.5 + 0.5 * math.sin(math.atan2(co.y, co.x - 0.36) * 9.0 + co.z * 4)
    g = 0.5 + 0.5 * math.sin(co.length * 90)
    c = nh.lerp(SHELL, CORD, 0.45 * nh.smoothstep(0.7, 1.0, k))
    return tuple(x * (0.92 + 0.08 * g) for x in c)


def build():
    mb = nh.MeshBuilder()
    ec.mud_patch(mb, 0.75, ((0.36, 0.34, 0.30), (0.50, 0.47, 0.41)))
    # crinoid host: short stem, plated calyx, folded arm stubs
    stem = [Vector((0.03 * math.sin(t * 3), 0, 0.02 + 0.55 * t)) for t in [i / 8 for i in range(9)]]
    mb.add(nh.tube(stem, [0.07] * 9, sides=6), ec._columnal_color(CRINOID, CRINOID_DARK), smooth=False)
    for k in range(5):
        a = k / 5 * math.tau
        mb.add(nh.tube([(0, 0, 0.04), (math.cos(a) * 0.18, math.sin(a) * 0.18, 0.02), (math.cos(a + 0.4) * 0.3, math.sin(a + 0.4) * 0.3, 0.01)],
                       [0.05, 0.03, 0.0], sides=5), CRINOID_DARK)
    top = stem[-1]
    mb.add(nh.tube([top, top + Vector((0, 0, 0.12)), top + Vector((0, 0, 0.26))], [0.08, 0.2, 0.25], sides=10),
           lambda co, n: nh.lerp(CRINOID, CRINOID_DARK, 0.5 * nh.smoothstep(0.6, 1.0, abs(math.sin(math.atan2(co.y, co.x) * 2.5)))))
    for k in range(5):
        a = k / 5 * math.tau + 0.6
        b = top + Vector((math.cos(a) * 0.22, math.sin(a) * 0.22, 0.24))
        mb.add(nh.tube([b, b + Vector((math.cos(a) * 0.08, math.sin(a) * 0.08, 0.12)), b + Vector((math.cos(a) * 0.04, math.sin(a) * 0.04, 0.24))],
                       [0.06, 0.05, 0.0], sides=6), CRINOID)
    cup_top = top + Vector((0, 0, 0.26))
    mb.add(nh.ellipsoid(tuple(cup_top), (0.24, 0.24, 0.06), 2), CRINOID_DARK)

    # the snail on top of the cup, aperture clamped down onto the calyx
    N = 30
    pts, radii = [], []
    for i in range(N + 1):
        c, r, _phi = coil(i / N)
        pts.append(c)
        radii.append(r if i else 0.0)
    off = cup_top + Vector((-0.36, 0.0, 0.02))
    sb = nh.tube(pts, radii, sides=16, cap_start=False, cap_end=True)
    nh.transform(sb, Matrix.Translation(off))
    mb.add(sb, shell_color)
    # flared, wavy lip
    c, r, _ = coil(1.0)
    mb.add(nh.tube([off + c + Vector((0, 0, 0.03)), off + c - Vector((0, 0, 0.01))], [r * 1.02, r * 1.12], sides=16), CORD)
    # long hollow spines on the outer side and flanks of the whorl
    for i in range(5, N, 3):
        t = i / N
        c, r, phi = coil(t)
        out = Vector((math.cos(phi), 0.0, math.sin(phi)))
        for d in (out, (out + Vector((0, 0.9, 0))).normalized(), (out + Vector((0, -0.9, 0))).normalized()):
            b = off + c + d * r * 0.85
            mb.add(nh.tube([b, b + d * (0.08 + 0.7 * r)], [r * 0.14 + 0.006, 0.003], sides=6), SPINE)
    obj = mb.to_object("Platyceras", roughness=0.55)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Platyceras", **ec.VIEWS)
