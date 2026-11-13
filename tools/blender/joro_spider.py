"""
Procedural low-poly Joro spider (Trichonephila clavata) on its golden orb web.

A near-vertical orb web (radial threads + a polygonal capture spiral, pale gold)
slung between two twig stems rising from the ground, with the spider resting
head-down at the hub: long yellow abdomen banded blue-black with a red patch
by the spinnerets, a small dark cephalothorax, and eight long yellow/black
banded legs spread on the web. The whole web leans back slightly so it reads
from a high strategy-map camera. Faces -Y, pivot on the ground (Ground style).

Usage:
  blender --background --python tools/blender/joro_spider.py -- [--render out.png]

Output: Assets/Resources/Models/Species/JoroSpider.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

SILK = (0.98, 0.84, 0.42)       # golden silk
TWIG = (0.36, 0.26, 0.15)
TWIG_TIP = (0.42, 0.50, 0.22)
LEAF = (0.32, 0.55, 0.20)
YELLOW = (0.98, 0.80, 0.12)
BLUE_BLACK = (0.06, 0.08, 0.16)
RED = (0.85, 0.12, 0.08)
CARAPACE = (0.14, 0.14, 0.16)

HUB = Vector((0.0, 0.0, 0.95))  # web centre (x across, z up; web lies in the XZ plane)
WEB_R = 0.62
RADIALS = 22
TILT = math.radians(14)         # web leans back (+Y) so the camera sees its face
THREAD = 0.0075


def web(rng):
    """Radials + polygonal capture spiral in the XZ plane around HUB."""
    shells = []
    angles = [i / RADIALS * math.tau + rng.uniform(-0.05, 0.05) for i in range(RADIALS)]
    # slightly egg-shaped: orb webs are larger below the hub
    def rim(a):
        return WEB_R * (1.0 + 0.12 * -math.sin(a)) * rng.uniform(0.97, 1.03)
    rims = [rim(a) for a in angles]
    for a, r in zip(angles, rims):
        p0 = HUB + Vector((math.cos(a), 0, math.sin(a))) * 0.04
        p1 = HUB + Vector((math.cos(a), 0, math.sin(a))) * r
        shells.append(nh.tube([p0, p1], [THREAD, THREAD], sides=3))
    # capture spiral: straight hops between neighbouring radials, outward
    pts, radii = [], []
    turns = 9
    steps = turns * RADIALS
    for k in range(steps + 1):
        i = k % RADIALS
        frac = 0.16 + 0.80 * k / steps
        pts.append(HUB + Vector((math.cos(angles[i]), -0.002, math.sin(angles[i]))) * rims[i] * frac)
        radii.append(THREAD * 0.8)
    shells.append(nh.tube(pts, radii, sides=3))
    # frame: polygon joining the radial tips
    frame = [HUB + Vector((math.cos(a), 0, math.sin(a))) * r for a, r in zip(angles, rims)]
    shells.append(nh.tube(frame + [frame[0]], [THREAD * 1.3] * (len(frame) + 1), sides=3))
    return shells, frame


def stem(x, height, lean, rng):
    pts = [Vector((x, 0.02, 0.0))]
    for k in range(1, 6):
        t = k / 5
        pts.append(Vector((x + lean * t * t, 0.02 + 0.05 * math.sin(t * 2.5), height * t)))
    tube = nh.tube(pts, [0.035, 0.03, 0.025, 0.02, 0.015, 0.009], sides=6)
    color = lambda co, n: nh.lerp(TWIG, TWIG_TIP, nh.smoothstep(0.2, 1.4, co.z))
    leaves = []
    for k in range(3):
        t = rng.uniform(0.25, 0.85)
        base = pts[0].lerp(pts[-1], t)
        side = rng.choice((-1, 1))
        tip = base + Vector((side * rng.uniform(0.16, 0.24), rng.uniform(-0.06, 0.06), rng.uniform(0.05, 0.14)))
        mid = base.lerp(tip, 0.5) + Vector((0, 0, 0.03))
        leaves.append(nh.tube([base, mid, tip], [0.004, 0.03, 0.0], sides=4, scale_xy=(1.0, 0.25)))
    return pts, tube, color, leaves


def anchor_threads(frame, stem_pts):
    """Bridge lines from the web's frame to the nearest points on a stem."""
    shells = []
    for p in frame:
        q = min(stem_pts, key=lambda s: (s - p).length)
        if (q - p).length < 0.55:
            shells.append(nh.tube([p, q], [THREAD * 1.2, THREAD * 1.2], sides=3))
    return shells


