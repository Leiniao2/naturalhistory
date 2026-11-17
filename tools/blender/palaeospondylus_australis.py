"""
Procedural Palaeospondylus australis (Early Devonian, Queensland, Australia) for the map (Swim style).

Described in 2025 (National Science Review) from the Cravens Peak Beds of the Georgina Basin,
western Queensland: limestone of late Emsian age (about 400 million years old) laid down in a
shallow marine setting, some 10 million years older than the Scottish P. gunni. Acid
preparation and CT scanning yielded an uncrushed, three-dimensional braincase (the holotype)
and some two hundred isolated elements referred to the species (jaw and gill-arch pieces,
vertebral centra, neural and haemal arches), but no articulated body. It differs from
P. gunni in a slightly longer pre-otic (front) part of the braincase and a dorsal fontanelle
with a narrow, pointed rather than transverse rear border.

The whole-body form is therefore reconstructed after P. gunni: a tiny, eel-like animal with a
cartilaginous skull, a ring of rostral cirri at the snout, a column of ring-shaped centra and a
caudal fin fold on forked radials. Here the snout is a little longer, the fontanelle tapers to
a point at the back, and the colours are a greyer, sandier marine tone.

Built with the machinery of palaeospondylus_gunni.py (lofted skull and body, fin-fold slabs,
fused with nh_model.MeshBuilder.fuse and decimated; crisp rostral ring, cirri and eyes), with
its own proportions in P.

Usage:
  blender --background --python tools/blender/palaeospondylus_australis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PalaeospondylusAustralis.fbx
Pivot at the body centre, faces -Y, dorsal side up (+Z). About 2 units long.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import palaeospondylus_gunni as pg  # noqa: E402  (Palaeospondylus builder, configured via pg.P)

P = dict(pg.P)
P.update(
    name="PalaeospondylusAustralis",
    y_tip=-1.00, y_skull=-0.62,
    # longer pre-otic region: the snout runs further ahead of the otic capsules
    half_w=[(-1.00, 0.026), (-0.95, 0.048), (-0.86, 0.066), (-0.74, 0.080), (-0.66, 0.088), (-0.60, 0.064),
            (-0.48, 0.052), (-0.10, 0.052), (0.30, 0.042), (0.65, 0.024), (0.97, 0.004)],
    half_h=[(-1.00, 0.020), (-0.95, 0.032), (-0.86, 0.042), (-0.74, 0.048), (-0.66, 0.050), (-0.60, 0.052),
            (-0.48, 0.060), (-0.10, 0.064), (0.30, 0.052), (0.65, 0.030), (0.97, 0.005)],
    nasal=(-0.93, 0.036), otic=(-0.70, 0.078),
    lamella=dict(y=-0.555, x=0.068, r=(0.040, 0.072, 0.011)),
    eye=dict(y=-0.81, r=0.011),
    fontanelle=(-0.76, 0.03, 0.075, 0.85),
    colors=dict(pg.P["colors"], back=(0.36, 0.34, 0.29), flank=(0.52, 0.49, 0.42), belly=(0.76, 0.73, 0.64),
                skull=(0.68, 0.63, 0.52), ring=(0.25, 0.23, 0.19), fin=(0.70, 0.67, 0.57),
                ray=(0.40, 0.37, 0.30), cirri=(0.74, 0.69, 0.56)),
)


def main():
    pg.P = P
    pg.main()


if __name__ == "__main__":
    main()
