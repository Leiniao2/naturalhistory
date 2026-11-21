# Batch 2: 300 more species, spread evenly over the periods. Brief for the per-period agents

Repo: ~/Personal/naturalhistory (Unity hex-map natural-history game). Each agent adds the species of
ONE period and stages everything under `tools/newspecies/batch2/`; a coordinator merges the staged
files into the game data afterwards (`python3 tools/newspecies/merge.py --dir tools/newspecies/batch2`).
Other Claude sessions are working in this repo in parallel.

## How many
23 species for your period (the Cretaceous agent: 24). Exactly that many, all with `firstAge` = your period.

## Hard rules
- Do NOT edit `Assets/Resources/Data/*.json`, `Assets/Resources/Localization/*.json`,
  `tools/evolution/*.py`, any C# file, existing `tools/blender/*.py`, or other agents' staged files.
  Only create:
  - `tools/blender/<id>.py` (one per species; you may also add a NEW shared module
    `tools/blender/nh_b2_<period>_<plan>.py` if it helps several of yours; don't edit existing modules),
  - `Assets/Resources/Models/Species/<Model>.fbx` and its `.fbx.meta`,
  - `tools/newspecies/batch2/<period>.json`, `<period>_loc.json`, `<period>_groups.json`, `<period>_renders/`.
- Never `git commit`, `git add`, `git stash` or `git checkout`.
- Real animals only (genus/species attested in the literature). Check
  `tools/newspecies/batch2/existing_species.txt` (all species now in the game, by period) so you add NO
  duplicate species, and avoid a second species of a genus already present unless it is clearly
  different and well known. Model file names must not clash with existing FBX files in
  `Assets/Resources/Models/Species/` (check with `ls`).

## What to pick
A broad, balanced sample of the period's animal life, to fill gaps: different body plans and
lineages (invertebrates and vertebrates, sea, fresh water and land where the period has them),
sizes from small to large, herbivores, predators, filter feeders, scavengers. Prefer well-known,
characterful or scientifically important animals (famous fossils, key transitional forms, the
period's typical fauna). Small protists only if they are notable; at most 2 per period.

## Map style must fit the habitats (important)
A group is only placed where it can move: `Ground` animals on land habitats only (no SaltWater /
FreshWater), `Swim` / `Float` animals in water habitats (SaltWater / FreshWater; Wetland is fine
alongside), `Fixed` (sessile) where they grow, `Soar` / `Swarm` fliers anywhere in their habitats,
`Drift` for microscopic life. Amphibious animals: pick the style for where they mostly live and list
habitats accordingly (the existing crocodilians are Ground with Wetland + FreshWater: they walk on
Wetland tiles). Seabed crawlers (trilobites, crabs, eurypterids) are `Swim` with "SaltWater", like the
existing ones; sea urchins, crinoids and corals are `Fixed`. Look at similar existing species in
species.json and copy their style/habitat pattern.

## Combat stats (set on every new species)
`attack` 1–10, `defense` 1–10, `hp` 3–15, `moves` 1–4. BASE values: the game multiplies attack,
defense and hp by its era factor (×1.2 per period after the Ediacaran), so compare only within your
period. Typical: attack 2–7, defense 1–4, hp 5–8, moves 1–2 (sessile/drifting 1, walkers/swimmers
2, fliers 3). Give each a profile that fits the animal (an armoured grazer: defense high, attack
low; a sprinting predator: attack and moves high, hp low...). Its genes, description and stats
should tell the same story. Combat rules for context: damage dealt = attacker attack / defender
defense × attacker era factor; damage taken back = defender defense / attacker attack × defender
era factor; animals more than 10× apart in size can't fight; hunters attacking listed prey eat it
outright; moves = actions per turn; groups without food nearby starve; only stationed groups heal.

## Species entry (`tools/newspecies/batch2/<period>.json`: a JSON array of objects)
Same schema as `Assets/Resources/Data/species.json` (read a few entries there for style):
- `id`: lower snake_case binomial, e.g. `smilodon_populator` (unique in the whole game)
- `commonName` (English, as players would know it), `scientificName`, `kingdom`: "Animalia"
- `group`: reuse an existing group from `tools/newspecies/batch2/existing_groups.txt` whenever it
  fits (exact spelling); only invent a new one when none fits, and then define it (see below)
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
- `attack`, `defense`, `hp`, `moves`
- `genes`: 3–6 of: carnivory swimming_speed armor_thickness vision_acuity reproduction_rate
  land_speed filter_feeding herbivory chemoreception group_defense heat_tolerance
  asexual_reproduction lateral_line camouflage flight_capability burrowing climbing omnivory
  cold_tolerance regeneration parental_care toxin_production endothermy decomposition clutch_size
  electroreception hibernation nectar_feeding, each `{"gene": id, "expression": 0..1}`
- `description`: 2–4 factual English sentences (size, look, how it lived, what made it special).
  No museum or fossil-site jargon.

## 3D model
Procedural low-poly Blender models like the existing ones: read `tools/blender/nh_model.py` and
2–3 scripts of similar animals (the period modules `nh_<per>_*.py`: nh_ord_*, nh_sil_*, nh_dev_*,
nh_car_*, nh_per_*, nh_tri_*, nh_jur_*, nh_cre_*, nh_pal_*, nh_neo_*, and single-species scripts).
Conventions: faces -Y, pivot at body centre (ground animals: see nh_model's docstring), vertex
colours, export via `nh.run(build, "<Model>")` to `Assets/Resources/Models/Species/<Model>.fbx`.
Build with `blender --background --python tools/blender/<id>.py -- --render tools/newspecies/batch2/<period>_renders/<id>.png`
and LOOK at the render (Read tool) to check it reads as the animal: correct body plan,
recognisable silhouette, distinctive colours. Reuse shared body-plan helpers (import existing
nh_* modules, don't edit them) but make each species recognisably itself.
`.fbx.meta`: copy the `.fbx.meta` of a similar existing model next to your FBX and replace its
`guid:` value with a fresh `python3 -c "import uuid;print(uuid.uuid4().hex)"`.

## Localization (`tools/newspecies/batch2/<period>_loc.json`)
`{"zh": {"<English text>": "<translation>", ...}, "ja": {...}, "ko", "de", "fr", "it", "es", "pt",
"ru"}`, keys = each species' `commonName` and `description` (exact English strings) and any new
group names. Chinese uses the established Chinese names of the animals (e.g. 刃齿虎, 甲龙) and the
word 进化 for evolution; other languages their usual names (often the genus name). pt is Brazilian.

## New groups (`tools/newspecies/batch2/<period>_groups.json`; `{}` if none)
`{"<Group>": {"tags": "<python expr as in tools/evolution/rules.py `groups`>", "path": "<python expr
as in tools/evolution/phylogeny.py GROUPS>"}}`, e.g.
`{"Glyptodont": {"tags": "MAMMAL+['Armoured']", "path": "PLACENTAL + '/Xenarthra/Cingulata/Glyptodontidae'"}}`.
Use the constants those files define (read them); keep tags to ones rules.py already uses. The
path places the group in the real tree of life: the evolution links are generated from it.

## Before finishing
- `python3 -c "import json;json.load(open('tools/newspecies/batch2/<period>.json'))"` (and _loc, _groups)
- every `model` has its FBX + meta, every species has all 9 translations of name and description,
  ids are unique and not in existing_species.txt, map style fits habitats
- Report (short): the species list (id, group, a/d/hp/m), any new groups, any model you're unsure of.
