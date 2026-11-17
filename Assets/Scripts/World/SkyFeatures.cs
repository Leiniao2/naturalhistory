using System;
using System.Collections.Generic;
using UnityEngine;

namespace NaturalHistory.World
{
    // The sky layer's moving weather systems, drawn by SkyVeil from small uniform arrays:
    //  - Typhoons: born now and then over warm tropical sea, spinning (anticlockwise in the north,
    //    clockwise in the south), drifting west and poleward, weakening over land, dying out.
    //  - Fronts: long arcs of cloud in the mid-latitudes, trailing equatorward from a low and carried
    //    east by the westerlies.
    //  - Volcanic ash: plumes streaming downwind from some of the volcanoes, more in periods of high
    //    volcanism; an eruption (NaturalEvents) throws up a big one that slowly thins.
    //  - Ground events seen from above, in step with their surface effects (NaturalEvents): a
    //    meteor's fireball over the clouds and the glow and smoke of its impact, the dark spinning
    //    cell over a tornado, the dust of a sandstorm, the white swirl of a blizzard.
    //  - Admin triggers (AdminPanel): any of these near the camera, plus an aurora and spells of
    //    cumulus or cirrus.
    // Every system fades in and out, so nothing pops. Owned by SkyLayer, which feeds it the map.
    // Rain falls on the surface under the typhoons and fronts (RainAt, WeatherFall).
    public class SkyFeatures
    {
        public const int MaxTyphoons = 4, MaxFronts = 6, MaxPlumes = 6, MaxEvents = 4;

        // Admin triggers, in AdminPanel's list after NaturalEvents.Names
        public static readonly string[] AdminNames = { "Aurora", "Typhoon", "Weather front", "Cumulus clouds", "Cirrus clouds", "Volcanic ash cloud" };

        private class SkyEvent { public Vector2 at; public int kind; public float born, life; } // kind: 1 tornado, 2 sandstorm, 3 blizzard
        private class Spell { public Vector2 at; public float born = -1000f, life; }
        private readonly List<SkyEvent> events = new();
        private readonly Spell aurora = new(), cumulus = new(), cirrus = new();
        private bool auroraNorth;
        private readonly List<Vector2> volcanoSites = new();
        // the latest meteor: its fall from entry to impact, timed like MeteorFx
        private Vector3 meteorEntry, meteorImpact;
        private float meteorBorn = -1000f;
        private const float MeteorFall = 1.8f, MeteorLife = 16f;
        private readonly Vector4[] eventData = new Vector4[MaxEvents];

        private class Typhoon { public Vector2 at, velocity; public float radius, spin, born, life, strength; }
        private class Front { public Vector2 at; public float bend, length, width, born, life, strength, hemisphere; }
        private class Plume { public Vector2 at; public float target, strength, length, fadeFrom; public bool eruption; }

        private readonly List<Typhoon> typhoons = new();
        private readonly List<Front> fronts = new();
        private readonly List<Plume> plumes = new();
        private readonly System.Random rng = new(98765);

        private float xMin, zMin, wrap = 1f, zSpan = 1f, cell = 1f;
        private readonly List<Vector2> warmSea = new();
        private Func<Vector2, bool> isLand = _ => false;
        private float nextTyphoonRoll, nextFrontRoll;

        private readonly Vector4[] typhoonData = new Vector4[MaxTyphoons];
        private readonly Vector4[] frontA = new Vector4[MaxFronts], frontB = new Vector4[MaxFronts];
        private readonly Vector4[] plumeData = new Vector4[MaxPlumes];

        // The map and its weather this turn
        public void SetMap(float xMin, float zMin, float wrap, float zSpan, float cellSize,
                           IEnumerable<Vector2> warmSea, Func<Vector2, bool> isLand,
                           IReadOnlyList<Vector2> volcanoes, float volcanism)
        {
            this.xMin = xMin; this.zMin = zMin; this.wrap = wrap; this.zSpan = zSpan; cell = cellSize;
            this.warmSea.Clear();
            this.warmSea.AddRange(warmSea);
            this.isLand = isLand ?? (_ => false);
            volcanoSites.Clear();
            volcanoSites.AddRange(volcanoes);

            // this turn's smoking volcanoes: the old quiet ones fade, new ones rise
            foreach (var p in plumes) if (!p.eruption) p.target = 0f;
            float chance = Mathf.Clamp(0.2f * volcanism, 0.1f, 0.7f);
            foreach (var v in volcanoes)
            {
                if (rng.NextDouble() > chance) continue;
                var p = plumes.Find(x => !x.eruption && (x.at - v).sqrMagnitude < 0.01f);
                if (p == null)
                {
                    if (plumes.Count >= MaxPlumes) break;
                    plumes.Add(p = new Plume { at = v, length = cell * (3f + 3f * (float)rng.NextDouble()) });
                }
                p.target = 0.55f + 0.35f * (float)rng.NextDouble();
            }
            // fewer warm seas (a cooler period) can leave typhoons over what is now cold water: they just die out
        }

