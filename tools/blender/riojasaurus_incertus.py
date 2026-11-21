"""
Procedural Riojasaurus incertus (Late Triassic sauropodomorph dinosaur, ~6.5 m).

A heavy, early long-necked dinosaur from La Rioja, Argentina: a small head with leaf-shaped
teeth on a long neck, a bulky, deep body, a long tail and four stout, pillar-like legs (it
walked on all fours, unlike its two-legged relative Plateosaurus), with a big thumb claw.
Built with nh_tri_tetrapod; painted grey-brown with pale flanks and dark bands.
Faces -Y, pivot on the ground.

Output: Assets/Resources/Models/Species/Riojasaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tri_tetrapod as tt  # noqa: E402


def sway(y):
    s = max(0.0, (y - 0.2) / 0.8)
    return 0.07 * s * s


AXIS = [
    (-1.00, 0.800, 0.007, 0.010),
    (-0.97, 0.806, 0.018, 0.022),
    (-0.93, 0.816, 0.026, 0.032),
    (-0.885, 0.822, 0.030, 0.038),
    (-0.845, 0.808, 0.026, 0.032),
    (-0.77, 0.765, 0.034, 0.040),
    (-0.68, 0.705, 0.046, 0.054),
    (-0.58, 0.630, 0.070, 0.080),
    (-0.46, 0.575, 0.120, 0.135),
    (-0.30, 0.555, 0.160, 0.185),
    (-0.13, 0.560, 0.165, 0.190),
    (0.03, 0.575, 0.135, 0.150),
    (0.18, 0.570, 0.086, 0.100),
    (0.38, 0.530, 0.058, 0.070, sway(0.38)),
    (0.58, 0.470, 0.036, 0.044, sway(0.58)),
    (0.78, 0.410, 0.020, 0.024, sway(0.78)),
    (0.98, 0.350, 0.004, 0.004, sway(0.98)),
]

LEGS = tt.Limb(pts=[(0.12, 0.02, 0.52), (0.14, -0.05, 0.32), (0.135, 0.03, 0.11), (0.135, -0.01, 0.024)],
               radii=[0.100, 0.068, 0.048, 0.040], toes=4, toe_len=0.06, toe_r=0.022, toe_spread=50,
               stride=8, claw_len=0.022, sole=(0.05, 0.06, 0.024))
ARMS = tt.Limb(pts=[(0.11, -0.36, 0.46), (0.135, -0.33, 0.28), (0.13, -0.37, 0.10), (0.13, -0.39, 0.022)],
               radii=[0.072, 0.054, 0.040, 0.034], toes=5, toe_len=0.045, toe_r=0.017, toe_spread=60,
               claw_len=0.018, stride=-8, sole=(0.04, 0.05, 0.022))


def thumb_claws(mb, surf, spec):
    for sx in (1, -1):
        hand = tt.limb_chain(ARMS, sx)[-1]
        base = hand + tt.Vector((sx * -0.03, -0.03, 0.03))
        mb.add(tt.curved_spike(base, (sx * -0.5, -1.0, 0.3), 0.06, 0.013, bend=(0, 0, -0.6)), tt.CLAW)


SPEC = tt.TetrapodSpec(
    name="Riojasaurus",
    axis=AXIS,
    blobs=[((0.10, 0.03, 0.49), (0.09, 0.16, 0.15), 25)],
    limbs=[LEGS, ARMS],
    voxel=0.0095, max_tris=12000,
    mouth=(-1.0, -0.90, 0.796, 0.802, 0.004),
    teeth=(6, 0.008, 0.0035, -0.99, -0.91),
    eyes=(-0.885, 0.832, 0.012, (0.70, 0.50, 0.20)),
    nostrils=(-0.975, 0.815),
    back=(0.34, 0.28, 0.20), flank=(0.62, 0.52, 0.38), belly=(0.88, 0.82, 0.68),
    pattern=("bands", (0.20, 0.16, 0.12), 14.0, 0.8, -0.45, 1.0),
    post=thumb_claws,
)

if __name__ == "__main__":
    tt.run(SPEC)
