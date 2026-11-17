using System.Collections.Generic;
using UnityEngine;

namespace NaturalHistory.World
{
    // High mountains: the tallest few mountain tiles of the map (by the peak their massif mesh
    // actually reaches), tagged HexCell.IsHighMountain and named "High mountain" in the tile panel.
    // Only these rise through the sky layer's cloud deck (SkyLayer.Measure); ordinary mountains
    // stay under the clouds. Table mountains (mesas) are never high.
    public partial class HexGrid
    {
        private const float HighMountainShare = 0.15f; // of the mountain tiles

        private void MarkHighMountains()
        {
            var peaks = new Dictionary<HexCell, float>();
            foreach (var go in featureObjects)
            {
                if (go == null || go.transform.parent == null) continue;
                var cell = go.transform.parent.GetComponent<HexCell>();
                if (cell == null || !cell.IsMountain) continue;
                var rend = go.GetComponent<Renderer>();
                if (rend == null) continue;
                float top = rend.bounds.max.y;
                peaks[cell] = peaks.TryGetValue(cell, out var p) ? Mathf.Max(p, top) : top;
            }

            var ranked = new List<HexCell>();
            for (int r = 0; r < height; r++)
            for (int q = 0; q < width; q++)
            {
                var cell = cells[q, r];
                if (cell == null) continue;
                cell.IsHighMountain = false;
                cell.PeakY = peaks.TryGetValue(cell, out var top) ? top : cell.transform.position.y + cell.SurfaceHeight;
                if (cell.IsMountain && cell.Feature != TerrainFeature.Mesa && peaks.ContainsKey(cell)) ranked.Add(cell);
            }
            if (ranked.Count == 0) return;
            ranked.Sort((a, b) => b.PeakY.CompareTo(a.PeakY));
            int high = Mathf.Max(1, Mathf.RoundToInt(ranked.Count * HighMountainShare));
            for (int i = 0; i < high; i++) ranked[i].IsHighMountain = true;
        }
    }
}
