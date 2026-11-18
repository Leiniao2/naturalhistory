import json, sys
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Assets", "Resources", "Data") + os.sep
AGES = "Ediacaran Cambrian Ordovician Silurian Devonian Carboniferous Permian Triassic Jurassic Cretaceous Paleogene Neogene Quaternary".split()
# Each species evolves from its closest relative in the real tree of life (phylogeny.py) that
# appears no later than it. The links below were written by hand: where the tree has the same
# origin and target, their requirements, grants and description are used; the rest are worked
# out from the species' traits (trait_rules.json) and described by the clade the target enters.
#
# from, to, functions required, behaviors required, functions granted, behaviors granted, why
CURATED = [
 # --- From the Ediacaran ---
 ("ikaria_wariootia","myllokunmingia_fengjiaoa",["through_gut","coelom","nerve_cords"],["burrowing_escape"],["notochord"],[],"Ikaria-like burrowers were among the first animals with a front, a back and a gut: the ancestry of chordates and so of the first vertebrates."),
 ("spriggina_floundersi","hallucigenia",["segmentation","cephalisation"],["hiding"],["compound_eyes"],[],"A segmented Ediacaran animal standing in for the soft-bodied ancestors of lobopodians and arthropods."),
 ("kimberella_quadrata","cameroceras",["radula","through_gut"],["patch_foraging"],["camera_eyes"],[],"Kimberella scraped mats with a mollusc-like feeding organ; molluscs went on to build shells and swim as cephalopods."),
 # --- Chordates and fish ---
 ("pikaia","myllokunmingia_fengjiaoa",["notochord","pharyngeal_slits"],["light_following"],["myomeres"],[],"One of the oldest known vertebrates, from the Chengjiang fauna: a skull and paired eyes around the chordate nerve cord."),
 ("myllokunmingia_fengjiaoa","dunkleosteus_terrelli",["jaws","dermal_armour","paired_fins"],["active_predation","pursuit_hunting"],["gill_arches"],["territoriality"],"Jaws evolved from gill arches; armoured placoderms were the first giant predators."),
 ("myllokunmingia_fengjiaoa","tiktaalik_roseae",["jaws","paired_fins","lungs"],["land_excursions"],["lobe_fins"],["basking"],"Lobe-finned fish with lungs and sturdy fins hauled out in shallow Devonian swamps."),
 ("myllokunmingia_fengjiaoa","mola_mola",["jaws","swim_bladder","gill_cover"],["schooling"],["endochondral_bone"],[],"Ray-finned fish took over the open sea."),
 ("mola_mola","ornate_butterflyfish",["chromatophores","acid_stomach"],["pair_bonds"],["structural_colour"],["patch_foraging"],"Reef fish specialised on coral polyps."),
 ("mola_mola","moorish_idol",["chromatophores","spiral_valve"],["schooling"],["structural_colour"],[],"Reef fish grazing sponges and algae."),
 ("mola_mola","cheilopogon_pinnatibarbatus",["paired_fins","swim_bladder"],["startle_escape"],[],["gliding"],"Flying fish escape predators by gliding on enlarged fins."),
 ("mola_mola","electrophorus_electricus",["electroreceptors","lungs"],["electric_signals"],["labyrinth_organ"],["venom_hunting"],"Knifefish turned muscle into electric organs; the electric eel gulps air."),
 ("dunkleosteus_terrelli","otodus_megalodon",["teeth","tooth_replacement","electroreceptors"],["pursuit_hunting","ambush_hunting"],["placoid_scales","rectal_gland"],[],"Sharks keep replacing their teeth all their lives; megalodon was the largest."),
 ("dunkleosteus_terrelli","mobula_alfredi",["electroreceptors","filter_apparatus"],["vertical_migration"],["claspers"],["cleaning_stations"],"Rays flattened out; mantas filter plankton."),
 # --- Onto land ---
 ("tiktaalik_roseae","ichthyostega",["lobe_fins","digits","weight_bearing_girdles"],["land_excursions","basking"],["throat_pumping"],[],"Early tetrapods had digits and could prop themselves up on land."),
 ("ichthyostega","hylonomus_lyelli",["amniotic_egg","keratin_scales","rib_breathing"],["shelter_resting","egg_sites"],["metanephros"],[],"The amniotic egg freed reptiles from the water."),
 ("ichthyostega","cane_toad",["toxic_skin","throat_pumping","aquatic_larvae"],["warning_colours","synchronised_spawning"],["metamorphosis_hormones"],[],"Toads defend themselves with poison glands."),
 ("ichthyostega","red_eyed_tree_frog",["aquatic_larvae","toxic_skin"],["egg_sites","nocturnal_refuge"],[],["startle_escape"],"Tree frogs lay eggs on leaves over water."),
 # --- Reptiles ---
 ("hylonomus_lyelli","american_alligator",["osteoderms","secondary_palate","four_chambered_heart"],["ambush_hunting","egg_guarding"],["temperature_sex"],[],"Crocodilians are archosaurs, closer to birds than to lizards."),
 ("hylonomus_lyelli","green_iguana",["uric_acid","salt_glands"],["basking","plant_feeding"],["hindgut_fermentation"],["autotomy"],"Lizards; iguanas ferment leaves in their gut."),
 ("hylonomus_lyelli","crotalus_mitchellii",["venom_glands","keratin_scales"],["ambush_hunting","skin_shedding"],[],["threat_display"],"Pit vipers sense heat and inject venom."),
 ("hylonomus_lyelli","green_sea_turtle",["salt_glands","rib_breathing"],["natal_homing","ocean_migration"],["beak","hard_eggshell"],[],"Turtles traded teeth for a beak; sea turtles return to the beach where they hatched."),
 ("hylonomus_lyelli","brachiosaurus",["upright_stance","air_sacs","raised_metabolism"],["herding","nesting"],["gastroliths","hollow_bones"],[],"Dinosaurs stood upright; air sacs let sauropods grow enormous."),
 ("brachiosaurus","triceratops_horridus",["horns","dental_batteries"],["herding","head_butting"],["beak"],[],"Ceratopsians sliced plants with batteries of teeth behind a beak."),
 ("brachiosaurus","ankylosaurus_magniventris",["osteoderms","upright_stance"],["tail_weapons"],["beak"],["rolling_up"],"Armoured dinosaurs with a bony tail club."),
 ("brachiosaurus","tyrannosaurus_rex",["hollow_bones","protofeathers","endothermy_node"],["pack_hunting","stalking"],["teeth"],["male_combat"],"Theropods: fast, warm-blooded predators, many of them feathered."),
 ("brachiosaurus","quetzalcoatlus",["hollow_bones","protofeathers","endothermy_node"],["gliding"],["air_sacs"],["roosting"],"Pterosaurs flew on wings of skin; Quetzalcoatlus was as big as a giraffe."),
 ("tyrannosaurus_rex","spinosaurus_aegyptiacus",["secondary_palate","salt_glands"],["ambush_hunting","patch_foraging"],[],["schooling"],"A river-dwelling theropod that hunted fish."),
 # --- Birds (from theropods) ---
 ("tyrannosaurus_rex","haliaeetus_leucocephalus",["feathers","feathered_wings","air_sacs"],["nesting","pursuit_hunting"],["syrinx","beak"],[],"Birds are living theropod dinosaurs."),
 ("tyrannosaurus_rex","american_avocet",["feathers","feathered_wings"],["nesting","patch_foraging"],["syrinx","beak"],[],"Shorebirds probe mud with long bills."),
 ("haliaeetus_leucocephalus","california_condor",["turbinates","acid_stomach"],["scavenging","communal_roosts"],[],["seasonal_dormancy"],"Vultures soar for hours looking for carcasses."),
 ("haliaeetus_leucocephalus","wandering_albatross",["salt_glands"],["ocean_migration","colonial_nesting"],[],["sleeping_on_the_wing"],"Albatrosses glide across whole oceans."),
 ("haliaeetus_leucocephalus","pelecanus_onocrotalus",["salt_glands"],["colonial_nesting","pack_hunting"],[],[],"Pelicans fish together, herding shoals."),
 ("american_avocet","phoenicopterus_roseus",["filter_apparatus","salt_glands"],["colonial_nesting","courtship_dance"],[],[],"Flamingos filter shrimp with an upside-down bill."),
 ("american_avocet","mandarin_duck",["filter_apparatus"],["pair_bonds","courtship_dance"],[],[],"Ducks dabble and pair for the season."),
 ("american_avocet","sunbittern",["structural_colour"],["eyespot_display"],[],["distraction_display"],"Sunbitterns flash eyespots on their wings."),
 ("american_avocet","superb_lyrebird",["syrinx"],["learned_song","courtship_dance"],[],[],"Songbirds learn their songs; lyrebirds mimic almost anything."),
 ("superb_lyrebird","metallura_tyrianthina",["torpor","structural_colour"],["nectar_feeding_node"],[],["learned_song"],"Hummingbirds hover on nectar and save energy in torpor at night."),
 ("superb_lyrebird","ara_macao",["large_brain"],["fruit_eating","pair_bonds","tool_use"],[],["traditions"],"Parrots: long-lived, clever, crack nuts with a strong beak."),
 # --- Mammals ---
 ("hylonomus_lyelli","platypus",["fur_and_glands","mammary_glands","differentiated_teeth"],["burrow_nests","egg_guarding"],["electroreceptors"],["nursing"],"Mammals came from synapsids; monotremes still lay eggs."),
 ("platypus","red_kangaroo",["mammary_glands","endothermy_node"],["nursing"],["pouch"],[],"Marsupials raise tiny young in a pouch."),
 ("platypus","brown_rat",["mammary_glands","endothermy_node","cusped_molars"],["nursing","nocturnal_refuge"],["placenta"],[],"Placental mammals nourish the embryo through a placenta."),
 ("brown_rat","olive_baboon",["neocortex","large_brain"],["social_hierarchy","facial_expressions"],[],["social_grooming"],"Primates: grasping hands, good eyes, big brains."),
 ("olive_baboon","pan_troglodytes",["prefrontal_cortex"],["tool_use","coalitions"],["long_childhood"],["gestures"],"Great apes use tools and pass on traditions."),
 ("brown_rat","desmodus_rotundus",["echolocating_ears","torpor"],["nocturnal_refuge"],[],["hanging_roost","echolocation_hunting"],"Bats fly and hunt by echolocation; vampire bats feed on blood."),
 ("brown_rat","lion",["differentiated_teeth","cusped_molars"],["stalking","pack_hunting"],[],["scent_marking"],"Carnivorans: shearing teeth for meat."),
 ("lion","jaguar",["myoglobin_stores"],["ambush_hunting"],[],[],"Jaguars ambush prey near water."),
 ("lion","giant_panda",["hindgut_fermentation"],["plant_feeding","winter_dens"],[],[],"A bear that went vegetarian, living on bamboo."),
 ("lion","giant_otter",["diving_reflex","blubber"],["family_groups"],[],[],"Otters hunt fish underwater in family groups."),
 ("brown_rat","white_tailed_deer",["hindgut_fermentation","cusped_molars"],["herding","grass_grazing"],["rumen"],["antler_tournaments"],"Ungulates: hooves and plant-digesting guts."),
 ("white_tailed_deer","maasai_giraffe",["rumen","high_blood_pressure"],["herding"],[],[],"Giraffes need very high blood pressure to reach their heads."),
 ("white_tailed_deer","equus_quagga",["hindgut_fermentation"],["nomadic_herds","stotting"],[],[],"Zebras migrate in great herds."),
 ("white_tailed_deer","delphinus_delphis",["diving_reflex","blubber","myoglobin_stores"],["ocean_migration","family_groups"],["echolocating_ears"],["echolocation_hunting"],"Whales and dolphins evolved from hoofed mammals that returned to the sea."),
 ("brown_rat","african_elephant",["large_brain","hindgut_fermentation"],["herding","infrasound"],[],["matriarchs"],"Elephants live in families led by the oldest female."),
 ("african_elephant","woolly_mammoth",["fur_and_glands","brown_fat"],["nomadic_herds","huddling"],[],[],"Mammoths grew thick fur for the Ice Age steppe."),
 ("african_elephant","american_manatee",["diving_reflex","myoglobin_stores"],["plant_feeding"],[],[],"Sea cows are the elephants' closest relatives."),
 # --- Arthropods ---
 ("hallucigenia","anomalocaris",["jointed_limbs","compound_eyes"],["active_predation"],["mandibles"],[],"Lobopodians gave rise to the arthropods; radiodonts were the first top predators."),
 ("hallucigenia","opabinia",["compound_eyes","segmentation"],["hiding"],[],[],"Opabinia had five eyes and a grasping proboscis."),
 ("anomalocaris","redlichia",["exoskeleton","jointed_limbs","compound_eyes"],["burrowing_escape"],["moulting_hormone"],[],"Trilobites armoured themselves in calcite."),
 ("redlichia","jaekelopterus_rhenaniae",["book_gills","giant_axons"],["pursuit_hunting"],[],["claw_duels"],"Sea scorpions grew to 2.5 m long."),
 ("jaekelopterus_rhenaniae","pulmonoscorpius_kirktonensis",["book_lungs","terrestrial_legs","waterproof_cuticle"],["land_excursions","ambush_hunting"],["venom_glands"],[],"Scorpions came ashore and breathe with book lungs."),
 ("redlichia","arthropleura_armata",["tracheae","terrestrial_legs","waterproof_cuticle"],["land_excursions","plant_feeding"],["malpighian_tubules"],[],"Myriapods were among the first animals on land; Arthropleura was the largest."),
 ("arthropleura_armata","arthropleura_cristata",["exoskeleton"],["burrowing_escape"],[],[],"A crested Arthropleura from the Carboniferous coal forests."),
 ("arthropleura_armata","archimylacris_acadica",["tracheae","spiracles","insect_wings"],["hiding","scavenging"],["juvenile_hormone"],[],"Insects took to the air: the first flying animals."),
 ("archimylacris_acadica","meganeura_monyi",["insect_wings","compound_eyes"],["pursuit_hunting"],[],[],"Griffinflies with 70 cm wings, in oxygen-rich air."),
 ("archimylacris_acadica","mosquito",["complete_metamorphosis","aquatic_larvae"],["mass_dispersal"],[],[],"Flies: two wings, larvae in water."),
 ("mosquito","monarch_butterfly",["complete_metamorphosis","structural_colour"],["seasonal_migration","nectar_feeding_node"],[],["sun_compass"],"Butterflies feed on flowers; monarchs migrate thousands of kilometres."),
 ("archimylacris_acadica","apis_mellifera",["complete_metamorphosis","venom_glands"],["colonial_living","nectar_feeding_node"],[],["waggle_dance","eusociality"],"Bees: a sting, a hive and the waggle dance."),
 ("archimylacris_acadica","photinus_carolinus",["complete_metamorphosis","bioluminescence"],["light_signals"],[],["courtship"],"Fireflies court with flashes of light."),
 # --- Cephalopods ---
 ("cameroceras","asteroceras",["camera_eyes","haemocyanin"],["vertical_migration"],[],[],"Ammonites coiled their shells and filled the Mesozoic seas."),
 ("asteroceras","nipponites_mirabilis",["three_hearts"],["vertical_migration"],[],[],"A heteromorph ammonite with a bizarrely knotted shell."),
 ("cameroceras","wyoteuthis_linsterorum",["camera_eyes","three_hearts"],["ink_cloud","schooling"],[],[],"Belemnites hid their shell inside the body, like squid."),
]
import hashlib
import phylogeny

