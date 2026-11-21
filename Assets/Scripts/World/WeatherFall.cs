using System;
using System.Collections.Generic;
using UnityEngine;

namespace NaturalHistory.World
{
    // Rain and snow on the surface, under the sky layer's thunderstorms and blizzards: tiles whose
    // storm or blizzard is strong this turn (SkyLayer's weather map) get a mesh of falling drops or
    // flakes, parented to the tile so it follows the map's east–west wrap. The drops are baked once
    // into a few pooled meshes and animated entirely by the WeatherFall shader. Shown only in the
    // surface view. SkyLayer sets the turn's storms and blizzards (Rebuild) and, every couple of
    // seconds, adds the rain under the moving typhoons and fronts (Refresh); only tiles whose rain
    // changes are touched.
    public class WeatherFall
    {
        private const float Threshold = 0.3f;   // storm / blizzard strength that brings rain or snow down
        private const float FallHeight = 0.9f;  // in cells, above the tile's top
        private const int MaxTiles = 160;
        private const int Levels = 3;           // pooled meshes per kind: light, steady, heavy

        private readonly Transform parent;
        private readonly Dictionary<HexCell, (GameObject go, int level, bool snowing)> tiles = new();
        private float[,] storm, blizzard;
        private HexGrid grid;
        private float cellSize;
        private Material rain, snow;
        private readonly Mesh[] rainMeshes = new Mesh[Levels], snowMeshes = new Mesh[Levels];
        private float builtFor = -1f; // cell size the meshes and materials were made for

        public WeatherFall(Transform parent) => this.parent = parent;

        public void Rebuild(HexGrid grid, float[,] storm, float[,] blizzard, float cellSize)
        {
            this.grid = grid; this.storm = storm; this.blizzard = blizzard; this.cellSize = cellSize;
            Refresh(null);
        }

        // extraRain: rain under the moving weather systems at a world point (0..1), or null
        public void Refresh(Func<Vector2, float> extraRain)
        {
            if (grid == null || storm == null || !Prepare(cellSize)) return;
            // the map being rebuilt at another size (HexGrid.GenerateSteps): wait for SkyLayer to hand in new arrays
            if (!grid.IsGenerated || blizzard == null || storm.GetLength(0) != grid.Width || storm.GetLength(1) != grid.Height
                || blizzard.GetLength(0) != grid.Width || blizzard.GetLength(1) != grid.Height) return;
            var wanted = new Dictionary<HexCell, (float strength, bool snowing)>();
            for (int r = 0; r < grid.Height; r++)
            for (int q = 0; q < grid.Width; q++)
            {
                var cell = grid.GetCell(q, r);
                if (cell == null || cell.Terrain == null) continue;
                float st = storm[q, r], bl = blizzard[q, r];
                if (extraRain != null) st = Mathf.Max(st, extraRain(new Vector2(cell.transform.position.x, cell.transform.position.z)));
                if (Mathf.Max(st, bl) < Threshold) continue;
                wanted[cell] = (Mathf.Max(st, bl), bl > st);
            }
            // the strongest first, up to the budget
            var keep = new List<KeyValuePair<HexCell, (float strength, bool snowing)>>(wanted);
            keep.Sort((a, b) => b.Value.strength.CompareTo(a.Value.strength));
            if (keep.Count > MaxTiles) keep.RemoveRange(MaxTiles, keep.Count - MaxTiles);
            var keepSet = new HashSet<HexCell>();
            bool visible = UnderView.Layer == MapLayer.Surface;
            foreach (var (cell, (strength, snowing)) in keep)
            {
                keepSet.Add(cell);
                int level = Mathf.Clamp(Mathf.FloorToInt(Mathf.InverseLerp(Threshold, 0.9f, strength) * Levels), 0, Levels - 1);
                if (tiles.TryGetValue(cell, out var old) && old.go != null)
                {
                    if (old.level == level && old.snowing == snowing) continue;
                    old.go.GetComponent<MeshFilter>().sharedMesh = snowing ? snowMeshes[level] : rainMeshes[level];
                    old.go.GetComponent<MeshRenderer>().sharedMaterial = snowing ? snow : rain;
                    tiles[cell] = (old.go, level, snowing);
                    continue;
                }
                var go = new GameObject(snowing ? "Snowfall" : "Rainfall");
                go.transform.SetParent(cell.transform, false);
                go.transform.localPosition = Vector3.up * (cell.SurfaceHeight + FallHeight * cellSize);
                go.AddComponent<MeshFilter>().sharedMesh = snowing ? snowMeshes[level] : rainMeshes[level];
                var mr = go.AddComponent<MeshRenderer>();
                mr.sharedMaterial = snowing ? snow : rain;
                mr.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
                mr.receiveShadows = false;
                go.SetActive(visible);
                tiles[cell] = (go, level, snowing);
            }
            var gone = new List<HexCell>();
            foreach (var kv in tiles) if (!keepSet.Contains(kv.Key)) gone.Add(kv.Key);
            foreach (var cell in gone) { if (tiles[cell].go != null) UnityEngine.Object.Destroy(tiles[cell].go); tiles.Remove(cell); }
        }

