"""
Small helpers for the batch-2 Jurassic species built on nh_car_tetrapod
(kayentatherium_wellesi.py, rugosodon_eurasiaticus.py, protosuchus_richardsoni.py ...):
extra() callables that add mammal ears, gnawing incisors, whiskers and rows of back
scutes to an nh_car_tetrapod.Spec. Each returns a function (spec, spine) -> [(bm, colour)].
"""

import math

from mathutils import Vector

import nh_model as nh


def ears(r, color, at=0.95, up=0.85, out=0.75, inner=None):
    """A pair of small rounded ears near the back of the head."""
    def fn(sp, spine):
        s = sp.head_len * at
        p = spine.at(s)
        res = []
        for sx in (-1, 1):
            c = p + Vector((sx * spine.rx(s) * out, 0, spine.rz(s) * up))
            res.append((nh.ellipsoid(c, (r * 0.45, r * 0.7, r), subdivisions=2), color))
            if inner:
                res.append((nh.ellipsoid(c + Vector((0, -r * 0.2, 0)), (r * 0.25, r * 0.45, r * 0.7), subdivisions=1), inner))
        return res
    return fn


def incisors(length, r, color=(0.85, 0.62, 0.30), lower=True):
    """Paired, forward-leaning gnawing incisors at the snout tip."""
    def fn(sp, spine):
        p = spine.at(0.0)
        s = sp.head_len * 0.05
        z = p.z - spine.rz(s) * 0.35
        res = []
        for sx in (-1, 1):
            b = Vector((p.x + sx * r * 1.1, p.y + length * 0.3, z))
            res.append((nh.tube([b, b + Vector((0, -length * 0.25, -length))], [r, r * 0.6], sides=5), color))
            if lower:
                b2 = b + Vector((0, length * 0.2, -length * 1.05))
                res.append((nh.tube([b2, b2 + Vector((0, -length * 0.45, length * 0.55))], [r * 0.9, r * 0.5], sides=5), color))
        return res
    return fn


def whiskers(length, color=(0.12, 0.10, 0.08), n=4):
    def fn(sp, spine):
        s = sp.head_len * 0.15
        p = spine.at(s)
        res = []
        for sx in (-1, 1):
            for k in range(n):
                b = p + Vector((sx * spine.rx(s) * 0.8, 0, spine.rz(s) * (0.1 - 0.15 * k)))
                d = Vector((sx * 1.0, 0.25 + 0.15 * k, 0.05 - 0.12 * k)).normalized()
                res.append((nh.tube([b, b + d * length], [0.0018, 0.0006], sides=3), color))
        return res
    return fn


def scutes(color, s0, s1, step, size, rows=(-0.35, 0.35), keel=0.8):
    """Paired rows of low keeled bony scutes down the back (s along the spine)."""
    def fn(sp, spine):
        res = []
        s = s0
        while s < s1:
            p = spine.at(s)
            rx, rz = spine.rx(s), spine.rz(s)
            k = min(1.0, rx / max(sp.trunk_r, 1e-6)) ** 0.5
            for xr in rows:
                c = p + Vector((xr * rx, 0, rz * 0.95))
                res.append((nh.ellipsoid(c, (size * 0.8 * k, size * k, size * 0.45 * k * keel), subdivisions=1), color))
            s += step
        return res
    return fn
