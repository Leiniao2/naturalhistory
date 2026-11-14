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
    // habitat tiles. Groups are children of their cell, so they follow the east–west wrap and are
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
        private static readonly int FlapId     = Shader.PropertyToID("_Flap");
        private static readonly int FlapRootId = Shader.PropertyToID("_FlapRoot");
        private static readonly int FlapSpanId = Shader.PropertyToID("_FlapSpan");

        private HexGrid grid;
        private Material material;
        private readonly List<Member> members = new();
        private readonly System.Random motionRng = new();

        private class Member
        {
            public Transform transform;
            public ColonyStyle style;
            public Vector3 basePosition;
            public Quaternion baseRotation;
            public Vector3 axis;   // Drift: tumble axis
            public float phase;
            public float speed;    // Soar/Swim: radians per second around the cell (sign = direction)
                                   // Ground: cells per second
            public float radius;   // Soar/Swim: circle radius; Ground: how far it strays from basePosition
            public float span;     // size on the map, in cells

            // Ground wandering
            public ColonyGait gait;
            public List<Member> colony; // to keep out of each other's way
            public Vector3 position, target;
            public float heading;       // yaw in degrees
            public bool moving;
            public float restUntil;

            // Wing beat
            public MeshRenderer renderer;
            public MaterialPropertyBlock block;
            public float flapRate;      // radians per second; 0 = no flapping
            public float flapAmplitude;
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
            float t = Time.time, dt = Time.deltaTime;
            foreach (var m in members)
            {
                if (m.transform == null) continue; // cell destroyed by a regenerate that hasn't re-placed yet
                var tr = m.transform;
                if (m.flapRate > 0f) Flap(m, t);
                switch (m.style)
                {
                    case ColonyStyle.Ground:
                        Wander(m, t, dt);
                        break;
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

        private static void Flap(Member m, float t)
        {
            // soarers glide most of the time and give a few slow beats every several seconds
            float burst = m.style == ColonyStyle.Soar ? Mathf.SmoothStep(0f, 1f, (Mathf.Sin(t * 0.5f + m.phase) - 0.35f) * 3f) : 1f;
            m.block.SetFloat(FlapId, Mathf.Sin(t * m.flapRate + m.phase) * m.flapAmplitude * burst);
            m.renderer.SetPropertyBlock(m.block);
        }

        // Rests a few seconds, turns towards a nearby spot and walks, hops or slithers there.
        private void Wander(Member m, float t, float dt)
        {
            if (!m.moving)
            {
                if (t >= m.restUntil) PickTarget(m);
                // idle: glance around a little
                m.transform.localPosition = m.position;
                m.transform.localRotation = Quaternion.Euler(0f, m.heading + Mathf.Sin(t * 0.4f + m.phase) * 5f, 0f);
                return;
            }

            var to = m.target - m.position;
            to.y = 0f;
            float dist = to.magnitude;
            float turn = Mathf.DeltaAngle(m.heading, Mathf.Atan2(to.x, to.z) * Mathf.Rad2Deg);
            m.heading += Mathf.Clamp(turn, -70f * dt, 70f * dt);
            // turn mostly on the spot, then set off
            if (Mathf.Abs(turn) < 30f)
                m.position += Quaternion.Euler(0f, m.heading, 0f) * Vector3.forward * Mathf.Min(m.speed * dt, dist);
            if (dist < 0.005f)
            {
                m.moving    = false;
                m.restUntil = t + (float)(2.0 + motionRng.NextDouble() * 6.0);
            }

            // gait: a small bob and sway while walking, bounds for hoppers, an S-wag for snakes
            float step = t * 6f / Mathf.Sqrt(Mathf.Max(m.span, 0.3f)) + m.phase; // big animals take slower strides
            float lift = 0f, roll = 0f, yaw = 0f;
            switch (m.gait)
            {
                case ColonyGait.Walk:    lift = Mathf.Abs(Mathf.Sin(step)) * 0.015f; roll = Mathf.Sin(step) * 2f; break;
                case ColonyGait.Hop:     lift = Mathf.Abs(Mathf.Sin(step * 0.5f)) * 0.18f; break;
                case ColonyGait.Slither: yaw = Mathf.Sin(step * 0.6f) * 14f; break;
            }
            m.transform.localPosition = m.position + Vector3.up * (lift * m.span);
            m.transform.localRotation = Quaternion.Euler(0f, m.heading + yaw, roll);
        }

        // A random spot around the animal's home, not too close to where its colony-mates are or are heading.
        private void PickTarget(Member m)
        {
            for (int attempt = 0; attempt < 6; attempt++)
            {
                float a = (float)(motionRng.NextDouble() * Mathf.PI * 2.0);
                float r = m.radius * Mathf.Sqrt((float)motionRng.NextDouble());
                var spot = m.basePosition + new Vector3(Mathf.Cos(a) * r, 0f, Mathf.Sin(a) * r);
                bool clear = true;
                foreach (var other in m.colony)
                {
                    float room = (m.span + other.span) * 0.4f;
                    if (other != m && (Vector3.Distance(spot, other.position) < room || Vector3.Distance(spot, other.target) < room))
                    {
                        clear = false;
                        break;
                    }
                }
                if (!clear) continue;
                m.target = spot;
                m.moving = true;
                return;
            }
            m.restUntil = Time.time + 1f; // boxed in; try again shortly
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

            // Microbes and swarms are sized by their longest dimension; everything else by its
            // footprint, so hanging tentacles or tall poses don't shrink the animal.
            var size = mesh.bounds.size;
            bool anyAxis = style is ColonyStyle.Drift or ColonyStyle.Swarm;
            float meshSpan = anyAxis ? Mathf.Max(size.x, size.y, size.z) : Mathf.Max(size.x, size.z);
            float schoolSpeed = rng.NextDouble() < 0.5 ? 0.18f : -0.18f; // Swim: radians per second
            if (!System.Enum.TryParse(def.mapGait, true, out ColonyGait gait)) gait = ColonyGait.Walk;
            var colony = new List<Member>();
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
                var member  = new Member
                {
                    style        = style,
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
                        member.gait      = gait;
                        member.colony    = colony;
                        member.radius    = Mathf.Clamp(span * 0.3f, 0.06f, 0.25f);
                        member.speed     = Mathf.Clamp(span * 0.15f, 0.03f, 0.15f) * (gait == ColonyGait.Hop ? 2f : 1f);
                        member.heading   = member.baseRotation.eulerAngles.y;
                        member.position  = member.target = pos;
                        member.restUntil = Time.time + R(0f, 4f);
                        colony.Add(member);
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
                mr.SetPropertyBlock(block);

                member.transform = go.transform;
                member.renderer  = mr;
                member.block     = block;
                members.Add(member);
            }
            return memberSpan;
        }
    }
}
