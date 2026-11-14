"""
Procedural red kangaroo (Osphranter rufus) for map colonies - a big male "boomer".

Resting upright stance: sitting back on powerful hind legs and long feet, the
thick tail as a third support, muscular bent forearms held in front of a broad
chest, a sculpted head (brow, cheekbones, long muzzle with nostrils and mouth)
and tall cupped ears. Reddish-brown back fading to a pale cream chest and belly,
dark paws, toes, claws and ear tips, pale muzzle band.

The body is built from overlapping parts and fused into one seamless,
voxel-remeshed surface with a little fur displacement; eyes, claws, nostrils
and the cupped ears are crisp details on top. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/kangaroo.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Kangaroo.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy  # noqa: E402
import bmesh  # noqa: E402
import nh_model as nh  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402

RED = (0.66, 0.30, 0.15)        # reddish-brown back
RED_DARK = (0.48, 0.20, 0.09)
CREAM = (0.93, 0.84, 0.70)      # chest / belly
DARK = (0.13, 0.08, 0.06)       # paws, toes, ear tips
CLAW = (0.10, 0.08, 0.07)
NOSE = (0.09, 0.07, 0.07)
MUZZLE = (0.95, 0.90, 0.82)     # pale band across the muzzle
EAR_INNER = (0.88, 0.72, 0.62)
EYE = (0.03, 0.02, 0.02)
EYE_SHINE = (0.85, 0.85, 0.85)


# ---------------------------------------------------------------- shape helpers

def resample(sections, steps=3):
    """Catmull-Rom interpolation of (center, rx, rd) sections for a smoother loft."""
    vals = [(Vector(c), rx, rd) for c, rx, rd in sections]
    out = []
    for i in range(len(vals) - 1):
        ps = (vals[max(0, i - 1)], vals[i], vals[i + 1], vals[min(len(vals) - 1, i + 2)])
        for k in range(steps):
            t = k / steps
            w = (-0.5 * t ** 3 + t * t - 0.5 * t, 1.5 * t ** 3 - 2.5 * t * t + 1,
                 -1.5 * t ** 3 + 2 * t * t + 0.5 * t, 0.5 * t ** 3 - 0.5 * t * t)
            c = Vector((0, 0, 0))
            for wj, pj in zip(w, ps):
                c += pj[0] * wj
            out.append((c, sum(wj * pj[1] for wj, pj in zip(w, ps)), sum(wj * pj[2] for wj, pj in zip(w, ps))))
    out.append(vals[-1])
    return out


def loft(sections, sides=24):
    """Closed shell through (center, half_width_x, half_depth) sections along a path in the YZ plane."""
    bm = bmesh.new()
    sections = resample(sections)
    pts = [s[0] for s in sections]
    rings = []
    for i, (c, rx, rd) in enumerate(sections):
        fwd = (pts[min(len(pts) - 1, i + 1)] - pts[max(0, i - 1)]).normalized()
        side = Vector((1, 0, 0))
        up = side.cross(fwd).normalized()
        rings.append([bm.verts.new(c + side * math.cos(k / sides * math.tau) * rx + up * math.sin(k / sides * math.tau) * rd)
                      for k in range(sides)])
    for ra, rb in zip(rings, rings[1:]):
        for k in range(sides):
            j = (k + 1) % sides
            bm.faces.new([ra[k], ra[j], rb[j], rb[k]])
    for ring, end, prev in ((rings[0], pts[0], pts[1]), (rings[-1], pts[-1], pts[-2])):
        r = (ring[0].co - end).length
        pole = bm.verts.new(end + (end - prev).normalized() * r * 0.6)
        for k in range(sides):
            bm.faces.new([ring[k], ring[(k + 1) % sides], pole])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def oriented(center, radii, pitch=0.0, yaw=0.0, roll=0.0, segments=20, rings=14):
    """UV ellipsoid rotated about X (pitch), Y (roll) then Z (yaw), degrees, moved to center."""
    bm = nh.uv_ellipsoid((0, 0, 0), radii, segments=segments, rings=rings)
    rot = (Matrix.Rotation(math.radians(yaw), 4, "Z") @ Matrix.Rotation(math.radians(roll), 4, "Y")
           @ Matrix.Rotation(math.radians(pitch), 4, "X"))
    nh.transform(bm, rot)
    nh.transform(bm, Matrix.Translation(Vector(center)))
    return bm


def cup_ear(base, height, width, depth, tilt_x, splay):
    """Closed, cupped ear: a half-ellipsoid shell open toward -Y, solidified, then posed."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=12, radius=1.0)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.y < -0.15], context="VERTS")
    for v in bm.verts:
        z01 = (v.co.z + 1) * 0.5
        taper = 0.35 + 0.65 * math.sin(math.pi * min(1.0, z01 * 0.95 + 0.05)) ** 0.7  # pointed tip
        v.co = Vector((v.co.x * width * taper, v.co.y * depth, (v.co.z + 1) * 0.5 * height))
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.007)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    nh.transform(bm, Matrix.Rotation(math.radians(splay), 4, "Y") @ Matrix.Rotation(math.radians(tilt_x), 4, "X"))
    nh.transform(bm, Matrix.Translation(Vector(base)))
    return bm


