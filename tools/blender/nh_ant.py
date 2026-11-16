"""
Shared builder for the procedural worker ants in tools/blender/ (fire, Argentine, pharaoh,
ghost and leafcutter ants), walking on the ground for map colonies.

A worker ant from separate glossy shells: a head (optionally heart-shaped with occipital
spines) with compound eyes, clypeus and toothed mandibles, and elbowed (geniculate)
antennae - a long scape plus a beaded funiculus whose segment count and club are set per
species; a humped mesosoma (pronotum, mesonotum, metanotal groove, propodeum) with
optional spine pairs; a waist of one node, a thin upright scale, a hidden scale, or a
petiole plus postpetiole; and an oval gaster banded by darker tergite margins, with an
optional sting. Six jointed legs: coxa, femur rising to a knee above the body line, tibia
down to the ground and a beaded tarsus with claws. Colour is baked into the vertex colours
with a soft highlight, since the map shader is diffuse only.

Map walking (see SpeciesColonies / MapFeatureFlap.cginc): everything below the hip line
swings as legs, grouped into three pairs by thirds of the model's length. So the whole body
sits just above the hip line, the knees rise above it, and each tibia + tarsus is kept
inside its own third of the length; build() checks this and prints mapHip.

Faces -Y, pivot on the ground (feet at z = 0).

Usage from a species script:
  import nh_ant
  nh_ant.run(dict(...species parameters, see DEFAULTS...), "ModelName")
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

LIGHT_DIR = Vector((-0.45, -0.55, 0.70)).normalized()  # baked highlight direction
EYE = (0.03, 0.03, 0.03)
EYE_SHEEN = (0.30, 0.30, 0.30)

DEFAULTS = dict(
    # body line: underside of the body above the ground (the legs lift it this high)
    base=0.12,
    # head: half-width, half-length, half-height; pitch (deg, + = mouth down); centre height
    head_w=0.115, head_l=0.125, head_h=0.080, head_pitch=12.0, head_z=0.080,
    head_heart=0.0,           # posterior notch (0 = oval, 1 = deep heart shape)
    neck=0.88,                # head centre ahead of the pronotum, in head half-lengths
    head_lobes=0.0,           # widens the back corners (Atta)
    occipital_spines=0.0,     # length of the spines on the back corners
    eye_r=0.028, eye_y=-0.15,  # eye radius; eye position along the head (-1 = front)
    mandible=1.0, mandible_teeth=4,
    # antennae: scape length, funiculus length, funiculus segments, club segments, club thickening
    scape=0.20, funiculus=0.26, fun_segs=11, club_segs=0, club_scale=1.6, ant_r=0.010,
    scape_dir=(0.80, -0.40, 0.45), fun_dir=(0.15, -0.95, -0.20), fun_dir2=(0.30, -0.70, -0.65),
    # mesosoma: length, height, width factor, metanotal groove depth, profile heights (t, rel radius)
    meso_len=0.36, meso_h=0.13, meso_w=0.95, groove=0.25,
    meso_profile=((0.0, 0.50), (0.12, 0.92), (0.28, 1.00), (0.48, 0.86), (0.62, 0.78),
                  (0.74, 0.74), (0.90, 0.66), (1.0, 0.40)),
    spines=(),                # (t along mesosoma, length, (dx, dy, dz) direction)
    # waist: "node" (one node), "two" (petiole + postpetiole), "scale" (upright scale), "hidden"
    waist="two", pet_h=0.050, pet_w=0.034, post_w=0.046,
    # gaster: half-length, half-width, half-height, tilt (deg, + = tip down)
    gaster_l=0.24, gaster_w=0.15, gaster_h=0.13, gaster_tilt=6.0, gaster_bands=4,
    sting=True,
    legs=1.0,                 # leg span scale
    knee_rise=0.10,           # knee height above the body line
    leg_r=0.013,
    gloss=0.45,
    # colours
    head_col=(0.4, 0.2, 0.1), meso_col=None, waist_col=None, gaster_col=(0.2, 0.1, 0.05),
    gaster_tip=None, tip_start=0.45, band_col=None, leg_col=None, scape_col=None, antenna_col=None,
    mandible_col=None,
)


# ---------------------------------------------------------------- colour

def darker(c, k):
    return tuple(x * k for x in c)


def shade(base, gloss=0.45, under=0.40):
    """Base colour with a darker underside and a soft baked highlight."""
    hi = nh.lerp(base, (1.0, 1.0, 1.0), 0.55)

    def col(co, n):
        c = nh.lerp(base, darker(base, 0.55), max(0.0, -n.z) * under)
        h = max(0.0, n.dot(LIGHT_DIR)) ** 10 * gloss
        return nh.lerp(c, hi, h)
    return col


# ---------------------------------------------------------------- helpers

def oriented(bm, rot, centre):
    nh.transform(bm, rot.to_4x4())
    nh.transform(bm, Matrix.Translation(Vector(centre)))
    return bm


def bezier(a, c, b, t):
    return a * (1 - t) ** 2 + c * 2 * t * (1 - t) + b * t * t


def beaded(points, radii, joint=0.62):
    """Tube through segment boundaries `points`: swollen in the middle of each segment,
    pinched at the joints (antennal funiculus, tarsi)."""
    pts, rs = [], []
    for i in range(len(points) - 1):
        a, b = Vector(points[i]), Vector(points[i + 1])
        r = radii[i]
        if i == 0:
            pts.append(a)
            rs.append(r * joint)
        pts.append(a.lerp(b, 0.5))
        rs.append(r)
        pts.append(b)
        nxt = radii[i + 1] if i + 1 < len(radii) else r
        rs.append(min(r, nxt) * joint if i < len(points) - 2 else r * 0.45)
    return nh.tube(pts, rs, sides=5)


class Ant:
    def __init__(self, params):
        p = dict(DEFAULTS)
        p.update(params)
        for k in ("meso_col", "waist_col", "leg_col", "scape_col", "antenna_col", "mandible_col"):
            if p[k] is None:
                p[k] = p["head_col"] if k != "waist_col" else (p["meso_col"] or p["head_col"])
        if p["gaster_tip"] is None:
            p["gaster_tip"] = p["gaster_col"]
        if p["band_col"] is None:
            p["band_col"] = darker(p["gaster_col"], 0.55)
        self.p = p
        self.mb = nh.MeshBuilder()
        self.base = p["base"]
        self.hip = self.base - 0.004
        self.y_meso = -0.18

    # ------------------------------------------------------------ head
    def head_point(self, local):
        return self.head_c + self.head_rot @ Vector(local)

    def build_head(self):
        p, mb = self.p, self.mb
        w, l, h = p["head_w"], p["head_l"], p["head_h"]
        self.head_c = Vector((0.0, self.y_meso - l * p["neck"], self.base + p["head_z"]))
        self.head_rot = Matrix.Rotation(math.radians(p["head_pitch"]), 3, "X")

        def deform(n):
            k = 1.0 - 0.06 * max(0.0, -n.y) ** 2   # a little narrower toward the mouth
            back = nh.smoothstep(0.25, 1.0, n.y)
            k -= p["head_heart"] * 0.30 * back * math.exp(-(n.x / 0.30) ** 2)
            k += p["head_lobes"] * 0.18 * back * min(1.0, abs(n.x) * 1.6)
            return k

        head = nh.uv_ellipsoid((0, 0, 0), (w, l, h), 16, 12, deform=deform)
        mb.add(oriented(head, self.head_rot, self.head_c), shade(p["head_col"], p["gloss"]))
        # clypeus
        mb.add(oriented(nh.uv_ellipsoid((0, -l * 0.86, -h * 0.25), (w * 0.42, l * 0.22, h * 0.40), 10, 6),
                        self.head_rot, self.head_c), shade(darker(p["head_col"], 0.92), p["gloss"]))
        # compound eyes on the sides
        for s in (-1, 1):
            c = (s * w * 0.90, l * p["eye_y"], h * 0.18)
            er = p["eye_r"]

            def eye_col(co, n):
                return nh.lerp(EYE, EYE_SHEEN, max(0.0, n.dot(LIGHT_DIR)) ** 4)
            mb.add(oriented(nh.uv_ellipsoid(c, (er * 0.75, er * 1.15, er), 8, 6), self.head_rot, self.head_c),
                   eye_col)
        # occipital spines on the back corners (Atta)
        if p["occipital_spines"] > 0:
            for s in (-1, 1):
                root = self.head_point((s * w * 0.78, l * 0.72, h * 0.45))
                tip = root + Vector((s * 0.45, 0.55, 0.70)).normalized() * p["occipital_spines"]
                mb.add(nh.tube([root, tip], [0.016, 0.0], sides=5), shade(p["head_col"], p["gloss"]))
        self.build_mandibles()
        self.build_antennae()

    def build_mandibles(self):
        p, mb = self.p, self.mb
        w, l, h = p["head_w"], p["head_l"], p["head_h"]
        m = p["mandible"]
        col = shade(darker(p["mandible_col"], 0.8), p["gloss"])
        self.mandible_tips = []
        for s in (-1, 1):
            base = Vector((s * w * 0.48, -l * 0.80, -h * 0.40))
            mid = base + Vector((-s * w * 0.04, -l * 0.40 * m, -h * 0.05))
            tip = Vector((s * w * 0.06, base.y - l * 0.62 * m, -h * 0.45))
            pts = [self.head_point(q) for q in (base, mid, tip)]
            mb.add(nh.tube(pts, [0.026 * m ** 0.5, 0.020 * m ** 0.5, 0.004], sides=6, scale_xy=(1.0, 0.5)), col)
            self.mandible_tips.append(pts[-1])
            # teeth along the inner (chewing) edge
            for k in range(p["mandible_teeth"]):
                t = 0.35 + 0.6 * k / max(p["mandible_teeth"] - 1, 1)
                q = bezier(Vector(base), Vector(mid), Vector(tip), t)
                inward = Vector((-s, -0.3, 0)).normalized()
                a = self.head_point(q)
                b = self.head_point(q + inward * 0.014 * m)
                mb.add(nh.tube([a, b], [0.006 * m ** 0.5, 0.0], sides=4), col)

    def build_antennae(self):
        p, mb = self.p, self.mb
        w, l, h = p["head_w"], p["head_l"], p["head_h"]
        r0 = p["ant_r"]
        scape_col = shade(p["scape_col"], p["gloss"] * 0.7)
        fun_col = shade(p["antenna_col"], p["gloss"] * 0.7)
        min_z = self.base + 0.03
        for s in (-1, 1):
            root = self.head_point((s * w * 0.34, -l * 0.62, h * 0.30))
            sd = Vector(p["scape_dir"])
            elbow = root + Vector((s * sd.x, sd.y, sd.z)).normalized() * p["scape"]
            mb.add(nh.tube([root, root.lerp(elbow, 0.5), elbow], [r0 * 0.9, r0 * 0.95, r0 * 1.15], sides=5),
                   scape_col)
            mb.add(nh.uv_ellipsoid(elbow, (r0 * 1.3,) * 3, 6, 4), scape_col)
            d1, d2 = Vector(p["fun_dir"]), Vector(p["fun_dir2"])
            d1 = Vector((s * d1.x, d1.y, d1.z)).normalized()
            d2 = Vector((s * d2.x, d2.y, d2.z)).normalized()
            L = p["funiculus"]
            ctrl = elbow + d1 * L * 0.55
            end = ctrl + d2 * L * 0.50
            if end.z < min_z:                       # keep the tips off the ground (and above the hips)
                end.z = min_z
            # segment lengths: pedicel a bit longer, club segments longer and thicker
            n, nc = p["fun_segs"], p["club_segs"]
            lens = [1.25] + [1.0] * (n - 1)
            for k in range(nc):
                lens[n - 1 - k] = 1.0 + 0.9 * (nc - k) / nc + (0.6 if k == 0 else 0.0)
            radii = [r0 * (1.0 + 0.15 * i / n) for i in range(n)]
            if nc:
                for k in range(nc):
                    radii[n - 1 - k] = r0 * p["club_scale"] * (1.0 - 0.08 * k)
            else:
                radii = [r0 * (0.85 + 0.55 * (i / n) ** 1.5) for i in range(n)]   # gradual thickening
            tot = sum(lens)
            ts, acc = [0.0], 0.0
            for x in lens:
                acc += x
                ts.append(acc / tot)
            pts = [bezier(elbow, ctrl, end, t) for t in ts]
            mb.add(beaded(pts, radii), fun_col)

    # ------------------------------------------------------------ mesosoma, waist, gaster
    def meso_radius(self, t):
        prof = self.p["meso_profile"]
        for (t0, r0), (t1, r1) in zip(prof, prof[1:]):
            if t <= t1:
                u = (t - t0) / max(t1 - t0, 1e-6)
                r = r0 + (r1 - r0) * (u * u * (3 - 2 * u))
                break
        else:
            r = prof[-1][1]
        # metanotal groove: a notch between mesonotum and propodeum
        r *= 1.0 - self.p["groove"] * math.exp(-((t - 0.64) / 0.05) ** 2)
        return r * self.p["meso_h"] * 0.5

    def meso_point(self, t):
        r = self.meso_radius(t)
        return Vector((0.0, self.y_meso + t * self.p["meso_len"], self.base + 0.006 + r)), r

    def build_mesosoma(self):
        p, mb = self.p, self.mb
        steps = 22
        pts, radii = [], []
        for i in range(steps + 1):
            c, r = self.meso_point(i / steps)
            pts.append(c)
            radii.append(r)
        mb.add(nh.tube(pts, radii, sides=12, scale_xy=(p["meso_w"], 1.0)), shade(p["meso_col"], p["gloss"]))
        # propodeal declivity: a rounded cap at the back
        c, r = self.meso_point(1.0)
        mb.add(nh.uv_ellipsoid(c, (r * p["meso_w"] * 1.05, r * 0.6, r * 1.05), 10, 6), shade(p["meso_col"], p["gloss"]))
        # spines (leafcutters: pronotal, mesonotal and propodeal pairs)
        for t, length, d in p["spines"]:
            c, r = self.meso_point(t)
            for s in (-1, 1):
                dd = Vector((s * d[0], d[1], d[2])).normalized()
                root = c + Vector((s * r * p["meso_w"] * 0.55, 0.0, r * 0.65))
                mb.add(nh.tube([root, root + dd * length * 0.55, root + dd * length], [0.017, 0.010, 0.0], sides=5),
                       shade(p["meso_col"], p["gloss"]))

    def build_waist(self):
        p, mb = self.p, self.mb
        col = shade(p["waist_col"], p["gloss"])
        y0 = self.y_meso + p["meso_len"]
        zb = self.base + 0.008
        kind = p["waist"]
        if kind in ("two", "node"):
            # stalked petiole node
            node = Vector((0.0, y0 + 0.055, zb + p["pet_h"] * 1.15))
            mb.add(nh.tube([Vector((0, y0 - 0.02, zb + 0.030)), Vector((0, y0 + 0.04, zb + 0.022)), node],
                           [0.020, 0.016, 0.020], sides=6), col)
            mb.add(nh.uv_ellipsoid(node, (p["pet_w"], 0.030, p["pet_h"]), 10, 8), col)
            y = node.y + 0.03
            if kind == "two":
                post = Vector((0.0, y + 0.035, zb + 0.040))
                mb.add(nh.uv_ellipsoid(post, (p["post_w"], 0.040, 0.040), 10, 8), col)
                mb.add(nh.tube([node, post], [0.018, 0.018], sides=6), col)
                y = post.y + 0.030
        elif kind == "scale":
            # thin upright scale leaning forward (dolichoderines)
            c = Vector((0.0, y0 + 0.030, zb + p["pet_h"]))
            rot = Matrix.Rotation(math.radians(-18), 3, "X")
            mb.add(oriented(nh.uv_ellipsoid((0, 0, 0), (p["pet_w"], 0.013, p["pet_h"]), 10, 8), rot, c), col)
            mb.add(nh.tube([Vector((0, y0 - 0.02, zb + 0.026)), Vector((0, y0 + 0.05, zb + 0.022))],
                           [0.018, 0.018], sides=6), col)
            y = y0 + 0.045
        else:
            # hidden: a tiny low scale under the overhanging gaster (Tapinoma)
            mb.add(nh.uv_ellipsoid((0.0, y0 + 0.012, zb + 0.022), (0.022, 0.012, 0.022), 8, 6), col)
            y = y0 - 0.005
        self.gaster_y0 = y

    def build_gaster(self):
        p, mb = self.p, self.mb
        gl, gw, gh = p["gaster_l"], p["gaster_w"], p["gaster_h"]
        y0 = self.gaster_y0
        tilt = math.radians(p["gaster_tilt"])
        rot = Matrix.Rotation(tilt, 3, "X")
        # lowest point of the tilted ellipsoid relative to its centre
        dz = math.sqrt((gl * math.sin(tilt)) ** 2 + (gh * math.cos(tilt)) ** 2)
        c = Vector((0.0, y0 + gl * 0.96, self.base + 0.010 + dz))
        self.gaster_c = c
        bands = p["gaster_bands"]
        gcol, tip, band = p["gaster_col"], p["gaster_tip"], p["band_col"]
        gloss = p["gloss"]

        def phase(t):
            return (t * (bands + 0.6)) % 1.0 if bands else 0.0

        def col(co, n):
            local = rot.inverted() @ (co - c)
            t = max(0.0, min(0.999, (local.y / gl + 1.0) * 0.5))
            base = nh.lerp(gcol, tip, nh.smoothstep(p["tip_start"], min(1.0, p["tip_start"] + 0.40), t))
            if bands and t > 0.12 and phase(t) > 0.74:
                base = nh.lerp(base, band, 0.85)     # darker hind margin of each tergite
            return shade(base, gloss)(co, n)

        # tube along the body axis, so the tergite margins get their own rings
        steps = 26
        pts, radii = [], []
        for i in range(steps + 1):
            t = i / steps
            pts.append(Vector((0.0, -gl + 2 * gl * t, 0.0)))
            r = gh * math.sin(math.pi * (0.04 + 0.96 * t)) ** 0.55 * (1.0 - 0.10 * t)
            if bands and t > 0.12:
                r *= 1.0 - 0.035 * nh.smoothstep(0.80, 1.0, phase(t))   # overlapping segment edges
            radii.append(r)
        radii[-1] = 0.0
        g = nh.tube(pts, radii, sides=14, scale_xy=(gw / gh, 1.0))
        mb.add(oriented(g, rot, c), col)
        self.gaster_tip_pt = c + rot @ Vector((0, gl * 0.90, 0))
        if p["sting"]:
            a = self.gaster_tip_pt - Vector((0, 0.01, 0.0))
            mb.add(nh.tube([a, a + rot @ Vector((0, 0.05, -0.012))], [0.008, 0.0], sides=5),
                   shade(darker(tip, 0.6), gloss))

    # ------------------------------------------------------------ legs
    def build_legs(self):
        p, mb = self.p, self.mb
        ys = [v.co.y for v in mb.bm.verts]
        ymin, ymax = min(ys), max(ys)
        L = ymax - ymin
        e1, e2 = ymin + L / 3, ymin + 2 * L / 3
        self.buckets = (ymin, e1, e2, ymax)
        g = p["legs"]
        col = shade(p["leg_col"], p["gloss"] * 0.8)
        joint_col = shade(darker(p["leg_col"], 0.78), p["gloss"] * 0.8)
        r = p["leg_r"]
        mw = p["meso_h"] * 0.5 * p["meso_w"]
        # (t along mesosoma for the coxa, knee y, ankle y, knee x, ankle x, tarsus direction)
        mid = 0.5 * (e1 + e2)
        specs = [
            (0.20, e1 - 0.05, e1 - 0.15 * g, 0.15, 0.25, (0.25, -1.0)),
            (0.50, mid - 0.03, mid + 0.01, 0.19, 0.34, (1.0, 0.15)),
            (0.76, e2 + 0.06, e2 + 0.22 * g, 0.22, 0.34, (0.35, 1.0)),
        ]
        self.legs = []
        for t, ky, ay, kx, ax, td in specs:
            c, _rr = self.meso_point(t)
            for s in (-1, 1):
                hip = Vector((s * mw * 0.55, c.y, self.base + 0.022))
                coxa = Vector((s * mw * 0.95, c.y + 0.005, self.hip + 0.008))
                knee = Vector((s * kx * g, ky, self.base + p["knee_rise"] * g))
                ankle = Vector((s * ax * g, ay, r * 0.75))
                tdir = Vector((s * td[0], td[1], 0.0)).normalized()
                toe = ankle + tdir * 0.09 * g + Vector((0, 0, -r * 0.35))
                mb.add(nh.tube([hip, coxa], [r * 1.5, r * 1.3], sides=6), col)
                mb.add(nh.tube([coxa, coxa.lerp(knee, 0.45) + Vector((0, 0, 0.012)), knee],
                               [r * 1.15, r * 1.40, r * 1.0], sides=6), col)
                mb.add(nh.uv_ellipsoid(knee, (r * 1.15,) * 3, 6, 4), joint_col)
                mb.add(nh.tube([knee, knee.lerp(ankle, 0.5), ankle], [r * 0.95, r * 0.85, r * 0.75], sides=5), col)
                tpts = [ankle.lerp(toe, k / 4) for k in range(5)]
                mb.add(beaded(tpts, [r * 0.70, r * 0.6, r * 0.55, r * 0.55], joint=0.75), joint_col)
                # paired tarsal claws
                for cs in (-1, 1):
                    cd = (tdir + Vector((-tdir.y, tdir.x, 0)) * 0.5 * cs).normalized()
                    mb.add(nh.tube([toe, toe + cd * 0.018 * g + Vector((0, 0, -0.004))], [r * 0.35, 0.0], sides=3),
                           joint_col)
                self.legs.append((knee, ankle, toe))

    def check_legs(self, obj):
        """Every leg vertex below the hip line must fall in its own third of the length."""
        ymin, e1, e2, ymax = self.buckets
        zs = [v.co.z for v in obj.data.vertices]
        ys = [v.co.y for v in obj.data.vertices]
        L = max(ys) - min(ys)
        ok = abs(min(ys) - ymin) < 1e-4 and abs(max(ys) - ymax) < 1e-4
        for i, (knee, ankle, toe) in enumerate(self.legs):
            pair = i // 2
            for q in (ankle, toe, knee.lerp(ankle, 0.3)):
                b = min(int((q.y - ymin) / L * 3), 2)
                if b != pair:
                    ok = False
                    print(f"WARNING leg pair {pair} point y={q.y:.3f} falls in bucket {b}")
        body_low = min(v.co.z for v in obj.data.vertices
                       if abs(v.co.x) < self.p["meso_h"] * 0.5 * self.p["meso_w"] * 0.5)
        print(f"legs in their thirds: {ok}; lowest midline body point {body_low:.3f} vs hip {self.hip:.3f}")
        return max(zs)

    def build(self, extra=None):
        self.build_head()
        self.build_mesosoma()
        self.build_waist()
        self.build_gaster()
        if extra:
            extra(self)
        self.build_legs()


def build_ant(params, name, extra=None, roughness=0.45):
    ant = Ant(params)
    ant.build(extra)
    obj = ant.mb.to_object(name, roughness=roughness)
    zmin = min(v.co.z for v in obj.data.vertices)
    height = ant.check_legs(obj) - zmin
    hip = ant.hip - zmin
    nh.ground_to_zero(obj)
    print(f"height {height:.3f}, hip {hip:.3f} -> mapHip {hip / height:.2f}")
    return obj


def run(params, name, extra=None, roughness=0.45):
    nh.run(lambda: build_ant(params, name, extra, roughness), name,
           ground=(0.42, 0.34, 0.22), views=((35, 25), (0, 80), (-90, 8)))
