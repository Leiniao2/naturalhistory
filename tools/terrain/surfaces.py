"""
Generates the extra ground surfaces of the hex map: Assets/Resources/TerrainSurfaces/*.png.

The base terrain textures (Assets/Textures/Terrain, one per TerrainKind) give every biome one look.
These add the materials the ground is made of in different places, picked per region by
HexGrid.SetGroundLook: rippled dune sand, desert pavement, salt flats, cracked clay, lava fields,
red slickrock, laterite, tundra stone polygons, crevassed ice, and the rock faces
of cliffs (granite, layered sandstone, columnar basalt, chalk with flint, bedded limestone).

Every texture is 512 x 512 and tiles seamlessly (all noise is periodic). Each is built as a height
field, lit from the upper left so pebbles, ripples and cracks read in relief, then coloured.

Needs numpy; Blender's bundled Python has it:
  /Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13 tools/terrain/surfaces.py
"""

import os
import struct
import zlib

import numpy as np

N = 512
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "procedural")  # not used in the game (replaced by Flow textures)
Y, X = np.mgrid[0:N, 0:N].astype(np.float64) / N  # 0..1, tiling


# ---------------------------------------------------------------- noise (all periodic)

def value_noise(cells, rng):
    """Smooth random field with `cells` lattice cells across the tile (bicubic, wraps)."""
    g = rng.random((cells, cells))
    fx, fy = X * cells, Y * cells
    ix, iy = np.floor(fx).astype(int), np.floor(fy).astype(int)
    tx, ty = fx - ix, fy - iy

    def cubic(p0, p1, p2, p3, t):
        return p1 + 0.5 * t * (p2 - p0 + t * (2 * p0 - 5 * p1 + 4 * p2 - p3 + t * (3 * (p1 - p2) + p3 - p0)))

    rows = []
    for dy in (-1, 0, 1, 2):
        yy = (iy + dy) % cells
        rows.append(cubic(*(g[yy, (ix + dx) % cells] for dx in (-1, 0, 1, 2)), tx))
    return cubic(*rows, ty)


def fbm(rng, base=4, octaves=5, gain=0.5):
    total, amp, norm, cells = np.zeros((N, N)), 1.0, 0.0, base
    for _ in range(octaves):
        total += amp * value_noise(cells, rng)
        norm += amp
        amp *= gain
        cells *= 2
    return total / norm


def cellular(cells, rng, jitter=0.9, stretch=(1.0, 1.0), warp=0.0):
    """Jittered-grid Voronoi: (F1, F2, id of the nearest cell's random value), all wrapping.
    stretch scales distances along x / y (elongated cells); warp (in cells) bends the cell edges
    with periodic noise so they wander instead of running dead straight."""
    pts = rng.random((cells, cells, 2)) * jitter + (1 - jitter) * 0.5
    val = rng.random((cells, cells))
    fx, fy = X * cells, Y * cells
    if warp:
        wrng = np.random.default_rng(int(rng.integers(1 << 30)))
        fx = fx + (value_noise(4, wrng) - 0.5) * warp + (value_noise(16, wrng) - 0.5) * warp * 0.3
        fy = fy + (value_noise(4, wrng) - 0.5) * warp + (value_noise(16, wrng) - 0.5) * warp * 0.3
    ix, iy = np.floor(fx).astype(int), np.floor(fy).astype(int)
    f1 = np.full((N, N), 9.0)
    f2 = np.full((N, N), 9.0)
    nid = np.zeros((N, N))
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            cx, cy = (ix + dx) % cells, (iy + dy) % cells
            px = ix + dx + pts[cy, cx, 0]
            py = iy + dy + pts[cy, cx, 1]
            d = np.sqrt(((fx - px) * stretch[0]) ** 2 + ((fy - py) * stretch[1]) ** 2)
            closer = d < f1
            f2 = np.where(closer, f1, np.minimum(f2, d))
            nid = np.where(closer, val[cy, cx], nid)
            f1 = np.where(closer, d, f1)
    return f1, f2, nid


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def shade(height, strength=2.0):
    """Lambert light from the upper left on a height field (wrapping gradients)."""
    gx = (np.roll(height, -1, 1) - np.roll(height, 1, 1)) * N * 0.5
    gy = (np.roll(height, -1, 0) - np.roll(height, 1, 0)) * N * 0.5
    nx, ny, nz = -gx * strength / N * 40, -gy * strength / N * 40, np.ones_like(height)
    length = np.sqrt(nx * nx + ny * ny + nz * nz)
    light = np.array([-0.55, -0.55, 0.63])
    light /= np.linalg.norm(light)
    lam = (nx * light[0] + ny * light[1] + nz * light[2]) / length
    return np.clip(0.55 + 0.6 * (lam - light[2]) + 0.45, 0.35, 1.4)


