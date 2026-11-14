using System.Collections.Generic;
using NaturalHistory.Data;
using UnityEngine;

namespace NaturalHistory.World
{
    // How a species' group looks and moves on its tile (species.json "mapStyle").
    public enum ColonyStyle
    {
        Drift, // micro-organisms: a cluster hovering over the tile, slowly tumbling and bobbing
        Fixed, // doesn't move: corals, sponges, mounds, and small animals modelled on a perch
        Float, // sits on the water surface (pivot at the waterline), rocking gently
        Ground,// stands on the tile (pivot at the feet) and wanders around its spot
        Soar,  // circles high above the tile, banked into the turn
        Swarm, // a jittery cloud of small fliers
        Swim,  // a school circling just above the water (tiles are opaque, so they can't go under it)
    }

    // How a Ground animal moves between spots (species.json "mapGait").
    public enum ColonyGait { Walk, Hop, Slither }

    // Shows a group of every species that has a map model (species.json "model") on one of its
    // habitat tiles, as a ColonyGroup that can be ordered to move or attack (click it, then a marked
    // neighbouring tile). Groups are children of their cell, so they follow the east–west wrap and are
    // destroyed when the map regenerates. Models face +Z with their pivot as described in
    // tools/blender/nh_model.py; they are rescaled from their mesh bounds, so file units don't matter.
    public class SpeciesColonies : MonoBehaviour
    {
        // count, size (longest dimension, in cells), spread radius from the cell centre
        private static readonly Dictionary<ColonyStyle, (int count, float span, float radius)> Layouts = new()
        {
            [ColonyStyle.Drift]  = (7, 0.32f, 0.36f),
            [ColonyStyle.Fixed]  = (3, 0.34f, 0.30f),
            [ColonyStyle.Float]  = (4, 0.26f, 0.32f),
            [ColonyStyle.Ground] = (3, 0.34f, 0.30f),
            [ColonyStyle.Soar]   = (3, 0.42f, 0.45f),
            [ColonyStyle.Swarm]  = (9, 0.11f, 0.22f),
            [ColonyStyle.Swim]   = (5, 0.26f, 0.32f),
        };

        // Map size grows with real body size (sqrt of length in metres), so a T. rex towers over a
        // lion; small animals keep their style's minimum size so they stay visible.
        private const float SizeSpanPerSqrtMetre = 0.8f;
        private const float MaxSpan              = 3f;   // in cells
        private const float ReserveSpan          = 0.9f; // bigger than this: keep neighbouring tiles free

        private const float SoarHeight  = 0.75f;
        private const float SwarmHeight = 0.35f;

        // Wing/fin beat amplitude (radians) by style; soarers only flap in short bursts between glides
        private const float SoarFlap  = 0.45f;
        private const float SwarmFlap = 0.6f;
        private const float SwimFlap  = 0.35f;
        private static readonly int FlapRootId = Shader.PropertyToID("_FlapRoot");
        private static readonly int FlapSpanId = Shader.PropertyToID("_FlapSpan");
        private static readonly int StrideLegsId = Shader.PropertyToID("_StrideLegs");
        private static readonly int StrideModeId = Shader.PropertyToID("_StrideMode");

        // Leg swing at full stride (radians); hoppers kick both legs together, further
        private const float WalkStride = 0.42f;
        private const float HopStride  = 0.6f;

        public static SpeciesColonies Instance { get; private set; }

        private HexGrid grid;
        private Material material;
        private readonly List<ColonyGroup> groups = new();
        private readonly Dictionary<HexCell, ColonyGroup> occupants = new();

        // Ordering a group around: click it, then click a marked neighbouring tile to move there,
        // or a marked tile holding another group to attack it.
        private ColonyGroup selected;
        private readonly List<HexCell> marked = new();
        private int clickFrame = -1;

        public ColonyGroup Selected => selected;
        public IReadOnlyList<ColonyGroup> Groups => groups;
        public ColonyGroup GroupAt(HexCell cell) => cell != null && occupants.TryGetValue(cell, out var g) ? g : null;

