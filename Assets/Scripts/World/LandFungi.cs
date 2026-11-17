using System.Collections.Generic;
using UnityEngine;

namespace NaturalHistory.World
{
    // A few land tiles also carry fungi among their plants (HexGrid.PlaceFeatures, PlantPlanner.Fungus):
    // a couple of clumps of one of the period's soil fungi (mushrooms, brackets, puffballs, lichens…),
    // or one or two giant Prototaxites trunks in the Silurian and Devonian. Shapes from UnderFlora.cs.
    public static partial class MapFeatureMeshes
    {
        static void AddLandFungi(Builder b, System.Random rng, float size, PlantDefinition fungus, List<Vector2> taken)
        {
            if (fungus == null) return;
            bool giant = fungus.form == "Prototaxites";
            float apothem = 0.8660254f * size;
            foreach (var p in HexScatter(rng, giant ? rng.Next(1, 3) : rng.Next(2, 4), apothem * 0.85f, (giant ? 0.3f : 0.12f) * size, taken))
            {
                float m = fungus.size * Mathf.Lerp(1f, AgeSize, 0.5f) * Range(rng, 0.85f, 1.15f) * (giant ? 1f : FungusScale);
                leafTint = fungus.Tint;
                int from = b.VertexCount;
                AddUnderFlora(b, rng, new Vector3(p.x, 0f, p.y), size, fungus, m);
                b.SinkBase(from, 0.005f * size, 0.04f * size);
                taken.Add(p);
            }
            leafTint = Color.white;
        }
    }
}
