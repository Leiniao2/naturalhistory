using NaturalHistory.Climate;
using NaturalHistory.Core;
using NaturalHistory.Data;
using UnityEngine;

namespace NaturalHistory.World
{
    // Shares of the map's land, for the world panel
    public struct WorldShares
    {
        public float Land;        // of all tiles
        public float Desert, Vegetated, Forest, Tundra, Ice; // of the land
        public int Volcanoes;
    }

    // The map follows the climate of the date it shows (EarthHistory): sea level moves the shore,
    // temperature the tundra and ice, aridity the deserts, the period and wetness the forests,
    // volcanism the number of volcanoes. Re-dressed at each new period, and within a period whenever
    // the climate has moved enough to show (a glacial, a hothouse spike).
    public partial class HexGrid
    {
        public WorldGenerator.Conditions DisplayedConditions { get; private set; } = WorldGenerator.Conditions.Today;
        public WorldShares Shares { get; private set; }
        public float DisplayedMillionYearsAgo { get; private set; }

        // The date shown: AgeManager's once a game is running, else the start of the period
        private float DateFor(GeologicalAge age)
        {
            var ages = AgeManager.Instance;
            if (Application.isPlaying && ages != null && ages.CurrentTurn > 0 && ages.CurrentAge == age) return ages.MillionYearsAgo;
            if (GameDataLoader.Ages == null) GameDataLoader.Initialize();
            return GameDataLoader.GetAge(age.ToString())?.startMillionYearsAgo ?? 0f;
        }

        private WorldGenerator.Conditions ConditionsFor(GeologicalAge age) => EarthHistory.ConditionsAt(DateFor(age), age);

        // Reclassifies the tiles for the date; rebuilds tile shapes, rivers and the under layer if
        // the shoreline moved.
        private void ApplyClimate(GeologicalAge age)
        {
            DisplayedMillionYearsAgo = DateFor(age);
            DisplayedConditions = EarthHistory.ConditionsAt(DisplayedMillionYearsAgo, age);
            if (!WorldGenerator.Reshape(cells, DisplayedConditions)) return;
            GenerateRivers(WorldSeed);
            GenerateUnder(WorldSeed);
            UpdateCellMeshes();
        }

        // Re-dress for a new period, or the same one when its climate has moved enough
        private void OnTimeChanged()
        {
            if (cells == null || AgeManager.Instance == null) return;
            var age = AgeManager.Instance.CurrentAge;
            if (age == DisplayedAge && !EarthHistory.Differs(DisplayedConditions, ConditionsFor(age))) return;
            DressForAge(age);
            Debug.Log($"[HexGrid] Map now shows the {age} at {DisplayedMillionYearsAgo:0.#} Ma");
            TerrainChanged?.Invoke();
        }

        private void CountShares()
        {
            int all = 0, land = 0, desert = 0, vegetated = 0, forest = 0, tundra = 0, ice = 0, volcanoes = 0;
            foreach (var c in cells)
            {
                if (c?.Terrain == null) continue;
                all++;
                if (c.Feature == TerrainFeature.Volcano) volcanoes++;
                if (c.IsWater) continue;
                land++;
                var k = c.Terrain.kind;
                if (k == TerrainKind.Desert) desert++;
                // tundra and ice by climate (Biome): before tundra plants existed it is drawn as fern prairie
                if (c.Biome == TerrainKind.Tundra) tundra++;
                if (c.Biome == TerrainKind.IceSheet || k == TerrainKind.IceSheet) ice++;
                if (c.IsForest || c.Feature == TerrainFeature.Jungle) forest++;
                if (c.Plants.Count > 0 || c.IsForest || c.Feature == TerrainFeature.Jungle) vegetated++;
            }
            float L = Mathf.Max(1, land);
            Shares = new WorldShares
            {
                Land = land / (float)Mathf.Max(1, all),
                Desert = desert / L, Vegetated = vegetated / L, Forest = forest / L, Tundra = tundra / L, Ice = ice / L,
                Volcanoes = volcanoes,
            };
        }
    }
}
