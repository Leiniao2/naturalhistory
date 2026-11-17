"""
Procedural Estemmenosuchus mirabilis (Middle Permian dinocephalian) for map colonies.

The second species of the "crowned crocodile", from the same Ocher locality (Perm region,
Russia) as E. uralensis. Same heavy barrel body, short tail and huge deep skull, but a
smaller animal with differently built horns: instead of one pair of great palmate blades it
carries TWO bony projections on each side of the head - a shorter, round-sectioned horn on
the skull roof that rises almost straight up like a young antler (the pair set well apart,
each with a small knobbed tine), and a second horn on the cheek (jugal) that sticks straight
out sideways.
Built on estemmenosuchus_uralensis.py: its body, limbs, skin sculpting, teeth and details
are reused unchanged; only the horns, their paint mask and the colouring are replaced. The
model is scaled to SIZE of E. uralensis (the game sizes animals by sizeCm anyway). Painted
warmer than E. uralensis - sandy grey-brown, darker and blotched over the back - with the
horns flushed brick-red and pale at the tips.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/estemmenosuchus_mirabilis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/EstemmenosuchusMirabilis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import estemmenosuchus_uralensis as base  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

NAME = "EstemmenosuchusMirabilis"
SIZE = 0.85

base.NAME = NAME
base.HIDE = (0.56, 0.45, 0.32)        # sandy tan-brown
base.HIDE_DARK = (0.34, 0.26, 0.18)
base.BELLY = (0.76, 0.69, 0.57)
base.MOTTLE = (0.23, 0.18, 0.14)
base.HORN = (0.62, 0.34, 0.24)        # brick-red flush
base.HORN_TIP = (0.84, 0.70, 0.54)
base.EYE = (0.66, 0.42, 0.12)

oriented = base.oriented


def antler(sx):
    """Skull-roof horn: rises nearly straight up from far out on the roof, shorter than in
    E. uralensis, with a small forward tine and a knobbed tip."""
    p = [Vector((sx * 0.118, -0.700, 0.905)), Vector((sx * 0.140, -0.698, 0.985)),
         Vector((sx * 0.158, -0.700, 1.050)), Vector((sx * 0.168, -0.708, 1.100))]
    parts = [nh.tube(p, [0.050, 0.039, 0.031, 0.026], sides=14, scale_xy=(0.85, 1.0)),
             oriented(p[-1] + Vector((0, 0, 0.006)), (0.032, 0.030, 0.028))]          # knobbed tip
    t0 = p[1].lerp(p[2], 0.4)
    tine = [t0, t0 + Vector((sx * 0.030, -0.040, 0.036)), t0 + Vector((sx * 0.050, -0.060, 0.062))]
    parts.append(nh.tube(tine, [0.022, 0.018, 0.014], sides=10))
    parts.append(oriented(tine[-1], (0.019, 0.019, 0.018)))
    return parts


def cheek_flange(sx):
    """Cheek (jugal) horn: a stout, slightly flattened horn sticking straight out sideways."""
    p = [Vector((sx * 0.110, -0.760, 0.740)), Vector((sx * 0.195, -0.758, 0.738)),
         Vector((sx * 0.265, -0.752, 0.742)), Vector((sx * 0.318, -0.745, 0.750))]
    return [oriented((sx * 0.13, -0.76, 0.735), (0.060, 0.062, 0.052)),
            nh.tube(p, [0.052, 0.040, 0.030, 0.022], sides=14, scale_xy=(1.0, 0.8)),
            oriented(p[-1] + Vector((sx * 0.004, 0, 0)), (0.026, 0.026, 0.022))]


def ornament(co):
    co = base.local(co)
    ax = abs(co.x)
    t_ant = 0.0
    if -0.80 < co.y < -0.60 and co.z > 0.94 and ax > 0.06:
        t_ant = nh.smoothstep(0.97, 1.11, co.z)
    t_chk = 0.0
    if -0.82 < co.y < -0.68 and 0.66 < co.z < 0.82 and ax > 0.16:
        t_chk = nh.smoothstep(0.19, 0.33, ax)
    return max(t_ant, t_chk)


base.antler = antler
base.cheek_flange = cheek_flange
base.ornament = ornament


def build():
    obj = base.build()
    obj.data.transform(Matrix.Scale(SIZE, 4))
    return obj


def render_head(path):
    scene = bpy.context.scene
    cam = scene.camera
    head_c = Vector((0.0, -0.84, 0.88)) * SIZE
    out = Path(path)
    for i, off in enumerate((Vector((0.75, -0.75, 0.20)), Vector((0.0, -1.1, 0.08)))):
        cam.location = head_c + off * SIZE
        cam.rotation_euler = (head_c - cam.location).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = str(out.with_name(f"{out.stem}_head{i}.png"))
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    nh.run(build, NAME, ground=(0.40, 0.38, 0.27), views=((35, 22), (-90, 6), (25, 65)))
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--render" in argv:
        render_head(argv[argv.index("--render") + 1])
