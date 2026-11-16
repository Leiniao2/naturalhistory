"""
Procedural high-detail Liopleurodon ferox (Middle-Late Jurassic pliosaurid plesiosaur)
for the map (Swim style).

Follows conservative size estimates (about 6-7 m, not the exaggerated 25 m of
older popular accounts): a huge, long, low head about a fifth of the body
length, wide at the back and tapering to a narrow snout with a slight spoon-
shaped expansion at the tip; a short, thick neck; a compact, teardrop-shaped
torpedo body; four large, swept-back hydrofoil flippers (the hind pair slightly
larger) held out mid-stroke; and a short tapering tail. The jaws hang slightly
open over big, recurved conical teeth, the longest fangs clustered at the front
of the snout. Upward-facing eyes set well back on the skull.

The body (head, neck, trunk, tail and all four flippers) and the lower jaw are
lofted sections and flattened tubes, each fused into one seamless surface
(nh_model.MeshBuilder.fuse), given a fine skin-texture displacement and
repainted procedurally (counter-shading with an irregular boundary and faint
mottling, darker flipper edges, pink gums). Teeth, eyes and nostrils are crisp
separate shells.

Usage:
  blender --background --python tools/blender/liopleurodon_ferox.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Liopleurodon.fbx
Pivot at the body centre, faces -Y, back up (+Z). About 2.2 units long, flipper span ~1.5.
"""

import math
import sys
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector, Matrix, noise

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402

VOXEL = 0.0115
JAW_VOXEL = 0.009
JAW_OPEN = math.radians(9)
HINGE = Vector((0.0, -0.585, -0.070))

BACK = (0.17, 0.20, 0.23)        # dark slate-grey back
BACK_DARK = (0.09, 0.11, 0.13)
FLANK = (0.34, 0.37, 0.38)
BELLY = (0.80, 0.78, 0.70)
SPOT = (0.11, 0.13, 0.15)
GUM = (0.62, 0.30, 0.30)
MOUTH = (0.32, 0.12, 0.12)
TOOTH = (0.93, 0.90, 0.80)
TOOTH_BASE = (0.75, 0.68, 0.55)
EYE = (0.03, 0.03, 0.03)
EYE_RING = (0.55, 0.48, 0.32)

# body sections: (y, half width, height above centre, depth below centre, centre z)
SECTIONS = [
    (-1.080, 0.016, 0.014, 0.008, -0.040),
    (-1.055, 0.045, 0.034, 0.014, -0.040),
    (-1.000, 0.062, 0.046, 0.018, -0.040),   # spoon-shaped tip of the snout
    (-0.940, 0.058, 0.052, 0.020, -0.037),
    (-0.860, 0.074, 0.066, 0.022, -0.032),
    (-0.760, 0.110, 0.090, 0.026, -0.025),
    (-0.660, 0.168, 0.125, 0.034, -0.015),
    (-0.580, 0.214, 0.158, 0.060, -0.005),   # broad back of the skull (jaw muscles)
    (-0.500, 0.202, 0.162, 0.150, 0.000),    # short, thick neck
    (-0.400, 0.225, 0.180, 0.180, 0.000),
    (-0.280, 0.265, 0.205, 0.205, 0.000),
    (-0.120, 0.295, 0.218, 0.215, 0.000),
    (0.060, 0.300, 0.220, 0.215, 0.000),
    (0.250, 0.272, 0.200, 0.195, 0.000),
    (0.430, 0.205, 0.160, 0.150, 0.004),
    (0.600, 0.130, 0.112, 0.102, 0.008),
    (0.780, 0.072, 0.072, 0.065, 0.010),
    (0.940, 0.034, 0.040, 0.036, 0.010),
    (1.060, 0.010, 0.014, 0.012, 0.010),
]
Y_TIP, Y_TAIL = SECTIONS[0][0], SECTIONS[-1][0]

