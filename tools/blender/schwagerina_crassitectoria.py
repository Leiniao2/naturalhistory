"""
Procedural Schwagerina crassitectoria (Early Permian, early Leonardian schwagerinid fusulinid;
Dunbar & Skinner 1937, Glass Mountains, West Texas). The name means "thick roof".

A stout, robust, broadly inflated test with bluntly rounded poles and an unusually thick
keriothecal wall, plain in the broken section as heavy dark-and-light banded whorls and a
thick outer rim. Fewer, more widely spaced whorls. Grey-tan.
Built with nh_schwagerina.py: a cluster of three tests, one broken across its middle to show
the coiled keriothecal wall in section. Colour is in vertex colours.
Faces -Y (long axis of the main test along Y), pivot at the cluster centre (Drift style).

Usage:
  blender --background --python tools/blender/schwagerina_crassitectoria.py -- [--render out.png]

Output: Assets/Resources/Models/Species/SchwagerinaCrassitectoria.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_schwagerina as sch  # noqa: E402

SPEC = sch.Spec(
    name="SchwagerinaCrassitectoria",
    tests=[((0.0, 0.0, 0.0), 0, 0, 0, 0.74, 0.43, False),
           ((0.64, 0.46, 0.06), 62, 14, 70, 0.56, 0.32, True),
           ((-0.62, 0.42, -0.10), -38, -12, 140, 0.48, 0.27, False)],
    prof_p=2.2, prof_q=0.5, septa=18, furrow=0.08, flute=0.06,
    whorls=4.2, loose=1.5, wall=0.30, wall_out=0.42, rim=0.12,
    test=(0.84, 0.77, 0.64), test_tan=(0.68, 0.60, 0.48), furrow_col=(0.50, 0.45, 0.37),
    suture=(0.38, 0.33, 0.26), wall_col=(0.33, 0.29, 0.23), kerio=(0.58, 0.51, 0.40),
    chamber=(0.90, 0.87, 0.79), roughness=0.65,)


if __name__ == "__main__":
    sch.main(SPEC)