        // A volcano erupts (NaturalEvents): a thick plume that thins over a couple of minutes
        public void Erupt(Vector2 at)
        {
            var p = plumes.Find(x => (x.at - at).sqrMagnitude < 0.01f);
            if (p == null)
            {
                if (plumes.Count >= MaxPlumes) plumes.RemoveAt(0);
                plumes.Add(p = new Plume { at = at });
            }
            p.eruption = true;
            p.target = 1.6f;
            p.length = cell * 9f;
            p.fadeFrom = Time.time;
        }

        // ---------- Ground events (NaturalEvents.Occurred) ----------

        public void OnPhenomenon(Phenomenon kind, HexCell cell)
        {
            if (cell == null) return;
            var at = new Vector2(cell.transform.position.x, cell.transform.position.z);
            switch (kind)
            {
                case Phenomenon.Eruption: Erupt(at); break;
                case Phenomenon.Meteor:
                {
                    // the same path MeteorFx flies (its entry is up-wind of the impact)
                    var fx = cell.GetComponentsInChildren<MeteorFx>();
                    var wind = fx.Length > 0 ? cell.transform.rotation * fx[fx.Length - 1].wind : Vector3.right;
                    meteorImpact = cell.transform.position + Vector3.up * cell.SurfaceHeight;
                    meteorEntry  = meteorImpact - wind.normalized * 2.6f * cell0 + Vector3.up * 3.2f * cell0;
                    meteorBorn   = Time.time;
                    break;
                }
                case Phenomenon.Tornado:   AddEvent(at, 1); break;
                case Phenomenon.Sandstorm: AddEvent(at, 2); break;
                case Phenomenon.Blizzard:  AddEvent(at, 3); break;
            }
        }

        private float cell0 => cell; // the fx's cell size (PhenomenonFx.s)

        private void AddEvent(Vector2 at, int kind)
        {
            if (events.Count >= MaxEvents) events.RemoveAt(0);
            events.Add(new SkyEvent { at = at, kind = kind, born = Time.time, life = 14f }); // NaturalEvents.EffectSeconds
        }

        // ---------- Admin triggers ----------

        public void Trigger(int index, Vector2 near)
        {
            float now = Time.time;
            switch (index)
            {
                case 0: // aurora over the pole nearer the camera
                    auroraNorth = near.y > zMin + zSpan * 0.5f;
                    aurora.born = now; aurora.life = 100f;
                    break;
                case 1:
                {
                    var at = Nearest(warmSea, near) ?? near;
                    nextTyphoonRoll = now + 20f;
                    if (typhoons.Count >= MaxTyphoons) typhoons.RemoveAt(0);
                    typhoons.Add(NewTyphoon(at, now));
                    break;
                }
                case 2:
                {
                    if (fronts.Count >= MaxFronts) fronts.RemoveAt(0);
                    var f = NewFront(now);
                    f.hemisphere = near.y > zMin + zSpan * 0.5f ? 1f : -1f;
                    f.at = near;
                    fronts.Add(f);
                    break;
                }
                case 3: cumulus.at = near; cumulus.born = now; cumulus.life = 120f; break;
                case 4: cirrus.at = near; cirrus.born = now; cirrus.life = 120f; break;
                default: Erupt(Nearest(volcanoSites, near) ?? near); break;
            }
        }

        private static Vector2? Nearest(List<Vector2> points, Vector2 to)
        {
            Vector2? best = null; float bd = float.MaxValue;
            foreach (var p in points) { float d = (p - to).sqrMagnitude; if (d < bd) { bd = d; best = p; } }
            return best;
        }

        // Fades in over `fadeIn`, holds, fades out over `fadeOut` before `life` ends
        private static float Envelope(float age, float life, float fadeIn, float fadeOut) =>
            age < 0f || age > life ? 0f : Mathf.Clamp01(age / fadeIn) * Mathf.Clamp01((life - age) / fadeOut);