# lower jaw sections (closed): (y, half width, top z, bottom z)
JAW = [
    (-1.070, 0.024, -0.054, -0.064),
    (-1.010, 0.056, -0.058, -0.084),
    (-0.940, 0.052, -0.057, -0.090),
    (-0.860, 0.068, -0.054, -0.098),
    (-0.760, 0.100, -0.051, -0.110),
    (-0.660, 0.156, -0.049, -0.124),
    (-0.580, 0.198, -0.065, -0.140),
    (-0.540, 0.180, -0.075, -0.135),
]

FORE = ([(0.22, -0.26, -0.06), (0.36, -0.235, -0.075), (0.50, -0.175, -0.090), (0.62, -0.095, -0.098),
         (0.71, -0.015, -0.098), (0.765, 0.045, -0.095)],
        [0.095, 0.108, 0.096, 0.072, 0.042, 0.0])
HIND = ([(0.20, 0.30, -0.05), (0.34, 0.335, -0.058), (0.48, 0.395, -0.064), (0.60, 0.475, -0.066),
         (0.69, 0.555, -0.064), (0.745, 0.615, -0.060)],
        [0.095, 0.112, 0.100, 0.076, 0.044, 0.0])


def section(y):
    for a, b in zip(SECTIONS, SECTIONS[1:]):
        if y <= b[0]:
            t = nh.smoothstep(a[0], b[0], y) * 0.5 + (y - a[0]) / (b[0] - a[0]) * 0.5
            return tuple(a[i] + (b[i] - a[i]) * t for i in range(1, 5))
    return SECTIONS[-1][1:]


def jaw_section(y):
    for a, b in zip(JAW, JAW[1:]):
        if y <= b[0]:
            t = (y - a[0]) / (b[0] - a[0])
            return tuple(a[i] + (b[i] - a[i]) * t for i in range(1, 4))
    return JAW[-1][1:]


def loft(y0, y1, n_y, n_a, point):
    """Closed loft along y with n_a points per ring; point(y, angle) -> Vector."""
    bm = bmesh.new()
    rings = []
    for i in range(n_y + 1):
        t = i / n_y
        y = y0 + (y1 - y0) * (0.5 - 0.5 * math.cos(math.pi * t))   # denser at the ends
        rings.append([bm.verts.new(point(y, k / n_a * math.tau)) for k in range(n_a)])
    for a, b in zip(rings, rings[1:]):
        for k in range(n_a):
            j = (k + 1) % n_a
            bm.faces.new([a[k], a[j], b[j], b[k]])
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def body_point(y, a):
    w, ht, hb, zc = section(y)
    c, s = math.cos(a), math.sin(a)
    # slightly squared-off cross-section (broad back, flat-ish belly)
    cx = math.copysign(abs(c) ** 0.85, c)
    sz = math.copysign(abs(s) ** 0.9, s)
    return Vector((w * cx, y, zc + (ht if s > 0 else hb) * sz))


def jaw_point(y, a):
    w, top, bot = jaw_section(y)
    c, s = math.cos(a), math.sin(a)
    mid, half = (top + bot) * 0.5, (top - bot) * 0.5
    cx = math.copysign(abs(c) ** 0.8, c)
    return Vector((w * cx, y, mid + half * s))


def jaw_matrix():
    return (Matrix.Translation(HINGE) @ Matrix.Rotation(JAW_OPEN, 4, "X") @ Matrix.Translation(-HINGE))


def flipper(pts, widths, flat=0.20):
    return nh.tube(pts, widths, sides=14, scale_xy=(1.0, flat))


def skin_detail(bm, amount=0.0035):
    bm.normal_update()
    for v in bm.verts:
        v.co += v.normal * (noise.noise(v.co * 55.0) * amount + noise.noise(v.co * 9.0) * amount * 0.8)
    bm.normal_update()


# ---------------------------------------------------------------- colour

