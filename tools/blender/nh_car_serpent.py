"""
Serpentine wrapper around nh_car_tetrapod for the long, limbless or near-limbless
Carboniferous lepospondyls (phlegethontia_longissima.py, brachydectes_newberryi.py).

Bends the nh_car_tetrapod spine into a gentle lateral S-wave (x += A sin(2 pi s / wavelength),
damped toward the head) before the body is lofted and fused, so a long thin body reads as a
slithering animal on the map instead of a straight stick. Ground style: pivot on the ground.
"""

import math

import nh_model as nh
import nh_car_tetrapod as tp

_orig_init = tp.Spine.__init__


def run(sp, amp=0.06, wavelength=0.55, phase=0.0, head_calm=0.15):
    def init(self, spec):
        _orig_init(self, spec)
        for p, s in zip(self.pts, self.s):
            p.x += amp * nh.smoothstep(0.0, head_calm, s) * math.sin(math.tau * s / wavelength + phase)
    tp.Spine.__init__ = init
    views = ((35, 25), (-90, 8), (160, 60))
    nh.run(lambda: tp.build(sp), sp.name, ground=(0.30, 0.27, 0.18), background=(0.20, 0.28, 0.18), views=views)
