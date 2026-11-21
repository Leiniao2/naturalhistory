#!/usr/bin/env python3
"""Builds Assets/Resources/Data/morphology.json and ethology.json from the lists below.

    python3 tools/trees/build_trees.py

Each tree is split into branches (sub-trees shown as tabs in the game's tree panel). A node is
    (id, name, age, prerequisites, description[, genes])
age is a GeologicalAge abbreviation (see AGES); prerequisites is a space-separated list of ids in the
same branch (each is drawn as a line). Column (tier) and row are laid out automatically
from the prerequisites, and cost from column and period. Once the trees are tuned by hand in the
concept editor, edit the JSON there instead of re-running this (it overwrites the files).
"""

import json
from pathlib import Path

AGES = {"Ed": "Ediacaran", "Or": "Ordovician", "Si": "Silurian", "De": "Devonian", "Cb": "Carboniferous",
        "Pe": "Permian", "Tr": "Triassic", "Ju": "Jurassic", "Cr": "Cretaceous", "Pg": "Paleogene",
        "Ng": "Neogene", "Q": "Quaternary"}
AGE_ORDER = list(AGES)

# ------------------------------------------------------------------ Morphology (shape)

MORPHOLOGY = [
    ("nervous", "Nervous System", "Nerves, brains and the sense organs that feed them.", [
        ("nerve_net", "Nerve Net", "Ed", "", "A diffuse web of neurons, like a jellyfish's."),
        ("nerve_cords", "Nerve Cords", "Ed", "nerve_net", "Nerves bundled into cords along the body."),
        ("cephalisation", "Cephalisation", "Ed", "nerve_cords", "Nerve tissue gathers at the front, next to the senses."),
        ("ganglia", "Ganglia", "Ed", "nerve_cords", "Clusters of neurons in each segment that process signals locally."),
        ("chemoreceptors", "Chemoreceptors", "Ed", "nerve_net", "Smell and taste: detecting dissolved chemicals.", "chemoreception"),
        ("compound_eyes", "Compound Eyes", "Ed", "cephalisation", "Hundreds of lenses, each seeing a pixel: the eyes of trilobites and insects.", "vision_acuity"),
        ("dorsal_nerve_cord", "Spinal Cord", "Ed", "cephalisation", "A hollow nerve cord along the back: the chordate spinal cord."),
        ("camera_eyes", "Camera Eyes", "Or", "dorsal_nerve_cord", "A lens focuses an image on the retina (vertebrates, cephalopods)."),
        ("three_part_brain", "Three-part Brain", "Or", "dorsal_nerve_cord", "Forebrain, midbrain and hindbrain, each with its own jobs."),
        ("giant_axons", "Giant Axons", "Or", "ganglia", "Extra-wide nerve fibres for lightning-fast escapes (squid)."),
        ("lateral_line_organ", "Lateral Line", "Or", "dorsal_nerve_cord", "Senses water movement along the flanks.", "lateral_line"),
        ("myelin", "Myelin", "Si", "three_part_brain", "Insulated nerves carry signals far faster; first seen in jawed fish."),
        ("cerebellum", "Cerebellum", "Si", "three_part_brain", "Coordinates movement and balance (jawed vertebrates)."),
        ("electroreceptors", "Electroreceptors", "De", "lateral_line_organ", "Sense the faint electric fields of hidden prey.", "electroreception"),
        ("pallium", "Pallium", "De", "cerebellum", "A forebrain roof that combines the senses: the ancestor of the cortex."),
        ("eardrums", "Eardrums", "Tr", "lateral_line_organ", "Membranes that pick up sound in air."),
        ("large_brain", "Large Brain", "Tr", "pallium", "More brain per kilo of body (early mammals and birds)."),
        ("neocortex", "Neocortex", "Ju", "large_brain", "Six-layered cortex for flexible behaviour (mammals)."),
        ("echolocating_ears", "Echolocating Ears", "Pg", "eardrums", "Hearing returning echoes of your own calls (bats, toothed whales).", "echolocation"),
        ("prefrontal_cortex", "Prefrontal Cortex", "Ng", "neocortex", "Planning and self-control (great apes)."),
        ("electric_organs", "Electric Organs", "Cr", "electroreceptors", "Muscle turned into living batteries that discharge to stun prey (electric eels, torpedo rays)."),
    ]),
    ("circulatory", "Circulatory System", "Blood, hearts and vessels.", [
        ("fluid_circulation", "Fluid Circulation", "Ed", "", "Body fluid is moved around by body movement and beating cilia."),
        ("pulsing_vessel", "Pulsing Vessel", "Ed", "fluid_circulation", "A muscular tube that squeezes blood along."),
        ("open_circulation", "Open Circulation", "Ed", "pulsing_vessel", "Blood bathes the organs directly (arthropods, most molluscs)."),
        ("closed_circulation", "Closed Circulation", "Ed", "pulsing_vessel", "Blood stays inside vessels and moves faster (annelids, vertebrates)."),
        ("haemocyanin", "Haemocyanin", "Ed", "open_circulation", "Copper-based blue blood that carries oxygen."),
        ("haemoglobin", "Haemoglobin", "Ed", "closed_circulation", "Iron-based red pigment that carries oxygen."),
        ("red_blood_cells", "Red Blood Cells", "Or", "haemoglobin", "Haemoglobin packed into cells carries far more oxygen."),
        ("two_chambered_heart", "Two-chambered Heart", "Or", "closed_circulation", "An atrium and a ventricle (fish)."),
        ("three_hearts", "Three Hearts", "Or", "closed_circulation", "Extra hearts pump blood through the gills (cephalopods)."),
        ("capillaries", "Capillaries", "Or", "closed_circulation", "Vessels one cell thick bring oxygen right up to every tissue."),
        ("blood_clotting", "Blood Clotting", "Si", "red_blood_cells", "Clotting proteins seal a wound before too much blood is lost."),
        ("hepatic_portal", "Hepatic Portal Vein", "Si", "two_chambered_heart", "Blood from the gut passes through the liver before reaching the body."),
        ("three_chambered_heart", "Three-chambered Heart", "De", "two_chambered_heart", "Two atria keep lung blood and body blood partly apart (amphibians)."),
        ("coronary_arteries", "Coronary Arteries", "De", "three_chambered_heart", "The heart muscle gets a blood supply of its own, so it can work harder."),
        ("accessory_hearts", "Accessory Hearts", "Cb", "open_circulation", "Extra pumps push blood into the wings, legs and antennae (insects)."),
        ("four_chambered_heart", "Four-chambered Heart", "Tr", "three_chambered_heart", "Fully separate lung and body circuits (archosaurs, mammals)."),
        ("high_blood_pressure", "High Blood Pressure", "Ju", "four_chambered_heart", "Enough pressure to push blood up a sauropod's long neck."),
        ("countercurrent_exchange", "Countercurrent Heat Exchange", "Cr", "four_chambered_heart", "Outgoing warm blood heats returning cold blood in flippers and legs."),
        ("diving_reflex", "Diving Reflex", "Pg", "four_chambered_heart", "On long dives the heart slows and blood goes to the brain (whales, seals)."),
        ("myoglobin_stores", "Myoglobin Stores", "Pg", "diving_reflex", "Muscles packed with oxygen-storing myoglobin."),
    ]),
    ("respiratory", "Respiratory System", "Gills, tracheae, lungs and air sacs.", [
        ("skin_breathing", "Skin Breathing", "Ed", "", "Oxygen diffuses in through a thin body wall."),
        ("gills", "Gills", "Ed", "skin_breathing", "Feathery surfaces for taking oxygen from water."),
        ("pharyngeal_slits", "Pharyngeal Slits", "Ed", "gills", "Slits in the throat that let water flow out past the gills."),
        ("book_gills", "Book Gills", "Or", "gills", "Stacked gill plates (horseshoe crabs, sea scorpions)."),
        ("gill_arches", "Gill Arches", "Or", "pharyngeal_slits", "Bony or cartilage arches support the gills."),
        ("tracheae", "Tracheae", "Si", "skin_breathing", "Air tubes run straight to the tissues (insects, millipedes)."),
        ("spiracles", "Spiracles", "Si", "tracheae", "Closable openings to the tracheae that save water."),
        ("book_lungs", "Book Lungs", "Si", "book_gills", "Air-breathing gill plates (scorpions, spiders)."),
        ("gill_cover", "Gill Cover", "Si", "gill_arches", "A bony flap that pumps water over the gills."),
        ("lungs", "Lungs", "De", "gill_arches", "Air sacs off the gut let fish gulp air in stagnant water.", "cold_tolerance"),
        ("swim_bladder", "Swim Bladder", "De", "lungs", "The lung becomes a gas float for buoyancy (ray-finned fish)."),
        ("throat_pumping", "Throat Pumping", "De", "lungs", "Gulping air in with the floor of the mouth (amphibians)."),
        ("larynx", "Larynx", "Cb", "lungs", "A valve that guards the airway; later the voice box."),
        ("rib_breathing", "Rib Breathing", "Cb", "throat_pumping", "Expanding the ribcage to draw air in (amniotes)."),
        ("diaphragm", "Diaphragm", "Pe", "rib_breathing", "A muscle sheet for powerful breathing (synapsids)."),
        ("turbinates", "Turbinates", "Pe", "diaphragm", "Scrolled nose bones that warm and moisten the air (warm-blooded animals)."),
        ("air_sacs", "Air Sacs", "Tr", "rib_breathing", "Air flows one way through the lungs (dinosaurs, birds)."),
        ("plastron_gill", "Bubble Gill", "Cr", "spiracles", "Breathing from a film of air held under water (water beetles)."),
        ("syrinx", "Syrinx", "Cr", "air_sacs", "The twin voice box of birds."),
        ("labyrinth_organ", "Labyrinth Organ", "Pg", "gill_cover", "A folded chamber above the gills for breathing air (gouramis)."),
    ]),
    ("digestive", "Digestive System", "Mouths, teeth, stomachs and guts.", [
        ("blind_gut", "Blind Gut", "Ed", "", "A sac with one opening, like a sea anemone's."),
        ("through_gut", "Through-gut", "Ed", "blind_gut", "A mouth at one end and an anus at the other."),
        ("filter_apparatus", "Filter Apparatus", "Ed", "through_gut", "Mucus nets or gill rakers strain food from water.", "filter_feeding"),
        ("radula", "Radula", "Ed", "through_gut", "A rasping tongue-ribbon (molluscs)."),
        ("mandibles", "Mandibles", "Ed", "through_gut", "Biting jaws of arthropods."),
        ("jaws", "Jaws", "Si", "filter_apparatus", "Hinged jaws made from gill arches, so prey can be grabbed.", "carnivory"),
        ("gizzard", "Gizzard", "Si", "through_gut", "A muscular stomach that grinds food."),
        ("acid_stomach", "Acid Stomach", "Si", "jaws", "An acidic stomach digests large prey (jawed vertebrates)."),
        ("teeth", "Teeth", "Si", "jaws", "Hard teeth for gripping and cutting."),
        ("spiral_valve", "Spiral Valve", "Si", "acid_stomach", "A corkscrew intestine packs in more surface (sharks)."),
        ("tooth_replacement", "Tooth Replacement", "De", "teeth", "Lost teeth are replaced all through life (sharks, reptiles)."),
        ("hindgut_fermentation", "Hindgut Fermentation", "Pe", "acid_stomach", "Microbes in an enlarged gut break down plant fibre.", "herbivory"),
        ("differentiated_teeth", "Differentiated Teeth", "Pe", "teeth", "Incisors, canines and molars for different jobs."),
        ("venom_glands", "Venom Glands", "Si", "through_gut", "Glands that make venom, delivered by fangs, stings or grooved teeth (scorpions, centipedes, snakes)."),
        ("secondary_palate", "Secondary Palate", "Tr", "differentiated_teeth", "A bony roof to the mouth: breathe while chewing."),
        ("gastroliths", "Gastroliths", "Ju", "gizzard", "Swallowed stones grind food (sauropods, birds)."),
        ("beak", "Beak", "Ju", "teeth", "A toothless keratin beak (turtles, birds, ceratopsians)."),
        ("cusped_molars", "Cusped Molars", "Ju", "differentiated_teeth", "Molars that both slice and crush (mammals)."),
        ("dental_batteries", "Dental Batteries", "Cr", "tooth_replacement", "Hundreds of stacked teeth grind tough plants (hadrosaurs)."),
        ("rumen", "Rumen", "Pg", "hindgut_fermentation", "A many-chambered stomach for chewing the cud (ruminants)."),
    ]),
    ("excretory", "Excretory System", "Getting rid of waste and keeping water and salt in balance.", [
        ("diffusion_waste", "Diffusion", "Ed", "", "Waste simply leaks out through the thin body wall."),
        ("osmoconformity", "Osmoconformity", "Ed", "diffusion_waste", "Body fluids as salty as the sea, so there is no water balance to fight for (most marine invertebrates)."),
        ("nephridia", "Nephridia", "Ed", "diffusion_waste", "Paired tubules in each segment filter the body fluid (worms)."),
        ("flame_cells", "Flame Cells", "Ed", "diffusion_waste", "Beating cilia draw fluid into fine tubules (flatworms)."),
        ("ammonia_excretion", "Ammonia Excretion", "Ed", "nephridia", "Toxic ammonia is flushed away with plenty of water: cheap in the sea."),
        ("antennal_glands", "Antennal Glands", "Or", "nephridia", "Kidney-like glands at the base of the antennae (crustaceans)."),
        ("pronephros", "Head Kidney", "Or", "nephridia", "The first vertebrate kidney: a few tubules just behind the head."),
        ("glomerular_kidney", "Filtering Kidney", "Si", "pronephros", "Kidneys filter waste out of the blood."),
        ("malpighian_tubules", "Malpighian Tubules", "Si", "nephridia", "Tubules pull waste out of the body fluid into the gut (insects, spiders)."),
        ("gill_salt_cells", "Gill Salt Cells", "Si", "ammonia_excretion", "Cells in the gills pump salt in or out, for life in fresh or salt water."),
        ("detox_liver", "Detoxifying Liver", "Si", "ammonia_excretion", "A liver that breaks down poisons and worn-out blood for disposal."),
        ("urinary_bladder", "Urinary Bladder", "De", "glomerular_kidney", "Stores urine and lets water be taken back (tetrapods)."),
        ("urea_cycle", "Urea", "De", "glomerular_kidney", "Ammonia is turned into urea, which is less toxic and needs less water (amphibians, sharks)."),
        ("rectal_gland", "Rectal Gland", "De", "gill_salt_cells", "A gland that pumps out excess salt (sharks)."),
        ("water_saving_rectum", "Water-saving Rectum", "Cb", "malpighian_tubules", "Almost every drop of water is recovered from the waste (desert beetles)."),
        ("uric_acid", "Uric Acid Waste", "Cb", "urea_cycle", "Water-saving solid waste (reptiles, birds, insects)."),
        ("metanephros", "Back Kidney", "Cb", "glomerular_kidney", "A compact kidney with many more filtering units (amniotes)."),
        ("salt_glands", "Salt Glands", "Tr", "gill_salt_cells", "Glands that get rid of excess salt (marine reptiles, seabirds)."),
        ("loop_of_henle", "Loop of Henle", "Ju", "metanephros", "Concentrated urine saves water (mammals, birds)."),
        ("desert_kidneys", "Desert Kidneys", "Ng", "loop_of_henle", "Kidneys so efficient the animal never needs to drink (kangaroo rats).", "heat_tolerance"),
    ]),
    ("endocrine", "Endocrine System", "Hormones, body heat and dormancy.", [
        ("hormone_signalling", "Hormone Signalling", "Ed", "", "Cells release chemical messages carried in body fluids."),
        ("neurosecretory_cells", "Neurosecretory Cells", "Ed", "hormone_signalling", "Nerve cells that release hormones."),
        ("insulin_signalling", "Insulin Signalling", "Ed", "hormone_signalling", "Hormones that control growth and the use of sugar."),
        ("moulting_hormone", "Moulting Hormone", "Ed", "neurosecretory_cells", "Ecdysone decides when an arthropod moults."),
        ("pituitary", "Pituitary Gland", "Or", "neurosecretory_cells", "The master gland under the brain."),
        ("pineal_clock", "Pineal Clock", "Or", "neurosecretory_cells", "Melatonin keeps track of day length and season."),
        ("antifreeze_proteins", "Antifreeze Proteins", "Or", "insulin_signalling", "Proteins that stop ice crystals forming in the blood.", "cold_tolerance"),
        ("thyroid", "Thyroid", "Or", "pituitary", "Iodine hormones set the metabolic rate."),
        ("stress_hormones", "Stress Hormones", "Si", "pituitary", "Adrenaline and cortisol: the fight-or-flight response."),
        ("sex_hormones", "Sex Hormones", "Si", "pituitary", "Testosterone and oestrogen shape adult bodies."),
        ("juvenile_hormone", "Juvenile Hormone", "Cb", "moulting_hormone", "Keeps insects as larvae until it is time to change."),
        ("metamorphosis_hormones", "Metamorphosis Trigger", "Cb", "thyroid", "A thyroid surge turns tadpoles into frogs."),
        ("aestivation", "Aestivation", "Pe", "stress_hormones", "Sleeping through droughts, like lungfish in mud cocoons.", "heat_tolerance"),
        ("raised_metabolism", "Raised Metabolism", "Pe", "thyroid", "Faster cells for sustained activity (therapsids)."),
        ("prolactin", "Prolactin", "Tr", "pituitary", "The hormone behind brooding and milk."),
        ("endothermy_node", "Endothermy", "Tr", "raised_metabolism", "Warm-blooded: body heat comes from metabolism.", "endothermy"),
        ("torpor", "Torpor", "Ju", "endothermy_node", "A daily drop in body temperature to save energy."),
        ("brown_fat", "Brown Fat", "Cr", "endothermy_node", "Fat that burns to make heat."),
        ("oxytocin_bonding", "Oxytocin Bonding", "Cr", "prolactin", "The hormone of pair bonds and mother–young attachment."),
        ("hibernation_node", "Hibernation", "Pg", "torpor", "Weeks-long deep torpor through the winter.", "hibernation"),
        ("diapause", "Diapause", "Si", "hormone_signalling", "Development pauses until conditions improve."),
    ]),
    ("reproductive", "Reproductive System", "Eggs, larvae, wombs and growing up.", [
        ("broadcast_spawning", "Broadcast Spawning", "Ed", "", "Releasing eggs and sperm into the sea.", "reproduction_rate"),
        ("budding", "Budding", "Ed", "broadcast_spawning", "Growing copies of yourself.", "asexual_reproduction"),
        ("planktonic_larvae", "Planktonic Larvae", "Ed", "broadcast_spawning", "Drifting young that spread far."),
        ("yolky_eggs", "Yolky Eggs", "Ed", "broadcast_spawning", "Bigger eggs with stored food.", "clutch_size"),
        ("regeneration_node", "Regeneration", "Ed", "budding", "Regrowing lost body parts.", "regeneration"),
        ("internal_fertilisation", "Internal Fertilisation", "Si", "yolky_eggs", "Sperm is delivered inside the female."),
        ("spermatophores", "Spermatophores", "Si", "yolky_eggs", "Sperm packets left for the female to pick up."),
        ("parthenogenesis", "Parthenogenesis", "Si", "budding", "Females reproduce without males."),
        ("claspers", "Claspers", "De", "internal_fertilisation", "Fin organs for mating (sharks, placoderms)."),
        ("egg_cases", "Egg Cases", "De", "yolky_eggs", "Tough capsules that protect the embryo (mermaid's purses)."),
        ("aquatic_larvae", "Aquatic Larvae", "De", "planktonic_larvae", "Tadpoles: amphibian young grow up in the water."),
        ("live_birth", "Live Birth", "De", "internal_fertilisation", "Young develop inside the mother (placoderms, ichthyosaurs)."),
        ("amniotic_egg", "Amniotic Egg", "Cb", "internal_fertilisation", "An egg with its own membranes and water supply, so it can be laid on land.", "clutch_size"),
        ("complete_metamorphosis", "Complete Metamorphosis", "Cb", "planktonic_larvae", "Larva, pupa and adult (beetles, flies, butterflies)."),
        ("temperature_sex", "Temperature Sex Determination", "Pe", "amniotic_egg", "Nest temperature decides the sex of the young (crocodiles, turtles)."),
        ("hard_eggshell", "Hard Eggshell", "Ju", "amniotic_egg", "Calcified shells (dinosaurs, birds)."),
        ("mammary_glands", "Mammary Glands", "Tr", "amniotic_egg", "Milk for the young."),
        ("placenta", "Placenta", "Cr", "mammary_glands", "The embryo is fed through the womb wall."),
        ("pouch", "Pouch", "Cr", "mammary_glands", "Tiny newborns finish growing in a pouch (marsupials)."),
        ("long_childhood", "Long Childhood", "Ng", "placenta", "Slow growth gives time for a bigger brain to develop."),
        ("hermaphroditism", "Hermaphroditism", "Ed", "broadcast_spawning", "Both sexes in one body (snails, worms)."),
        ("colonial_living", "Colonial Living", "Ed", "budding", "Clones joined into one colony (corals, graptolites)."),
    ]),
    ("locomotor", "Locomotor System", "Bones, joints and muscles: the skeleton and how it moves.", [
        ("bilateral_body", "Bilateral Body", "Ed", "", "A front, a back and two mirrored sides: the body plan of most animals.", "swimming_speed burrowing"),
        ("muscle_bands", "Muscle Bands", "Ed", "bilateral_body", "Long and circular muscles for crawling, wriggling and burrowing."),
        ("segmentation", "Segmentation", "Ed", "bilateral_body", "The body is built from repeated segments that can specialise independently."),
        ("coelom", "Body Cavity", "Ed", "bilateral_body", "A fluid-filled cavity that cushions the organs and works as a hydrostatic skeleton."),
        ("exoskeleton", "Exoskeleton", "Ed", "segmentation", "A hard outer cuticle that protects the body and anchors the muscles.", "armor_thickness"),
        ("jointed_limbs", "Jointed Limbs", "Ed", "exoskeleton muscle_bands", "Hinged legs inside the exoskeleton: the arthropod toolkit.", "land_speed"),
        ("notochord", "Notochord", "Ed", "coelom", "A stiff, flexible rod along the back: the first chordate skeleton.", "lateral_line"),
        ("myomeres", "Myomeres", "Ed", "notochord muscle_bands", "Zig-zag muscle blocks that bend the body from side to side: fish-style swimming."),
        ("vertebral_column", "Vertebrae", "Or", "notochord", "Blocks of cartilage or bone protect the nerve cord and stiffen the back."),
        ("tail_fin", "Tail Fin", "Or", "myomeres", "A broad tail turns side-to-side bending into thrust."),
        ("paired_fins", "Paired Fins", "Si", "tail_fin", "Fins on both sides give steering, braking and lift.", "electroreception"),
        ("endochondral_bone", "Internal Bone", "Si", "vertebral_column", "Bone that replaces cartilage: the inner skeleton of bony fish and their descendants."),
        ("terrestrial_legs", "Terrestrial Legs", "Si", "jointed_limbs", "Legs that hold the body up out of water: the first land millipedes."),
        ("lobe_fins", "Lobe Fins", "De", "paired_fins", "Fleshy fins with a bony core, the starting point for legs.", "climbing"),
        ("digits", "Digits", "De", "lobe_fins", "Fingers and toes at the end of the limb (Acanthostega had eight)."),
        ("weight_bearing_girdles", "Weight-bearing Girdles", "De", "endochondral_bone", "Shoulder and hip girdles strong enough to carry the body out of water."),
        ("insect_wings", "Insect Wings", "Cb", "terrestrial_legs", "Thin outgrowths of the thorax: the first animals to fly.", "flight_capability"),
        ("upright_stance", "Upright Stance", "Tr", "digits weight_bearing_girdles", "Legs held under the body for efficient running and breathing."),
        ("hollow_bones", "Hollow Bones", "Tr", "endochondral_bone", "Air-filled bones are light and strong (dinosaurs, pterosaurs, birds)."),
        ("feathered_wings", "Feathered Wings", "Ju", "upright_stance hollow_bones", "Arms lined with flight feathers, as on Archaeopteryx."),
        ("tail_weapons", "Tail Weapons", "Ju", "bilateral_body", "Clubs and spikes swung at attackers (stegosaurs, ankylosaurs)."),
        ("gliding", "Gliding", "Pe", "bilateral_body", "Leaping and gliding between trees."),
    ]),
    ("immune", "Immune System", "Defences against parasites and disease.", [
        ("phagocytes", "Phagocytes", "Ed", "", "Wandering cells that engulf bacteria and debris."),
        ("antimicrobial_peptides", "Antimicrobial Peptides", "Ed", "phagocytes", "Small proteins that punch holes in bacteria."),
        ("pattern_receptors", "Pattern Recognition", "Ed", "phagocytes", "Receptors that recognise molecules common to many microbes."),
        ("encapsulation", "Encapsulation", "Ed", "phagocytes", "Parasites too big to swallow are walled off inside a capsule of cells."),
        ("complement", "Complement System", "Ed", "pattern_receptors", "Blood proteins that tag invaders and burst them open."),
        ("melanisation", "Melanisation", "Or", "encapsulation", "Invaders are smothered in melanin (insects, crustaceans)."),
        ("inflammation", "Inflammation", "Or", "complement", "Heat, swelling and a rush of defender cells to a wound."),
        ("variable_receptors", "Variable Receptors", "Or", "pattern_receptors", "An adaptive immune system of its own, built from different genes (lampreys, hagfish)."),
        ("adaptive_immunity", "Adaptive Immunity", "Si", "inflammation", "Lymphocytes reshuffle their genes to recognise almost any invader (jawed vertebrates)."),
        ("antibodies", "Antibodies", "Si", "adaptive_immunity", "Y-shaped proteins that lock on to one particular invader."),
        ("thymus", "Thymus", "Si", "adaptive_immunity", "A gland where T cells learn to tell self from foreign."),
        ("mhc", "MHC Molecules", "Si", "thymus", "Molecules that show fragments of invaders to T cells."),
        ("spleen", "Spleen", "Si", "adaptive_immunity", "Filters the blood and stores immune cells."),
        ("lymphatic_system", "Lymphatic System", "De", "spleen", "Vessels that return fluid and carry immune cells."),
        ("immune_memory", "Immune Memory", "De", "antibodies", "A second infection is beaten faster than the first."),
        ("bone_marrow", "Bone Marrow", "De", "spleen", "Blood and immune cells are made inside the bones (tetrapods)."),
        ("fever", "Fever", "Pe", "inflammation", "Raising body temperature to slow down pathogens."),
        ("maternal_antibodies", "Maternal Antibodies", "Tr", "antibodies", "Mothers pass their protection on through the egg or milk."),
        ("lymph_nodes", "Lymph Nodes", "Cr", "lymphatic_system", "Filter stations where immune cells meet invaders (mammals)."),
        ("germinal_centres", "Germinal Centres", "Cr", "lymph_nodes", "Antibodies are fine-tuned to fit their target better and better (mammals)."),
    ]),
    ("integument", "Integumentary System", "Skin, scales, feathers, fur, colour and armour.", [
        ("epidermis", "Epidermis", "Ed", "", "A protective outer layer of cells."),
        ("mucus_coat", "Mucus Coat", "Ed", "epidermis", "Slippery slime that protects the skin and eases movement."),
        ("chitin_cuticle", "Chitin Cuticle", "Ed", "epidermis", "A tough skin made of a sugar polymer."),
        ("spines", "Spines", "Ed", "chitin_cuticle", "Sharp projections deter predators (Wiwaxia, Hallucigenia)."),
        ("chromatophores", "Chromatophores", "Or", "epidermis", "Pigment cells that can change colour.", "camouflage"),
        ("dermal_armour", "Dermal Armour", "Or", "epidermis", "Bony plates in the skin (early jawless fish).", "armor_thickness"),
        ("placoid_scales", "Placoid Scales", "Si", "dermal_armour", "Tiny tooth-like scales that cut drag (sharks)."),
        ("bioluminescence", "Bioluminescence", "Si", "chromatophores", "Making light with a chemical reaction."),
        ("waterproof_cuticle", "Waterproof Cuticle", "Si", "chitin_cuticle", "A wax layer stops the body drying out on land."),
        ("toxic_skin", "Toxic Skin", "Cb", "mucus_coat", "Skin glands that make poison (amphibians).", "toxin_production"),
        ("keratin_scales", "Keratin Scales", "Cb", "epidermis", "Dry, waterproof scales (reptiles)."),
        ("osteoderms", "Osteoderms", "Pe", "keratin_scales dermal_armour", "Bony plates under the scales (crocodiles, ankylosaurs)."),
        ("protofeathers", "Protofeathers", "Tr", "keratin_scales", "Fuzzy filaments for insulation."),
        ("fur_and_glands", "Fur and Glands", "Tr", "keratin_scales", "Insulating hair and skin glands (mammals).", "parental_care"),
        ("feathers", "Feathers", "Ju", "protofeathers", "Vaned feathers for warmth, display and flight.", "endothermy"),
        ("structural_colour", "Structural Colour", "Ju", "feathers", "Iridescent colour from microscopic structure instead of pigment."),
        ("horns", "Horns", "Cr", "keratin_scales", "Keratin-sheathed bony horns (ceratopsians, later antelopes and cattle)."),
        ("sweat_glands", "Sweat Glands", "Pg", "fur_and_glands", "Cooling by evaporation."),
        ("blubber", "Blubber", "Pg", "fur_and_glands", "A thick fat layer insulates in cold seas."),
        ("quills", "Quills", "Pg", "fur_and_glands", "Hairs hardened into spines (porcupines, hedgehogs)."),
        ("countershading", "Countershading", "De", "epidermis", "Dark above and pale below, so the body looks flat."),
        ("ink_cloud", "Ink Cloud", "Cb", "chromatophores", "A cloud of ink covers the escape (cephalopods)."),
        ("warning_colours", "Warning Colours", "Cb", "epidermis", "Bright colours that advertise poison.", "toxin_production"),
        ("chemical_spray", "Chemical Spray", "Pe", "epidermis", "Spraying irritants (bombardier beetles, later skunks)."),
        ("mimicry", "Mimicry", "Ju", "warning_colours", "Harmless species copying dangerous ones."),
    ]),
]

