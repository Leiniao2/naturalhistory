"""
Small helper for the second Silurian batch (pterygotus_anglicus.py, erettopterus_bilobus.py,
deiphon_forbesi.py, arctinurus_boltoni.py ...): lets a species script reuse a shared
body-plan builder (nh_sil_eurypterid, nh_sil_trilobite, ...) and still add its own parts in
the builder's own coordinates, just before the mesh becomes an object (and is re-centred).

  obj = with_extras(lambda: eu.build(SPEC), lambda mb: mb.add(...))
"""

import nh_model as nh


def with_extras(build_fn, extras_fn):
    orig = nh.MeshBuilder.to_object
    done = {"n": 0}

    def patched(self, name, roughness=0.6):
        if done["n"] == 0:
            done["n"] = 1
            extras_fn(self)
        return orig(self, name, roughness)

    nh.MeshBuilder.to_object = patched
    try:
        return build_fn()
    finally:
        nh.MeshBuilder.to_object = orig
