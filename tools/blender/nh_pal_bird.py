"""
Parametric birds for the Paleogene species in tools/blender/:

  * Spec / build(): a standing or walking bird (gastornis_giganteus.py,
    presbyornis_pervetus.py): body egg, S-neck, head, two-part beak, folded wings,
    tail, two legs with three forward toes (one leg forward mid-stride).
    Faces -Y, pivot on the ground (Ground, mapLegs 1).
  * Penguin / build_penguin(): a swimming penguin (kumimanu_biceae.py), body
    horizontal, flippers spread, feet trailing. Pivot at the body centre (Swim).
"""

import math
from dataclasses import dataclass

from mathutils import Vector, noise

import nh_model as nh

EYE = (0.04, 0.03, 0.02)
EYE_RING = (0.85, 0.70, 0.25)


@dataclass
class Spec:
    name: str
    body: tuple = (0.22, 0.38, 0.26)   # body half-sizes x, y, z
    body_z: float = 0.9                # body centre height
    body_pitch: float = -10.0          # + = breast up
    neck_len: float = 0.45
    neck_r: float = 0.08
    neck_lean: float = 15.0            # degrees forward from vertical
    head_r: float = 0.1
    beak_len: float = 0.2
    beak_h: float = 0.08               # beak depth at the base
    beak_w: float = 0.06
    beak_hook: float = 0.0
    beak_flat: float = 1.0             # ducks: wide, flat bill (>1)
    leg_len: float = 0.6               # hip to ground
    leg_r: float = 0.05
    thigh_r: float = 0.09
    toe_len: float = 0.12
    web: bool = False
    wing: float = 0.2                  # folded wing length (0 = vestigial)
    tail: float = 0.12
    plumage: tuple = (0.3, 0.25, 0.2)
    back: tuple = None
    pale: tuple = (0.7, 0.65, 0.55)
    head_col: tuple = None
    wing_col: tuple = None
    beak_col: tuple = (0.75, 0.68, 0.5)
    leg_col: tuple = (0.45, 0.40, 0.32)
    eye_r: float = 0.02
    shaggy: float = 0.5
    voxel: float = 0.014
    max_tris: int = 12000
    ground: tuple = (0.32, 0.40, 0.24)


def _rot_x(v, deg):
    a = math.radians(deg)
    return Vector((v.x, v.y * math.cos(a) - v.z * math.sin(a), v.y * math.sin(a) + v.z * math.cos(a)))


