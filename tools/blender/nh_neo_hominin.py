"""
Shared upright-walking hominin for the Neogene / Pleistocene batch (tag "neo"):
Ardipithecus, Australopithecus, Homo neanderthalensis.

One fused body caught mid-stride (left leg forward, right arm forward), the
hips at the printed mapHip so the game's biped walk swings the legs.

  * Spec: stature, leg / arm length (fractions of stature), shoulder and hip
    width, chest girth, head size, muzzle projection, brow ridge, big-toe
    splay (grasping foot), hair cover (whole body or head only), skin / hair
    colours, an optional hide wrap around the waist (Neanderthal).
  * Faces -Y, pivot on the ground.
"""

import math
from dataclasses import dataclass

from mathutils import Vector, noise

import nh_model as nh

# Resolution of the fused body relative to each Spec's voxel / max_tris (see build)
DETAIL = 0.5
TRIS = 2.6
SMOOTH = 18  # more passes at the finer voxel, so the joins between the body parts stay soft

EYE = (0.18, 0.11, 0.06)
PUPIL = (0.02, 0.015, 0.01)


@dataclass
class Spec:
    name: str
    stature: float = 1.2
    leg: float = 0.45            # hip height / stature
    arm: float = 0.42            # shoulder-to-fingertip / stature
    shoulder: float = 0.16       # half-width (fraction of stature)
    hip: float = 0.12
    chest: float = 0.11          # chest half-depth
    belly: float = 1.0
    head: float = 0.085          # cranium radius / stature
    muzzle: float = 0.6          # 0 = flat face, 1 = ape-like snout
    brow: float = 0.5
    forehead: float = 0.0        # high vault (0 = low, sloping)
    stoop: float = 8.0           # forward lean of the trunk, degrees
    toe_splay: float = 0.0       # grasping big toe
    fur: float = 1.0             # 1 = hair all over, 0 = head hair only
    hair: tuple = (0.25, 0.17, 0.11)
    skin: tuple = (0.55, 0.40, 0.30)
    wrap: tuple = None           # hide wrap colour
    stride: float = 0.16
    bulk: float = 1.0            # limb thickness
    shag: float = 0.006
    voxel: float = 0.012
    max_tris: int = 9000


