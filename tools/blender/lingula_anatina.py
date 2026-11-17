"""
Procedural Lingula anatina (living lingulid brachiopod, Indo-Pacific tidal flats) for the map,
Fixed style.

A "living fossil" lamp shell: an elongate, tongue-shaped, flattened shell about 4-5 cm long,
of two thin, near-equal organophosphatic valves - glossy olive-green to greenish brown,
banded with growth lines around the posterior beak, paler at the margin, the front edge
squarely truncated - and a long, thick, translucent pale fleshy pedicle. It lives upright
in a vertical burrow in intertidal sand and mud with only the front margin at the surface,
where the setae along the margin are gathered into three funnels, the setal
"pseudosiphons" (inhalant at the sides, exhalant in the middle). Shown as three animals in
small sediment mounds round dark burrow openings: one feeding with its setal funnels just
at the surface, one half emerged, and one stretched right up out of its burrow so the
shell and the top of its pedicle, running down into the hole, read at map scale. Shared
lingulid code lives in nh_brachiopod.py.

Usage:
  blender --background --python tools/blender/lingula_anatina.py -- [--render out.png]

Output: Assets/Resources/Models/Species/LingulaAnatina.fbx

Faces -Y; pivot at the base of the sediment patch (z = 0).
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Matrix, Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_brachiopod as br  # noqa: E402

NAME = "LingulaAnatina"
SAND = ((0.50, 0.46, 0.37), (0.68, 0.63, 0.50))
HOLE = (0.24, 0.20, 0.15)
SPEC = br.LingulidSpec(
    length=0.52, width=0.21, thick=0.026, widest=0.68, post_exp=1.7, ant_exp=3.2, fullness=3.0,
    growth_lines=6, n_len=30, n_around=26,
    shell=(0.32, 0.30, 0.15), shell_light=(0.47, 0.43, 0.25), margin=(0.70, 0.64, 0.44),
    commissure=(0.10, 0.10, 0.05),
    setae="siphons", setae_count=30, setae_len=0.10, setae_r=0.0035, setae_col=(0.46, 0.40, 0.26),
    pedicle_r=0.038, pedicle_col=(0.88, 0.79, 0.68), pedicle_col2=(0.80, 0.70, 0.60), pedicle_bands=9,
)

# (x, y), how far the beak sits above (+) or below (-) the burrow mouth, lean azimuth/angle (deg),
# facing azimuth (deg)
INDIVIDUALS = (
    ((-0.24, 0.10), -0.43, 0, 4, 10),        # feeding: only the setal funnels at the surface
    ((0.04, -0.06), -0.20, 210, 10, -10),    # half emerged
    ((0.24, 0.16), 0.17, 40, 26, 25),        # stretched out of its burrow, pedicle showing
)


def build():
    rng = random.Random(9)
    mb = nh.MeshBuilder()
    bumps = [(x, y, 0.17, 0.11) for (x, y), *_ in INDIVIDUALS]
    pits = [(x, y, 0.085, 0.07, HOLE) for (x, y), *_ in INDIVIDUALS]
    height = br.seabed(mb, 0.5, SAND, seed=7, base=0.03, relief=0.01, bumps=bumps, pits=pits)
    for i, ((x, y), dz, laz, lean, faz) in enumerate(INDIVIDUALS):
        mouth = Vector((x, y, height(x, y)))
        la, le = math.radians(laz), math.radians(lean)
        axis = Vector((math.cos(la) * math.sin(le), math.sin(la) * math.sin(le), math.cos(le)))
        beak = mouth + axis * (dz / axis.z)
        fa = math.radians(faz)
        face = Vector((math.sin(fa), -math.cos(fa), 0.0))
        # the pedicle runs straight down the burrow, well below the surface
        anchor = mouth + Vector((0, 0, -0.5))
        br.place_lingulid(mb, SPEC, rng, beak, axis, face, anchor, seed=i + 1,
                          pedicle_slack=0.3, wiggle=0.004, holdfast=False)
        # the burrow mouth: a dark slit-shaped opening round the shell, in a raised collar
        rot = Matrix.Rotation(math.atan2(face.y, face.x) + math.pi / 2, 3, "Z")
        mb.add(nh.ellipsoid(tuple(mouth + Vector((0, 0, 0.012))), (0.19, 0.12, 0.022), subdivisions=2, rotation=rot,
                            deform=lambda n, k=i: 1.0 + 0.12 * noise.noise(n * 2.0 + Vector((k * 3.0, 0, 0)))),
               lambda co, n: nh.lerp(SAND[0], SAND[1], 0.4 + 0.4 * noise.noise(co * 8.0)))
        mb.add(nh.ellipsoid(tuple(mouth + Vector((0, 0, 0.030))), (0.115, 0.045, 0.006), subdivisions=2, rotation=rot), HOLE)
    return br.finish(mb, NAME, roughness=0.35, floor=0.0)


if __name__ == "__main__":
    nh.run(build, NAME, ground=(0.50, 0.46, 0.37), background=(0.05, 0.14, 0.18), views=br.VIEWS)
