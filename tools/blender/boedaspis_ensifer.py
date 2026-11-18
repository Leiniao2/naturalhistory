"""
Procedural Boedaspis ensifer (Middle Ordovician odontopleurid trilobite from the St Petersburg
region of Russia) for map colonies (Swim style).

Perhaps the spiniest of all trilobites: a small, flat odontopleurid shield ringed with long,
slender spines - long genal spines, a pair of very long spines rising from the occipital ring
and sweeping up and back over the body, rows of long pleural spines on each of the ten
thoracic segments and a fringe of spines round the tiny pygidium. Butterscotch-coloured,
pustulose shell, eyes on short stalks. Built with nh_ord_trilobite.py plus the occipital pair.
Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/boedaspis_ensifer.py -- [--render out.png]

Output: Assets/Resources/Models/Species/BoedaspisEnsifer.fbx
"""

import sys
from pathlib import Path

from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ord_trilobite as tri  # noqa: E402

SPEC = tri.Spec(
    name="BoedaspisEnsifer",
    length=0.95, segments=10, ceph_frac=0.32, pyg_frac=0.10,
    ceph_w=0.40, thorax_w=0.34, thorax_w_back=0.22, pyg_w=0.16,
    ceph_p=1.6, ceph_q=2.4, pyg_p=1.5, pyg_q=1.5,
    dome=0.05, axis_frac=0.38, axis_h=0.08, pyg_axis=0.6, pyg_ribs=1,
    glab_w=0.32, glab_front=0.9, glab_len=0.9, glab_h=0.09, glab_furrows=2,
    eye_size=0.6, eye_x=0.6, eye_y=0.4, eye_stalk=0.07,
    genal_spine=0.85, genal_spread=0.45, genal_r=0.028,
    pleural_spine=0.42, pleural_grow=0.10, pleural_back=0.55, pleural_r=0.016,
    pyg_spines=[(0.25, 0.32, 0.10), (0.55, 0.30, 0.35), (0.85, 0.26, 0.6)], border=0.1, rows_seg=3,
    shell=(0.70, 0.48, 0.20), shell_light=(0.88, 0.68, 0.36),
    axis=(0.60, 0.38, 0.15), groove=(0.34, 0.20, 0.08), under=(0.56, 0.40, 0.22),
    spine=(0.80, 0.58, 0.28),
)


def build():
    """tri.build() plus the pair of long occipital spines, added to its MeshBuilder just before
    it becomes an object (so they share the body's centring)."""
    body = tri.Body(SPEC)
    y0 = body.y_ceph - 0.05
    z0 = body.height(0.0, y0)
    orig = nh.MeshBuilder.to_object

    def to_object(self, name, roughness=0.6):
        for sx in (-1, 1):
            base = Vector((sx * 0.035, y0, z0 - 0.02))
            tip = base + Vector((sx * 0.12, 0.62, 0.36))
            self.add(tri.spine(base, tip, 0.026, bend=(0, -0.04, 0.10), flat=1.0), SPEC.spine)
        return orig(self, name, roughness)

    nh.MeshBuilder.to_object = to_object
    try:
        return tri.build(SPEC)
    finally:
        nh.MeshBuilder.to_object = orig


if __name__ == "__main__":
    nh.run(build, SPEC.name, **tri.VIEWS)
