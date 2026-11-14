"""
Procedural low-poly white-tailed deer buck (Odocoileus virginianus) for map colonies.

Standing alert on slender legs with knees, hocks, dewclaws and cloven dark
hooves; a deep barrel with visible shoulder, ribcage and haunch muscles; a
graceful neck; a sculpted head (eye sockets, preorbital glands, muzzle and
nostrils) with white eye rings, muzzle band, chin and throat patch; large cupped
ears; branching antlers with a burr at the base and tapered tines; a tan /
reddish-brown coat with a white belly, and the tail raised so its white
underside flags.

The body is built from overlapping parts and fused into one seamless,
voxel-remeshed surface with a little fur displacement; eyes, glands, nostrils,
hooves, dewclaws, ears and antlers are crisp details on top.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/white_tailed_deer.py -- [--render out.png]

Output: Assets/Resources/Models/Species/WhiteTailedDeer.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy  # noqa: E402
import bmesh  # noqa: E402
import nh_model as nh  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402

COAT = (0.62, 0.40, 0.22)       # tan / reddish-brown
COAT_DARK = (0.46, 0.29, 0.15)  # darker back line
WHITE = (0.95, 0.93, 0.88)
HOOF = (0.10, 0.08, 0.07)
NOSE = (0.05, 0.04, 0.04)
GLAND = (0.22, 0.13, 0.10)
ANTLER = (0.50, 0.40, 0.28)
ANTLER_TIP = (0.76, 0.68, 0.54)
EYE = (0.03, 0.02, 0.02)
EYE_SHINE = (0.85, 0.85, 0.85)


# ---------------------------------------------------------------- shape helpers

def oriented(center, radii, pitch=0.0, yaw=0.0, roll=0.0, segments=20, rings=14, deform=None):
    """UV ellipsoid rotated about X (pitch), Y (roll) then Z (yaw), degrees, moved to center."""
    bm = nh.uv_ellipsoid((0, 0, 0), radii, segments=segments, rings=rings, deform=deform)
    rot = (Matrix.Rotation(math.radians(yaw), 4, "Z") @ Matrix.Rotation(math.radians(roll), 4, "Y")
           @ Matrix.Rotation(math.radians(pitch), 4, "X"))
    nh.transform(bm, rot)
    nh.transform(bm, Matrix.Translation(Vector(center)))
    return bm


def cup_ear(base, height, width, depth, tilt_x, splay):
    """Closed, cupped ear: a half-ellipsoid shell open toward -Y, solidified, then posed."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=12, radius=1.0)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.y < -0.15], context="VERTS")
    for v in bm.verts:
        z01 = (v.co.z + 1) * 0.5
        taper = 0.35 + 0.65 * math.sin(math.pi * min(1.0, z01 * 0.85 + 0.12)) ** 0.6  # broad, pointed leaf
        v.co = Vector((v.co.x * width * taper, v.co.y * depth, z01 * height))
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.006)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    nh.transform(bm, Matrix.Rotation(math.radians(splay), 4, "Y") @ Matrix.Rotation(math.radians(tilt_x), 4, "X"))
    nh.transform(bm, Matrix.Translation(Vector(base)))
    return bm


def fur_displace(bm, amount=0.003, freq=42.0):
    bm.normal_update()
    for v in bm.verts:
        v.co += v.normal * noise.noise(v.co * freq) * amount


def render_closeups(path, target, dist, views):
    scene = bpy.context.scene
    cam = scene.camera
    out = Path(path)
    for i, (az, el) in enumerate(views):
        a, e = math.radians(az), math.radians(el)
        cam.location = Vector(target) + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist
        cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = str(out.with_name(f"{out.stem}_head{i}.png"))
        bpy.ops.render.render(write_still=True)


# ---------------------------------------------------------------- colours

def coat(belly=-0.45):
    """Brown coat, darker along the spine, white where the surface faces down."""
    def color(co, n):
        c = nh.lerp(COAT, COAT_DARK, nh.smoothstep(0.55, 0.95, n.z))
        c = nh.lerp(c, COAT, 0.3 * max(0.0, noise.noise(co * 12.0)))
        return nh.lerp(c, WHITE, nh.smoothstep(belly + 0.12, belly - 0.12, n.z))
    return color


