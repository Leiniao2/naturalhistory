using System.Collections.Generic;
using UnityEngine;

namespace NaturalHistory.World
{
    // The shapes a volcano prop can take, so no two volcanic peaks look alike
    public enum VolcanoForm
    {
        Strato,       // steep concave cone, lava lake, lava down the gullies, a side cone
        Snowcapped,   // tall, smooth and symmetrical with a snowy summit (Fuji); a quiet crater
        Shield,       // stepped lava shield: a broad apron of old flows, a summit shield with a glowing pit crater, rift spatter cones (Hawaii)
        CinderField,  // a steep scoria cone with a deep bowl, little cones beside it, black lava field
        Caldera,      // a collapsed summit: jagged ring of cliffs round a crater lake with an island cone
        Twin,         // two cones grown together, one active, one dormant
        Somma,        // a young cone inside the breached rim of an older, bigger one (Vesuvius)
        LavaDome,     // a cluster of bulging domes of stiff lava bristling with spines, no crater
        Fissure,      // a row of spatter cones along a glowing rift (Iceland)
    }

    public static partial class MapFeatureMeshes
    {
        static readonly Color Scoria     = new(0.40f, 0.21f, 0.16f);
        static readonly Color Dacite     = new(0.50f, 0.45f, 0.43f);
        static readonly Color CraterLake = new(0.16f, 0.50f, 0.60f);
        static readonly Color OldSlope   = new(0.40f, 0.42f, 0.30f); // an old, weathered rim, part grown over

        // Where each volcano mesh's active vent is (in the mesh's space), for its smoke and eruptions
        static readonly Dictionary<Mesh, Vector3> vents = new();

        public static bool TryGetVent(Mesh mesh, out Vector3 vent)
        {
            vent = default;
            return mesh != null && vents.TryGetValue(mesh, out vent);
        }

        static void RegisterVent(Mesh mesh, Vector3 vent)
        {
            if (vents.Count > 512)
            {
                var gone = new List<Mesh>();
                foreach (var m in vents.Keys) if (m == null) gone.Add(m);
                foreach (var m in gone) vents.Remove(m);
            }
            vents[mesh] = vent;
        }

        // A random form; snowy cones where it is cold, none under the sea
        public static VolcanoForm PickVolcanoForm(System.Random rng, bool cold, bool underwater)
        {
            var forms = new List<(VolcanoForm form, float weight)>
            {
                (VolcanoForm.Strato, 1.2f), (VolcanoForm.Shield, 1f), (VolcanoForm.CinderField, 0.9f),
                (VolcanoForm.Caldera, 0.8f), (VolcanoForm.Twin, 0.9f), (VolcanoForm.Somma, 0.7f),
                (VolcanoForm.LavaDome, 0.7f), (VolcanoForm.Fissure, 0.7f),
            };
            if (!underwater) forms.Add((VolcanoForm.Snowcapped, cold ? 3f : 0.7f));
            float total = 0f;
            foreach (var f in forms) total += f.weight;
            float pick = Range(rng, 0f, total);
            foreach (var f in forms) { pick -= f.weight; if (pick <= 0f) return f.form; }
            return VolcanoForm.Strato;
        }

        enum Crater { Lava, Water, Dry, None }

        // One cone of a volcano. Everything is in the volcano mesh's space.
        sealed class Cone
        {
            public Vector3 at;
            public float radius, height, top;
            public int sides = 40, rings = 14;
            public float ridge = 0.22f, jitter = 0.05f, profile = 1.7f, rough = 1f;
            public Crater crater = Crater.Lava;
            public float craterDepth = 0.12f, craterInset = 0.6f;
            public int streams;
            public float streamReach = 0.4f;    // how far down the slope lava streams run (0..1)
            public float snowline = 2f;         // height (0..1) above which steep-enough faces are snow
            public bool parasite;
            public Color ash = Ash, rock = Basalt;
            public int blocks = 12;
            public float breach, breachAt;      // how much of the rim one side has lost (0..1), and which way (degrees)
            public Color? cover;                // if set, what grows on every gentle face (karst towers' jungle)
        }

