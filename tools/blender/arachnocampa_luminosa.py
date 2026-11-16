"""
Procedural New Zealand glowworm (Arachnocampa luminosa) colony under a small rock
arch, a cave mouth in a damp forest gully, for the map (Fixed style).

A weathered, mossy natural arch (a thick lintel on two heavy buttress feet, with
a few arching fern fronds on its crown) over a pad of damp leaf litter: the
sheltered, still, humid kind of ceiling the glowworms need. Along the ceiling
lie several larvae (the luminous larvae of a fungus gnat): slender, segmented,
translucent grey grubs with a small dark head, each resting in a pale silk and
mucus hammock slung from the rock by short threads. The last segment of each
larva glows blue-green; it is coloured above 1.0 (like the firefly's lantern and
the game's lava) so it stays bright under the map's shading: Unity sees
GLOW = (0.20, 1.50, 1.30) there. Below every hammock hangs a curtain of long
vertical silk "fishing lines" beaded with sticky droplets (pale and faintly
blue-green, as if catching the light) that snare insects drawn to the glow.
Larvae sit on both shoulders of the ceiling so the curtain reads through the
arch from the front and the back. Threads are thickened well beyond life so
they read at map scale.
Faces -Y (the arch opens front to back), pivot on the ground.

Usage:
  blender --background --python tools/blender/arachnocampa_luminosa.py -- [--render out.png]

Output: Assets/Resources/Models/Species/NZGlowworm.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmesh  # noqa: E402
import nh_model as nh  # noqa: E402
from mathutils import Matrix, Vector, noise  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

ROCK = (0.27, 0.25, 0.22)
ROCK_WET = (0.17, 0.16, 0.15)
ROCK_DARK = (0.07, 0.075, 0.08)   # shaded alcove under the overhang
MOSS = (0.20, 0.36, 0.13)
MOSS_DARK = (0.12, 0.24, 0.09)
LITTER = (0.22, 0.18, 0.12)       # damp leaf litter on the ground
FERN = (0.22, 0.46, 0.14)
FERN_STEM = (0.25, 0.20, 0.12)
LARVA = (0.56, 0.58, 0.57)        # translucent grey
LARVA_GUT = (0.36, 0.38, 0.37)
HEAD = (0.16, 0.11, 0.07)
HAMMOCK = (0.80, 0.82, 0.83)
SILK = (0.84, 0.88, 0.90)
GLOW_BASE = (0.2, 1.0, 0.9)       # painted colour, replaced by GLOW after export prep
GLOW = (0.20, 1.50, 1.30)         # > 1: stays bright under shading (target value in the FBX)
DROP = (0.74, 0.97, 1.0)          # sticky droplets, glinting with the blue-green light

LARVAE = 9
LINES_PER = (4, 7)


# ---------------------------------------------------------------- rock

ARCH_SPAN = 0.70   # half-span of the arch's centre line at the ground
ARCH_TOP = 0.92    # height of the centre line at the crown


def arch_point(u):
    """Centre line of the arch, u in [0, 1] from the left foot to the right foot."""
    a = math.pi * (1.0 - u)
    return Vector((ARCH_SPAN * math.cos(a), 0.0, ARCH_TOP * math.sin(a) ** 0.85))


def rock():
    """Natural rock arch (a tiny cave mouth): a thick lintel on two buttress feet, lumpy boulders
    fused on, then weathered with noise. The glowworms hang from its ceiling."""
    mb = nh.MeshBuilder()
    n = 24
    pts, rs = [], []
    for i in range(n + 1):
        u = i / n
        pts.append(arch_point(u) - Vector((0, 0, 0.1 if i in (0, n) else 0.0)))
        rs.append(0.19 + 0.17 * abs(2 * u - 1) ** 2.2)          # slim crown, heavy feet
    mb.add(nh.tube(pts, rs, sides=20, scale_xy=(1.0, 1.0)), ROCK)
    for sx in (-1, 1):
        mb.add(nh.uv_ellipsoid((sx * 0.74, 0.04, 0.16), (0.3, 0.3, 0.24), 18, 12), ROCK)       # foot boulders
        mb.add(nh.uv_ellipsoid((sx * 0.62, 0.06, 0.5), (0.2, 0.24, 0.26), 16, 10), ROCK)
    mb.add(nh.uv_ellipsoid((-0.12, 0.03, ARCH_TOP + 0.1), (0.36, 0.2, 0.12), 18, 10), ROCK)     # crown hump
    mb.add(nh.uv_ellipsoid((0.25, -0.02, ARCH_TOP + 0.04), (0.22, 0.18, 0.1), 16, 10), ROCK)
    bm = mb.fuse(voxel=0.028, smooth=4, smooth_factor=0.5, max_tris=4200)
    # cut flat at the ground and weather the surface
    for v in bm.verts:
        v.co.z = max(v.co.z, 0.0)
    bm.normal_update()
    for v in bm.verts:
        if v.co.z < 0.01:
            continue
        d = (0.05 * noise.noise(v.co * 2.2) + 0.03 * noise.noise(v.co * 5.0 + Vector((2, 5, 1)))
             + 0.01 * noise.noise(v.co * 12.0 + Vector((4, 1, 2))))
        v.co += v.normal * d * min(1.0, v.co.z / 0.08)
    bm.normal_update()
    return bm


def rock_color(co, n):
    c = nh.lerp(ROCK, ROCK_WET, nh.smoothstep(-0.2, 0.5, noise.noise(Vector((co.x * 6, co.y * 6, co.z * 1.5)))))
    c = nh.lerp(c, ROCK_DARK, nh.smoothstep(0.0, -0.5, n.z) * nh.smoothstep(0.1, 0.4, co.z))   # dim alcove
    moss = nh.smoothstep(0.25, 0.65, n.z + 0.25 * noise.noise(co * 7.0))
    moss = max(moss, nh.smoothstep(0.12, 0.0, co.z) * 0.8)                # mossy foot
    c = nh.lerp(c, nh.lerp(MOSS, MOSS_DARK, max(0.0, noise.noise(co * 14.0))), moss)
    return c


def ground_patch(rng):
    """Low irregular pad of damp leaf litter and moss under the curtain."""
    pts = []
    for i in range(20):
        a = i / 20 * math.tau
        r = 1.0 + 0.12 * math.sin(3 * a + 1.0) + rng.uniform(-0.05, 0.05)
        pts.append((math.cos(a) * 1.05 * r, math.sin(a) * 0.55 * r, 0.012))
    bm = nh.flat_panel(pts, thickness=0.024)

    def color(co, n):
        return nh.lerp(LITTER, MOSS_DARK, nh.smoothstep(-0.2, 0.4, noise.noise(co * 5.0)))
    return bm, color


def fern(base, direction, length, rng):
    """Arching frond: rachis plus paired leaflets, drooping over the crest."""
    d = Vector(direction).normalized()
    pts = []
    for k in range(7):
        t = k / 6
        pts.append(base + d * length * t + Vector((0, 0, 0.45 * length * math.sin(t * math.pi * 0.8) - 0.45 * length * t * t)))
    shells = [(nh.tube(pts, [0.008, 0.007, 0.006, 0.005, 0.004, 0.003, 0.0], sides=4), FERN_STEM)]
    side = d.cross(Vector((0, 0, 1))).normalized()
    for k in range(1, 12):
        t = k / 12
        p = pts[k // 2].lerp(pts[k // 2 + 1], (k % 2) * 0.5)
        L = length * 0.26 * (1.0 - 0.7 * t)
        for s in (-1, 1):
            tip = p + side * s * L + d * L * 0.4 + Vector((0, 0, -L * 0.3))
            shells.append((nh.tube([p, p.lerp(tip, 0.5) + Vector((0, 0, 0.01)), tip], [0.004, 0.017, 0.0],
                                   sides=4, scale_xy=(1.0, 0.25)), FERN))
    return shells


# ---------------------------------------------------------------- glowworms

def frame_on(n, rng):
    """Tangent (along the larva), bitangent and normal on the face; larvae lie roughly level."""
    t = n.cross(Vector((0, 0, 1)))
    if t.length < 1e-3:
        t = Vector((1, 0, 0))
    t.normalize()
    rot = Matrix.Rotation(rng.uniform(-0.5, 0.5), 3, n)
    t = rot @ t
    return t, n.cross(t).normalized()


def larva(p, n, rng):
    """Larva in its hammock at surface point p (normal n). Returns (shells, glow shell, hang points)."""
    t, b = frame_on(n, rng)
    L = rng.uniform(0.13, 0.16)
    c = p + n * 0.032
    shells = []
    # hammock: a pale, flattened silk sling between the larva and the rock, with suspensory threads
    sling = nh.uv_ellipsoid((0, 0, 0), (L * 0.72, 0.03, 0.007), 12, 6)
    m = Matrix((t, b, n)).transposed().to_4x4()
    nh.transform(sling, m)
    nh.transform(sling, Matrix.Translation(p + n * 0.016))
    shells.append((sling, HAMMOCK))
    for s in (-1, 1):
        for q in (-1, 1):
            a = p + n * 0.016 + t * s * L * 0.6 + b * q * 0.02
            shells.append((nh.tube([a, p + t * s * L * 0.66 + b * q * 0.026 - n * 0.004], [0.003, 0.003], sides=3), SILK))
    # body: slender, segmented, a slight S-curve; head end dark, tail end lit
    steps = 14
    pts, rs = [], []
    for i in range(steps + 1):
        u = i / steps
        pts.append(c + t * (u - 0.5) * L + b * 0.012 * math.sin(u * math.pi * 2.0) + n * 0.004 * math.sin(u * math.pi))
        seg = 1.0 - 0.1 * nh.smoothstep(0.7, 1.0, (u * 10) % 1.0)
        rs.append(0.0135 * math.sin(math.pi * (0.12 + 0.82 * u)) ** 0.35 * seg)
    rs[0] = 0.0
    cut = int(steps * 0.7)
    gut_axis = (pts[0], pts[-1])

    def body_col(co, nn):
        return nh.lerp(LARVA, LARVA_GUT, nh.smoothstep(0.4, 0.9, -nn.dot(n)) * 0.6)
    shells.append((nh.tube(pts[:cut + 2], rs[:cut + 2], sides=10), body_col))
    head_c = pts[0] + (pts[0] - pts[1]).normalized() * 0.004
    shells.append((nh.uv_ellipsoid(head_c, (0.009, 0.009, 0.009), 8, 6), HEAD))
    # lantern: the swollen last segments, a touch fatter than the body
    glow_pts = pts[cut:] + [pts[-1] + (pts[-1] - pts[-2]).normalized() * k for k in (0.012, 0.02)]
    glow_rs = [0.015 + 0.008 * nh.smoothstep(0, 2, i) for i in range(len(pts) - cut)] + [0.017, 0.0]
    glow = nh.tube(glow_pts, glow_rs, sides=10)
    # the lines hang from points along the underside of the hammock
    hang = [c + t * rng.uniform(-0.6, 0.6) * L + b * rng.uniform(-0.02, 0.02) - Vector((0, 0, 0.012))
            for _ in range(rng.randint(*LINES_PER))]
    return shells, glow, hang


def fishing_line(top, length, rng):
    """Vertical silk thread with sticky droplets strung along it, a bigger drop at the end."""
    bot = top - Vector((0, 0, length))
    line = nh.tube([top, top.lerp(bot, 0.5) + Vector((rng.uniform(-0.004, 0.004), rng.uniform(-0.004, 0.004), 0)), bot],
                   [0.0065, 0.006, 0.0055], sides=4)
    drops = []
    z = 0.03 + rng.uniform(0.0, 0.02)
    while z < length - 0.02:
        r = rng.uniform(0.0085, 0.0115)
        drops.append(nh.ellipsoid(top - Vector((0, 0, z)), (r, r, r * 1.25), subdivisions=1))
        z += rng.uniform(0.05, 0.075)
    drops.append(nh.ellipsoid(bot - Vector((0, 0, 0.008)), (0.014, 0.014, 0.018), subdivisions=1))
    return line, drops


def ceiling_sites(tree, rng):
    """Spots on the arch's ceiling for the larvae: cast up and slightly in from the front and the back
    (so they sit on the lower shoulders of the lintel and show from either side), keep downward-facing
    hits."""
    sites = []
    tries = 0
    while len(sites) < LARVAE and tries < 600:
        tries += 1
        x = rng.uniform(-0.36, 0.36)
        side = -1 if len(sites) % 2 == 0 else 1
        org = Vector((x, side * rng.uniform(0.15, 0.32), 0.1))
        d = Vector((0, -side * 0.22, 1.0)).normalized()
        hit, n, _i, _d = tree.ray_cast(org, d)
        if hit is None or n.z > -0.35 or hit.z < 0.45:
            continue
        if any((hit - q).length < 0.15 for q, _ in sites):
            continue
        sites.append((hit, n))
    return sites


# ---------------------------------------------------------------- glow

def srgb_to_linear(c):
    return ((c + 0.055) / 1.055) ** 2.4 if c > 0.04045 else c / 12.92


def light(obj, ranges):
    """Swaps the byte "Col" layer for a float one so glowing parts can go above 1.0 (see
    photinus_carolinus.py). ranges: [(lo, hi, rgb)] vertex index ranges and their stored colour."""
    me = obj.data
    old = me.color_attributes["Col"]
    vals = [tuple(d.color) for d in old.data]
    me.color_attributes.remove(old)
    new = me.color_attributes.new("Col", "FLOAT_COLOR", "CORNER")
    lit = [(lo, hi, tuple(srgb_to_linear(c) for c in rgb) + (1.0,)) for lo, hi, rgb in ranges]
    for loop, v in zip(me.loops, vals):
        vi = loop.vertex_index
        col = v
        for lo, hi, c in lit:
            if lo <= vi < hi:
                col = c
                break
        new.data[loop.index].color = col
    me.color_attributes.active_color = new
    me.color_attributes.render_color_index = me.color_attributes.active_color_index


def build():
    rng = random.Random(7)
    mb = nh.MeshBuilder()
    rock_bm = rock()
    tree = BVHTree.FromBMesh(rock_bm)
    sites = ceiling_sites(tree, rng)
    mb.add(rock_bm, color=rock_color)
    mb.add(*ground_patch(rng))
    for k in range(5):
        x = -0.62 + 0.31 * k + rng.uniform(-0.06, 0.06)
        hit, _n, _i, _d = tree.ray_cast(Vector((x, rng.uniform(-0.1, 0.1), 3.0)), Vector((0, 0, -1)))
        if hit is None:
            continue
        d = (rng.uniform(-0.5, 0.5), -1.0 if k % 2 == 0 else 1.0, 0.0)
        for s, col in fern(hit - Vector((0, 0, 0.01)), d, rng.uniform(0.4, 0.5), rng):
            mb.add(s, col)

    glows, drops = [], []
    for p, n in sites:
        shells, glow, hang = larva(p, n, rng)
        for s, col in shells:
            mb.add(s, col)
        glows.append(glow)
        for top in hang:
            # hang free of the rock and well above the ground
            down, _, _, dist = tree.ray_cast(top - Vector((0, 0, 0.005)), Vector((0, 0, -1)))
            room = (dist - 0.04) if down is not None else top.z - 0.08
            length = min(rng.uniform(0.22, 0.58), room, top.z - 0.1)
            if length < 0.08:
                continue
            line, ds = fishing_line(top, length, rng)
            mb.add(line, SILK)
            drops += ds

    ranges = []
    lo = len(mb.bm.verts)
    for d in drops:
        mb.add(d, DROP, smooth=False)
    ranges.append((lo, len(mb.bm.verts), DROP))
    lo = len(mb.bm.verts)
    for g in glows:
        mb.add(g, GLOW_BASE)
    ranges.append((lo, len(mb.bm.verts), GLOW))

    obj = mb.to_object("NZGlowworm", roughness=0.55)
    light(obj, ranges)
    nh.ground_to_zero(obj)
    print(f"{len(sites)} larvae, {len(drops)} droplets")
    return obj


if __name__ == "__main__":
    nh.run(build, "NZGlowworm", background=(0.02, 0.04, 0.05), ground=(0.10, 0.12, 0.09),
           views=((20, 20), (0, 55), (-60, 35), (180, 45)))
