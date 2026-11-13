using System.Collections.Generic;
using NaturalHistory.Data;
using UnityEngine;

namespace NaturalHistory.World
{
    // How a species' group looks and moves on its tile (species.json "mapStyle").
    public enum ColonyStyle
    {
        Drift, // micro-organisms: a cluster hovering over the tile, slowly tumbling and bobbing
        Float, // sits on the water surface (pivot at the waterline), rocking gently
        Ground,// stands on the tile (pivot at the feet), each facing its own way
        Soar,  // circles high above the tile, banked into the turn
        Swarm, // a jittery cloud of small fliers
        Swim,  // a school circling just above the water (tiles are opaque, so they can't go under it)
    }

    // Shows a group of every species that has a map model (species.json "model") on one of its
    // habitat tiles. Groups are children of their cell, so they follow the east–west wrap and are
    // destroyed when the map regenerates. Models face +Z with their pivot as described in
    // tools/blender/nh_model.py; they are rescaled from their mesh bounds, so file units don't matter.
    public class SpeciesColonies : MonoBehaviour
    {
        // count, size (longest dimension, in cells), spread radius from the cell centre
        private static readonly Dictionary<ColonyStyle, (int count, float span, float radius)> Layouts = new()
        {
            [ColonyStyle.Drift]  = (7, 0.32f, 0.36f),
            [ColonyStyle.Float]  = (4, 0.26f, 0.32f),
            [ColonyStyle.Ground] = (3, 0.34f, 0.30f),
            [ColonyStyle.Soar]   = (3, 0.42f, 0.45f),
            [ColonyStyle.Swarm]  = (9, 0.11f, 0.22f),
            [ColonyStyle.Swim]   = (5, 0.26f, 0.32f),
        };

        private const float SoarHeight  = 0.75f;
        private const float SwarmHeight = 0.35f;

        private HexGrid grid;
        private Material material;
        private readonly List<Member> members = new();

        private struct Member
        {
            public Transform transform;
            public ColonyStyle style;
            public Vector3 basePosition;
            public Quaternion baseRotation;
            public Vector3 axis;   // Drift: tumble axis
            public float phase;
            public float speed;    // Soar/Swim: radians per second around the cell (sign = direction)
            public float radius;   // Soar/Swim: circle radius
        }

        // Spawns the component in any scene that has a HexGrid, so Game.unity doesn't need editing.
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Bootstrap()
        {
            if (FindAnyObjectByType<HexGrid>() == null || FindAnyObjectByType<SpeciesColonies>() != null) return;
            new GameObject("SpeciesColonies").AddComponent<SpeciesColonies>();
        }

        private void Start()
        {
            grid = HexGrid.Instance;
            if (grid == null) { Debug.LogWarning("[SpeciesColonies] No HexGrid in scene."); return; }
            if (GameDataLoader.Species == null) GameDataLoader.Initialize();

            grid.Generated += PlaceColonies;
            if (grid.IsGenerated) PlaceColonies();
        }

        private void OnDestroy()
        {
            if (grid != null) grid.Generated -= PlaceColonies;
        }

