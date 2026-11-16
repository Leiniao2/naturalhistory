"""
Procedural Choia carteri (Middle Cambrian demosponge, Burgess Shale, British Columbia) for the
map: a small, low conical disc of radiating spicule thatch with a starburst of long, slender
coronal spicules.

The real sponge has a flattened disc about 2 cm across, built of fine radiating monaxon
spicules (oxeas); longer, slightly stouter coronal spicules project up to ~2.5-3 cm past the
margin, so the whole animal spans up to ~5 cm. Proportions follow that here: the disc is
about 40% of the overall width and rises into a fairly steep, slightly domed cone with a
small osculum at its apex. Fine radial tracts (many narrow ribs, mostly as colour) stand for
the spicule thatch. Around it ~70 long, thin coronal spicules: one tier fans up and out from
the top of the margin, the other droops to rest on the mud, propping the unattached disc just
above the sea floor. Pale cream-buff body (colour is unknown; this is a plausible sponge tone)
with glassy whitish silica spicules. See nh_choia.py for the shared builder.
Fixed style: pivot on the ground (z = 0).

Usage:
  blender --background --python tools/blender/choia_carteri.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ChoiaCarteri.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import nh_model as nh  # noqa: E402
import nh_choia as nc  # noqa: E402

SPEC = nc.ChoiaSpec(
    seed=5,
    disc_r=0.40,
    disc_h=0.30,
    rim_t=0.07,
    cone_p=1.25,
    lift=0.06,
    segments=64,
    ribs=32,                       # fine thatch
    rib_depth=0.004,
    osculum_r=0.045,
    upper=(36, (0.50, 0.66), (0.012, 0.015), (12.0, 38.0)),
    lower=(32, (0.52, 0.66), (0.012, 0.015), (None, None)),
    jitter=0.15,
    sag=0.05,
    body=(0.88, 0.80, 0.62),
    body_dark=(0.64, 0.54, 0.38),
    rib_col=(0.96, 0.91, 0.76),
    osculum=(0.30, 0.22, 0.14),
    spicule_base=(0.82, 0.76, 0.62),
    spicule_tip=(0.97, 0.96, 0.91),
)


def build():
    return nc.build(SPEC, "ChoiaCarteri")


if __name__ == "__main__":
    nh.run(build, "ChoiaCarteri", ground=(0.36, 0.34, 0.30), views=((20, 30), (70, 12), (10, 75)))
