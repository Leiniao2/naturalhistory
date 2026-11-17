"""
Procedural Schwagerina guembeli (Early Permian, early Leonardian schwagerinid fusulinid;
Dunbar & Skinner 1937, Glass Mountains, West Texas; now placed in Praeskinnerella).

Smaller and slender: an elongate fusiform test, narrow for its length, tapering gently to
bluntly pointed poles, with close regular septal furrows. Pale cream-grey.
Built with nh_schwagerina.py: a cluster of three tests, one broken across its middle to show
the coiled keriothecal wall in section. Colour is in vertex colours.
Faces -Y (long axis of the main test along Y), pivot at the cluster centre (Drift style).

Usage:
  blender --background --python tools/blender/schwagerina_guembeli.py -- [--render out.png]

Output: Assets/Resources/Models/Species/SchwagerinaGuembeli.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_schwagerina as sch  # noqa: E402

SPEC = sch.Spec(
    name="SchwagerinaGuembeli",
    tests=[((0.0, 0.0, 0.0), 0, 0, 0, 0.72, 0.19, False),
           ((0.40, 0.36, 0.05), 58, 14, 70, 0.54, 0.15, True),
           ((-0.40, 0.32, -0.08), -34, -12, 140, 0.46, 0.125, False)],
    prof_p=1.9, prof_q=0.62, pole_point=0.15, septa=16, furrow=0.07, flute=0.05,
    whorls=5.5, loose=1.4, wall=0.14, wall_out=0.22, rim=0.05,
    test=(0.91, 0.87, 0.76), test_tan=(0.76, 0.69, 0.55), furrow_col=(0.56, 0.51, 0.42),
    suture=(0.43, 0.38, 0.30), wall_col=(0.40, 0.35, 0.28), kerio=(0.70, 0.65, 0.55),
    chamber=(0.96, 0.94, 0.88),)


if __name__ == "__main__":
    sch.main(SPEC)
