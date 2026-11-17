"""
Procedural Phacops latifrons for the map: the classic Middle Devonian phacopid trilobite
(Eifelian-Givetian, about 393-383 million years ago), abundant in the Eifel hills of
Germany and also known from Morocco, Spain and Bolivia; usually 4-6 cm long.

The best-known schizochroal eye of any trilobite: each big kidney-shaped eye carries
dozens of separate, large calcite lenses in vertical rows. The cephalon is dominated by
a huge, tuberculate glabella swelling forward over the front margin; the genal angles
are rounded (no spines), the thorax has 11 segments and the pygidium is small and
rounded. Phacops is famous for being found tightly enrolled, like a pill-bug.

Built with nh_dev_trilobite.py. Colours are unknown: dark grey-brown with a warmer
glabella. Faces -Y, pivot at the body centre (Swim style, like the other trilobites).

Usage:
  blender --background --python tools/blender/phacops_latifrons.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PhacopsLatifrons.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_dev_trilobite as tri  # noqa: E402

SPEC = tri.Spec(
    name="PhacopsLatifrons",
    ceph_frac=0.36, pyg_frac=0.17, ceph_w=0.54, thorax_w=0.50, pyg_w=0.34,
    dome=0.12, glabella=0.17, glabella_w=0.24, eye_size=1.15, eye_x=0.62, eye_h=0.09,
    tubercles=0.35,
    shell=(0.30, 0.29, 0.28), shell_light=(0.58, 0.56, 0.52), axis=(0.44, 0.36, 0.28),
    groove=(0.14, 0.11, 0.08), under=(0.40, 0.34, 0.27),
)

if __name__ == "__main__":
    nh.run(lambda: tri.build(SPEC), "PhacopsLatifrons", views=((30, 40), (0, 85), (-90, 12), (150, 30)))