        // How hard it rains under the typhoons and fronts at a point (0..1), for WeatherFall
        public float RainAt(Vector2 p)
        {
            float rain = 0f;
            foreach (var t in typhoons)
            {
                float d = Wrapped(p - t.at).magnitude / t.radius;
                if (d < 1f && d > 0.1f) rain = Mathf.Max(rain, t.strength * (1f - Mathf.SmoothStep(0.5f, 1f, d)));
            }
            foreach (var f in fronts)
            {
                var (head, tail) = Ends(f);
                var q = f.at + Wrapped(p - f.at);
                float best = float.MaxValue; var prev = head;
                for (int k = 1; k <= 8; k++)
                {
                    float u = k / 8f;
                    var pt = Vector2.Lerp(Vector2.Lerp(head, f.at, u), Vector2.Lerp(f.at, tail, u), u);
                    var seg = pt - prev; var rel = q - prev;
                    float h = Mathf.Clamp01(Vector2.Dot(rel, seg) / Mathf.Max(seg.sqrMagnitude, 1e-4f));
                    best = Mathf.Min(best, (rel - seg * h).magnitude);
                    prev = pt;
                }
                if (best < f.width) rain = Mathf.Max(rain, f.strength * 0.8f * (1f - best / f.width));
            }
            return rain;
        }

        private Vector2 Wrapped(Vector2 r)
        {
            r.x -= Mathf.Round(r.x / wrap) * wrap;
            return r;
        }

        private static (Vector2 head, Vector2 tail) Ends(Front f) =>
            (f.at + new Vector2(f.length * 0.35f, f.hemisphere * f.length * 0.45f),
             f.at + new Vector2(-f.length * 0.55f * f.bend, -f.hemisphere * f.length * 0.7f));

        public void Tick(Material material)
        {
            float now = Time.time, dt = Mathf.Min(Time.deltaTime, 0.1f);
            SpawnTyphoons(now);
            SpawnFronts(now);

            for (int i = typhoons.Count - 1; i >= 0; i--)
            {
                var t = typhoons[i];
                float age = now - t.born;
                t.at += t.velocity * dt;
                t.velocity.y += Mathf.Sign(t.velocity.y) * 0.004f * cell * dt; // curving poleward with time
                bool overLand = isLand(t.at);
                if (overLand) t.life = Mathf.Min(t.life, age + 25f); // falls apart over land
                t.strength = Mathf.Clamp01(age / 15f) * Mathf.Clamp01((t.life - age) / 20f);
                if (age > t.life) typhoons.RemoveAt(i);
            }
            for (int i = fronts.Count - 1; i >= 0; i--)
            {
                var f = fronts[i];
                float age = now - f.born;
                f.at.x += 0.3f * cell * dt; // with the westerlies
                f.strength = Mathf.Clamp01(age / 20f) * Mathf.Clamp01((f.life - age) / 25f);
                if (age > f.life) fronts.RemoveAt(i);
            }
            for (int i = plumes.Count - 1; i >= 0; i--)
            {
                var p = plumes[i];
                if (p.eruption && now - p.fadeFrom > 30f) { p.target = 0f; p.eruption = false; } // the eruption dies down
                p.strength = Mathf.MoveTowards(p.strength, p.target, dt / (p.target > p.strength ? 8f : 40f));
                if (p.strength <= 0f && p.target <= 0f) plumes.RemoveAt(i);
            }
            if (material == null) return;

            for (int i = 0; i < MaxTyphoons; i++)
                typhoonData[i] = i < typhoons.Count ? new Vector4(typhoons[i].at.x, typhoons[i].at.y, typhoons[i].radius, typhoons[i].strength * typhoons[i].spin) : Vector4.zero;
            for (int i = 0; i < MaxFronts; i++)
            {
                if (i >= fronts.Count) { frontA[i] = frontB[i] = Vector4.zero; continue; }
                var f = fronts[i];
                // a quadratic arc: from the low (poleward, east) through `at` to the tail (equatorward, west)
                var (head, tail) = Ends(f);
                frontA[i] = new Vector4(head.x, head.y, f.at.x, f.at.y);
                frontB[i] = new Vector4(tail.x, tail.y, f.width, f.strength);
            }
            for (int i = 0; i < MaxPlumes; i++)
                plumeData[i] = i < plumes.Count ? new Vector4(plumes[i].at.x, plumes[i].at.y, plumes[i].strength, plumes[i].length * Mathf.Max(0.4f, plumes[i].strength)) : Vector4.zero;
            material.SetVectorArray("_Typhoons", typhoonData);
            material.SetVectorArray("_FrontsA", frontA);
            material.SetVectorArray("_FrontsB", frontB);
            material.SetVectorArray("_Plumes", plumeData);

            // ground events seen from above
            events.RemoveAll(e => now - e.born > e.life);
            for (int i = 0; i < MaxEvents; i++)
                eventData[i] = i < events.Count
                    ? new Vector4(events[i].at.x, events[i].at.y, events[i].kind, Envelope(now - events[i].born, events[i].life, 2f, 3f))
                    : Vector4.zero;
            material.SetVectorArray("_Events", eventData);

            // the meteor: its fireball until impact, then the glow of the impact and its smoke
            float mt = now - meteorBorn;
            if (mt >= 0f && mt < MeteorLife)
            {
                float fl = Mathf.Clamp01(mt / MeteorFall), g = fl * fl * 0.45f + fl * 0.55f;
                var head = Vector3.Lerp(meteorEntry, meteorImpact, g);
                var dir = new Vector2(meteorImpact.x - meteorEntry.x, meteorImpact.z - meteorEntry.z).normalized;
                bool above = head.y > SkyLayer.DeckHeight; // over the clouds it blazes; under them it glows through
                material.SetVector("_MeteorHead", new Vector4(head.x, head.z, mt < MeteorFall ? (above ? 1f : 0.55f) : 0f, 0f));
                material.SetVector("_MeteorDir", new Vector4(dir.x, dir.y, cell * 1.6f * fl + cell * 0.3f, 0f));
                float since = mt - MeteorFall;
                float glow  = since < 0f ? 0f : Mathf.Exp(-since / 1.6f);
                float smoke = since < 0f ? 0f : Envelope(since, MeteorLife - MeteorFall, 2.5f, 4f);
                material.SetVector("_Impact", new Vector4(meteorImpact.x, meteorImpact.z, glow, smoke));
            }
            else
            {
                material.SetVector("_MeteorHead", Vector4.zero);
                material.SetVector("_Impact", Vector4.zero);
            }

            // admin spells
            float a = Envelope(now - aurora.born, aurora.life, 8f, 15f);
            material.SetVector("_AuroraBoost", new Vector4(auroraNorth ? a : 0f, auroraNorth ? 0f : a, 0f, 0f));
            material.SetVector("_CumulusBoost", new Vector4(cumulus.at.x, cumulus.at.y, cell * 6f, Envelope(now - cumulus.born, cumulus.life, 10f, 15f)));
            material.SetVector("_CirrusBoost", new Vector4(cirrus.at.x, cirrus.at.y, cell * 8f, Envelope(now - cirrus.born, cirrus.life, 10f, 15f)));
        }

