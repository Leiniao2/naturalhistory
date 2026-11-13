using System.Collections.Generic;
using System.Linq;
using NaturalHistory.Biology;
using NaturalHistory.Core;
using UnityEngine;

namespace NaturalHistory.Data
{
    // Loads all JSON data files from Resources/Data/ and provides typed lookups.
    // Call GameDataLoader.Initialize() once at startup (from GameManager).
    public static class GameDataLoader
    {
        public static IReadOnlyList<RealmDefinition> Realms { get; private set; }
        public static IReadOnlyList<AgeDefinition> Ages { get; private set; }
        public static IReadOnlyList<GeneDefinition> Genes { get; private set; }
        public static IReadOnlyList<SpeciesDefinition> Species { get; private set; }
        public static IReadOnlyList<ClimateKeyframe> ClimateHistory { get; private set; } // sorted oldest → newest
        public static IReadOnlyList<FactionDefinition> Factions { get; private set; }

        private static readonly Dictionary<string, RealmDefinition> realmById = new();
        private static readonly Dictionary<string, AgeDefinition> ageById = new();
        private static readonly Dictionary<string, GeneDefinition> geneById = new();
        private static readonly Dictionary<string, SpeciesDefinition> speciesById = new();
        private static readonly Dictionary<string, FactionDefinition> factionById = new();

        public static void Initialize()
        {
            LoadRealms();
            LoadAges();
            LoadGenes();
            LoadClimateHistory();
            LoadSpecies();
            LoadFactions();
            Debug.Log($"[GameDataLoader] Loaded {Realms.Count} realms, {Ages.Count} ages, {Genes.Count} genes, {Species.Count} species, {Factions.Count} factions.");
        }

        // --- Loaders ---

        private static void LoadRealms()
        {
            var asset = Resources.Load<TextAsset>("Data/realms");
            var collection = JsonUtility.FromJson<RealmCollection>(asset.text);
            Realms = collection.realms;
            realmById.Clear();
            foreach (var r in Realms) realmById[r.id] = r;
        }

        private static void LoadAges()
        {
            var asset = Resources.Load<TextAsset>("Data/ages");
            var collection = JsonUtility.FromJson<AgeCollection>(asset.text);
            Ages = collection.ages;
            ageById.Clear();
            foreach (var a in Ages) ageById[a.id] = a;
        }

        private static void LoadGenes()
        {
            var asset = Resources.Load<TextAsset>("Data/genes");
            var collection = JsonUtility.FromJson<GeneCollection>(asset.text);
            Genes = collection.genes;
            geneById.Clear();
            foreach (var g in Genes) geneById[g.id] = g;
        }

        private static void LoadClimateHistory()
        {
            var asset = Resources.Load<TextAsset>("Data/climate_history");
            var collection = JsonUtility.FromJson<ClimateHistoryCollection>(asset.text);
            ClimateHistory = collection.keyframes.OrderByDescending(k => k.ma).ToList();
        }

        private static void LoadSpecies()
        {
            var asset = Resources.Load<TextAsset>("Data/species");
            var collection = asset != null ? JsonUtility.FromJson<SpeciesCollection>(asset.text) : null;
            Species = collection?.species ?? new List<SpeciesDefinition>();
            speciesById.Clear();
            foreach (var s in Species) speciesById[s.id] = s;
        }

        private static void LoadFactions()
        {
            var asset = Resources.Load<TextAsset>("Data/factions");
            var collection = asset != null ? JsonUtility.FromJson<FactionCollection>(asset.text) : null;
            Factions = collection?.factions ?? new List<FactionDefinition>();
            factionById.Clear();
            foreach (var f in Factions)
            {
                f.iconicAnimals ??= new List<IconicAnimalDefinition>();
                factionById[f.id] = f;
            }
        }

        // --- Lookups ---

        public static RealmDefinition GetRealm(string id)
            => realmById.TryGetValue(id, out var r) ? r : null;

        public static AgeDefinition GetAge(string id)
            => ageById.TryGetValue(id, out var a) ? a : null;

        public static GeneDefinition GetGene(string id)
            => geneById.TryGetValue(id, out var g) ? g : null;

        public static SpeciesDefinition GetSpecies(string id)
            => speciesById.TryGetValue(id, out var s) ? s : null;

        public static FactionDefinition GetFaction(string id)
            => id != null && factionById.TryGetValue(id, out var f) ? f : null;

        public static List<RealmDefinition> GetRealmsByType(string type)
            => Realms.Where(r => r.type == type).ToList();

        public static List<GeneDefinition> GetGenesByCategory(string category)
            => Genes.Where(g => g.category == category).ToList();

        public static List<GeneDefinition> GetGenesUnlockedByAge(string ageId)
        {
            // Return genes unlocked at or before the given age
            var ageIndex = Ages.ToList().FindIndex(a => a.id == ageId);
            return Genes
                .Where(g =>
                {
                    var geneAgeIndex = Ages.ToList().FindIndex(a => a.id == g.unlockAge);
                    return geneAgeIndex <= ageIndex;
                })
                .ToList();
        }

        // --- Factory helpers ---

        // Build a GeneMap for a new species, populated with genes available for the current age
        public static GeneMap BuildStartingGeneMap(string currentAgeId)
        {
            var map = new GeneMap();
            foreach (var def in GetGenesUnlockedByAge(currentAgeId))
            {
                map.AddGene(new Biology.Gene
                {
                    id = def.id,
                    displayName = def.displayName,
                    category = System.Enum.TryParse<GeneCategory>(def.category, out var cat) ? cat : GeneCategory.Locomotion,
                    expressionLevel = def.defaultExpression,
                    description = def.description
                });
            }
            return map;
        }

        // Build a BioRealm from its definition
        public static BioRealm BuildRealm(string realmId)
        {
            var def = GetRealm(realmId);
            if (def == null)
            {
                Debug.LogError($"[GameDataLoader] Unknown realm id: {realmId}");
                return null;
            }

            return new BioRealm
            {
                Id = def.id,
                DisplayName = def.displayName,
                Type = def.type == "Marine" ? RealmType.Marine : RealmType.Land,
                RealmColor = ColorUtility.TryParseHtmlString(def.color, out var c) ? c : Color.white
            };
        }
    }
}