def body_color(co, n):
    x, y, z = co
    ax = abs(x)
    big = noise.noise(co * 6.0)
    fine = noise.noise(co * 40.0)
    if ax > 0.26 and abs(n.z) > 0.2 and -0.3 < y < 0.7 and z < -0.03:
        # flippers: dark above, pale below, darker trailing/tip edge
        if n.z > 0:
            c = nh.lerp(BACK, BACK_DARK, nh.smoothstep(0.5, 0.75, ax) * 0.6 + max(0.0, big) * 0.3)
        else:
            c = nh.lerp(BELLY, FLANK, nh.smoothstep(0.45, 0.75, ax) * 0.7)
        return c
    w, ht, hb, zc = section(y)
    # counter-shading: the boundary sits a little below the flank midline and wanders
    rel = (z - zc) / max(hb, 0.01)
    edge = -0.25 + 0.18 * noise.noise(Vector((y * 4.0, x * 2.0, 3.1)))
    belly = 1 - nh.smoothstep(edge - 0.25, edge + 0.15, rel)
    c = nh.lerp(BACK, FLANK, nh.smoothstep(0.7, -0.1, n.z) * 0.6)
    c = nh.lerp(c, BACK_DARK, nh.smoothstep(0.75, 1.0, n.z) * 0.5)
    # faint dark mottling on the back and flanks
    c = nh.lerp(c, SPOT, nh.smoothstep(0.25, 0.5, big + fine * 0.3) * 0.55 * (1 - belly))
    c = nh.lerp(c, BELLY, belly)
    if y < -0.6 and n.z < -0.3 and z > zc - hb - 0.01 and rel > -1.2:
        # underside of the upper jaw (palate and gum line)
        c = nh.lerp(c, GUM, nh.smoothstep(-0.3, -0.7, n.z))
    return nh.lerp(c, BACK_DARK, max(0.0, fine) * 0.15)


def jaw_color(co, n):
    # the jaw is already rotated open here, so compare the normal with its rotated "up"
    up = (jaw_matrix().to_3x3() @ Vector((0, 0, 1))).normalized()
    d = n.dot(up)
    if d > 0.55:
        return nh.lerp(GUM, MOUTH, nh.smoothstep(0.08, 0.0, abs(co.x)) * 0.6)   # tongue groove
    c = nh.lerp(BELLY, FLANK, nh.smoothstep(-0.3, 0.4, d) * 0.6)
    return nh.lerp(c, SPOT, max(0.0, noise.noise(co * 30.0)) * 0.15)


# ---------------------------------------------------------------- teeth

def tooth(base, down, outward, back, length, radius):
    """Recurved conical tooth: down along `down`, curving back (+y) and slightly inward."""
    pts, radii = [], []
    n = 5
    for k in range(n + 1):
        t = k / n
        p = base + down * (length * t) + back * (length * 0.22 * t * t) - outward * (length * 0.10 * t * t)
        pts.append(p)
        radii.append(radius * (1 - t) ** 0.9 if k < n else 0.0)
    return nh.tube(pts, radii, sides=7)


def tooth_color(base):
    return lambda co, n: nh.lerp(TOOTH_BASE, TOOTH, nh.smoothstep(0.0, 0.025, (co - base).length))


