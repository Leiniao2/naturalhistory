"""
Procedural Palaeospondylus gunni (Middle Devonian, Achanarras, Scotland) for the map (Swim style).

A tiny (about 5 cm), eel-like vertebrate known from thousands of flattened skeletons in the
Achanarras lake beds of Caithness (about 390-385 million years old). Only the cartilage
skeleton is preserved - no teeth, scales or dermal bone - and its relationships are still
argued over (hagfish, stem tetrapod or a relative of sharks have all been proposed). What is
known is followed here: a compact cartilaginous skull with paired nasal and otic capsules and
a pair of flat postoccipital lamellae behind it; at the snout tip, a ring of short, stiff
cirri radiating around the opening of the rostral cartilage; a long column of ring-shaped
vertebral centra; and a tail fin supported above and below by forked radials, the ventral lobe
a little deeper than the dorsal. Paired fins are left out. The soft body outline is a
conservative eel-like reconstruction; muted olive-brown with paler cartilage on the head.

The skull, lamellae, body tube and caudal fin fold are lofted / slabbed (helpers from
otodus_megalodon.py), fused into one seamless surface (nh_model.MeshBuilder.fuse), given
ring grooves for the vertebral centra and decimated, then repainted procedurally (rings,
neural-arch row, fin radials). The rostral ring, cirri and eyes are crisp shells.

palaeospondylus_australis.py reuses this file with its own proportions (module-level P).

Usage:
  blender --background --python tools/blender/palaeospondylus_gunni.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PalaeospondylusGunni.fbx
Pivot at the body centre, faces -Y, dorsal side up (+Z). About 2 units long.
"""

import math
import sys
from pathlib import Path

from mathutils import Vector, noise

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import otodus_megalodon as om  # noqa: E402  (loft / fin-slab / interpolation helpers)
import mola_mola as mola  # noqa: E402  (decimate helper)

P = dict(
    name="PalaeospondylusGunni",
    voxel=0.011, max_tris=4200,
    y_tip=-1.00, y_skull=-0.66, y_end=0.97,
    # half-width / half-height of the head and body, snout to tail tip
    half_w=[(-1.00, 0.030), (-0.96, 0.055), (-0.88, 0.075), (-0.76, 0.090), (-0.68, 0.082), (-0.62, 0.060),
            (-0.50, 0.052), (-0.10, 0.052), (0.30, 0.042), (0.65, 0.024), (0.97, 0.004)],
    half_h=[(-1.00, 0.022), (-0.96, 0.036), (-0.88, 0.046), (-0.76, 0.052), (-0.68, 0.050), (-0.62, 0.050),
            (-0.50, 0.060), (-0.10, 0.064), (0.30, 0.052), (0.65, 0.030), (0.97, 0.005)],
    nasal=(-0.93, 0.040), otic=(-0.74, 0.075),     # (y, x) of the paired capsule bulges
    lamella=dict(y=-0.59, x=0.068, r=(0.040, 0.075, 0.011)),
    ring=dict(rx=0.032, rz=0.022, tube=0.008, cirri=10, length=0.075, r=0.0065),
    centra=0.032,                                     # spacing of the vertebral rings
    dorsal_fin=dict(y0=0.22, y_peak=0.66, h=0.075),
    ventral_fin=dict(y0=0.40, y_peak=0.70, h=0.11),
    eye=dict(y=-0.84, r=0.011),
    fontanelle=(-0.80, 0.03, 0.06, 0.0),           # dorsal fontanelle (y, half width, half length, rear taper)
    colors=dict(back=(0.33, 0.30, 0.22), flank=(0.47, 0.43, 0.33), belly=(0.70, 0.66, 0.55),
                skull=(0.60, 0.55, 0.42), ring=(0.22, 0.19, 0.14), fin=(0.66, 0.62, 0.50),
                ray=(0.34, 0.30, 0.22), cirri=(0.66, 0.60, 0.46), eye=(0.05, 0.05, 0.04)),
    preview=dict(background=(0.05, 0.13, 0.14), views=((35, 25), (90, 4), (30, 62), (-25, 12))),
)


def w(y): return om._interp(P["half_w"], y)
def h(y): return om._interp(P["half_h"], y)