def mix(a, b, t):
    t = t[..., None] if np.ndim(t) == 2 else t
    return np.asarray(a) * (1 - t) + np.asarray(b) * t


def palette(t, stops):
    """Colour ramp: stops = [(position, (r, g, b)), ...]"""
    t = np.clip(t, 0, 1)
    out = np.zeros((N, N, 3))
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        k = np.clip((t - p0) / max(p1 - p0, 1e-6), 0, 1)[..., None]
        inside = ((t >= p0) & (t <= p1))[..., None]
        out = np.where(inside, np.asarray(c0) * (1 - k) + np.asarray(c1) * k, out)
    return out


def grain(rng, amount):
    return 1 + (rng.random((N, N)) - 0.5) * amount


def save(name, rgb):
    os.makedirs(OUT, exist_ok=True)
    img = (np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8)
    raw = b"".join(b"\x00" + img[y].tobytes() for y in range(N))

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", N, N, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    with open(os.path.join(OUT, name + ".png"), "wb") as f:
        f.write(png)
    print("wrote", name, rgb.mean(axis=(0, 1)).round(2))


def periodic_sin(freq_x, freq_y, warp):
    """sin along an integer direction so it tiles; warp (field) bends the ripples."""
    return np.sin(2 * np.pi * (X * freq_x + Y * freq_y) + warp)


# ---------------------------------------------------------------- surfaces

def dune_sand():
    rng = np.random.default_rng(1)
    warp = fbm(rng, 3, 4) * 7
    ripples = periodic_sin(9, 4, warp)
    ripples = np.sign(ripples) * np.abs(ripples) ** 0.6           # sharp crests, wide troughs
    swell = fbm(rng, 2, 3)
    h = ripples * 0.25 + swell * 1.5
    lit = shade(h, 1.4)
    base = palette(swell, [(0, (0.78, 0.62, 0.40)), (0.5, (0.86, 0.70, 0.46)), (1, (0.92, 0.79, 0.56))])
    save("DuneSand", base * lit[..., None] * grain(rng, 0.12)[..., None])


def desert_pavement():
    rng = np.random.default_rng(2)
    soil = fbm(rng, 4, 5)
    base = palette(soil, [(0, (0.66, 0.54, 0.40)), (1, (0.80, 0.68, 0.52))])
    f1, f2, nid = cellular(34, rng, 0.85)
    size = 0.22 + 0.18 * cellular(34, np.random.default_rng(3))[2]
    pebble = smoothstep(size, size * 0.55, f1)                   # rounded stones
    stone_col = palette(nid, [(0, (0.22, 0.17, 0.14)), (0.35, (0.42, 0.28, 0.20)), (0.6, (0.55, 0.47, 0.40)), (1, (0.30, 0.27, 0.26))])
    h = pebble * 0.6 + soil * 0.3
    lit = shade(h, 2.2)
    col = mix(base, stone_col * (0.9 + 0.3 * pebble[..., None]), pebble * 0.95)
    save("DesertPavement", col * lit[..., None] * grain(rng, 0.1)[..., None])