def banded(p0, p1, light, dark, bands, light_frac=0.35):
    """Colour fn: alternating bands along p0->p1."""
    a, b = Vector(p0), Vector(p1)
    d = b - a
    L2 = max(d.length_squared, 1e-9)

    def color(co, n):
        t = max(0.0, min(1.0, (co - a).dot(d) / L2))
        f = (t * bands) % 1.0
        return light if f > 1.0 - light_frac else dark
    return color


def spider(k=1.7):
    """Spider at the hub, head down, on the viewer's (-Y) face of the web.
    k scales the spider up from life-like proportions so it reads at map scale."""
    shells = []
    ceph_c = HUB + Vector((0, -0.045, -0.05)) * k
    abd_c = HUB + Vector((0, -0.06, 0.17)) * k
    abd_len = 0.2 * k

    # abdomen: long cylinder-ish, bands across its length; red patch at the rear tip underside
    abd = nh.uv_ellipsoid(abd_c, (0.064 * k, 0.056 * k, abd_len), segments=14, rings=16)

    def abd_color(co, n):
        v = (co.z - abd_c.z) / abd_len      # -1 (front, near cephalothorax) .. 1 (rear tip)
        if v > 0.8 and n.y > -0.2:
            return RED                       # spinneret patch, facing the web
        f = ((v + 1.0) * 3.0) % 1.0
        c = YELLOW if f < 0.62 else BLUE_BLACK
        if abs(co.x - abd_c.x) < 0.014 * k and n.y < -0.3 and f < 0.62:
            c = nh.lerp(c, BLUE_BLACK, 0.55)  # dark midline stripe on the back
        return c
    shells.append((abd, abd_color))

    ceph = nh.uv_ellipsoid(ceph_c, (0.046 * k, 0.036 * k, 0.056 * k), segments=12, rings=8)
    shells.append((ceph, CARAPACE))

    # legs: (angle from "down" in the web plane, length) for one side.
    # Head is down, so legs I and II reach down/out, III is short, IV reaches up.
    legs = [(-0.2, 0.62), (-0.6, 0.52), (-1.4, 0.26), (-2.55, 0.5)]
    for sx in (-1, 1):
        for ang, length in legs:
            a = math.pi * 1.5 - sx * ang
            dirv = Vector((math.cos(a), 0, math.sin(a)))
            base = ceph_c + Vector((sx * 0.02 * k, 0, 0))
            L = length * k
            knee = base + dirv * L * 0.36 + Vector((sx * 0.04 * k, -0.06 * k, 0.02 * k))
            ankle = base + dirv * L * 0.78 + Vector((0, -0.025 * k, 0))
            tip = base + dirv * L + Vector((0, 0.035 * k, 0))
            segs = [(base, knee, 0.012, 0.011, 2), (knee, ankle, 0.011, 0.008, 3), (ankle, tip, 0.008, 0.0, 2)]
            for p0, p1, r0, r1, bands in segs:
                shells.append((nh.tube([p0, p1], [r0 * k, r1 * k], sides=4),
                               banded(p0, p1, YELLOW, BLUE_BLACK, bands, light_frac=0.45)))
    return shells


def build():
    rng = random.Random(11)
    mb = nh.MeshBuilder()

    web_shells, frame = web(rng)
    for s in web_shells:
        mb.add(s, SILK)
    for s, c in spider():
        mb.add(s, c)

    # tilt web + spider back around the ground line, then add the stems (tilted too)
    left_pts, left, lc, left_leaves = stem(-0.88, 1.75, 0.12, rng)
    right_pts, right, rc, right_leaves = stem(0.86, 1.6, -0.1, rng)
    for s in anchor_threads(frame, left_pts) + anchor_threads(frame, right_pts):
        mb.add(s, SILK)
    # top bridge line between the stems
    mb.add(nh.tube([left_pts[-2], right_pts[-2]], [THREAD * 1.3, THREAD * 1.3], sides=3), SILK)
    mb.add(left, lc)
    mb.add(right, rc)
    for leaf in left_leaves + right_leaves:
        mb.add(leaf, LEAF)
    # a little grass tuft at each stem base so it sits on the ground
    for x in (-0.88, 0.86):
        for k in range(5):
            a = k / 5 * math.tau + rng.uniform(0, 0.6)
            base = Vector((x + math.cos(a) * 0.03, 0.02 + math.sin(a) * 0.03, 0))
            tip = base + Vector((math.cos(a) * 0.1, math.sin(a) * 0.1, rng.uniform(0.14, 0.22)))
            mb.add(nh.tube([base, tip], [0.018, 0.0], sides=3, scale_xy=(1.0, 0.4)), LEAF)

    bmesh.ops.rotate(mb.bm, verts=mb.bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(-TILT, 3, "X"))

    obj = mb.to_object("JoroSpider", roughness=0.45)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "JoroSpider", ground=(0.30, 0.42, 0.22), views=((20, 20), (35, 60), (-90, 10)))