def build(s):
    b = nh.MeshBuilder()
    bx, by, bz = s.body
    bc = Vector((0, 0, s.body_z))
    body = nh.ellipsoid((0, 0, 0), s.body, subdivisions=4)
    nh.transform(body, nh.Matrix.Rotation(math.radians(s.body_pitch), 4, "X"))
    nh.transform(body, nh.Matrix.Translation(bc))
    b.add(body, s.plumage)
    # neck rises from the front of the body in a gentle S
    n0 = bc + _rot_x(Vector((0, -by * 0.75, bz * 0.35)), s.body_pitch)
    lean = math.radians(s.neck_lean)
    n2 = n0 + Vector((0, -math.sin(lean), math.cos(lean))) * s.neck_len
    n1 = n0.lerp(n2, 0.5) + Vector((0, 0.06 * s.neck_len, 0))
    b.add(nh.tube([tuple(n0), tuple(n1), tuple(n2)], [s.neck_r * 1.4, s.neck_r, s.neck_r * 0.9], sides=14),
          s.head_col or s.plumage)
    hc = n2 + Vector((0, -s.head_r * 0.3, s.head_r * 0.3))
    b.add(nh.ellipsoid(tuple(hc), (s.head_r * 0.85, s.head_r * 1.1, s.head_r)), s.head_col or s.plumage)
    # beak: deep upper mandible + lower mandible
    bb = hc + Vector((0, -s.head_r * 0.75, -s.head_r * 0.1))
    tip = bb + Vector((0, -s.beak_len, -s.beak_hook * s.beak_len * 0.5))
    b.add(nh.tube([tuple(bb), tuple(bb.lerp(tip, 0.5) + Vector((0, 0, s.beak_h * 0.1))), tuple(tip)],
                  [s.beak_h * 0.55, s.beak_h * 0.45, max(s.voxel * 1.2, s.beak_h * 0.12)], sides=12,
                  scale_xy=(s.beak_w / s.beak_h * s.beak_flat, 1.0)), s.beak_col)
    if s.beak_hook > 0:
        b.add(nh.ellipsoid(tuple(tip + Vector((0, s.beak_len * 0.06, -s.beak_h * 0.25))),
                           (s.beak_w * 0.35, s.beak_len * 0.1, s.beak_h * 0.3)), s.beak_col)
    # folded wings along the flanks
    if s.wing > 0:
        for sx in (-1, 1):
            w0 = bc + _rot_x(Vector((sx * bx * 0.85, -by * 0.35, bz * 0.3)), s.body_pitch)
            w1 = w0 + Vector((sx * 0.01, s.wing, -s.wing * 0.25))
            b.add(nh.tube([tuple(w0), tuple(w0.lerp(w1, 0.5)), tuple(w1)], [bx * 0.3, bx * 0.25, s.voxel * 1.3],
                          sides=10, scale_xy=(0.35, 1.0)), s.wing_col or s.back or s.plumage)
    if s.tail > 0:
        t0 = bc + _rot_x(Vector((0, by * 0.85, bz * 0.2)), s.body_pitch)
        t1 = t0 + Vector((0, s.tail, s.tail * 0.2))
        b.add(nh.tube([tuple(t0), tuple(t1)], [bz * 0.35, s.voxel * 1.3], sides=10, scale_xy=(1.6, 0.6)),
              s.back or s.plumage)
    # legs: thighs in the body, tarsi to the ground, three toes forward (+ a small hind toe)
    for sx, stride in ((-1, -0.1), (1, 0.08)):
        hip = bc + Vector((sx * bx * 0.55, by * 0.05, -bz * 0.4))
        knee = hip + Vector((sx * 0.01, -0.02, -s.leg_len * 0.35))
        foot = Vector((sx * bx * 0.5, stride * s.leg_len, 0.0))
        ankle = foot + Vector((0, 0.03, s.leg_len * 0.2))
        b.add(nh.ellipsoid(tuple(hip + Vector((0, 0, -s.leg_len * 0.1))), (s.thigh_r, s.thigh_r * 1.5, s.thigh_r * 1.6)),
              s.plumage)
        b.add(nh.tube([tuple(hip), tuple(knee)], [s.thigh_r, s.leg_r * 1.2], sides=10), s.plumage)
        b.add(nh.tube([tuple(knee), tuple(ankle), tuple(foot + Vector((0, 0, s.leg_r)))],
                      [s.leg_r * 1.1, s.leg_r, s.leg_r * 0.9], sides=10), s.leg_col)
        for a in (-0.45, 0.0, 0.45):
            d = Vector((math.sin(a) * sx, -math.cos(a), 0))
            b.add(nh.tube([tuple(foot + Vector((0, 0, s.leg_r * 0.6))),
                           tuple(foot + d * s.toe_len + Vector((0, 0, s.leg_r * 0.35)))],
                          [s.leg_r * 0.6, s.leg_r * 0.35], sides=8), s.leg_col)
        if s.web:
            z = Vector((0, 0, s.leg_r * 0.35))
            outline = [foot + z] + [foot + z + Vector((math.sin(a) * sx, -math.cos(a), 0)) * s.toe_len * 0.95
                                    for a in (-0.45, -0.22, 0.0, 0.22, 0.45)]
            b.add(nh.flat_panel([tuple(p) for p in outline], thickness=s.voxel * 1.5), s.leg_col)
        b.add(nh.tube([tuple(foot + Vector((0, 0, s.leg_r * 0.6))), tuple(foot + Vector((0, s.toe_len * 0.35, s.leg_r * 0.3)))],
                      [s.leg_r * 0.5, s.leg_r * 0.3], sides=8), s.leg_col)
    fused = b.fuse(voxel=s.voxel, smooth=4, smooth_factor=0.5, max_tris=s.max_tris)
    fused.normal_update()
    for v in fused.verts:
        if v.co.z > s.leg_len * 0.75:
            v.co += v.normal * 0.004 * s.shaggy * noise.noise(v.co * 35.0)
    mb = nh.MeshBuilder()
    mb.add(fused)
    for sx in (-1, 1):
        e = hc + Vector((sx * s.head_r * 0.72, -s.head_r * 0.35, s.head_r * 0.2))
        mb.add(nh.ellipsoid(tuple(e), (s.eye_r * 1.3,) * 3, subdivisions=2), EYE_RING)
        mb.add(nh.ellipsoid(tuple(e + Vector((sx * s.eye_r * 0.5, 0, 0))), (s.eye_r,) * 3, subdivisions=2), EYE)
    obj = mb.to_object(s.name)
    nh.ground_to_zero(obj)
    top = max(v.co.z for v in obj.data.vertices)
    print(f"{s.name}: hip at {s.leg_len:.3f}, height {top:.3f}, mapHip ~ {(s.body_z - s.body[2] * 0.6) / top:.2f}")
    return obj


