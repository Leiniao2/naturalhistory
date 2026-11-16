"""
Procedural devil clam (Tridacna tevoroa) for the map, Fixed style.

A giant clam of deep, dim reef slopes (roughly 25-200 m) around Tonga and Fiji, about
40-50 cm long, resting on coral rubble: a relatively thin, light shell, broadly oval,
cream-white with a faint pinkish tinge, with six or seven low, broad ribs whose backs
carry fine radial riblets and no fluted scales, the thin margin only gently scalloped.
Living where little light reaches, its mantle is dull - drab olive-brown with darker
brown patches and few markings - and stays inside the gape rather than spreading over
the shell edge; a row of small eye spots, a raised exhalant siphon and the slit of the
inhalant aperture complete it (see nh_tridacna.py). Pivot at the base (z = 0).

Usage:
  blender --background --python tools/blender/tridacna_tevoroa.py -- [--render out.png]

Output: Assets/Resources/Models/Species/DevilClam.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tridacna as tc  # noqa: E402

SHELL = (0.88, 0.82, 0.76)          # cream-white, faint pink
SHELL_DARK = (0.70, 0.62, 0.58)
FOULING = (0.50, 0.46, 0.38)
MANTLE = (0.36, 0.30, 0.18)         # drab olive-brown
MANTLE2 = (0.30, 0.27, 0.17)
PATCHES = (0.16, 0.12, 0.08)        # darker brown patches
EDGE = (0.40, 0.36, 0.24)
EYES = (0.55, 0.58, 0.50)


def build():
    return tc.build(
        "DevilClam", seed=13, length=1.5, height=0.88, inflation=0.30, spread=1.78,
        centre=(0.0, 0.44), ribs=7, rib_amp=0.035, rib_sharp=0.9, scallop=0.04,
        fine=5, fine_amp=0.016, gape=0.13, lip=0.018, n_theta=120, n_u=14,
        shell=SHELL, shell_dark=SHELL_DARK, fouling=FOULING, foul=0.25,
        mantle=MANTLE, mantle2=MANTLE2, pattern="mottle", pattern_col=PATCHES, pattern_scale=4.0,
        pattern_amt=0.9, edge_col=EDGE, edge_width=0.10, eye_col=EYES, eyes=44,
        over=0.035, droop=0.015, bulge=0.05, ruffle=0.01, mantle_frac=0.64, n_w=16, mantle_smooth=0.8,
        seat="rubble")


if __name__ == "__main__":
    nh.run(build, "DevilClam", ground=(0.55, 0.52, 0.45), views=((35, 30), (10, 70), (-90, 10)))
