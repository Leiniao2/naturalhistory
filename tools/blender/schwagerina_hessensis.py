"""
Procedural Schwagerina hessensis (Early Permian, early Leonardian schwagerinid fusulinid;
Dunbar & Skinner 1937, Hess Limestone, Glass Mountains, West Texas).

An inflated fusiform test, fattest at the middle and tapering to more pointed poles, with
strongly fluted septa showing as deep, close furrows and loosely coiled outer whorls. Pale cream.
Built with nh_schwagerina.py: a cluster of three tests, one broken across its middle to show
the coiled keriothecal wall in section. Colour is in vertex colours.
Faces -Y (long axis of the main test along Y), pivot at the cluster centre (Drift style).

Usage:
  blender --background --python tools/blender/schwagerina_hessensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/SchwagerinaHessensis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_schwagerina as sch  # noqa: E402

SPEC = sch.Spec(
    name="SchwagerinaHessensis",
    tests=[((0.0, 0.0, 0.0), 0, 0, 0, 0.82, 0.40, False),
           ((0.64, 0.48, 0.06), 60, 14, 70, 0.60, 0.29, True),
           ((-0.62, 0.44, -0.10), -40, -12, 140, 0.52, 0.25, False)],
    prof_p=1.8, prof_q=0.68, pole_point=0.3, septa=22, furrow=0.065, flute=0.07,
    whorls=5.0, loose=1.6, wall=0.15, wall_out=0.25, rim=0.05,
    test=(0.95, 0.89, 0.74), test_tan=(0.82, 0.70, 0.52), furrow_col=(0.62, 0.50, 0.35),
    suture=(0.48, 0.37, 0.24), wall_col=(0.45, 0.35, 0.24), kerio=(0.74, 0.63, 0.47),
    chamber=(0.98, 0.94, 0.84),)


if __name__ == "__main__":
    sch.main(SPEC)
