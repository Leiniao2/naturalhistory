"""
Shared pieces for the abalone models (haliotis_discus.py, haliotis_midae.py).

An abalone clinging to a low rock: a flattened, ear-shaped shell grown as a single huge
body whorl around a small, low spire set near the posterior right margin. The shell is
swept as a self-similar logarithmic spiral - every ring of the mesh is an earlier
position of the margin, scaled down and turned about the apex - so the rings double as
growth lines and anything placed at a fixed ring angle traces the spiral:

  * the selenizone: a raised keel spiralling out from the apex along the left side,
    carrying the row of respiratory holes (tremata). The newest few, toward the
    anterior margin, stay open (raised rims around dark holes); older ones are sealed
    into low bumps.
  * radial cords/ridges (rugose shells) run from the apex out to the margin and
    crinkle it into a wavy edge.

The outside is painted through the caller's palette with growth bands, a worn pinkish
spire and patches of encrusting coralline algae; the thick lip shows a sliver of nacre.
Under the shell sits the muscular foot, and around it the frilly epipodium: a wavy
skirt that pokes out past the shell rim, fringed with slender epipodial tentacles, plus
a pair of cephalic tentacles and the snout at the front.

Frame: anterior (head) toward -Y, the animal's left side is +X, Z up. Pivot at the base
of the rock (z = 0). Shell length 1.0 units.
"""

import math
import random

import bmesh
from mathutils import Matrix, Vector, noise

import nh_model as nh

ROCK_DARK = (0.30, 0.28, 0.26)
ROCK_LIGHT = (0.50, 0.47, 0.42)
CORALLINE = (0.78, 0.44, 0.54)
NACRE = (0.80, 0.84, 0.86)
NACRE_TINT = (0.62, 0.78, 0.76)
HOLE = (0.04, 0.03, 0.03)


def grid(rings, colors, wrap=True):
    """Open patch between successive rings (each a list of points; a ring of length 1 is a
    pole and is fanned). wrap: close each ring into a loop. colors: same shape, rgb."""
    bm = bmesh.new()
    col = bm.loops.layers.color.new("Col")
    verts = [[bm.verts.new(p) for p in ring] for ring in rings]

    def face(vs, cs):
        try:
            f = bm.faces.new(vs)
        except ValueError:
            return
        for loop, c in zip(f.loops, cs):
            loop[col] = (c[0], c[1], c[2], 1.0)

    for i in range(len(rings) - 1):
        a, b = verts[i], verts[i + 1]
        ca, cb = colors[i], colors[i + 1]
        n = len(b) if len(a) == 1 else len(a)
        last = n if wrap else n - 1
        for k in range(last):
            j = (k + 1) % n
            if len(a) == 1:
                face([a[0], b[k], b[j]], [ca[0], cb[k], cb[j]])
            elif len(b) == 1:
                face([a[k], a[j], b[0]], [ca[k], ca[j], cb[0]])
            else:
                face([a[k], a[j], b[j], b[k]], [ca[k], ca[j], cb[j], cb[k]])
    return bm


def _outline(a, half_w, half_l, ear):
    """Ear-shaped margin around the shell centre: an oval, a little straighter along the
    left (hole-bearing) side and narrower toward the posterior end."""
    x = half_w * math.cos(a)
    y = half_l * math.sin(a)
    if x > 0:
        x *= 1.0 - ear * 0.35 * (1.0 - abs(math.sin(a))) * 0.5   # straighter left side
    x *= 1.0 - ear * 0.18 * max(0.0, math.sin(a))                  # narrower posterior (+Y)
    return Vector((x, y, 0.0))