        private void Update()
        {
            float t = Time.time;
            foreach (var m in members)
            {
                if (m.transform == null) continue; // cell destroyed by a regenerate that hasn't re-placed yet
                var tr = m.transform;
                switch (m.style)
                {
                    case ColonyStyle.Drift:
                        tr.localRotation = Quaternion.AngleAxis(t * 12f + m.phase * 57f, m.axis) * m.baseRotation;
                        tr.localPosition = m.basePosition + Vector3.up * (Mathf.Sin(t * 0.8f + m.phase) * 0.02f);
                        break;
                    case ColonyStyle.Float:
                        tr.localRotation = m.baseRotation * Quaternion.Euler(Mathf.Sin(t * 1.1f + m.phase) * 4f, 0f,
                                                                             Mathf.Sin(t * 0.9f + m.phase * 2f) * 5f);
                        tr.localPosition = m.basePosition + Vector3.up * (Mathf.Sin(t * 1.3f + m.phase) * 0.006f);
                        break;
                    case ColonyStyle.Soar:
                    {
                        float a   = m.phase + t * m.speed;
                        var pos   = new Vector3(Mathf.Cos(a) * m.radius, m.basePosition.y + Mathf.Sin(t * 0.5f + m.phase) * 0.04f, Mathf.Sin(a) * m.radius);
                        var ahead = new Vector3(-Mathf.Sin(a), 0f, Mathf.Cos(a)) * Mathf.Sign(m.speed);
                        tr.localPosition = pos;
                        tr.localRotation = Quaternion.LookRotation(ahead) * Quaternion.Euler(0f, 0f, 22f * Mathf.Sign(m.speed));
                        break;
                    }
                    case ColonyStyle.Swim:
                    {
                        float a   = m.phase + t * m.speed;
                        var ahead = new Vector3(-Mathf.Sin(a), 0f, Mathf.Cos(a)) * Mathf.Sign(m.speed);
                        tr.localPosition = new Vector3(Mathf.Cos(a) * m.radius, m.basePosition.y + Mathf.Sin(t * 0.9f + m.phase) * 0.008f, Mathf.Sin(a) * m.radius);
                        tr.localRotation = Quaternion.LookRotation(ahead) * Quaternion.Euler(0f, Mathf.Sin(t * 3f + m.phase * 3f) * 6f, 0f);
                        break;
                    }
                    case ColonyStyle.Swarm:
                    {
                        float p = m.phase;
                        var jitter = new Vector3(Mathf.Sin(t * 2.3f + p) + 0.5f * Mathf.Sin(t * 5.1f + p * 3f),
                                                 Mathf.Sin(t * 1.7f + p * 2f),
                                                 Mathf.Cos(t * 2.9f + p) + 0.5f * Mathf.Cos(t * 4.3f + p * 5f)) * 0.05f;
                        tr.localPosition = m.basePosition + jitter;
                        tr.localRotation = m.baseRotation * Quaternion.Euler(0f, Mathf.Sin(t * 1.9f + p) * 40f, 0f);
                        break;
                    }
                }
            }
        }

        private void PlaceColonies()
        {
            members.Clear();
            if (material == null) material = Resources.Load<Material>("Materials/MapFeatures");
            var rng  = new System.Random(grid.WorldSeed ^ 0x5eed);
            var used = new HashSet<HexCell>();

            foreach (var def in GameDataLoader.Species)
            {
                if (string.IsNullOrEmpty(def.model)) continue;
                var mesh = LoadMesh(def.model);
                if (mesh == null) { Debug.LogWarning($"[SpeciesColonies] No mesh at Resources/{def.model} for {def.id}."); continue; }
                if (!System.Enum.TryParse(def.mapStyle, true, out ColonyStyle style)) style = ColonyStyle.Drift;
                var cell = FindHabitatCell(def, used, rng);
                if (cell == null) { Debug.Log($"[SpeciesColonies] No habitat tile for {def.id}; skipping."); continue; }
                used.Add(cell);
                BuildColony(cell, def, mesh, style, rng);
                Debug.Log($"[SpeciesColonies] Placed {def.commonName} ({style}) at {cell}.");
            }
        }

        private static Mesh LoadMesh(string path)
        {
            var model = Resources.Load<GameObject>(path);
            var filter = model != null ? model.GetComponentInChildren<MeshFilter>() : null;
            return filter != null ? filter.sharedMesh : null;
        }

        // A random tile among the habitat tiles closest to the map centre, where the camera starts.
        // Tiles that already carry a reef, forest or oasis prop, or another species, are a last resort.
        private HexCell FindHabitatCell(SpeciesDefinition def, HashSet<HexCell> used, System.Random rng)
        {
            var candidates = new List<(HexCell cell, float dist)>();
            var center = new Vector2((grid.Width - 1) * 0.5f, (grid.Height - 1) * 0.5f);
            for (int r = 0; r < grid.Height; r++)
            for (int q = 0; q < grid.Width; q++)
            {
                var cell = grid.GetCell(q, r);
                if (cell == null || cell.Terrain == null || cell.IsMountain) continue;
                if (def.habitats == null || !def.habitats.Contains(cell.Terrain.kind.ToString())) continue;
                float dist = Vector2.Distance(new Vector2(q, r), center);
                if (cell.Feature != TerrainFeature.None) dist += 1000f;
                if (used.Contains(cell)) dist += 2000f;
                candidates.Add((cell, dist));
            }
            if (candidates.Count == 0) return null;
            candidates.Sort((a, b) => a.dist.CompareTo(b.dist));
            return candidates[rng.Next(Mathf.Min(5, candidates.Count))].cell;
        }

