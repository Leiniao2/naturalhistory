"""
Procedural Phillipsia gemmulifera (Early Carboniferous of Europe, a proetid trilobite about
3 cm long, one of the last trilobites) for map colonies (Swim style, a sea-floor crawler).

An oval proetid: a rounded cephalon with a big, bulbous, inflated glabella that is nearly
parallel-sided, large crescent-shaped (kidney) eyes close beside it, short genal spines,
nine thoracic segments with a raised axis, and a large, semicircular pygidium (tail shield)
almost as long as the head, with many axial rings and pleural ribs. Warm pinkish-tan shell.
Built with nh_sil_trilobite. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/phillipsia_gemmulifera.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Phillipsia.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_sil_trilobite as tr  # noqa: E402
import bmesh  # noqa: E402

SPEC = tr.Spec(
    name="Phillipsia",
    segments=9, ceph_frac=0.34, pyg_frac=0.32, W=0.46, thorax_w=0.44, thorax_w_back=0.40, pyg_w=0.40,
    ceph_p=2.2, ceph_q=2.0, pyg_p=2.2, pyg_q=1.5,
    dome=0.10, glab_front=0.13, glab_back=0.12, glab_h=0.10, glab_len=0.92, glab_furrows=2,
    axis_w=0.13, axis_h=0.07,
    eye="small", eye_x=0.24, eye_y=0.42, eye_size=2.0, genal_spine=0.12,
    pyg_rings=12, pyg_ribs=8, antenna=0.18,
    shell=(0.62, 0.42, 0.32), shell_light=(0.82, 0.64, 0.50), axis=(0.54, 0.34, 0.26), groove=(0.24, 0.13, 0.09),
    eye_col=(0.12, 0.10, 0.09),
)

def build():
    """tr.build, then make every shell's normals point outwards (with these proportions some
    cephalon faces came out flipped and rendered dark)."""
    obj = tr.build(SPEC)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()
    return obj


if __name__ == "__main__":
    nh.run(build, SPEC.name, **tr.VIEWS)
