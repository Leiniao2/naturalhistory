"""
Small shared detail helpers for the batch-2 Carboniferous fish built on nh_car_fish
(rhabdoderma_elegans.py, belantsea_montana.py, elonichthys_peltigerus.py, sagenodus_inaequalis.py).

  * dots(): crisp flecks / spots scattered over both flanks (ray-cast onto the fused body).
  * mouth_line(): a dark mouth slit along the side of the head.
Both return [(bm, colour)] lists for a Spec's `extra` hooks.
"""

from mathutils import Vector

import nh_model as nh
import nh_car_fish as cf


def dots(sp, tree, n, col, y_range, z_range, r_range, sink=0.35, flat=1.0):
    """n dots over y_range (body stations) and z_range (fraction of the half-height above
    the centre line), radius in r_range; sink: fraction of the radius pushed under the skin
    (so they read as flat patches); flat < 1 squashes them sideways."""
    out = []
    for i in range(n):
        y = y_range[0] + (i * 0.61803 % 1.0) * (y_range[1] - y_range[0])
        zf = z_range[0] + ((i * 0.41421) % 1.0) * (z_range[1] - z_range[0])
        sx = 1 if i % 2 else -1
        z = cf.zmid(sp, y) + cf.interp(sp.height, y) * zf
        loc, nrm, _i, _d = tree.ray_cast(Vector((sx * 1.0, y, z)), Vector((-sx, 0, 0)))
        if loc is None or abs(loc.x) < 0.01:
            continue
        r = r_range[0] + (r_range[1] - r_range[0]) * ((i * 0.7548) % 1.0)
        out.append((nh.ellipsoid(loc - nrm * r * sink, (r * flat, r * 1.2, r), subdivisions=1), col))
    return out


def mouth_line(sp, tree, y0, y1, z0, z1, col=cf.GILL, r=0.004):
    out = []
    for sx in (-1, 1):
        pts = []
        for k in range(6):
            t = k / 5
            y, z = y0 + (y1 - y0) * t, z0 + (z1 - z0) * t
            loc, nrm, _i, _d = tree.ray_cast(Vector((sx * 1.0, y, cf.zmid(sp, y) + z)), Vector((-sx, 0, 0)))
            if loc is not None:
                pts.append(loc + nrm * 0.001)
        if len(pts) >= 2:
            out.append((nh.tube(pts, [r] * len(pts), sides=4), col))
    return out
