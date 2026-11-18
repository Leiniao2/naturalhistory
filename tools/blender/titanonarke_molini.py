"""
Procedural Titanonarke molini (Monte Bolca, Italy, early Eocene, ~50 Ma) for map colonies:
an early electric ray (Torpediniformes), about half a metre long.

A round, soft, flabby disc made of the head and the fused pectoral fins, holding
two big kidney-shaped electric organs that could stun prey with a shock; a short,
thick tail with two small dorsal fins and a broad, paddle-like caudal fin, small
pelvic fins behind the disc and small eyes with spiracles on top. Shown mottled
brown with dark spots above, cream below (like living torpedo rays).
Faces -Y, pivot at the body centre (swimmer).

Usage:
  blender --background --python tools/blender/titanonarke_molini.py -- [--render out.png]

Output: Assets/Resources/Models/Species/TitanonarkeMolini.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

TOP = (0.46, 0.34, 0.22)
SPOT = (0.20, 0.13, 0.08)
ORGAN = (0.56, 0.44, 0.30)
BELLY = (0.88, 0.84, 0.74)
EYE = (0.05, 0.05, 0.04)
RIM = (0.65, 0.55, 0.30)


def build():
    b = nh.MeshBuilder()
    # the disc: nearly circular, thick in the middle, thin at the edge
    b.add(nh.ellipsoid((0, -0.15, 0), (0.48, 0.44, 0.09), subdivisions=5,
                       deform=lambda v: 1.0 - 0.06 * max(0.0, -v.y) ** 4), TOP)
    b.add(nh.ellipsoid((0, -0.12, 0.02), (0.30, 0.32, 0.08)), TOP)                 # raised centre
    # pelvic fins: rounded lobes tucked behind the disc
    for sx in (-1, 1):
        b.add(nh.ellipsoid((sx * 0.20, 0.30, -0.01), (0.15, 0.13, 0.035)), TOP)
    # thick, short tail
    b.add(nh.tube([(0, 0.15, 0.0), (0, 0.45, 0.0), (0, 0.72, 0.0), (0, 0.86, 0.0)], [0.10, 0.075, 0.05, 0.035],
                  sides=12, scale_xy=(1.1, 0.8)), TOP)
    fused = b.fuse(voxel=0.012, smooth=4, smooth_factor=0.5, max_tris=8000)
    fused.normal_update()

    def paint(co, n):
        c = TOP
        # the two kidney-shaped electric organs show as smooth paler patches either side of the head
        for sx in (-1, 1):
            d = ((co.x - sx * 0.22) / 0.13) ** 2 + ((co.y + 0.2) / 0.22) ** 2
            c = nh.lerp(c, ORGAN, 0.6 * (1 - nh.smoothstep(0.6, 1.0, d)))
        v = noise.noise(co * 11.0)
        c = nh.lerp(c, SPOT, 0.85 * nh.smoothstep(0.30, 0.42, v))
        c = nh.lerp(c, SPOT, 0.2 * max(0.0, noise.noise(co * 30.0)))
        c = nh.lerp(c, BELLY, nh.smoothstep(0.0, -0.4, n.z))
        return c

    mb = nh.MeshBuilder()
    mb.add(fused, color=paint)
    # two small dorsal fins and the paddle-shaped caudal fin (vertical panels)
    def vfin(outline, color):
        """outline: (y, z) points of a median fin."""
        panel = nh.flat_panel([(z, y, 0.0) for (y, z) in outline], thickness=0.018)
        # flat_panel is built in XY: rotate it so the panel stands upright in the YZ plane
        nh.transform(panel, nh.Matrix.Rotation(-1.5708, 4, "Y"))
        mb.add(panel, color, smooth=False)
    vfin([(0.40, 0.05), (0.47, 0.13), (0.53, 0.12), (0.55, 0.05)], TOP)
    vfin([(0.58, 0.04), (0.64, 0.11), (0.69, 0.10), (0.70, 0.03)], TOP)
    vfin([(0.80, 0.0), (0.84, 0.13), (0.95, 0.15), (1.02, 0.0), (0.95, -0.14), (0.84, -0.12)], SPOT)
    # eyes and spiracles on top of the head
    for sx in (-1, 1):
        mb.add(nh.ellipsoid((sx * 0.07, -0.36, 0.085), (0.022, 0.026, 0.018), subdivisions=2), EYE)
        mb.add(nh.ellipsoid((sx * 0.07, -0.30, 0.083), (0.018, 0.022, 0.008), subdivisions=2), RIM)
    obj = mb.to_object("TitanonarkeMolini")
    vs = obj.data.vertices
    lo = Vector((min(v.co.x for v in vs), min(v.co.y for v in vs), min(v.co.z for v in vs)))
    hi = Vector((max(v.co.x for v in vs), max(v.co.y for v in vs), max(v.co.z for v in vs)))
    c = (lo + hi) / 2
    for v in vs:
        v.co -= c
    return obj


if __name__ == "__main__":
    nh.run(build, "TitanonarkeMolini", background=(0.05, 0.22, 0.32), views=((35, 35), (-90, 5), (0, 80)))
