# Evolution data

Generates and checks the two data files behind evolving species (see `Assets/Scripts/Evolution`):

- `rules.py` → `Assets/Resources/Data/trait_rules.json`: tags for every species group (body plan:
  Arthropod, Vertebrate, Mammal…) and which tags each Function (morphology) / Behavior (ethology)
  item needs. Fails if a species group in `species.json` has no tags, so run it after adding species.
- `phylogeny.py`: the real tree of life behind the links. Every species group (and a few species
  on their own) has a path of nested clades from the root of the eukaryotes; each clade can have a
  one-sentence note, used as the description of links entering it.
- `links.py` → `Assets/Resources/Data/evolution.json`: which species evolve into which. Every species
  with a map model evolves from its closest relative in `phylogeny.py` that appears no later than it
  (the deepest shared clade, each step out on a side branch counting against it, then the latest),
  so earlier members of a clade stand in for its stem. Requirements (always items of the **origin**
  species' trees) and items granted on evolving are picked from the traits of the two groups and the
  target's genes, unless a hand-written link (CURATED) has the same pair. Checks that every
  requirement is acquirable by the origin and available by the target's period.

```sh
python3 tools/evolution/rules.py && python3 tools/evolution/links.py
```