        private void BuildColony(HexCell cell, SpeciesDefinition def, Mesh mesh, ColonyStyle style, System.Random rng)
        {
            float R(float min, float max) => min + (float)rng.NextDouble() * (max - min);
            var (count, memberSpan, colonyRadius) = Layouts[style];
            if (def.colonySize > 0) count = def.colonySize;
            if (def.mapScale > 0f) memberSpan *= def.mapScale;
            var root = new GameObject($"Colony_{def.id}").transform;
            root.SetParent(cell.transform, false);
            root.localPosition = Vector3.up * cell.SurfaceHeight;

            // Microbes and swarms are sized by their longest dimension; everything else by its
            // footprint, so hanging tentacles or tall poses don't shrink the animal.
            var size = mesh.bounds.size;
            bool anyAxis = style is ColonyStyle.Drift or ColonyStyle.Swarm;
            float meshSpan = anyAxis ? Mathf.Max(size.x, size.y, size.z) : Mathf.Max(size.x, size.z);
            float schoolSpeed = rng.NextDouble() < 0.5 ? 0.18f : -0.18f; // Swim: radians per second

            for (int i = 0; i < count; i++)
            {
                // One member in the middle, the rest scattered around it
                float angle = (i / (float)Mathf.Max(1, count - 1) + R(-0.06f, 0.06f)) * Mathf.PI * 2f;
                float dist  = i == 0 ? 0f : colonyRadius * R(0.55f, 1f);
                float span  = memberSpan * R(0.8f, 1.12f);
                var pos     = new Vector3(Mathf.Cos(angle) * dist, 0f, Mathf.Sin(angle) * dist);
                var member  = new Member
                {
                    style        = style,
                    phase        = R(0f, Mathf.PI * 2f),
                    baseRotation = Quaternion.Euler(0f, R(0f, 360f), 0f),
                };
                switch (style)
                {
                    case ColonyStyle.Drift:
                        pos.y        = span * R(0.35f, 0.5f);
                        member.axis  = new Vector3(R(-1f, 1f), 1f, R(-1f, 1f)).normalized;
                        member.baseRotation = Quaternion.identity;
                        break;
                    case ColonyStyle.Swarm:
                        pos   *= 0.8f;
                        pos.y  = SwarmHeight + R(-0.12f, 0.12f);
                        break;
                    case ColonyStyle.Soar:
                        pos.y         = SoarHeight + R(-0.1f, 0.15f);
                        member.radius = colonyRadius * R(0.6f, 1.1f);
                        member.speed  = R(0.25f, 0.4f) * (rng.NextDouble() < 0.8 ? 1f : -1f);
                        member.phase  = angle;
                        break;
                    case ColonyStyle.Swim:
                        // the whole school circles the same way, about three quarters above the
                        // surface (the opaque tile would hide anything deeper), at slightly different depths
                        pos.y         = (-mesh.bounds.min.y - 0.25f * size.y) * (span / meshSpan) + R(0f, 0.02f);
                        member.radius = i == 0 ? colonyRadius * 0.35f : dist;
                        member.speed  = schoolSpeed * R(0.9f, 1.1f);
                        member.phase  = angle;
                        break;
                }
                member.basePosition = pos;

                var go = new GameObject(def.id);
                go.transform.SetParent(root, false);
                go.transform.localPosition = pos;
                go.transform.localRotation = member.baseRotation;
                go.transform.localScale    = Vector3.one * (span / meshSpan);
                go.AddComponent<MeshFilter>().sharedMesh = mesh;
                var mr = go.AddComponent<MeshRenderer>(); // no collider: clicks reach the hex below
                mr.sharedMaterial = material;
                var block = new MaterialPropertyBlock();
                float v = R(0.92f, 1.06f);
                block.SetColor("_Color", new Color(v, v * R(0.97f, 1.02f), v * R(0.94f, 1.0f)));
                mr.SetPropertyBlock(block);

                member.transform = go.transform;
                members.Add(member);
            }
        }
    }
}
