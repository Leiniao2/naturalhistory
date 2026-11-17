"""
Procedural Lingulella chengjiangensis (Early Cambrian lingulid brachiopod, Chengjiang biota,
Yunnan, ~518 million years ago) for the map, Fixed style.

A tiny lamp shell about 1 cm long, known from Chengjiang with its soft parts preserved: a
thin, flattened, oval-to-subtriangular shell of two near-equal organophosphatic valves -
dark brown, banded with fine concentric growth lines around the pointed posterior beak and
paler at the thin margin - with a fringe of long setae radiating from the front and side
margins, and a long, slender, faintly annulated fleshy pedicle (longer than the shell)
leaving the beak. Three individuals stand up on their pedicles, anchored by small holdfasts
in a patch of grey-olive Chengjiang mud, leaning apart so their valves and setae read from
above. Shared lingulid code lives in nh_brachiopod.py.

Usage:
  blender --background --python tools/blender/lingulella_chengjiangensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/LingulellaChengjiangensis.fbx

Faces -Y; pivot at the base of the mud patch (z = 0).
"""

import math
import random
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_brachiopod as br  # noqa: E402

NAME = "LingulellaChengjiangensis"
MUD = ((0.30, 0.30, 0.24), (0.46, 0.44, 0.35))
SPEC = br.LingulidSpec(
    length=0.30, width=0.22, thick=0.022, widest=0.58, post_exp=1.1, ant_exp=2.1, fullness=1.7,
    growth_lines=7, n_len=26, n_around=24,
    shell=(0.24, 0.15, 0.09), shell_light=(0.46, 0.32, 0.19), margin=(0.62, 0.50, 0.32),
    commissure=(0.08, 0.05, 0.03),
    setae="fringe", setae_count=40, setae_len=0.24, setae_r=0.0035, setae_col=(0.62, 0.52, 0.34),
    pedicle_r=0.019, pedicle_col=(0.66, 0.54, 0.40), pedicle_col2=(0.48, 0.36, 0.26), pedicle_bands=26,
)

# (anchor x, y), beak height, lean direction (azimuth deg), lean (deg), facing azimuth (deg), size
INDIVIDUALS = (
    ((0.00, 0.02), 0.40, 200, 14, 0, 1.0),
    ((-0.26, 0.10), 0.30, 130, 30, -35, 0.85),
    ((0.22, 0.14), 0.33, 50, 26, 30, 0.92),
)


def build():
    rng = random.Random(5)
    mb = nh.MeshBuilder()
    height = br.seabed(mb, 0.44, MUD, seed=3, base=0.03, relief=0.012)
    for i, ((x, y), bh, laz, lean, faz, k) in enumerate(INDIVIDUALS):
        spec = replace(SPEC, length=SPEC.length * k, width=SPEC.width * k,
                       pedicle_r=SPEC.pedicle_r * (0.8 + 0.2 * k))
        anchor = Vector((x, y, height(x, y) - 0.006))
        la, le = math.radians(laz), math.radians(lean)
        lean_v = Vector((math.cos(la) * math.sin(le), math.sin(la) * math.sin(le), math.cos(le)))
        # pedicle runs up and out; the beak sits where it ends, shell continuing its line
        beak = anchor + Vector((lean_v.x * bh * 0.6, lean_v.y * bh * 0.6, bh))
        axis = (lean_v * 1.6 + Vector((0, 0, 0.6))).normalized()
        fa = math.radians(faz)
        face = Vector((math.sin(fa), -math.cos(fa), 0.25))
        br.place_lingulid(mb, spec, rng, beak, axis, face, anchor, seed=i + 1,
                          pedicle_slack=0.4, wiggle=0.005)
    return br.finish(mb, NAME, roughness=0.55)


if __name__ == "__main__":
    nh.run(build, NAME, ground=(0.30, 0.30, 0.24), background=(0.05, 0.14, 0.18), views=br.VIEWS)
