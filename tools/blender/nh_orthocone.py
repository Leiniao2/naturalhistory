"""
Shared pieces for the straight-shelled nautiloid models (orthoceras_regulare.py,
cameroceras_trentonense.py).

  * conch(): a straight, tapering orthocone along +Y (aperture at the front, apex at
    the back), swept ring by ring so every vertex can carry its own colour. Alternate
    rings are pushed out a touch for fine transverse growth lines; septal sutures show
    as faint darker rings along the phragmocone (spacing grows with the shell's
    diameter), a dark line marks the siphuncle, and the aperture has a thin rim with a
    shallow hyponomic sinus on the ventral (-Z) side. The caller paints the shell
    pattern (bands, stripes) through a colour function.
  * soft_body(): the animal in the body chamber - a fleshy head with eyes, an optional
    dorsal hood (Nautilus-like), a ring of arms or tentacles reaching forward and the
    funnel (hyponome) underneath.

Frame: forward -Y (arms first), dorsal +Z, the conch centred on the Y axis.
"""

import math

from mathutils import Vector, noise

import nh_model as nh
import nh_ammonite as am

EYE = (0.04, 0.04, 0.05)
EYE_RIM = (0.78, 0.70, 0.46)
INSIDE = (0.20, 0.10, 0.07)


def conch(length, r_aperture, r_apex, paint, rings=110, sides=18, y0=0.0,
          body_frac=0.28, septum_spacing=0.55, siphuncle=0.0, sinus=0.18,
          growth=0.012, bulge=0.05):
    """Orthocone from the aperture (y0) back to the apex (y0 + length).

      paint(s, a, info) -> rgb: s = 0 aperture .. 1 apex, a = angle around the axis
        (pi/2 = dorsal, -pi/2 = ventral), info = dict(ridge, suture, body) where
        ridge is 0/1 for alternate growth rings, suture 0..1 near a septum and body is
        1 on the body chamber.
      septum_spacing: chamber length in shell radii.
      siphuncle: angle of the siphuncle line (pi/2 central-dorsal hint, -pi/2 ventral).
      bulge: slight convexity of the profile (0 = a perfectly straight cone).
    Returns (bmesh, aperture_radius)."""

    def radius(s):
        base = r_aperture + (r_apex - r_aperture) * s
        return base * (1.0 + bulge * math.sin(math.pi * min(1.0, s * 1.2)))

    # septa: walk back from the end of the body chamber, one chamber at a time
    septa = []
    s = body_frac
    while s < 0.985:
        septa.append(s)
        s += septum_spacing * radius(s) / length

    ring_pts, ring_cols = [], []
    # aperture: inner wall -> lip -> outer surface
    lip_rings = [(0.6, 0.86, True), (0.0, 0.90, True), (0.0, 1.0, False)]  # (y in radii, r, inside)
    for k, (dy, rk, inside) in enumerate(lip_rings):
        ring, cols = [], []
        for j in range(sides):
            a = j / sides * math.tau
            sin_off = sinus * r_aperture * max(0.0, -math.sin(a)) ** 2
            y = y0 + dy * r_aperture + sin_off
            r = r_aperture * rk
            ring.append(Vector((r * math.cos(a), y, r * math.sin(a))))
            cols.append(INSIDE if inside else paint(0.0, a, dict(ridge=0, suture=0.0, body=1.0)))
        ring_pts.append(ring)
        ring_cols.append(cols)

    for i in range(1, rings + 1):
        s = i / rings
        s = s ** 1.25  # more rings near the aperture, where growth lines are wide apart
        if s > 0.999:
            break
        r = radius(s)
        ridge = i % 2
        sut = 0.0
        for q in septa:
            d = abs(s - q) * length / max(r, 1e-4)
            sut = max(sut, 1.0 - d / 0.12)
        body = 1.0 if s < body_frac else 0.0
        k = 1.0 + growth * ridge * (1.0 - 0.6 * s)
        k *= 1.0 + 0.03 * nh.smoothstep(0.04, 0.0, s)  # slightly thickened rim
        ring, cols = [], []
        for j in range(sides):
            a = j / sides * math.tau
            sin_off = sinus * r_aperture * max(0.0, -math.sin(a)) ** 2 * nh.smoothstep(0.06, 0.0, s)
            ring.append(Vector((r * k * math.cos(a), y0 + s * length + sin_off, r * k * math.sin(a))))
            col = paint(s, a, dict(ridge=ridge, suture=max(0.0, sut), body=body))
            if siphuncle and s > body_frac:
                da = math.atan2(math.sin(a - siphuncle), math.cos(a - siphuncle))
                col = nh.lerp(col, (col[0] * 0.55, col[1] * 0.5, col[2] * 0.48),
                              0.45 * nh.smoothstep(0.5, 0.15, abs(da)))
            cols.append(col)
        ring_pts.append(ring)
        ring_cols.append(cols)

    # blunt apex
    tip_r = radius(0.999)
    ring_pts.append([Vector((tip_r * 0.5 * math.cos(j / sides * math.tau), y0 + length,
                             tip_r * 0.5 * math.sin(j / sides * math.tau))) for j in range(sides)])
    ring_cols.append([paint(1.0, j / sides * math.tau, dict(ridge=0, suture=0.0, body=0.0)) for j in range(sides)])
    bm = am.grid_mesh(ring_pts, ring_cols, cap_start=True, cap_end=True)
    return bm, r_aperture


