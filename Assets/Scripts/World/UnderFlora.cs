using UnityEngine;

namespace NaturalHistory.World
{
    // Fungi (caves and soil) and the extra water-plant forms of the layer under sea level
    // (plants.json layer "under"). For these forms the species' tint is its actual colour, not a
    // multiplier on a built-in one, so a fly agaric can be scarlet and a glowing bonnet green.
    public static partial class MapFeatureMeshes
    {
        static readonly Color FungusStem = new(0.90f, 0.86f, 0.78f);
        static readonly Color Gill       = new(0.82f, 0.76f, 0.66f);
        static readonly Color LogBark    = new(0.30f, 0.22f, 0.15f);

        // Adds one clump of a fungus or water plant; false if the form isn't one of these.
        // `size` is the cell size, `m` the species' size × random factor.
        static bool AddUnderFlora(Builder b, System.Random rng, Vector3 root, float size, PlantDefinition plant, float m)
        {
            var c = plant.Tint;
            float s = size * 0.05f * m; // a typical clump size
            switch (plant.form)
            {
                // ---- Fungi, lichens and slime moulds ----
                case "Mushroom":     AddMushrooms(b, rng, root, s, c, rng.Next(2, 5), spots: false, glow: false); break;
                case "Toadstool":    AddMushrooms(b, rng, root, s * 1.1f, c, rng.Next(1, 4), spots: true, glow: false); break;
                case "GlowCap":      AddMushrooms(b, rng, root, s * 0.7f, c, rng.Next(5, 9), spots: false, glow: true); break;
                case "Inkcap":       AddInkcaps(b, rng, root, s, c); break;
                case "Funnel":       AddFunnels(b, rng, root, s, c); break;
                case "Bracket":      AddBrackets(b, rng, root, s, c); break;
                case "Puffball":     AddPuffballs(b, rng, root, s, c); break;
                case "Earthstar":    AddEarthstars(b, rng, root, s, c); break;
                case "Lattice":      AddLattice(b, rng, root, s, c); break;
                case "CoralFungus":  AddCoralFungus(b, rng, root, s, c); break;
                case "Cup":          for (int i = rng.Next(3, 6); i > 0; i--) AddCup(b, rng, root + Jitter(rng, s * 1.2f), s * Range(rng, 0.35f, 0.6f), Shade(rng, c)); break;
                case "Morel":        AddMorels(b, rng, root, s, c); break;
                case "Mycelium":     AddMycelium(b, rng, root, s * 2.5f, c, nodes: false); break;
                case "SlimeMold":    AddMycelium(b, rng, root, s * 2f, c, nodes: true); break;
                case "Stalks":       AddStalks(b, rng, root, s, c); break;
                case "Lichen":       AddLichen(b, rng, root, s, c); break;
                case "Truffle":      AddTruffles(b, rng, root, s, c); break;
                case "Prototaxites": AddPrototaxites(b, rng, root, size * 0.55f * m, c); break;

                // ---- Water plants and algae ----
                case "Fan":          AddFans(b, rng, root, s * 1.4f, c); break;
                case "Bubble":       AddBubbles(b, rng, root, s, c); break;
                case "SeaLettuce":   AddFrondRosette(b, rng, root + Vector3.up * 0.003f, rng.Next(6, 10), s * 1.6f, s * Range(rng, 0.4f, 1.0f), s * 0.3f, s * 0.9f, Shade(rng, c)); break;
                case "Feather":      AddFeathers(b, rng, root, s * 2f, c); break;
                case "Grape":        AddGrapes(b, rng, root, s * 1.6f, c); break;
                case "Tuft":         AddTufts(b, rng, root, s * 1.8f, c); break;
                case "Ribbon":       AddRibbons(b, rng, root, size * 0.2f * m, c); break;
                case "Whorl":        AddWhorls(b, rng, root, s * 2.6f, c); break;
                case "Rosette":      AddFrondRosette(b, rng, root + Vector3.up * 0.003f, rng.Next(7, 11), s * 2.2f, s * 2.4f, s * 0.6f, s * 0.45f, Shade(rng, c)); break;
                case "Lotus":        AddLotus(b, rng, root, s * 3f, c); break;
                case "Cushion":      for (int i = rng.Next(4, 8); i > 0; i--) AddBlob(b, rng, root + Jitter(rng, s), s * Range(rng, 0.35f, 0.6f), 0.55f, 0, Shade(rng, c)); break;
                case "Mat":          AddMats(b, rng, root, s * 2f, c); break;
                case "Calcareous":   AddCoinChains(b, rng, root, s * 1.6f, c); break;
                case "Fingers":      AddFingers(b, rng, root, s * 1.8f, c); break;
                case "Wineglass":    AddWineglasses(b, rng, root, s * 1.4f, c); break;
                default: return false;
            }
            return true;
        }