        // True if this click is (or was just) about colonies, so other click handlers (the player
        // ball) should leave it alone. Safe to call before or after this component handles the click.
        public bool HandlesClick(HexCell cell) =>
            clickFrame == Time.frameCount || selected != null || GroupAt(cell) != null;

        // Spawns the component in any scene that has a HexGrid, so Game.unity doesn't need editing.
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Bootstrap()
        {
            if (FindAnyObjectByType<HexGrid>() == null || FindAnyObjectByType<SpeciesColonies>() != null) return;
            new GameObject("SpeciesColonies").AddComponent<SpeciesColonies>();
        }

        private void Awake() => Instance = this;

        private void Start()
        {
            grid = HexGrid.Instance;
            if (grid == null) { Debug.LogWarning("[SpeciesColonies] No HexGrid in scene."); return; }
            if (GameDataLoader.Species == null) GameDataLoader.Initialize();

            grid.Generated += PlaceColonies;
            if (grid.IsGenerated) PlaceColonies();
            CellSelector.CellClicked += OnCellClicked;
        }

        private void OnDestroy()
        {
            if (grid != null) grid.Generated -= PlaceColonies;
            CellSelector.CellClicked -= OnCellClicked;
            if (Instance == this) Instance = null;
        }

        private void OnCellClicked(HexCell cell)
        {
            if (selected != null)
            {
                clickFrame = Time.frameCount;
                var group = selected;
                if (marked.Contains(cell))
                {
                    var other = GroupAt(cell);
                    var from  = group.Cell;
                    Select(null);
                    if (other != null) group.Attack(cell);
                    else if (group.MoveTo(cell))
                    {
                        occupants.Remove(from);
                        occupants[group.Cell] = group;
                    }
                    return;
                }
                var clicked = GroupAt(cell);
                Select(clicked != group && clicked != null && clicked.CanMove && !clicked.IsBusy ? clicked : null);
                return;
            }

            var g = GroupAt(cell);
            if (g == null) return;
            clickFrame = Time.frameCount;
            if (g.CanMove && !g.IsBusy) Select(g);
        }

        // Marks the tiles the group can go to: green to move, red to attack another group there.
        private void Select(ColonyGroup group)
        {
            foreach (var c in marked) if (c != null) c.SetGroupTarget(HexCell.GroupTarget.None);
            marked.Clear();
            selected = group;
            if (group == null) return;
            foreach (var n in grid.GetNeighbors(group.Cell))
            {
                if (!group.CanEnter(n)) continue;
                marked.Add(n);
                n.SetGroupTarget(GroupAt(n) != null ? HexCell.GroupTarget.Attack : HexCell.GroupTarget.Move);
            }
        }

