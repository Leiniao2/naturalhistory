"""Generates Assets/Resources/Data/plants.json: the plant species shown on the map.

Each plant: period range, layer ("canopy" = forest trees, "ground" = open ground / understory),
the terrains it grows on (TerrainKind names, as the map shows them in its period, see EraFlora),
for canopy plants the forest types it forms, the mesh form, a leaf tint (multiplies the form's
leaf colours) and a size. Checks every period × terrain × layer the map can show has plants.
Run: python3 tools/flora/plants.py
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "Assets", "Resources", "Data")
AGES = "Cambrian Ordovician Silurian Devonian Carboniferous Permian Triassic Jurassic Cretaceous Paleogene Neogene Quaternary".split()
AB = {a[:3]: a for a in AGES}
CANOPY_FORMS = {"Lycopsid","Sigillaria","Calamites","TreeFern","Cycad","Bennettitalean","Araucaria","Ginkgo","Glossopteris",
                "Cordaites","Archaeopteris","Wattieza","Conifer","Broadleaf","Palm","Acacia","Baobab","Mangrove","Bamboo"}
GROUND_FORMS = {"GroundFern","Horsetail","Moss","Cooksonia","Grass","Shrub","Flower","Reed","WaterLily","Succulent","Cactus",
                "Cycad","Bennettitalean","Clubmoss"}
UNDER_FORMS = {"Algae","Seagrass","Kelp","Coralline","Charophyte","Stromatolite"}
UNDER_TERRAINS = {"Seabed","DeepSeabed","Lakebed"}  # UnderKind names (the layer below the map)
B, C, J = "Broadleaf", "Conifer", "Jungle"

# id, common name, scientific name, group, first, last ("" = today), layer, terrains, forests, form, tint, size, note
P = [
 # ---- Ordovician–Silurian: the first land plants ----
 ("liverwort","Thalloid liverwort","Marchantiophyta","Liverwort","Ord","","ground",["Mossland","Wetland","Rainforest"],[],"Moss","#B8E090",0.9,"Flat green lobes on damp ground: among the very first land plants."),
 ("cryptospore_moss","Cryptospore plant","Cryptospore-producing embryophytes","Early land plant","Ord","Sil","ground",["Mossland","Barren"],[],"Moss","#C8D890",0.7,"Known only from their spores; tiny moss-like crusts."),
 ("hornwort","Hornwort","Anthocerotophyta","Hornwort","Sil","","ground",["Mossland","Wetland"],[],"Cooksonia","#A8D070",0.8,"Flat thalli sprouting horn-shaped spore capsules."),
 ("cooksonia","Cooksonia","Cooksonia pertoni","Early vascular plant","Sil","Dev","ground",["Mossland","Wetland"],[],"Cooksonia","#C0D070",1.0,"The first known vascular plant: forked stems a few centimetres tall."),
 ("baragwanathia","Baragwanathia","Baragwanathia longifolia","Lycopsid","Sil","Dev","ground",["Mossland","Wetland"],[],"Clubmoss","#90C060",1.0,"An early clubmoss with leafy stems."),
 ("early_moss","True moss","Bryophyta","Moss","Sil","","ground",["Mossland","Wetland","Tundra","Rainforest","Hill"],[],"Moss","#A0C860",1.0,"Cushions of moss on damp ground and rocks."),
 # ---- Devonian ----
 ("rhynia","Rhynia","Rhynia gwynne-vaughanii","Rhyniophyte","Dev","Dev","ground",["Mossland","Wetland"],[],"Cooksonia","#B8D070",1.4,"Leafless forked stems from the Rhynie chert hot springs."),
 ("aglaophyton","Aglaophyton","Aglaophyton major","Polysporangiophyte","Dev","Dev","ground",["Mossland","Wetland"],[],"Cooksonia","#A8C868",1.5,"Rhynie chert plant with water-conducting tissue but no leaves."),
 ("zosterophyllum","Zosterophyllum","Zosterophyllum myretonianum","Zosterophyll","Sil","Dev","ground",["Mossland","Wetland"],[],"Clubmoss","#98C070",1.1,"Clumps of stems with spore sacs along the sides."),
 ("psilophyton","Psilophyton","Psilophyton dawsonii","Trimerophyte","Dev","Dev","ground",["Mossland","Hill","Barren"],[],"Cooksonia","#C8D878",1.8,"Branching stems up to half a metre: forerunner of ferns and seed plants."),
 ("asteroxylon","Asteroxylon","Asteroxylon mackiei","Lycopsid","Dev","Dev","ground",["Mossland","Wetland"],[],"Clubmoss","#88B858",1.3,"Leafy clubmoss of the Rhynie chert."),
 ("drepanophycus","Drepanophycus","Drepanophycus spinaeformis","Lycopsid","Dev","Dev","ground",["Mossland","Hill"],[],"Clubmoss","#90B860",1.2,"Creeping clubmoss with spiny leaves."),
 ("leclercqia","Leclercqia","Leclercqia complexa","Lycopsid","Dev","Dev","ground",["Mossland","Wetland","Hill"],[],"Clubmoss","#80B060",1.0,"Herbaceous clubmoss with forked leaves."),
 ("pertica","Pertica","Pertica quadrifaria","Trimerophyte","Dev","Dev","ground",["Mossland","Hill"],[],"Horsetail","#B0C870",1.6,"Upright, much-branched stems nearly a metre tall."),
 ("rellimia","Rellimia","Rellimia thomsonii","Progymnosperm","Dev","Dev","ground",["Mossland","Hill","Wetland"],[],"Shrub","#90B060",1.2,"Shrubby progymnosperm."),
 ("elkinsia","Elkinsia","Elkinsia polymorpha","Seed fern","Dev","Dev","ground",["Mossland","Wetland"],[],"GroundFern","#90C070",1.1,"The oldest known seed plant."),
 ("archaeopteris","Archaeopteris","Archaeopteris hibernica","Progymnosperm","Dev","Car","canopy",["Mossland","Wetland","Hill","FernPrairie"],[B,C],"Archaeopteris","#FFFFFF",1.0,"The first modern-looking tree, forming the first forests."),
 ("wattieza","Wattieza","Wattieza givetiana (Eospermatopteris)","Cladoxylopsid","Dev","Dev","canopy",["Mossland","Wetland"],[B,J],"Wattieza","#FFFFFF",1.0,"The earliest known tree: a pole with a crown of branches, Gilboa forest."),
 ("calamophyton","Calamophyton","Calamophyton primaevum","Cladoxylopsid","Dev","Dev","canopy",["Mossland","Wetland"],[J],"Wattieza","#D8F0B0",0.8,"Small tree with a crown of finger-like branches."),
 ("protolepidodendron","Protolepidodendron","Protolepidodendron scharyanum","Lycopsid","Dev","Dev","canopy",["Mossland","Wetland"],[J],"Lycopsid","#C0E8A0",0.55,"A small early scale tree."),
 # ---- Carboniferous ----
 ("lepidodendron","Scale tree","Lepidodendron aculeatum","Lycopsid","Car","Per","canopy",["CoalSwamp","Wetland","FernPrairie"],[J,B],"Lycopsid","#FFFFFF",1.0,"Giant club moss up to 40 m; its trunks became coal."),
 ("lepidophloios","Lepidophloios","Lepidophloios laricinus","Lycopsid","Car","Car","canopy",["CoalSwamp"],[J],"Lycopsid","#E0F0C0",0.85,"Scale tree with a dense, drooping crown."),
 ("sigillaria","Sigillaria","Sigillaria elegans","Lycopsid","Car","Per","canopy",["CoalSwamp","Wetland","FernPrairie"],[J,B],"Sigillaria","#FFFFFF",1.0,"Ribbed lycopsid trunk topped by tufts of grassy leaves."),
 ("calamites","Calamites","Calamites carinatus","Horsetail","Car","Per","canopy",["CoalSwamp","Wetland","FernPrairie"],[J],"Calamites","#FFFFFF",1.0,"Tree-sized horsetail growing in thickets along rivers."),
 ("psaronius","Psaronius","Psaronius (Marattiales)","Tree fern","Car","Per","canopy",["CoalSwamp","FernPrairie","Rainforest","Wetland"],[J,B],"TreeFern","#FFFFFF",1.0,"Marattialean tree fern with a trunk wrapped in roots."),
 ("medullosa","Medullosa","Medullosa noei","Seed fern","Car","Per","canopy",["CoalSwamp","FernPrairie","Wetland"],[J,B],"TreeFern","#C8E098",0.9,"Seed fern tree with huge fronds and seeds the size of eggs."),
 ("cordaites","Cordaites","Cordaites principalis","Cordaitale","Car","Per","canopy",["FernPrairie","Hill","CoalSwamp"],[C,B],"Cordaites","#FFFFFF",1.0,"Tall tree with strap-shaped leaves, related to conifers."),
 ("walchia","Walchia","Walchia piniformis","Conifer","Car","Per","canopy",["FernPrairie","Hill","Desert"],[C],"Conifer","#D8F0D0",0.85,"One of the first conifers, like a small Norfolk pine."),
 ("neuropteris","Neuropteris","Neuropteris heterophylla","Seed fern","Car","Per","ground",["FernPrairie","CoalSwamp","Wetland","Hill"],[],"GroundFern","#C0E0A0",1.1,"Seed fern whose tongue-shaped leaflets are common coal-ball fossils."),
 ("alethopteris","Alethopteris","Alethopteris serlii","Seed fern","Car","Per","ground",["FernPrairie","CoalSwamp"],[],"GroundFern","#A8D088",1.2,"Fern-like seed plant of the coal forests."),
 ("sphenophyllum","Sphenophyllum","Sphenophyllum emarginatum","Horsetail","Car","Tri","ground",["CoalSwamp","FernPrairie","Wetland"],[],"Horsetail","#B0D878",0.8,"Scrambling horsetail with wedge-shaped leaves in whorls."),
 ("botryopteris","Botryopteris","Botryopteris forensis","Fern","Car","Per","ground",["FernPrairie","CoalSwamp","Rainforest"],[],"GroundFern","#98C878",0.9,"Small early fern, often growing on other plants."),
 ("selaginella","Spikemoss","Selaginella","Lycopsid","Car","","ground",["CoalSwamp","FernPrairie","Rainforest","Wetland","Hill"],[],"Clubmoss","#88C068",0.9,"Low clubmoss lineage that survives today."),
 ("lycopodium","Clubmoss","Lycopodium","Lycopsid","Car","","ground",["FernPrairie","Hill","Tundra","Rainforest"],[],"Clubmoss","#98C878",1.0,"Evergreen creeping clubmoss."),
 # ---- Permian ----
 ("glossopteris","Glossopteris","Glossopteris browniana","Seed fern","Per","Tri","canopy",["FernPrairie","Wetland","Hill","Tundra"],[B,J],"Glossopteris","#FFFFFF",1.0,"Tongue-leaved tree of Gondwana; its spread helped prove continental drift."),
 ("gangamopteris","Gangamopteris","Gangamopteris cyclopteroides","Seed fern","Per","Per","canopy",["FernPrairie","Wetland"],[B],"Glossopteris","#D8E8B0",0.85,"Early glossopterid of the cold southern lowlands."),
 ("gigantopteris","Gigantopteris","Gigantopteris nicotianaefolia","Gigantopterid","Per","Per","canopy",["Rainforest","Wetland","FernPrairie"],[J],"Glossopteris","#B0E0A0",0.9,"Climbing seed plant with broad, net-veined leaves, in tropical Cathaysia."),
 ("ullmannia","Ullmannia","Ullmannia bronnii","Conifer","Per","Per","canopy",["FernPrairie","Hill","Desert"],[C],"Conifer","#C8E8C8",0.9,"Conifer of the dry Zechstein coasts."),
 ("voltzia","Voltzia","Voltzia heterophylla","Conifer","Per","Tri","canopy",["FernPrairie","Hill","Wetland"],[C,B],"Conifer","#C0E0C0",1.0,"Conifer of the Permian and Triassic."),
 ("taeniopteris","Taeniopteris","Taeniopteris","Cycadophyte","Per","Cre","ground",["FernPrairie","Rainforest","Hill"],[],"Cycad","#C8E0A0",0.9,"Strap-leaved plant related to the cycads."),
 ("equisetites","Giant horsetail","Equisetites arenaceus","Horsetail","Per","Jur","ground",["FernPrairie","Wetland","Rainforest"],[],"Horsetail","#A0D070",1.6,"Horsetails as thick as a wrist, lining Triassic rivers."),
 ("osmunda","Royal fern","Osmunda","Fern","Per","","ground",["FernPrairie","Wetland","Rainforest","Hill"],[],"GroundFern","#A8D888",1.3,"Royal ferns have barely changed in 200 million years."),
 ("lebachia","Lebachia","Lebachia (Utrechtia)","Conifer","Per","Per","canopy",["Hill","FernPrairie"],[C],"Conifer","#D0E8C0",0.8,"Early Permian walchian conifer."),
 # ---- Triassic ----
 ("dicroidium","Dicroidium","Dicroidium odontopteroides","Seed fern","Tri","Tri","canopy",["FernPrairie","Wetland","Hill"],[B,J],"Glossopteris","#C8E8A8",1.0,"Seed fern tree that dominated southern Triassic forests."),
 ("araucarioxylon","Araucarioxylon","Araucarioxylon arizonicum (Agathoxylon)","Conifer","Tri","Tri","canopy",["FernPrairie","Hill","Wetland"],[C],"Araucaria","#FFFFFF",1.0,"The great logs of the Petrified Forest, Arizona."),
 ("pleuromeia","Pleuromeia","Pleuromeia sternbergii","Lycopsid","Tri","Tri","ground",["FernPrairie","Desert","Hill","Barren"],[],"Clubmoss","#B8D080",1.6,"Unbranched lycopsid that spread over the world after the end-Permian extinction."),
 ("neocalamites","Neocalamites","Neocalamites carrerei","Horsetail","Tri","Jur","ground",["Wetland","FernPrairie"],[],"Horsetail","#A0C870",1.4,"Triassic horsetail of river banks."),
 ("bjuvia","Bjuvia","Bjuvia simplex","Cycad","Tri","Tri","canopy",["Rainforest","FernPrairie"],[J],"Cycad","#FFFFFF",1.4,"One of the earliest true cycads."),
 ("baiera","Baiera","Baiera furcata","Ginkgophyte","Tri","Cre","canopy",["FernPrairie","Hill","Wetland"],[B],"Ginkgo","#D8F0A0",0.9,"Ginkgo relative with deeply divided leaves."),
 ("cladophlebis","Cladophlebis","Cladophlebis","Fern","Tri","Cre","ground",["FernPrairie","Rainforest","Wetland","Hill"],[],"GroundFern","#A0D080",1.2,"Common Mesozoic fern foliage."),
 ("schizoneura","Schizoneura","Schizoneura gondwanensis","Horsetail","Per","Jur","ground",["Wetland","FernPrairie"],[],"Horsetail","#B0D878",1.1,"Gondwanan horsetail with split leaf sheaths."),
 ("lepidopteris","Lepidopteris","Lepidopteris ottonis","Seed fern","Per","Jur","ground",["FernPrairie","Hill"],[],"GroundFern","#C0D890",1.0,"Peltasperm seed fern."),
 ("yuccites","Yuccites","Yuccites vogesiacus","Conifer","Tri","Tri","ground",["Desert","Hill"],[],"Succulent","#B8D0A0",1.0,"Strap-leaved Triassic conifer of dry ground."),
 # ---- Jurassic ----
 ("araucaria_mirabilis","Monkey-puzzle","Araucaria mirabilis","Conifer","Jur","Jur","canopy",["FernPrairie","Hill","Wetland"],[C,B],"Araucaria","#FFFFFF",1.05,"Jurassic monkey-puzzle tree, fossilised cones from Cerro Cuadrado."),
 ("brachyphyllum","Brachyphyllum","Brachyphyllum","Conifer","Tri","Cre","canopy",["FernPrairie","Hill","Desert"],[C],"Conifer","#C8E0C0",0.95,"Scale-leaved conifer of dry Mesozoic coasts."),
 ("pagiophyllum","Pagiophyllum","Pagiophyllum","Conifer","Tri","Cre","canopy",["FernPrairie","Hill"],[C],"Conifer","#B8D8B8",1.0,"Conifer with stiff, awl-shaped leaves."),
 ("ginkgo_huttonii","Jurassic ginkgo","Ginkgo huttonii","Ginkgophyte","Jur","Jur","canopy",["FernPrairie","Wetland","Hill"],[B],"Ginkgo","#FFFFFF",1.0,"Ginkgo with lobed fan leaves."),
 ("czekanowskia","Czekanowskia","Czekanowskia","Czekanowskiale","Tri","Cre","canopy",["Wetland","FernPrairie","Tundra"],[B],"Ginkgo","#E0F0A0",0.85,"Deciduous ginkgo relative of cool, wet forests."),
 ("podozamites","Podozamites","Podozamites lanceolatus","Conifer","Tri","Cre","canopy",["FernPrairie","Wetland"],[C],"Conifer","#C8E8B0",0.9,"Conifer with broad, flat leaves."),
 ("dicksonia","Tree fern","Dicksonia","Tree fern","Jur","","canopy",["Rainforest","FernPrairie","Wetland"],[J],"TreeFern","#D0F0B0",1.05,"Soft tree ferns, alive today in Australia and New Zealand."),
 ("williamsonia","Williamsonia","Williamsonia gigas","Bennettitale","Jur","Cre","ground",["FernPrairie","Rainforest","Hill"],[],"Bennettitalean","#FFFFFF",1.2,"Bennettitalean with flower-like cones."),
 ("cycadeoidea","Cycadeoidea","Cycadeoidea","Bennettitale","Jur","Cre","ground",["FernPrairie","Hill","Desert"],[],"Bennettitalean","#D8E0A0",1.0,"Squat, barrel-trunked bennettitalean."),
 ("matonia","Matonia","Matonia (Phlebopteris)","Fern","Tri","","ground",["FernPrairie","Rainforest"],[],"GroundFern","#A8D890",1.3,"Umbrella-fronded fern; a Jurassic fern-prairie dominant."),
 ("coniopteris","Coniopteris","Coniopteris hymenophylloides","Fern","Jur","Cre","ground",["FernPrairie","Wetland","Rainforest"],[],"GroundFern","#98D080",1.6,"Fern of the Jurassic understory; the 'giant ferns' of dinosaur country."),
 ("equisetum","Horsetail","Equisetum","Horsetail","Jur","","ground",["Wetland","FernPrairie","Plain","Tundra"],[],"Horsetail","#A0D070",1.0,"Living horsetails; their kind has been around since the Jurassic."),
 ("cycas","Cycad","Cycas","Cycad","Jur","","canopy",["Rainforest","FernPrairie","Savanna"],[J],"Cycad","#E0F0C0",1.3,"Palm-like cycads, a group older than the dinosaurs."),
 ("sciadopitys","Umbrella pine","Sciadopitys","Conifer","Jur","","canopy",["FernPrairie","Hill","Rainforest"],[C],"Conifer","#B0D8A8",0.95,"A living fossil, now only in Japan."),
 # ---- Cretaceous ----
 ("archaefructus","Archaefructus","Archaefructus liaoningensis","Flowering plant","Cre","Cre","ground",["Wetland"],[],"Reed","#C0E890",0.9,"One of the oldest flowering plants, a water plant from Liaoning."),
 ("montsechia","Montsechia","Montsechia vidalii","Flowering plant","Cre","Cre","ground",["Wetland"],[],"WaterLily","#A0D880",0.8,"An early aquatic flowering plant from Spain."),
 ("nymphaea","Water lily","Nymphaea","Flowering plant","Cre","","ground",["Wetland"],[],"WaterLily","#FFFFFF",1.0,"Water lilies are among the oldest flowering plant lineages."),
 ("magnolia","Magnolia","Magnolia","Flowering plant","Cre","","canopy",["FernPrairie","Wetland","Plain","Hill","Rainforest"],[B,J],"Broadleaf","#D0F0B0",1.0,"Magnolias were pollinated by beetles before bees existed."),
 ("platanus","Sycamore","Platanus","Flowering plant","Cre","","canopy",["FernPrairie","Wetland","Plain"],[B],"Broadleaf","#E0F8B0",1.05,"Plane trees along Cretaceous rivers."),
 ("sassafras","Sassafras","Sassafras","Flowering plant","Cre","","canopy",["FernPrairie","Plain","Hill"],[B],"Broadleaf","#C8E8A0",0.9,"Laurel-family tree with mitten-shaped leaves."),
 ("liriodendron","Tulip tree","Liriodendron","Flowering plant","Cre","","canopy",["FernPrairie","Plain","Hill"],[B],"Broadleaf","#E8F8A8",1.1,"Tall magnolia relative with tulip-like flowers."),
 ("sequoia","Redwood","Sequoia","Conifer","Cre","","canopy",["FernPrairie","Hill","Wetland","Plain"],[C],"Conifer","#C8E0C0",1.25,"Redwoods: the tallest trees on Earth."),
 ("metasequoia","Dawn redwood","Metasequoia","Conifer","Cre","","canopy",["Wetland","FernPrairie","Plain","Tundra"],[C],"Conifer","#D8F0B0",1.1,"Deciduous redwood; once covered the Arctic, now wild only in China."),
 ("frenelopsis","Frenelopsis","Frenelopsis","Conifer","Tri","Cre","canopy",["Desert","Hill","FernPrairie"],[C],"Conifer","#B8D0A8",0.75,"Drought-hardy, jointed conifer of dry coasts."),
 ("weichselia","Weichselia","Weichselia reticulata","Fern","Cre","Cre","ground",["FernPrairie","Wetland","Desert"],[],"GroundFern","#B0D088",1.2,"Tough fern of Cretaceous coastal flats."),
 ("tempskya","Tempskya","Tempskya","Fern","Cre","Cre","canopy",["FernPrairie","Rainforest","Wetland"],[J],"TreeFern","#B8E098",0.9,"False tree fern: its 'trunk' was a mass of stems and roots."),
 ("sabal","Palmetto","Sabal","Palm","Cre","","canopy",["Rainforest","Wetland","Plain","Savanna"],[J],"Palm","#FFFFFF",1.0,"Fan palms appear late in the Cretaceous."),
 ("nypa","Nipa palm","Nypa fruticans","Palm","Cre","","canopy",["Wetland","Rainforest"],[J],"Palm","#D8F0A0",0.75,"Mangrove palm; Eocene London was full of them."),
 ("early_flowers","Early flowering herbs","Chloranthaceae","Flowering plant","Cre","","ground",["FernPrairie","Plain","Hill","Rainforest"],[],"Flower","#FFFFFF",1.0,"Small herbs among the first flowering plants."),
 # ---- Paleogene ----
 ("taxodium","Bald cypress","Taxodium","Conifer","Pal","","canopy",["Wetland","Plain","Rainforest"],[C,J],"Conifer","#E0F0A8",1.0,"Swamp conifer with 'knees' poking out of the water."),
 ("quercus","Oak","Quercus","Flowering plant","Pal","","canopy",["Plain","Hill","Savanna","Steppe"],[B],"Broadleaf","#FFFFFF",1.05,"Oaks spread across the northern continents."),
 ("fagus","Beech","Fagus","Flowering plant","Pal","","canopy",["Plain","Hill"],[B],"Broadleaf","#E8FFC0",1.1,"Smooth-barked trees of shady forests."),
 ("acer","Maple","Acer","Flowering plant","Pal","","canopy",["Plain","Hill","Tundra"],[B],"Broadleaf","#F8E8A8",1.0,"Maples, with winged seeds."),
 ("laurus","Laurel","Laurus","Flowering plant","Pal","","canopy",["Plain","Rainforest","Hill"],[B,J],"Broadleaf","#C0E0A0",0.95,"Evergreen laurel forests of the warm Eocene."),
 ("alnus","Alder","Alnus","Flowering plant","Pal","","canopy",["Wetland","Plain","Tundra"],[B],"Broadleaf","#C8E8A8",0.9,"Alders grow with their roots in wet ground."),
 ("ficus","Fig","Ficus","Flowering plant","Pal","","canopy",["Rainforest","Savanna","Wetland"],[J,B],"Broadleaf","#B8E098",1.15,"Figs and their wasps have evolved together for 60 million years."),
 ("rhizophora","Red mangrove","Rhizophora","Flowering plant","Pal","","canopy",["Wetland","Rainforest"],[J],"Mangrove","#FFFFFF",1.0,"Mangroves stand on stilt roots in salt water."),
 ("ginkgo_biloba","Ginkgo","Ginkgo biloba","Ginkgophyte","Pal","","canopy",["Plain","Hill","Tundra"],[B],"Ginkgo","#F0F8A0",1.0,"The last ginkgo: a living fossil."),
 ("early_grass","Early grasses","Poaceae (bamboos and early grasses)","Grass","Pal","","ground",["Plain","Hill","Savanna","Steppe","Tundra"],[],"Grass","#D0E8A0",0.9,"Grasses existed but didn't form grasslands until the Neogene."),
 ("nothofagus","Southern beech","Nothofagus","Flowering plant","Cre","","canopy",["Hill","Plain","Tundra","FernPrairie"],[B],"Broadleaf","#B8D898",0.95,"Beeches of the southern continents, from Antarctica to Patagonia."),
 ("cinnamomum","Camphor tree","Cinnamomum","Flowering plant","Pal","","canopy",["Rainforest","Plain"],[J,B],"Broadleaf","#A8D898",1.0,"Laurel-family tree of warm forests."),
 ("pinus","Pine","Pinus","Conifer","Cre","","canopy",["Hill","Plain","Tundra","Steppe","FernPrairie"],[C],"Conifer","#C0D8B0",1.0,"Pines: hardy conifers of poor soils and cold."),
 # ---- Neogene–Quaternary ----
 ("picea","Spruce","Picea","Conifer","Neo","","canopy",["Tundra","Hill","Plain"],[C],"Conifer","#A8C8B0",1.05,"The dark spruces of the boreal forest."),
 ("larix","Larch","Larix","Conifer","Neo","","canopy",["Tundra","Hill"],[C],"Conifer","#E0F0B0",1.0,"A conifer that drops its needles in winter."),
 ("abies","Fir","Abies","Conifer","Neo","","canopy",["Hill","Tundra","Plain"],[C],"Conifer","#98C0A8",1.1,"Firs of cool mountain forests."),
 ("betula","Birch","Betula","Flowering plant","Neo","","canopy",["Tundra","Plain","Hill"],[B],"Broadleaf","#E8FFB0",0.85,"White-barked birches, first trees back after the ice."),
 ("eucalyptus","Eucalyptus","Eucalyptus","Flowering plant","Neo","","canopy",["Savanna","Plain","Hill","Steppe"],[B,J],"Broadleaf","#B8D0B8",1.15,"Gum trees: fire-adapted Australian forests."),
 ("acacia","Acacia","Vachellia (Acacia)","Flowering plant","Neo","","canopy",["Savanna","Steppe","Desert"],[B],"Acacia","#FFFFFF",1.0,"Flat-topped thorn trees of the savanna."),
 ("baobab","Baobab","Adansonia digitata","Flowering plant","Neo","","canopy",["Savanna","Steppe"],[B],"Baobab","#FFFFFF",1.0,"Swollen trunks store water through the dry season."),
 ("ceiba","Kapok tree","Ceiba pentandra","Flowering plant","Neo","","canopy",["Rainforest"],[J],"Broadleaf","#B0E090",1.35,"Emergent giant towering over the rainforest canopy."),
 ("dipterocarp","Dipterocarp","Shorea","Flowering plant","Neo","","canopy",["Rainforest"],[J],"Broadleaf","#A8D890",1.3,"Tall trees of Southeast Asian rainforests."),
 ("bamboo","Bamboo","Phyllostachys","Grass","Neo","","canopy",["Rainforest","Hill","Plain"],[J,B],"Bamboo","#FFFFFF",1.0,"Giant grasses that grow a metre a day."),
 ("phoenix","Date palm","Phoenix dactylifera","Palm","Neo","","canopy",["Desert","Savanna","Wetland"],[J],"Palm","#C8D8A0",1.05,"Palm of desert oases."),
 ("cocos","Coconut palm","Cocos nucifera","Palm","Neo","","canopy",["Rainforest","Wetland","Savanna"],[J],"Palm","#E0F0A0",1.15,"Its floating nuts spread it to tropical shores worldwide."),
 ("themeda","Red oat grass","Themeda triandra","Grass","Neo","","ground",["Savanna","Steppe","Plain"],[],"Grass","#F0C890",1.2,"C4 grass of the African and Australian savannas."),
 ("stipa","Feather grass","Stipa","Grass","Neo","","ground",["Steppe","Plain","Desert"],[],"Grass","#E8E0A8",1.1,"Feathery grass of the Eurasian steppe."),
 ("poa","Meadow grass","Poa","Grass","Neo","","ground",["Plain","Hill","Tundra"],[],"Grass","#FFFFFF",1.0,"Temperate meadow grasses."),
 ("andropogon","Big bluestem","Andropogon gerardi","Grass","Neo","","ground",["Plain","Steppe","Savanna"],[],"Grass","#B8C8D0",1.4,"Tall grass of the North American prairie."),
 ("triodia","Spinifex","Triodia","Grass","Neo","","ground",["Desert","Steppe"],[],"Grass","#D8D090",0.9,"Spiny hummock grass of Australia's deserts."),
 ("mammoth_steppe_grass","Mammoth-steppe sedge","Carex (steppe sedges)","Sedge","Qua","","ground",["Steppe","Tundra"],[],"Grass","#C8D098",0.9,"Grasses and sedges of the Ice Age mammoth steppe."),
 ("artemisia","Sagebrush","Artemisia","Flowering plant","Neo","","ground",["Steppe","Desert","Hill"],[],"Shrub","#B8C8B0",1.0,"Silvery, aromatic shrubs of dry plains."),
 ("calluna","Heather","Calluna vulgaris","Flowering plant","Neo","","ground",["Hill","Tundra","Plain"],[],"Shrub","#E0B8D8",0.8,"Purple-flowering heath of acid moorland."),
 ("larrea","Creosote bush","Larrea tridentata","Flowering plant","Neo","","ground",["Desert"],[],"Shrub","#B0C090",0.9,"Desert shrub; some clones are over 10,000 years old."),
 ("saguaro","Saguaro","Carnegiea gigantea","Cactus","Neo","","ground",["Desert"],[],"Cactus","#FFFFFF",1.0,"Giant columnar cactus of the Sonoran Desert."),
 ("opuntia","Prickly pear","Opuntia","Cactus","Neo","","ground",["Desert","Steppe","Savanna"],[],"Succulent","#C8E0A0",1.0,"Cactus with flat, padded stems."),
 ("welwitschia","Welwitschia","Welwitschia mirabilis","Gnetophyte","Neo","","ground",["Desert"],[],"Succulent","#A8B888",1.2,"Two strap leaves that grow for over a thousand years, Namib Desert."),
 ("euphorbia","Candelabra spurge","Euphorbia candelabrum","Flowering plant","Neo","","ground",["Desert","Savanna"],[],"Cactus","#C0D8A0",1.1,"African succulent that looks like a cactus."),
 ("dryas","Mountain avens","Dryas octopetala","Flowering plant","Neo","","ground",["Tundra","Hill"],[],"Flower","#FFFFFF",0.8,"Tundra flower that gave its name to the Younger Dryas cold snap."),
 ("salix_arctica","Arctic willow","Salix arctica","Flowering plant","Neo","","ground",["Tundra"],[],"Shrub","#C8D8A0",0.6,"A willow that grows only a few centimetres tall."),
 ("eriophorum","Cottongrass","Eriophorum","Sedge","Neo","","ground",["Tundra","Wetland"],[],"Flower","#FFFFFF",0.9,"Sedge with cotton-white seed heads."),
 ("saxifraga","Purple saxifrage","Saxifraga oppositifolia","Flowering plant","Neo","","ground",["Tundra","Hill"],[],"Flower","#F0C0F0",0.7,"One of the northernmost flowering plants."),
 ("sphagnum","Peat moss","Sphagnum","Moss","Per","","ground",["Wetland","Tundra"],[],"Moss","#D0E080",1.0,"Builds peat bogs that store vast amounts of carbon."),
 ("phragmites","Common reed","Phragmites australis","Grass","Neo","","ground",["Wetland"],[],"Reed","#FFFFFF",1.2,"Tall reed beds of marshes and lakes."),
 ("papyrus","Papyrus","Cyperus papyrus","Sedge","Neo","","ground",["Wetland"],[],"Reed","#C8F0A0",1.4,"Sedge of the Nile, made into the first paper."),
 ("typha","Cattail","Typha","Flowering plant","Pal","","ground",["Wetland"],[],"Reed","#D0D8A0",1.0,"Bulrushes with brown, sausage-shaped flower spikes."),
 ("heliconia","Heliconia","Heliconia","Flowering plant","Neo","","ground",["Rainforest"],[],"Flower","#FFD0A0",1.2,"Lobster-claw flowers pollinated by hummingbirds."),
 ("rainforest_fern","Bird's-nest fern","Asplenium nidus","Fern","Pal","","ground",["Rainforest","Wetland"],[],"GroundFern","#C8F0A0",1.2,"Fern rosettes of the rainforest floor and branches."),
 ("wildflowers","Meadow wildflowers","Asteraceae and kin","Flowering plant","Neo","","ground",["Plain","Hill","Steppe"],[],"Flower","#FFFFFF",1.0,"Daisies, clovers and their kin in the grass."),
 ("aloe","Aloe","Aloe","Flowering plant","Neo","","ground",["Desert","Savanna","Hill"],[],"Succulent","#B8D0A0",1.0,"Succulent rosettes of African dry lands."),
 ("protea","King protea","Protea cynaroides","Flowering plant","Neo","","ground",["Hill","Savanna","Steppe"],[],"Flower","#FFC0D0",1.1,"Fire-adapted fynbos shrub; Proteaceae date back to Gondwana."),
 ("banksia","Banksia","Banksia","Flowering plant","Neo","","ground",["Savanna","Hill","Steppe"],[],"Shrub","#C0D0A0",1.0,"Australian shrub with bottlebrush flower spikes."),
 ("ilex","Holly","Ilex","Flowering plant","Pal","","ground",["Plain","Hill"],[],"Shrub","#90C090",0.9,"Evergreen shrub of forest edges."),
 ("rhododendron","Rhododendron","Rhododendron","Flowering plant","Pal","","ground",["Hill","Plain"],[],"Shrub","#E8C0E0",1.0,"Flowering shrubs of mountain slopes."),
 # ---- Under the water: seabed and lakebed (layer "under", terrains = UnderKind) ----
 ("green_algae","Green algae","Chlorophyta","Green alga","Cam","","under",["Seabed"],[],"Algae","#90D060",1.0,"Turf of green seaweed on sunlit seabed; land plants descend from green algae."),
 ("red_algae","Red algae","Rhodophyta","Red alga","Cam","","under",["Seabed"],[],"Algae","#E07070",1.0,"Red seaweeds, among the oldest complex algae."),
 ("stromatolites","Stromatolites","Cyanobacterial mats","Cyanobacteria","Cam","","under",["Seabed","Lakebed"],[],"Stromatolite","#FFFFFF",1.0,"Layered mounds built by cyanobacteria; rare today, as at Shark Bay."),
 ("epiphyton","Epiphyton","Epiphyton","Calcimicrobe","Cam","Dev","under",["Seabed"],[],"Coralline","#C8B090",0.9,"Bushy calcified microbes that built Cambrian reefs with archaeocyathids."),
 ("dasyclads","Dasyclad algae","Dasycladales","Green alga","Cam","","under",["Seabed"],[],"Algae","#A8D880",0.8,"Little umbrella-shaped green algae of warm lagoons."),
 ("receptaculites","Receptaculites","Receptaculites oweni","Calcareous alga","Ord","Per","under",["Seabed"],[],"Coralline","#D8C8A0",1.1,"The 'sunflower coral': a disc-shaped calcareous alga."),
 ("solenopora","Solenopora","Solenopora","Red alga","Ord","Cre","under",["Seabed"],[],"Coralline","#D89898",1.0,"Calcified red alga that helped build Paleozoic reefs."),
 ("codiaceans","Codiacean algae","Codiaceae","Green alga","Ord","","under",["Seabed"],[],"Algae","#88C870",1.0,"Calcified green algae whose fragments make carbonate sand."),
 ("phylloid_algae","Phylloid algae","Ivanovia","Green alga","Car","Per","under",["Seabed"],[],"Algae","#C8D890",1.2,"Potato-chip-shaped algae that formed Late Paleozoic mounds."),
 ("halimeda","Halimeda","Halimeda","Green alga","Tri","","under",["Seabed"],[],"Algae","#A8D888",1.1,"Segmented green alga; its plates pile up into sand banks."),
 ("caulerpa","Caulerpa","Caulerpa","Green alga","Jur","","under",["Seabed"],[],"Seagrass","#80D070",0.8,"A creeping seaweed that is a single giant cell."),
 ("coralline_algae","Coralline algae","Lithothamnion","Red alga","Cre","","under",["Seabed"],[],"Coralline","#E8A8B8",1.0,"Pink, rock-hard crusts that cement coral reefs together."),
 ("thalassocharis","Early seagrass","Thalassocharis","Seagrass","Cre","Cre","under",["Seabed"],[],"Seagrass","#90C070",0.9,"One of the first flowering plants to return to the sea."),
 ("posidonia","Neptune grass","Posidonia oceanica","Seagrass","Pal","","under",["Seabed"],[],"Seagrass","#70B060",1.2,"Mediterranean seagrass; some meadows are thousands of years old."),
 ("zostera","Eelgrass","Zostera marina","Seagrass","Pal","","under",["Seabed"],[],"Seagrass","#80C068",1.1,"Seagrass meadows of cool coasts, nurseries for fish."),
 ("thalassia","Turtle grass","Thalassia testudinum","Seagrass","Pal","","under",["Seabed"],[],"Seagrass","#78C060",1.0,"Tropical seagrass grazed by turtles and manatees."),
 ("halophila","Paddle weed","Halophila ovalis","Seagrass","Neo","","under",["Seabed"],[],"Seagrass","#90D070",0.7,"Small seagrass, food of dugongs."),
 ("sargassum","Sargassum","Sargassum","Brown alga","Pal","","under",["Seabed"],[],"Kelp","#C8A858",0.6,"Brown seaweed with air bladders; rafts of it float in the Sargasso Sea."),
 ("giant_kelp","Giant kelp","Macrocystis pyrifera","Brown alga","Neo","","under",["Seabed"],[],"Kelp","#B09040",1.4,"Kelp forests up to 50 m tall along cool coasts."),
 ("laminaria","Oarweed","Laminaria digitata","Brown alga","Neo","","under",["Seabed"],[],"Kelp","#A08838",0.9,"Kelp with broad, strap-like blades."),
 ("bladderwrack","Bladderwrack","Fucus vesiculosus","Brown alga","Neo","","under",["Seabed"],[],"Algae","#A89048",1.0,"Rockweed of the tidal shore, buoyed by air bladders."),
 ("spirogyra","Filamentous algae","Spirogyra","Green alga","Cam","","under",["Lakebed"],[],"Algae","#A8E078",1.0,"Slimy green threads in still fresh water."),
 ("chara","Stonewort","Chara","Charophyte","Sil","","under",["Lakebed"],[],"Charophyte","#A0C870",1.0,"Whorled charophytes, the closest algal relatives of land plants."),
 ("palaeonitella","Palaeonitella","Palaeonitella cranii","Charophyte","Dev","Dev","under",["Lakebed"],[],"Charophyte","#B0D080",0.8,"A stonewort from the Rhynie chert hot springs."),
 ("nitella","Nitella","Nitella","Charophyte","Car","","under",["Lakebed"],[],"Charophyte","#B8D888",0.9,"Delicate, translucent stonewort."),
 ("isoetes","Quillwort","Isoetes","Lycopsid","Tri","","under",["Lakebed"],[],"Seagrass","#90C070",0.9,"Underwater clubmoss, the last relative of the giant scale trees."),
 ("potamogeton","Pondweed","Potamogeton","Flowering plant","Cre","","under",["Lakebed"],[],"Kelp","#90C060",0.5,"Rooted water plant with floating leaves."),
 ("vallisneria","Tape grass","Vallisneria","Flowering plant","Neo","","under",["Lakebed"],[],"Seagrass","#88C870",1.1,"Ribbon-leaved underwater meadows of rivers and lakes."),
 ("elodea","Waterweed","Elodea","Flowering plant","Neo","","under",["Lakebed"],[],"Charophyte","#80C060",0.9,"Bushy waterweed of ponds."),
]
species_terrains = {"Plain","Hill","Mountain","Desert","Wetland","Tundra","IceSheet","Savanna","Rainforest","Steppe",
                    "Barren","MicrobialMat","Mossland","FernPrairie","CoalSwamp"}
errs, ids = [], set()
for p in P:
    pid, name, sci, group, f, l, layer, terr, forests, form, tint, size, note = p
    if pid in ids: errs.append(f"duplicate {pid}")
    ids.add(pid)
    if f not in AB or (l and l not in AB): errs.append(f"{pid}: bad age")
    elif l and AGES.index(AB[l]) < AGES.index(AB[f]): errs.append(f"{pid}: ends before it starts")
    if layer not in ("canopy","ground","under"): errs.append(f"{pid}: layer")
    if layer == "under" and (form not in UNDER_FORMS or any(t not in UNDER_TERRAINS for t in terr)): errs.append(f"{pid}: under form/terrain")
    if layer == "canopy" and (form not in CANOPY_FORMS or not forests): errs.append(f"{pid}: canopy form/forests")
    if layer == "ground" and form not in GROUND_FORMS: errs.append(f"{pid}: ground form {form}")
    for t in terr:
        if t not in species_terrains and layer != "under": errs.append(f"{pid}: terrain {t}")
if errs: sys.exit("\n".join(errs))

# Coverage: which terrains each period shows (EraFlora.TerrainFor), and whether plants grow there
def era_terrains(age):
    i = AGES.index(age)
    t = {"Desert","Mountain"}
    plain = "Barren" if i <= 2 else "Mossland" if i == 3 else "FernPrairie" if i <= 8 else "Plain"
    t |= {plain}
    if i == 0: t |= {"MicrobialMat","Barren"}
    if i in (1,2): t |= {"Mossland","Barren"}
    if i == 3: t |= {"Mossland","Wetland","Barren"}
    if i == 4: t |= {"CoalSwamp","FernPrairie","Hill","IceSheet"}
    if 5 <= i <= 8: t |= {"FernPrairie","Wetland","Rainforest","Hill"}
    if i >= 9: t |= {"Plain","Hill","Wetland","Rainforest","Tundra"}
    if i >= 10: t |= {"Savanna","Steppe","IceSheet"}
    return t - {"Mountain","IceSheet"}
def alive(p, age):
    i = AGES.index(age)
    return AGES.index(AB[p[4]]) <= i and (not p[5] or i <= AGES.index(AB[p[5]]))
gaps = []
for age in AGES:
    for t in sorted(era_terrains(age)):
        g = [p[0] for p in P if p[6] == "ground" and alive(p, age) and t in p[7]]
        c = [p[0] for p in P if p[6] == "canopy" and alive(p, age) and t in p[7]]
        if not g and AGES.index(age) >= 1 and t not in ("Barren","MicrobialMat","Desert"): gaps.append(f"{age} {t}: no ground plants")
        if not c and AGES.index(age) >= 3 and t not in ("Barren","MicrobialMat","Desert","Mossland" if age != "Devonian" else "-"):
            gaps.append(f"{age} {t}: no forest trees")
for age in AGES:
    for t in ("Seabed","Lakebed"):
        if not [p for p in P if p[6] == "under" and alive(p, age) and t in p[7]]: gaps.append(f"{age} {t}: no water plants")
out = {"notes": "Plant species shown on the map (see World/PlantCatalog). layer: canopy = trees of forest tiles, ground = open ground and understory, under = seabed / lakebed plants and algae on the layer below the map (terrains are UnderKind names). terrains: TerrainKind names as shown in the plant's period. forests: forest types a canopy plant forms (Broadleaf, Conifer, Jungle). form: mesh shape; tint multiplies its leaf colours; size scales it. Generated by tools/flora/plants.py.",
       "plants": [{"id": p[0], "commonName": p[1], "scientificName": p[2], "group": p[3], "firstAge": AB[p[4]], "lastAge": AB[p[5]] if p[5] else "",
                   "layer": p[6], "terrains": p[7], "forests": p[8], "form": p[9], "tint": p[10], "size": p[11], "description": p[12]} for p in P]}
json.dump(out, open(os.path.join(DATA, "plants.json"), "w"), indent=1)
print(f"ok {len(P)} plants ({sum(p[6]=='canopy' for p in P)} canopy, {sum(p[6]=='ground' for p in P)} ground)")
print("gaps:", "\n  ".join([""] + gaps) if gaps else "none")
