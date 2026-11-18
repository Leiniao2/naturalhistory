# 200 new species with distinctive combat profiles: brief for the per-period build agents

Repo: ~/Personal/naturalhistory (Unity hex-map natural-history game). Each agent adds the species of
ONE period (or two) and stages everything under `tools/newspecies/`; a coordinator merges the staged
files into the game data afterwards. Other Claude sessions are working in this repo in parallel.

## Hard rules
- Do NOT edit `Assets/Resources/Data/*.json`, `Assets/Resources/Localization/*.json`,
  `tools/evolution/*.py`, any C# file, or other agents' staged files. Only create:
  - `tools/blender/<id>.py` (one per species; you may also add a new shared module
    `tools/blender/nh_<period>_<plan>.py` if it helps several of yours),
  - `Assets/Resources/Models/Species/<Model>.fbx` and its `.fbx.meta`,
  - `tools/newspecies/<period>.json`, `<period>_loc.json`, `<period>_groups.json`, `<period>_renders/`.
- Never `git commit`, `git add`, `git stash` or `git checkout`.
- Real animals only (genus/species attested in the literature), `firstAge` = your period. Check
  `tools/newspecies/existing_species.txt` (all 551 species now in the game, by period, with group)
  so you add NO duplicate species and preferably no second species of a genus already present.

## What to pick
Animals that stand out in combat terms, so players have interesting choices. Aim for a mix in
each period, roughly: ~30% hard hitters (apex predators, venom, crushing jaws, electric organs),
~25% tanks (heavy armour, shells, spines, plates, sheer bulk with huge HP), ~25% fast movers
(sprinters, fast swimmers, gliders, fliers: moves 3–4), ~20% odd specialists (regenerators,
toxic prey, burrowers, swarms, ambushers). Varied sizes, habitats (sea, fresh water, land), diets
and map styles. Prefer characterful, recognisable or scientifically important animals.

## Combat stats (set explicitly on every new species)
`attack` 1–10, `defense` 1–10, `hp` 3–15, `moves` 1–4. These are BASE values before the game's
era factor (×1.2 per period), so compare only within your period. Typical existing animals sit
around attack 2–7, defense 1–4, hp 5–8, moves 1–2 (sessile/drifting 1, walkers/swimmers 2, fliers
3). Make each new species clearly distinctive in at least one stat (e.g. attack 9–10, defense
8–10, hp 12–15, or moves 4), with trade-offs elsewhere (a tank is slow and weak in attack, a
sprinter has low HP, etc.). Its genes, description and stats should tell the same story.
Combat rules for context: damage = attack/defense × (attacker size / defender size) × era;
animals more than 10× apart in size can't fight; hunters attacking listed prey eat it outright;
moves = actions per turn (move a tile / attack / reproduce); groups without food nearby starve.

## Species entry (`tools/newspecies/<period>.json`: a JSON array of objects)
Same schema as `Assets/Resources/Data/species.json` (read a few entries there for style):
- `id`: lower snake_case binomial, e.g. `smilodon_populator` (unique in the whole game)
- `commonName` (English, as players would know it), `scientificName`, `kingdom`: "Animalia"
- `group`: reuse an existing group from `tools/newspecies/existing_groups.txt` whenever it fits
  (exact spelling); only invent a new one when none fits, and then define it (see below)
- `firstAge` / `lastAge` (period names: Ediacaran Cambrian Ordovician Silurian Devonian
  Carboniferous Permian Triassic Jurassic Cretaceous Paleogene Neogene Quaternary; lastAge ""
  if still alive today)
- `habitats`: from SaltWater FreshWater Wetland Rainforest Plain Savanna Steppe Hill Mountain
  Desert Tundra
- `diet`: Herbivore Carnivore Omnivore Scavenger Parasite "Filter feeder" Detritivore;
  hunters: `prey` (species ids or group names they eat, and/or "Small animals"); omnivores
  `mainDiet`; parasites `hosts`; optional `tags` (Flyer, Surfacer, Burrower, Pollinator)