        // Builds a cone; returns its vent (the middle of its crater floor, or its summit).
        static Vector3 AddVolcanoCone(Builder b, System.Random rng, float size, Cone c, System.Func<Vector2, float> groundAt)
        {
            int sides = c.sides, rings = c.rings;
            float h = c.height;
            var below = c.at + Vector3.down * Mathf.Max(h, 0.2f * size);
            var g = ConeGrid(rng, c.at, c.radius, h, c.top, sides, rings, c.ridge, c.jitter, c.profile, out var spokes);

            // a breached rim: one side worn or blown away, lower the further up the slope
            if (c.breach > 0f)
                for (int k = 1; k <= rings; k++)
                for (int i = 0; i < sides; i++)
                {
                    var p = g[k, i];
                    float a = Mathf.Atan2(p.x - c.at.x, p.z - c.at.z) * Mathf.Rad2Deg;
                    float w = Mathf.Pow(Mathf.Max(0f, Mathf.Cos(Mathf.DeltaAngle(a, c.breachAt) * Mathf.Deg2Rad)), 3f);
                    p.y = c.at.y + (p.y - c.at.y) * (1f - c.breach * w * (k / (float)rings));
                    g[k, i] = p;
                }
            if (groundAt != null)
                for (int i = 0; i < sides; i++)
                    g[0, i].y = Mathf.Min(g[0, i].y, groundAt(new Vector2(g[0, i].x, g[0, i].z)) - 0.01f);

            // rough, faceted slopes: two octaves of noise push the flanks in and out and lift or sink
            // them, strongest low down; the rim stays fairly true for the crater
            float seed = Range(rng, 0f, 100f);
            for (int k = 1; k <= rings; k++)
            {
                float t = k / (float)rings;
                float rough = Mathf.Lerp(1f, 0.35f, t) * c.rough;
                for (int i = 0; i < sides; i++)
                {
                    float a  = i / (float)sides * Mathf.PI * 2f;
                    float ca = Mathf.Cos(a), sa = Mathf.Sin(a);
                    float n1 = Mathf.PerlinNoise(seed + ca * 2.2f + t * 2.5f, seed * 0.7f + sa * 2.2f) - 0.5f;
                    float n2 = Mathf.PerlinNoise(seed * 1.3f + ca * 6.5f + t * 8f, seed + sa * 6.5f + t * 5f) - 0.5f;
                    var p = g[k, i];
                    var radial = new Vector3(p.x - c.at.x, 0f, p.z - c.at.z);
                    if (radial.sqrMagnitude > 1e-8f)
                        p += radial.normalized * (n1 * 0.09f + n2 * 0.05f) * c.radius * 1.7f * rough;
                    p.y += (n1 * 0.03f + n2 * 0.045f + Range(rng, -0.012f, 0.012f)) * h * rough;
                    g[k, i] = p;
                }
            }

            // flat-shaded facets: ash and scree on gentle ground, bare rock on steep faces and toward
            // the summit, in noisy patches; snow above the snowline on all but the steepest faces
            Color Face(Vector3 p0, Vector3 p1, Vector3 p2)
            {
                var m  = (p0 + p1 + p2) / 3f;
                float t  = Mathf.Clamp01((m.y - c.at.y) / Mathf.Max(h, 1e-4f));
                float up = FaceUp(p0, p1, p2, below);
                float patch = Mathf.PerlinNoise(seed + m.x / size * 6f, seed - m.z / size * 6f);
                var ground = t < 0.25f ? c.ash : Color.Lerp(c.ash, c.rock, Mathf.InverseLerp(0.25f, 0.7f, t + (patch - 0.5f) * 0.3f));
                var col = Color.Lerp(ground, c.rock * 0.85f, Mathf.InverseLerp(0.75f, 0.35f, up));
                if (patch > 0.68f && up > 0.6f) col = Color.Lerp(col, c.ash * 1.15f, 0.5f);
                if (t + (patch - 0.5f) * 0.25f > c.snowline && up > 0.4f) col = Color.Lerp(Snow, Snow * 0.88f, patch);
                if (c.cover is Color cov && up > 0.62f) col = Color.Lerp(cov, cov * 0.8f, patch);
                return Shade(rng, col, 0.08f) * Mathf.Lerp(0.82f, 1.04f, up);
            }
            for (int k = 0; k < rings; k++)
            for (int i = 0; i < sides; i++)
            {
                int j = (i + 1) % sides;
                b.AddTri(g[k, i], g[k, j], g[k + 1, j], Face(g[k, i], g[k, j], g[k + 1, j]), below);
                b.AddTri(g[k, i], g[k + 1, j], g[k + 1, i], Face(g[k, i], g[k + 1, j], g[k + 1, i]), below);
            }

            // blocks of lava and tephra strewn over the flanks
            for (int n = c.blocks; n > 0; n--)
            {
                int k = rng.Next(1, Mathf.Max(2, rings * 3 / 4));
                int i = rng.Next(sides);
                var at = Vector3.Lerp(g[k, i], g[k, (i + 1) % sides], Range(rng, 0f, 1f));
                AddRock(b, rng, at, c.radius * Range(rng, 0.02f, 0.05f), rng.NextDouble() < 0.6 ? c.rock : c.ash);
            }

            float rimY = 0f;
            for (int i = 0; i < sides; i++) rimY += g[rings, i].y / sides;
            var centre = new Vector3(c.at.x, rimY, c.at.z);
            if (c.crater == Crater.None)
            {
                // a closed, lumpy summit
                var apex = centre + Vector3.up * c.top * 0.6f;
                for (int i = 0; i < sides; i++)
                    b.AddTri(g[rings, i], g[rings, (i + 1) % sides], apex, Shade(rng, c.rock, 0.08f), below);
                return apex;
            }

            // crater: an inner wall down to a lava lake, a crater lake or a dry floor
            float floorY = rimY - c.craterDepth * h;
            var floor = new Vector3[sides];
            for (int i = 0; i < sides; i++)
            {
                var p = g[rings, i];
                floor[i] = new Vector3(c.at.x + (p.x - c.at.x) * c.craterInset, floorY, c.at.z + (p.z - c.at.z) * c.craterInset);
            }
            var fill = c.crater switch { Crater.Lava => Lava, Crater.Water => CraterLake, _ => c.ash * 0.75f };
            var mid = new Vector3(c.at.x, floorY, c.at.z);
            for (int i = 0; i < sides; i++)
            {
                int j = (i + 1) % sides;
                var outside = (g[rings, i] + g[rings, j]) * 0.5f;
                outside = new Vector3(c.at.x + (outside.x - c.at.x) * 3f, floorY, c.at.z + (outside.z - c.at.z) * 3f);
                b.AddQuad(g[rings, i], g[rings, j], floor[j], floor[i], Shade(rng, c.rock * 0.7f, 0.04f), outside);
                b.AddTri(mid, floor[i], floor[j], fill * Range(rng, 0.9f, 1.08f), mid + Vector3.down);
            }

            // lava streams follow the deepest gullies from the rim partway down the slope
            if (c.crater == Crater.Lava && c.streams > 0)
            {
                var order = new List<int>();
                for (int i = 0; i < sides; i++) order.Add(i);
                order.Sort((x, y) => spokes[x].CompareTo(spokes[y]));
                for (int n = 0; n < c.streams; n++)
                {
                    int end = Mathf.Clamp(Mathf.RoundToInt(rings * (1f - c.streamReach * Range(rng, 0.7f, 1.15f))), 0, rings - 1);
                    AddLavaStream(b, rng, g, order[n * sides / (c.streams + 1)], rings, end, size, below);
                }
            }

            // a parasitic cone low on a flank
            if (c.parasite)
            {
                float a = Range(rng, 0f, Mathf.PI * 2f);
                var dir = new Vector3(Mathf.Sin(a), 0f, Mathf.Cos(a));
                var pc  = c.at + dir * c.radius * 0.72f + Vector3.up * h * Mathf.Pow(0.25f, c.profile);
                AddVolcanoCone(b, rng, size, new Cone
                {
                    at = pc, radius = 0.2f * c.radius, height = 0.22f * c.radius, top = 0.07f * c.radius, sides = 10, rings = 3,
                    ridge = 0.1f, jitter = 0.06f, profile = 1.2f, rough = 0.4f, crater = Crater.Dry, craterDepth = 0.4f,
                    ash = c.ash, rock = c.rock, blocks = 0,
                }, null);
            }
            return mid;
        }

