"""
Procedural Rhinconichthys taylori (Late Cretaceous pachycormid) for the map (Swim style).

A suspension-feeding pachycormid described in 2010 (Friedman et al., Science) from a nearly
complete, three-dimensional but toothless skull from the Cenomanian Lower Chalk of Kent,
England. Only the skull is known; relatives described later from Colorado and Japan suggest
bodies of roughly 2-4.5 m. The skull is dominated by an enormously long hyomandibula and lower
jaw that swing the mouth open into a vast gape, with a short, upturned snout above it.

The body is therefore a reconstruction after other pachycormids (Leedsichthys, Bonnerichthys):
a short, deep, fusiform body behind a very large head; long, narrow, scythe-shaped pectoral
fins; a single falcate dorsal fin; a small anal fin; and a tall, deeply forked tail. Pelvic
fins (small or absent in pachycormids) are left out. Here the jaw hinge sits far back, the
upper head is tilted up about it and the lower jaw hangs wide open, showing gill rakers across
the throat. Muted grey-brown above, pale below.

Built with the pachycormid machinery from leedsichthys_problematicus.py (lofted body and upper
head, fin slabs, fused with nh_model.MeshBuilder.fuse; a separately fused, hinged lower jaw;
crisp scythe pectorals, eyes and ray-cast gill rakers), with its own proportions in P.

Usage:
  blender --background --python tools/blender/rhinconichthys_taylori.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Rhinconichthys.fbx
Pivot at the body centre, faces -Y, dorsal fin up (+Z). About 2 units long.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import leedsichthys_problematicus as lp  # noqa: E402  (pachycormid builder, configured via lp.P)

P = dict(lp.P)
P.update(
    name="Rhinconichthys",
    voxel=0.022, jaw_voxel=0.018,
    y_tip=-1.00, y_ped=0.60, y_hinge=-0.46,
    gape=math.radians(38),
    snout_up=math.radians(14),
    palate=0.22,
    jaw_w=0.96,
    # big, deep head (about a third of the length) on a short, deep body
    half_w=[(-1.00, 0.04), (-0.96, 0.12), (-0.86, 0.19), (-0.70, 0.235), (-0.48, 0.25), (-0.25, 0.235),
            (0.0, 0.19), (0.25, 0.12), (0.48, 0.06), (0.60, 0.04)],
    half_top=[(-1.00, 0.04), (-0.96, 0.10), (-0.86, 0.165), (-0.70, 0.22), (-0.48, 0.255),
              (-0.25, 0.25), (0.0, 0.20), (0.25, 0.13), (0.48, 0.065), (0.60, 0.045)],
    half_bot=[(-1.00, 0.04), (-0.96, 0.10), (-0.86, 0.17), (-0.70, 0.225), (-0.48, 0.25),
              (-0.25, 0.235), (0.0, 0.18), (0.25, 0.11), (0.48, 0.055), (0.60, 0.04)],
    center_z=[(-1.00, 0.02), (-0.6, 0.0), (0.0, 0.0), (0.60, 0.01)],
    pect=dict(y_front=-0.34, chord=0.13, sweep=0.44, span=0.66, droop=16, lead=0.08, trail=0.50, th=0.030),
    dorsal=dict(y0=-0.02, y1=0.20, height=0.22, rake=0.15),
    anal=dict(y0=0.28, y1=0.38, height=0.10, rake=0.06),
    caudal=dict(y_root=0.51, up=(0.98, 0.58), lo=(0.96, -0.54), fork=(0.75, 0.01), th=0.07),
    eye=dict(y=-0.82, up=0.30, r=0.028),
    opercle=0.10,
    rakers=dict(cols=26, rows=14, r=0.0025),
    colors=dict(lp.P["colors"], back=(0.24, 0.22, 0.20), flank=(0.45, 0.43, 0.39), belly=(0.84, 0.82, 0.76),
                fin_edge=(0.16, 0.14, 0.13)),
)


def main():
    lp.P = P
    lp.main()


if __name__ == "__main__":
    main()
