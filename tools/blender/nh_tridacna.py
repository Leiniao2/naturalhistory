"""
Shared pieces for the giant clam models (tridacna_gigas.py, tridacna_maxima.py,
tridacna_tevoroa.py, tridacna_crocea.py).

A giant clam lies hinge-down, gaping upward, the way tridacnids live with their
sunlit mantle - and the photosynthetic zooxanthellae it farms - turned to the light:

  * two heavy valves fanned out from the umbones at the bottom. Their radial ribs are
    folds of the whole shell, and the ribs of one valve sit opposite the furrows of the
    other, so the gaping commissure along the top zig-zags and the margin is scalloped
    into rounded lobes. Options: rounded or close-set ribs, fine radial riblets, rows of
    upturned fluted scales (separate crisp flaps) on the rib crests, an asymmetric,
    elongate outline, a thin or thick lip.
  * the fleshy siphonal mantle bulging out of the gape and, in some species, draped
    over the shell edge: two lobes with a groove down the middle, a wavy margin set with
    small eye spots (hyaline organs), a raised exhalant siphon near one end and the
    slit-like inhalant aperture in the middle; painted with spots, streaks or mottled
    patches through the caller's palette.
  * a seat: rubble on sand, or a lump of coral rock the clam is partly or wholly bored
    into (embed = how much of the shell height the rock hides).

Frame: the long (anterior-posterior) axis along X, valves on -Y (facing the viewer)
and +Y, gape up (+Z). Pivot at the base (z = 0).
"""

import math
import random

import bmesh
from mathutils import Vector, noise

import nh_model as nh
import nh_coral as nc

HOLE = (0.05, 0.04, 0.05)
ROCK_COLS = ((0.62, 0.58, 0.48), (0.54, 0.50, 0.42), (0.70, 0.66, 0.56))   # pale reef rock
CORALLINE = (0.76, 0.44, 0.54)
TURF = (0.34, 0.38, 0.22)


def grid(rings, colors, wrap=False):
    """Patch between successive rows of points (a row of length 1 is a pole, fanned).
    wrap: close each row into a loop. colors: same shape, rgb."""
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
        for k in range(n if wrap else n - 1):
            j = (k + 1) % n
            if len(a) == 1:
                face([a[0], b[k], b[j]], [ca[0], cb[k], cb[j]])
            elif len(b) == 1:
                face([a[k], a[j], b[0]], [ca[k], ca[j], cb[0]])
            else:
                face([a[k], a[j], b[j], b[k]], [ca[k], ca[j], cb[j], cb[k]])
    return bm


def orient(bm, want):
    """Flip every face if the faces on average point away from the direction fn(face) -> Vector."""
    bm.normal_update()
    s = sum(f.normal.dot(want(f)) * f.calc_area() for f in bm.faces)
    if s < 0:
        bmesh.ops.reverse_faces(bm, faces=list(bm.faces))
    return bm


