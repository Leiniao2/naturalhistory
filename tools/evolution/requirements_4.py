# Hand-picked requirements and grants for evolution links (fourth part: the links through the
# transitional species added to join up the tree: Plectronoceras, Bactrites, Fordilla, Sanctacaris,
# Nephila jurassica, Tshekardocoleus, Climatius, Leptolepis, Triadobatrachus, Najash, Lesothosaurus,
# Vegavis, Sinodelphys, Protungulatum, Purgatorius, Miacis, Phenacodus and Indohyus),
# keyed "from>to": (functions required, behaviors required, functions granted, behaviors granted).
REVIEWED = {
    # --- Molluscs: the first cephalopod and the first bivalve ---
    "wiwaxia_corrugata>plectronoceras_cambrense": (["radula", "open_circulation"], ["active_predation"], ["three_hearts"], ["vertical_migration"]),
    "plectronoceras_cambrense>cameroceras": (["three_hearts", "haemocyanin"], ["vertical_migration"], ["camera_eyes"], ["pursuit_hunting"]),
    "cameroceras>bactrites_gracilis": (["camera_eyes", "three_hearts"], ["vertical_migration"], [], ["schooling"]),
    "bactrites_gracilis>agoniatites_vanuxemi": (["camera_eyes", "haemocyanin"], ["vertical_migration"], ["large_brain"], []),
    "bactrites_gracilis>wyoteuthis_linsterorum": (["camera_eyes", "chromatophores"], ["schooling"], ["large_brain","ink_cloud"], []),
    "wiwaxia_corrugata>fordilla_troyensis": (["filter_apparatus", "haemocyanin"], ["burrowing_escape"], [], ["settling"]),
    "fordilla_troyensis>tridacna_gigas": (["filter_apparatus", "planktonic_larvae"], ["settling"], [], ["reef_building"]),
    # --- Chelicerates ---
    "marrella_splendens>sanctacaris_uniformis": (["jointed_limbs", "compound_eyes"], ["active_predation"], [], ["pursuit_hunting"]),
    "sanctacaris_uniformis>megalograptus_ohioensis": (["jointed_limbs", "book_gills"], ["pursuit_hunting"], ["giant_axons"], []),
    "sanctacaris_uniformis>lunataspis_aurora": (["book_gills", "exoskeleton"], ["burrowing_escape"], ["haemocyanin"], []),
    "sanctacaris_uniformis>offacolus_kingi": (["book_gills", "jointed_limbs"], ["hiding"], [], []),
    "sanctacaris_uniformis>haliestes_dasos": (["jointed_limbs", "open_circulation"], ["patch_foraging"], [], ["egg_guarding"]),
    "weygoldtina_anglica>nephila_jurassica": (["book_lungs", "venom_glands"], ["silk_traps"], [], ["ballooning"]),
    "nephila_jurassica>joro_spider": (["venom_glands", "book_lungs"], ["silk_traps"], [], ["female_choice"]),
    # --- Insects: the beetle line ---
    "mazothairos_enormis>tshekardocoleus_magnus": (["insect_wings", "complete_metamorphosis"], ["hiding"], [], ["burrowing_escape"]),
    "tshekardocoleus_magnus>kalligramma_haeckeli": (["complete_metamorphosis", "insect_wings"], ["active_predation"], ["structural_colour"], ["eyespot_display"]),
    "tshekardocoleus_magnus>seven_spot_ladybird": (["complete_metamorphosis", "toxic_skin", "warning_colours"], [], [], ["playing_dead"]),
    # --- Fish: acanthodians to sharks, and the first teleost ---
    "entelognathus_primordialis>climatius_reticulatus": (["jaws", "paired_fins"], ["schooling"], ["placoid_scales"], []),
    "climatius_reticulatus>cladoselache_fyleri": (["placoid_scales", "tooth_replacement"], ["pursuit_hunting"], ["rectal_gland"], []),
    "cheirolepis_trailli>leptolepis_coryphaenoides": (["swim_bladder", "gill_cover"], ["schooling"], [], ["vertical_migration"]),
    "leptolepis_coryphaenoides>xiphactinus_audax": (["swim_bladder", "teeth"], ["pursuit_hunting"], [], ["ambush_hunting"]),
    "leptolepis_coryphaenoides>knightia_eocaena": (["swim_bladder", "filter_apparatus"], ["schooling"], [], ["spawning_aggregations"]),
    "leptolepis_coryphaenoides>megapiranha_paranensis": (["teeth", "swim_bladder"], ["pack_hunting"], [], []),
    "leptolepis_coryphaenoides>mola_mola": (["swim_bladder", "acid_stomach"], ["vertical_migration"], [], ["basking"]),
    # --- Frogs ---
    "amphibamus_grandiceps>triadobatrachus_massinoti": (["aquatic_larvae", "throat_pumping"], ["land_excursions"], ["metamorphosis_hormones"], []),
    "triadobatrachus_massinoti>cane_toad": (["toxic_skin", "metamorphosis_hormones"], ["synchronised_spawning"], ["warning_colours"], []),
    # --- Squamates: the first snakes ---
    "mosasaurus_hoffmannii>najash_rionegrina": (["keratin_scales", "venom_glands"], ["burrowing_escape"], [], ["skin_shedding"]),
    "najash_rionegrina>titanoboa_cerrejonensis": (["keratin_scales", "secondary_palate"], ["ambush_hunting"], [], ["basking"]),
    # --- Dinosaurs: the first ornithischian ---
    "eoraptor_lunensis>lesothosaurus_diagnosticus": (["upright_stance", "gastroliths"], ["plant_feeding"], ["beak"], ["herding"]),
    "lesothosaurus_diagnosticus>scelidosaurus_harrisonii": (["osteoderms", "beak"], ["plant_feeding"], ["tail_weapons"], []),
    "lesothosaurus_diagnosticus>iguanodon_bernissartensis": (["dental_batteries", "beak"], ["herding"], [], ["nesting"]),
    "lesothosaurus_diagnosticus>psittacosaurus_mongoliensis": (["beak", "gastroliths"], ["plant_feeding"], ["horns"], ["creches"]),
    # --- Birds: the first crown bird and its descendants ---
    "confuciusornis_sanctus>vegavis_iaai": (["feathered_wings", "syrinx"], ["incubation"], ["salt_glands"], ["pair_bonds"]),
    "vegavis_iaai>gastornis_giganteus": (["upright_stance", "beak"], ["plant_feeding"], [], ["nesting"]),
    "vegavis_iaai>kumimanu_biceae": (["blubber", "diving_reflex"], ["pursuit_hunting"], [], ["colonial_nesting"]),
    "vegavis_iaai>phorusrhacos_longissimus": (["beak", "upright_stance"], ["pursuit_hunting"], [], ["stalking"]),
    "vegavis_iaai>american_avocet": (["feathered_wings", "salt_glands"], ["patch_foraging"], [], ["distraction_display"]),
    "vegavis_iaai>phoenicopterus_roseus": (["filter_apparatus", "salt_glands"], ["colonial_nesting"], [], ["courtship_dance"]),
    "vegavis_iaai>metallura_tyrianthina": (["torpor", "structural_colour"], ["nectar_feeding_node"], [], ["leks"]),
    # --- Mammals: the first metatherian ---
    "repenomamus_giganticus>sinodelphys_szalayi": (["mammary_glands", "pouch"], [], [], ["nocturnal_refuge"]),
    "sinodelphys_szalayi>thylacosmilus_atrox": (["pouch", "differentiated_teeth"], ["ambush_hunting"], [], ["stalking"]),
    # --- Placentals: the first placental and the stems of its orders ---
    "juramaia_sinensis>protungulatum_donnae": (["placenta", "cusped_molars"], ["omnivory_node"], [], []),
    "protungulatum_donnae>purgatorius_unio": (["placenta", "large_brain"], ["fruit_eating"], [], ["nocturnal_refuge"]),
    "protungulatum_donnae>phenacodus_primaevus": (["cusped_molars", "hindgut_fermentation"], ["plant_feeding"], [], ["herding"]),
    "protungulatum_donnae>uintatherium_anceps": (["horns", "hindgut_fermentation"], ["plant_feeding"], [], ["male_combat"]),
    "purgatorius_unio>plesiadapis_tricuspidens": (["cusped_molars", "neocortex"], ["fruit_eating"], [], []),
    "purgatorius_unio>ceratogaulus_hatcheri": (["cusped_molars", "horns"], ["burrow_systems"], [], ["food_caching"]),
    "phenacodus_primaevus>miacis_parvivorus": (["differentiated_teeth", "neocortex"], ["stalking"], [], ["scent_marking"]),
    "miacis_parvivorus>hoplophoneus_primaevus": (["differentiated_teeth", "myoglobin_stores"], ["ambush_hunting"], [], []),
    "miacis_parvivorus>hyaenodon_horridus": (["differentiated_teeth", "large_brain"], ["pursuit_hunting"], [], ["scavenging"]),
    "phenacodus_primaevus>icaronycteris_index": (["echolocating_ears", "torpor"], ["nocturnal_refuge"], ["echolocating_ears"], []),
    "phenacodus_primaevus>archaeotherium_mortoni": (["hindgut_fermentation", "differentiated_teeth"], ["omnivory_node"], [], ["mud_wallowing"]),
    "phenacodus_primaevus>paraceratherium_transouralicum": (["hindgut_fermentation", "high_blood_pressure"], ["plant_feeding"], [], []),
    "phenacodus_primaevus>megacerops_coloradensis": (["horns", "hindgut_fermentation"], ["herding"], [], ["male_combat"]),
    "phenacodus_primaevus>chalicotherium_grande": (["hindgut_fermentation", "cusped_molars"], ["plant_feeding"], [], []),
    "phenacodus_primaevus>macrauchenia_patachonica": (["hindgut_fermentation", "high_blood_pressure"], ["herding"], [], []),
    "phenacodus_primaevus>indohyus_indirae": (["diving_reflex", "hindgut_fermentation"], ["hiding"], [], ["freezing"]),
    # --- Whales: from the raoellid ---
    "indohyus_indirae>pakicetus_attocki": (["diving_reflex", "differentiated_teeth"], ["ambush_hunting"], ["myoglobin_stores"], []),
    "indohyus_indirae>andrewsarchus_mongoliensis": (["differentiated_teeth", "large_brain"], ["scavenging"], [], []),
}