        // A volcano of the given form (or a random one) filling the tile. heightScale scales its
        // height; groundAt gives the tile surface height at a point, so the base follows it. Its
        // active vent is registered for the smoke and eruptions (TryGetVent).
        public static Mesh CreateVolcano(System.Random rng, float size, float heightScale, System.Func<Vector2, float> groundAt = null,
                                         VolcanoForm? form = null, bool underwater = false)
        {
            var f = form ?? PickVolcanoForm(rng, false, underwater);
            if (underwater && f == VolcanoForm.Snowcapped) f = VolcanoForm.Strato;
            var b = new Builder();
            float h = size * Range(rng, 0.8f, 1.0f) * heightScale;
            float turn = Range(rng, 0f, 360f);
            Vector3 Along(float x, float z) => Quaternion.Euler(0f, turn, 0f) * new Vector3(x, 0f, z) * size;
            float GroundY(Vector3 p) => groundAt != null ? groundAt(new Vector2(p.x, p.z)) : 0f;
            var lake = underwater ? Crater.Dry : Crater.Water;
            Vector3 vent;
            bool boulders = true;

            switch (f)
            {
                case VolcanoForm.Snowcapped:
                    vent = AddVolcanoCone(b, rng, size, new Cone
                    {
                        radius = 0.62f * size, height = h * 1.15f, top = 0.09f * size, profile = 2.1f, ridge = 0.14f,
                        crater = Crater.Dry, craterDepth = 0.05f, snowline = 0.55f, blocks = 8,
                    }, groundAt);
                    break;

                case VolcanoForm.Shield:
                {
                    // A stepped lava shield rather than a flat pancake: a broad, rugged apron of old
                    // flows ending in a wide shoulder, a steeper summit shield on it with a glowing pit
                    // crater, spatter cones along a rift on the lower flank, and tongues of fresh black lava
                    float shoulder = h * 0.3f;
                    AddVolcanoCone(b, rng, size, new Cone
                    {
                        radius = 0.82f * size, height = shoulder, top = 0.42f * size, sides = 44, rings = 10, profile = 0.9f,
                        ridge = 0.16f, jitter = 0.06f, rough = 1f, crater = Crater.None, blocks = 8,
                    }, groundAt);
                    vent = AddVolcanoCone(b, rng, size, new Cone
                    {
                        at = Vector3.up * (shoulder - 0.012f * size), radius = 0.46f * size, height = h * 0.34f, top = 0.15f * size,
                        sides = 36, rings = 10, profile = 1.3f, ridge = 0.16f, jitter = 0.05f, rough = 1f,
                        crater = Crater.Lava, craterDepth = 0.35f, craterInset = 0.7f,
                        streams = rng.Next(2, 4), streamReach = 0.85f, blocks = 6,
                    }, null);
                    // a rift of little spatter cones on the apron
                    float riftAt = Range(rng, 0f, Mathf.PI * 2f);
                    for (int i = rng.Next(2, 4); i > 0; i--)
                    {
                        float a = riftAt + (i - 1.5f) * 0.32f;
                        var p = new Vector3(Mathf.Sin(a), 0f, Mathf.Cos(a)) * Range(rng, 0.5f, 0.62f) * size;
                        p.y = Mathf.Lerp(shoulder, 0f, Mathf.InverseLerp(0.42f, 0.82f, p.magnitude / size)) + GroundY(p) * 0.5f;
                        AddVolcanoCone(b, rng, size, new Cone
                        {
                            at = p, radius = Range(rng, 0.07f, 0.11f) * size, height = h * Range(rng, 0.08f, 0.14f), top = 0.03f * size,
                            sides = 12, rings = 4, profile = 1.1f, ridge = 0.1f, rough = 0.5f, crater = Crater.Lava,
                            craterDepth = 0.25f, blocks = 1,
                        }, null);
                    }
                    // fresh black lava spilling over the apron, one tongue still glowing at its snout
                    float away = riftAt + Mathf.PI * Range(rng, 0.6f, 1.4f);
                    for (int i = 0; i < 8; i++)
                    {
                        float d = 0.44f + i * 0.05f;
                        float a = away + Mathf.Sin(i * 1.7f) * 0.18f;
                        var p = new Vector3(Mathf.Sin(a), 0f, Mathf.Cos(a)) * d * size;
                        p.y = Mathf.Lerp(shoulder, 0f, Mathf.InverseLerp(0.42f, 0.82f, d)) + 0.004f * size;
                        AddBlob(b, rng, p, size * Range(rng, 0.05f, 0.08f), 0.2f, 0, i >= 6 ? LavaCool : Shade(rng, Basalt, 0.08f), angular: true);
                    }
                    boulders = false;
                    break;
                }

                case VolcanoForm.CinderField:
                {
                    var at = Along(Range(rng, -0.08f, 0.08f), Range(rng, -0.08f, 0.08f));
                    vent = AddVolcanoCone(b, rng, size, new Cone
                    {
                        at = at, radius = 0.32f * size, height = h * 0.36f, top = 0.17f * size, sides = 32, rings = 10,
                        profile = 1.05f, ridge = 0.06f, jitter = 0.03f, rough = 0.4f, crater = Crater.Dry,
                        craterDepth = 0.4f, craterInset = 0.45f, ash = Scoria, rock = Scoria * 0.75f, blocks = 6,
                    }, groundAt);
                    // little cones beside it
                    for (int i = rng.Next(1, 3); i > 0; i--)
                    {
                        var p = Along(Mathf.Sin(i * 2.3f + turn) * 0.5f, Mathf.Cos(i * 2.3f + turn) * 0.5f);
                        p.y = GroundY(p);
                        AddVolcanoCone(b, rng, size, new Cone
                        {
                            at = p, radius = Range(rng, 0.1f, 0.15f) * size, height = h * Range(rng, 0.1f, 0.16f), top = 0.06f * size,
                            sides = 14, rings = 4, profile = 1.1f, ridge = 0.08f, rough = 0.3f, crater = Crater.Dry,
                            craterDepth = 0.35f, craterInset = 0.5f, ash = Scoria * 1.1f, rock = Scoria * 0.8f, blocks = 2,
                        }, groundAt);
                    }
                    // a black lava field spreading from the main cone, still glowing at its snout
                    float away = Range(rng, 0f, Mathf.PI * 2f);
                    for (int i = 0; i < 9; i++)
                    {
                        float d = 0.26f + i * 0.06f;
                        var p = at + new Vector3(Mathf.Sin(away + Mathf.Sin(i * 1.3f) * 0.25f), 0f, Mathf.Cos(away + Mathf.Sin(i * 1.3f) * 0.25f)) * d * size;
                        p.y = GroundY(p);
                        AddBlob(b, rng, p, size * Range(rng, 0.07f, 0.1f), 0.18f, 0, i >= 7 ? LavaCool : Shade(rng, Basalt, 0.08f), angular: true);
                    }
                    break;
                }

                case VolcanoForm.Caldera:
                {
                    // the rim: a broad, low, jagged ring; its "crater" is the caldera, flooded
                    var floorVent = AddVolcanoCone(b, rng, size, new Cone
                    {
                        radius = 0.78f * size, height = h * 0.42f, top = 0.46f * size, sides = 48, profile = 1.25f, ridge = 0.28f,
                        jitter = 0.07f, crater = lake, craterDepth = 0.5f, craterInset = 0.93f, blocks = 10,
                        ash = Color.Lerp(Ash, OldSlope, underwater ? 0f : 0.35f),
                    }, groundAt);
                    // a young cone rising out of the lake
                    vent = AddVolcanoCone(b, rng, size, new Cone
                    {
                        at = floorVent + Along(Range(rng, -0.12f, 0.12f), Range(rng, -0.12f, 0.12f)) - Vector3.up * 0.01f,
                        radius = 0.15f * size, height = h * 0.3f, top = 0.045f * size, sides = 16, rings = 5, profile = 1.2f,
                        ridge = 0.1f, rough = 0.5f, crater = Crater.Dry, craterDepth = 0.15f, blocks = 2,
                    }, null);
                    boulders = false;
                    break;
                }

                case VolcanoForm.Twin:
                {
                    // two cones side by side whose flanks merge into a saddle: the taller one active
                    vent = AddVolcanoCone(b, rng, size, new Cone
                    {
                        at = Along(-0.2f, Range(rng, -0.06f, 0.06f)), radius = 0.44f * size, height = h, top = 0.11f * size,
                        crater = Crater.Lava, streams = 1, blocks = 8,
                    }, groundAt);
                    bool snowy = !underwater && rng.NextDouble() < 0.5;
                    AddVolcanoCone(b, rng, size, new Cone
                    {
                        at = Along(0.25f, Range(rng, -0.06f, 0.06f)), radius = 0.38f * size, height = h * Range(rng, 0.65f, 0.8f),
                        top = 0.08f * size, profile = 1.9f, ridge = 0.16f, crater = Crater.Dry, craterDepth = 0.06f,
                        snowline = snowy ? 0.6f : 2f, blocks = 6,
                    }, groundAt);
                    break;
                }

                case VolcanoForm.Somma:
                {
                    // the old volcano's rim, half blown away, older and part grown over
                    float breachAt = Range(rng, 0f, 360f);
                    AddVolcanoCone(b, rng, size, new Cone
                    {
                        radius = 0.74f * size, height = h * 0.55f, top = 0.44f * size, sides = 48, profile = 1.3f, ridge = 0.2f,
                        crater = Crater.Dry, craterDepth = 0.3f, craterInset = 0.92f, breach = 0.8f, breachAt = breachAt,
                        ash = Color.Lerp(Ash, OldSlope, underwater ? 0f : 0.5f), blocks = 8,
                    }, groundAt);
                    // the young cone inside, a little toward the breach
                    var lean = Quaternion.Euler(0f, breachAt, 0f) * Vector3.forward * 0.08f * size;
                    lean.y = 0f;
                    vent = AddVolcanoCone(b, rng, size, new Cone
                    {
                        at = lean, radius = 0.36f * size, height = h * 0.95f, top = 0.08f * size, crater = Crater.Lava,
                        streams = 1, streamReach = 0.5f, blocks = 6,
                    }, groundAt);
                    break;
                }

                case VolcanoForm.LavaDome:
                {
                    // bulging domes of stiff lava crowded together, the biggest in the middle
                    vent = Vector3.zero;
                    int domes = rng.Next(3, 6);
                    for (int i = 0; i < domes; i++)
                    {
                        var at = i == 0 ? Vector3.zero : Along(Mathf.Sin(i * 2.4f) * Range(rng, 0.25f, 0.4f), Mathf.Cos(i * 2.4f) * Range(rng, 0.25f, 0.4f));
                        at.y = i == 0 ? 0f : GroundY(at);
                        float r = (i == 0 ? 0.34f : Range(rng, 0.15f, 0.24f)) * size;
                        var top = AddVolcanoCone(b, rng, size, new Cone
                        {
                            at = at, radius = r, height = h * (i == 0 ? 0.5f : Range(rng, 0.18f, 0.32f)), top = 0.3f * r,
                            sides = 24, rings = 8, profile = 0.45f, ridge = 0.14f, jitter = 0.08f, rough = 1.3f,
                            crater = Crater.None, ash = Dacite, rock = Dacite * 0.78f, blocks = 4,
                        }, groundAt);
                        if (i == 0) vent = top;
                        // spines of lava pushed up out of the dome
                        for (int k = i == 0 ? rng.Next(2, 4) : rng.Next(0, 2); k > 0; k--)
                            AddCone(b, rng, top + new Vector3(Range(rng, -0.4f, 0.4f) * r, -0.04f * r, Range(rng, -0.4f, 0.4f) * r),
                                    0.12f * r, Range(rng, 0.3f, 0.6f) * r, Shade(rng, Dacite * 0.65f, 0.06f));
                    }
                    break;
                }

                case VolcanoForm.Fissure:
                {
                    // a row of spatter cones along a rift that glows between them
                    int cones = rng.Next(4, 7);
                    vent = Vector3.zero;
                    var rift = new List<Vector3>();
                    for (int i = 0; i < cones; i++)
                    {
                        float x = Mathf.Lerp(-0.55f, 0.55f, i / (float)(cones - 1));
                        var at = Along(x, Mathf.Sin(x * 3f + turn) * 0.06f);
                        at.y = GroundY(at);
                        var top = AddVolcanoCone(b, rng, size, new Cone
                        {
                            at = at, radius = Range(rng, 0.08f, 0.13f) * size, height = h * Range(rng, 0.1f, 0.2f), top = 0.035f * size,
                            sides = 14, rings = 4, profile = 1.1f, ridge = 0.1f, rough = 0.4f, crater = Crater.Lava,
                            craterDepth = 0.2f, blocks = 2,
                        }, groundAt);
                        if (i == cones / 2) vent = top;
                        rift.Add(at);
                    }
                    var side = Quaternion.Euler(0f, turn, 0f) * Vector3.forward;
                    // The rift between the cones: a crooked crack of uneven width, mostly dark crust
                    // with lava glowing only in a few gaps, and dark spatter heaped along its lips.
                    for (int i = 0; i + 1 < rift.Count; i++)
                    {
                        const int steps = 6;
                        var prev = rift[i];
                        float prevW = 0.006f * size;
                        for (int k = 1; k <= steps; k++)
                        {
                            float t = k / (float)steps;
                            var next = Vector3.Lerp(rift[i], rift[i + 1], t);
                            if (k < steps) next += side * Range(rng, -0.025f, 0.025f) * size;     // zigzag
                            next.y = GroundY(next);
                            float w = k < steps ? Range(rng, 0.004f, 0.016f) * size : 0.006f * size; // narrow and uneven
                            var lift = Vector3.up * 0.004f * size;
                            bool glowing = rng.NextDouble() < 0.35;
                            var color = glowing ? Lava * Range(rng, 0.8f, 1.05f) : Color.Lerp(LavaCool, Basalt, Range(rng, 0.5f, 0.9f));
                            b.AddQuad(prev - side * prevW + lift, prev + side * prevW + lift, next + side * w + lift, next - side * w + lift,
                                      color, (prev + next) * 0.5f - Vector3.up);
                            // spatter ramparts along both lips
                            if (rng.NextDouble() < 0.7)
                            {
                                var lip = (prev + next) * 0.5f + side * (w + 0.012f * size) * (rng.NextDouble() < 0.5 ? -1f : 1f);
                                lip.y = GroundY(lip);
                                AddBlob(b, rng, lip, size * Range(rng, 0.012f, 0.022f), 0.5f, 0, Shade(rng, Scoria * 0.7f, 0.1f), angular: true);
                            }
                            prev = next;
                            prevW = w;
                        }
                    }
                    // fresh black lava spread out on both sides of the rift
                    for (int i = 0; i < 14; i++)
                    {
                        var p = rift[rng.Next(rift.Count)] + side * Range(rng, 0.06f, 0.3f) * (rng.NextDouble() < 0.5 ? -1f : 1f)
                              + Quaternion.Euler(0f, turn, 0f) * Vector3.right * Range(rng, -0.08f, 0.08f) * size;
                        p.y = GroundY(p);
                        AddBlob(b, rng, p, size * Range(rng, 0.06f, 0.1f), 0.15f, 0, rng.NextDouble() < 0.2 ? LavaCool : Shade(rng, Basalt, 0.08f), angular: true);
                    }
                    break;
                }

                default: // Strato
                    vent = AddVolcanoCone(b, rng, size, new Cone
                    {
                        radius = 0.58f * size, height = h, top = 0.15f * size, sides = 48, rings = 18,
                        streams = rng.Next(1, 3), streamReach = 0.4f, parasite = true, blocks = 20,
                    }, groundAt);
                    break;
            }

            if (boulders)
                foreach (var p in Scatter(rng, rng.Next(3, 6), 0.7f * size, 0.08f * size, new List<Vector2>()))
                    if (p.magnitude > 0.55f * size)
                    {
                        var at = new Vector3(p.x, 0f, p.y);
                        at.y = GroundY(at);
                        AddRock(b, rng, at, size * Range(rng, 0.03f, 0.05f), Basalt);
                    }

            var mesh = b.ToMesh("Volcano");
            RegisterVent(mesh, vent);
            return mesh;
        }
    }
}