def body_point(y, a):
    """Rounded cross-section; the skull is flattened (wider than deep), the body more eel-like
    and laterally compressed toward the tail. Capsule bulges on the skull sides."""
    c, s = math.cos(a), math.sin(a)
    n = 2.3
    ww = w(y)
    for (cy, cx), amp in ((P["nasal"], 0.012), (P["otic"], 0.016)):
        ww += amp * math.exp(-((y - cy) / 0.045) ** 2)
    x = ww * math.copysign(abs(c) ** (2.0 / n), c)
    z = h(y) * math.copysign(abs(s) ** (2.0 / n), s)
    return Vector((x, y, z))


def fin_fold(up):
    """Caudal fin fold above (up) or below the tail: rises gently, deepest near the peak,
    then runs out to the pointed tail tip."""
    d = P["dorsal_fin"] if up else P["ventral_fin"]
    s = 1 if up else -1
    ye = P["y_end"]
    root = lambda y: s * (h(y) * 0.5)  # noqa: E731  (inside the body so it fuses)
    pts = []
    n = 14
    for i in range(n + 1):
        y = d["y0"] + (ye + 0.02 - d["y0"]) * i / n
        t = (y - d["y0"]) / (ye + 0.02 - d["y0"])
        tp = (d["y_peak"] - d["y0"]) / (ye + 0.02 - d["y0"])
        prof = math.sin(math.pi * 0.5 * min(1.0, t / tp)) if t < tp else math.cos(math.pi * 0.5 * (t - tp) / (1 - tp))
        pts.append((y, s * (h(y) + d["h"] * max(prof, 0.0) ** 0.8)))
    pts += [(ye - 0.02, root(ye - 0.02)), (d["y0"] + 0.02, root(d["y0"] + 0.02))]
    th = [0.026 - 0.004 * ((u - d["y0"]) / (ye - d["y0"])) for u, _ in pts]
    return om.fin_slab(pts, th, om.midline_frame)


def lamella(sign):
    L = P["lamella"]
    return nh.ellipsoid((sign * L["x"], L["y"], -0.005), L["r"], subdivisions=3)


def ring_amount(p):
    """0..1 groove between successive vertebral centra (behind the skull)."""
    if p.y < P["y_skull"] + 0.06 or p.y > P["y_end"] - 0.03:
        return 0.0
    k = (p.y - P["y_skull"]) / P["centra"]
    f = abs(k - round(k))
    return (1.0 - nh.smoothstep(0.06, 0.2, f)) * (1.0 - nh.smoothstep(P["y_end"] - 0.2, P["y_end"], p.y) * 0.6)


def on_body(p):
    """1 on the body tube, 0 out on the fin fold."""
    y = max(min(p.y, P["y_end"]), P["y_tip"])
    return 1.0 - nh.smoothstep(h(y) * 1.05, h(y) * 1.35, abs(p.z))


def body_color(p, n):
    C = P["colors"]
    y = max(min(p.y, P["y_end"]), P["y_tip"])
    up = nh.smoothstep(-h(y) * 0.6, h(y) * 0.9, p.z)
    c = nh.lerp(C["belly"], C["flank"], nh.smoothstep(-h(y) * 0.9, 0.0, p.z))
    c = nh.lerp(c, C["back"], up * 0.8)
    head = 1.0 - nh.smoothstep(P["y_skull"] - 0.02, P["y_skull"] + 0.06, p.y)
    c = nh.lerp(c, C["skull"], head * 0.7)
    lam = P["lamella"]
    if abs(abs(p.x) - lam["x"]) < lam["r"][0] * 1.1 and abs(p.y - lam["y"]) < lam["r"][1]:
        c = nh.lerp(c, C["skull"], 0.5)
    # dorsal fontanelle: a darker oval on the skull roof
    fy, fw, fl, point = P["fontanelle"]
    taper = 1.0 - point * nh.smoothstep(0.0, 1.0, (p.y - fy) / fl)  # narrower toward the back
    q = Vector((p.x / (fw * max(taper, 0.15)), (p.y - fy) / fl, 0))
    if p.z > 0 and n.z > 0.4:
        c = nh.lerp(c, C["ring"], (1.0 - nh.smoothstep(0.7, 1.0, q.length)) * 0.45)
    mott = noise.noise(p * 14.0) * 0.5 + 0.5
    c = nh.lerp(c, tuple(v * 0.85 for v in c), mott * 0.35)
    body = on_body(p)
    # vertebral rings and the row of neural arches along the back
    c = nh.lerp(c, C["ring"], ring_amount(p) * 0.65 * body)
    if p.y > P["y_skull"] and p.z > h(y) * 0.6 and body > 0.5:
        k = (p.y - P["y_skull"]) / P["centra"]
        arch = 1.0 - nh.smoothstep(0.15, 0.3, abs(k - math.floor(k) - 0.5))
        c = nh.lerp(c, C["ring"], arch * 0.3)
    # fin fold: pale with forked radials, slanting back
    if body < 1.0:
        fin = C["fin"]
        k = (p.y - abs(p.z) * 0.6) / (P["centra"] * 0.5)
        ray = 1.0 - nh.smoothstep(0.12, 0.28, abs(k - round(k)))
        fin = nh.lerp(fin, C["ray"], ray * 0.55)
        c = nh.lerp(c, fin, 1.0 - body)
    return c


