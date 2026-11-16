using System;
using System.Collections.Generic;
using System.Linq;
using NaturalHistory.Core;
using UnityEngine;

namespace NaturalHistory.World
{
    // Chooses which plant species (plants.json) grow on each tile in one period and builds their
    // meshes. Purely visual.
    //
    // Candidates are the species alive in the period that grow on the tile's terrain (forest tiles:
    // canopy species forming that forest type, plus an understory). Each species has its own smooth
    // noise field over the map; the tile takes the species scoring highest there, so a species
    // dominates a region of several tiles and the mix shifts gradually across a continent.
    // Meshes are cached per species combination, a couple of variants each.
    public class PlantPlanner
    {
        private const int Variants   = 2;
        private const float Patchiness = 0.22f; // noise frequency per cell: regions a few tiles across

        private readonly List<PlantDefinition> alive;
        private readonly float cellSize, wrapWidth;
        private readonly int seed;
        private readonly GeologicalAge age;
        private readonly Func<Mesh, Mesh> track;
        private readonly Dictionary<string, Mesh[]> cache = new();
        private readonly Dictionary<string, Vector3> offsets = new();

        public PlantPlanner(GeologicalAge age, int seed, float cellSize, float wrapWidth, Func<Mesh, Mesh> track)
        {
            alive = PlantCatalog.AliveIn(age);
            this.age = age;
            this.seed = seed;
            this.cellSize = cellSize;
            this.wrapWidth = wrapWidth;
            this.track = track;
        }

        public bool HasPlants => alive.Count > 0;

        // Dominant and second species for a tile. forest: "Broadleaf" / "Conifer" / "Jungle" for the
        // canopy of a forest tile, null for ground plants. Either may be null.
        public (PlantDefinition first, PlantDefinition second) Choose(HexCell cell, string forest)
        {
            if (cell?.Terrain == null || alive.Count == 0) return (null, null);
            string terrain = cell.Terrain.kind.ToString();
            bool canopy = forest != null;
            var candidates = alive.Where(p => p.layer == (canopy ? "canopy" : "ground") && p.terrains.Contains(terrain) && (!canopy || p.forests.Contains(forest))).ToList();
            if (canopy && candidates.Count == 0) // no tree listed for this terrain: any of that forest type, then any tree
                candidates = alive.Where(p => p.IsCanopy && p.forests.Contains(forest)).ToList();
            if (canopy && candidates.Count == 0)
                candidates = alive.Where(p => p.IsCanopy).ToList();
            if (candidates.Count == 0) return (null, null);

            return Rank(cell, candidates);
        }

        // Water plants, algae, fungi and microbial mats of the layer under sea level (plants.json
        // layer "under"), by the tile's UnderKind (terrains: Seabed, Lakebed, DeepSeabed, Cave, Rock).
        public (PlantDefinition first, PlantDefinition second) ChooseUnder(HexCell cell)
        {
            if (cell == null) return (null, null);
            string kind = cell.Under.ToString();
            var candidates = alive.Where(p => p.layer == "under" && p.terrains.Contains(kind)).ToList();
            return candidates.Count == 0 ? (null, null) : Rank(cell, candidates);
        }

        private (PlantDefinition, PlantDefinition) Rank(HexCell cell, List<PlantDefinition> candidates)
        {
            var pos = cell.Coordinates.ToWorldPosition(cellSize);
            var ranked = candidates.OrderByDescending(p => Score(p, pos)).ToList();
            return (ranked[0], ranked.Count > 1 ? ranked[1] : null);
        }

        // density: how thick the bed is on this tile (water beds; 1 = normal), part of the cache key
        public Mesh Under(System.Random rng, UnderKind kind, PlantDefinition main, PlantDefinition second, float density = 1f)
        {
            string k = kind.ToString();
            var extras = main == null ? null : Accents(main, second, alive.Where(p => p.layer == "under" && p.terrains.Contains(k)));
            return Variant(rng, $"u|{kind}|{main?.id}|{second?.id}|{density:0.##}",
                           () => MapFeatureMeshes.CreateUnderDetail(rng, cellSize, kind, main, second, extras, density));
        }