        private void SpawnTyphoons(float now)
        {
            if (now < nextTyphoonRoll) return;
            nextTyphoonRoll = now + 20f;
            if (warmSea.Count == 0 || typhoons.Count >= MaxTyphoons) return;
            int wanted = Mathf.Clamp(warmSea.Count / 40, 1, MaxTyphoons); // more warm sea, more of them
            if (typhoons.Count >= wanted || rng.NextDouble() > 0.4) return;
            typhoons.Add(NewTyphoon(warmSea[rng.Next(warmSea.Count)], now));
        }

        private Typhoon NewTyphoon(Vector2 at, float now)
        {
            float north = at.y > zMin + zSpan * 0.5f ? 1f : -1f;
            return new Typhoon
            {
                at = at,
                velocity = new Vector2(-0.18f, 0.06f * north) * cell * (0.8f + 0.4f * (float)rng.NextDouble()),
                radius = cell * (2.2f + 1.6f * (float)rng.NextDouble()),
                spin = north, // anticlockwise seen from above in the north
                born = now,
                life = 150f + 150f * (float)rng.NextDouble(),
            };
        }

        private void SpawnFronts(float now)
        {
            if (now < nextFrontRoll) return;
            nextFrontRoll = now + 18f;
            if (fronts.Count >= MaxFronts || rng.NextDouble() > 0.5) return;
            fronts.Add(NewFront(now));
        }

        private Front NewFront(float now)
        {
            float hemisphere = rng.NextDouble() < 0.5 ? 1f : -1f;
            float lat = 0.42f + 0.2f * (float)rng.NextDouble();
            float z = zMin + zSpan * 0.5f + hemisphere * lat * zSpan * 0.5f;
            return new Front
            {
                at = new Vector2(xMin + wrap * (float)rng.NextDouble(), z),
                bend = 0.6f + 0.8f * (float)rng.NextDouble(),
                length = cell * (7f + 6f * (float)rng.NextDouble()),
                width = cell * (0.45f + 0.3f * (float)rng.NextDouble()),
                hemisphere = hemisphere,
                born = now,
                life = 160f + 140f * (float)rng.NextDouble(),
            };
        }
    }
}
