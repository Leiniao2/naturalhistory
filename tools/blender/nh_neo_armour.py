"""
Shared glyptodont body for the Neogene / Quaternary armoured xenarthrans in
tools/blender/ (glyptotherium_texanum.py, doedicurus_clavicaudatus.py), generalised
from glyptodon_clavipes.py.

  * Spec: carapace half-width / half-length / height (the dome), how far the dome's
    top is flattened or peaked, the flared skirt, head size, leg size, tail length and
    girth, the number of armoured tail rings, and an optional terminal tail club
    (Doedicurus) with big conical spikes.
  * build(spec): carapace, belly, head with a bony head cap, pillar legs with claws and
    a ringed tail fused into one surface; the carapace gets a rosette (voronoi)
    osteoderm relief and is repainted dark seams / pale rosette centres; crisp eyes,
    claws and club spikes are added afterwards.
  * Faces -Y, pivot on the ground.
"""

import math
from dataclasses import dataclass

from mathutils import Vector, noise

import nh_model as nh

EYE = (0.06, 0.04, 0.03)
CLAW = (0.18, 0.15, 0.12)


@dataclass
class Spec:
    name: str
    rx: float = 0.42             # carapace half-width
    ry: float = 0.62             # carapace half-length
    rz: float = 0.46             # carapace half-height (dome)
    zc: float = 0.42             # carapace centre height
    skirt: float = 0.06          # flare of the lower rim
    flat_top: float = 0.04       # flattening of the top of the dome
    head: float = 1.0
    leg: float = 1.0
    tail_len: float = 0.50
    tail_r: float = 0.11
    tail_rings: int = 5
    tail_lift: float = 0.0       # raises the tail end (a club held off the ground)
    club: float = 0.0            # radius of a terminal tail club (0 = none)
    club_spikes: int = 0
    spike: tuple = (0.55, 0.47, 0.36)
    shell: tuple = (0.42, 0.33, 0.22)
    shell_pale: tuple = (0.62, 0.52, 0.38)
    seam: tuple = (0.20, 0.15, 0.10)
    rim: tuple = (0.25, 0.19, 0.13)
    skin: tuple = (0.36, 0.31, 0.26)
    rosette: float = 11.0        # osteoderm frequency
    voxel: float = 0.016
    max_tris: int = 11000