- `sizeCm` (adult body length), `startingPopulation`, `playable`: true
- `model`: "Models/Species/<PascalCaseName>" (matches your FBX file name)
- `mapStyle`: Ground Swim Fixed Soar Drift Swarm Float; optional `mapGait` (Walk Hop Slither Run),
  `mapLegs`, `mapHip`, `colonySize`, `mapScale`, `wingBeat`, `wingRoot`, `mapBackward`,
  `mapUndulate`, `mapAttack` (Charge Bite Pounce Strike Dive Sting Ram Shock Snap Engulf Lash),
  `mapDefense` (Brace Rear Scatter Coil Hide Ink Tighten Mob Puff), as similar species do
- `attack`, `defense`, `hp`, `moves` (see above)
- `genes`: 3–6 of: carnivory swimming_speed armor_thickness vision_acuity reproduction_rate
  land_speed filter_feeding herbivory chemoreception group_defense heat_tolerance
  asexual_reproduction lateral_line camouflage flight_capability burrowing climbing omnivory
  cold_tolerance regeneration parental_care toxin_production endothermy decomposition clutch_size
  electroreception hibernation nectar_feeding, each `{"gene": id, "expression": 0..1}`
- `description`: 2–4 factual English sentences (size, look, how it lived, what made it special;
  mention what makes it tough / fast / dangerous). No museum or fossil-site jargon.

## 3D model
Procedural low-poly Blender models like the existing ones: read `tools/blender/nh_model.py` and
2–3 scripts of similar animals in your period (e.g. `ankylosaurus_magniventris.py`, and the period
modules `nh_<per>_*.py`: nh_ord_*, nh_sil_*, nh_dev_*, nh_car_*, nh_per_*, nh_tri_*, nh_jur_*,
nh_cre_*, nh_pal_*, nh_neo_*). Conventions: faces -Y, pivot at body centre, vertex colours, export
via `nh.run(build, "<Model>")` to `Assets/Resources/Models/Species/<Model>.fbx`. Build with
`blender --background --python tools/blender/<id>.py -- --render tools/newspecies/<period>_renders/<id>.png`
and look at the render to check it reads as the animal (correct body plan, recognisable
silhouette, distinctive colours). Reuse shared body-plan helpers rather than writing every
model from scratch, but make each species recognisably itself (armour, horns, fins, colours…).
`.fbx.meta`: copy the `.fbx.meta` of a similar existing model next to your FBX and replace its
`guid:` value with a fresh `python3 -c "import uuid;print(uuid.uuid4().hex)"`.

## Localization (`tools/newspecies/<period>_loc.json`)
`{"zh": {"<English text>": "<translation>", ...}, "ja": {...}, "ko", "de", "fr", "it", "es", "pt",
"ru"}`, keys = each species' `commonName` and `description` (exact English strings) and any new
group names. Chinese uses the established Chinese names of the animals (e.g. 刃齿虎, 甲龙); other
languages their usual names (often the genus name).

## New groups (`tools/newspecies/<period>_groups.json`; `{}` if none)
`{"<Group>": {"tags": "<python expr as in tools/evolution/rules.py `groups`>", "path": "<python expr
as in tools/evolution/phylogeny.py GROUPS>"}}`, e.g.
`{"Glyptodont": {"tags": "MAMMAL+['Armoured']", "path": "PLACENTAL + '/Xenarthra/Cingulata/Glyptodontidae'"}}`.
Use the constants those files define (read them); keep tags to ones rules.py already uses.

## Before finishing
- `python3 -c "import json;json.load(open('tools/newspecies/<period>.json'))"` (and _loc, _groups)
- every `model` has its FBX + meta, every species has all 9 translations of name and description,
  ids are unique and not in existing_species.txt
- Report: the species list (id, group, stats a/d/hp/m, one-line role), any new groups, any model
  you're unsure of. Keep the report short.