def salt_flat():
    rng = np.random.default_rng(4)
    f1, f2, nid = cellular(7, rng, 0.8, warp=1.2)
    ridge = smoothstep(0.07, 0.0, f2 - f1)                       # raised salt ridges on polygon edges
    crust = fbm(rng, 6, 5)
    h = ridge * 0.5 + crust * 0.15
    lit = shade(h, 1.8)
    base = palette(crust, [(0, (0.80, 0.80, 0.80)), (1, (0.94, 0.93, 0.90))])
    base = base * (0.96 + 0.06 * nid[..., None])
    col = mix(base, (0.98, 0.98, 0.97), ridge * 0.7)
    save("SaltFlat", col * lit[..., None] * grain(rng, 0.05)[..., None])


def cracked_clay():
    rng = np.random.default_rng(5)
    f1, f2, nid = cellular(14, rng, 0.9, warp=0.9)
    edge = f2 - f1
    crack = smoothstep(0.05, 0.015, edge)
    curl = smoothstep(0.0, 0.25, edge)                           # plates curl up at their rims
    clay = fbm(rng, 5, 4)
    h = curl * 0.25 - crack * 0.6 + clay * 0.1
    lit = shade(h, 2.0)
    base = palette(clay * 0.6 + nid * 0.4, [(0, (0.62, 0.48, 0.34)), (1, (0.76, 0.62, 0.46))])
    col = mix(base, (0.20, 0.15, 0.11), crack)
    save("CrackedClay", col * lit[..., None] * grain(rng, 0.08)[..., None])


def lava_field():
    rng = np.random.default_rng(6)
    warp = fbm(rng, 3, 4) * 9
    ropes = periodic_sin(14, 6, warp)                            # ropy pahoehoe folds
    lumps = fbm(rng, 5, 5)
    f1, f2, _ = cellular(8, rng, 0.9)
    crack = smoothstep(0.035, 0.0, f2 - f1)
    h = ropes * 0.12 + lumps * 0.8 - crack * 0.4
    lit = shade(h, 2.4)
    oxid = smoothstep(0.6, 0.75, fbm(rng, 3, 3))                 # rusty, oxidised patches
    base = mix(palette(lumps, [(0, (0.10, 0.10, 0.11)), (1, (0.26, 0.25, 0.25))]), (0.42, 0.22, 0.15), oxid * 0.6)
    save("LavaField", base * lit[..., None] * grain(rng, 0.15)[..., None])


def slickrock():
    rng = np.random.default_rng(8)
    warp = fbm(rng, 2, 4) * 5
    beds = periodic_sin(0, 7, warp + X * 0)                      # cross-bedded sandstone layers
    cross = periodic_sin(3, 9, fbm(rng, 3, 3) * 6)
    smooth = fbm(rng, 3, 5)
    potholes = smoothstep(0.7, 0.78, fbm(rng, 6, 3))
    h = smooth * 0.8 - potholes * 0.3 + beds * 0.03
    lit = shade(h, 1.5)
    t = 0.5 + 0.3 * beds + 0.15 * cross + 0.2 * (smooth - 0.5)
    base = palette(t, [(0, (0.62, 0.30, 0.18)), (0.45, (0.76, 0.42, 0.24)), (0.75, (0.86, 0.60, 0.40)), (1, (0.92, 0.80, 0.62))])
    col = mix(base, (0.40, 0.22, 0.14), potholes * 0.6)
    save("Slickrock", col * lit[..., None] * grain(rng, 0.06)[..., None])