def leg_color(co, n):
    """Coat on the outside, paler on the inner faces of the legs, pale band above the hoof."""
    inner = nh.smoothstep(0.2, 0.8, -n.x if co.x > 0 else n.x) * nh.smoothstep(0.75, 0.55, co.z)
    c = nh.lerp(coat(-0.6)(co, n), WHITE, 0.55 * inner)
    return nh.lerp(nh.lerp(WHITE, COAT, 0.45), c, nh.smoothstep(0.06, 0.12, co.z))


# ---------------------------------------------------------------- build

FRONT_X, HIND_X = 0.09, 0.095


def front_leg(x):
    return ([(x * 0.4, -0.24, 0.90), (x * 0.85, -0.25, 0.80), (x, -0.27, 0.68), (x, -0.29, 0.52),
             (x * 0.95, -0.30, 0.36), (x * 0.95, -0.30, 0.14), (x * 0.95, -0.305, 0.075), (x * 0.95, -0.322, 0.045)],
            [0.06, 0.085, 0.07, 0.045, 0.03, 0.021, 0.02, 0.019])


def hind_leg(x):
    return ([(x * 0.4, 0.25, 0.92), (x * 0.85, 0.25, 0.82), (x, 0.25, 0.72), (x, 0.22, 0.55),
             (x * 0.95, 0.36, 0.33), (x * 0.95, 0.34, 0.14), (x * 0.95, 0.33, 0.075), (x * 0.95, 0.315, 0.045)],
            [0.07, 0.10, 0.09, 0.06, 0.03, 0.021, 0.02, 0.019])


