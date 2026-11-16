import json, sys
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Assets", "Resources", "Data") + os.sep
AGES = "Ediacaran Cambrian Ordovician Silurian Devonian Carboniferous Permian Triassic Jurassic Cretaceous Paleogene Neogene Quaternary".split()
# from, to, functions required, behaviors required, functions granted, behaviors granted, why
L = [
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
species = {s["id"]: s for s in json.load(open(P+"species.json"))["species"]}
rules = json.load(open(P+"trait_rules.json"))
gtags = {g["group"]: set(g["tags"]) for g in rules["groups"]}
need = {"morphology": {r["item"]: set(r["tags"]) for r in rules["functions"]},
        "ethology":   {r["item"]: set(r["tags"]) for r in rules["behaviors"]}}
nodes = {k: {n["id"]: n for n in json.load(open(P+f"{k}.json"))["nodes"]} for k in ["morphology","ethology"]}
errs = []
seen = set()
for frm, to, fr, br, fg, bg, why in L:
    for sid in (frm, to):
        if sid not in species: errs.append(f"unknown species {sid}")
    if frm not in species or to not in species: continue
    if (frm,to) in seen: errs.append(f"duplicate {frm}>{to}")
    seen.add((frm,to))
    o, t = species[frm], species[to]
    if not t.get("model"): errs.append(f"{to}: no model")
    if t.get("mapStyle") == "Fixed": errs.append(f"{to}: Fixed (can't move)")
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
out = {"notes": "Evolution links: a copy of `from` can evolve into `to` once its species has every required function (morphology) and behavior (ethology) item, the target's period has begun and it stands on or next to a tile the target can live on. Requirements are items of the origin species' trees. grantFunctions/grantBehaviors are acquired automatically on evolving. Validated against trait_rules.json by tools.",
       "links": [{"from": f, "to": t, "functions": fr, "behaviors": br, "grantFunctions": fg, "grantBehaviors": bg, "description": why}
                 for f, t, fr, br, fg, bg, why in L]}
json.dump(out, open(P+"evolution.json","w"), indent=1)
print("ok", len(L), "links,", len({x for l in L for x in l[:2]}), "species")
