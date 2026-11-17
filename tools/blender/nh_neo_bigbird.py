"""
Shared giant flightless bird for the Neogene / Pleistocene batch (tag "neo"):
terror birds (Phorusrhacos, Kelenken) and moa (Dinornis).

A fused biped caught mid-stride (left leg forward): a feathered body, long
legs with bare scaly shanks and three forward toes, an S-curved neck, a head
with either a tall, hooked, laterally flattened beak (terror birds) or a small
blunt bill (moa), small folded wings (or none) and a short tail plume.
The hip line printed by build() is the mapHip for the biped walk.
Faces -Y, pivot on the ground.
"""

import math
from dataclasses import dataclass

from mathutils import Matrix, Vector, noise

import nh_model as nh

EYE = (0.75, 0.55, 0.15)
PUPIL = (0.02, 0.02, 0.02)
CLAW = (0.15, 0.13, 0.11)


@dataclass
class Spec:
    name: str
    hip: float = 1.0             # hip height
    body: tuple = (0.22, 0.40, 0.25)   # half-width, half-length, half-height
    body_tilt: float = 10.0      # degrees nose-up
    leg_r: float = 0.06
    neck: tuple = ((0, -0.35, 0.15), (0, -0.48, 0.42), (0, -0.50, 0.65))   # offsets from body centre
    neck_r: tuple = (0.12, 0.08, 0.065)
    head_r: float = 0.08
    beak_len: float = 0.30
    beak_h: float = 0.14         # beak depth at the base
    hook: float = 1.0            # 0 = blunt bill, 1 = raptor hook
    wing: float = 0.25           # folded wing length (0 = none)
    tail: float = 0.15
    feather: tuple = (0.35, 0.28, 0.20)
    dark: tuple = (0.20, 0.15, 0.11)
    pale: tuple = (0.70, 0.62, 0.50)
    head_col: tuple = None
    beak_col: tuple = (0.80, 0.68, 0.40)
    leg_col: tuple = (0.55, 0.48, 0.32)
    stride: float = 0.30
    shag: float = 0.01
    voxel: float = 0.018
    max_tris: int = 10000
    eye_col: tuple = EYE