# ------------------------------------------------------------------ Ethology (behaviour)

ETHOLOGY = [
    ("foraging", "Foraging Behaviour", "Finding, catching and eating food.", [
        ("foraging", "Foraging", "Ed", "", "Searching the sea floor for food.", "filter_feeding"),
        ("scavenging", "Scavenging", "Ed", "foraging", "Feeding on the dead.", "decomposition"),
        ("active_predation", "Active Predation", "Ed", "foraging", "Hunting other animals (Anomalocaris).", "carnivory"),
        ("ambush_hunting", "Ambush Hunting", "Ed", "active_predation", "Waiting hidden and striking at passing prey."),
        ("patch_foraging", "Patch Foraging", "Or", "foraging", "Moving on when a food patch runs low."),
        ("pursuit_hunting", "Pursuit Hunting", "Or", "active_predation", "Chasing prey down in open water."),
        ("plant_feeding", "Plant Feeding", "Si", "patch_foraging", "Eating land plants.", "herbivory"),
        ("silk_traps", "Silk Traps", "Cb", "ambush_hunting", "Webs and trip-lines of silk."),
        ("omnivory_node", "Omnivory", "Pe", "scavenging plant_feeding", "Eating whatever is available.", "omnivory"),
        ("stalking", "Stalking", "Pe", "ambush_hunting", "Creeping up on prey unseen."),
        ("pack_hunting", "Pack Hunting", "Ju", "stalking", "Hunting together to take bigger prey."),
        ("nectar_feeding_node", "Nectar Feeding", "Cr", "plant_feeding", "Drinking nectar and carrying pollen between flowers.", "nectar_feeding"),
        ("fruit_eating", "Fruit Eating", "Cr", "plant_feeding", "Eating fruit and spreading the seeds."),
        ("food_caching", "Food Caching", "Pg", "patch_foraging", "Hiding food for later (squirrels, jays)."),
        ("fungus_farming", "Fungus Farming", "Pg", "plant_feeding", "Growing fungus gardens for food (leafcutter ants, termites)."),
        ("grass_grazing", "Grass Grazing", "Ng", "plant_feeding", "Grazing the new grasslands in herds."),
        ("tool_use", "Tool Use", "Ng", "food_caching", "Using objects as tools.", ""),
        ("persistence_hunting", "Persistence Hunting", "Q", "pursuit_hunting", "Running prey to exhaustion (humans)."),
    ]),
    ("antipredator", "Antipredator Behaviour", "Hiding, fleeing, fighting back and bluffing.", [
        ("withdrawal", "Withdrawal Reflex", "Ed", "", "Pulling back into a tube or shell when touched."),
        ("hiding", "Hiding", "Ed", "withdrawal", "Keeping still in cover.", "camouflage"),
        ("burrowing_escape", "Burrowing Escape", "Ed", "withdrawal", "Digging into the sediment to escape.", "burrowing"),
        ("rolling_up", "Rolling Up", "Ed", "withdrawal", "Curling into an armoured ball (trilobites, pill bugs)."),
        ("autotomy", "Autotomy", "Or", "withdrawal", "Dropping a limb or tail to escape."),
        ("freezing", "Freezing", "Or", "hiding", "Staying motionless so predators lose interest."),
        ("startle_escape", "Startle Escape", "Si", "withdrawal", "A lightning-fast flick of the body away from danger (fish)."),
        ("playing_dead", "Playing Dead", "Pe", "freezing", "Going limp until the predator gives up."),
        ("eyespot_display", "Eyespot Display", "Pe", "freezing", "Flashing fake eyes to startle attackers."),
        ("group_vigilance", "Group Vigilance", "Tr", "freezing", "Many eyes: some watch while others feed."),
        ("mobbing", "Mobbing", "Cr", "group_vigilance", "Ganging up to drive a predator away."),
        ("distraction_display", "Distraction Display", "Cr", "playing_dead", "Faking a broken wing to lure predators from the nest."),
        ("stotting", "Stotting", "Ng", "startle_escape", "Leaping high to show predators you are too fit to chase."),
        ("selfish_herd", "Selfish Herd", "Or", "hiding", "Pushing into the middle of the group so others are on the outside."),
    ]),
    ("reproductive", "Reproductive Behaviour", "Courtship, mating and raising the young.", [
        ("spawning_aggregations", "Spawning Aggregations", "Ed", "", "Gathering in one place to spawn."),
        ("synchronised_spawning", "Synchronised Spawning", "Or", "spawning_aggregations", "Spawning together on a cue from the moon or temperature."),
        ("egg_sites", "Choosing Egg Sites", "Or", "spawning_aggregations", "Laying eggs in safe places."),
        ("mate_guarding", "Mate Guarding", "Si", "spawning_aggregations", "Staying close to a mate to keep rivals away."),
        ("egg_guarding", "Egg Guarding", "Si", "egg_sites", "Staying with the eggs to drive off egg-eaters."),
        ("sperm_competition", "Sperm Competition", "Si", "mate_guarding", "Rival males compete after mating, inside the female."),
        ("courtship", "Courtship", "Cb", "mate_guarding", "Rituals that persuade a mate."),
        ("nuptial_gifts", "Nuptial Gifts", "Pe", "courtship", "Offering food to a mate."),
        ("female_choice", "Female Choice", "Pe", "courtship", "Females choose the best-looking or best-sounding male."),
        ("courtship_dance", "Courtship Dance", "Tr", "courtship", "Elaborate dances performed for a mate."),
        ("feeding_young", "Feeding the Young", "Tr", "egg_guarding", "Bringing food to the young."),
        ("pair_bonds", "Pair Bonds", "Cr", "courtship", "Staying with one partner for a season or for life."),
        ("leks", "Leks", "Cr", "courtship_dance", "Males display side by side while females choose."),
        ("biparental_care", "Biparental Care", "Ju", "feeding_young", "Both parents raise the young."),
        ("mouthbrooding", "Mouthbrooding", "Pg", "egg_guarding", "Sheltering eggs and fry in the mouth (cichlids)."),
        ("alloparenting", "Alloparenting", "Pg", "biparental_care", "Aunts, siblings and others help raise the young."),
        ("brood_parasitism", "Brood Parasitism", "Ng", "feeding_young", "Tricking others into raising your chicks (cuckoos)."),
        ("teaching", "Teaching", "Ng", "alloparenting", "Showing the young how to do things on purpose."),
    ]),
    ("social", "Social Behaviour", "Groups, colonies, hierarchies and traditions.", [
        ("aggregation", "Aggregation", "Ed", "", "Gathering where conditions are good."),
        ("schooling", "Schooling", "Or", "aggregation", "Swimming in coordinated groups for safety.", "group_defense"),
        ("kin_recognition", "Kin Recognition", "Si", "aggregation", "Telling relatives from strangers by smell or sight."),
        ("family_groups", "Family Groups", "Pe", "aggregation", "Parents and young stay together."),
        ("herding", "Herding", "Tr", "schooling", "Moving and feeding in herds (dinosaurs)."),
        ("eusociality", "Eusociality", "Cr", "family_groups", "Sterile workers serve a breeding queen (termites, ants)."),
        ("castes", "Castes", "Cr", "eusociality", "Soldiers, workers and nurses, each built for its job."),
        ("social_hierarchy", "Social Hierarchy", "Pg", "herding", "A pecking order settles who gets what."),
        ("cooperative_breeding", "Cooperative Breeding", "Pg", "family_groups", "Helpers raise young that are not their own."),
        ("creches", "Crèches", "Cr", "family_groups", "Young gathered together in nurseries."),
        ("social_grooming", "Social Grooming", "Pg", "social_hierarchy", "Cleaning each other to build bonds."),
        ("superorganism", "Superorganism", "Pg", "castes", "A colony acting as one body (army ants)."),
        ("coalitions", "Coalitions", "Ng", "social_hierarchy", "Allies band together to rise in rank."),
        ("fission_fusion", "Fission–fusion Groups", "Ng", "coalitions", "Groups split and merge day by day (chimpanzees, elephants)."),
        ("reciprocal_altruism", "Reciprocal Altruism", "Ng", "social_grooming", "Helping those who help you (vampire bats sharing blood)."),
        ("mixed_species_flocks", "Mixed-species Flocks", "Ng", "herding", "Different species forage together for safety."),
        ("matriarchs", "Matriarchs", "Ng", "fission_fusion", "Old females lead the group with remembered knowledge."),
        ("traditions", "Traditions", "Q", "matriarchs", "Behaviour passed down the generations (whale songs, chimp tool kits)."),
        ("large_societies", "Large Societies", "Q", "traditions reciprocal_altruism", "Cooperation among many unrelated individuals."),
    ]),
    ("agonistic", "Agonistic Behaviour", "Threats, fights, submission and territory.", [
        ("aggression", "Aggression", "Ed", "", "Pushing, nipping or chasing a rival away from food or space."),
        ("retreat", "Retreat", "Ed", "aggression", "Backing off from a stronger rival before getting hurt."),
        ("overgrowth_fights", "Overgrowth Contests", "Or", "aggression", "Sessile animals fight for space by overgrowing or stinging their neighbours (corals)."),
        ("threat_display", "Threat Display", "Si", "aggression", "Spreading fins, gaping or rearing up to look bigger instead of fighting."),
        ("submission", "Submission Signals", "Si", "retreat", "Showing that you give up, so the winner stops attacking."),
        ("claw_duels", "Claw Duels", "Si", "threat_display", "Sizing each other up and grappling with claws (crustaceans, scorpions)."),
        ("territoriality", "Territoriality", "De", "aggression", "Claiming and defending an area."),
        ("ritualised_fighting", "Ritualised Fighting", "De", "threat_display", "Contests with rules: pushing and wrestling that rarely cause injury."),
        ("rival_assessment", "Assessing Rivals", "Pe", "threat_display", "Judging a rival's strength before deciding whether to fight."),
        ("winner_effect", "Winner and Loser Effects", "Pe", "submission", "Winning makes an animal bolder; losing makes it cautious."),
        ("male_combat", "Male Combat", "Pe", "ritualised_fighting", "Shoving, wrestling and butting rivals."),
        ("dear_enemy", "Dear Enemy Effect", "Cr", "territoriality", "Known neighbours are tolerated; fights are saved for strangers."),
        ("head_butting", "Head Butting", "Cr", "male_combat", "Dome-headed clashes (pachycephalosaurs, later rams)."),
        ("siblicide", "Siblicide", "Cr", "aggression", "The strongest chick kills its nestmates (eagles, boobies)."),
        ("food_stealing", "Food Stealing", "Cr", "aggression", "Robbing other animals of their catch (skuas)."),
        ("harems", "Harems", "Pg", "male_combat", "One male defends a group of females."),
        ("infanticide", "Infanticide", "Pg", "harems", "A male taking over a group kills his rival's young (lions)."),
        ("antler_tournaments", "Antler Tournaments", "Ng", "male_combat", "Ritual antler fights (deer)."),
        ("rutting_season", "Rutting Season", "Ng", "male_combat", "A short, intense mating season."),
        ("border_patrols", "Border Patrols", "Ng", "territoriality", "Groups patrol and raid the edges of their range (chimpanzees, wolves)."),
    ]),
    ("communication", "Communication Behaviour", "Scent, colour, sound and language.", [
        ("chemical_signals", "Chemical Signals", "Ed", "", "Leaving chemical traces for others to detect."),
        ("pheromones", "Pheromones", "Or", "chemical_signals", "Chemical messages to your own species."),
        ("substrate_vibration", "Substrate Vibration", "Or", "chemical_signals", "Tapping signals through the ground or a web."),
        ("colour_signals", "Colour Signals", "Si", "chemical_signals", "Changing or showing colours to send messages."),
        ("light_signals", "Light Signals", "Si", "colour_signals", "Flashing light codes (deep-sea fish, later fireflies)."),
        ("stridulation", "Stridulation", "Cb", "substrate_vibration", "Rubbing body parts together to chirp."),
        ("display_postures", "Display Postures", "Pe", "colour_signals", "Showing size and colour to settle disputes without fighting."),
        ("scent_marking", "Scent Marking", "Tr", "pheromones", "Marking territory with scent."),
        ("vocal_communication", "Vocal Communication", "Cr", "stridulation", "Calls made with the voice."),
        ("alarm_calls", "Alarm Calls", "Cr", "vocal_communication", "Warning the group that a predator is near."),
        ("electric_signals", "Electric Signals", "Pg", "chemical_signals", "Talking with electric pulses (weakly electric fish)."),
        ("waggle_dance", "Waggle Dance", "Pg", "substrate_vibration", "Dancing the direction of food to the hive (honeybees)."),
        ("learned_song", "Learned Song", "Pg", "vocal_communication", "Songs copied from adults (songbirds)."),
        ("facial_expressions", "Facial Expressions", "Pg", "display_postures", "Faces that show mood (mammals)."),
        ("duets", "Duets", "Ng", "learned_song", "Pairs singing together in time."),
        ("referential_calls", "Referential Calls", "Ng", "alarm_calls", "Different alarms for eagle, snake and leopard (vervet monkeys)."),
        ("infrasound", "Infrasound", "Ng", "vocal_communication", "Calls too low for us to hear that carry for kilometres (elephants)."),
        ("whale_song", "Whale Song", "Ng", "learned_song", "Long songs that change from year to year."),
        ("gestures", "Gestures", "Ng", "facial_expressions", "Meaningful hand and body movements (great apes)."),
        ("language", "Language", "Q", "referential_calls gestures", "Open-ended symbolic speech."),
    ]),
    ("migration", "Migratory Behaviour", "Steering, homing and long journeys.", [
        ("taxis", "Taxis", "Ed", "", "Steering toward food and away from danger by following gradients."),
        ("light_following", "Light Following", "Ed", "taxis", "Moving toward or away from light."),
        ("home_range", "Home Range", "Or", "taxis", "Staying in and returning to a familiar area."),
        ("vertical_migration", "Daily Vertical Migration", "Or", "light_following", "Rising at night and sinking by day (plankton)."),
        ("facing_current", "Facing the Current", "Si", "taxis", "Holding position against flowing water."),
        ("land_excursions", "Land Excursions", "Si", "home_range", "Short trips out of the water onto land."),
        ("seasonal_migration", "Seasonal Migration", "Cb", "home_range", "Moving with the seasons.", "hibernation"),
        ("sun_compass", "Sun Compass", "Cb", "light_following", "Navigating by the sun's position."),
        ("mass_dispersal", "Mass Dispersal Flights", "Cb", "land_excursions", "Swarms take off together to settle new ground."),
        ("ballooning", "Ballooning", "Pe", "mass_dispersal", "Drifting on the wind on silk threads (spiders)."),
        ("landmark_maps", "Landmark Maps", "Tr", "home_range", "Learning landmarks to find the way home."),
        ("natal_homing", "Natal Homing", "Cr", "seasonal_migration", "Returning to the place of birth to breed (salmon, turtles)."),
        ("magnetic_navigation", "Magnetic Navigation", "Cr", "natal_homing", "Steering by the Earth's magnetic field."),
        ("path_integration", "Path Integration", "Cr", "sun_compass", "Counting steps and turns to head straight home (ants)."),
        ("star_navigation", "Star Navigation", "Pg", "sun_compass", "Steering by the stars (migrating birds)."),
        ("ocean_migration", "Ocean Migration", "Pg", "magnetic_navigation", "Journeys of thousands of kilometres every year (whales, terns)."),
        ("rafting", "Rafting", "Pg", "land_excursions", "Crossing oceans on floating vegetation (monkeys to South America)."),
        ("nomadic_herds", "Nomadic Herds", "Ng", "seasonal_migration", "Following the rains and the grass (wildebeest)."),
        ("altitudinal_migration", "Altitudinal Migration", "Ng", "seasonal_migration", "Up the mountain in summer, down in winter."),
    ]),
    ("nest_building", "Nest-building Behaviour", "Tubes, burrows, nests, cells and mounds.", [
        ("settling", "Settling", "Ed", "", "Choosing a good spot on the sea floor to settle."),
        ("tube_building", "Tube Building", "Ed", "settling", "Building a protective tube to live in."),
        ("burrow_systems", "Burrow Systems", "Ed", "settling", "Digging tunnels in the sediment.", "burrowing"),
        ("reef_building", "Reef Building", "Ed", "tube_building", "Building reefs together (archaeocyathids, later corals)."),
        ("rock_boring", "Rock Boring", "Or", "burrow_systems", "Drilling homes into rock and wood."),
        ("burrow_nests", "Burrow Nests", "Pe", "burrow_systems", "Raising young underground."),
        ("silk_shelters", "Silk Shelters", "Pe", "tube_building", "Spinning silk retreats and cocoons."),
        ("nesting", "Nesting", "Tr", "burrow_nests", "Building a nest for eggs and young.", "parental_care"),
        ("nest_defence", "Nest Defence", "Tr", "nesting", "Fighting off nest raiders."),
        ("provisioned_cells", "Provisioned Cells", "Ju", "burrow_nests", "Sealed cells stocked with food for the larvae (wasps)."),
        ("incubation", "Incubation", "Cr", "nesting", "Sitting on the eggs to keep them warm."),
        ("colonial_nesting", "Colonial Nesting", "Cr", "nest_defence", "Nesting in large, defended colonies."),
        ("woven_nests", "Woven Nests", "Cr", "nesting", "Weaving nests from plant fibres."),
        ("mud_nests", "Mud Nests", "Cr", "nesting", "Nests plastered together from pellets of mud (swallows, potter wasps)."),
        ("paper_nests", "Paper Nests", "Cr", "provisioned_cells", "Chewed wood pulp shaped into hanging combs (paper wasps)."),
        ("termite_mounds", "Termite Mounds", "Pg", "burrow_systems", "Climate-controlled mound cities."),
        ("wax_combs", "Wax Combs", "Pg", "provisioned_cells", "Building combs of hexagonal wax cells (bees)."),
        ("bubble_nests", "Bubble Nests", "Pg", "nesting", "Floating rafts of mucus bubbles that hold the eggs (gouramis, bettas)."),
        ("bowers", "Bowers", "Ng", "woven_nests", "Decorated display structures (bowerbirds)."),
        ("dam_building", "Dam Building", "Ng", "burrow_systems", "Engineering ponds with dams (beavers)."),
    ]),
    ("maintenance", "Maintenance Behaviour", "Grooming, cleaning, keeping cool or warm, and staying healthy.", [
        ("self_cleaning", "Self-cleaning", "Ed", "", "Wiping sediment and fouling off the body with cilia or limbs."),
        ("moulting_behaviour", "Moulting Behaviour", "Ed", "self_cleaning", "Hiding away while a new cuticle hardens."),
        ("basking", "Basking", "De", "self_cleaning", "Warming up in the sun before becoming active."),
        ("shade_seeking", "Shade Seeking", "De", "basking", "Moving into shade or burrows to avoid overheating."),
        ("antenna_grooming", "Antenna Grooming", "De", "self_cleaning", "Cleaning antennae and legs with special combs (insects)."),
        ("scratching", "Scratching", "Cb", "self_cleaning", "Scratching itchy skin with a hind foot."),
        ("skin_rubbing", "Rubbing", "Pe", "scratching", "Rubbing against rocks and trees to scrape off parasites."),
        ("skin_shedding", "Skin Shedding", "Pe", "moulting_behaviour", "Rubbing off the old skin, sometimes in one piece (snakes, lizards)."),
        ("mud_wallowing", "Mud Wallowing", "Tr", "skin_rubbing", "Coating the skin with mud to cool off and keep insects away."),
        ("wound_licking", "Wound Licking", "Tr", "scratching", "Licking wounds clean: saliva kills bacteria."),
        ("panting", "Panting", "Tr", "shade_seeking", "Cooling off by breathing fast."),
        ("preening", "Preening", "Ju", "scratching", "Straightening and oiling feathers with the beak."),
        ("huddling", "Huddling", "Cr", "basking", "Pressing together to keep warm (penguins, mice)."),
        ("cleaning_stations", "Cleaning Stations", "Cr", "self_cleaning", "Cleaner fish and shrimp service visiting 'clients'."),
        ("dust_bathing", "Dust Bathing", "Cr", "preening", "Rolling in dust to remove excess oil and parasites."),
        ("bathing", "Bathing", "Cr", "preening", "Splashing in water to clean feathers or fur."),
        ("nest_sanitation", "Nest Sanitation", "Cr", "self_cleaning", "Carrying waste and dead nestmates out of the nest (bees, birds)."),
        ("anting", "Anting", "Pg", "preening", "Rubbing ants into the feathers for their formic acid."),
        ("latrines", "Latrines", "Pg", "nest_sanitation", "Using fixed dung sites away from food and young."),
        ("self_medication", "Self-medication", "Ng", "wound_licking", "Eating bitter plants or clay to fight parasites and toxins (chimpanzees, parrots)."),
    ]),
    ("resting", "Resting Behaviour", "Sleep, shelter, dormancy and saving energy.", [
        ("quiescence", "Quiescence", "Ed", "", "Periods of stillness that save energy."),
        ("daily_rhythm", "Daily Rhythm", "Ed", "quiescence", "An internal clock sets the times for activity and rest."),
        ("shelter_resting", "Resting in Shelter", "Or", "quiescence", "Resting in crevices or burrows out of sight."),
        ("sleep", "Sleep", "Or", "daily_rhythm", "Deep, reversible rest with the senses turned down."),
        ("mucus_cocoon", "Mucus Cocoon", "De", "shelter_resting", "Sleeping inside a bubble of mucus (parrotfish, lungfish)."),
        ("deep_sleep", "Deep Sleep", "Pe", "sleep", "Slow-wave sleep that restores the brain."),
        ("nocturnal_refuge", "Nocturnal Refuge", "Tr", "daily_rhythm", "Active only at night (early mammals)."),
        ("roosting", "Roosting", "Ju", "shelter_resting", "Resting high off the ground, out of reach of predators."),
        ("dreaming_sleep", "Dreaming Sleep", "Ju", "deep_sleep", "REM sleep that consolidates memories (mammals, birds)."),
        ("half_brain_sleep", "Half-brain Sleep", "Cr", "deep_sleep", "One half of the brain sleeps while the other keeps watch (dolphins, ducks)."),
        ("communal_roosts", "Communal Roosts", "Pg", "roosting", "Sleeping together in large numbers."),
        ("hanging_roost", "Hanging Roost", "Pg", "roosting", "Resting upside down, ready to drop into flight (bats)."),
        ("crepuscular_activity", "Dawn and Dusk Activity", "Pg", "daily_rhythm", "Active in twilight, between the day and night shifts of predators."),
        ("winter_dens", "Winter Dens", "Pg", "shelter_resting", "Sheltering in a den through the cold months (bears)."),
        ("sleeping_nests", "Sleeping Nests", "Ng", "roosting", "Building a fresh bed in the trees every night (great apes)."),
        ("sleeping_on_the_wing", "Sleeping on the Wing", "Ng", "half_brain_sleep", "Sleeping in flight (swifts, frigatebirds)."),
        ("sentinels", "Sentinels", "Ng", "communal_roosts", "One keeps watch while the rest sleep or feed (meerkats)."),
        ("rafting_rest", "Resting in Rafts", "Ng", "communal_roosts", "Floating together, holding on to each other or to kelp (sea otters)."),
    ]),
]


