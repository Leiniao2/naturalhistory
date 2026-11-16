using System.Collections.Generic;
using NaturalHistory.Core;
using UnityEngine;

namespace NaturalHistory.World
{
    // The layer under sea level, shown instead of the surface while UnderView is on.
    //
    //   - Under land: a maze. Solid bedrock that nothing can get through, with winding tunnels of
    //     soil and burrows carved through it from the caves (karst regions, ~25% of land) and the
    //     coast; every open tile can be reached from the others.
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
        private const float TunnelShare  = 0.3f;  // of land carved into tunnels (the rest that isn't cave is bedrock)

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
                    kind = cell.Depth >= 0.7f ? UnderKind.DeepSeabed : UnderKind.Seabed; // only the deepest water: its floor is bare mud and bacterial mats
                    if (kind == UnderKind.Seabed && coast && odd > 0.36f)
                        kind = odd > 0.44f ? UnderKind.Rock : UnderKind.Cave;              // sea caves, a buried headland
                }
                else
                {
                    kind = caves.Contains(cell) ? UnderKind.Cave : UnderKind.Bedrock; // tunnels are carved below
                    if (coast && odd > 0.38f)      kind = UnderKind.Seabed;               // a drowned valley under the coast
                    else if (lake && odd < -0.40f) kind = UnderKind.Lakebed;              // an old lake, buried
                }
                cell.SetUnder(kind, UnderFeature.None);
                if (kind is UnderKind.Seabed or UnderKind.DeepSeabed) sea.Add((cell, Noise(cell, 0.35f, volcanoOff) + (kind == UnderKind.DeepSeabed ? 0.1f : 0f)));
                if (kind == UnderKind.DeepSeabed) deep.Add((cell, Noise(cell, 0.6f, ventOff)));
            }

            CarveTunnels(rng);

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

        // Winding tunnels through the bedrock: "worms" set out from the caves, the coast and earlier
        // tunnels, keep roughly to a heading and turn now and then, and stop rather than open into a
        // passage beside them (now and then they break through, making loops), so corridors stay one
        // tile wide. Then any pocket still cut off is joined to the rest by the shortest way through.
        private void CarveTunnels(System.Random rng)
        {
            bool Open(HexCell c) => c != null && c.Terrain != null && !UnderView.Blocks(c.Under);
            var starts = new List<HexCell>();
            int landCount = 0;
            foreach (var cell in cells)
            {
                if (cell.Terrain == null || cell.IsWater) continue;
                landCount++;
                if (!Open(cell)) foreach (var n in GetNeighbors(cell)) { if (n.IsWater) { starts.Add(cell); break; } } // coast: in from the sea
                else starts.Add(cell);                                                                                  // cave edges
            }
            if (starts.Count == 0) return;

            int budget = Mathf.RoundToInt(landCount * TunnelShare), carved = 0;
            for (int worm = 0; carved < budget && worm < budget * 4; worm++)
            {
                var here = starts[rng.Next(starts.Count)];
                if (!Open(here)) { here.SetUnder(UnderKind.Rock, UnderFeature.None); carved++; }
                int dir = rng.Next(6), length = rng.Next(5, 16);
                for (int step = 0; step < length; step++)
                {
                    double turn = rng.NextDouble();
                    if (turn < 0.2) dir = (dir + 1) % 6; else if (turn < 0.4) dir = (dir + 5) % 6;
                    var next = EdgeNeighbors(here)[dir];
                    if (next == null || next.Terrain == null || next.IsWater) break;
                    if (!Open(next))
                    {
                        int openAround = 0;
                        foreach (var n in GetNeighbors(next)) if (n != here && !n.IsWater && Open(n)) openAround++;
                        if (openAround >= 2 && rng.NextDouble() > 0.12) break; // would widen into a hall: stop here
                        next.SetUnder(UnderKind.Rock, UnderFeature.None);
                        carved++;
                    }
                    here = next;
                    if (rng.NextDouble() < 0.15) starts.Add(here); // a branch may set out from here later
                }
            }

            // Join up: flood the open layer from the water (the seabed is all one), then dig the
            // shortest way from each pocket left over to the reached part
            var reached = new HashSet<HexCell>();
            int joins = 0;
            void Flood(HexCell from)
            {
                var queue = new Queue<HexCell>();
                if (reached.Add(from)) queue.Enqueue(from);
                while (queue.Count > 0)
                    foreach (var n in GetNeighbors(queue.Dequeue()))
                        if (Open(n) && reached.Add(n)) queue.Enqueue(n);
            }
            foreach (var cell in cells) if (cell.Terrain != null && cell.IsWater && Open(cell) && !reached.Contains(cell)) Flood(cell);
            foreach (var cell in cells)
            {
                if (!Open(cell) || reached.Contains(cell)) continue;
                var parent = new Dictionary<HexCell, HexCell> { [cell] = null };
                var queue  = new Queue<HexCell>();
                queue.Enqueue(cell);
                HexCell meet = null;
                while (queue.Count > 0 && meet == null)
                {
                    var c = queue.Dequeue();
                    foreach (var n in GetNeighbors(c))
                    {
                        if (n.Terrain == null || parent.ContainsKey(n)) continue;
                        parent[n] = c;
                        if (reached.Contains(n)) { meet = n; break; }
                        queue.Enqueue(n);
                    }
                }
                for (var c = meet != null ? parent[meet] : null; c != null; c = parent[c])
                    if (!Open(c)) { c.SetUnder(UnderKind.Rock, UnderFeature.None); joins++; }
                Flood(cell);
            }
            int solid = 0;
            foreach (var cell in cells) if (cell.Terrain != null && !cell.IsWater && !Open(cell)) solid++;
            Debug.Log($"[HexGrid] Underground maze — {carved} tunnel tiles carved, {joins} dug to join pockets, {solid} of {landCount} land tiles solid bedrock");
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
            var bedrock = new Mesh[8];
            for (int i = 0; i < bedrock.Length; i++) bedrock[i] = Track(CreateBedrockMesh(rng));
            Mesh Pick(Mesh[] pool) => pool[rng.Next(pool.Length)];
            // Water-plant beds vary a little across the map, but every seabed and lakebed tile is covered
            var bedOffset = new Vector3((float)rng.NextDouble(), (float)rng.NextDouble(), (float)rng.NextDouble()) * 1000f;
            float BedDensity(HexCell c)
            {
                if (c.Under is not (UnderKind.Seabed or UnderKind.DeepSeabed or UnderKind.Lakebed)) return 1f;
                var pos = c.Coordinates.ToWorldPosition(cellSize);
                var p = OnMapLoop(new Vector2(pos.x, pos.z)) * (0.18f / cellSize) + bedOffset;
                float n = PerlinNoise3D.Sample(p.x, p.y, p.z);
                return n < -0.25f ? 0.85f : n > 0.25f ? 1.15f : 1f; // three steps, so the meshes can still be shared
            }
            foreach (var cell in cells)
            {
                if (cell.Terrain == null) continue;
                Mesh mesh = cell.Under == UnderKind.Bedrock ? Pick(bedrock) : cell.UnderFeature switch
                {
                    UnderFeature.Volcano => Track(MapFeatureMeshes.CreateVolcano(rng, cellSize, 0.5f + 0.3f * (float)rng.NextDouble())),
                    UnderFeature.Vents   => Track(MapFeatureMeshes.CreateVents(rng, cellSize)),
                    _ => plants.Under(rng, cell.Under,
                                      cell.UnderPlants.Count > 0 ? cell.UnderPlants[0] : null,
                                      cell.UnderPlants.Count > 1 ? cell.UnderPlants[1] : null,
                                      BedDensity(cell)),
                };
                if (mesh == null) continue;
                var go = new GameObject(mesh.name);
                if (!Application.isPlaying) go.hideFlags = HideFlags.DontSave;
                go.transform.SetParent(cell.transform, false);
                go.transform.localPosition = Vector3.up * cell.SurfaceHeight;
                go.transform.localRotation = Quaternion.Euler(0f, 60f * rng.Next(6), 0f); // hex-filling: keep edges aligned
                go.AddComponent<MeshFilter>().sharedMesh = mesh;
                bool water = cell.Under is UnderKind.Seabed or UnderKind.Lakebed && cell.UnderFeature == UnderFeature.None;
                go.AddComponent<MeshRenderer>().sharedMaterial = water ? SwayMaterial() : featureMaterial;
                go.SetActive(false);
                underObjects.Add(go);
            }
        }

        // The prop material with swaying turned on, for seabed and lakebed plants: tall fronds lean
        // slowly with the swell, low algae barely stir (MapFeature.shader _Sway)
        private Material swayMaterial;
        private Material SwayMaterial()
        {
            if (swayMaterial == null)
            {
                swayMaterial = new Material(featureMaterial) { name = "MapFeaturesSway" };
                swayMaterial.SetVector("_Sway", new Vector4(0.18f, 0.25f * cellSize, 0.9f, 2.5f * cellSize));
            }
            return swayMaterial;
        }

        // A block of solid rock filling the hex: a jagged, faceted top standing well above the
        // tunnels around it, with walls going down into the ground, so the bedrock reads as the
        // walls of the maze. Faceted (own vertices per face) dark grey with lighter crests.
        private Mesh CreateBedrockMesh(System.Random rng)
        {
            float R(float min, float max) => min + (float)rng.NextDouble() * (max - min);
            float corner = cellSize * TileRadius, apo = corner * 0.8660254f;
            var top = new Vector3[12];   // outer ring: corner i at 2i, edge midpoint at 2i + 1
            var inner = new Vector3[6];
            for (int j = 0; j < 12; j++)
            {
                float a = Mathf.Deg2Rad * 30f * j;
                float rad = (j % 2 == 0 ? corner : apo) * R(0.97f, 1f);
                top[j] = new Vector3(Mathf.Sin(a) * rad, cellSize * R(0.13f, 0.2f), Mathf.Cos(a) * rad);
            }
            for (int i = 0; i < 6; i++)
            {
                float a = Mathf.Deg2Rad * (60f * i + R(-12f, 12f));
                float rad = corner * R(0.4f, 0.6f);
                inner[i] = new Vector3(Mathf.Sin(a) * rad, cellSize * R(0.2f, 0.3f), Mathf.Cos(a) * rad);
            }
            var centre = new Vector3(R(-0.05f, 0.05f) * cellSize, cellSize * R(0.26f, 0.34f), R(-0.05f, 0.05f) * cellSize);
            float bottom = -cellSize * 0.2f;

            var verts = new List<Vector3>(); var colors = new List<Color>(); var tris = new List<int>();
            void Face(Vector3 a, Vector3 b, Vector3 c, Color col)
            {
                int k = verts.Count;
                verts.Add(a); verts.Add(b); verts.Add(c);
                colors.Add(col); colors.Add(col); colors.Add(col);
                tris.Add(k); tris.Add(k + 1); tris.Add(k + 2);
            }
            Color Rock(float y) // higher is lighter: crests catch the light
            {
                float v = Mathf.Lerp(0.26f, 0.42f, Mathf.InverseLerp(0.1f, 0.34f, y / cellSize)) * R(0.92f, 1.08f);
                return new Color(v, v * 0.97f, v * 0.93f);
            }
            for (int i = 0; i < 6; i++)
            {
                int n = (i + 1) % 6;
                Vector3 a = inner[i], b = top[2 * i], c = top[2 * i + 1], d = top[(2 * i + 2) % 12];
                Face(centre, a, inner[n], Rock((centre.y + a.y + inner[n].y) / 3f));
                Face(a, b, c, Rock((a.y + b.y + c.y) / 3f));
                Face(a, c, inner[n], Rock((a.y + c.y + inner[n].y) / 3f));
                Face(inner[n], c, d, Rock((inner[n].y + c.y + d.y) / 3f));
            }
            for (int j = 0; j < 12; j++)
            {
                Vector3 t0 = top[j], t1 = top[(j + 1) % 12];
                Vector3 b0 = new(t0.x, bottom, t0.z), b1 = new(t1.x, bottom, t1.z);
                var wall = Rock(0f) * 0.85f;
                Face(t0, b0, t1, wall);
                Face(t1, b0, b1, wall);
            }
            var mesh = new Mesh { name = "Bedrock" };
            mesh.SetVertices(verts);
            mesh.SetColors(colors);
            mesh.SetTriangles(tris, 0);
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            return mesh;
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
                if (on) cell.ShowUnder(UnderMaterial(cell), UnderTint(cell));
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

        // A water tile whose plants are mats, crusts or turf shows them painted into its floor
        // (UnderMeshes.CoverOf), e.g. Materials/Under/UnderSeabedCoralline; otherwise the plain floor.
        private readonly Dictionary<string, Material> coverMaterials = new();
        private Material UnderMaterial(HexCell cell)
        {
            if (cell.UnderFeature == UnderFeature.None && cell.Under is UnderKind.Seabed or UnderKind.DeepSeabed or UnderKind.Lakebed)
            {
                var plants = cell.UnderPlants;
                string cover = MapFeatureMeshes.CoverOf(cell.Under, plants.Count > 0 ? plants[0] : null, plants.Count > 1 ? plants[1] : null);
                if (cover != null)
                {
                    string name = $"Under{cell.Under}{cover}";
                    if (!coverMaterials.TryGetValue(name, out var m) || m == null)
                        coverMaterials[name] = m = Resources.Load<Material>($"Materials/Under/{name}");
                    if (m != null) return m;
                }
            }
            return UnderMaterial(cell.Under);
        }

        // Seen through the water above: everything under the sea is tinted sea blue, turquoise over
        // the shallows deepening to blue with depth; lakebeds a lighter green-blue. Plus slight
        // per-tile variation; deep seabed darkens with depth, volcanic ground is darker.
        private static readonly Color ShallowSea = new(0.55f, 0.95f, 1.45f);
        private static readonly Color DeepSea    = new(0.62f, 0.82f, 1.5f);
        private static readonly Color LakeWater  = new(0.75f, 1.0f, 1.2f);

        private static Color UnderTint(HexCell cell)
        {
            var (q, r) = cell.Coordinates.ToOffsetCoordinates();
            uint h = unchecked((uint)(q * 73856093) ^ (uint)(r * 19349663));
            float j = 0.97f + 0.06f * ((h & 0xFFFF) / 65535f); // slight, so neighbouring tiles read as one floor
            if (cell.Under == UnderKind.DeepSeabed) j *= Mathf.Lerp(1f, 0.8f, Mathf.InverseLerp(0.5f, 1f, cell.Depth));
            if (cell.UnderFeature != UnderFeature.None) j *= 0.92f;
            if (cell.Under == UnderKind.Bedrock) j *= 0.6f;
            var water = Color.white;
            if (cell.Terrain.kind == TerrainKind.SaltWater) water = Color.Lerp(ShallowSea, DeepSea, cell.Depth);
            else if (cell.Terrain.kind == TerrainKind.FreshWater) water = LakeWater;
            return water * j;
        }

        // Underground-niche animals live in the under layer; everyone else on the surface
        private void ShowGroupsForView()
        {
            var colonies = SpeciesColonies.Instance;
            if (colonies == null) return;
            foreach (var g in colonies.Groups)
            {
                if (g == null) continue;
                bool visible = UnderView.Shows(g);
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
