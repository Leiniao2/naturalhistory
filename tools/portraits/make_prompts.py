"""
Prompts for the species portraits (static paintings used in the evolution tree and other UI).

Generated with Google Flow (Nano Banana) in the style chosen on 2026-11-17: a heroic painterly
concept-art portrait like Humankind's culture illustrations, but saturated and in clean daylight.
Writes prompts.json: {"style", "prompts": [{"id", "name", "prompt"}]} in species.json order;
the style (STYLE) is sent once per batch and applies to every subject prompt (batch.py).
Usage: python3 tools/portraits/make_prompts.py
"""

import json
import os
import re

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
SPECIES = os.path.join(ROOT, "Assets", "Resources", "Data", "species.json")
OUT = os.path.join(os.path.dirname(__file__), "prompts.json")

STYLE = (
    "Heroic painterly concept-art portrait in the style of the culture illustrations of the strategy "
    "game Humankind; visible confident brush strokes, semi-realistic stylised forms, saturated and "
    "vibrant colours. Clean natural daylight, cool/warm lighting balance with rim light. NO sepia, NO "
    "golden-brown tint, NO yellow haze. The animal (or organism) is the clear hero subject in the foreground, "
    "whole body, filling most of the frame, slightly low camera angle, in a proud characteristic pose. "
    "Soft, loosely painted atmospheric backdrop of its habitat. Anatomy scientifically accurate, "
    "natural realistic colouring. Square image. No text, no UI, no frame, no logo."
)

AGE = {
    "Ediacaran": "Ediacaran", "Cambrian": "Cambrian", "Ordovician": "Ordovician",
    "Silurian": "Silurian", "Devonian": "Devonian", "Carboniferous": "Carboniferous",
    "Permian": "Permian", "Triassic": "Triassic", "Jurassic": "Jurassic",
    "Cretaceous": "Cretaceous", "Paleogene": "Paleogene", "Neogene": "Neogene",
    "Quaternary": "Pleistocene-to-present",
}

HABITAT = {
    "SaltWater": "a bright sunlit sea with vivid turquoise and cobalt blue water",
    "FreshWater": "a clear river or lake with teal water and green plants",
    "Wetland": "a lush green swamp with clear shallow water",
    "Rainforest": "a lush emerald-green forest",
    "Plain": "open green plains under a crisp blue sky",
    "Savanna": "a sunny savanna under a blue sky",
    "Steppe": "a wide grassy steppe under a blue sky",
    "Hill": "green rolling hills under a blue sky",
    "Mountain": "rocky mountains under a crisp blue sky",
    "Desert": "a bright desert with blue sky",
    "Tundra": "a bright snowy tundra under a blue sky",
}

# early land had no flowering plants or grass: keep the backdrop plausible for the age
OLD_LAND = {"Silurian", "Devonian", "Carboniferous", "Permian", "Triassic", "Jurassic"}

POSE = {
    "Swim": "",
    "Drift": "drifting in the water",
    "Float": "floating at the surface",
    "Fixed": "growing in place",
    "Soar": "in flight, wings spread",
    "Swarm": "in flight",
    "Ground": "",
}


# extra direction for species the first pass got wrong (shape, or the animal lost in the scene)
FIXES = {
    "rhyniella_praecursor": "It is a springtail (Collembola), NOT a beetle, cockroach or crayfish: a tiny soft-bodied, "
                            "wingless hexapod with a plump elongated body, short four-segmented antennae, three pairs of "
                            "short legs and a forked jumping organ (furcula) folded under its tail; shown huge in close-up "
                            "on a moss-covered Devonian plant stem.",
    "selenidium_pendula":   "It is ONE single cell, not a worm: smooth, slender and elongated, its surface marked with fine "
                            "lengthwise folds (no rings or segments, no head, no legs), translucent with a visible nucleus.",
    "longisquama_insignis": "Close-up: the small lizard-like reptile fills most of the frame and is clearly visible, sharp and "
                            "in focus, with its row of long, tall, feather-like plumes standing up along its back; the "
                            "plants are only a soft, blurred background.",
}


