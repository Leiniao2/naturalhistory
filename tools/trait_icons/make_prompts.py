"""
Prompts for the paintings of the Functions (morphology.json) and Behaviors (ethology.json) items,
shown on their cards in the trees (UI/TreePanel, UI/TraitIcons).

Generated with Google Flow like the species portraits (tools/portraits), in the same painterly
style but as a card illustration of the trait: the organ, body part or behaviour itself, shown on
a typical animal that has it. Writes prompts.json: {"style", "prompts": [{"id", "tree", "item",
"prompt"}]}; ids are "f_<item>" (Functions) and "b_<item>" (Behaviors), the downloaded file names
(batch.py, fetch.js, import.sh).
Usage: python3 tools/trait_icons/make_prompts.py
"""

import json
import os
import re

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
DATA = os.path.join(ROOT, "Assets", "Resources", "Data")
OUT = os.path.join(os.path.dirname(__file__), "prompts.json")

STYLE = (
    "Painterly concept-art card illustration in the style of the culture and technology illustrations of "
    "the strategy game Humankind; visible confident brush strokes, semi-realistic stylised forms, saturated "
    "and vibrant colours, clean natural daylight with a soft rim light. NO sepia, NO golden-brown tint. One "
    "clear, readable subject filling most of the frame, centred, recognisable even as a small thumbnail; "
    "a soft, loosely painted backdrop. Scientifically accurate anatomy and natural colouring. Square image. "
    "No text, no letters, no labels, no UI, no frame, no logo."
)

KIND = {"morphology": "body part, organ or body system", "ethology": "behaviour"}


def subject(tree, branch, node):
    desc = node["description"].strip()
    # "(honeybees)", "(Anomalocaris)": the description already names who does it
    return (f"{node['displayName']}: an illustration of the animal {KIND[tree]} \"{node['displayName']}\" "
            f"({branch['displayName']}). {desc} Show it clearly on a typical animal that has it"
            + (", the relevant body part emphasised, in a cutaway or close-up where it is internal" if tree == "morphology"
               else ", caught in the act") + ".")


def main():
    prompts = []
    for tree, prefix in (("morphology", "f"), ("ethology", "b")):
        data = json.load(open(os.path.join(DATA, f"{tree}.json"), encoding="utf-8"))
        branches = {b["id"]: b for b in data["branches"]}
        for n in data["nodes"]:
            prompts.append({"id": f"{prefix}_{n['id']}", "tree": tree, "item": n["id"],
                            "prompt": subject(tree, branches[n["branch"]], n)})
    json.dump({"style": STYLE, "prompts": prompts}, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(len(prompts), "prompts ->", OUT)


if __name__ == "__main__":
    main()
