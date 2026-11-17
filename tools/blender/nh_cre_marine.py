"""
Swimmers for the Cretaceous batch: marine reptiles, fish and a diving bird.

Helpers on top of nh_cre_tetrapod: flippers as flattened limb lofts, vertical/horizontal
fins and tail lobes as ribbons from outlines, and a ready preview. Everything swims facing
-Y with the pivot at the body centre.
"""

import math

from mathutils import Vector

import nh_model as nh
import nh_cre_core as cc
import nh_cre_tetrapod as tp


def flipper(points, radii, flat=0.22):
    """Right-side flipper (mirrored by the builder) from shoulder to tip."""
    return tp.Limb(list(points), list(radii), toes=0, flat=(1.0, flat))


def fin(mb, outline_base, outline_tip, color, thickness=0.012, side=None):
    """Fin between a base polyline (on the body) and a tip polyline (its outer edge).
    side: None = vertical (median) fin, else horizontal hint."""
    hint = Vector((1, 0, 0)) if side is None else Vector((0, 0, 1))
    mb.add(cc.membrane(cc.polyline(outline_base, 10), cc.polyline(outline_tip, 10), nv=4,
                       thickness=thickness, normal_hint=hint), color)


def tail_lobes(mb, base_y, base_z, top, bottom, color, thickness=0.014, chord=0.08):
    """Forked/crescent tail: two lobes from the peduncle at (0, base_y, base_z) to tip points
    top and bottom (y, z)."""
    for ty, tz in (top, bottom):
        lead = [(0, base_y - chord * 0.3, base_z), (0, (base_y + ty) * 0.5 - 0.01, (base_z + tz) * 0.5), (0, ty, tz)]
        trail = [(0, base_y + chord * 0.5, base_z), (0, (base_y + ty) * 0.5 + chord * 0.3, (base_z + tz) * 0.45), (0, ty + 0.005, tz)]
        mb.add(cc.membrane(cc.polyline(lead, 10), cc.polyline(trail, 10), nv=4, thickness=thickness,
                           normal_hint=Vector((1, 0, 0))), color)


def fish_paint(back, flank, belly, extra=None, mottle=0.06):
    def paint(co, n):
        c = cc.countershade(n, belly, flank, back, lo=-0.6, mid=-0.15, hi=0.6)
        if extra:
            c = extra(co, n, c)
        return cc.mottle(c, co, mottle)
    return paint


def run(make, name, preview=None):
    nh.run(lambda: tp.build(make()), name, **(preview or tp.SWIM_VIEWS))