def build(name, *, seed=1, length=1.4, height=0.9, inflation=0.36, spread=1.85,
          centre=(0.0, 0.40), asym=0.0, tri=0.0, ribs=5, rib_amp=0.10, rib_sharp=0.8,
          scallop=0.10, fine=0, fine_amp=0.0, scale_rows=0, scale_len=0.05, scale_from=0.45,
          gape=0.05, lip=0.04, n_theta=96, n_u=24,
          shell=(0.80, 0.78, 0.70), shell_dark=(0.55, 0.53, 0.46), fouling=(0.40, 0.40, 0.28),
          foul=0.4, scale_col=None,
          mantle=(0.45, 0.38, 0.16), mantle2=(0.30, 0.34, 0.16), pattern="spots",
          pattern_col=(0.20, 0.75, 0.70), pattern_scale=9.0, pattern_amt=0.5,
          edge_col=(0.20, 0.55, 0.60), edge_width=0.15, eye_col=(0.25, 0.85, 0.80), eyes=50,
          over=0.04, droop=0.02, bulge=0.06, ruffle=0.02, mantle_frac=0.82, n_w=16, mantle_smooth=0.3,
          siphon_col=None, seat="rubble", embed=0.0, rock_size=1.0, rock_round=3.5):
    """Builds the clam and returns the object (not yet exported).

      height: umbo-to-margin height; inflation: half thickness of the closed shell.
      spread: half the fan angle of the valve (radians, ~1.6-1.9).
      centre: centre of the elliptical outline as fractions of (length/2, height); the umbo
        sits at the origin, so a low centre gives a fan, a high one a rounded oval.
      asym: shifts the outline toward +X (umbones off-centre, one end drawn out).
      tri: narrows the top of the outline toward a rounded triangle.
      ribs/rib_amp/rib_sharp: number of ribs, fold depth and profile (1 = sine, <1 = boxy).
      scallop: how far each rib crest lobes out at the margin (fraction of height).
      fine/fine_amp: radial riblets per rib and their height.
      scale_rows/scale_len/scale_from: fluted scale flaps per rib crest, size, first row (u).
      gape: half-width of the opening at the middle of the margin; lip: shell thickness.
      mantle..pattern_amt: mantle palette; pattern is "spots", "streaks" or "mottle".
      over/droop: how far the mantle edge reaches out over the shell margin and hangs down.
      mantle_smooth: 0 = the mantle edge follows the zig-zag margin, 1 = it runs smoothly
        over the rib lobes (species whose mantle spreads over the shell edge).
      seat: "rubble" (on sand) or "rock" (bored into a coral lump; embed 0..1 of the height);
        rock_size scales the lump, rock_round sets its profile (low = domed, high = flat-topped)."""
    rng = random.Random(seed)
    sv = Vector((rng.random() * 30, rng.random() * 30, rng.random() * 30))
    hl = length * 0.5
    cx, cz = centre[0] * hl + asym * hl, centre[1] * height
    ax, az = hl, height - cz
    T = spread

    def fold(th):
        """Rib fold -1..1 at fan angle th (crests of valve +Y where > 0)."""
        c = math.cos(ribs * math.pi * th / T)
        f = math.copysign(abs(c) ** rib_sharp, c)
        return f * (1.0 - (abs(th) / T) ** 6)

    def outline(th):
        """Distance from the umbo to the elliptical margin along fan angle th."""
        dx, dz = math.sin(th), math.cos(th)
        # narrow the top for a triangular outline
        sx = ax * (1.0 - tri * 0.45 * max(0.0, dz))
        # ray / ellipse intersection, ellipse centred (cx, cz) with radii (sx, az)
        a = (dx / sx) ** 2 + (dz / az) ** 2
        b = -2 * (cx * dx / sx ** 2 + cz * dz / az ** 2)
        c = (cx / sx) ** 2 + (cz / az) ** 2 - 1
        return (-b + math.sqrt(max(0.0, b * b - 4 * a * c))) / (2 * a)

    def end_fac(th):
        return max(0.0, 1.0 - (abs(th) / T) ** 3) ** 0.6

    def gape_at(th):
        return gape * max(0.0, 1.0 - (abs(th) / (T * mantle_frac)) ** 2.5)

    def valve_point(s, u, th, inner=False):
        f = fold(th)
        rho = outline(th) * (1.0 + scallop * height / max(outline(th), 1e-3) * 0.5 * max(0.0, s * f) ** 1.3
                             - scallop * 0.15 * max(0.0, -s * f))
        r = rho * u
        x, z = math.sin(th) * r, math.cos(th) * r
        infl = (u ** 0.55) * (1.0 - u ** 2.2) ** 0.75 * 1.55 * end_fac(th)
        y = s * (gape_at(th) * u ** 3 + inflation * infl) + rib_amp * f * u ** 1.1 * height
        if fine:
            y += s * fine_amp * height * u * max(0.0, math.cos(ribs * fine * math.pi * th / T)) ** 2
        if inner:
            y -= s * lip * (0.4 + 0.6 * u)
            z -= lip * 0.3
        return Vector((x, y, z))

    def shell_paint(s, u, th, p):
        f = s * fold(th)
        c = nh.lerp(shell_dark, shell, 0.5 + 0.5 * f)
        k = 0.88 + 0.24 * noise.noise(p * 7.0 + sv)
        c = tuple(min(1.0, x * k) for x in c)
        # fouling (turf algae, sediment) creeping up from the base and along the furrows
        fz = nh.smoothstep(0.55, 0.0, u) + 0.35 * (1 - f) * 0.5
        fz = min(1.0, fz * foul * (0.7 + 0.6 * (0.5 + 0.5 * noise.noise(p * 4.0 + sv))))
        c = nh.lerp(c, fouling, fz)
        if noise.noise(p * 5.0 + sv * 1.7) > 0.45:
            c = nh.lerp(c, CORALLINE, 0.5)
        # growth lines
        g = 0.5 + 0.5 * math.sin(u * 60.0 + 2 * noise.noise(p * 3))
        return tuple(x * (0.94 + 0.08 * g) for x in c)

    mb = nh.MeshBuilder()
    ths = [-T + 2 * T * i / (n_theta - 1) for i in range(n_theta)]
    us = [(i / n_u) ** 0.85 for i in range(1, n_u + 1)]
    margins = {}
    for s in (-1, 1):
        rings, cols = [[Vector((0, s * 0.002, 0))]], [[shell_dark]]
        for u in us:
            row = [valve_point(s, u, th) for th in ths]
            rings.append(row)
            cols.append([shell_paint(s, u, th, p) for th, p in zip(ths, row)])
        margins[s] = rings[-1]
        lip_row = [valve_point(s, 1.0, th, inner=True) for th in ths]
        rings.append(lip_row)
        cols.append([nh.lerp(shell, (0.95, 0.94, 0.90), 0.6)] * n_theta)
        for u in reversed(us[:-1:3]):
            rings.append([valve_point(s, u, th, inner=True) for th in ths])
            cols.append([(0.92, 0.91, 0.86)] * n_theta)
        rings.append([Vector((0, 0, lip * 0.5))])
        cols.append([(0.92, 0.91, 0.86)])
        v = grid(rings, cols)
        bmesh.ops.recalc_face_normals(v, faces=v.faces)   # outer + inner surface: nearly closed
        mb.add(v)

    # ---------------- fluted scales on the rib crests
    if scale_rows:
        sc_col = scale_col or nh.lerp(shell, (1, 1, 1), 0.3)
        for s in (-1, 1):
            for k in range(-ribs, ribs + 1):
                th = T * k / ribs
                if abs(th) > T * 0.9 or s * fold(th) < 0.5:
                    continue
                for j in range(scale_rows):
                    u = scale_from + (0.97 - scale_from) * (j / max(1, scale_rows - 1)) ** 0.8
                    width = T / ribs * 0.7
                    size = scale_len * height * (0.45 + 0.55 * u)
                    rows = []
                    for layer, (along, out) in enumerate(((0.0, 0.0), (0.55, 0.22), (1.0, 0.5))):
                        row = []
                        for q in (-1.0, -0.4, 0.4, 1.0):
                            tq = th + q * width
                            p = valve_point(s, u, tq)
                            p2 = valve_point(s, min(1.0, u + 0.03), tq)
                            tang = (p2 - p).normalized()
                            nrm = Vector((0, s, 0))
                            curl = 1.0 - 0.6 * q * q     # flap curled into a gutter, middle standing out most
                            row.append(p + tang * size * along + nrm * size * out * curl)
                        rows.append(row)
                    back = [[p - Vector((0, s * 0.006, 0)) + Vector((0, 0, -0.004)) for p in r] for r in reversed(rows)]
                    flap = grid(rows + back, [[sc_col] * 4] * 6)
                    mb.add(flap)

    # ---------------- mantle
    paint_rng = random.Random(seed + 7)
    Tm = T * mantle_frac
    n_m = int(n_theta * mantle_frac * 1.1)
    mths = [-Tm + 2 * Tm * i / (n_m - 1) for i in range(n_m)]
    ws = [-1 + 2 * i / (n_w - 1) for i in range(n_w)]

    def margin_pt(s, th):
        """Margin point under the mantle edge, smoothed over one rib period."""
        raw = valve_point(s, 1.0, th)
        if mantle_smooth <= 0:
            return raw
        win = T / ribs
        pts = [valve_point(s, 1.0, th + win * (k / 6.0)) for k in range(-6, 7)]
        # envelope: as far out and as high as the rib lobes nearby, so none poke through
        env = Vector((raw.x, max((p.y * s for p in pts)) * s, max(p.z for p in pts)))
        return raw.lerp(env, mantle_smooth)

    def mantle_paint(th, w, p, edge):
        c = nh.lerp(mantle, mantle2, 0.5 + 0.5 * noise.noise(p * 4.0 + sv * 2))
        if pattern == "spots":
            d = noise.voronoi(p * pattern_scale + sv, distance_metric="DISTANCE")[0][0]
            c = nh.lerp(c, pattern_col, nh.smoothstep(0.42, 0.25, d) * pattern_amt)
        elif pattern == "streaks":
            # wavy lines running out from the midline toward the edge, plus scattered dots
            ph = th * pattern_scale * 6 + 1.5 * math.sin(w * 4 + th * 3) + noise.noise(p * 5.0) * 1.2
            c = nh.lerp(c, pattern_col, nh.smoothstep(0.55, 0.85, math.sin(ph)) * pattern_amt)
            d = noise.voronoi(p * pattern_scale * 1.6 + sv, distance_metric="DISTANCE")[0][0]
            c = nh.lerp(c, mantle2, nh.smoothstep(0.35, 0.2, d) * 0.6)
        elif pattern == "mottle":
            m = noise.noise(p * pattern_scale + sv * 3) + 0.4 * noise.noise(p * pattern_scale * 2.7)
            c = nh.lerp(c, pattern_col, nh.smoothstep(0.05, 0.45, m) * pattern_amt)
        # coloured band along the mantle edge
        c = nh.lerp(c, edge_col, nh.smoothstep(1.0 - edge_width - 0.08, 1.0 - edge_width, abs(w)) * 0.85)
        return c

    top_pts = {}
    rings, cols = [], []
    def drape_pt(s, th, depth):
        """Where a mantle edge hanging `depth` below the margin rests on the shell: the outer
        envelope of the valve surface there (so rib lobes never poke through)."""
        u_d = max(0.55, min(0.995, 1.0 - depth / height))
        win = T / ribs
        pts = [valve_point(s, u_d, th + win * (k / 6.0)) for k in range(-6, 7)]
        raw = valve_point(s, u_d, th)
        env = Vector((raw.x, max(p.y * s for p in pts) * s, raw.z))
        return (raw + Vector((0, s * 0.01, 0))).lerp(env, min(1.0, mantle_smooth * 2.0))

    for i, th in enumerate(mths):
        endf = max(0.0, 1.0 - (abs(th) / Tm) ** 2.2) ** 0.5
        mL, mR = margin_pt(-1, th), margin_pt(1, th)
        wave = math.sin(th * 11.0 + 1.3 * math.sin(th * 4.0))       # broad lobes of the mantle edge
        ov = (over + 0.015) * endf * (1.0 + 0.15 * wave)
        dr = droop * endf * (1.0 + 0.2 * wave)
        dL, dR = drape_pt(-1, th, dr), drape_pt(1, th, dr)
        row, rc = [], []
        for w in ws:
            t = (w + 1) * 0.5
            p = mL.lerp(mR, t)
            q = nh.smoothstep(0.7, 1.0, abs(w))          # 0 over the gape .. 1 at the edge
            if q > 0:
                m, d, sd = (mR, dR, 1) if w > 0 else (mL, dL, -1)
                core = mL.lerp(mR, 0.5 + 0.5 * math.copysign(0.7, w))
                rim = core.lerp(m, min(1.0, q * 1.6))
                p = rim.lerp(d, q ** 1.6)
                p.y += sd * (0.01 + ov * q ** 1.2)       # roll out over the lip
                p.z += 0.025 * height * math.sin(math.pi * min(1.0, q * 1.3)) * endf
            p.z += 0.012 + bulge * height * endf * (1 - min(1.0, abs(w) / 0.85) ** 2) ** 0.7
            p.z -= 0.022 * height * endf * math.exp(-(w / 0.13) ** 2)      # groove between the lobes
            p.z += ruffle * height * endf * math.sin(th * 17.0 + w * 3) * abs(w) ** 1.5
            row.append(p)
            rc.append(mantle_paint(th, w, p, abs(w)))
            top_pts[(i, round(w, 4))] = p
        # underside back to the start (inside the shell), closing the loop
        for w in (1.0, 0.4, -0.4, -1.0):
            if abs(w) == 1.0:
                p = row[-1 if w > 0 else 0].copy() + Vector((0, -w * 0.006, -0.014))   # thin edge
            else:
                p = mL.lerp(mR, (w + 1) * 0.5)
                p.z += -0.02 - 0.08 * height
            row.append(p)
            rc.append(nh.lerp(mantle2, (0.1, 0.1, 0.1), 0.3))
        rings.append(row)
        cols.append(rc)
    mbm = grid(rings, cols, wrap=True)
    bmesh.ops.recalc_face_normals(mbm, faces=mbm.faces)
    mb.add(mbm)

    def mantle_at(th, w):
        i = min(range(n_m), key=lambda k: abs(mths[k] - th))
        wk = min(ws, key=lambda x: abs(x - w))
        return top_pts[(i, round(wk, 4))]

    # eye spots (hyaline organs) along both mantle edges
    for k in range(eyes):
        th = -Tm * 0.92 + 1.84 * Tm * (k // 2) / max(1, eyes // 2 - 1) + paint_rng.uniform(-0.01, 0.01)
        w = 0.86 if k % 2 else -0.86
        p = mantle_at(th, w)
        r = 0.010 * height * paint_rng.uniform(0.8, 1.2)
        mb.add(nh.ellipsoid(tuple(p + Vector((0, 0, r * 0.3))), (r, r, r * 0.6), subdivisions=0), eye_col, smooth=False)

    # exhalant siphon: a short raised chimney near one end
    sc = siphon_col or nh.lerp(mantle, mantle2, 0.5)
    base = mantle_at(Tm * 0.55, 0.0)
    rs = 0.05 * height
    chim = nh.tube([base - Vector((0, 0, rs * 0.5)), base + Vector((0, 0, rs * 0.8)), base + Vector((0, 0, rs * 1.2))],
                   [rs * 1.5, rs * 1.0, rs * 0.75], sides=10, cap_start=False, cap_end=False)
    mb.add(chim, sc)
    mb.add(nh.ellipsoid(tuple(base + Vector((0, 0, rs * 1.05))), (rs * 0.7, rs * 0.7, rs * 0.12), subdivisions=1), HOLE)
    # inhalant aperture: a long dark slit along the midline, fringed with tiny papillae
    a0, a1 = -Tm * 0.35, Tm * 0.05
    for k in range(6):
        th = a0 + (a1 - a0) * k / 5
        p = mantle_at(th, 0.0)
        w = 0.035 * height * math.sin(math.pi * (k + 0.5) / 6) ** 0.7
        mb.add(nh.ellipsoid(tuple(p + Vector((0, 0, 0.004))), (0.075 * height, w, 0.008), subdivisions=1), HOLE)
        for sd in (-1, 1):
            q = p + Vector((0, sd * (w + 0.008), 0.006))
            mb.add(nh.ellipsoid(tuple(q), (0.009, 0.009, 0.012), subdivisions=0), nh.lerp(mantle, (1, 1, 0.9), 0.4))

    # ---------------- seat
    if seat == "rubble":
        nc.rubble(mb, rng, hl * 0.95, hl * 1.35, count=9, size=(0.05 * length, 0.09 * length))
    elif seat == "rock":
        top = embed * height
        n_r, n_a = 14, 56
        rx, ry = hl * 1.18 * rock_size, max(inflation * 2.3, hl * 0.9) * rock_size
        rings, cols = [[Vector((0, 0, top + 0.01))]], [[ROCK_COLS[0]]]
        for i in range(1, n_r + 1):
            rr = i / n_r
            row, rc = [], []
            for j in range(n_a):
                a = j / n_a * math.tau
                bump = 1.0 + 0.12 * noise.noise(Vector((math.cos(a), math.sin(a), 0)) * 1.6 + sv)
                p = Vector((math.cos(a) * rx * rr * bump, math.sin(a) * ry * rr * bump, 0.0))
                h = top * max(0.0, 1.0 - rr ** rock_round) ** 0.4 if i < n_r else -0.01
                h += 0.05 * height * noise.noise(p * 3.5 + sv) * (1 - rr ** 4)
                p.z = h
                row.append(p)
                k = 0.5 + 0.5 * noise.noise(p * 6 + sv)
                c = nh.lerp(ROCK_COLS[1], ROCK_COLS[2], k)
                cr = noise.noise(p * 7.0 + sv * 1.3)
                if cr > 0.25:
                    c = nh.lerp(c, CORALLINE, min(1.0, (cr - 0.25) * 4) * 0.8)
                elif cr < -0.3:
                    c = nh.lerp(c, TURF, min(1.0, (-0.3 - cr) * 4) * 0.7)
                rc.append(c)
            rings.append(row)
            cols.append(rc)
        rock = grid(rings, cols, wrap=True)
        orient(rock, lambda f: Vector((0, 0, 1)))
        mb.add(rock, smooth=True)
        # a few coral knobs and polyp bumps on the rock
        for _ in range(6):
            a = rng.uniform(0, math.tau)
            rr = rng.uniform(0.65, 0.92)
            p = Vector((math.cos(a) * rx * rr, math.sin(a) * ry * rr, 0))
            p.z = top * max(0.0, 1.0 - rr ** rock_round) ** 0.4
            s = rng.uniform(0.03, 0.07) * length
            mb.add(nh.ellipsoid(tuple(p), (s, s * 0.9, s * 0.6), subdivisions=1,
                                deform=lambda n: 1.0 + 0.2 * noise.noise(n * 3 + sv)),
                   rng.choice(((0.72, 0.62, 0.42), (0.62, 0.50, 0.58), (0.50, 0.55, 0.38))), smooth=False)

    obj = mb.to_object(name, roughness=0.6)
    nh.ground_to_zero(obj)
    return obj
