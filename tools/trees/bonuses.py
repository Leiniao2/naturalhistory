#!/usr/bin/env python3
"""Gives every Functions (morphology.json) and Behaviors (ethology.json) item a stat bonus that
the player's groups of a species get once the species has it (World/TraitBonuses.cs):

    "bonus": {"attack": 1} / {"defense": 1} / {"hp": 2} / {"moves": 1}

What an item gives follows its branch: senses, hunting and fighting add attack; armour, the immune
system, hiding and group defence add defence; organs that keep the body running, breeding and rest
add HP; a few ways of getting about (fins, legs, wings, long migrations) add an action a turn.
The free root items (cost 0, every species starts with them) give nothing. In game the bonus is
multiplied by the species' era factor like its base stats (CombatStats.Era).

Edits the two JSON files in place (they are hand-tuned, so build_trees.py isn't re-run); safe to
run again.   python3 tools/trees/bonuses.py
"""

import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / "Assets" / "Resources" / "Data"

AMOUNT = {"attack": 1, "defense": 1, "hp": 2, "moves": 1}

BRANCH = {
    "morphology": {
        "nervous": "attack", "circulatory": "hp", "respiratory": "hp", "digestive": "hp",
        "excretory": "defense", "endocrine": "hp", "reproductive": "hp", "locomotor": "attack",
        "immune": "defense", "integument": "defense",
    },
    "ethology": {
        "foraging": "attack", "antipredator": "defense", "reproductive": "hp", "social": "defense",
        "agonistic": "attack", "communication": "defense", "migration": "hp", "nest_building": "defense",
        "maintenance": "hp", "resting": "hp",
    },
}

# a tile further a turn: the big steps in getting about
MOVES = {"tail_fin", "terrestrial_legs", "insect_wings", "feathered_wings",
         "seasonal_migration", "mass_dispersal", "ocean_migration", "nomadic_herds"}


def main():
    for tree in ("morphology", "ethology"):
        path = DATA / f"{tree}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        counts = {}
        for n in data["nodes"]:
            if not n["prerequisites"] or n["cost"] == 0:
                n.pop("bonus", None)
                continue
            stat = "moves" if n["id"] in MOVES else BRANCH[tree][n["branch"]]
            n["bonus"] = {stat: AMOUNT[stat]}
            counts[stat] = counts.get(stat, 0) + 1
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(tree, counts)


if __name__ == "__main__":
    main()
