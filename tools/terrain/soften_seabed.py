"""
Softens the water-bed floor textures of the under layer (Assets/Textures/Terrain): their sand
ripples, gravel and mat patches read as busy stripes and blotches over whole seas (each texture
repeats several times across a tile, so even broad patches line up into a pattern). Keeps the
overall colour, only a faint trace of the broad light and dark patches and of the fine grain, and
drops the ripple-sized pattern in between. Run it on the original textures (from git), not twice. Blurs wrap around (FFT), so the textures stay seamless.

Run with Blender (numpy and PNG I/O):
  blender --background --python tools/terrain/soften_seabed.py
"""

import os

import bpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "..", "..", "Assets", "Textures", "Terrain")
NAMES = [
    "UnderSeabed", "UnderLakebed", "UnderDeepSeabed",
    "UnderSeabedMicrobialMat", "UnderLakebedMicrobialMat",
    "UnderSeabedAlgalTurf", "UnderLakebedAlgalTurf", "UnderDeepSeabedBacterialMat",
]
BROAD, FINE = 22.0, 2.0          # blur radii in pixels (Gaussian sigma)
KEEP_BROAD, KEEP_FINE = 0.2, 0.3


def blur(px, sigma):
    h, w, _ = px.shape
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    g = np.exp(-2 * (np.pi * sigma) ** 2 * (fx * fx + fy * fy))
    out = np.empty_like(px)
    for c in range(3):
        out[..., c] = np.real(np.fft.ifft2(np.fft.fft2(px[..., c]) * g))
    return out


for name in NAMES:
    path = os.path.join(TEX, name + ".png")
    if not os.path.exists(path):
        continue
    img = bpy.data.images.load(path)
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)
    rgb = px[..., :3]
    mean = rgb.reshape(-1, 3).mean(axis=0)
    broad = blur(rgb, BROAD)
    fine = rgb - blur(rgb, FINE)
    out = mean + (broad - mean) * KEEP_BROAD + fine * KEEP_FINE
    px[..., :3] = np.clip(out, 0, 1)
    img.pixels[:] = px.ravel()
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)
    print("softened", name)