def main(spec):
    nh.run(lambda: build(spec), spec.name, ground=spec.ground, views=((35, 20), (-90, 5), (150, 35)))


# ---------------------------------------------------------------- penguin

@dataclass
class Penguin:
    name: str
    length: float = 1.6
    girth: float = 0.28
    beak_len: float = 0.22
    flipper: float = 0.45
    back: tuple = (0.12, 0.13, 0.15)
    belly: tuple = (0.92, 0.91, 0.88)
    beak_col: tuple = (0.15, 0.13, 0.12)
    foot_col: tuple = (0.55, 0.45, 0.38)
    eye_r: float = 0.025
    voxel: float = 0.014
    max_tris: int = 10000


def build_penguin(s):
    b = nh.MeshBuilder()
    L, g = s.length, s.girth
    pts = [(0, -L * 0.42, 0.02), (0, -L * 0.3, 0.0), (0, -L * 0.1, 0), (0, L * 0.15, 0), (0, L * 0.36, -0.01), (0, L * 0.46, -0.02)]
    rr = [g * 0.42, g * 0.7, g * 0.97, g, g * 0.75, g * 0.3]
    b.add(nh.tube(pts, rr, sides=18, scale_xy=(0.95, 1.0)), s.back)
    head = Vector((0, -L * 0.45, 0.03))
    b.add(nh.ellipsoid(tuple(head), (g * 0.42, g * 0.55, g * 0.42)), s.back)
    tip = head + Vector((0, -g * 0.5 - s.beak_len, -0.01))
    b.add(nh.tube([tuple(head + Vector((0, -g * 0.35, -0.005))), tuple(tip)], [g * 0.16, s.voxel], sides=10,
                  scale_xy=(0.7, 1.0)), s.beak_col)
    for sx in (-1, 1):
        r0 = Vector((sx * g * 0.8, -L * 0.18, g * 0.15))
        r1 = r0 + Vector((sx * s.flipper * 0.85, s.flipper * 0.45, -s.flipper * 0.1))
        b.add(nh.tube([tuple(r0), tuple(r0.lerp(r1, 0.4)), tuple(r1)], [g * 0.2, g * 0.22, s.voxel * 1.2], sides=10,
                      scale_xy=(1.0, 0.25)), s.back)
        f0 = Vector((sx * g * 0.35, L * 0.36, -g * 0.45))
        b.add(nh.tube([tuple(f0), tuple(f0 + Vector((sx * 0.02, g * 0.55, -g * 0.05)))], [g * 0.12, g * 0.1], sides=8,
                      scale_xy=(1.4, 0.5)), s.foot_col)
    fused = b.fuse(voxel=s.voxel, smooth=4, smooth_factor=0.5, max_tris=s.max_tris)
    col = fused.loops.layers.color["Col"]

    def paint(co, n):
        # dark back and flipper tops, white belly; keep the beak and feet colours
        if co.y < -L * 0.45 - g * 0.3 or (co.y > L * 0.34 and co.z < -g * 0.35):
            return None
        side = co.z + 0.25 * abs(co.x) - (0.05 if co.y < -L * 0.3 else 0.0)
        return nh.lerp(s.belly, s.back, nh.smoothstep(-g * 0.25, g * 0.05, side))

    for f in fused.faces:
        for l in f.loops:
            c = paint(l.vert.co, l.vert.normal)
            if c is not None:
                l[col] = (*c, 1.0)
    mb = nh.MeshBuilder()
    mb.add(fused)
    for sx in (-1, 1):
        mb.add(nh.ellipsoid(tuple(head + Vector((sx * g * 0.38, -g * 0.2, g * 0.12))), (s.eye_r,) * 3, subdivisions=2), EYE)
    obj = mb.to_object(s.name)
    vs = obj.data.vertices
    lo = Vector((min(v.co.x for v in vs), min(v.co.y for v in vs), min(v.co.z for v in vs)))
    hi = Vector((max(v.co.x for v in vs), max(v.co.y for v in vs), max(v.co.z for v in vs)))
    c = (lo + hi) / 2
    for v in vs:
        v.co -= c
    return obj


def main_penguin(spec):
    nh.run(lambda: build_penguin(spec), spec.name, background=(0.05, 0.22, 0.32), views=((35, 25), (-90, 5), (0, 80)))