def skin_detail(bm):
    bm.normal_update()
    for v in bm.verts:
        p = v.co
        d = noise.noise(p * 80.0) * 0.0005 - ring_amount(p) * on_body(p) * 0.004
        v.co = p + v.normal * d


def build_body():
    parts = nh.MeshBuilder()
    grey = (0.5, 0.5, 0.5)
    parts.add(om.loft(P["y_tip"], P["y_end"], 110, 24, body_point), grey)
    parts.add(fin_fold(True), grey)
    parts.add(fin_fold(False), grey)
    for sg in (-1, 1):
        parts.add(lamella(sg), grey)
    fused = parts.fuse(voxel=P["voxel"], smooth=5, smooth_factor=0.5)
    skin_detail(fused)
    return mola.decimate(fused, P["max_tris"])


def snout_details(mb):
    """Annular rostral cartilage at the snout tip, ringed by short stiff cirri."""
    C = P["colors"]
    R = P["ring"]
    y0 = P["y_tip"] + 0.012
    m = 16
    ring = [(R["rx"] * math.cos(k / m * math.tau), y0, R["rz"] * math.sin(k / m * math.tau)) for k in range(m + 1)]
    mb.add(nh.tube(ring, [R["tube"]] * len(ring), sides=6, cap_start=False, cap_end=False), C["cirri"])
    # the opening inside the ring
    mb.add(nh.ellipsoid((0, y0 - 0.002, 0), (R["rx"] * 0.75, 0.004, R["rz"] * 0.7), subdivisions=2), C["ring"])
    for k in range(R["cirri"]):
        a = (k + 0.5) / R["cirri"] * math.tau
        ca, sa = math.cos(a), math.sin(a)
        base = Vector((R["rx"] * ca, y0, R["rz"] * sa))
        out = Vector((ca, 0.0, sa * 0.8))
        fwd = Vector((0, -1, 0))
        L = R["length"]
        pts = [base + fwd * 0.004]
        for t in (0.35, 0.7, 1.0):
            pts.append(base + (fwd * (0.8 - 0.1 * t) + out * (0.35 + 0.45 * t)).normalized() * L * t)
        mb.add(nh.tube(pts, [R["r"], R["r"] * 0.8, R["r"] * 0.55, 0.0], sides=5), C["cirri"])


def eyes(mb):
    C = P["colors"]
    e = P["eye"]
    y = e["y"]
    for sx in (-1, 1):
        x = sx * (w(y) + 0.012 * math.exp(-((y - P["otic"][0]) / 0.045) ** 2)) * 0.86
        z = h(y) * 0.45
        mb.add(nh.ellipsoid((x, y, z), (e["r"] * 0.7, e["r"], e["r"] * 0.9), subdivisions=2), C["eye"])


def build():
    mb = nh.MeshBuilder()
    mb.add(build_body(), body_color)
    snout_details(mb)
    eyes(mb)
    return mb.to_object(P["name"], roughness=0.6)


def main():
    nh.run(build, P["name"], **P["preview"])


if __name__ == "__main__":
    main()
