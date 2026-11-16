using System.Collections.Generic;
using NaturalHistory.Core;
using UnityEngine;

namespace NaturalHistory.World
{
    // The layer under sea level, shown instead of the surface while UnderView is on.
    //
    //   - Under land: rock and soil with roots and burrows, or caves (karst regions, ~25% of land).
    //   - Under the sea: sunlit shallow seabed with its water plants, or the dark deep seabed, with
    //     the odd underwater volcano and field of hydrothermal vents. Under lakes: lakebed.
    //   - Now and then it doesn't follow the surface (a drowned valley under the coast, a buried lake,
    //     a sea cave under shallow water), in a few small clusters.
    //
    // In the under view each tile wears its under skin, the surface props (forests, mountains,
    // rivers…) are hidden and the under props appear; only underground-niche animals are shown.
    public partial class HexGrid
    {
        private const float CaveShare = 0.25f;   // of land
        private const float VolcanoShare = 0.03f; // of sea tiles
        private const float VentShare    = 0.02f; // of deep sea tiles

        private readonly List<GameObject> underObjects = new();
        private readonly Dictionary<UnderKind, Material> underMaterials = new();
        private bool underDirty = true;
        private float nextGroupCheck;

        // ---------- Generation ----------

        private void GenerateUnder(int worldSeed)
        {
            var rng = new System.Random(worldSeed ^ 0x0DDBA11);
            Vector3 Offset() => new((float)rng.NextDouble() * 1000f, (float)rng.NextDouble() * 1000f, (float)rng.NextDouble() * 1000f);
            var karstOff = Offset(); var oddOff = Offset(); var volcanoOff = Offset(); var ventOff = Offset();
            float Noise(HexCell c, float freq, Vector3 off)
            {
                var pos = c.Coordinates.ToWorldPosition(cellSize);
                var p = OnMapLoop(new Vector2(pos.x, pos.z)) * (freq / cellSize) + off;
                return PerlinNoise3D.Sample(p.x, p.y, p.z);
            }

            // Caves: the karstiest share of the land (hills and mountains a little more often)
            var land = new List<(HexCell cell, float v)>();
            var sea  = new List<(HexCell cell, float v)>();
            var deep = new List<(HexCell cell, float v)>();
            foreach (var cell in cells)
            {
                if (cell.Terrain == null) continue;
                if (!cell.IsWater) land.Add((cell, Noise(cell, 0.3f, karstOff) + (cell.Elevation >= 5 ? 0.15f : 0f)));
            }
            land.Sort((a, b) => b.v.CompareTo(a.v));
            var caves = new HashSet<HexCell>();
            for (int i = 0; i < land.Count * CaveShare; i++) caves.Add(land[i].cell);

            foreach (var cell in cells)
            {
                if (cell.Terrain == null) continue;
                // Small clusters where the layer below doesn't match the surface: |odd| near 0.5 is rare
                float odd = Noise(cell, 0.9f, oddOff);
                bool coast = false, lake = cell.Terrain.kind == TerrainKind.Wetland;
                foreach (var n in GetNeighbors(cell))
                {
                    if (n.Terrain == null) continue;
                    if (n.IsWater != cell.IsWater) coast = true;
                    if (n.Terrain.kind == TerrainKind.FreshWater) lake = true;
                }

                UnderKind kind;
                if (cell.Terrain.kind == TerrainKind.FreshWater)
                    kind = odd > 0.42f ? UnderKind.Cave : UnderKind.Lakebed;              // a flooded cave system
                else if (cell.IsWater)
                {
                    kind = cell.Depth >= 0.5f ? UnderKind.DeepSeabed : UnderKind.Seabed;
                    if (kind == UnderKind.Seabed && coast && odd > 0.36f)
                        kind = odd > 0.44f ? UnderKind.Rock : UnderKind.Cave;              // sea caves, a buried headland
                }
                else
                {
                    kind = caves.Contains(cell) ? UnderKind.Cave : UnderKind.Rock;
                    if (coast && odd > 0.38f)      kind = UnderKind.Seabed;               // a drowned valley under the coast
                    else if (lake && odd < -0.40f) kind = UnderKind.Lakebed;              // an old lake, buried
                }
                cell.SetUnder(kind, UnderFeature.None);
                if (kind is UnderKind.Seabed or UnderKind.DeepSeabed) sea.Add((cell, Noise(cell, 0.35f, volcanoOff) + (kind == UnderKind.DeepSeabed ? 0.1f : 0f)));
                if (kind == UnderKind.DeepSeabed) deep.Add((cell, Noise(cell, 0.6f, ventOff)));
            }

            sea.Sort((a, b) => b.v.CompareTo(a.v));
            for (int i = 0; i < sea.Count * VolcanoShare; i++) sea[i].cell.SetUnder(sea[i].cell.Under, UnderFeature.Volcano);
            deep.Sort((a, b) => b.v.CompareTo(a.v));
            int vents = 0;
            foreach (var (cell, _) in deep)
            {
                if (vents >= deep.Count * VentShare) break;
                if (cell.UnderFeature != UnderFeature.None) continue;
                cell.SetUnder(cell.Under, UnderFeature.Vents);
                vents++;
            }
            underDirty = true;
        }

