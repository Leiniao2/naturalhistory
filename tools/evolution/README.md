# Evolution data

Generates and checks the two data files behind evolving species (see `Assets/Scripts/Evolution`):

- `rules.py` → `Assets/Resources/Data/trait_rules.json`: tags for every species group (body plan:
  Arthropod, Vertebrate, Mammal…) and which tags each Function (morphology) / Behavior (ethology)
  item needs. Fails if a species group in `species.json` has no tags, so run it after adding species.
- `links.py` → `Assets/Resources/Data/evolution.json`: which species evolve into which, the items
  required (always items of the **origin** species' trees), and items granted on evolving. Checks
  that every requirement is acquirable by the origin and available by the target's period, and that
  targets have a map model that can move.

```sh
python3 tools/evolution/rules.py && python3 tools/evolution/links.py
```