def build(s):
    b = nh.MeshBuilder()
    SH, LG = s.shell, s.skin
    zc = s.zc

    def shell_deform(v):
        return 1.0 + s.skirt * max(0.0, -v.z) - s.flat_top * max(0.0, v.z) ** 3

    b.add(nh.ellipsoid((0, 0, zc), (s.rx, s.ry, s.rz), subdivisions=4, deform=shell_deform), SH)
    b.add(nh.ellipsoid((0, 0, zc - s.rz * 0.26), (s.rx * 0.8, s.ry * 0.8, s.rz * 0.3)), LG)   # belly
    hk = s.head
    hy = -s.ry - 0.04 * hk
    hz = zc - s.rz * 0.30
    b.add(nh.ellipsoid((0, hy, hz), (0.12 * hk, 0.14 * hk, 0.12 * hk)), LG)
    b.add(nh.ellipsoid((0, hy - 0.10 * hk, hz - 0.06 * hk), (0.085 * hk, 0.10 * hk, 0.10 * hk)), LG)
    b.add(nh.ellipsoid((0, hy, hz + 0.09 * hk), (0.10 * hk, 0.12 * hk, 0.05 * hk)), SH)        # head cap
    # tail with armoured rings
    t0 = Vector((0, s.ry * 0.9, zc - s.rz * 0.25))
    t1 = Vector((0, s.ry * 0.9 + s.tail_len, max(0.14, zc - s.rz * 0.6) + s.tail_lift))
    pts = [t0.lerp(t1, k / 3) + Vector((0, 0, -0.03 * math.sin(math.pi * k / 3))) for k in range(4)]
    end_r = s.tail_r * (0.75 if s.club > 0 else 0.32)
    b.add(nh.tube([tuple(p) for p in pts], [s.tail_r, s.tail_r * 0.8, s.tail_r * 0.6 + end_r * 0.2, end_r], sides=12), SH)
    for i in range(s.tail_rings):
        t = i / s.tail_rings
        p = pts[0].lerp(pts[-1], t + 0.05)
        r = s.tail_r * (1.05 - t * (0.55 if s.club == 0 else 0.25))
        b.add(nh.tube([tuple(p + Vector((0, -0.015, 0))), tuple(p + Vector((0, 0.015, 0)))], [r, r], sides=12), SH)
    club_c = None
    if s.club > 0:
        club_c = pts[-1] + (pts[-1] - pts[-2]).normalized() * s.club * 0.9
        b.add(nh.ellipsoid(tuple(club_c), (s.club * 0.85, s.club * 1.25, s.club * 0.8), subdivisions=3), SH)
    claws = []
    lx, ly = s.rx * 0.6, s.ry * 0.53
    lk = s.leg
    ztop = zc - s.rz * 0.2
    for (x, y, st) in ((-lx, -ly, -0.05), (lx, -ly, 0.05), (-lx, ly, 0.04), (lx, ly, -0.05)):
        b.add(nh.tube([(x * 0.9, y, ztop), (x, y + st, 0.05)], [0.085 * lk, 0.075 * lk], sides=12), LG)
        b.add(nh.ellipsoid((x, y + st - 0.02, 0.04), (0.085 * lk, 0.10 * lk, 0.045)), LG)
        for a in (-0.5, 0.0, 0.5):
            claws.append(Vector((x + math.sin(a) * 0.07 * lk, y + st - 0.11 * lk, 0.025)))
    fused = b.fuse(voxel=s.voxel, smooth=3, smooth_factor=0.5, max_tris=s.max_tris)
    fused.normal_update()
    col = fused.loops.layers.color.get("Col")
    shell_v = {}
    for v in fused.verts:
        q = v.co - Vector((0, 0, zc))
        on_shell = ((q.x / s.rx) ** 2 + (q.y / s.ry) ** 2 + (q.z / s.rz) ** 2 > 0.8 and v.co.z > zc - s.rz * 0.6
                    and abs(v.co.y) < s.ry * 1.04)
        on_tail = v.co.y > s.ry * 0.95 and v.co.z > 0.06
        if on_shell or on_tail:
            dist, _p = noise.voronoi(v.co * (s.rosette if on_shell else s.rosette * 1.5), distance_metric="DISTANCE")
            d = dist[1] - dist[0]
            v.co += v.normal * 0.008 * nh.smoothstep(0.0, 0.25, d)
            shell_v[v] = (d, on_shell)
    fused.normal_update()
    for f in fused.faces:
        for l in f.loops:
            c = l[col]
            c = (c[0], c[1], c[2])
            v = l.vert
            if v in shell_v:
                d, on_shell = shell_v[v]
                c = nh.lerp(s.seam, nh.lerp(s.shell, s.shell_pale, nh.smoothstep(0.25, 0.6, d)),
                            nh.smoothstep(0.02, 0.12, d))
                if on_shell and v.co.z < zc - s.rz * 0.4:
                    c = nh.lerp(c, s.rim, 0.5)
            l[col] = (c[0], c[1], c[2], 1.0)
    mb = nh.MeshBuilder()
    mb.add(fused)
    for sx in (-1, 1):
        mb.add(nh.ellipsoid((sx * 0.085 * hk, hy - 0.10 * hk, hz + 0.0), (0.016 * hk,) * 3, subdivisions=2), EYE)
    for c in claws:
        mb.add(nh.tube([tuple(c + Vector((0, 0.02, 0.01))), tuple(c + Vector((0, -0.04, -0.015)))], [0.014, 0.0],
                       sides=5), CLAW)
    if club_c is not None and s.club_spikes:
        # big conical spikes over the top and sides of the club (Doedicurus)
        n = s.club_spikes
        for ring, yo in ((0, -0.45), (1, 0.45)):
            for i in range(n):
                a = math.radians(-25 + 230 * (i + 0.5 * ring) / max(n - 1, 1))
                if a > math.radians(205):
                    continue
                d = Vector((math.cos(a), yo * 0.6, math.sin(a))).normalized()
                base = club_c + Vector((d.x * s.club * 0.8, d.y * s.club * 1.2, d.z * s.club * 0.75))
                mb.add(nh.tube([tuple(base - d * s.club * 0.2), tuple(base + d * s.club * 0.75)],
                               [s.club * 0.24, 0.0], sides=8), s.spike)
    obj = mb.to_object(s.name)
    nh.ground_to_zero(obj)
    return obj


def main(spec, ground=(0.45, 0.42, 0.30)):
    nh.run(lambda: build(spec), spec.name, ground=ground, views=((35, 20), (-90, 5), (0, 10)))