def build(s):
    S = s.stature
    b = nh.MeshBuilder()
    HAIR, SKIN = (1, 0, 0), (0, 1, 0)   # tags; painted after fusing
    zh = S * s.leg
    lean = math.radians(s.stoop)
    up = Vector((0, -math.sin(lean), math.cos(lean)))
    torso_len = S * 0.30
    pelvis = Vector((0, 0, zh + S * 0.03))
    chest = pelvis + up * torso_len * 0.70
    shoulder = pelvis + up * torso_len
    # trunk
    b.add(nh.ellipsoid(tuple(pelvis), (S * s.hip, S * 0.075, S * 0.07)), HAIR)
    b.add(nh.tube([tuple(pelvis), tuple(pelvis.lerp(chest, 0.5)), tuple(chest), tuple(shoulder - up * S * 0.02)],
                  [S * 0.075 * s.belly, S * 0.085 * s.belly, S * s.chest, S * 0.075], sides=14,
                  scale_xy=(s.shoulder / s.chest * 0.85, 1.0)), HAIR)
    b.add(nh.ellipsoid(tuple(shoulder - up * S * 0.05), (S * s.shoulder * 0.92, S * s.chest * 0.85, S * 0.06)), HAIR)
    # neck + head
    neck_top = shoulder + up * S * 0.03 + Vector((0, -S * 0.02, 0))
    b.add(nh.tube([tuple(shoulder - up * S * 0.02), tuple(neck_top)], [S * 0.05, S * 0.045], sides=10), HAIR)
    hr = S * s.head
    hc = neck_top + Vector((0, -hr * 0.2, hr * 0.7))
    b.add(nh.ellipsoid(tuple(hc), (hr * 0.82, hr * 1.0, hr * (0.85 + 0.2 * s.forehead))), HAIR)
    face_c = hc + Vector((0, -hr * (0.65 + 0.45 * s.muzzle), -hr * 0.45))
    b.add(nh.ellipsoid(tuple(face_c), (hr * 0.55, hr * (0.35 + 0.25 * s.muzzle), hr * 0.42)), SKIN)
    b.add(nh.ellipsoid(tuple(hc + Vector((0, -hr * 0.62, -hr * 0.05))), (hr * 0.62, hr * 0.45, hr * 0.55)), SKIN)
    if s.brow > 0:
        b.add(nh.tube([tuple(hc + Vector((sx * hr * 0.42, -hr * 0.82, hr * 0.18))) for sx in (-1, 0, 1)],
                      [hr * 0.12 * s.brow + 0.004] * 3, sides=8), SKIN)
    for sx in (-1, 1):
        b.add(nh.ellipsoid(tuple(hc + Vector((sx * hr * 0.82, hr * 0.05, -hr * 0.1))), (hr * 0.1, hr * 0.18, hr * 0.24)),
              SKIN)
    # arms (right arm forward)
    for sx, sw in ((-1, -1), (1, 1)):
        sh = shoulder + Vector((sx * S * s.shoulder * 0.88, 0, -S * 0.03))
        L = S * s.arm
        elbow = sh + Vector((sx * S * 0.025, -sw * L * 0.12 * 0, -L * 0.45)) + Vector((0, sw * -L * 0.10, 0))
        hand = elbow + Vector((sx * S * 0.01, sw * -L * 0.18, -L * 0.36))
        b.add(nh.tube([tuple(sh), tuple(elbow), tuple(hand)], [S * 0.036 * s.bulk, S * 0.029 * s.bulk, S * 0.022 * s.bulk], sides=10), HAIR)
        b.add(nh.ellipsoid(tuple(hand + Vector((0, 0, -S * 0.04))), (S * 0.02, S * 0.03, S * 0.05)), SKIN)
    # legs (left leg forward)
    for sx, sw in ((-1, 1), (1, -1)):
        hp = pelvis + Vector((sx * S * s.hip * 0.6, 0, -S * 0.02))
        st = s.stride * S * sw
        foot = Vector((sx * S * s.hip * 0.6, -st, 0.0))
        knee = hp.lerp(foot, 0.5) + Vector((0, -S * 0.035, S * 0.01))
        ankle = foot + Vector((0, 0, S * 0.04))
        b.add(nh.tube([tuple(hp), tuple(knee), tuple(ankle)], [S * 0.052 * s.bulk, S * 0.037 * s.bulk, S * 0.025 * s.bulk], sides=10), HAIR)
        b.add(nh.ellipsoid(tuple(hp + Vector((0, S * 0.01, -S * 0.08))), (S * 0.05, S * 0.055, S * 0.10)), HAIR)
        b.add(nh.ellipsoid(tuple(foot + Vector((0, -S * 0.04, S * 0.018))), (S * 0.03, S * 0.07, S * 0.02)), SKIN)
        if s.toe_splay > 0:
            b.add(nh.ellipsoid(tuple(foot + Vector((-sx * S * 0.035 * s.toe_splay, -S * 0.09, S * 0.014))),
                               (S * 0.012, S * 0.03, S * 0.012)), SKIN)
    if s.wrap:
        b.add(nh.tube([tuple(pelvis + Vector((0, 0, S * 0.04))), tuple(pelvis - Vector((0, 0, S * 0.10)))],
                      [S * s.hip * 1.12, S * s.hip * 1.18], sides=14, scale_xy=(1.0, 0.75)), (0, 0, 1))
    # finer than the Spec asks: the Neogene megafauna are seen big and close on the map, and at the
    # old resolution their bodies came out lumpy, with stick legs (DETAIL / TRIS scale every Spec)
    fused = b.fuse(voxel=s.voxel * DETAIL, smooth=SMOOTH, smooth_factor=0.6, max_tris=int(s.max_tris * TRIS))
    fused.normal_update()
    col = fused.loops.layers.color.get("Col")
    # head-hair region: top/back of the cranium
    for v in fused.verts:
        if v.co.z < 0.02:
            continue
        a = s.shag * max(0.0, noise.noise(Vector((v.co.x * 60, v.co.y * 60, v.co.z * 20))))
        v.co += v.normal * a
    fused.normal_update()
    for f in fused.faces:
        for l in f.loops:
            t = l[col]
            p, n = l.vert.co, l.vert.normal
            hair_w = t[0] * s.fur
            q = p - hc
            if q.length < hr * 1.3 and q.z > -hr * 0.25 and q.y > -hr * 0.75:
                hair_w = max(hair_w, 1.0)
            c = nh.lerp(s.skin, s.hair, min(1.0, hair_w))
            c = nh.lerp(c, nh.lerp(c, (0, 0, 0), 0.3), 0.3 * max(0.0, noise.noise(p * 25)))
            if s.wrap and t[2] > 0.5:
                c = nh.lerp(s.wrap, nh.lerp(s.wrap, (0, 0, 0), 0.4), 0.5 * max(0.0, noise.noise(p * 30)))
            l[col] = (c[0], c[1], c[2], 1.0)
    mb = nh.MeshBuilder()
    mb.add(fused)
    for sx in (-1, 1):
        e = hc + Vector((sx * hr * 0.30, -hr * 1.04, hr * 0.0))
        nh.eye(mb, e, Vector((sx * 0.35, -1, 0)), hr * 0.13, s.skin,
               forward=(0, -1, 0))  # facing forward, like ours
    obj = mb.to_object(s.name)
    nh.ground_to_zero(obj)
    top = max(v.co.z for v in obj.data.vertices)
    print(f"{s.name}: hip at {zh:.3f}, height {top:.3f}, mapHip ~ {zh / top:.2f}")
    return obj


def main(spec, ground=(0.45, 0.42, 0.30)):
    nh.run(lambda: build(spec), spec.name, ground=ground, views=((35, 15), (-90, 5), (0, 5)))