# Species without a map model can't be shown or played, so they are left out of the tree
species = {s["id"]: s for s in json.load(open(P+"species.json"))["species"] if s.get("model")}
order = {sid: i for i, sid in enumerate(species)}
rules = json.load(open(P+"trait_rules.json"))
gtags = {g["group"]: set(g["tags"]) for g in rules["groups"]}
need = {"morphology": {r["item"]: set(r["tags"]) for r in rules["functions"]},
        "ethology":   {r["item"]: set(r["tags"]) for r in rules["behaviors"]}}
nodes = {k: {n["id"]: n for n in json.load(open(P+f"{k}.json"))["nodes"]} for k in ["morphology","ethology"]}
errs = []

# ---------- The tree ----------
def path(sid):
    s = species[sid]
    p = phylogeny.SPECIES.get(sid) or phylogeny.GROUPS.get(s["group"])
    if p is None: errs.append(f"{sid}: group {s['group']} not in phylogeny.GROUPS")
    return (p or "Eukaryota").split("/")

paths = {sid: path(sid) for sid in species}
age = {sid: AGES.index(species[sid]["firstAge"]) for sid in species}
# appears first, basal first; phylogeny.FIRST: stems that come before the rest of their period
first = {sid: i for i, sid in enumerate(phylogeny.FIRST)}
rank = {sid: (age[sid], first.get(sid, len(first)), len(paths[sid]), order[sid]) for sid in species}

