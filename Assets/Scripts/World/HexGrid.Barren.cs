using System.Collections.Generic;
using NaturalHistory.Core;
using UnityEngine;

namespace NaturalHistory.World
{
    // Not every tile is green. In broad regions a few tiles across (a smooth noise field, so they
    // come in patches rather than as single holes) plant cover thins out:
    //  - sea deserts: open sea floor with nothing growing (bare sand) or one sparse species and no
    //    painted mats or meadows; more of the deep sea floor than of the shelf
    //  - on land, deserts are mostly bare sand and rock, the rest a few plants of a single species;
    //    some steppe and tundra is just as thin
    // Only once the beds and land plants have filled in (the Devonian on); before that the floors
    // and land are bare enough already.
    public partial class HexGrid
    {
        public enum PlantCover { Full, Sparse, Bare }

        private readonly HashSet<HexCell> sparseBeds = new();

        private float BarrenNoise(HexCell cell, float salt)
        {
            var pos = cell.Coordinates.ToWorldPosition(cellSize);
            var p = OnMapLoop(new Vector2(pos.x, pos.z)) * (0.2f / cellSize) + new Vector3(311f, 59f, 877f) * salt + Vector3.one * (WorldSeed % 983);
            return PerlinNoise3D.Sample(p.x, p.y, p.z); // about -1..1, mostly within ±0.4
        }

        // Sea floor (shelf and deep): about one shelf tile in five and two deep-sea tiles in five a sea desert
        private PlantCover SeaCover(HexCell cell, GeologicalAge age)
        {
            if (age < GeologicalAge.Devonian || !cell.IsWater || cell.UnderFeature != UnderFeature.None) return PlantCover.Full;
            float n = BarrenNoise(cell, 1f);
            return cell.Under switch
            {
                UnderKind.Seabed     => n > 0.3f ? PlantCover.Bare : n > 0.15f ? PlantCover.Sparse : PlantCover.Full,
                UnderKind.DeepSeabed => n > 0.08f ? PlantCover.Bare : n > -0.08f ? PlantCover.Sparse : PlantCover.Full,
                _                    => PlantCover.Full,
            };
        }

        // Land ground plants: deserts about half bare, the rest sparse; a fifth of steppe and tundra sparse
        private PlantCover LandCover(HexCell cell, GeologicalAge age)
        {
            if (age < GeologicalAge.Devonian) return PlantCover.Full;
            float n = BarrenNoise(cell, 2f);
            return cell.Terrain.kind switch
            {
                TerrainKind.Desert                       => n > -0.02f ? PlantCover.Bare : PlantCover.Sparse,
                TerrainKind.Steppe or TerrainKind.Tundra => n > 0.18f ? PlantCover.Sparse : PlantCover.Full,
                _                                        => PlantCover.Full,
            };
        }

        // After the beds are chosen (DressUnder): sea deserts lose their plants, or keep only the main one
        private void ThinSeaDeserts(GeologicalAge age)
        {
            sparseBeds.Clear();
            foreach (var cell in cells)
            {
                if (cell?.Terrain == null) continue;
                switch (SeaCover(cell, age))
                {
                    case PlantCover.Bare:
                        cell.SetUnderPlants();
                        sparseBeds.Add(cell);
                        break;
                    case PlantCover.Sparse:
                        cell.SetUnderPlants(cell.UnderPlants.Count > 0 ? cell.UnderPlants[0] : null);
                        sparseBeds.Add(cell);
                        break;
                }
            }
        }
    }
}
