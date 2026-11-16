"""
Paints the floor of the underground lakes (UnderGroundwater in Assets/Textures/Terrain): the
seabed texture's fine pebbles, faintly, recoloured lake-blue (its sand ripples are filtered out:
still underground water has none), so groundwater basins under the land read as clear water.
Wraps like its source. Used untinted (HexGrid.UnderTint).

Run with Blender (for numpy and PNG I/O):
  blender --background --python tools/terrain/groundwater.py
"""

import os

import bpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "..", "..", "Assets", "Textures", "Terrain")

img = bpy.data.images.load(os.path.join(TEX, "UnderSeabed.png"))
w, h = img.size
px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)[..., :3]
bpy.data.images.remove(img)

lum = px @ np.array([0.3, 0.59, 0.11], np.float32)
# Still water shows no ripples: the seabed's sand ripples (its broad light/dark waves) are taken
# out by subtracting a wrap-around blur, leaving only the fine pebbles, kept faint.
fy = np.fft.fftfreq(h)[:, None]
fx = np.fft.fftfreq(w)[None, :]
sigma = 6.0                                      # px; anything broader than this is removed
blur = np.real(np.fft.ifft2(np.fft.fft2(lum) * np.exp(-2 * (np.pi * sigma) ** 2 * (fx ** 2 + fy ** 2))))
detail = lum - blur
t = np.clip(detail / (10 * detail.std()) + 0.5, 0, 1)[..., None]
deep = np.array([0.20, 0.50, 0.70], np.float32)
pale = np.array([0.36, 0.68, 0.84], np.float32)
out = deep * (1 - t) + pale * t

img = bpy.data.images.new("UnderGroundwater", w, h, alpha=False)
img.pixels[:] = np.concatenate([out, np.ones((h, w, 1), np.float32)], axis=2).ravel()
img.filepath_raw = os.path.join(TEX, "UnderGroundwater.png")
img.file_format = "PNG"
img.save()
print("wrote UnderGroundwater")