        static Vector3 Jitter(System.Random rng, float r) => new(Range(rng, -r, r), 0f, Range(rng, -r, r));

        // Mushroom cap: a dome over a ring of gills; `droop` < 0 turns it into a funnel
        static void AddCap(Builder b, System.Random rng, Vector3 top, float r, float h, Color cap, Color under, float droop = 0.25f)
        {
            int n = fineDetail ? 20 : 10;
            var rim  = new Vector3[n];
            var apex = top + Vector3.up * h;
            var hub  = top - Vector3.up * h * 0.15f;
            float rot = Range(rng, 0f, 6.3f);
            for (int i = 0; i < n; i++)
            {
                float a = rot + i * Mathf.PI * 2f / n;
                rim[i] = top + new Vector3(Mathf.Cos(a) * r * Range(rng, 0.92f, 1.08f), -h * droop, Mathf.Sin(a) * r * Range(rng, 0.92f, 1.08f));
            }
            for (int i = 0; i < n; i++)
            {
                var p0 = rim[i]; var p1 = rim[(i + 1) % n];
                var mid = Vector3.Lerp((p0 + p1) * 0.5f, apex, 0.45f) + Vector3.up * h * 0.1f; // rounded shoulder
                b.AddTri(p0, p1, mid, cap * Range(rng, 0.94f, 1.06f), hub);
                b.AddTri(p0, mid, apex, cap * 1.04f, hub);
                b.AddTri(p1, apex, mid, cap * 1.04f, hub);
                b.AddTri(p0, p1, hub, under, apex);
            }
        }

        static void AddMushrooms(Builder b, System.Random rng, Vector3 root, float s, Color cap, int count, bool spots, bool glow)
        {
            var color = glow ? cap * 2.2f : cap;           // glowing caps stay bright in the dark
            var stem  = glow ? Color.Lerp(FungusStem, cap, 0.4f) * 1.4f : FungusStem;
            for (int i = 0; i < count; i++)
            {
                var foot = root + (i == 0 ? Vector3.zero : Jitter(rng, s * 0.9f));
                float h  = s * Range(rng, 0.6f, 1.1f) * (i == 0 ? 1.15f : 1f);
                float r  = s * Range(rng, 0.35f, 0.5f) * (i == 0 ? 1.15f : 1f);
                var top  = foot + Vector3.up * h + new Vector3(Range(rng, -0.1f, 0.1f), 0f, Range(rng, -0.1f, 0.1f)) * s;
                AddLimb(b, foot - Vector3.up * 0.003f, top, r * 0.22f, r * 0.17f, Shade(rng, stem, 0.05f));
                AddCap(b, rng, top, r, r * 0.55f, Shade(rng, color, 0.06f), glow ? color * 0.8f : Color.Lerp(cap, Gill, 0.65f));
                if (!spots) continue;
                for (int k = 0; k < 6; k++) // the white warts of a fly agaric
                {
                    float a = Range(rng, 0f, 6.3f), d = Range(rng, 0.15f, 0.75f);
                    var p = top + new Vector3(Mathf.Cos(a) * d * r, r * 0.55f * (1f - d * d) * 0.9f + 0.002f * s, Mathf.Sin(a) * d * r);
                    AddGem(b, p, new Vector3(0.12f, 0.06f, 0.12f) * r, new Color(0.97f, 0.95f, 0.9f), Vector3.up);
                }
            }
        }