def common(a, b):
    n = 0
    for x, y in zip(paths[a], paths[b]):
        if x != y: break
        n += 1
    return n

MIN_COMMON = 2  # below the root of the eukaryotes there is no ancestor to stand in for
METAZOA = phylogeny.METAZOA.split("/")  # cousins may stand in for a shared ancestor only among the animals
parent = {}
for t in sorted(species, key=lambda s: rank[s]):
    best, key = None, None
    for s in species:
        if rank[s] >= rank[t]: continue
        c = common(s, t)
        if c < MIN_COMMON: continue
        side = len(paths[s]) - c   # how far the candidate is out on a side branch of the shared clade
        # a cousin stands in for the ancestor they share only among the animals: an amoeba is no
        # stand-in for the ancestor of choanoflagellates, nor a social amoeba for that of the
        # plasmodial slime moulds; such a protist starts its own line instead
        if side and (c < len(METAZOA) or paths[s][:len(METAZOA)] != METAZOA): continue
        # the deepest shared clade, counting each step out on a side branch against it (a stem member
        # of the target's own line beats a more derived cousin); then the latest
        k = (c - side, -side, c, age[s], -rank[s][2], -order[s])
        if key is None or k > key: best, key = s, k
    if best: parent[t] = best

# ---------- Requirements and grants ----------
tagfreq = {}
for tags in gtags.values():
    for tg in tags: tagfreq[tg] = tagfreq.get(tg, 0) + 1

