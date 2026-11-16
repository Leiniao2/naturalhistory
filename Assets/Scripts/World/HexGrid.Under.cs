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
        private const float UnderWaterGrowth = 0.5f; // the layer below has this much more water than the surface (of the surface's water tiles)

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

            DrownUnderLand(sea, Offset());
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
            // shallow hydrothermal fields: on the shelf around seamounts, and now and then elsewhere
            foreach (var (cell, v) in sea)
            {
                if (cell.Under != UnderKind.Seabed || cell.UnderFeature != UnderFeature.None) continue;
                bool nearSeamount = false;
                foreach (var n in GetNeighbors(cell)) if (n.UnderFeature == UnderFeature.Volcano) nearSeamount = true;
                double roll = rng.NextDouble();
                if (nearSeamount ? roll < 0.3 : roll < 0.006) cell.SetUnder(cell.Under, UnderFeature.Geothermal);
            }
            ComputeSeabedRelief(worldSeed);
            underDirty = true;
        }

        // Winding tunnels through the bedrock: "worms" set out from the caves, the coast and earlier
        // tunnels, keep roughly to a heading and turn now and then, and stop rather than open into a
        // passage beside them (now and then they break through, making loops), so corridors stay one
        // tile wide. Then any pocket still cut off is joined to the rest by the shortest way through.
        // Below the land near the coast and lakes lie drowned valleys, old sea floors and buried lakes:
        // land tiles are taken nearest the water first (with noise, so the edge wanders), and lower
        // ground before high, until the layer below has UnderWaterGrowth more water than the surface.
        // Near lakes and far from the sea they are lakebeds, otherwise seabed.
        private void DrownUnderLand(List<(HexCell cell, float v)> sea, Vector3 off)
        {
            int water = 0;
            foreach (var c in cells) if (c?.Terrain != null && c.IsWater) water++;
            int already = 0;
            foreach (var c in cells) if (c?.Terrain != null && !c.IsWater && WaterBed(c.Under)) already++;
            int want = Mathf.RoundToInt(water * UnderWaterGrowth) - already;
            if (want <= 0) return;

            // steps to the nearest salt and fresh water
            var toSea = new Dictionary<HexCell, int>(); var toLake = new Dictionary<HexCell, int>();
            void Steps(Dictionary<HexCell, int> dist, System.Func<HexCell, bool> source)
            {
                var queue = new Queue<HexCell>();
                foreach (var c in cells) if (c?.Terrain != null && source(c)) { dist[c] = 0; queue.Enqueue(c); }
                while (queue.Count > 0)
                {
                    var c = queue.Dequeue();
                    foreach (var n in GetNeighbors(c))
                        if (n?.Terrain != null && !dist.ContainsKey(n)) { dist[n] = dist[c] + 1; queue.Enqueue(n); }
                }
            }
            Steps(toSea, c => c.Terrain.kind == TerrainKind.SaltWater);
            Steps(toLake, c => c.Terrain.kind == TerrainKind.FreshWater || c.Terrain.kind == TerrainKind.Wetland);

            var land = new List<(HexCell cell, float score)>();
            foreach (var c in cells)
            {
                if (c?.Terrain == null || c.IsWater || WaterBed(c.Under)) continue;
                int s = toSea.TryGetValue(c, out var ds) ? ds : 99, l = toLake.TryGetValue(c, out var dl) ? dl : 99;
                var pos = c.Coordinates.ToWorldPosition(cellSize);
                var p = OnMapLoop(new Vector2(pos.x, pos.z)) * (0.35f / cellSize) + off;
                float score = Mathf.Min(s, l + 0.5f) + PerlinNoise3D.Sample(p.x, p.y, p.z) * 4f + c.Elevation * 0.25f + (c.IsMountain ? 3f : 0f);
                land.Add((c, score));
            }
            land.Sort((a, b) => a.score.CompareTo(b.score));
            for (int i = 0; i < Mathf.Min(want, land.Count); i++)
            {
                var c = land[i].cell;
                int s = toSea.TryGetValue(c, out var ds) ? ds : 99, l = toLake.TryGetValue(c, out var dl) ? dl : 99;
                var kind = l + 1 < s ? UnderKind.Lakebed : UnderKind.Seabed;
                c.SetUnder(kind, UnderFeature.None);
                if (kind == UnderKind.Seabed) sea.Add((c, -1f)); // shallow old sea floor: rarely a seamount
            }
        }

        private void CarveTunnels(System.Random rng)
        {
            bool Open(HexCell c) => c != null && c.Terrain != null && !UnderView.Blocks(c.Under);
            var starts = new List<HexCell>();
            int landCount = 0;
            foreach (var cell in cells)
            {
                if (cell.Terrain == null || cell.IsWater) continue;
                if (WaterBed(cell.Under)) continue;                                                                       // drowned: not part of the maze
                landCount++;
                if (!Open(cell)) foreach (var n in GetNeighbors(cell)) { if (n.IsWater || WaterBed(n.Under)) { starts.Add(cell); break; } } // in from the water
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
        // The Ediacaran and Cambrian seafloor was mostly microbial: in broad regions of the shallow
        // seabed and lakebed stromatolites (about 30% of tiles) or microbial mats (about 30%) are the
        // main growth there, the tile's other plant coming second; HexGrid.UnderMaterial then paints
        // them into the floor. Noise thresholds are quantiles of PerlinNoise3D (0.155: top 30%,
        // -0.074: top 60%).
        private void MoreMicrobialFloors(GeologicalAge age, List<(HexCell cell, PlantDefinition main, PlantDefinition second)> beds)
        {
            if (age > GeologicalAge.Cambrian || beds.Count == 0) return;
            var alive = PlantCatalog.AliveIn(age);
            var offset = new Vector3(613f, 151f, 277f) + Vector3.one * (WorldSeed % 997);
            for (int i = 0; i < beds.Count; i++)
            {
                var (cell, main, second) = beds[i];
                if (cell.UnderFeature != UnderFeature.None) continue;
                string kind = cell.Under.ToString();
                var stromatolite = alive.Find(p => p.layer == "under" && p.form == "Stromatolite" && p.terrains.Contains(kind));
                var mat          = alive.Find(p => p.layer == "under" && p.form == "Mat" && p.terrains.Contains(kind));
                var pos = cell.Coordinates.ToWorldPosition(cellSize);
                var q = OnMapLoop(new Vector2(pos.x, pos.z)) * (0.3f / cellSize) + offset;
                float n = PerlinNoise3D.Sample(q.x, q.y, q.z);
                var floor = n > 0.3f ? stromatolite : n > -0.074f ? mat : null; // stromatolite floors on ~15% of the beds
                if (floor == null || floor == main) continue;
                beds[i] = (cell, floor, main != null && main != floor ? main : second);
            }
        }

        private void DressUnder(GeologicalAge age)
        {
            var plants = new PlantPlanner(age, WorldSeed, cellSize, WrapWidth, Track);
            var seabed = new List<(HexCell cell, PlantDefinition main, PlantDefinition second)>();
            var lakebed = new List<(HexCell cell, PlantDefinition main, PlantDefinition second)>();
            foreach (var cell in cells)
            {
                if (cell.Terrain == null) continue;
                var (main, second) = plants.ChooseUnder(cell);
                if (cell.Under == UnderKind.Seabed) seabed.Add((cell, main, second));
                else if (cell.Under == UnderKind.Lakebed) lakebed.Add((cell, main, second));
                else cell.SetUnderPlants(main, second);
            }
            MoreAlgalTurf(plants, seabed);
            MoreMicrobialFloors(age, seabed);
            MoreMicrobialFloors(age, lakebed);
            foreach (var (cell, main, second) in seabed) cell.SetUnderPlants(main, second);
            foreach (var (cell, main, second) in lakebed) cell.SetUnderPlants(main, second);
            underDirty = true;
            if (UnderView.On) ApplyUnderView();
        }

        // Algal turf covers far more of the seabed, most of all in warm water: at least twice the
        // share the species ranking alone gives (up to 85% of seabed tiles), made up by turning the
        // warmest tiles that aren't turf yet into turf. Warmth is the water's temperature by
        // latitude, with a broad patchy noise so the turf edge isn't a straight band.
        private const float AlgalTurfBoost = 2.2f, AlgalTurfMax = 0.85f;

        private void MoreAlgalTurf(PlantPlanner plants, List<(HexCell cell, PlantDefinition main, PlantDefinition second)> seabed)
        {
            if (seabed.Count == 0) return;
            bool Turf(PlantDefinition a, PlantDefinition b) => MapFeatureMeshes.CoverOf(UnderKind.Seabed, a, b) == "AlgalTurf";
            int turf = 0;
            foreach (var t in seabed) if (Turf(t.main, t.second)) turf++;
            int target = Mathf.Min(Mathf.RoundToInt(seabed.Count * AlgalTurfMax),
                                   Mathf.Max(Mathf.CeilToInt(turf * AlgalTurfBoost), Mathf.CeilToInt(seabed.Count * 0.2f)));
            if (turf >= target) return;

            var off = new Vector3(17.3f, 41.9f, 5.7f) + Vector3.one * (WorldSeed % 997);
            float Warmth(HexCell c)
            {
                float lat = c.HasInputs ? c.Inputs.lat
                          : Mathf.Abs(c.Coordinates.ToOffsetCoordinates().row / (float)Mathf.Max(Height - 1, 1) * 2f - 1f);
                var pos = c.Coordinates.ToWorldPosition(cellSize);
                var p = OnMapLoop(new Vector2(pos.x, pos.z)) * (0.22f / cellSize) + off;
                return 1f - 0.9f * lat + 0.25f * PerlinNoise3D.Sample(p.x, p.y, p.z);
            }
            var order = new List<int>();
            for (int i = 0; i < seabed.Count; i++) if (!Turf(seabed[i].main, seabed[i].second)) order.Add(i);
            var warmth = new Dictionary<int, float>();
            foreach (int i in order) warmth[i] = Warmth(seabed[i].cell);
            order.Sort((a, b) => warmth[b].CompareTo(warmth[a]));
            foreach (int i in order)
            {
                if (turf >= target) break;
                var (cell, main, second) = seabed[i];
                var (m, s) = plants.WithAlgalTurf(cell, main, second);
                if (!Turf(m, s)) continue;
                seabed[i] = (cell, m, s);
                turf++;
            }
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
                    UnderFeature.Volcano => Track(MapFeatureMeshes.CreateVolcano(rng, cellSize, 0.5f + 0.3f * (float)rng.NextDouble(), underwater: true)),
                    UnderFeature.Vents   => Track(MapFeatureMeshes.CreateVents(rng, cellSize)),
                    UnderFeature.Geothermal => Track(MapFeatureMeshes.CreateShallowVents(rng, cellSize)),
                    _ => plants.Under(rng, cell.Under,
                                      cell.UnderPlants.Count > 0 ? cell.UnderPlants[0] : null,
                                      cell.UnderPlants.Count > 1 ? cell.UnderPlants[1] : null,
                                      BedDensity(cell) * (MeadowCovered(cell) ? MeadowPropShare : 1f)),
                };
                if (mesh == null) continue;
                var go = new GameObject(mesh.name);
                if (!Application.isPlaying) go.hideFlags = HideFlags.DontSave;
                go.transform.SetParent(cell.transform, false);
                go.transform.localPosition = Vector3.up * UnderSurface(cell); // on the seabed, below sea level
                go.transform.localRotation = Quaternion.Euler(0f, 60f * rng.Next(6), 0f); // hex-filling: keep edges aligned
                go.AddComponent<MeshFilter>().sharedMesh = mesh;
                bool water = cell.Under is UnderKind.Seabed or UnderKind.Lakebed && cell.UnderFeature == UnderFeature.None;
                go.AddComponent<MeshRenderer>().sharedMaterial = water ? SwayMaterial() : featureMaterial;
                if (cell.UnderFeature == UnderFeature.Geothermal && Application.isPlaying && MapFeatureMeshes.TryGetSteamVents(mesh, out var seeps))
                    go.AddComponent<GeothermalSteam>().Init(cellSize, WorldSeed ^ cell.Coordinates.GetHashCode(), seeps, -1, underwater: true);
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

        private static bool WaterBed(UnderKind k) => k is UnderKind.Seabed or UnderKind.DeepSeabed or UnderKind.Lakebed;

        private void ApplyUnderView()
        {
            if (cells == null) return;
            bool on = UnderView.On;
            foreach (var go in featureObjects) if (go != null) go.SetActive(!on);
            if (on && underDirty) BuildUnderProps();
            foreach (var go in underObjects) if (go != null) go.SetActive(on);

            Shader.SetGlobalFloat("_BuiltinEdgeBlend", on ? 1f : 0f); // the built-in shader blends tile edges only down here
            ShowSeabedRelief(on);
            var textures = new Texture[6];
            var tints    = new Vector4[6];
            var scales   = new float[6];
            foreach (var cell in cells)
            {
                if (cell.Terrain == null) continue;
                if (!on) { cell.ShowSurface(); continue; }
                // Fade into the neighbouring beds: water beds into water beds, rock and caves into rock
                System.Array.Clear(textures, 0, 6);
                System.Array.Clear(tints, 0, 6);
                System.Array.Clear(scales, 0, 6);
                var n = EdgeNeighbors(cell);
                for (int e = 0; e < 6; e++)
                {
                    if (n[e]?.Terrain == null || WaterBed(n[e].Under) != WaterBed(cell.Under)) continue;
                    var m = UnderMaterial(n[e]);
                    if (m == null || !m.HasProperty("_BaseMap")) continue;
                    var t = UnderTint(n[e]);
                    textures[e] = m.GetTexture("_BaseMap");
                    tints[e]    = new Vector4(t.r, t.g, t.b, 1f);
                    scales[e]   = m.HasProperty("_Tiling") ? m.GetFloat("_Tiling") : 0f;
                }
                cell.ShowUnder(UnderMaterial(cell), UnderTint(cell), textures, tints, scales, waterBed: WaterBed(cell.Under));
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
        // Meadows: about 40% of the seabed and lakebed with water plants, in broad regions, shows its
        // plants painted into the floor (seagrass meadow, kelp bed, seaweed or waterweed meadow, by
        // the main species) with only MeadowPropShare of the 3D plants standing on it — much less to draw.
        private const float MeadowPropShare = 0.3f;
        // noise above this is meadow: 40% of the beds, 55% from the Cretaceous on, when the seas hold
        // much more plant bed (measured on PerlinNoise3D's distribution)
        private float MeadowThreshold => DisplayedAge >= NaturalHistory.Core.GeologicalAge.Cretaceous ? -0.037f : 0.074f;
        private bool IsMeadow(HexCell cell)
        {
            if (cell.Under is not (UnderKind.Seabed or UnderKind.Lakebed) || cell.UnderPlants.Count == 0) return false;
            var pos = cell.Coordinates.ToWorldPosition(cellSize);
            var p = OnMapLoop(new Vector2(pos.x, pos.z)) * (0.22f / cellSize) + new Vector3(311f, 77f, 913f) + Vector3.one * (WorldSeed % 1000);
            return PerlinNoise3D.Sample(p.x, p.y, p.z) > MeadowThreshold;
        }

        // Whether this tile's floor is shown as a stromatolite floor (named so in the tile panel)
        public bool ShowsStromatoliteFloor(HexCell cell) => FloorCover(cell) == "Stromatolite";

        private bool MeadowCovered(HexCell cell) => MapFeatureMeshes.IsMeadowCover(FloorCover(cell));

        // The painted floor a water tile shows (now only stromatolites, on the tiles where they are the
        // floor), or null for the plain, sunlit seabed.
        private string FloorCover(HexCell cell)
        {
            if (cell.UnderFeature != UnderFeature.None || cell.Under is not (UnderKind.Seabed or UnderKind.DeepSeabed or UnderKind.Lakebed)) return null;
            var plants = cell.UnderPlants;
            string cover = MapFeatureMeshes.CoverOf(cell.Under, plants.Count > 0 ? plants[0] : null, plants.Count > 1 ? plants[1] : null, IsMeadow(cell));
            // painted: stromatolite floors; mats, algal turf and meadows as see-through clumps on the
            // plain floor (tools/terrain/mat_patches.py). Coralline crusts show as their 3D plants.
            return cover is "Stromatolite" or "MicrobialMat" or "BacterialMat" or "AlgalTurf" || MapFeatureMeshes.IsMeadowCover(cover) ? cover : null;
        }

        private int StromatoliteVariant(HexCell cell)
        {
            var pos = cell.Coordinates.ToWorldPosition(cellSize);
            var p = OnMapLoop(new Vector2(pos.x, pos.z)) * (0.3f / cellSize) + Vector3.one * 517f;
            float n = PerlinNoise3D.Sample(p.x, p.y, p.z);
            var (q, r) = cell.Coordinates.ToOffsetCoordinates();
            int jitter = ((q * 7 + r * 13) & 7) == 0 ? 1 : 0; // the odd tile breaks a patch up
            return ((n < -0.128f ? 0 : n > 0.128f ? 2 : 1) + jitter) % 3;
        }

        private Material UnderMaterial(HexCell cell)
        {
            string cover = FloorCover(cell);
            if (cover != null)
            {
                string name = $"Under{cell.Under}{cover}";
                // stromatolite fields come in three kinds (domes, current-drawn heads, columns), mixed
                // in patches so neighbouring tiles differ (Materials/Under/...Stromatolite, 2, 3)
                if (cover == "Stromatolite") name += StromatoliteVariant(cell) switch { 1 => "2", 2 => "3", _ => "" };
                if (!coverMaterials.TryGetValue(name, out var m) || m == null)
                    coverMaterials[name] = m = Resources.Load<Material>($"Materials/Under/{name}");
                if (m != null) return m;
            }
            return UnderMaterial(cell.Under);
        }

        // Floors keep their own colours under a light veil of water: seabed (and old sea floors under
        // the land) a faint pale blue, lakebeds a fainter green-blue, so they read as under water
        // without hiding the floor; only the deepest layer, the deep seabed, is tinted deep blue
        // (darker the deeper it lies). Stromatolite floors take the same veil, and so do the 3D
        // stromatolites on them (MapFeatureMeshes.SeaVeil), so floor and domes are one tone. Plus slight per-tile variation; volcanic ground and bedrock are darker.
        private static readonly Color DeepSea   = new(0.62f, 0.82f, 1.5f);
        private static Color SeaVeil  => MapFeatureMeshes.SeaVeil;
        private static Color LakeVeil => MapFeatureMeshes.LakeVeil;

        private Color UnderTint(HexCell cell)
        {
            var (q, r) = cell.Coordinates.ToOffsetCoordinates();
            uint h = unchecked((uint)(q * 73856093) ^ (uint)(r * 19349663));
            float j = 0.97f + 0.06f * ((h & 0xFFFF) / 65535f); // slight, so neighbouring tiles read as one floor
            if (cell.UnderFeature != UnderFeature.None) j *= 0.92f;
            if (cell.Under == UnderKind.Bedrock) j *= 0.6f;
            // a little lighter on the banks and darker in the hollows and the deep, so the seabed's
            // relief (HexGrid.Seabed) shows in its shading too
            if (cell.IsWater && cell.Terrain.kind == TerrainKind.SaltWater)
                j *= Mathf.Lerp(1.06f, 0.72f, Mathf.InverseLerp(0.03f, 0.5f, cell.SurfaceHeight - UnderSurface(cell)));
            if (cell.Under == UnderKind.Seabed) return SeaVeil * j;
            if (cell.Under == UnderKind.Lakebed) return LakeVeil * j;
            if (cell.Under != UnderKind.DeepSeabed || FloorCover(cell) == "Stromatolite") return Color.white * j;
            j *= Mathf.Lerp(1f, 0.8f, Mathf.InverseLerp(0.5f, 1f, cell.Depth));
            return DeepSea * j;
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
                // down to the seabed in the under view: seafloor dwellers onto it, swimmers half way
                float depth = UnderView.On && g.Cell != null && g.Cell.IsWater ? g.Cell.SurfaceHeight - UnderSurface(g.Cell) : 0f;
                g.DepthOffset = g.Niche == Niche.Underground ? depth : depth * 0.5f;
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
