"""
Procedural Dicranurus monstrosus for the map: an odontopleurid trilobite from the Early
Devonian (Emsian, about 400 million years ago) of the Jebel Issoumour area, Morocco;
about 5-6 cm long without its spines.

Odontopleurids are the spiniest of all trilobites. Dicranurus is unmistakable for the
pair of great, ram's-horn spines rising from the occipital ring at the back of its head,
which sweep up, back and curl round outwards. It also had long genal spines, a long,
backward-curving spine on the tip of every one of its nine thoracic segments, a small
pygidium with a pair of long spines, and a finely tuberculate shell; its eyes sat on
low stalks.

Built with nh_dev_spiny.py (nh_ord_trilobite shell) plus the curled horns. Colours are
unknown: ochre with darker grooves. Faces -Y, pivot at the body centre (Swim style).

Usage:
  blender --background --python tools/blender/dicranurus_monstrosus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Dicranurus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_dev_spiny as sp  # noqa: E402

SHELL = (0.60, 0.40, 0.18)
LIGHT = (0.80, 0.60, 0.32)
HORN = (0.70, 0.50, 0.25)

SPEC = sp.tri.Spec(
    name="Dicranurus",
    length=0.9, segments=9, ceph_frac=0.34, pyg_frac=0.10,
    ceph_w=0.38, thorax_w=0.30, thorax_w_back=0.22, pyg_w=0.18,
    ceph_p=1.6, ceph_q=2.4, pyg_p=1.5, pyg_q=1.5,
    dome=0.05, axis_frac=0.40, axis_h=0.07, pyg_axis=0.6, pyg_ribs=1,
    glab_w=0.36, glab_front=0.9, glab_len=0.85, glab_h=0.10, glab_furrows=2,
    eye_size=0.6, eye_x=0.6, eye_y=0.40, eye_stalk=0.05,
    genal_spine=0.60, genal_spread=0.45, genal_r=0.026,
    pleural_spine=0.42, pleural_grow=0.10, pleural_back=0.75, pleural_r=0.015,
    pyg_spines=[(0.35, 0.50, 0.12), (0.75, 0.22, 0.45)], border=0.1, rows_seg=4,
    shell=SHELL, shell_light=LIGHT, axis=(0.52, 0.33, 0.14),
    groove=(0.20, 0.12, 0.05), under=(0.42, 0.30, 0.16),
)


def extras(mb, body):
    sp.tubercles(mb, body, 120, 0.008, LIGHT, seed=3)
    y0 = body.y_ceph - 0.05
    z0 = body.height(0.05, y0)
    for sx in (-1, 1):
        # ram's horn: up from the occipital ring, back over the thorax, then curling down
        # and round outwards in a widening spiral
        pts = []
        n = 26
        for i in range(n):
            t = i / (n - 1)
            a = math.pi * 1.75 * t                    # sweep angle round the coil
            r = 0.20 * (1.0 - 0.55 * t)
            cy, cz = y0 + 0.02, z0 + 0.20
            y = cy + r * math.sin(a) * 1.0
            z = cz - r * math.cos(a)
            x = sx * (0.05 + 0.22 * t ** 0.8)
            pts.append((x, y, z))
        sp.curl(mb, pts, 0.038, HORN)


if __name__ == "__main__":
    nh.run(lambda: sp.build(SPEC, extras), SPEC.name, **sp.VIEWS)
