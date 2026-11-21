"""
Shared extras for the batch-2 Permian tetrapods built with nh_per_tetra
(sphenacodon_ferox.py, platyhystrix_rugosus.py, suminia_getmanovi.py ...).

  * sail(...): returns a crisp(mb, spec) hook that raises a dorsal sail or low crest of
    neural spines along the back - a membrane over the spine tips (optional), spines with
    optional knobs (Platyhystrix's rough, bumpy spines) and a height profile that rises and
    falls between y0 and y1.
  * chain(crisps): combine several crisp hooks into one.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_per_tetra as pt  # noqa: E402
from mathutils import Vector as V  # noqa: E402


def back_z(spec, y):
    z, _w, hh, _x = pt.rows_at(spec.torso, y)
    return z + hh


def sail(y0, y1, height, n=18, spine_col=(0.25, 0.18, 0.12), sail_col=None, top_col=None,
         membrane=True, knobs=0, knob_col=None, lean=0.05, peak=0.5, spine_r=0.008):
    def h_at(y):
        t = (y - y0) / (y1 - y0)
        if t <= 0 or t >= 1:
            return 0.0
        # asymmetric hump peaking at `peak`
        u = t / peak if t < peak else (1 - t) / (1 - peak)
        return height * math.sin(math.pi * 0.5 * u) ** 0.8

    def crisp(mb, spec):
        sc = sail_col or spec.back
        tc = top_col or sc
        if membrane:
            top, low = [], []
            for i in range(41):
                y = y0 + (y1 - y0) * i / 40
                top.append(V((0, y + lean * h_at(y), back_z(spec, y) + h_at(y) * 0.95)))
                low.append(V((0, y, back_z(spec, y) - 0.03)))

            def col(co, n_):
                h = max(h_at(co.y), 0.02)
                t = (co.z - back_z(spec, co.y)) / h
                return nh.lerp(nh.lerp(spec.back, sc, nh.smoothstep(0.0, 0.3, t)), tc, nh.smoothstep(0.75, 1.0, t))
            mb.add(pt.membrane(low + top[::-1], 0.007), col, smooth=False)
        for i in range(n):
            y = y0 + 0.01 + (y1 - y0 - 0.02) * i / (n - 1)
            h = h_at(y)
            if h < 0.01:
                continue
            base = V((0, y, back_z(spec, y) - 0.03))
            tip = V((0, y + lean * h, back_z(spec, y) + h + 0.01))
            mb.add(nh.tube([base, tip], [spine_r, spine_r * 0.5], sides=6), spine_col)
            for k in range(knobs):
                p = base.lerp(tip, 0.35 + 0.6 * (k + 0.5) / knobs)
                for sx in (1, -1):
                    mb.add(nh.ellipsoid(p + V((sx * spine_r * 0.9, 0, 0)), (spine_r * 1.1,) * 3, subdivisions=1),
                           knob_col or spine_col)
    return crisp


def chain(*hooks):
    def crisp(mb, spec):
        for h in hooks:
            if h:
                h(mb, spec)
    return crisp