# internal parasites: painted inside their host, not in the landscape their hosts live in
INSIDE = {
    "selenidium_pendula":       "inside the gut of a marine worm: a glistening tube of pink-red gut wall and folds, lit softly from within",
    "entamoeba_histolytica":    "inside a primate's large intestine: moist pink-red gut lining with folds and mucus, softly lit",
    "giardia_duodenalis":       "inside a mammal's small intestine, clinging to a carpet of finger-like pink villi, softly lit",
    "trichomonas_gallinae":     "inside a bird's throat: moist pink mucous lining, softly lit",
    "trypanosoma_brucei":       "in a mammal's bloodstream: flowing red plasma among red blood cells inside a vessel",
    "plasmodium_falciparum":    "in human blood: inside and among red blood cells in a flowing vessel",
    "trichonympha_campanula":   "inside a termite's hindgut, crowded with wood fragments and other microbes, warm amber-pink gut wall",
    "trichonympha_collaris":    "inside a termite's hindgut, crowded with wood fragments and other microbes, warm amber-pink gut wall",
    "taenia_solium":            "inside a human small intestine: the scolex hooked into pink folds and villi of the gut wall, the long ribbon trailing through it",
    "taenia_saginata":          "inside a human small intestine: the scolex anchored in pink folds and villi of the gut wall, the very long ribbon trailing through it",
    "echinococcus_granulosus":  "inside a dog's small intestine, among pink finger-like villi",
    "spirometra_mansoni":       "inside a cat's small intestine, among pink folds and villi of the gut wall",
    "demodex_folliculorum":     "inside a human hair follicle: head-down in a narrow sheath of skin beside the hair shaft, magnified",
    "otodectes_cynotis":        "deep in a cat's ear canal among skin flakes, wax and fine hairs, magnified",
}


def size_text(cm):
    if cm is None:
        return ""
    if cm < 0.1:
        return f"microscopic, about {cm * 10000:.0f} micrometres"
    if cm < 1:
        return f"about {cm * 10:.0f} mm long"
    if cm < 100:
        return f"about {cm:g} cm long"
    return f"about {cm / 100:g} m long"


def backdrop(s):
    if s["id"] in INSIDE:
        return INSIDE[s["id"]]
    age = s.get("firstAge")
    habitats = s.get("habitats") or ["SaltWater"]
    h = habitats[0]
    text = HABITAT.get(h, "its natural habitat")
    era = AGE.get(age, age)
    if s.get("kingdom") == "Protista":
        return f"a magnified view inside a drop of clear blue-green {('sea' if h == 'SaltWater' else 'fresh')} water, with soft out-of-focus particles"
    if h not in ("SaltWater", "FreshWater") and age in OLD_LAND:
        text += " (only ferns, horsetails, cycads and conifers; no grass or flowers)"
    if age in ("Ediacaran", "Cambrian", "Ordovician") and h == "SaltWater":
        text = "a bright shallow sea floor with vivid turquoise and cobalt blue water (microbial mats, no fish or modern plants)"
    return f"{text}, {era}"


def prompt(s):
    name = s["commonName"]
    sci = s.get("scientificName") or ""
    who = f"{name} ({sci})" if sci and sci != name else name
    inside = s["id"] in INSIDE
    pose = "" if inside else POSE.get(s.get("mapStyle") or "", "")
    bits = [b for b in (pose, size_text(s.get("sizeCm"))) if b]
    group = (s.get("group") or "animal").lower()
    head = f"{who}, {'an' if group[0] in 'aeiou' else 'a'} {group}" + (f", {', '.join(bits)}" if bits else "")
    head += f", {backdrop(s)} (stylised and clean, not gory)." if inside else f", in {backdrop(s)}."
    fix = FIXES.get(s["id"])
    return f"{head} Appearance: {short(s.get('description') or '')}" + (f" {fix}" if fix else "")


def short(desc, limit=260):
    """The first sentences of the description, up to about limit characters."""
    out = ""
    for sentence in re.split(r"(?<=[.;])\s+", desc.strip()):
        if out and len(out) + len(sentence) > limit:
            break
        out = f"{out} {sentence}".strip()
    return out


def main():
    species = json.load(open(SPECIES, encoding="utf-8"))["species"]
    out = [{"id": s["id"], "name": s["commonName"], "prompt": prompt(s)} for s in species]
    json.dump({"style": STYLE, "prompts": out}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(out), "prompts ->", OUT)


if __name__ == "__main__":
    main()