def jitter(*parts):
    return int(hashlib.md5("|".join(parts).encode()).hexdigest()[:6], 16) / 0xFFFFFF * 0.01

def genes(sid):
    return {g["gene"]: g["expression"] for g in species[sid].get("genes") or []}

def pick(kind, frm, to, n, granted):
    A, B = gtags[species[frm]["group"]], gtags[species[to]["group"]]
    tage = age[to]
    go, gt = genes(frm), genes(to)
    scored = []
    for item, node in nodes[kind].items():
        nd = need[kind].get(item, {"Animal"})
        if AGES.index(node["age"]) > tage or not (nd & B): continue
        if granted:
            if nd & A: continue                     # new to the line
        elif not (nd & A): continue                 # the origin can acquire it
        novelty = len(nd & (B - A))
        spec = sum(1.0 / tagfreq.get(tg, 1) for tg in nd & B)
        # what the item does for the target: the genes it unlocks that the target has, above all
        # those it has more of than the origin (what changes on the way)
        gain = sum(max(0.0, gt[g] - go.get(g, 0.0)) + 0.3 * gt[g] for g in node.get("unlocksGenes") or [] if g in gt)
        # items any vertebrate or any animal has (jaws, a bilateral body) say little about this step:
        # weight the gain by how particular the item is to the target's line, and by its tier
        focus = 0.25 + min(1.0, 12.0 * spec)
        scored.append((4 * gain * focus + 2 * novelty + spec + 0.08 * node["tier"] + jitter(frm, to, item), item))
    scored.sort(reverse=True)
    # leave out what nearly every animal of the line has (jaws for a vertebrate, lungs for a
    # tetrapod) unless nothing more particular is left
    def generic(item):
        nd = need[kind].get(item, {"Animal"}) & B
        return min(tagfreq.get(tg, 999) for tg in nd) > GENERIC
    particular = [x for x in scored if not generic(x[1])]
    return [i for _, i in (particular if len(particular) >= n else scored)[:n]]