        static void AddInkcaps(Builder b, System.Random rng, Vector3 root, float s, Color c)
        {
            for (int i = rng.Next(2, 5); i > 0; i--)
            {
                var foot = root + Jitter(rng, s * 0.7f);
                float h = s * Range(rng, 0.9f, 1.4f);
                AddLimb(b, foot - Vector3.up * 0.003f, foot + Vector3.up * h, s * 0.06f, s * 0.05f, FungusStem);
                AddBlob(b, rng, foot + Vector3.up * (h + s * 0.15f), s * 0.18f, 1.9f, 0, Shade(rng, c, 0.05f)); // tall shaggy bell
                AddGem(b, foot + Vector3.up * (h - s * 0.12f), new Vector3(0.2f, 0.05f, 0.2f) * s, new Color(0.1f, 0.09f, 0.1f), Vector3.up); // inky rim
            }
        }

        static void AddFunnels(Builder b, System.Random rng, Vector3 root, float s, Color c)
        {
            for (int i = rng.Next(2, 5); i > 0; i--)
            {
                var foot = root + Jitter(rng, s * 0.8f);
                float h = s * Range(rng, 0.45f, 0.75f), r = s * Range(rng, 0.28f, 0.4f);
                AddLimb(b, foot - Vector3.up * 0.003f, foot + Vector3.up * h, r * 0.3f, r * 0.5f, Shade(rng, c, 0.05f));
                AddCap(b, rng, foot + Vector3.up * h, r, r * 0.25f, Shade(rng, c, 0.05f), c * 0.85f, droop: -0.9f); // rim curls up
            }
        }