def build(branches, out_path):
    nodes, by_id = [], {}
    for branch_id, _, _, entries in branches:
        for e in entries:
            node_id, name, age, pre, desc = e[:5]
            genes = e[5].split() if len(e) > 5 and e[5] else []
            assert node_id not in by_id, f"duplicate id {node_id}"
            by_id[node_id] = {"id": node_id, "displayName": name, "branch": branch_id, "tier": 0, "row": 0, "cost": 0,
                              "age": AGES[age], "prerequisites": pre.split(), "unlocksGenes": genes, "description": desc}
            nodes.append(by_id[node_id])

    # Checks: references exist, prerequisites are not from a later period
    # and are in the node's own branch, so every one is drawn as a line in its tab
    for n in nodes:
        for p in n["prerequisites"]:
            assert p in by_id, f"{n['id']}: unknown prerequisite {p}"
            pa, na = list(AGES.values()).index(by_id[p]["age"]), list(AGES.values()).index(n["age"])
            assert pa <= na, f"{n['id']} ({n['age']}) requires later {p} ({by_id[p]['age']})"
            assert by_id[p]["branch"] == n["branch"], f"{n['id']}: prerequisite {p} is in another branch"

    # Layout per branch: column = longest chain of same-branch prerequisites; rows in order,
    # each node as close as possible to the average row of its prerequisites
    for branch_id, *_ in branches:
        members = [n for n in nodes if n["branch"] == branch_id]
        depth = {}
        def tier(n):
            if n["id"] not in depth:
                local = [by_id[p] for p in n["prerequisites"] if by_id[p]["branch"] == branch_id]
                depth[n["id"]] = 1 + max((tier(p) for p in local), default=-1)
            return depth[n["id"]]
        for n in members:
            n["tier"] = tier(n)
        used = {}
        for n in sorted(members, key=lambda n: (n["tier"], members.index(n))):
            local = [by_id[p] for p in n["prerequisites"] if by_id[p]["branch"] == branch_id]
            want = round(sum(p["row"] for p in local) / len(local)) if local else 0
            taken = used.setdefault(n["tier"], set())
            row = min((r for r in range(0, 40) if r not in taken), key=lambda r: (abs(r - want), r))
            taken.add(row)
            n["row"] = row
        roots = [n for n in members if not n["prerequisites"]]
        assert len(roots) == 1, f"branch {branch_id} should have exactly one root, has {[r['id'] for r in roots]}"

    for n in nodes:
        age_index = list(AGES.values()).index(n["age"])
        n["cost"] = 0 if not n["prerequisites"] else max(4, round((4 + 2 * n["tier"] + age_index) * 0.65))

    data = {"branches": [{"id": b, "displayName": name, "description": desc} for b, name, desc, _ in branches],
            "nodes": nodes}
    Path(out_path).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    counts = {b: sum(1 for n in nodes if n["branch"] == b) for b, *_ in branches}
    print(f"{out_path}: {len(nodes)} nodes {counts}")


if __name__ == "__main__":
    data_dir = Path(__file__).resolve().parents[2] / "Assets" / "Resources" / "Data"
    build(MORPHOLOGY, data_dir / "morphology.json")
    build(ETHOLOGY, data_dir / "ethology.json")
