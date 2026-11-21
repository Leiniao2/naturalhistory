"""
Procedural Spheniscus urbinai (Late Miocene of Peru and Chile) for map
colonies: an extinct banded penguin, larger than its living relative the
Humboldt penguin.

A stout penguin about 90 cm long with a long, dagger-like bill for catching
fish, black back and flippers, white belly crossed by a black breast band and
a white stripe curving over the eye, as in the living banded penguins.
Built with nh_pal_bird.py (swimming penguin body). Faces -Y, pivot at the
body centre.

Usage:
  blender --background --python tools/blender/spheniscus_urbinai.py -- [--render out.png]

Output: Assets/Resources/Models/Species/SpheniscusUrbinai.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_pal_bird as nb  # noqa: E402

SPEC = nb.Penguin(
    name="SpheniscusUrbinai",
    length=1.5, girth=0.27, beak_len=0.30, flipper=0.48,
    back=(0.10, 0.10, 0.11), belly=(0.93, 0.92, 0.89), beak_col=(0.14, 0.12, 0.11),
    foot_col=(0.30, 0.26, 0.24),
)
BAND = (0.08, 0.08, 0.09)


def build():
    obj = nb.build_penguin(SPEC)
    L, g = SPEC.length, SPEC.girth
    me = obj.data
    col = me.vertex_colors.get("Col") if hasattr(me, "vertex_colors") and me.vertex_colors else None
    attr = me.color_attributes.get("Col") if col is None else None
    vs = me.vertices
    ymin = min(v.co.y for v in vs)
    for poly in me.polygons:
        for li in poly.loop_indices:
            co = vs[me.loops[li].vertex_index].co
            t = (co.y - ymin) / L
            c = (col.data[li].color if col else attr.data[li].color)
            # black band across the breast, curving up the flanks
            if 0.27 < t - 0.06 * (co.z / g) < 0.33 and co.z < g * 0.2 and c[0] > 0.5:
                c = (*BAND, 1.0)
            # white stripe from above the eye back over the cheek
            elif 0.12 < t < 0.25 and abs(abs(co.x) - g * 0.36) < g * 0.12 and abs(co.z - g * (0.18 - 0.25 * (t - 0.12))) < g * 0.07:
                c = (*SPHE_W, 1.0)
            else:
                continue
            if col:
                col.data[li].color = c
            else:
                attr.data[li].color = c
    return obj


SPHE_W = (0.93, 0.92, 0.89)

if __name__ == "__main__":
    nh.run(build, SPEC.name, background=(0.05, 0.22, 0.32), views=((35, 25), (-90, 5), (0, 80)))