        private void PlaceColonies()
        {
            Select(null);
            groups.Clear();
            occupants.Clear();
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
                // big animals spill over onto the neighbouring tiles; keep other colonies off them
                if (BuildColony(cell, def, mesh, style, rng) > ReserveSpan)
                    foreach (var n in grid.GetNeighbors(cell)) used.Add(n);
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

        // Returns the size of one member (in cells).
        private float BuildColony(HexCell cell, SpeciesDefinition def, Mesh mesh, ColonyStyle style, System.Random rng)
        {
            float R(float min, float max) => min + (float)rng.NextDouble() * (max - min);
            var (count, memberSpan, colonyRadius) = Layouts[style];
            if (def.colonySize > 0) count = def.colonySize;
            float sizeSpan = SizeSpanPerSqrtMetre * Mathf.Sqrt(Mathf.Max(def.sizeCm, 0f) / 100f);
            memberSpan = Mathf.Min(Mathf.Max(memberSpan, sizeSpan), MaxSpan);
            if (def.mapScale > 0f) memberSpan *= def.mapScale; // per-model framing (tall perch, wide web...)
            colonyRadius = Mathf.Max(colonyRadius, memberSpan * 0.7f); // big animals need room
            var root = new GameObject($"Colony_{def.id}").transform;
            root.SetParent(cell.transform, false);
            root.localPosition = Vector3.up * cell.SurfaceHeight;
            if (!System.Enum.TryParse(def.mapGait, true, out ColonyGait gait)) gait = ColonyGait.Walk;
            var group = root.gameObject.AddComponent<ColonyGroup>();
            group.Init(def, style, gait, cell, memberSpan);
            groups.Add(group);
            occupants[cell] = group;

            // Microbes and swarms are sized by their longest dimension; everything else by its
            // footprint, so hanging tentacles or tall poses don't shrink the animal.
            var size = mesh.bounds.size;
            bool anyAxis = style is ColonyStyle.Drift or ColonyStyle.Swarm;
            float meshSpan = anyAxis ? Mathf.Max(size.x, size.y, size.z) : Mathf.Max(size.x, size.z);
            float schoolSpeed = rng.NextDouble() < 0.5 ? 0.18f : -0.18f; // Swim: radians per second
            float halfSpan = Mathf.Max(-mesh.bounds.min.x, mesh.bounds.max.x);
            float flapAmplitude = style switch
            {
                ColonyStyle.Soar  => SoarFlap,
                ColonyStyle.Swarm => SwarmFlap,
                ColonyStyle.Swim  => SwimFlap,
                _                 => 0f,
            };

            for (int i = 0; i < count; i++)
            {
                // One member in the middle, the rest scattered around it
                float angle = (i / (float)Mathf.Max(1, count - 1) + R(-0.06f, 0.06f)) * Mathf.PI * 2f;
                float dist  = i == 0 ? 0f : colonyRadius * R(0.55f, 1f);
                float span  = memberSpan * R(0.8f, 1.12f);
                var pos     = new Vector3(Mathf.Cos(angle) * dist, 0f, Mathf.Sin(angle) * dist);
                var member  = new ColonyGroup.Member
                {
                    span         = span,
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
                        pos.y         = SoarHeight + span * 0.3f + R(-0.1f, 0.15f); // big wings fly higher
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
                    case ColonyStyle.Ground:
                        // big animals amble slowly over a wider patch; small ones scurry about their spot
                        member.radius    = Mathf.Clamp(span * 0.3f, 0.06f, 0.25f);
                        member.speed     = Mathf.Clamp(span * 0.15f, 0.03f, 0.15f) * (gait == ColonyGait.Hop ? 2f : 1f);
                        member.heading   = member.baseRotation.eulerAngles.y;
                        member.position  = member.target = pos;
                        member.restUntil = Time.time + R(0f, 4f);
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
                if (def.wingBeat > 0f && flapAmplitude > 0f)
                {
                    block.SetFloat(FlapRootId, (def.wingRoot > 0f ? def.wingRoot : 0.15f) * halfSpan);
                    block.SetFloat(FlapSpanId, halfSpan);
                    member.flapRate      = def.wingBeat * R(0.9f, 1.1f) * Mathf.PI * 2f;
                    member.flapAmplitude = flapAmplitude;
                }
                if (style == ColonyStyle.Ground && gait != ColonyGait.Slither)
                {
                    // everything below the hips swings as legs (see MapFeatureFlap.cginc)
                    var b      = mesh.bounds;
                    float hipY = b.min.y + (def.mapHip > 0f ? def.mapHip : 0.45f) * b.size.y;
                    block.SetVector(StrideLegsId, new Vector4(hipY, hipY - b.min.y, b.min.z, b.max.z));
                    block.SetVector(StrideModeId, new Vector4(def.mapLegs > 0 ? def.mapLegs : 2, gait == ColonyGait.Hop ? 1f : 0f, 0f, 0f));
                    member.strideAmplitude = gait == ColonyGait.Hop ? HopStride : WalkStride;
                    member.legLength       = (hipY - b.min.y) * (span / meshSpan);
                }
                mr.SetPropertyBlock(block);

                member.transform = go.transform;
                member.renderer  = mr;
                member.block     = block;
                group.AddMember(member);
            }
            return memberSpan;
        }
    }
}
