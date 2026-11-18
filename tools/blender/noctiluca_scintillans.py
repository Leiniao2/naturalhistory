"""
Procedural low-poly Noctiluca scintillans, "sea sparkle", a giant heterotrophic dinoflagellate.

One nearly spherical, balloon-like cell, clear blue-white and translucent-looking, flushed very
pale pink on the side with the groove (the ventral sulcus, a dimple with a short gutter across
it). From the central cytoplasmic mass beside the groove, fine pink cytoplasm strands radiate out
through the vacuole to the far side of the cell (drawn as colour on the surface, branching a
little). One stout, transversely striated, flexible tentacle hangs and curls down out of the
groove. Bright cyan-blue speckles over the surface stand for its bioluminescent scintillons.
Colour is in vertex colours (see nh_model).

Usage:
  blender --background --python tools/blender/noctiluca_scintillans.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Noctiluca.fbx
About 1.6 units tall/across including the tentacle; the groove and tentacle face -Y (front).
Pivot at the cell centre (Float).
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Matrix, Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402

SEED = 21
R = 0.62                    # cell radius
GROOVE = Vector((0.0, -1.0, -0.40)).normalized()   # direction of the groove from the centre
STRANDS = 13
SPECKLES = 22

CLEAR = (0.84, 0.93, 0.99)       # clear blue-white vacuole
BLUSH = (0.97, 0.89, 0.92)       # very pale pink side
STRAND = (0.92, 0.46, 0.60)      # pink cytoplasm strands
MASS = (0.92, 0.52, 0.62)        # central cytoplasm round the nucleus
GROOVE_C = (0.86, 0.66, 0.74)
TENTACLE = (0.96, 0.76, 0.70)
TENTACLE_BAND = (0.80, 0.52, 0.52)
GLOW = (0.30, 1.0, 1.0)


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()
    # local frame of the cell: +Z points into the groove; the gutter runs along local X
    rot = Vector((0, 0, 1)).rotation_difference(GROOVE).to_matrix().to_4x4()

    def deform(n):
        dimple = 0.13 * math.exp(-((1.0 - n.z) / 0.05))
        gutter = 0.05 * math.exp(-(n.y / 0.10) ** 2) * nh.smoothstep(0.35, 0.85, n.z)
        return 1.0 - dimple - gutter + 0.008 * noise.noise(n * 3.0)

    cell = nh.uv_ellipsoid((0, 0, 0), (R, R, R * 0.98), segments=40, rings=22, deform=deform)
    nh.transform(cell, rot)
    inv = rot.inverted()

    def cell_col(co, nrm):
        n = (inv @ co).normalized()
        theta = math.acos(max(-1.0, min(1.0, n.z)))          # 0 at the groove
        phi = math.atan2(n.y, n.x)
        c = nh.lerp(CLEAR, BLUSH, nh.smoothstep(1.5, 0.4, theta))
        # radiating strands: meridians from the groove, wandering and forking a little
        wob = 0.12 * noise.noise(Vector((math.cos(phi) * 2, math.sin(phi) * 2, theta * 1.5)))
        u = (phi + wob) * STRANDS / math.tau
        strand = math.exp(-(((u + 0.5) % 1.0 - 0.5) / 0.10) ** 2)
        fork = math.exp(-(((u * 2 + 0.5) % 1.0 - 0.5) / 0.13) ** 2) * nh.smoothstep(1.4, 2.0, theta)
        s = max(strand, fork * 0.8) * nh.smoothstep(0.25, 0.6, theta) * (1.0 - nh.smoothstep(2.3, 2.9, theta))
        c = nh.lerp(c, STRAND, s * 0.9)
        # the central cytoplasm mass beside the groove, and the groove itself
        c = nh.lerp(c, MASS, nh.smoothstep(0.55, 0.25, theta) * 0.85)
        return nh.lerp(c, GROOVE_C, nh.smoothstep(0.18, 0.05, theta))

    mb.add(cell, cell_col)

    # the tentacle: out of the groove, hanging down and curling forward at the tip
    base = GROOVE * R * 0.84
    pts, radii = [], []
    n = 26
    for k in range(n):
        t = k / (n - 1)
        down = 0.62 * t
        p = base + GROOVE * 0.10 * min(1.0, t * 4) + Vector((0.0, 0.0, -down))
        p += Vector((0.05 * math.sin(t * 3.0), -0.14 * t ** 2 + 0.10 * math.sin(t * math.pi) * t,
                     0.18 * nh.smoothstep(0.65, 1.0, t)))
        pts.append(p)
        radii.append(0.078 * (1.0 - 0.55 * t) if k < n - 1 else 0.02)
    total = sum((b - a).length for a, b in zip(pts, pts[1:]))
    lens = [0.0]
    for a, b in zip(pts, pts[1:]):
        lens.append(lens[-1] + (b - a).length)

    def tent_col(co, nrm):
        best = min(range(n), key=lambda i: (pts[i] - co).length_squared)
        band = 1.0 if best % 2 else 0.0                        # transverse striations
        c = nh.lerp(TENTACLE, TENTACLE_BAND, band * 0.7)
        return nh.lerp(c, BLUSH, nh.smoothstep(0.15, 0.0, lens[best] / total) * 0.6)

    mb.add(nh.tube(pts, radii, sides=7), tent_col)

    # bioluminescent speckles (scintillons) on the surface
    placed = 0
    while placed < SPECKLES:
        d = Vector((rng.gauss(0, 1), rng.gauss(0, 1), rng.gauss(0, 1))).normalized()
        if d.dot(GROOVE) > 0.75:
            continue
        r = rng.uniform(0.024, 0.036)
        q = d.rotation_difference(Vector((0, 0, 1))).to_matrix()
        sp = nh.ellipsoid((0, 0, 0), (r, r, r * 0.45), subdivisions=1, rotation=q.inverted())
        nh.transform(sp, Matrix.Translation(d * (R * 0.99)))
        mb.add(sp, GLOW)
        placed += 1
    return mb.to_object("Noctiluca", roughness=0.25)


if __name__ == "__main__":
    nh.run(build, "Noctiluca", background=(0.02, 0.06, 0.12), views=((35, 20), (-70, 5), (180, 40)))