def red_earth():
    rng = np.random.default_rng(9)
    soil = fbm(rng, 4, 5)
    lit = shade(soil * 0.6, 1.2)
    base = palette(soil, [(0, (0.52, 0.24, 0.14)), (0.6, (0.66, 0.34, 0.20)), (1, (0.74, 0.46, 0.28))])
    # sparse tufts of dry grass: short strokes clustered in patches
    tufts = np.zeros((N, N))
    patch = fbm(rng, 3, 3)
    for _ in range(900):
        x, y = rng.integers(0, N, 2)
        if patch[y, x] < 0.48:
            continue
        length = rng.integers(3, 8)
        dx = rng.integers(-2, 3)
        for k in range(length):
            tufts[(y - k) % N, (x + dx * k // length) % N] = 1
    col = mix(base, (0.80, 0.70, 0.36), tufts * 0.85)
    save("RedEarth", col * lit[..., None] * grain(rng, 0.12)[..., None])


def patterned_ground():
    rng = np.random.default_rng(10)
    f1, f2, nid = cellular(7, rng, 0.8, warp=1.0)
    edge = f2 - f1
    stones = smoothstep(0.12, 0.04, edge)
    pebbles = cellular(60, rng, 0.9)[0]
    stone_bits = smoothstep(0.32, 0.18, pebbles) * stones
    centre = fbm(rng, 6, 4)
    h = centre * 0.3 + stone_bits * 0.5
    lit = shade(h, 2.0)
    base = palette(centre * 0.7 + nid * 0.3, [(0, (0.42, 0.40, 0.28)), (0.5, (0.52, 0.50, 0.34)), (1, (0.62, 0.58, 0.42))])
    col = mix(base, (0.55, 0.53, 0.50), stones * 0.55)
    col = mix(col, (0.68, 0.66, 0.62), stone_bits)
    save("PatternedGround", col * lit[..., None] * grain(rng, 0.1)[..., None])


def crevassed_ice():
    rng = np.random.default_rng(11)
    flow = fbm(rng, 3, 4) * 3
    crevasse = smoothstep(0.965, 0.995, np.abs(periodic_sin(1, 5, flow + fbm(rng, 6, 3) * 2)))
    crevasse *= smoothstep(0.45, 0.6, fbm(rng, 3, 3))           # only in broken stretches
    sastrugi = periodic_sin(13, 2, fbm(rng, 4, 3) * 5)
    snow = fbm(rng, 6, 5)
    h = snow * 0.4 + sastrugi * 0.05 - crevasse * 0.8
    lit = shade(h, 1.6)
    base = palette(snow, [(0, (0.78, 0.86, 0.92)), (1, (0.94, 0.97, 1.0))])
    col = mix(base, (0.22, 0.42, 0.62), crevasse * 0.9)
    save("CrevassedIce", col * lit[..., None])


# Cliff faces (seen from the side: x across, y down). Fairly neutral so HexGrid's cliff tint can
# still warm or cool them a little.

def cliff_granite():
    rng = np.random.default_rng(12)
    f1, f2, _ = cellular(5, rng, 0.8, stretch=(1.0, 0.6))
    joints = smoothstep(0.05, 0.0, f2 - f1)
    rock = fbm(rng, 6, 5)
    flecks = rng.random((N, N))
    h = rock * 0.7 - joints * 0.6
    lit = shade(h, 2.4)
    base = palette(rock, [(0, (0.52, 0.50, 0.50)), (1, (0.74, 0.70, 0.68))])
    flecks = value_noise(160, rng)                                # grains a few pixels across
    base = mix(base, (0.18, 0.17, 0.17), smoothstep(0.78, 0.86, flecks) * 0.8)            # black mica
    base = mix(base, (0.82, 0.64, 0.58), smoothstep(0.24, 0.16, flecks) * 0.7)            # pink feldspar
    col = mix(base, (0.16, 0.15, 0.15), joints)
    save("CliffGranite", col * lit[..., None])


def cliff_sandstone():
    rng = np.random.default_rng(13)
    warp = fbm(rng, 2, 4) * 2.5
    strata = periodic_sin(0, 15, warp)
    fine = periodic_sin(0, 47, warp * 1.3)
    rock = fbm(rng, 6, 5)
    h = strata * 0.08 + rock * 0.6
    lit = shade(h, 2.2)
    t = 0.5 + 0.3 * strata + 0.1 * fine + 0.2 * (rock - 0.5)
    base = palette(t, [(0, (0.60, 0.34, 0.24)), (0.4, (0.74, 0.48, 0.32)), (0.7, (0.84, 0.66, 0.48)), (1, (0.90, 0.80, 0.64))])
    save("CliffSandstone", base * lit[..., None] * grain(rng, 0.05)[..., None])


def cliff_basalt():
    rng = np.random.default_rng(14)
    # vertical columns of random width, broken by horizontal joints at their own heights
    cols = 22
    edges = np.sort(rng.random(cols))
    xi = np.searchsorted(edges, X) % cols
    left, right = edges[(xi - 1) % cols], edges[xi]
    width = np.where(right > left, right - left, right + 1 - left)
    across = ((X - left) % 1) / np.maximum(width, 1e-3)
    face = np.sin(np.pi * np.clip(across, 0, 1)) ** 0.5           # rounded column faces
    offset = rng.random(cols)[xi]
    joint = smoothstep(0.96, 1.0, np.abs(np.sin(2 * np.pi * (Y * 6 + offset))))
    rock = fbm(rng, 6, 4)
    h = face * 0.5 + rock * 0.2 - joint * 0.3
    lit = shade(h, 2.6)
    base = palette(rock * 0.6 + rng.random(cols)[xi] * 0.4, [(0, (0.17, 0.17, 0.18)), (1, (0.34, 0.33, 0.33))])
    col = mix(base, (0.08, 0.08, 0.08), np.maximum(joint, smoothstep(0.2, 0.0, face)))
    save("CliffBasalt", col * lit[..., None] * grain(rng, 0.08)[..., None])


def cliff_chalk():
    rng = np.random.default_rng(15)
    warp = fbm(rng, 2, 4) * 1.5
    bands = periodic_sin(0, 8, warp)
    flint_rows = smoothstep(0.93, 0.99, bands)
    nodules = smoothstep(0.3, 0.15, cellular(40, rng, 0.9)[0]) * flint_rows
    rock = fbm(rng, 6, 5)
    h = rock * 0.5 - nodules * 0.2
    lit = shade(h, 1.6)
    base = palette(rock, [(0, (0.82, 0.81, 0.77)), (1, (0.96, 0.95, 0.92))])
    col = mix(base, (0.18, 0.18, 0.2), nodules)
    save("CliffChalk", col * lit[..., None])


def cliff_limestone():
    rng = np.random.default_rng(16)
    warp = fbm(rng, 2, 3) * 1.2
    beds = smoothstep(0.95, 1.0, np.abs(periodic_sin(0, 9, warp)))
    f1, f2, nid = cellular(5, rng, 0.5, stretch=(1.0, 0.3), warp=0.4)  # a few vertical joints
    joints = smoothstep(0.04, 0.0, f2 - f1)
    stain = smoothstep(0.55, 0.75, fbm(rng, 3, 4)) * (0.3 + 0.7 * Y)
    rock = fbm(rng, 6, 5)
    h = rock * 0.5 - beds * 0.4 - joints * 0.4
    lit = shade(h, 2.0)
    base = palette(rock * 0.7 + nid * 0.3, [(0, (0.68, 0.66, 0.60)), (1, (0.86, 0.83, 0.75))])
    col = mix(base, (0.30, 0.28, 0.25), np.maximum(beds, joints) * 0.85)
    col = mix(col, (0.55, 0.48, 0.38), stain * 0.4)
    save("CliffLimestone", col * lit[..., None])


if __name__ == "__main__":
    for make in (dune_sand, desert_pavement, salt_flat, cracked_clay, lava_field,
                 slickrock, red_earth, patterned_ground, crevassed_ice,
                 cliff_granite, cliff_sandstone, cliff_basalt, cliff_chalk, cliff_limestone):
        make()