GENERIC = 100  # tags held by more groups than this are too common to stand for a step

def note_for(frm, to):
    pf, pt = paths[frm], paths[to]
    c = common(frm, to)
    for clade in pt[c:]:                            # the first clade the target enters
        if clade in phylogeny.CLADE_NOTES: return phylogeny.CLADE_NOTES[clade]
    for clade in reversed(pt):                      # same clade: its own note
        if clade in phylogeny.CLADE_NOTES: return phylogeny.CLADE_NOTES[clade]
    return ""

curated = {(f, t): (fr, br, fg, bg, why) for f, t, fr, br, fg, bg, why in CURATED}
# requirements and grants chosen by hand for the generated links (requirements.py), keyed "from>to"
try:
    from requirements import REVIEWED
except ImportError:
    REVIEWED = {}
L = []
for t in sorted(parent, key=lambda s: rank[s]):
    f = parent[t]
    if (f, t) in curated:
        L.append((f, t) + curated[(f, t)])
        continue
    if f"{f}>{t}" in REVIEWED:
        fr, br, fg, bg = REVIEWED[f"{f}>{t}"]
        L.append((f, t, fr, br, fg, bg, note_for(f, t)))
        continue
    L.append((f, t, pick("morphology", f, t, 2, False), pick("ethology", f, t, 1, False),
              pick("morphology", f, t, 1, True), pick("ethology", f, t, 1, True), note_for(f, t)))