def add_teeth(mb):
    m = jaw_matrix()
    # upper jaw: along the outer margin of the palate
    n_up = 17
    for k in range(n_up):
        t = k / (n_up - 1)
        y = -1.045 + 0.42 * t ** 1.1
        w, ht, hb, zc = section(y)
        front = 1 - nh.smoothstep(0.0, 0.35, t)
        L = 0.030 + 0.045 * front + 0.012 * math.sin(k * 2.1) ** 2
        r = L * 0.20
        for sx in (-1, 1):
            base = Vector((sx * w * 0.78, y, zc - hb * 0.55))
            down = Vector((sx * (0.25 * (1 - front) + 0.15 * front), -0.40 * front, -1.0)).normalized()   # front fangs splay forward
            mb.add(tooth(base, down, Vector((sx, 0, 0)), Vector((0, 1, 0)), L, r), tooth_color(base), smooth=True)
    # lower jaw
    n_lo = 15
    for k in range(n_lo):
        t = k / (n_lo - 1)
        y = -1.035 + 0.40 * t ** 1.1
        w, top, bot = jaw_section(y)
        front = 1 - nh.smoothstep(0.0, 0.35, t)
        L = 0.028 + 0.038 * front + 0.010 * math.cos(k * 1.7) ** 2
        r = L * 0.20
        for sx in (-1, 1):
            base = m @ Vector((sx * w * 0.70, y, top - 0.004))
            up = (m.to_3x3() @ Vector((sx * (0.15 * (1 - front) + 0.15 * front), -0.25 * front, 1.0))).normalized()
            mb.add(tooth(base, up, Vector((sx, 0, 0)), Vector((0, 1, 0)), L, r), tooth_color(base), smooth=True)


# ---------------------------------------------------------------- build

def build_body():
    parts = nh.MeshBuilder()
    grey = (0.5, 0.5, 0.5)  # repainted after fusing
    parts.add(loft(Y_TIP, Y_TAIL, 120, 40, body_point), grey)
    for sx in (-1, 1):
        for pts, widths in (FORE, HIND):
            parts.add(flipper([(sx * x, y, z) for x, y, z in pts], widths, flat=0.19), grey)
    fused = parts.fuse(voxel=VOXEL, smooth=6, smooth_factor=0.5, max_tris=15000)
    skin_detail(fused)
    return fused


def build_jaw():
    parts = nh.MeshBuilder()
    parts.add(loft(JAW[0][0], JAW[-1][0], 40, 28, jaw_point), (0.5, 0.5, 0.5))
    fused = parts.fuse(voxel=JAW_VOXEL, smooth=4, smooth_factor=0.5, max_tris=2600)
    skin_detail(fused, amount=0.002)
    nh.transform(fused, jaw_matrix())
    fused.normal_update()
    return fused


def build():
    mb = nh.MeshBuilder()
    mb.add(build_body(), body_color)
    mb.add(build_jaw(), jaw_color)
    add_teeth(mb)
    # eyes set high on the skull, looking up and outward
    for sx in (-1, 1):
        y = -0.665
        w, ht, hb, zc = section(y)
        c = Vector((sx * w * 0.62, y, zc + ht * 0.72))
        mb.add(nh.ellipsoid(c, (0.029, 0.036, 0.026), subdivisions=2), EYE_RING)
        mb.add(nh.ellipsoid(c + Vector((sx * 0.007, -0.002, 0.008)), (0.020, 0.025, 0.019), subdivisions=2), EYE)
        # small external nostrils ahead of the eyes
        y = -0.79
        w, ht, hb, zc = section(y)
        mb.add(nh.ellipsoid((sx * w * 0.45, y, zc + ht * 0.88), (0.007, 0.013, 0.005), subdivisions=1), BACK_DARK)
    return mb.to_object("Liopleurodon", roughness=0.62)


def closeup(path, cam_loc, target, lens=55):
    scene = bpy.context.scene
    cam = scene.camera
    cam.data.lens = lens
    cam.location = Vector(cam_loc)
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    bpy.ops.wm.read_factory_settings(use_empty=True)
    obj = build()
    nh.export_fbx(obj, "Liopleurodon")
    if "--render" in argv:
        out = Path(argv[argv.index("--render") + 1])
        nh.render_preview(obj, out, views=((35, 25), (90, 4), (20, 70), (200, -30)), background=(0.05, 0.18, 0.24))
        closeup(out.with_name(f"{out.stem}_head.png"), (0.95, -1.75, 0.20), (0.0, -0.80, -0.05), lens=50)


if __name__ == "__main__":
    main()