def soft_body(mb, y_ap, r, flesh, flesh_light, arms=10, arm_len=2.2, arm_r=0.13,
              hood=False, hood_col=None, eye_r=0.24, spot=None, curl=0.4, spread=0.55, droop=0.25):
    """Head emerging from an aperture of radius r at y = y_ap, facing -Y, back up (+Z).
    arm_len, arm_r, eye_r are in units of r."""

    def at(fy, fx, fz):
        return Vector((fx * r, y_ap - fy * r, fz * r))

    def flesh_col(co, n):
        k = nh.smoothstep(-0.6, 0.6, co.z / r)
        col = nh.lerp(flesh_light, flesh, k)
        if spot is not None:
            m = noise.noise(co * (9.0 / r))
            col = nh.lerp(col, spot, nh.smoothstep(0.15, 0.45, m) * (0.3 + 0.5 * k))
        return col

    # head: plugs into the body chamber, narrowing to the arm crown
    mb.add(nh.tube([at(-0.6, 0, 0), at(0.0, 0, 0), at(0.45, 0, -0.02), at(0.85, 0, -0.05), at(1.05, 0, -0.06)],
                   [0.86 * r, 0.88 * r, 0.82 * r, 0.64 * r, 0.50 * r], sides=14, scale_xy=(1.0, 0.92)),
           flesh_col)

    # funnel (hyponome) under the head, in the hyponomic sinus
    mb.add(nh.tube([at(-0.2, 0, -0.55), at(0.35, 0, -0.70), at(0.8, 0, -0.78)],
                   [0.22 * r, 0.18 * r, 0.14 * r], sides=8), flesh_light)

    if hood:
        hc = hood_col or flesh

        def hood_paint(co, n):
            m = noise.noise(co * (7.0 / r) + Vector((3, 1, 2)))
            c = nh.lerp(hc, (hc[0] * 0.65, hc[1] * 0.6, hc[2] * 0.55), nh.smoothstep(0.0, 0.4, m))
            return nh.lerp(c, flesh_light, nh.smoothstep(0.1, -0.4, n.z) * 0.6)

        mb.add(nh.ellipsoid(at(0.5, 0, 0.40), (0.55 * r, 0.95 * r, 0.34 * r), subdivisions=3,
                            deform=lambda v: 1.0 + 0.02 * math.sin(v.y * 9.0)), hood_paint)

    for side in (-1, 1):
        c = at(0.35, side * 0.70, 0.18)
        out = Vector((side, -0.35, 0.1)).normalized()

        def eye_col(co, n, out=out):
            d = n.dot(out)
            return EYE if d > 0.55 else (EYE_RIM if d > 0.35 else flesh)

        mb.add(nh.ellipsoid(c, (eye_r * r,) * 3, subdivisions=2), eye_col)

    for i in range(arms):
        a = (i + 0.5) / arms * math.tau
        ca, sa = math.cos(a), math.sin(a)
        ring = 0.38 if arms <= 12 else (0.40 if i % 2 else 0.30)
        base = at(0.92, ring * ca, ring * sa * 0.9 - 0.08)
        length = arm_len * r * (1.0 + 0.12 * math.cos(a * 3.0)) * (0.82 if arms > 12 and i % 2 == 0 else 1.0)
        out = Vector((ca, 0.0, sa))
        pts, radii = [], []
        steps = 7
        for k in range(steps + 1):
            t = k / steps
            p = base + Vector((0, -1, 0)) * (length * t * (1 - 0.15 * t)) + out * (r * spread * t * (1 + curl * t))
            p.z -= r * droop * t * t  # tips droop a little
            pts.append(p)
            radii.append(arm_r * r * (1 - 0.8 * t) + 0.015 * r)

        def arm_col(co, n, base=base, length=length):
            t = min(1.0, (co - base).length / length)
            band = 0.5 + 0.5 * math.sin(t * 30.0)
            c = nh.lerp(flesh, flesh_light, 0.3 + 0.6 * t)
            return nh.lerp(c, flesh, band * 0.25)

        mb.add(nh.tube(pts, radii, sides=5, cap_start=False), arm_col)


def centre(obj):
    from mathutils import Vector as V
    corners = [V(c) for c in obj.bound_box]
    c = sum(corners, V()) / 8
    for v in obj.data.vertices:
        v.co -= c
