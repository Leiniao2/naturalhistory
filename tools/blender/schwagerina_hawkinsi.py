"""
Procedural Schwagerina hawkinsi (Early Permian, early Leonardian schwagerinid fusulinid;
Dunbar & Skinner 1937, Glass Mountains, West Texas; now often placed in Chalaroschwagerina).

A large, elongate, subcylindrical test with a long straight-sided middle and bluntly rounded
poles, deep close septal furrows and loosely coiled outer whorls. Warm buff.
Built with nh_schwagerina.py: a cluster of three tests, one broken across its middle to show
the coiled keriothecal wall in section. Colour is in vertex colours.
Faces -Y (long axis of the main test along Y), pivot at the cluster centre (Drift style).

Usage:
  blender --background --python tools/blender/schwagerina_hawkinsi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/SchwagerinaHawkinsi.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_schwagerina as sch  # noqa: E402

SPEC = sch.Spec(
    name="SchwagerinaHawkinsi",
    tests=[((0.0, 0.0, 0.0), 0, 0, 0, 0.98, 0.30, False),
           ((0.60, 0.50, 0.06), 64, 14, 70, 0.74, 0.23, True),
           ((-0.58, 0.46, -0.10), -36, -12, 140, 0.62, 0.19, False)],
    prof_p=5.0, prof_q=0.42, septa=20, furrow=0.07, flute=0.05,
    whorls=5.5, loose=1.8, wall=0.14, wall_out=0.24, rim=0.05,
    test=(0.92, 0.80, 0.60), test_tan=(0.78, 0.62, 0.42), furrow_col=(0.58, 0.44, 0.28),
    suture=(0.46, 0.33, 0.20), wall_col=(0.42, 0.31, 0.20), kerio=(0.72, 0.58, 0.40),
    chamber=(0.96, 0.89, 0.74),)


if __name__ == "__main__":
    sch.main(SPEC)
