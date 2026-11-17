"""
Procedural Pentamerus oblongus (early Silurian pentamerid brachiopod, Llandovery, shells
up to about 10 cm long, forming dense shell banks in Britain, the Baltic and North
America) for map colonies (Fixed style).

A cluster of large, smooth, elongate-oval, strongly biconvex shells living as they are
found in Silurian shell banks: upright, the big incurved beak of the deeper ventral valve
sunk in the mud and the anterior commissure facing up. Each shell shows fine growth
bands, a dark commissure line where the two valves meet and a faint median ridge (the
trace of the internal spondylium septum). Pale grey-buff shells on grey lime mud. Uses
the seabed patch of nh_brachiopod.py. Faces -Y, pivot at the base of the mud patch.

Usage:
  blender --background --python tools/blender/pentamerus_oblongus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PentamerusOblongus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Matrix, Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_brachiopod as br  # noqa: E402

NAME = "PentamerusOblongus"
MUD = ((0.36, 0.36, 0.33), (0.52, 0.51, 0.46))
SHELL = (0.78, 0.72, 0.60)
SHELL_DARK = (0.56, 0.50, 0.40)
LINE = (0.20, 0.17, 0.13)

# (x, y, scale, yaw deg, lean deg)
SHELLS = ((0.0, 0.0, 1.0, 20, 8), (-0.40, 0.26, 0.85, 140, -12), (0.42, 0.20, 0.9, -60, 14),
          (0.14, -0.44, 0.7, 80, -16), (-0.36, -0.30, 0.65, 200, 12))


def shell(L=1.0, W=0.25, Dv=0.21, Dd=0.13):
    """Local frame: long axis +Z (beak at the bottom), ventral valve toward -Y."""
    def deform(n):
        # taper to the beak end (z < 0) and blunt the anterior end
        k = 1.0 - 0.35 * max(0.0, -n.z) ** 1.5
        return k
    bm = nh.uv_ellipsoid((0, 0, 0), (W, 1.0, L * 0.5), 18, 14, deform=deform)
    for v in bm.verts:
        v.co.y *= Dv if v.co.y < 0 else Dd
    nh.transform(bm, Matrix.Translation(Vector((0, 0, L * 0.5))))

    def col(co, n):
        t = co.z / L
        c = nh.lerp(SHELL_DARK, SHELL, 0.5 + 0.5 * t)
        c = nh.lerp(c, LINE, 0.45 * nh.smoothstep(0.85, 0.98, math.cos(t * 30.0)))   # growth bands
        c = nh.lerp(c, SHELL_DARK, 0.2 * (0.5 + 0.5 * noise.noise(co * 8.0)))
        if abs(co.y) < 0.02:
            c = LINE                                                                       # commissure
        if abs(co.x) < 0.012 and co.y < -0.05:
            c = nh.lerp(c, SHELL_DARK, 0.6)                                                # median ridge
        return c
    parts = [(bm, col)]
    # incurved ventral beak
    beak = nh.tube([(0, -0.05, 0.12), (0, -0.14, 0.02), (0, -0.10, -0.08), (0, -0.02, -0.10)],
                   [0.09, 0.07, 0.04, 0.0], sides=10)
    parts.append((beak, SHELL_DARK))
    return parts


def build():
    mb = nh.MeshBuilder()
    height = br.seabed(mb, 0.85, MUD, seed=5, base=0.03, relief=0.012, n_r=12, n_a=48, oval=0.85)
    for x, y, k, yaw, lean in SHELLS:
        m = (Matrix.Translation(Vector((x, y, height(x, y) - 0.12 * k))) @ Matrix.Rotation(math.radians(yaw), 4, "Z")
             @ Matrix.Rotation(math.radians(lean), 4, "X") @ Matrix.Scale(k, 4))
        for bm, col in shell():
            nh.transform(bm, m)
            mb.add(bm, col)
    return br.finish(mb, NAME, roughness=0.6)


if __name__ == "__main__":
    nh.run(build, NAME, ground=MUD[0], background=(0.05, 0.14, 0.18), views=br.VIEWS)