def build():
    body = nh.MeshBuilder()

    # Barrel with ribcage, withers, shoulder blades, haunches and rump
    def body_deform(n):
        k = 1.0 + 0.14 * max(0.0, -n.y) * max(0.0, -n.z + 0.4)  # barrel chest
        k *= 1.0 + 0.08 * max(0.0, n.y) * max(0.0, n.z + 0.5)    # round rump
        k *= 1.0 - 0.06 * (1.0 - abs(n.y)) * max(0.0, -n.z)      # tucked waist
        return k
    body.add(oriented((0, 0.0, 0.81), (0.18, 0.41, 0.225), pitch=3, segments=28, rings=20, deform=body_deform), coat())
    body.add(oriented((0, -0.12, 0.80), (0.19, 0.24, 0.235)), coat())                       # ribcage
    body.add(oriented((0, -0.25, 0.97), (0.07, 0.13, 0.06), pitch=-8), coat())             # withers
    body.add(oriented((0, 0.30, 0.93), (0.13, 0.15, 0.08)), coat())                        # rump
    for sx in (-1, 1):
        body.add(oriented((sx * 0.105, -0.27, 0.85), (0.07, 0.11, 0.165), pitch=-18), coat(-0.6))   # shoulder
        body.add(oriented((sx * 0.105, 0.27, 0.84), (0.085, 0.16, 0.17), pitch=10), coat(-0.6))     # haunch
        body.add(oriented((sx * 0.10, 0.25, 0.67), (0.07, 0.10, 0.13), pitch=-15), coat(-0.6))      # thigh
        body.add(oriented((sx * 0.10, -0.29, 0.66), (0.055, 0.07, 0.10), pitch=-5), coat(-0.6))     # forearm

        pts, radii = front_leg(sx * FRONT_X)
        body.add(nh.tube(pts, radii, sides=14), leg_color)
        body.add(oriented((sx * FRONT_X * 0.95, -0.302, 0.36), (0.03, 0.033, 0.042)), leg_color)   # knee (carpus)
        pts, radii = hind_leg(sx * HIND_X)
        body.add(nh.tube(pts, radii, sides=14), leg_color)
        body.add(oriented((sx * HIND_X * 0.95, 0.372, 0.335), (0.027, 0.04, 0.045), pitch=20), leg_color)  # hock

    # Neck: thick where it meets the shoulders; white throat patch near the jaw
    def neck_color(co, n):
        c = coat(-0.7)(co, n)
        throat = nh.smoothstep(1.02, 1.08, co.z) * nh.smoothstep(0.0, -0.45, n.y + n.z * 0.3)
        return nh.lerp(c, WHITE, throat)
    body.add(nh.tube([(0, -0.18, 0.80), (0, -0.28, 0.88), (0, -0.37, 0.98), (0, -0.43, 1.10), (0, -0.46, 1.18)],
                     [0.15, 0.13, 0.092, 0.072, 0.065], sides=18), neck_color)

    # Head: skull, brow ridges over the eye sockets, cheeks, long muzzle, chin, nose pad
    def head_color(co, n):
        c = coat(-0.6)(co, n)
        return nh.lerp(c, WHITE, nh.smoothstep(-0.3, -0.7, n.z))  # white chin/jaw
    body.add(oriented((0, -0.50, 1.245), (0.072, 0.095, 0.078), pitch=-22), head_color)
    for sx in (-1, 1):
        body.add(oriented((sx * 0.047, -0.515, 1.292), (0.03, 0.042, 0.02), pitch=-15), head_color)  # brow
        body.add(oriented((sx * 0.048, -0.57, 1.215), (0.028, 0.06, 0.032), pitch=-28), head_color)  # cheek

    def muzzle_color(co, n):
        c = nh.lerp(COAT, COAT_DARK, 0.35 * nh.smoothstep(0.5, 0.95, n.z))  # slightly darker bridge
        band = nh.smoothstep(0.014, 0.0, abs(co.y + 0.675))                   # white band behind the nose
        c = nh.lerp(c, WHITE, max(band, nh.smoothstep(-0.25, -0.6, n.z)))
        return c
    snout = nh.tube([(0, -0.47, 1.27), (0, -0.55, 1.235), (0, -0.62, 1.19), (0, -0.68, 1.155), (0, -0.705, 1.14),
                     (0, -0.712, 1.137)],
                    [0.072, 0.064, 0.048, 0.037, 0.031, 0.02], sides=18, scale_xy=(1.0, 1.15))
    body.add(snout, muzzle_color)
    body.add(oriented((0, -0.64, 1.128), (0.03, 0.05, 0.02), pitch=-25), WHITE)               # chin

    # Tail: raised and flared; white underside ("flag"), brown on top; white rump patch
    def tail_color(co, n):
        top = nh.smoothstep(0.55, 0.85, n.z - n.y * 0.6) * nh.smoothstep(0.06, 0.02, abs(co.x))
        return nh.lerp(WHITE, COAT_DARK, top)
    body.add(nh.tube([(0, 0.36, 0.87), (0, 0.44, 0.93), (0, 0.50, 1.0), (0, 0.53, 1.05), (0, 0.545, 1.075)],
                     [0.045, 0.064, 0.06, 0.038, 0.012], sides=14, scale_xy=(1.0, 0.5)), tail_color)
    body.add(oriented((0, 0.39, 0.84), (0.075, 0.035, 0.08)), WHITE)

    fused = body.fuse(voxel=0.0068, smooth=4, smooth_factor=0.5, max_tris=15500)
    fur_displace(fused)
    mb = nh.MeshBuilder()
    mb.add(fused)

    # ---- crisp details
    mb.add(oriented((0, -0.706, 1.146), (0.03, 0.016, 0.026), pitch=-20), NOSE)             # moist nose pad
    for sx in (-1, 1):
        # eyes in white rings under the brow, preorbital gland in front, nostrils
        mb.add(nh.ellipsoid((sx * 0.06, -0.535, 1.266), (0.012, 0.028, 0.022), subdivisions=3), WHITE)
        mb.add(nh.ellipsoid((sx * 0.067, -0.538, 1.266), (0.01, 0.018, 0.016), subdivisions=2), EYE)
        mb.add(nh.ellipsoid((sx * 0.074, -0.545, 1.272), (0.003, 0.003, 0.003), subdivisions=1), EYE_SHINE)
        mb.add(oriented((sx * 0.055, -0.575, 1.252), (0.006, 0.022, 0.006), pitch=-25, segments=8, rings=6), GLAND)
        mb.add(oriented((sx * 0.0135, -0.723, 1.151), (0.0055, 0.004, 0.008), roll=sx * 25, segments=8, rings=6), (0.01, 0.01, 0.01))

        # cupped ears out to the sides, pale inside with a dark rim
        def ear_color(co, n):
            inner = nh.smoothstep(-0.4, -0.8, n.y)
            return nh.lerp(COAT_DARK, nh.lerp(COAT, WHITE, 0.75), inner)
        mb.add(cup_ear((sx * 0.055, -0.455, 1.30), 0.17, 0.055, 0.026, tilt_x=-10, splay=sx * 58), ear_color)

        # cloven hooves and dewclaws
        for leg, (lx, ly) in ((front_leg, (FRONT_X, -0.322)), (hind_leg, (HIND_X, 0.315))):
            hx = sx * lx * 0.95
            for half in (-1, 1):  # two toes with a cleft, sloping forward to a point
                hx2 = hx + half * 0.0108
                mb.add(nh.tube([(hx2, ly + 0.012, 0.052), (hx2, ly + 0.004, 0.03), (hx2, ly - 0.012, 0.008),
                                (hx2 + half * 0.002, ly - 0.03, 0.0)],
                               [0.0115, 0.0125, 0.012, 0.004], sides=10, scale_xy=(1.0, 0.8)), HOOF)
            back = 0.02 if ly < 0 else 0.02
            for half in (-1, 1):
                b = Vector((hx + half * 0.012, ly + back, 0.07))
                mb.add(nh.tube([b, b + Vector((0, 0.008, -0.012)), b + Vector((0, 0.012, -0.022))],
                               [0.006, 0.005, 0.0], sides=5), HOOF)

        # antlers: burr at the pedicle, main beam back/out/up then forward, tapered tines
        def antler_color(co, n):
            return nh.lerp(ANTLER, ANTLER_TIP, nh.smoothstep(1.40, 1.62, co.z))
        mb.add(oriented((sx * 0.037, -0.49, 1.305), (0.026, 0.026, 0.011), roll=sx * 20, segments=14, rings=8,
                        deform=lambda v: 1.0 + 0.18 * noise.noise(v * 6.0)), ANTLER)       # burr
        beam = [(sx * 0.035, -0.49, 1.30), (sx * 0.055, -0.48, 1.35), (sx * 0.09, -0.465, 1.41), (sx * 0.14, -0.45, 1.46),
                (sx * 0.175, -0.48, 1.51), (sx * 0.18, -0.53, 1.55), (sx * 0.16, -0.60, 1.575), (sx * 0.12, -0.66, 1.585),
                (sx * 0.09, -0.69, 1.585)]
        mb.add(nh.tube(beam, [0.021, 0.02, 0.019, 0.017, 0.015, 0.013, 0.011, 0.007, 0.0], sides=8), antler_color)
        for base, tip, r in (((sx * 0.06, -0.478, 1.36), (sx * 0.055, -0.525, 1.45), 0.010),
                             ((sx * 0.145, -0.452, 1.465), (sx * 0.15, -0.455, 1.63), 0.012),
                             ((sx * 0.178, -0.52, 1.545), (sx * 0.19, -0.535, 1.69), 0.011),
                             ((sx * 0.155, -0.61, 1.575), (sx * 0.155, -0.63, 1.68), 0.0085)):
            b, t = Vector(base), Vector(tip)
            mid = b.lerp(t, 0.5) + Vector((sx * 0.006, 0, 0))
            mb.add(nh.tube([b, b.lerp(t, 0.2), mid, t.lerp(b, 0.15), t], [r, r * 0.9, r * 0.7, r * 0.35, 0.0], sides=8),
                   antler_color)

    obj = mb.to_object("WhiteTailedDeer")
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "WhiteTailedDeer", ground=(0.38, 0.48, 0.26), views=((35, 25), (-90, 8), (20, 65), (200, 20)))
    if "--render" in sys.argv:
        render_closeups(sys.argv[sys.argv.index("--render") + 1], (0, -0.58, 1.30), 0.7, ((30, 10), (-80, 5)))