def fur_displace(bm, amount=0.004, freq=38.0):
    bm.normal_update()
    for v in bm.verts:
        v.co += v.normal * noise.noise(v.co * freq) * amount


# ---------------------------------------------------------------- colours

def fur(co, n):
    c = nh.lerp(RED, RED_DARK, nh.smoothstep(0.3, 0.95, n.y * 0.7 + n.z * 0.4))
    return nh.lerp(c, RED, 0.3 * max(0.0, noise.noise(co * 10.0)))


def body_color(co, n):
    c = fur(co, n)
    if co.z > 1.0 and co.y < -0.08:  # head
        if co.y < -0.335:
            return NOSE
        c = nh.lerp(c, CREAM, nh.smoothstep(-0.2, -0.7, n.z))            # pale chin and lips
        # pale stripe from the mouth corner back along the side of the muzzle
        stripe = (nh.smoothstep(0.012, 0.0, abs(co.z - (1.092 + 0.25 * (co.y + 0.30))))
                  * nh.smoothstep(-0.31, -0.28, co.y) * nh.smoothstep(-0.15, -0.19, co.y)
                  * nh.smoothstep(0.35, 0.7, abs(n.x)))
        return nh.lerp(c, MUZZLE, 0.85 * stripe)
    front = nh.smoothstep(-0.15, -0.55, n.y) * nh.smoothstep(0.16, 0.30, co.z)
    return nh.lerp(c, CREAM, front)


def limb_fur(co, n):
    return nh.lerp(fur(co, n), CREAM, 0.55 * nh.smoothstep(-0.5, -0.9, n.z))


# ---------------------------------------------------------------- build

