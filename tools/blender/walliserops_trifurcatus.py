"""
Procedural Walliserops trifurcatus for the map: a spiny acastid (phacopid) trilobite from
the Early Devonian (Emsian, about 400 million years ago) of the Jebel Oufatene area,
Morocco; about 7-8 cm long without its spines.

Its trademark is a long, three-pronged "trident" growing forward from the front of the
head - possibly used by males in contests, like the horns of a stag beetle. It also had
big schizochroal eyes topped by a small spike, long genal spines sweeping back from the
cheeks, a tall spine on every axial ring of the thorax and long, backward-curving pleural
spines, plus spines on the small pygidium.

Built with nh_dev_trilobite.py plus the trident and eye spikes. Colours are unknown:
amber-brown. Faces -Y, pivot at the body centre (Swim style).

Usage:
  blender --background --python tools/blender/walliserops_trifurcatus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Walliserops.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_dev_trilobite as tri  # noqa: E402

SPEC = tri.Spec(
    name="Walliserops",
    length=1.0, ceph_frac=0.36, pyg_frac=0.18, ceph_w=0.36, thorax_w=0.30, pyg_w=0.20,
    dome=0.08, glabella=0.10, glabella_w=0.15, eye_size=0.8, eye_x=0.6, eye_h=0.07,
    genal_spine=0.42, axial_spines=0.10, pleural_spines=0.10, tubercles=0.3,
    rows_seg=3, cols=24,
    shell=(0.50, 0.34, 0.18), shell_light=(0.74, 0.56, 0.34), axis=(0.56, 0.38, 0.20),
    groove=(0.20, 0.12, 0.06), under=(0.44, 0.32, 0.20),
)


def extras(mb, body):
    s = SPEC
    yf = body.y_front
    z0 = body.height(0, yf + 0.06)
    # the trident: a long shaft from the glabella front, forking into three prongs
    shaft_end = (0, yf - 0.36, z0 + 0.10)
    mb.add(tri.spine((0, yf + 0.06, z0 - 0.01), (0, yf - 0.46, z0 + 0.12), 0.030), s.shell)
    for sx in (-1, 1):
        mb.add(tri.spine((sx * 0.005, shaft_end[1] + 0.02, shaft_end[2]),
                         (sx * 0.10, shaft_end[1] - 0.10, shaft_end[2] + 0.03), 0.016, bend=(sx * 0.03, 0, 0)),
               s.shell)
        ex, ey = body.eyes()[0 if sx < 0 else 1]
        z = body.height(ex, ey) + 0.07
        mb.add(tri.spine((ex, ey, z - 0.02), (ex, ey + 0.02, z + 0.08), 0.012), s.shell_light)
        # pygidial spines
        mb.add(tri.spine((sx * 0.10, body.y_back - 0.08, 0.0), (sx * 0.16, body.y_back + 0.12, -0.01), 0.014),
               s.shell)


if __name__ == "__main__":
    nh.run(lambda: tri.build(SPEC, extras), "Walliserops", views=((30, 40), (0, 85), (-90, 12), (150, 30)))
