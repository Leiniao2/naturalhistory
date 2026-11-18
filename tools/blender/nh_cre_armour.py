"""
Armour helpers for DinoSpec bodies (nh_cre_dino) in the second Cretaceous batch: find points
on the trunk/tail surface from the spec's own midline rows and stud them with osteoderms,
keeled scutes or spikes (ankylosaurs, nodosaurs, armoured titanosaurs, crocodyliforms).

Frame as everywhere: Z up, faces -Y, +X is the animal's left.
"""

import math

from mathutils import Vector

import nh_model as nh
import nh_cre_core as cc
import nh_cre_dino as dn


def body_at(s, y):
    """(z, half width, half height) of the midline loft at y (linear between rows)."""
    rows = sorted(dn._axis_rows(s), key=lambda r: r[0])
    if y <= rows[0][0]:
        return rows[0][1], rows[0][2], rows[0][3]
    for a, b in zip(rows, rows[1:]):
        if a[0] <= y <= b[0]:
            t = (y - a[0]) / max(1e-6, b[0] - a[0])
            return tuple(a[i] + (b[i] - a[i]) * t for i in (1, 2, 3))
    return rows[-1][1], rows[-1][2], rows[-1][3]


def surface(s, y, ang, inset=0.0):
    """Point and outward normal on the body at y; ang in degrees from the top (0) towards +x
    (90 = the left flank, negative = right). The loft is a superellipse (power ~2.1), so an
    ellipse is close enough."""
    z, hw, hh = body_at(s, y)
    a = math.radians(ang)
    p = Vector((math.sin(a) * hw, y, z + math.cos(a) * hh))
    n = Vector((math.sin(a) / max(hw, 1e-4), 0, math.cos(a) / max(hh, 1e-4))).normalized()
    return p - n * inset, n


def scutes(mb, s, ys, angles, size, color, height=0.6, keel=True, sides=6, inset=0.25):
    """Low keeled osteoderms (squashed cones) at every (y, angle) combination."""
    for y in ys:
        for ang in angles:
            p, n = surface(s, y, ang, inset=size * inset)
            if keel:
                mb.add(cc.cone(p, p + n * size * (height + 0.4), size * 0.7, sides=sides), color)
            mb.add(nh.ellipsoid(tuple(p), (size, size * 1.2, size * 0.55),
                                rotation=n.to_track_quat("Z", "Y").to_matrix(), subdivisions=1), color)


def spikes(mb, s, ys, ang, length, r, color, back=0.35, up=0.0):
    """A row of spikes along the flank at angle ang, swept back by `back`, mirrored."""
    for y in ys:
        for sx in (1, -1):
            p, n = surface(s, y, ang * sx, inset=r * 0.5)
            d = (n + Vector((0, back, up))).normalized()
            mb.add(cc.cone(p, p + d * length, r, sides=6), color)
