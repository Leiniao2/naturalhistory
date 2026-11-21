"""
Shared parts for the batch-2 Cambrian species (hurdia_victoria.py, cambroraster_falcatus.py,
stanleycaris_hirpex.py, and the arthropods): a radiodont trunk with swimming flaps and a
tail fan, a radiodont frontal limb with comb spines, stalked eyes, and an arthropod
trunk of tergites with biramous leg tips. Builds on nh_model / nh_edicam / nh_edi_kit.
Faces -Y throughout.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
import nh_edi_kit as kit  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402


def radiodont_trunk(mb, y0, y1, seg, width, body, dark, belly, flap, flap_len=0.13,
                    fan=3, fan_len=0.16, fan_col=None, flat=0.6):
    """Segmented, tapering trunk along +Y with a pair of swimming flaps per segment
    and a fan of `fan` tail blades on each side."""
    mb.add(ec.segmented_trunk(y0, y1, seg, lambda t: width * (1 - 0.6 * t), flat=flat, sides=10, tip=0.02),
           ec.banded(body, dark, belly, y0, (y1 - y0) / seg, amount=0.5))
    for i in range(seg):
        t = i / max(seg - 1, 1)
        y = y0 + (i + 0.5) * (y1 - y0) / seg
        for s in (-1, 1):
            f = ec.paddle(flap_len * (1 - 0.45 * t) + 0.03, flap_len * 0.32, n=10, taper=0.55, thickness=0.01)
            nh.transform(f, Matrix.Rotation(math.radians(-18), 4, "Z"))
            ec.mirror(f, s)
            nh.transform(f, Matrix.Translation((s * width * 0.8 * (1 - 0.5 * t), y, -0.01)))
            mb.add(f, flap, smooth=False)
    for s in (-1, 1):
        for k in range(fan):
            b = ec.paddle(fan_len, fan_len * 0.16, n=8, taper=0.5, thickness=0.008)
            nh.transform(b, Matrix.Rotation(math.radians(62 + 12 * k), 4, "Z"))
            ec.mirror(b, s)
            nh.transform(b, Matrix.Translation((s * 0.015, y1 - 0.03 + 0.015 * k, 0.0)))
            mb.add(b, fan_col or flap, smooth=False)


def frontal_limb(mb, side, base, reach, drop, r, limb, spine, n=6, spine_len=0.08, comb=0,
                 hook=0.0, curl=0.12):
    """A radiodont frontal appendage: a tapering, curled limb from `base` forward (-Y) and
    down, with one long spine per podomere pointing inward/down (plus `comb` small
    auxiliary spines on each), optionally hooked forward at the tip (hook)."""
    b = Vector(base)
    pts = kit.curve(b, b + Vector((side * 0.02, -reach * 0.6, -drop * 0.2)),
                    b + Vector((-side * 0.01, -reach, -drop)), n)
    radii = [r * (1 - 0.6 * i / n) for i in range(n + 1)]
    mb.add(nh.tube(pts, radii, sides=6), limb)
    for k in range(1, n + 1):
        p = pts[k]
        L = spine_len * (1 - 0.3 * k / n)
        tip = p + Vector((-side * L * 0.6, -hook * L, -L))
        mid = p.lerp(tip, 0.5) + Vector((0, -hook * L * 0.6, 0))
        mb.add(ec.spike(p, tip, r=r * 0.42, sides=4, mid=mid), spine, smooth=False)
        for q in range(comb):
            c = p.lerp(tip, 0.3 + q * 0.6 / max(comb, 1))
            mb.add(ec.spike(c, c + Vector((0, curl * L * 0.5, -L * 0.25)), r=r * 0.1, sides=3), spine, smooth=False)


def stalked_eye(mb, base, tip, r, stalk, eye=(0.03, 0.03, 0.03)):
    base, tip = Vector(base), Vector(tip)
    mb.add(nh.tube([base, base.lerp(tip, 0.5), tip], [r * 0.45, r * 0.4, r * 0.35], sides=6), stalk)
    mb.add(nh.ellipsoid(tuple(tip), (r, r * 1.15, r * 0.9), subdivisions=2), eye)


def tergites(mb, y0, y1, n, width_fn, height, color_fn, droop=0.9, overlap=2.2):
    """n overlapping dome-topped tergites from y0 to y1 (arthropod trunk). width_fn(t)."""
    L = (y1 - y0) / n
    for i in range(n):
        t = i / max(n - 1, 1)
        y = y0 + (i + 0.5) * L
        mb.add(ec.plate(y, width_fn(t), L * 0.5 * overlap, height, edge_droop=droop), color_fn(i, t))


def legs_under(mb, y0, y1, n, width_fn, color, z=-0.03, reach=0.12, drop=0.07, r=0.012):
    for i in range(n):
        t = i / max(n - 1, 1)
        y = y0 + (y1 - y0) * t
        w = width_fn(t)
        for s in (-1, 1):
            root = Vector((s * w * 0.55, y, z))
            mb.add(ec.jointed_leg([root, root + Vector((s * reach * 0.7, 0.0, -drop * 0.3)),
                                   root + Vector((s * reach, 0.02, -drop))], r, r * 0.4, sides=4), color)


def antenna(mb, root, side, length, r, color, spread=0.5, droop=-0.02, n=5):
    root = Vector(root)
    pts = kit.curve(root, root + Vector((side * length * spread * 0.3, -length * 0.55, 0.01)),
                    root + Vector((side * length * spread, -length, droop)), n)
    radii = [r * (1 - i / n) for i in range(n + 1)]
    mb.add(nh.tube(pts, radii, sides=4), color)