# ---------- Checks ----------
seen = set()
for frm, to, fr, br, fg, bg, why in L:
    if (frm,to) in seen: errs.append(f"duplicate {frm}>{to}")
    seen.add((frm,to))
    o, t = species[frm], species[to]
    if not t.get("model"): errs.append(f"{to}: no model")
    if AGES.index(t["firstAge"]) < AGES.index(o["firstAge"]): errs.append(f"{frm}>{to}: target older than origin")
    tags = gtags[o["group"]]
    for k, items in (("morphology", fr), ("ethology", br)):
        for i in items:
            n = nodes[k].get(i)
            if n is None: errs.append(f"{frm}>{to}: unknown {k} {i}"); continue
            if not (need[k].get(i, {"Animal"}) & tags): errs.append(f"{frm}>{to}: {i} not available to {o['group']}")
            if AGES.index(n["age"]) > AGES.index(t["firstAge"]): errs.append(f"{frm}>{to}: {i} ({n['age']}) after target appears ({t['firstAge']})")
    for k, items in (("morphology", fg), ("ethology", bg)):
        for i in items:
            if i not in nodes[k]: errs.append(f"{frm}>{to}: unknown granted {k} {i}")
if errs: print("\n".join(errs)); sys.exit(1)
out = {"notes": "Evolution links: a copy of `from` can evolve into `to` once its species has every required function (morphology) and behavior (ethology) item, the target's period has begun and it stands on or next to a tile the target can live on. Requirements are items of the origin species' trees. grantFunctions/grantBehaviors are acquired automatically on evolving. Generated from the tree of life in tools/evolution/phylogeny.py and validated against trait_rules.json by tools/evolution/links.py.",
       "links": [{"from": f, "to": t, "functions": fr, "behaviors": br, "grantFunctions": fg, "grantBehaviors": bg, "description": why}
                 for f, t, fr, br, fg, bg, why in L]}
json.dump(out, open(P+"evolution.json","w"), indent=1)
kept = sum(1 for l in L if (l[0], l[1]) in curated)
stale = sorted(k for k in REVIEWED if tuple(k.split(">")) not in {(l[0], l[1]) for l in L})
if stale: print("requirements.py: no such link any more:", ", ".join(stale))
roots = sorted(s for s in species if s not in parent)
print("ok", len(L), "links,", kept, "hand-written kept;", len(roots), "roots:", ", ".join(roots))