        // A few more species mixed in among a tile's two, so neighbouring tiles of the same region
        // don't look identical: alive on the same ground, preferring shapes the tile doesn't have
        // yet. Picked from the pair itself (not at random) so each combination keeps one mesh cache.
        private List<PlantDefinition> Accents(PlantDefinition main, PlantDefinition second, IEnumerable<PlantDefinition> pool, int count = 2)
        {
            var forms = new HashSet<string> { main.form };
            if (second != null) forms.Add(second.form);
            int pair = StableHash(main.id + "|" + second?.id);
            var result = new List<PlantDefinition>();
            foreach (var p in pool.Where(p => p != main && p != second)
                                  .OrderBy(p => forms.Contains(p.form) ? 1 : 0)
                                  .ThenBy(p => StableHash(p.id) ^ pair))
            {
                if (result.Count == count) break;
                if (forms.Add(p.form) || result.Count == 0) result.Add(p);
            }
            return result;
        }

        private float Score(PlantDefinition p, Vector3 pos)
        {
            if (!offsets.TryGetValue(p.id, out var off))
            {
                var r = new System.Random(seed ^ StableHash(p.id));
                off = new Vector3((float)r.NextDouble(), (float)r.NextDouble(), (float)r.NextDouble()) * 1000f;
                offsets[p.id] = off;
            }
            // Around the map's east–west loop, so regions match up across the wrap seam
            float angle = pos.x / wrapWidth * Mathf.PI * 2f;
            float rad   = wrapWidth / (Mathf.PI * 2f);
            var q = new Vector3(Mathf.Cos(angle) * rad, Mathf.Sin(angle) * rad, pos.z) * (Patchiness / cellSize) + off;
            return PerlinNoise3D.Sample(q.x, q.y, q.z) + 0.15f * PerlinNoise3D.Sample(q.x * 3f, q.y * 3f, q.z * 3f)
                 - p.rarity * RarityPenalty; // rare species (the colourful trees) only win where their noise peaks
        }

        // How far a rarity of 1 pushes a species down the ranking (noise spans about -1..1)
        private const float RarityPenalty = 0.45f;

        // FNV-1a: unlike string.GetHashCode, the same in every run, so a seed always gives the same map
        private static int StableHash(string s)
        {
            unchecked
            {
                uint h = 2166136261;
                foreach (char c in s) h = (h ^ c) * 16777619;
                return (int)h;
            }
        }

        public Mesh Stand(System.Random rng, PlantDefinition canopy, PlantDefinition canopy2, PlantDefinition under) =>
            Variant(rng, $"s|{canopy.id}|{canopy2?.id}|{under?.id}", () => MapFeatureMeshes.CreatePlantStand(rng, cellSize, canopy, canopy2, under));

        public Mesh Ground(System.Random rng, PlantDefinition main, PlantDefinition second, TerrainKind kind)
        {
            string k = kind.ToString();
            var extras = Accents(main, second, alive.Where(p => p.layer == "ground" && p.terrains.Contains(k)));
            return Variant(rng, $"g|{main.id}|{second?.id}|{kind}", () => MapFeatureMeshes.CreatePlantGround(rng, cellSize, main, second, kind, extras));
        }

        private Mesh Variant(System.Random rng, string key, Func<Mesh> create)
        {
            var inner = create;
            create = () =>
            {
                MapFeatureMeshes.SetAgeBoost(age);
                try { return inner(); }
                finally { MapFeatureMeshes.SetAgeBoost(GeologicalAge.Quaternary); }
            };
            if (!cache.TryGetValue(key, out var meshes)) cache[key] = meshes = new Mesh[Variants];
            int i = rng.Next(Variants);
            return meshes[i] ??= track(create());
        }
    }
}