def build(name, *, seed=3, length=1.0, width=0.72, height=0.24, ear=0.5,
          apex=(-0.30, 0.66), spin=0.30, row_angle=-0.15, holes_open=5, holes_closed=6,
          hole_size=0.030, keel=0.035, radial_ridges=0, ridge_amp=0.0, ridge_wave=0.0,
          bumps=0.0, growth_amp=0.004, rough=0.006, encrust=0.25,
          shell=((0.40, 0.38, 0.22),), shell_dark=(0.25, 0.24, 0.14), spire=(0.62, 0.48, 0.44),
          foot=(0.12, 0.11, 0.09), epipodium=(0.18, 0.18, 0.13), tentacle=(0.30, 0.30, 0.22),
          tentacle_tip=(0.55, 0.55, 0.45), stripes=0.0, frills=26, tentacles=56,
          tentacle_len=0.09, foot_height=0.085, rock=True):
    """Builds the abalone and returns the object (not yet exported).

      width/height: shell width and dome height as fractions of the length.
      apex: spire position as fractions of the half-width (x, + = left) and half-length
        (y, + = posterior).
      spin: how far the growth spiral turns per e-fold of growth (radians).
      row_angle: direction (radians, in the outline's angle) where the hole row meets the
        anterior-left margin.
      radial_ridges/ridge_amp/ridge_wave: number, height and waviness of the radial ridges.
      bumps: knobbliness where the ridges cross growth undulations (rugose shells).
      shell: one or more base colours blended in noisy patches; shell_dark: growth bands.
      stripes: 0..1 dark/pale banding on the epipodial tentacles."""
    rng = random.Random(seed)
    hl, hw = length * 0.5, length * width * 0.5
    H = length * height
    ap = Vector((apex[0] * hw, apex[1] * hl, 0.0))
    seed_v = Vector((rng.random() * 40, rng.random() * 40, rng.random() * 40))
    base_z = foot_height + (0.05 if rock else 0.0)   # shell margin height above z = 0
    rock_top = 0.05 if rock else 0.0
    n_a, n_t = 68, 19
    angles = [row_angle + k / n_a * math.tau for k in range(n_a)]  # ring index 0 = hole row

    def spiral_point(t, a):
        """Margin point at angle a, at growth stage t (0 = apex .. 1 = today's margin)."""
        rel = _outline(a, hw, hl, ear) - ap
        rot = Matrix.Rotation(-spin * math.log(max(t, 1e-4)), 3, "Z")
        return ap + (rot @ rel) * t

    def ang_from_row(a):
        d = (a - row_angle) % math.tau
        return d if d < math.pi else d - math.tau

    def height_at(t, a, p):
        # broad, flat-topped body whorl, highest toward the spire, rolling down to the margin
        z = H * max(0.0, 1.0 - t ** 2.5) ** 0.6 * (0.92 + 0.08 * math.cos(ang_from_row(a) * 0.5))
        z += H * 0.10 * math.exp(-(t / 0.12) ** 2)                      # low spire
        # selenizone keel, with a steeper flank outside it
        g = ang_from_row(a)
        z += keel * length * t * math.exp(-(g / 0.16) ** 2) * nh.smoothstep(0.05, 0.4, t)
        z -= keel * 0.8 * length * t * nh.smoothstep(0.05, 0.5, g) * (1 - nh.smoothstep(0.5, 1.2, g)) * t
        return z

    def relief(t, a, p):
        """Radial ridges, growth undulations and roughness (displacement along z)."""
        lt = math.log(max(t, 1e-3))
        r = 0.0
        if radial_ridges:
            ph = a * radial_ridges + ridge_wave * math.sin(lt * 5.0 + a * 3.0)
            ridge = 0.5 + 0.5 * math.cos(ph)
            growth = 0.5 + 0.5 * math.cos(lt * 11.0 + 0.8 * math.sin(a * 5))
            r += length * t * ridge_amp * (ridge ** 1.5) * (1.0 - bumps + bumps * growth * 2.0)
        r += growth_amp * length * t * math.sin(lt * 34.0) ** 8
        r += rough * length * noise.noise(p * 14.0 + seed_v) * nh.smoothstep(0.0, 0.3, t)
        return r

    def shell_col(t, a, p, z_rel):
        lt = math.log(max(t, 1e-3))
        k = 0.5 + 0.5 * noise.noise(p * 3.0 + seed_v)
        c = shell[0]
        for extra in shell[1:]:
            c = nh.lerp(c, extra, nh.smoothstep(0.35, 0.75, noise.noise(p * 2.2 + seed_v * 1.7 + Vector((len(c), 0, 0))) * 0.5 + 0.5))
        c = tuple(x * (0.85 + 0.3 * k) for x in c)
        band = 0.5 + 0.5 * math.sin(lt * 9.0 + 0.6 * math.sin(a * 2))
        c = nh.lerp(c, shell_dark, nh.smoothstep(0.55, 0.95, band) * 0.6)
        if radial_ridges:   # ridge crests worn paler, troughs darker
            ph = a * radial_ridges + ridge_wave * math.sin(lt * 5.0 + a * 3.0)
            c = nh.lerp(c, shell_dark, (0.5 - 0.5 * math.cos(ph)) * 0.35 * nh.smoothstep(0.2, 0.5, t))
        c = nh.lerp(spire, c, nh.smoothstep(0.06, 0.22, t))           # eroded spire
        e = noise.noise(p * 4.5 + seed_v * 2.3)
        if e > 0.62 - encrust * 0.6:
            c = nh.lerp(c, CORALLINE, min(1.0, (e - (0.62 - encrust * 0.6)) * 4.0) * 0.85)
        if noise.noise(p * 11.0 + seed_v * 0.7) > 0.55:              # tiny pale encrusters
            c = nh.lerp(c, (0.82, 0.80, 0.72), 0.6)
        return c

    # ---------------- shell surface (apex pole + rings out to the margin), then the lip
    rings, cols = [], []
    ts = [0.0] + [0.03 + 0.97 * (i / n_t) ** 1.25 for i in range(1, n_t + 1)]
    for t in ts:
        if t == 0.0:
            p = ap.copy()
            p.z = base_z + height_at(0.0, 0.0, p)
            rings.append([p])
            cols.append([spire])
            continue
        ring, rc = [], []
        for a in angles:
            p = spiral_point(t, a)
            # crinkle the margin with the radial ridges
            p.z = base_z + height_at(t, a, p) + relief(t, a, p)
            ring.append(p)
            rc.append(shell_col(t, a, p, p.z - base_z))
        rings.append(ring)
        cols.append(rc)
    margin = rings[-1]
    centre = sum((Vector((p.x, p.y, 0)) for p in margin), Vector()) / len(margin)
    lip_out, lip_in, lip_c1, lip_c2 = [], [], [], []
    for p in margin:
        q = Vector((p.x, p.y, 0.0))
        d = (q - centre)
        lip_out.append(Vector((q.x + d.normalized().x * 0.004, q.y + d.normalized().y * 0.004, p.z - 0.022 * length)))
        lip_in.append(Vector((centre.x + d.x * 0.93, centre.y + d.y * 0.93, p.z - 0.03 * length)))
        lip_c1.append(nh.lerp(shell[0], shell_dark, 0.5))
        lip_c2.append(NACRE if noise.noise(q * 9) < 0.2 else NACRE_TINT)
    rings += [lip_out, lip_in]
    cols += [lip_c1, lip_c2]
    mb = nh.MeshBuilder()
    sh = grid(rings, cols)
    bmesh.ops.recalc_face_normals(sh, faces=sh.faces)
    mb.add(sh)

    # ---------------- tremata along the spiral keel (newest at the margin)
    n_holes = holes_open + holes_closed
    t_k = 0.97
    for k in range(n_holes):
        if t_k < 0.12:
            break
        p = spiral_point(t_k, row_angle)
        p.z = base_z + height_at(t_k, row_angle, p) + relief(t_k, row_angle, p)
        r = hole_size * length * (0.55 + 0.45 * t_k)
        if k < holes_open:
            # raised rim (a short cone frustum) around a dark open hole
            rim = nh.tube([p - Vector((0, 0, r * 0.5)), p + Vector((0, 0, r * 0.45)), p + Vector((0, 0, r * 0.5))],
                          [r * 1.6, r * 1.05, r * 0.85], sides=8, cap_start=False, cap_end=False)
            mb.add(rim, nh.lerp(shell[0], shell_dark, 0.3))
            hole = nh.ellipsoid(tuple(p + Vector((0, 0, r * 0.3))), (r * 0.9, r * 0.9, r * 0.08), subdivisions=1)
            mb.add(hole, HOLE)
        else:
            mb.add(nh.ellipsoid(tuple(p + Vector((0, 0, r * 0.05))), (r * 1.2, r * 1.2, r * 0.45), subdivisions=1),
                   nh.lerp(shell[0], spire, 0.35))
        t_k *= 0.9 - 0.25 / n_holes

    # ---------------- foot, epipodium skirt with frills, epipodial and cephalic tentacles
    foot_bm = nh.ellipsoid((centre.x, centre.y, rock_top + foot_height * 0.55),
                           (hw * 0.82, hl * 0.84, foot_height * 0.75), subdivisions=3)
    for v in foot_bm.verts:
        v.co.z = max(v.co.z, rock_top + 0.004)
    mb.add(foot_bm, lambda co, n: nh.lerp(foot, (0.30, 0.27, 0.20), 0.25 + 0.25 * noise.noise(co * 18)))

    sk_rings, sk_cols = [], []
    n_s = 120
    cross = 5
    edge_pts = []
    for k in range(n_s):
        a = row_angle + k / n_s * math.tau
        m = _outline(a, hw, hl, ear)
        frill = 0.5 + 0.5 * math.sin(a * frills + 1.3 * math.sin(a * 3))
        out = 1.035 + 0.035 * frill
        z = rock_top + foot_height * (0.62 + 0.25 * frill)
        p_out = centre + (m - centre) * out
        p_in = centre + (m - centre) * 0.9
        ring, rc = [], []
        for j in range(cross):
            ph = j / cross * math.tau
            w = 0.5 + 0.5 * math.cos(ph)                 # 1 = outer edge
            q = p_in.lerp(p_out, w)
            q.z = z + math.sin(ph) * foot_height * 0.16 - w * foot_height * 0.15 * frill
            ring.append(q)
            rc.append(nh.lerp(epipodium, tentacle, 0.3 * w * frill))
        sk_rings.append(ring)
        sk_cols.append(rc)
        edge_pts.append((p_out, z - foot_height * 0.15 * frill, m - centre))
    sk_rings.append(sk_rings[0])
    sk_cols.append(sk_cols[0])
    skirt = grid(sk_rings, sk_cols)
    bmesh.ops.remove_doubles(skirt, verts=skirt.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(skirt, faces=skirt.faces)
    mb.add(skirt)

    for k in range(tentacles):
        p_out, z, outward = edge_pts[(k * n_s) // tentacles + rng.randrange(0, 2)]
        d = Vector((outward.x, outward.y, 0)).normalized()
        side = Vector((-d.y, d.x, 0))
        base = Vector((p_out.x, p_out.y, z)) - d * 0.01
        L = tentacle_len * length * rng.uniform(0.6, 1.2)
        lift = rng.uniform(-0.3, 0.5)
        sway = rng.uniform(-0.7, 0.7)
        pts = [base]
        for s in range(1, 4):
            f = s / 3
            pts.append(pts[-1] + (d + side * sway * f * f * 2 + Vector((0, 0, lift - 0.9 * f))).normalized() * (L / 3))
        rad = 0.011 * length * rng.uniform(0.8, 1.2)
        tb = nh.tube(pts, [rad, rad * 0.8, rad * 0.55, 0.0], sides=4, cap_start=False)

        def tcol(co, n, b=base, L=L):
            f = min(1.0, (co - b).length / L)
            c = nh.lerp(tentacle, tentacle_tip, f)
            if stripes and math.sin(f * 18.0) > 0.3:
                c = nh.lerp(c, epipodium, stripes)
            return c
        mb.add(tb, tcol)

    # head at the anterior margin: snout and two longer cephalic tentacles
    front = _outline(-math.pi / 2, hw, hl, ear)
    head = Vector((front.x * 0.2, front.y * 0.98, rock_top + foot_height * 0.55))
    mb.add(nh.ellipsoid(tuple(head), (0.07 * length, 0.05 * length, foot_height * 0.4), subdivisions=2), foot)
    for sx in (-1, 1):
        b = head + Vector((sx * 0.035 * length, -0.02 * length, foot_height * 0.15))
        pts = [b, b + Vector((sx * 0.03, -0.06, 0.02)) * length, b + Vector((sx * 0.07, -0.12, 0.015)) * length]
        mb.add(nh.tube(pts, [0.011 * length, 0.008 * length, 0.0], sides=5, cap_start=False), tentacle)

    # ---------------- rock slab with coralline crust
    if rock:
        def rock_deform(n):
            return 1.0 + noise.noise(n * 2.0 + seed_v) * 0.18

        rk = nh.ellipsoid((centre.x, centre.y, 0.0), (hw * 1.3, hl * 1.18, 0.1), subdivisions=2, deform=rock_deform)
        for v in rk.verts:
            v.co.z = min(max(v.co.z, -0.02), rock_top + 0.006 * noise.noise(v.co * 9))

        def rock_col(co, n):
            c = nh.lerp(ROCK_DARK, ROCK_LIGHT, 0.5 + 0.5 * noise.noise(co * 6.0 + seed_v))
            crust = noise.noise(co * 3.1 + seed_v * 1.3)
            if crust > 0.05 and n.z > 0.2:
                c = nh.lerp(c, CORALLINE, min(1.0, (crust - 0.05) * 3.0))
            return c
        mb.add(rk, rock_col, smooth=False)

    obj = mb.to_object(name, roughness=0.8)
    nh.ground_to_zero(obj)
    return obj
