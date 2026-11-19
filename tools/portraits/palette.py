"""
Portrait backdrop colours, shared by make_prompts.py (asks new paintings for them) and
recolor.py (turns the existing paintings to them):

  - The founding protists' lines: the protists descending from each founder get its colour.
  - Other water-only species: one of several water colours, chosen per species, so the sea isn't
    always teal.
"""

import hashlib

# founding protist -> (hue in degrees, words for the prompt)
LINES = {
    "thecamonas_trahens":       (350.0, "rose-red tinted"),  # Amorphea
    "telonema_subtile":         (118.0, "green tinted"),     # Diaphoretickes
    "malawimonas_jakobiformis": (228.0, "cobalt-blue tinted"),  # Excavata
}

# (name, hue or None to keep teal, saturation scale, value scale, words for the prompt), weight
WATERS = [
    (("teal",    None,  1.00, 1.00, "vivid turquoise and teal"), 2),
    (("cobalt",  218.0, 1.05, 0.95, "deep cobalt-blue"), 3),
    (("indigo",  245.0, 1.00, 0.85, "dark indigo-blue"), 2),
    (("dusk",    280.0, 0.72, 0.85, "violet dusk-lit"), 2),
    (("emerald", 150.0, 0.78, 0.88, "emerald-green"), 2),
]

PROTIST_GROUPS = {"Apusomonad", "Telonemid", "Malawimonad", "Heliozoan", "Ciliate", "Amoebozoan", "Choanoflagellate",
                  "Gregarine", "Heterolobosean", "Euglenid", "Foraminifer", "Fusulinid", "Radiolarian", "Dinoflagellate",
                  "Archamoeba", "Kinetoplastid", "Diplomonad", "Parabasalid", "Haemosporidian"}


def is_protist(d):
    g = d.get("group") or ""
    return g in PROTIST_GROUPS or "amoeba" in g.lower() or "mould" in g.lower()


def aquatic(d):
    """Lives only in the sea or fresh water (painted under water)"""
    h = set(d.get("habitats") or [])
    return bool(h) and h <= {"SaltWater", "FreshWater"}


def water_for(sid):
    total = sum(w for _, w in WATERS)
    h = int(hashlib.md5(sid.encode()).hexdigest(), 16) % total
    for water, w in WATERS:
        if h < w:
            return water
        h -= w
    return WATERS[0][0]


def line_of(species, links):
    """species id -> founder id, for the founders and the protists of their lines"""
    kids = {}
    for l in links:
        kids.setdefault(l["from"], []).append(l["to"])
    result = {}
    for founder in LINES:
        stack, seen = [founder], set()
        while stack:
            s = stack.pop()
            if s in seen:
                continue
            seen.add(s)
            if s == founder or is_protist(species.get(s, {})):
                result.setdefault(s, founder)
            stack.extend(kids.get(s, []))
    return result