def build(s):
    b = nh.MeshBuilder()
    FEA, LEG, BEAK, HEAD = (1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0)
    bw, bl, bh = s.body
    C = Vector((0, 0.05, s.hip + bh * 0.35))
    tilt = math.radians(s.body_tilt)
    ax = Vector((0, -math.cos(tilt), math.sin(tilt)))
    b.add(nh.ellipsoid(tuple(C), (bw, bl, bh), subdivisions=4,
                       rotation=Matrix.Rotation(-tilt, 3, "X")), FEA)
    b.add(nh.ellipsoid(tuple(C + Vector((0, 0.05, -bh * 0.35))), (bw * 0.85, bl * 0.7, bh * 0.7)), FEA)
    # tail plume
    if s.tail > 0:
        root = C - ax * bl * 0.85
        b.add(nh.tube([tuple(root), tuple(root - ax * s.tail + Vector((0, 0, -s.tail * 0.3)))],
                      [bh * 0.45, bh * 0.15], sides=10, scale_xy=(1.4, 0.6)), FEA)
    # neck + head
    pts = [C + Vector(p) for p in s.neck]
    pts.insert(0, C + ax * bl * 0.55)
    radii = [s.neck_r[0] * 1.1] + list(s.neck_r)
    b.add(nh.tube([tuple(p) for p in pts], radii, sides=12), FEA)
    hc = pts[-1] + Vector((0, -s.head_r * 0.4, s.head_r * 0.3))
    b.add(nh.ellipsoid(tuple(hc), (s.head_r * 0.85, s.head_r * 1.2, s.head_r)), HEAD)
    # beak: tall, laterally compressed tube with a downward hook
    base = hc + Vector((0, -s.head_r * 0.8, -s.head_r * 0.1))
    n = 6
    bpts, br = [], []
    for i in range(n + 1):
        t = i / n
        y = -s.beak_len * t
        z = -s.hook * s.beak_h * 0.8 * nh.smoothstep(0.7, 1.0, t) ** 1.2 - s.beak_h * 0.1 * t
        bpts.append(tuple(base + Vector((0, y, z))))
        br.append(max(s.beak_h * 0.5 * (1 - 0.55 * t ** 2.0) * (1 - 0.6 * nh.smoothstep(0.8, 1.0, t)), s.voxel * 0.6))
    b.add(nh.tube(bpts, br, sides=12, scale_xy=(0.45 if s.hook > 0.3 else 0.8, 1.0)), BEAK)
    # wings folded on the flanks
    if s.wing > 0:
        for sx in (-1, 1):
            w0 = C + Vector((sx * bw * 0.85, -bl * 0.35, bh * 0.25))
            b.add(nh.tube([tuple(w0), tuple(w0 + Vector((sx * 0.02, s.wing, -s.wing * 0.35)))], [bh * 0.25, bh * 0.08],
                          sides=8, scale_xy=(0.45, 1.0)), FEA)
    # legs (left forward)
    claws = []
    for sx, sw in ((-1, 1), (1, -1)):
        r = s.leg_r
        hipj = C + Vector((sx * bw * 0.55, 0.02, -bh * 0.3))
        foot = Vector((sx * bw * 0.45, 0.05 - sw * s.stride, 0.0))
        knee = Vector((sx * bw * 0.6, hipj.y - s.hip * 0.18, s.hip * 0.72))
        ankle = foot + Vector((0, s.hip * 0.10 + 0.04 * sw, s.hip * 0.38))
        b.add(nh.ellipsoid(tuple(hipj.lerp(knee, 0.4)), (r * 1.8, r * 2.2, r * 3.2)), FEA)   # drumstick
        b.add(nh.tube([tuple(knee), tuple(ankle)], [r * 1.3, r * 0.75], sides=10), LEG)
        b.add(nh.tube([tuple(ankle), tuple(foot + Vector((0, 0, r * 0.5)))], [r * 0.7, r * 0.6], sides=10), LEG)
        for a in (-0.45, 0.0, 0.45):
            d = Vector((math.sin(a), -math.cos(a), 0))
            tip = foot + d * s.hip * 0.16 + Vector((0, 0, r * 0.3))
            b.add(nh.tube([tuple(foot + Vector((0, 0, r * 0.5))), tuple(tip)], [r * 0.5, r * 0.3], sides=8), LEG)
            claws.append((tip, d, r))
        b.add(nh.tube([tuple(foot + Vector((0, 0, r * 0.5))), tuple(foot + Vector((0, s.hip * 0.06, r * 0.3)))],
                      [r * 0.4, r * 0.25], sides=6), LEG)
    fused = b.fuse(voxel=s.voxel, smooth=4, smooth_factor=0.5, max_tris=s.max_tris)
    fused.normal_update()
    for v in fused.verts:
        if v.co.z > s.hip * 0.75:
            v.co += v.normal * s.shag * max(0.0, noise.noise(Vector((v.co.x * 25, v.co.y * 25, v.co.z * 10))))
    fused.normal_update()
    col = fused.loops.layers.color.get("Col")
    for f in fused.faces:
        for l in f.loops:
            t = l[col]
            p, nrm = l.vert.co, l.vert.normal
            if t[2] > 0.5 and t[0] < 0.5:
                c = s.beak_col
            elif t[1] > 0.5 and t[0] < 0.5:
                c = s.leg_col
            else:
                c = s.feather
                c = nh.lerp(c, s.dark, 0.6 * nh.smoothstep(0.3, 0.9, nrm.z))
                c = nh.lerp(c, s.pale, 0.7 * nh.smoothstep(-0.1, -0.8, nrm.z))
                if t[1] > 0.5 and s.head_col:
                    c = s.head_col
                c = nh.lerp(c, s.dark, 0.25 * max(0.0, noise.noise(p * 18)))
            l[col] = (c[0], c[1], c[2], 1.0)
    mb = nh.MeshBuilder()
    mb.add(fused)
    for sx in (-1, 1):
        e = hc + Vector((sx * s.head_r * 0.78, -s.head_r * 0.35, s.head_r * 0.2))
        mb.add(nh.ellipsoid(tuple(e), (s.head_r * 0.18,) * 3, subdivisions=2), s.eye_col)
        mb.add(nh.ellipsoid(tuple(e + Vector((sx * s.head_r * 0.1, -s.head_r * 0.03, 0))), (s.head_r * 0.09,) * 3,
                            subdivisions=1), PUPIL)
    for tip, d, r in claws:
        mb.add(nh.tube([tuple(tip - d * r * 0.3), tuple(tip + d * r * 1.2 + Vector((0, 0, -r * 0.3)))], [r * 0.3, 0.0],
                       sides=6), CLAW)
    obj = mb.to_object(s.name)
    nh.ground_to_zero(obj)
    top = max(v.co.z for v in obj.data.vertices)
    print(f"{s.name}: hip at {s.hip:.3f}, height {top:.3f}, mapHip ~ {s.hip / top:.2f}")
    return obj


def main(spec, ground=(0.45, 0.42, 0.30)):
    nh.run(lambda: build(spec), spec.name, ground=ground, views=((35, 15), (-90, 5), (0, 5)))