        // Shelf fungi stacked on a fallen, mossy log
        static void AddBrackets(Builder b, System.Random rng, Vector3 root, float s, Color c)
        {
            float a = Range(rng, 0f, Mathf.PI);
            var along = new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a));
            float len = s * Range(rng, 1.6f, 2.4f), r = s * 0.22f;
            var p0 = root - along * len * 0.5f + Vector3.up * r * 0.8f;
            var p1 = root + along * len * 0.5f + Vector3.up * r * 0.7f;
            AddLimb(b, p0, p1, r, r * 0.85f, LogBark);
            var side = Vector3.Cross(Vector3.up, along);
            for (int i = rng.Next(4, 8); i > 0; i--)
            {
                float t = Range(rng, 0.1f, 0.9f), sgn = rng.NextDouble() < 0.5 ? -1f : 1f;
                var at = Vector3.Lerp(p0, p1, t) + side * sgn * r * 0.85f + Vector3.up * Range(rng, -0.3f, 0.5f) * r;
                float w = s * Range(rng, 0.25f, 0.42f);
                AddBlob(b, rng, at + side * sgn * w * 0.35f, w, 0.28f, 0, Shade(rng, c, 0.08f));
                AddBlob(b, rng, at + side * sgn * w * 0.5f - Vector3.up * w * 0.05f, w * 0.7f, 0.2f, 0, Color.Lerp(c, Color.white, 0.35f)); // paler growing edge
            }
        }

        static void AddPuffballs(Builder b, System.Random rng, Vector3 root, float s, Color c)
        {
            for (int i = rng.Next(1, 4); i > 0; i--)
            {
                float r = s * Range(rng, 0.25f, 0.5f);
                var at = root + Jitter(rng, s * 0.8f) + Vector3.up * r * 0.7f;
                AddBlob(b, rng, at, r, 0.85f, 1, Shade(rng, c, 0.05f));
                AddGem(b, at + Vector3.up * r * 0.82f, new Vector3(0.15f, 0.05f, 0.15f) * r, c * 0.45f, Vector3.up); // the spore pore
            }
        }

        static void AddEarthstars(Builder b, System.Random rng, Vector3 root, float s, Color c)
        {
            for (int i = rng.Next(1, 3); i > 0; i--)
            {
                var at = root + Jitter(rng, s * 0.7f);
                float r = s * Range(rng, 0.3f, 0.45f);
                int rays = rng.Next(6, 9);
                for (int k = 0; k < rays; k++)
                {
                    float a = k * Mathf.PI * 2f / rays;
                    var dir = new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a));
                    AddGem(b, at + dir * r * 0.75f + Vector3.up * 0.004f * s, new Vector3(r * 0.22f, r * 0.05f, r * 0.75f), Shade(rng, c), Vector3.up);
                }
                AddBlob(b, rng, at + Vector3.up * r * 0.35f, r * 0.4f, 0.85f, 0, Color.Lerp(c, new Color(0.75f, 0.68f, 0.58f), 0.5f));
            }
        }

        // Cage fungus: a hollow lattice ball
        static void AddLattice(Builder b, System.Random rng, Vector3 root, float s, Color c)
        {
            float r = s * 0.45f;
            var centre = root + Vector3.up * r * 0.95f;
            for (int ring = 0; ring < 3; ring++)
            {
                var axis = Quaternion.Euler(ring * 60f, ring * 40f, 0f);
                const int n = 8;
                for (int k = 0; k < n; k++)
                {
                    float a0 = k * Mathf.PI * 2f / n, a1 = (k + 1) * Mathf.PI * 2f / n;
                    var q0 = centre + axis * new Vector3(Mathf.Cos(a0), 0f, Mathf.Sin(a0)) * r;
                    var q1 = centre + axis * new Vector3(Mathf.Cos(a1), 0f, Mathf.Sin(a1)) * r;
                    AddLimb(b, q0, q1, r * 0.09f, r * 0.09f, Shade(rng, c, 0.06f));
                }
            }
            AddBlob(b, rng, root + Vector3.up * r * 0.1f, r * 0.45f, 0.4f, 0, new Color(0.92f, 0.9f, 0.86f)); // the egg it hatched from
        }

        static void AddCoralFungus(Builder b, System.Random rng, Vector3 root, float s, Color c)
        {
            for (int i = rng.Next(4, 7); i > 0; i--)
            {
                var foot = root + Jitter(rng, s * 0.3f);
                var mid  = foot + new Vector3(Range(rng, -0.25f, 0.25f), Range(rng, 0.4f, 0.6f), Range(rng, -0.25f, 0.25f)) * s;
                AddLimb(b, foot - Vector3.up * 0.003f, mid, s * 0.07f, s * 0.05f, Shade(rng, c, 0.05f));
                for (int k = rng.Next(2, 4); k > 0; k--)
                {
                    var tip = mid + new Vector3(Range(rng, -0.25f, 0.25f), Range(rng, 0.3f, 0.5f), Range(rng, -0.25f, 0.25f)) * s;
                    AddLimb(b, mid, tip, s * 0.045f, s * 0.02f, Shade(rng, c * 1.06f, 0.05f));
                }
            }
        }

        static void AddMorels(Builder b, System.Random rng, Vector3 root, float s, Color c)
        {
            for (int i = rng.Next(2, 4); i > 0; i--)
            {
                var foot = root + Jitter(rng, s * 0.7f);
                float h = s * Range(rng, 0.35f, 0.5f);
                AddLimb(b, foot - Vector3.up * 0.003f, foot + Vector3.up * h, s * 0.08f, s * 0.08f, FungusStem);
                AddBlob(b, rng, foot + Vector3.up * (h + s * 0.25f), s * 0.18f, 1.7f, 0, Shade(rng, c, 0.05f));
                for (int k = 0; k < 7; k++) // honeycomb pits
                {
                    float a = Range(rng, 0f, 6.3f), y = Range(rng, 0.05f, 0.45f);
                    AddGem(b, foot + Vector3.up * (h + y * s) + new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a)) * s * 0.17f * (1f - y),
                           Vector3.one * s * 0.05f, c * 0.55f, new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a)));
                }
            }
        }

        // Fine threads spreading over the ground (moulds, mycorrhizae); with `nodes`, a slime mould's
        // vein network with plump feeding fronts
        static void AddMycelium(Builder b, System.Random rng, Vector3 root, float r, Color c, bool nodes)
        {
            float lift = 0.004f * r;
            for (int i = rng.Next(6, 10); i > 0; i--)
            {
                float a = Range(rng, 0f, 6.3f);
                var prev = root + Vector3.up * lift;
                for (int k = 1; k <= 3; k++)
                {
                    a += Range(rng, -0.6f, 0.6f);
                    var p = prev + new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a)) * r * Range(rng, 0.2f, 0.35f);
                    AddLimb(b, prev, p, r * (nodes ? 0.04f : 0.012f), r * (nodes ? 0.03f : 0.008f), Shade(rng, c, 0.06f));
                    if (rng.NextDouble() < 0.4)
                    {
                        float a2 = a + Range(rng, 0.6f, 1.2f) * (rng.NextDouble() < 0.5 ? -1f : 1f);
                        AddLimb(b, p, p + new Vector3(Mathf.Cos(a2), 0f, Mathf.Sin(a2)) * r * 0.2f, r * 0.01f, r * 0.005f, c);
                    }
                    prev = p;
                }
                if (nodes) AddBlob(b, rng, prev, r * 0.09f, 0.5f, 0, c * 1.05f);
                else if (rng.NextDouble() < 0.5) AddGem(b, prev, Vector3.one * r * 0.03f, c * 1.1f, Vector3.up);
            }
        }

        // Thin upright stalks with swollen heads (cordyceps, chocolate-tube slime)
        static void AddStalks(Builder b, System.Random rng, Vector3 root, float s, Color c)
        {
            for (int i = rng.Next(5, 9); i > 0; i--)
            {
                var foot = root + Jitter(rng, s * 0.5f);
                var tip  = foot + new Vector3(Range(rng, -0.15f, 0.15f), Range(rng, 0.6f, 1.1f), Range(rng, -0.15f, 0.15f)) * s;
                AddLimb(b, foot, tip, s * 0.03f, s * 0.025f, Shade(rng, c * 0.9f, 0.05f));
                AddGem(b, tip, new Vector3(0.05f, 0.14f, 0.05f) * s, Shade(rng, c, 0.06f), (tip - foot).normalized);
            }
        }

        static void AddLichen(Builder b, System.Random rng, Vector3 root, float s, Color c)
        {
            for (int i = rng.Next(4, 8); i > 0; i--)
                AddBlob(b, rng, root + Jitter(rng, s * 1.2f) + Vector3.up * 0.004f * s, s * Range(rng, 0.25f, 0.5f), Range(rng, 0.2f, 0.55f), 0, Shade(rng, c, 0.1f));
            for (int i = rng.Next(2, 5); i > 0; i--) // little fruiting cups
                AddGem(b, root + Jitter(rng, s) + Vector3.up * 0.1f * s, new Vector3(0.07f, 0.04f, 0.07f) * s, c * 0.6f, Vector3.up);
        }

        static void AddTruffles(Builder b, System.Random rng, Vector3 root, float s, Color c)
        {
            AddBlob(b, rng, root, s * 0.7f, 0.25f, 0, new Color(0.36f, 0.27f, 0.2f)); // turned-over soil
            for (int i = rng.Next(2, 5); i > 0; i--)
                AddBlob(b, rng, root + Jitter(rng, s * 0.5f) + Vector3.up * s * 0.05f, s * Range(rng, 0.15f, 0.25f), 0.85f, 0, Shade(rng, c, 0.08f));
        }

        // Prototaxites: a giant, branchless fungal trunk of the Silurian and Devonian
        static void AddPrototaxites(Builder b, System.Random rng, Vector3 root, float h, Color c)
        {
            var top = root + new Vector3(Range(rng, -0.04f, 0.04f), 1f, Range(rng, -0.04f, 0.04f)) * h;
            Banded(b, rng, root - Vector3.up * 0.005f, top, h * 0.075f, h * 0.06f, c, c * 0.82f, 7);
            AddBlob(b, rng, top, h * 0.07f, 0.8f, 0, c * 1.05f);
        }

        // ---- Water plants ----

        // A thin sheet seen from both sides (fan blades, lily pads)
        static void AddSheet(Builder b, Vector3 a, Vector3 b1, Vector3 c1, Color color)
        {
            var n = Vector3.Cross(b1 - a, c1 - a).normalized * 0.001f;
            var mid = (a + b1 + c1) / 3f;
            b.AddTri(a, b1, c1, color, mid - n);
            b.AddTri(a, b1, c1, color * 0.85f, mid + n);
        }

        // Padina and phylloid algae: rounded fans on short stalks
        static void AddFans(Builder b, System.Random rng, Vector3 root, float s, Color c)
        {
            for (int i = rng.Next(3, 6); i > 0; i--)
            {
                var foot = root + Jitter(rng, s * 0.6f);
                float face = Range(rng, 0f, 6.3f);
                var fwd = new Vector3(Mathf.Cos(face), 0f, Mathf.Sin(face));
                var side = Vector3.Cross(Vector3.up, fwd);
                var hub = foot + Vector3.up * s * 0.15f;
                AddLimb(b, foot, hub, s * 0.03f, s * 0.025f, c * 0.8f);
                int n = fineDetail ? 14 : 7;
                var prev = Vector3.zero;
                float r = s * Range(rng, 0.45f, 0.7f);
                var col = Shade(rng, c, 0.08f);
                for (int k = 0; k <= n; k++)
                {
                    float a = Mathf.Lerp(-1.2f, 1.2f, k / (float)n);
                    var p = hub + (Vector3.up * Mathf.Cos(a) + side * Mathf.Sin(a)) * r + fwd * Mathf.Sin(k * 1.7f) * r * 0.08f;
                    if (k > 0) AddSheet(b, hub, prev, p, Mathf.CeilToInt(k * 7f / n) % 2 == 0 ? col : col * 0.92f); // the 7 bands of a Padina fan
                    prev = p;
                }
            }
        }

        // Bubble algae and marimo: glossy green balls
        static void AddBubbles(Builder b, System.Random rng, Vector3 root, float s, Color c)
        {
            for (int i = rng.Next(4, 9); i > 0; i--)
            {
                float r = s * Range(rng, 0.15f, 0.35f);
                var at = root + Jitter(rng, s * 0.8f) + Vector3.up * r * 0.8f;
                AddBlob(b, rng, at, r, 1f, 0, Shade(rng, c, 0.06f));
                AddGem(b, at + new Vector3(-0.35f, 0.6f, 0.35f) * r, Vector3.one * r * 0.18f, Color.Lerp(c, Color.white, 0.7f), Vector3.up); // glint
            }
        }

        // Feather algae and bladderworts: plumes of fine side branchlets along a stem
        static void AddFeathers(Builder b, System.Random rng, Vector3 root, float s, Color c)
        {
            for (int i = rng.Next(3, 6); i > 0; i--)
            {
                var foot = root + Jitter(rng, s * 0.3f);
                var tip  = foot + new Vector3(Range(rng, -0.25f, 0.25f), Range(rng, 0.7f, 1f), Range(rng, -0.25f, 0.25f)) * s;
                var col = Shade(rng, c, 0.06f);
                AddLimb(b, foot, tip, s * 0.02f, s * 0.01f, col);
                var axis = (tip - foot).normalized;
                var side = Vector3.Cross(axis, Vector3.forward).normalized;
                for (int k = 1; k < 8; k++)
                {
                    var at = Vector3.Lerp(foot, tip, k / 8f);
                    float len = s * 0.2f * (1f - k / 9f);
                    AddLimb(b, at, at + (side + axis * 0.5f).normalized * len, s * 0.008f, s * 0.003f, col * 1.05f);
                    AddLimb(b, at, at + (-side + axis * 0.5f).normalized * len, s * 0.008f, s * 0.003f, col * 1.05f);
                }
            }
        }

        // Sea grapes and Neptune's necklace: stalks hung with round beads
        static void AddGrapes(Builder b, System.Random rng, Vector3 root, float s, Color c)
        {
            for (int i = rng.Next(3, 6); i > 0; i--)
            {
                var foot = root + Jitter(rng, s * 0.4f);
                var tip  = foot + new Vector3(Range(rng, -0.3f, 0.3f), Range(rng, 0.5f, 0.9f), Range(rng, -0.3f, 0.3f)) * s;
                AddLimb(b, foot, tip, s * 0.015f, s * 0.01f, c * 0.8f);
                for (int k = 2; k < 9; k++)
                    AddBlob(b, rng, Vector3.Lerp(foot, tip, k / 9f) + Jitter(rng, s * 0.03f), s * 0.055f, 1f, 0, Shade(rng, c, 0.06f));
            }
        }

        // Finely branched red and brown seaweeds
        static void AddTufts(Builder b, System.Random rng, Vector3 root, float s, Color c)
        {
            for (int i = rng.Next(5, 9); i > 0; i--)
            {
                var foot = root + Jitter(rng, s * 0.25f);
                var mid  = foot + new Vector3(Range(rng, -0.25f, 0.25f), Range(rng, 0.35f, 0.5f), Range(rng, -0.25f, 0.25f)) * s;
                var col  = Shade(rng, c, 0.08f);
                AddLimb(b, foot, mid, s * 0.02f, s * 0.014f, col);
                for (int k = rng.Next(2, 4); k > 0; k--)
                    AddLimb(b, mid, mid + new Vector3(Range(rng, -0.25f, 0.25f), Range(rng, 0.25f, 0.45f), Range(rng, -0.25f, 0.25f)) * s, s * 0.012f, s * 0.004f, col * 1.08f);
            }
        }

        // Strap kelps and wakame: long wavy blades rising from a holdfast
        static void AddRibbons(Builder b, System.Random rng, Vector3 root, float h, Color c)
        {
            AddBlob(b, rng, root, h * 0.06f, 0.5f, 0, c * 0.6f); // holdfast
            for (int i = rng.Next(3, 6); i > 0; i--)
            {
                float a = Range(rng, 0f, 6.3f);
                var dir = new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a));
                var col = Shade(rng, c, 0.08f);
                var prev = root;
                for (int k = 1; k <= 4; k++)
                {
                    float t = k / 4f;
                    var p = root + Vector3.up * h * t * Range(rng, 0.85f, 1f) + dir * (t * 0.25f + Mathf.Sin(t * 5f + a) * 0.06f) * h;
                    AddFrond(b, prev, (p - prev).normalized, (p - prev).magnitude * 1.05f, 0f, 0f, h * 0.07f, col * (0.9f + 0.1f * t));
                    prev = p;
                }
            }
        }

        // Hornwort, milfoil and dasyclads: upright stems ringed with whorls of needles
        static void AddWhorls(Builder b, System.Random rng, Vector3 root, float h, Color c)
        {
            for (int i = rng.Next(3, 6); i > 0; i--)
            {
                var foot = root + Jitter(rng, h * 0.25f);
                var tip  = foot + new Vector3(Range(rng, -0.1f, 0.1f), Range(rng, 0.8f, 1f), Range(rng, -0.1f, 0.1f)) * h;
                var col  = Shade(rng, c, 0.06f);
                AddLimb(b, foot, tip, h * 0.012f, h * 0.008f, col * 0.85f);
                for (int k = 1; k <= 6; k++)
                {
                    var at = Vector3.Lerp(foot, tip, k / 6.5f);
                    for (int w = 0; w < 6; w++)
                    {
                        float a = w * Mathf.PI / 3f + k * 0.5f;
                        AddLimb(b, at, at + new Vector3(Mathf.Cos(a) * 0.12f, 0.05f, Mathf.Sin(a) * 0.12f) * h, h * 0.006f, h * 0.002f, col);
                    }
                }
            }
        }

        // Lotus and water lilies: long stalks reaching up to round leaves and the odd flower
        static void AddLotus(Builder b, System.Random rng, Vector3 root, float h, Color c)
        {
            for (int i = rng.Next(3, 5); i > 0; i--)
            {
                var foot = root + Jitter(rng, h * 0.15f);
                var top  = foot + new Vector3(Range(rng, -0.15f, 0.15f), Range(rng, 0.6f, 1f), Range(rng, -0.15f, 0.15f)) * h;
                AddLimb(b, foot, top, h * 0.012f, h * 0.01f, c * 0.75f);
                float r = h * Range(rng, 0.14f, 0.22f);
                AddBlob(b, rng, top, r, 0.1f, 0, Shade(rng, c, 0.06f));
                if (rng.NextDouble() < 0.35)
                    AddGem(b, top + Vector3.up * r * 0.25f, new Vector3(0.35f, 0.4f, 0.35f) * r, new Color(0.98f, 0.62f, 0.78f), Vector3.up);
            }
        }

        // Microbial mats: flat, layered, bubbly patches
        static void AddMats(Builder b, System.Random rng, Vector3 root, float s, Color c)
        {
            for (int i = rng.Next(3, 6); i > 0; i--)
                AddBlob(b, rng, root + Jitter(rng, s * 0.8f) + Vector3.up * 0.003f * s, s * Range(rng, 0.35f, 0.6f), 0.12f, 0, Shade(rng, c, 0.1f));
            for (int i = rng.Next(3, 7); i > 0; i--) // oxygen bubbles
                AddGem(b, root + Jitter(rng, s) + Vector3.up * s * 0.06f, Vector3.one * s * 0.03f, Color.Lerp(c, Color.white, 0.6f), Vector3.up);
        }

        // Halimeda and calcified red algae: branching chains of stony discs
        static void AddCoinChains(Builder b, System.Random rng, Vector3 root, float s, Color c)
        {
            for (int i = rng.Next(3, 6); i > 0; i--)
            {
                var at  = root + Jitter(rng, s * 0.3f);
                var dir = new Vector3(Range(rng, -0.4f, 0.4f), 1f, Range(rng, -0.4f, 0.4f)).normalized;
                for (int k = 0; k < 6; k++)
                {
                    at += dir * s * 0.13f;
                    AddBlob(b, rng, at, s * 0.08f, 0.35f, 0, Shade(rng, c, 0.06f) * (1f + 0.03f * k));
                    dir = (dir + new Vector3(Range(rng, -0.4f, 0.4f), 0.1f, Range(rng, -0.4f, 0.4f))).normalized;
                }
            }
        }

        // Codium ("dead man's fingers"): thick, spongy, forking fingers
        static void AddFingers(Builder b, System.Random rng, Vector3 root, float s, Color c)
        {
            for (int i = rng.Next(3, 6); i > 0; i--)
            {
                var foot = root + Jitter(rng, s * 0.2f);
                var mid  = foot + new Vector3(Range(rng, -0.25f, 0.25f), Range(rng, 0.3f, 0.5f), Range(rng, -0.25f, 0.25f)) * s;
                AddLimb(b, foot, mid, s * 0.06f, s * 0.055f, Shade(rng, c, 0.05f));
                for (int k = 0; k < 2; k++)
                {
                    var tip = mid + new Vector3(Range(rng, -0.25f, 0.25f), Range(rng, 0.25f, 0.4f), Range(rng, -0.25f, 0.25f)) * s;
                    AddLimb(b, mid, tip, s * 0.055f, s * 0.05f, Shade(rng, c, 0.05f));
                    AddBlob(b, rng, tip, s * 0.05f, 1f, 0, c);
                }
            }
        }

        // Mermaid's wineglass: slender stalks topped with little ribbed umbrellas
        static void AddWineglasses(Builder b, System.Random rng, Vector3 root, float s, Color c)
        {
            for (int i = rng.Next(5, 9); i > 0; i--)
            {
                var foot = root + Jitter(rng, s * 0.5f);
                var top  = foot + new Vector3(Range(rng, -0.1f, 0.1f), Range(rng, 0.5f, 0.8f), Range(rng, -0.1f, 0.1f)) * s;
                AddLimb(b, foot, top, s * 0.012f, s * 0.01f, c * 0.85f);
                AddCap(b, rng, top, s * Range(rng, 0.1f, 0.15f), s * 0.03f, Shade(rng, c, 0.05f), c * 0.8f, droop: -0.6f);
            }
        }
    }
}
