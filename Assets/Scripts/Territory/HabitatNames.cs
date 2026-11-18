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

        private enum Realm { Land, Sea, Lake }

        // Best match for `area` (the center hex first, then its neighbours) among the faction's names
        // not in `taken`; `fallback` if none fits. A name has to make sense where the center is:
        //  - it suits the center hex's realm: at sea it is a sea, reef or coast; on a lake a lake or
        //    wetland; on land a land name (never a pure sea, nor a lake without one in the area)
        //  - best, every one of its tags is found in the area; else at least half of them, but no
        //    water it names (ocean, reef, lake, coast) may be missing
        // Within the better of the two, the score per name is the matching hexes summed over its
        // tags, divided by the number of tags; ties go to the name listed first (the better-known one).
        public static string Pick(string factionId, IReadOnlyList<HexCell> area, ISet<string> taken, string fallback)
        {
            EnsureLoaded();
            if (factionId == null || !byFaction.TryGetValue(factionId, out var names) || area.Count == 0) return fallback;

            var sea = new Dictionary<HexCell, bool>();
            var counts = new Dictionary<string, int>();
            foreach (var cell in area)
            foreach (var tag in TagsOf(cell, area, sea))
                counts[tag] = counts.TryGetValue(tag, out int c) ? c + 1 : 1;
            var realm = RealmOf(area[0], sea);

            string best = null;
            int bestTier = 0;
            float bestScore = -1f;
            foreach (var entry in names)
            {
                if (string.IsNullOrEmpty(entry.name) || taken.Contains(entry.name) || entry.tags == null || entry.tags.Count == 0) continue;
                if (!Suits(entry.tags, realm, counts)) continue;
                int present = entry.tags.Count(counts.ContainsKey);
                int tier = present == entry.tags.Count ? 2
                         : present * 2 >= entry.tags.Count && !entry.tags.Any(t => WaterTags.Contains(t) && !counts.ContainsKey(t)) ? 1 : 0;
                if (tier == 0) continue;
                float score = entry.tags.Sum(t => counts.TryGetValue(t, out int c) ? c : 0) / (float)entry.tags.Count;
                if (tier > bestTier || (tier == bestTier && score > bestScore)) { bestTier = tier; bestScore = score; best = entry.name; }
            }
            return best ?? fallback;
        }

        private static readonly HashSet<string> WaterTags = new() { "ocean", "reef", "lake", "coast" };

        private static bool Suits(List<string> tags, Realm realm, Dictionary<string, int> counts) => realm switch
        {
            Realm.Sea  => tags.Any(t => t is "ocean" or "reef" or "coast"),
            Realm.Lake => tags.Any(t => t is "lake" or "wetland"),
            _          => tags.Any(t => !WaterTags.Contains(t)) && (!tags.Contains("lake") || counts.ContainsKey("lake")),
        };

        private static Realm RealmOf(HexCell cell, Dictionary<HexCell, bool> sea) =>
            cell == null || !cell.IsWater ? Realm.Land : IsSea(cell, sea) ? Realm.Sea : Realm.Lake;

        // Salt water, or shallow ("fresh") water joined to it: the map's FreshWater band is mostly the
        // shallow fringe of the sea, and only a body of it that never touches salt water is a lake
        private static bool IsSea(HexCell cell, Dictionary<HexCell, bool> cache)
        {
            if (cell.Terrain.kind == TerrainKind.SaltWater) return true;
            if (cache.TryGetValue(cell, out bool known)) return known;
            var grid = HexGrid.Instance;
            var body = new List<HexCell> { cell };
            var seen = new HashSet<HexCell> { cell };
            bool salt = false;
            for (int i = 0; i < body.Count && !salt && grid != null; i++)
                foreach (var n in grid.GetNeighbors(body[i]))
                {
                    if (n?.Terrain == null || !seen.Add(n)) continue;
                    if (n.Terrain.kind == TerrainKind.SaltWater) { salt = true; break; }
                    if (n.Terrain.kind == TerrainKind.FreshWater) body.Add(n);
                }
            foreach (var c in body) cache[c] = salt;
            return salt;
        }

        // Environment tags of one hex. On land both the period's ground cover (Terrain) and the
        // present-day biome its climate makes (Biome) count, so a Cretaceous fern prairie still reads
        // as grassland; water is only what it is (a sea, with a coast if the area has land, or a lake).
        private static HashSet<string> TagsOf(HexCell cell, IReadOnlyList<HexCell> area, Dictionary<HexCell, bool> sea)
        {
            var tags = new HashSet<string>();
            if (cell == null || cell.Terrain == null) return tags;
            if (cell.IsWater)
            {
                if (IsSea(cell, sea))
                {
                    tags.Add("ocean");
                    if (area.Any(c => c != null && c.Terrain != null && !c.IsWater)) tags.Add("coast");
                }
                else tags.Add("lake");
            }
            else
            {
                AddKind(tags, cell.Terrain.kind);
                if (cell.Biome is not (TerrainKind.SaltWater or TerrainKind.FreshWater)) AddKind(tags, cell.Biome);
                if (area.Any(c => c != null && c.Terrain != null && c.IsWater && IsSea(c, sea))) tags.Add("coast");
            }

            switch (cell.Feature)
            {
                case TerrainFeature.BroadleafForest:
                case TerrainFeature.ConiferForest: if (!cell.IsWater) tags.Add("forest"); break;
                case TerrainFeature.Jungle:        if (!cell.IsWater) tags.Add("rainforest"); break;
                case TerrainFeature.Reef:          if (cell.IsWater) tags.Add("reef"); break;
                case TerrainFeature.Oasis:         tags.Add("desert"); tags.Add("lake"); break;
                case TerrainFeature.Geothermal:    tags.Add("volcano"); break;
                case TerrainFeature.Mesa:
                case TerrainFeature.Canyon:
                case TerrainFeature.Danxia:        if (!cell.IsWater) tags.Add("mountain"); break;
                case TerrainFeature.Karst:         tags.Add(cell.IsWater ? "coast" : "mountain"); break;
                case TerrainFeature.WhiteCliffs:   tags.Add("coast"); break;
                case TerrainFeature.Volcano:       tags.Add("volcano"); if (!cell.IsWater) tags.Add("mountain"); break;
            }
            return tags;
        }

        private static void AddKind(HashSet<string> tags, TerrainKind kind)
        {
            switch (kind)
            {
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