def build():
    body = nh.MeshBuilder()

    # Torso -> neck -> head -> muzzle as one lofted spine
    sections = [
        ((0, 0.10, 0.13), 0.10, 0.10),
        ((0, 0.08, 0.20), 0.170, 0.18),
        ((0, 0.05, 0.32), 0.205, 0.225),
        ((0, 0.02, 0.46), 0.195, 0.215),
        ((0, -0.01, 0.60), 0.170, 0.185),
        ((0, -0.035, 0.73), 0.140, 0.150),   # broad boomer chest/shoulders
        ((0, -0.055, 0.84), 0.100, 0.110),
        ((0, -0.07, 0.93), 0.074, 0.082),
        ((0, -0.085, 1.01), 0.066, 0.072),
        ((0, -0.105, 1.08), 0.074, 0.080),
        ((0, -0.135, 1.125), 0.080, 0.082),
        ((0, -0.18, 1.135), 0.070, 0.072),
        ((0, -0.235, 1.118), 0.054, 0.058),
        ((0, -0.29, 1.095), 0.041, 0.046),
        ((0, -0.335, 1.08), 0.030, 0.034),
    ]
    body.add(loft(sections), body_color)

    # Head sculpt: brow ridges, cheekbones, jaw, nose pad
    for sx in (-1, 1):
        body.add(oriented((sx * 0.045, -0.165, 1.185), (0.03, 0.045, 0.018), pitch=-8), fur)
        body.add(oriented((sx * 0.058, -0.19, 1.115), (0.026, 0.055, 0.03), pitch=-10, yaw=sx * 8), fur)
    body.add(oriented((0, -0.235, 1.078), (0.038, 0.075, 0.026), pitch=-12), CREAM)          # lower jaw / chin
    body.add(oriented((0, -0.338, 1.088), (0.03, 0.02, 0.026)), NOSE)                         # nose pad

    # Chest: pectorals and a deep breastbone
    for sx in (-1, 1):
        body.add(oriented((sx * 0.065, -0.10, 0.70), (0.075, 0.06, 0.085), pitch=-10), CREAM)

    # Muscular forearms: shoulder, bulging upper arm, forearm, wrist, paw and fingers
    for sx in (-1, 1):
        body.add(oriented((sx * 0.10, -0.07, 0.80), (0.06, 0.06, 0.07)), fur)                 # deltoid
        arm = nh.tube([(sx * 0.08, -0.08, 0.82), (sx * 0.12, -0.13, 0.76), (sx * 0.13, -0.17, 0.69),
                       (sx * 0.11, -0.23, 0.655), (sx * 0.09, -0.27, 0.64)],
                      [0.055, 0.05, 0.04, 0.032, 0.024], sides=14)
        body.add(arm, fur)
        body.add(oriented((sx * 0.125, -0.13, 0.75), (0.04, 0.05, 0.055), pitch=40), fur)    # biceps
        body.add(oriented((sx * 0.12, -0.21, 0.67), (0.034, 0.05, 0.03), pitch=-25), fur)    # forearm
        body.add(oriented((sx * 0.085, -0.285, 0.633), (0.026, 0.028, 0.022)), DARK)        # paw
        for f in (-1, 0, 1):
            base = Vector((sx * 0.085 + f * 0.013, -0.298, 0.628))
            tip = base + Vector((f * 0.004, -0.012, -0.03))
            body.add(nh.tube([base, (base + tip) / 2, tip], [0.009, 0.008, 0.006], sides=6), DARK)

    # Hind legs: powerful haunch + quad, knee, calf, defined heel, long foot with toes
    for sx in (-1, 1):
        x = sx * 0.135
        body.add(oriented((x * 0.92, 0.0, 0.25), (0.115, 0.24, 0.17), pitch=-22), limb_fur)       # haunch
        body.add(oriented((x * 1.02, -0.09, 0.22), (0.08, 0.10, 0.10), pitch=-30), limb_fur)      # quadriceps
        body.add(oriented((x * 1.05, -0.15, 0.20), (0.05, 0.04, 0.05)), fur)                       # knee
        body.add(nh.tube([(x, -0.14, 0.21), (x * 1.05, -0.05, 0.15), (x * 1.08, 0.08, 0.075), (x * 1.08, 0.15, 0.05)],
                         [0.07, 0.062, 0.045, 0.036], sides=14), fur)
        body.add(oriented((x * 1.08, -0.02, 0.13), (0.045, 0.07, 0.045), pitch=-35), fur)        # calf
        body.add(oriented((x * 1.08, 0.17, 0.05), (0.034, 0.042, 0.04)), RED_DARK)               # heel

        def foot_color(co, n):
            return nh.lerp(RED_DARK, DARK, nh.smoothstep(-0.14, -0.27, co.y))
        foot = nh.tube([(x * 1.08, 0.175, 0.035), (x * 1.06, 0.06, 0.032), (x * 1.02, -0.10, 0.03),
                        (x * 0.98, -0.24, 0.026), (x * 0.96, -0.30, 0.022)],
                       [0.034, 0.046, 0.046, 0.04, 0.03], sides=14, scale_xy=(1.0, 0.62))
        body.add(foot, foot_color)
        # big fourth toe and the smaller fifth toe beside it
        for dx, length, r in ((0.0, 0.07, 0.022), (sx * 0.026, 0.045, 0.015)):
            base = Vector((x * 0.96 + dx, -0.29, 0.022))
            body.add(nh.tube([base, base + Vector((0, -length * 0.6, -0.002)), base + Vector((0, -length, -0.004))],
                             [r, r * 0.9, r * 0.7], sides=8, scale_xy=(1.0, 0.7)), DARK)

    # Tail: thick muscular base, tapering, resting on the ground in a gentle curve
    tail = nh.tube([(0, 0.12, 0.30), (0, 0.27, 0.17), (0.01, 0.42, 0.08), (0.035, 0.60, 0.04),
                    (0.07, 0.78, 0.032), (0.09, 0.93, 0.04), (0.095, 1.02, 0.055), (0.095, 1.05, 0.06)],
                   [0.125, 0.10, 0.075, 0.056, 0.043, 0.03, 0.016, 0.006], sides=16)
    body.add(tail, limb_fur)

    fused = body.fuse(voxel=0.0075, smooth=4, smooth_factor=0.5, max_tris=15500)
    fur_displace(fused, amount=0.0035)

    mb = nh.MeshBuilder()
    mb.add(fused)

    # ---- crisp details
    for sx in (-1, 1):
        # eyes with a highlight, set high under the brow
        mb.add(nh.ellipsoid((sx * 0.064, -0.172, 1.163), (0.015, 0.02, 0.017), subdivisions=2), EYE)
        mb.add(nh.ellipsoid((sx * 0.072, -0.182, 1.170), (0.004, 0.004, 0.004), subdivisions=1), EYE_SHINE)
        # nostrils
        mb.add(oriented((sx * 0.012, -0.355, 1.088), (0.007, 0.004, 0.005), segments=8, rings=6), (0.02, 0.01, 0.01))
        # mouth line
        mb.add(nh.tube([(0, -0.338, 1.064), (sx * 0.02, -0.32, 1.063), (sx * 0.035, -0.29, 1.067), (sx * 0.045, -0.26, 1.075)],
                       [0.0035, 0.0035, 0.003, 0.0], sides=5), (0.05, 0.03, 0.03))

        def ear_color(co, n, sx=sx):
            inner = nh.smoothstep(-0.45, -0.8, n.y)
            c = nh.lerp(RED, EAR_INNER, inner)
            return nh.lerp(c, DARK, nh.smoothstep(1.34, 1.38, co.z))
        mb.add(cup_ear((sx * 0.042, -0.095, 1.16), 0.22, 0.042, 0.022, tilt_x=-6, splay=sx * 10), ear_color)

        # claws: on fingers and on the two big toes
        for f in (-1, 0, 1):
            tip = Vector((sx * 0.085 + f * 0.013 + f * 0.004, -0.31, 0.598))
            mb.add(nh.tube([tip, tip + Vector((0, -0.006, -0.012)), tip + Vector((0, -0.01, -0.022))],
                           [0.005, 0.004, 0.0], sides=5), CLAW)
        x = sx * 0.135
        for dx, length in ((0.0, 0.07), (sx * 0.026, 0.045)):
            tip = Vector((x * 0.96 + dx, -0.29 - length, 0.018))
            mb.add(nh.tube([tip, tip + Vector((0, -0.012, -0.006)), tip + Vector((0, -0.022, -0.016))],
                           [0.009, 0.006, 0.0], sides=6), CLAW)

    obj = mb.to_object("Kangaroo")
    nh.ground_to_zero(obj)
    return obj


def render_closeups(path, target, dist, views):
    scene = bpy.context.scene
    cam = scene.camera
    out = Path(path)
    for i, (az, el) in enumerate(views):
        a, e = math.radians(az), math.radians(el)
        cam.location = Vector(target) + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist
        cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = str(out.with_name(f"{out.stem}_head{i}.png"))
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    nh.run(build, "Kangaroo", ground=(0.55, 0.42, 0.25), views=((35, 25), (-90, 8), (20, 65), (200, 20)))
    if "--render" in sys.argv:
        obj = bpy.data.objects["Kangaroo"]
        zmax = max(v.co.z for v in obj.data.vertices)
        render_closeups(sys.argv[sys.argv.index("--render") + 1], (0, -0.2, zmax - 0.27), 0.75, ((30, 10), (-80, 5)))
