"""
Procedural Gigantoscorpio willsi (Early Carboniferous of Glencartholm, Scotland, a large
scorpion about 30 cm long that may have lived partly in water) for map colonies (Ground style).

Uses the giant-scorpion body of pulmonoscorpius_kirktonensis.py (carapace with eye tubercle,
seven tergites, five-segment tail curled over the back ending in a swollen venom bulb and
curved sting, big chelate pedipalps, eight splayed legs) repainted in Gigantoscorpio's own
colours: a warm amber-brown body with paler segment rims, rust-red pincers and a dark
red-black sting. Faces -Y, pivot on the ground (feet at z = 0).

Usage:
  blender --background --python tools/blender/gigantoscorpio_willsi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Gigantoscorpio.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import pulmonoscorpius_kirktonensis as pk  # noqa: E402

pk.BODY = (0.34, 0.20, 0.09)
pk.RIM = (0.62, 0.42, 0.20)
pk.CLAW = (0.46, 0.16, 0.06)
pk.FINGER = (0.14, 0.06, 0.03)
pk.LEG = (0.44, 0.30, 0.15)
pk.LEG_TIP = (0.62, 0.46, 0.24)
pk.STING = (0.20, 0.05, 0.03)

if __name__ == "__main__":
    nh.run(pk.build, "Gigantoscorpio", ground=(0.30, 0.26, 0.18), views=((35, 30), (0, 75), (-90, 10)))