        public void SetVisible(bool on)
        {
            foreach (var t in tiles.Values) if (t.go != null && t.go.activeSelf != on) t.go.SetActive(on);
        }

        public void Clear()
        {
            foreach (var t in tiles.Values) if (t.go != null) UnityEngine.Object.Destroy(t.go);
            tiles.Clear();
        }

        private bool Prepare(float cellSize)
        {
            if (rain != null && Mathf.Approximately(builtFor, cellSize)) return true;
            var shader = Resources.Load<Shader>("Shaders/WeatherFall");
            if (shader == null) { Debug.LogWarning("[WeatherFall] Shaders/WeatherFall not found."); return false; }
            float fall = FallHeight * cellSize;
            rain = new Material(shader) { name = "Rain" };
            rain.SetColor("_Color", new Color(0.78f, 0.84f, 0.95f, 0.55f));
            rain.SetFloat("_Round", 0f);
            rain.SetFloat("_Fall", fall);
            rain.SetFloat("_Speed", 2.6f * cellSize);
            rain.SetFloat("_Width", 0.008f * cellSize);
            rain.SetFloat("_Length", 0.12f * cellSize);
            rain.SetVector("_Drift", new Vector4(0.12f, 0.05f, 0f, 0f));
            snow = new Material(shader) { name = "Snow" };
            snow.SetColor("_Color", new Color(1f, 1f, 1f, 0.95f));
            snow.SetFloat("_Round", 1f);
            snow.SetFloat("_Fall", fall);
            snow.SetFloat("_Speed", 0.35f * cellSize);
            snow.SetFloat("_Width", 0.018f * cellSize);
            snow.SetVector("_Drift", new Vector4(0.25f, 0.1f, 0f, 0f));
            snow.SetFloat("_Sway", 0.05f * cellSize);
            var rng = new System.Random(12345);
            for (int l = 0; l < Levels; l++)
            {
                rainMeshes[l] = Drops(rng, 60 + 70 * l, cellSize, fall, "Rain" + l);
                snowMeshes[l] = Drops(rng, 30 + 35 * l, cellSize, fall, "Snow" + l);
            }
            builtFor = cellSize;
            return true;
        }

        // `count` drops spread over the hex at the top of the fall; each a quad whose four vertices
        // share the drop's spot (the shader opens it), with its corner, phase and size in the UVs
        private static Mesh Drops(System.Random rng, int count, float cellSize, float fall, string name)
        {
            var verts = new Vector3[count * 4];
            var corner = new Vector2[count * 4];
            var drop = new Vector2[count * 4];
            var tris = new int[count * 6];
            float radius = 0.85f * cellSize;
            var corners = new[] { new Vector2(-1, -1), new Vector2(1, -1), new Vector2(1, 1), new Vector2(-1, 1) };
            for (int i = 0; i < count; i++)
            {
                float a = (float)rng.NextDouble() * Mathf.PI * 2f, d = Mathf.Sqrt((float)rng.NextDouble()) * radius;
                var at = new Vector3(Mathf.Sin(a) * d, 0f, Mathf.Cos(a) * d);
                var info = new Vector2((float)rng.NextDouble(), 0.7f + 0.6f * (float)rng.NextDouble());
                for (int k = 0; k < 4; k++) { verts[i * 4 + k] = at; corner[i * 4 + k] = corners[k]; drop[i * 4 + k] = info; }
                int v = i * 4, t = i * 6;
                tris[t] = v; tris[t + 1] = v + 2; tris[t + 2] = v + 1;
                tris[t + 3] = v; tris[t + 4] = v + 3; tris[t + 5] = v + 2;
            }
            var mesh = new Mesh { name = name, vertices = verts, triangles = tris };
            mesh.SetUVs(0, corner);
            mesh.SetUVs(1, drop);
            // the shader moves the drops down and sideways through the whole fall
            mesh.bounds = new Bounds(new Vector3(0f, -fall * 0.5f, 0f), new Vector3(radius * 2.6f, fall + 0.3f * cellSize, radius * 2.6f));
            return mesh;
        }
    }
}