        // ---------- Dressing ----------

        // After the surface is dressed for a period: pick the water plants below (named in the tile
        // panel straight away), and rebuild the under props when they are next shown.
        private void DressUnder(GeologicalAge age)
        {
            var plants = new PlantPlanner(age, WorldSeed, cellSize, WrapWidth, Track);
            foreach (var cell in cells)
            {
                if (cell.Terrain == null) continue;
                var (main, second) = plants.ChooseUnder(cell);
                cell.SetUnderPlants(main, second);
            }
            underDirty = true;
            if (UnderView.On) ApplyUnderView();
        }

        private void BuildUnderProps()
        {
            foreach (var go in underObjects) if (go != null) { if (Application.isPlaying) Destroy(go); else DestroyImmediate(go); }
            underObjects.Clear();
            underDirty = false;
            if (featureMaterial == null) featureMaterial = Resources.Load<Material>("Materials/MapFeatures");
            if (featureMaterial == null) return;

            var rng = new System.Random(WorldSeed ^ 0x5EABED);
            var plants = new PlantPlanner(DisplayedAge, WorldSeed, cellSize, WrapWidth, Track);
            foreach (var cell in cells)
            {
                if (cell.Terrain == null) continue;
                Mesh mesh = cell.UnderFeature switch
                {
                    UnderFeature.Volcano => Track(MapFeatureMeshes.CreateVolcano(rng, cellSize, 0.5f + 0.3f * (float)rng.NextDouble())),
                    UnderFeature.Vents   => Track(MapFeatureMeshes.CreateVents(rng, cellSize)),
                    _ => plants.Under(rng, cell.Under,
                                      cell.UnderPlants.Count > 0 ? cell.UnderPlants[0] : null,
                                      cell.UnderPlants.Count > 1 ? cell.UnderPlants[1] : null),
                };
                if (mesh == null) continue;
                var go = new GameObject(mesh.name);
                if (!Application.isPlaying) go.hideFlags = HideFlags.DontSave;
                go.transform.SetParent(cell.transform, false);
                go.transform.localPosition = Vector3.up * cell.SurfaceHeight;
                go.transform.localRotation = Quaternion.Euler(0f, 60f * rng.Next(6), 0f); // hex-filling: keep edges aligned
                go.AddComponent<MeshFilter>().sharedMesh = mesh;
                go.AddComponent<MeshRenderer>().sharedMaterial = featureMaterial;
                go.SetActive(false);
                underObjects.Add(go);
            }
        }

        // ---------- The view ----------

        private void ApplyUnderView()
        {
            if (cells == null) return;
            bool on = UnderView.On;
            foreach (var go in featureObjects) if (go != null) go.SetActive(!on);
            if (on && underDirty) BuildUnderProps();
            foreach (var go in underObjects) if (go != null) go.SetActive(on);

            foreach (var cell in cells)
            {
                if (cell.Terrain == null) continue;
                if (on) cell.ShowUnder(UnderMaterial(cell.Under), UnderTint(cell));
                else cell.ShowSurface();
            }
            ShowGroupsForView();
        }

        private Material UnderMaterial(UnderKind kind)
        {
            if (!underMaterials.TryGetValue(kind, out var m) || m == null)
                underMaterials[kind] = m = Resources.Load<Material>($"Materials/Under/Under{kind}");
            return m;
        }

        // Slight per-tile variation; deep seabed darkens with depth, volcanic ground is darker
        private static Color UnderTint(HexCell cell)
        {
            var (q, r) = cell.Coordinates.ToOffsetCoordinates();
            uint h = unchecked((uint)(q * 73856093) ^ (uint)(r * 19349663));
            float j = 0.92f + 0.16f * ((h & 0xFFFF) / 65535f);
            if (cell.Under == UnderKind.DeepSeabed) j *= Mathf.Lerp(1f, 0.8f, Mathf.InverseLerp(0.5f, 1f, cell.Depth));
            if (cell.UnderFeature != UnderFeature.None) j *= 0.85f;
            return new Color(j, j, j);
        }

        // Underground-niche animals live in the under layer; everyone else on the surface
        private void ShowGroupsForView()
        {
            var colonies = SpeciesColonies.Instance;
            if (colonies == null) return;
            foreach (var g in colonies.Groups)
            {
                if (g == null) continue;
                bool visible = UnderView.On == (g.Niche == Niche.Underground);
                foreach (var rend in g.GetComponentsInChildren<Renderer>(true))
                    if (rend.enabled != visible) rend.enabled = visible;
            }
        }

        // Groups spawn, move, reproduce and evolve at any time: keep their visibility in step
        private void LateUpdate()
        {
            if (!Application.isPlaying || Time.unscaledTime < nextGroupCheck) return;
            nextGroupCheck = Time.unscaledTime + 0.25f;
            ShowGroupsForView();
        }
    }
}
