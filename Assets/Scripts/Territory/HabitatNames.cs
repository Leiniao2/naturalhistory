using System;
using System.Collections.Generic;
using System.Linq;
using NaturalHistory.World;
using UnityEngine;

namespace NaturalHistory.Territory
{
    [Serializable]
    public class HabitatNameEntry
    {
        public string name;
        public List<string> tags; // coast, ocean, reef, lake, wetland, desert, grassland, savanna,
                                  // forest, rainforest, mountain, hill, tundra, ice, volcano
    }

    [Serializable]
    public class FactionHabitatNames
    {
        public string faction; // factions.json id
        public List<HabitatNameEntry> names;
    }

    [Serializable]
    public class HabitatNamesFile
    {
        public List<FactionHabitatNames> factions;
    }

    // Names habitat centers after real parks and landmarks of the player's faction
    // (Resources/Data/habitat_names.json), choosing the one whose tags best match the center's hexes.
    public static class HabitatNames
    {
        private static Dictionary<string, List<HabitatNameEntry>> byFaction;

        private static void EnsureLoaded()
        {
            if (byFaction != null) return;
            byFaction = new Dictionary<string, List<HabitatNameEntry>>();
            var asset = Resources.Load<TextAsset>("Data/habitat_names");
            if (asset == null) { Debug.LogWarning("[HabitatNames] Resources/Data/habitat_names.json not found."); return; }
            var file = JsonUtility.FromJson<HabitatNamesFile>(asset.text);
            if (file?.factions == null) return;
            foreach (var f in file.factions)
                if (!string.IsNullOrEmpty(f.faction) && f.names != null)
                    byFaction[f.faction] = f.names;
        }

        // Best match for `area` among the faction's names not in `taken`; `fallback` if none are left.
        // Score per name: matching hexes summed over its tags, divided by the number of tags, so a
        // one-tag name that fits every hex beats a four-tag name that fits a few. Ties go to the
        // name listed first (the better-known one).
        public static string Pick(string factionId, IReadOnlyCollection<HexCell> area, ISet<string> taken, string fallback)
        {
            EnsureLoaded();
            if (factionId == null || !byFaction.TryGetValue(factionId, out var names)) return fallback;

            var counts = new Dictionary<string, int>();
            foreach (var cell in area)
            foreach (var tag in TagsOf(cell, area))
                counts[tag] = counts.TryGetValue(tag, out int c) ? c + 1 : 1;

            string best = null;
            float bestScore = -1f;
            foreach (var entry in names)
            {
                if (string.IsNullOrEmpty(entry.name) || taken.Contains(entry.name)) continue;
                int tagCount = entry.tags?.Count ?? 0;
                float score = tagCount == 0 ? 0f
                    : entry.tags.Sum(t => counts.TryGetValue(t, out int c) ? c : 0) / (float)tagCount;
                if (score > bestScore) { bestScore = score; best = entry.name; }
            }
            return best ?? fallback;
        }

        // Environment tags of one hex. Both the period's ground cover (Terrain) and the present-day
        // biome its climate makes (Biome) count, so a Cretaceous fern prairie still reads as grassland.
        public static HashSet<string> TagsOf(HexCell cell, IReadOnlyCollection<HexCell> area)
        {
            var tags = new HashSet<string>();
            if (cell == null || cell.Terrain == null) return tags;
            AddKind(tags, cell.Terrain.kind);
            AddKind(tags, cell.Biome);
            if (cell.Terrain.kind == TerrainKind.SaltWater)
                tags.Add(area.Any(c => c != null && !c.IsWater) ? "coast" : "ocean");

            switch (cell.Feature)
            {
                case TerrainFeature.BroadleafForest:
                case TerrainFeature.ConiferForest: tags.Add("forest"); break;
                case TerrainFeature.Jungle:        tags.Add("rainforest"); break;
                case TerrainFeature.Reef:          tags.Add("reef"); break;
                case TerrainFeature.Oasis:         tags.Add("desert"); tags.Add("lake"); break;
                case TerrainFeature.Geothermal:    tags.Add("volcano"); break;
                case TerrainFeature.Mesa:
                case TerrainFeature.Canyon:
                case TerrainFeature.Danxia:        tags.Add("mountain"); break;
                case TerrainFeature.Karst:         tags.Add(cell.IsWater ? "coast" : "mountain"); break;
                case TerrainFeature.WhiteCliffs:   tags.Add("coast"); break;
                case TerrainFeature.Volcano:       tags.Add("volcano"); tags.Add("mountain"); break;
            }
            return tags;
        }

        private static void AddKind(HashSet<string> tags, TerrainKind kind)
        {
            switch (kind)
            {
                case TerrainKind.SaltWater:    tags.Add("ocean"); break;
                case TerrainKind.FreshWater:   tags.Add("lake"); break;
                case TerrainKind.Plain:
                case TerrainKind.Steppe:
                case TerrainKind.FernPrairie:  tags.Add("grassland"); break;
                case TerrainKind.Savanna:      tags.Add("savanna"); break;
                case TerrainKind.Hill:         tags.Add("hill"); break;
                case TerrainKind.Mountain:     tags.Add("mountain"); break;
                case TerrainKind.Desert:
                case TerrainKind.Barren:       tags.Add("desert"); break;
                case TerrainKind.Wetland:
                case TerrainKind.MicrobialMat: tags.Add("wetland"); break;
                case TerrainKind.CoalSwamp:    tags.Add("wetland"); tags.Add("forest"); break;
                case TerrainKind.Tundra:
                case TerrainKind.Mossland:     tags.Add("tundra"); break;
                case TerrainKind.IceSheet:     tags.Add("ice"); break;
                case TerrainKind.Rainforest:   tags.Add("rainforest"); break;
            }
        }
    }
}
