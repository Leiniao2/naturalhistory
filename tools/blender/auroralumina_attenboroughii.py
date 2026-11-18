"""
Procedural Auroralumina attenboroughii (Ediacaran crown-group cnidarian, Charnwood Forest, ~560 Ma).

A ringed, amber organic skeleton (periderm) rises from a small holdfast, then forks into two
flaring cups; from each cup a soft polyp spreads a dense crown of glowing orange stinging
tentacles ("dawn lantern"). About 20 cm tall. Fixed style: pivot on the seabed (z = 0).

Usage:
  blender --background --python tools/blender/auroralumina_attenboroughii.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Auroralumina.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
import nh_edi_kit as kit  # noqa: E402
from mathutils import Vector  # noqa: E402

PERI = (0.70, 0.50, 0.26)
PERI_DARK = (0.46, 0.30, 0.14)
POLYP = (0.96, 0.62, 0.32)
TENT = (1.0, 0.72, 0.36)
MOUTH = (0.55, 0.22, 0.12)
HOLD = (0.52, 0.42, 0.32)


def build():
    mb = nh.MeshBuilder()
    mb.add(ec.frond_disc(0.12, 0.04), HOLD)
    stalk = kit.curve((0, 0, 0.0), (0, 0.02, 0.3), (0.0, 0.0, 0.55), 8)
    mb.add(nh.tube(stalk, [0.045, 0.05, 0.052, 0.055, 0.058, 0.06, 0.065, 0.07, 0.075], sides=12),
           kit.ringed(PERI, PERI_DARK, period=0.045))
    for s in (-1, 1):
        fork = kit.curve((0, 0, 0.53), (s * 0.12, 0, 0.66), (s * 0.24, -0.02, 0.92), 8)
        radii = [0.07 - 0.002 * i for i in range(6)] + [0.075, 0.095, 0.115]
        mb.add(nh.tube(fork, radii, sides=12), kit.ringed(PERI, PERI_DARK, period=0.04))
        top = Vector(fork[-1])
        up = (Vector(fork[-1]) - Vector(fork[-3])).normalized()
        # polyp body bulging out of the cup, oral cone in the middle
        mb.add(nh.ellipsoid(top + up * 0.02, (0.1, 0.1, 0.05), subdivisions=3,
                            rotation=Vector((0, 0, 1)).rotation_difference(up).to_matrix()), POLYP)
        mb.add(nh.ellipsoid(top + up * 0.065, (0.03, 0.03, 0.03), subdivisions=2), MOUTH)
        kit.crown(mb, top + up * 0.04, 0.085, 22, 0.24, 0.012, TENT, up=tuple(up), spread=50,
                  droop=-0.45, seed=7 + s)
        kit.crown(mb, top + up * 0.05, 0.05, 12, 0.17, 0.010, POLYP, up=tuple(up), spread=25,
                  droop=-0.2, seed=11 + s)
    return ec.ground(mb.to_object("Auroralumina", roughness=0.45))


if __name__ == "__main__":
    ec.export(build, "Auroralumina", fixed=True)
