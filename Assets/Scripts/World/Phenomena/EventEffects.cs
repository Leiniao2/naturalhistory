using System.Collections.Generic;
using UnityEngine;

namespace NaturalHistory.World
{
    // The rare natural events NaturalEvents plays on the map. Each is a short animation built from
    // PhenomenonFx parts: angular rocks and water on the map material, soft see-through smoke, and
    // additive glow for fire and lava, with point lights and camera shake for the violent moments.
    // `toward` (where used) is the neighbouring tile it runs into, `wind` the horizontal direction it
    // drifts with (unit length, tile space).

    static class FxColors
    {
        public static readonly Color Fire    = new(2.6f, 1.3f, 0.35f);  // > 1: stays bright under shading
        public static readonly Color Lava    = new(2.2f, 0.75f, 0.15f);
        public static readonly Color Ember   = new(1.1f, 0.3f, 0.08f);
        public static readonly Color Basalt  = new(0.22f, 0.2f, 0.19f);
        public static readonly Color Ash     = new(0.32f, 0.3f, 0.29f);
        public static readonly Color Dust    = new(0.62f, 0.52f, 0.4f);
        public static readonly Color Sand    = new(1.05f, 0.86f, 0.58f);
        public static readonly Color Rock    = new(0.5f, 0.46f, 0.42f);
        public static readonly Color Snow    = new(1.25f, 1.28f, 1.32f);
        public static readonly Color Ice     = new(0.82f, 0.95f, 1.12f);
        public static readonly Color Foam    = new(1.25f, 1.3f, 1.35f);
        public static readonly Color Muddy   = new(0.46f, 0.47f, 0.38f);
        public static readonly Color Sea     = new(0.16f, 0.36f, 0.52f);
        public static readonly Color Storm   = new(0.36f, 0.37f, 0.4f);
        public static readonly Color Debris  = new(0.36f, 0.28f, 0.18f);

        // For the soft (FxSmoke / FxGlow) parts
        public static readonly Color Smoke     = new(0.30f, 0.28f, 0.27f);
        public static readonly Color DarkSmoke = new(0.12f, 0.11f, 0.11f);
        public static readonly Color WhiteHot  = new(4f, 3.4f, 2.4f);
        public static readonly Color Flame     = new(3f, 1.2f, 0.25f);
        public static readonly Color Lightning = new(3f, 3.4f, 4.5f);
        public static readonly Color Wood      = new(0.42f, 0.30f, 0.18f);
        public static readonly Color Spray     = new(0.92f, 0.96f, 1f);
    }

    // ---- Meteor: a fireball streaks down, a blinding flash and shockwave, a mushroom of dust,
    // glowing debris and a smoking crater (a towering splash on water)

    public class MeteorFx : PhenomenonFx
    {
        public Vector3 wind = Vector3.right;
        private const float Fall = 1.8f; // seconds until impact
        private Part head;
        private Part[] core, fire, smoke, flash, ring, cloud, debris, embers, crater, pool;
        private Light light;
        private Vector3 impact, entry;
        private bool water, shaken;
        private Vector3[] ringDir, debrisVel, cloudOff;

        protected override void Build()
        {
            water  = cell.IsWater;
            impact = OnGround(new Vector3(R(-0.2f, 0.2f), 0f, R(-0.2f, 0.2f)) * s);
            entry  = impact - wind * 2.6f * s + Vector3.up * 3.2f * s;
            head   = AddRocks(1, "Meteor")[0];
            core   = AddGlow(2, "Fireball");
            fire   = AddGlow(16, "Fire");
            smoke  = AddSmoke(18, "SmokeTrail");
            flash  = AddGlow(2, "Flash");
            ring   = AddSmoke(22, "Shockwave");
            cloud  = AddSmoke(16, water ? "Spray" : "Mushroom");
            debris = AddRocks(12, "Debris");
            embers = AddGlow(12, "Ember");
            crater = water ? new Part[0] : AddRocks(10, "Crater");
            pool   = water ? new Part[0] : AddGlow(1, "MoltenPool");
            light  = AddLight(new Color(1f, 0.7f, 0.4f), 5f);

            ringDir = new Vector3[ring.Length];
            for (int i = 0; i < ring.Length; i++)
            {
                float a = (i + R(-0.3f, 0.3f)) / ring.Length * Mathf.PI * 2f;
                ringDir[i] = new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a));
            }
            debrisVel = new Vector3[debris.Length];
            for (int i = 0; i < debris.Length; i++)
            {
                float a = R(0f, Mathf.PI * 2f);
                debrisVel[i] = new Vector3(Mathf.Cos(a) * R(0.3f, 0.75f), R(1.0f, 1.8f), Mathf.Sin(a) * R(0.3f, 0.75f)) * s;
            }
            cloudOff = new Vector3[cloud.Length];
            for (int i = 0; i < cloud.Length; i++)
                cloudOff[i] = new Vector3(R(-1f, 1f), R(0f, 1f), R(-1f, 1f));
        }

        private Vector3 Path(float f) => Vector3.Lerp(entry, impact, f * f * 0.45f + f * 0.55f); // speeds up as it falls

        protected override void Animate(float u, float t)
        {
            if (t < Fall)
            {
                float f = t / Fall;
                var p = Path(f);
                Show(head, p, Vector3.one * 0.07f * s, FxColors.Ember, Quaternion.Euler(t * 400f, t * 300f, 0f));
                float flicker = 1f + 0.15f * Mathf.Sin(t * 53f);
                Show(core[0], p, 0.11f * s * flicker, FxColors.WhiteHot, 1f);
                Show(core[1], p, 0.26f * s * flicker, FxColors.Flame, 0.8f);
                for (int i = 0; i < fire.Length; i++)
                {
                    float fb = Mathf.Max(0f, f - (i + 1) * 0.018f);
                    float k  = 1f - i / (float)fire.Length;
                    Show(fire[i], Path(fb), (0.05f + 0.13f * k) * s, Color.Lerp(FxColors.Ember, FxColors.Flame, k), k * Ramp(f, 0f, 0.05f));
                }
                for (int i = 0; i < smoke.Length; i++)
                {
                    float fb = Mathf.Max(0f, f - 0.05f - i * 0.035f);
                    Show(smoke[i], Path(fb) + Vector3.up * i * 0.01f * s, (0.09f + 0.012f * i) * s, FxColors.Smoke * 1.6f,
                         0.7f * (1f - i / (float)smoke.Length) * Ramp(f, 0.05f + i * 0.035f, 0.1f + i * 0.035f));
                }
                SetLight(light, p, Mathf.Lerp(2f, 8f, f));
                foreach (var x in flash) Hide(x);
                foreach (var x in ring) Hide(x);
                foreach (var x in cloud) Hide(x);
                foreach (var x in debris) Hide(x);
                foreach (var x in embers) Hide(x);
                foreach (var x in crater) Hide(x);
                foreach (var x in pool) Hide(x);
                return;
            }

            if (!shaken) { shaken = true; Shake(impact, 2.2f, 1.4f); }
            Hide(head);
            foreach (var x in core) Hide(x);
            float a = t - Fall;
            float left = duration - Fall;
            float fade = 1f - Ramp(a, left - 1.5f, left);

            // the fire trail goes out, the smoke trail hangs and drifts away
            for (int i = 0; i < fire.Length; i++) Hide(fire[i]);
            for (int i = 0; i < smoke.Length; i++)
            {
                float fb = Mathf.Max(0f, 1f - 0.05f - i * 0.035f);
                Show(smoke[i], Path(fb) + Vector3.up * (i * 0.01f + a * 0.05f) * s + wind * a * 0.04f * s,
                     (0.09f + 0.012f * i) * s * (1f + 0.3f * a), FxColors.Smoke * 1.6f,
                     0.7f * (1f - i / (float)smoke.Length) * (1f - Ramp(a, 0.5f, 3.5f)));
            }

            // blinding flash and a light that lights up the whole neighbourhood
            Show(flash[0], impact + Vector3.up * 0.1f * s, Mathf.Lerp(0.3f, 1.3f, Ramp(a, 0f, 0.3f)) * s, FxColors.WhiteHot, 1f - Ramp(a, 0.1f, 0.9f));
            Show(flash[1], impact + Vector3.up * 0.15f * s, Mathf.Lerp(0.2f, 0.6f, Ramp(a, 0f, 0.6f)) * s, FxColors.Flame, 1f - Ramp(a, 0.3f, 1.8f));
            SetLight(light, impact + Vector3.up * 0.3f * s, 30f * Mathf.Exp(-a * 2.5f) + (water ? 0f : 2f * (1f - Ramp(a, 1f, 5f))));

            // shockwave: a ring of dust (or spray) racing out over the ground
            for (int i = 0; i < ring.Length; i++)
            {
                float r = (1f - Mathf.Exp(-a * 2.2f)) * 1.1f * s;
                var p = impact + ringDir[i] * r;
                p.y = Ground(p) + 0.05f * s;
                Show(ring[i], p, (0.12f + 0.12f * Ramp(a, 0f, 1.5f)) * s, water ? FxColors.Spray : FxColors.Dust * 1.1f,
                     0.85f * Ramp(a, 0f, 0.1f) * (1f - Ramp(a, 0.6f, 3f)));
            }

            // a mushroom of dust (or a column of spray) climbing over the impact
            for (int i = 0; i < cloud.Length; i++)
            {
                var o = cloudOff[i];
                float rise = (1f - Mathf.Exp(-a * (water ? 2f : 1.1f))) * (water ? 0.8f : 1.3f) * s * (0.4f + 0.6f * o.y);
                float spread = (water ? 0.08f : 0.12f + 0.22f * o.y * Ramp(a, 0.5f, 3f)) * s;
                var p = impact + new Vector3(o.x * spread, rise, o.z * spread) + wind * a * 0.03f * s;
                if (water) p.y = Mathf.Lerp(p.y, impact.y, Ramp(a, 1.2f, 3f)); // the spray falls back
                Show(cloud[i], p, (0.12f + 0.08f * o.y) * s * (1f + 0.3f * a),
                     water ? FxColors.Spray : Color.Lerp(FxColors.DarkSmoke * 2f, FxColors.Dust, o.y),
                     0.9f * Ramp(a, 0.05f, 0.3f) * fade * (water ? 1f - Ramp(a, 1.5f, 3.5f) : 1f));
            }

            // glowing rocks thrown out on high arcs, cooling as they land
            float g = 3f * s;
            for (int i = 0; i < debris.Length; i++)
            {
                var v = debrisVel[i];
                float flight = v.y / g * 2f, tt = Mathf.Min(a, flight);
                var p = impact + new Vector3(v.x * tt, v.y * tt - 0.5f * g * tt * tt, v.z * tt);
                p.y = Mathf.Max(p.y, Ground(p) + 0.012f * s);
                float heat = 1f - Ramp(a, flight * 0.6f, flight + 1.5f);
                Show(debris[i], p, Vector3.one * (0.022f + 0.012f * (i % 3)) * s * fade, water ? FxColors.Foam : Color.Lerp(FxColors.Basalt, FxColors.Ember, heat),
                     Quaternion.Euler(tt * 300f * (i + 1), tt * 120f, 0f));
                Show(embers[i], p, 0.06f * s, FxColors.Flame, water ? 0f : heat * 0.8f);
            }

            // crater: a raised rim of blackened rock round a molten pool that dims and crusts over
            for (int i = 0; i < crater.Length; i++)
            {
                float ang = i / (float)crater.Length * Mathf.PI * 2f;
                var p = OnGround(impact + new Vector3(Mathf.Cos(ang), 0f, Mathf.Sin(ang)) * 0.14f * s, 0.008f * s);
                Show(crater[i], p, new Vector3(0.06f, 0.035f, 0.05f) * s * Ramp(a, 0f, 0.25f) * fade,
                     Color.Lerp(FxColors.Ember, FxColors.Basalt, Ramp(a, 0.5f, 3f)), Quaternion.Euler(0f, ang * Mathf.Rad2Deg, 15f));
            }
            foreach (var x in pool)
                Show(x, impact + Vector3.up * 0.01f * s, new Vector3(0.16f, 0.03f, 0.16f) * s, FxColors.Lava, 0.9f * (1f - Ramp(a, 0.5f, left)), Quaternion.identity);
        }
    }

    // ---- Volcano eruption: a blast and shockwave, a lava fountain, a towering black ash column
    // with lightning, glowing bombs trailing smoke, pyroclastic flows and lava down the flanks

    public class EruptionFx : PhenomenonFx
    {
        public Vector3 wind = Vector3.right;
        private Part[] ventGlow, fountain, ash, bolts, bombs, bombGlow, bombSmoke, flows, lava, crust, blast;
        private Light ventLight, boltLight;
        private Vector3 vent;
        private float volcanoTop;
        private float[] ashOffset, fountainOffset, bombOffset, flowOffset, boltAt;
        private Vector3[] bombDir, flowDir, fountainDir, ashJitter, boltPos;
        private int lastBlast = -1;

        protected override void Build()
        {
            // the crater is the top of the volcano prop, if there is one
            float top = cell.SurfaceHeight + 0.85f * s;
            foreach (var mf in cell.GetComponentsInChildren<MeshFilter>())
                if (mf.sharedMesh != null && mf.sharedMesh.name == "Volcano")
                    top = mf.transform.localPosition.y + mf.sharedMesh.bounds.max.y * mf.transform.localScale.y - 0.03f * s;
            vent = new Vector3(0f, top, 0f);
            volcanoTop = top;

            blast     = AddGlow(2, "Blast");
            ventGlow  = AddGlow(2, "Vent");
            fountain  = AddGlow(26, "Fountain");
            ash       = AddSmoke(44, "Ash");
            bolts     = AddGlow(3, "Lightning");
            bombs     = AddRocks(14, "Bomb");
            bombGlow  = AddGlow(14, "BombGlow");
            bombSmoke = AddSmoke(14, "BombSmoke");
            flows     = AddSmoke(28, "PyroclasticFlow");
            lava      = AddGlow(24, "LavaFlow");
            crust     = AddRocks(18, "LavaCrust");
            ventLight = AddLight(new Color(1f, 0.45f, 0.15f), 4f);
            boltLight = AddLight(new Color(0.7f, 0.8f, 1f), 4f);

            ashOffset = new float[ash.Length];
            ashJitter = new Vector3[ash.Length];
            for (int i = 0; i < ash.Length; i++)
            {
                ashOffset[i] = (i + R(-0.3f, 0.3f)) / ash.Length;
                ashJitter[i] = new Vector3(R(-1f, 1f), R(0.8f, 1.2f), R(-1f, 1f));
            }
            fountainOffset = new float[fountain.Length];
            fountainDir    = new Vector3[fountain.Length];
            for (int i = 0; i < fountain.Length; i++)
            {
                fountainOffset[i] = R(0f, 1f);
                float a = R(0f, Mathf.PI * 2f);
                fountainDir[i] = new Vector3(Mathf.Cos(a) * R(0.05f, 0.25f), R(0.8f, 1.2f), Mathf.Sin(a) * R(0.05f, 0.25f));
            }
            bombOffset = new float[bombs.Length];
            bombDir    = new Vector3[bombs.Length];
            for (int i = 0; i < bombs.Length; i++)
            {
                bombOffset[i] = R(0f, 1f);
                float a = R(0f, Mathf.PI * 2f);
                bombDir[i] = new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a)) * R(0.35f, 0.9f);
            }
            flowDir = new Vector3[4];
            float a0 = R(0f, Mathf.PI * 2f);
            for (int i = 0; i < flowDir.Length; i++)
            {
                float a = a0 + i * Mathf.PI * 0.5f + R(-0.3f, 0.3f);
                flowDir[i] = new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a));
            }
            flowOffset = new float[flows.Length];
            for (int i = 0; i < flows.Length; i++) flowOffset[i] = R(0f, 1f);
            boltAt  = new float[bolts.Length];
            boltPos = new Vector3[bolts.Length];
            for (int i = 0; i < bolts.Length; i++) boltAt[i] = -10f;
        }

        // A point on the flank `along` (0 = vent, 1 = foot of the volcano and beyond) in direction d
        private Vector3 Flank(Vector3 d, float along, float lift)
        {
            var flat = d * along * 0.75f * s;
            var p = new Vector3(flat.x, 0f, flat.z);
            float ground = Ground(p);
            p.y = Mathf.Max(ground, Mathf.Lerp(volcanoTop, ground, Mathf.Pow(Mathf.Clamp01(along / 0.75f), 0.6f))) + lift;
            return p;
        }

        protected override void Animate(float u, float t)
        {
            float power = Envelope(u, 0.04f, 0.25f);

            // opening blast: flash, shockwave of light, a hard shake; then a smaller blast every few seconds
            int blastIndex = t < 0.4f ? -1 : Mathf.FloorToInt((t - 0.4f) / 3.2f);
            if (blastIndex != lastBlast && u < 0.8f)
            {
                lastBlast = blastIndex;
                Shake(vent, blastIndex == 0 ? 2.5f : 1f, blastIndex == 0 ? 2f : 0.8f);
            }
            float sinceBlast = t < 0.4f ? 99f : (t - 0.4f) % 3.2f;
            float big = blastIndex == 0 ? 1f : 0.5f;
            Show(blast[0], vent + Vector3.up * 0.1f * s, Mathf.Lerp(0.2f, 1.4f * big, Ramp(sinceBlast, 0f, 0.35f)) * s, FxColors.WhiteHot, (1f - Ramp(sinceBlast, 0.1f, 0.8f)) * power);
            Show(blast[1], vent + Vector3.up * 0.2f * s, Mathf.Lerp(0.3f, 0.9f * big, Ramp(sinceBlast, 0f, 0.6f)) * s, FxColors.Flame, (1f - Ramp(sinceBlast, 0.3f, 1.5f)) * power);

            float flick = 0.85f + 0.15f * Mathf.Sin(t * 13f) + 0.1f * Mathf.Sin(t * 31f);
            Show(ventGlow[0], vent + Vector3.up * 0.03f * s, 0.18f * s * flick, FxColors.Flame, power);
            Show(ventGlow[1], vent + Vector3.up * 0.05f * s, 0.4f * s * flick, FxColors.Lava, 0.6f * power);
            SetLight(ventLight, vent + Vector3.up * 0.25f * s, (6f + 4f * flick + 18f * (1f - Ramp(sinceBlast, 0f, 0.8f))) * power);

            // lava fountain: molten spray leaping out of the crater and falling back
            for (int i = 0; i < fountain.Length; i++)
            {
                float c  = Mathf.Repeat(t / 1.1f + fountainOffset[i], 1f);
                var d    = fountainDir[i];
                float tt = c * 0.9f;
                var p = vent + new Vector3(d.x * tt * s, (d.y * 1.4f * tt - 1.55f * tt * tt) * s, d.z * tt * s);
                Show(fountain[i], p, (0.05f + 0.03f * (i % 3)) * s, Color.Lerp(FxColors.WhiteHot, FxColors.Lava, c), power * (1f - Ramp(c, 0.7f, 1f)));
            }

            // ash column: dense black puffs blasting up, swelling and spreading downwind into a canopy
            for (int i = 0; i < ash.Length; i++)
            {
                float c  = Mathf.Repeat(t / 5f + ashOffset[i], 1f);
                var j    = ashJitter[i];
                float up = (1f - (1f - c) * (1f - c)) * 3f * s * j.y;
                float canopy = Ramp(c, 0.55f, 1f);
                var p = vent + Vector3.up * up + wind * (canopy * canopy * 1.4f * s)
                      + new Vector3(j.x, 0f, j.z) * (0.06f + 0.5f * canopy) * s;
                float size = Mathf.Lerp(0.12f, 0.55f, c) * s * Ramp(c, 0f, 0.05f);
                var col = Color.Lerp(FxColors.DarkSmoke, FxColors.Smoke * 1.4f, c);
                col = Color.Lerp(col, FxColors.Ember, 0.35f * (1f - Ramp(c, 0f, 0.15f))); // lit from below at the vent
                Show(ash[i], p, size, col, power * 0.95f * (1f - Ramp(c, 0.8f, 1f)));
            }

            // volcanic lightning flickering inside the column
            for (int i = 0; i < bolts.Length; i++)
            {
                if (t - boltAt[i] > R(0.6f, 2.2f) && power > 0.3f && rng.NextDouble() < 0.04)
                {
                    boltAt[i]  = t;
                    boltPos[i] = vent + Vector3.up * R(0.9f, 2.2f) * s + wind * R(0f, 0.6f) * s + new Vector3(R(-0.2f, 0.2f), 0f, R(-0.2f, 0.2f)) * s;
                }
                float on = Mathf.Clamp01(1f - (t - boltAt[i]) / 0.12f);
                Show(bolts[i], boltPos[i], new Vector3(0.025f, 0.45f, 0.025f) * s, FxColors.Lightning, on,
                     Quaternion.Euler(R(-25f, 25f), i * 70f, R(-25f, 25f)));
            }
            float boltOn = 0f; int lit = 0;
            for (int i = 0; i < bolts.Length; i++)
            {
                float on = Mathf.Clamp01(1f - (t - boltAt[i]) / 0.12f);
                if (on > boltOn) { boltOn = on; lit = i; }
            }
            SetLight(boltLight, boltPos[lit], 25f * boltOn);

            // lava bombs flung far on high arcs, glowing and trailing smoke, cooling where they land
            float g = 2.8f * s;
            for (int i = 0; i < bombs.Length; i++)
            {
                float c  = Mathf.Repeat(t / 2.6f + bombOffset[i], 1f);
                float tt = c * 1.5f;
                var v = bombDir[i] * s;
                var p = vent + new Vector3(v.x * tt, 1.7f * s * tt - 0.5f * g * tt * tt, v.z * tt);
                float ground = Ground(p) + 0.015f * s;
                bool landed = p.y < ground;
                if (landed) p.y = ground;
                float heat = landed ? 1f - Ramp(c, 0.65f, 0.95f) : 1f;
                float size = (0.03f + 0.012f * (i % 3)) * s * power * (1f - Ramp(c, 0.9f, 1f));
                Show(bombs[i], p, Vector3.one * size, Color.Lerp(FxColors.Basalt, FxColors.Ember, heat), Quaternion.Euler(c * 600f, i * 40f, 0f));
                Show(bombGlow[i], p, size * 3f, FxColors.Flame, heat * power * 0.9f);
                var trail = vent + new Vector3(v.x * tt * 0.8f, 1.7f * s * tt * 0.8f - 0.5f * g * tt * tt * 0.64f, v.z * tt * 0.8f);
                Show(bombSmoke[i], trail, 0.08f * s * (0.5f + c), FxColors.Smoke, landed ? 0f : 0.55f * power);
            }

            // pyroclastic flows: dense grey avalanches of hot ash pouring down the flanks
            float flowing = Ramp(u, 0.12f, 0.25f) * (1f - Ramp(u, 0.75f, 0.95f));
            for (int i = 0; i < flows.Length; i++)
            {
                var d = flowDir[i % flowDir.Length];
                float c = Mathf.Repeat(t / 3.5f + flowOffset[i], 1f);
                float along = c * 1.15f;
                var side = Vector3.Cross(Vector3.up, d) * Mathf.Sin(i * 1.7f) * (0.05f + 0.15f * c) * s;
                var p = Flank(d, along, (0.04f + 0.08f * c) * s) + side;
                Show(flows[i], p, (0.1f + 0.16f * c) * s, Color.Lerp(FxColors.Smoke * 1.2f, FxColors.Dust * 0.8f, c),
                     0.9f * flowing * Ramp(c, 0f, 0.08f) * (1f - Ramp(c, 0.75f, 1f)));
            }

            // lava streams: a glowing front creeping down the flanks, crusting over behind it
            float front = Ramp(u, 0.06f, 0.75f);
            for (int i = 0; i < lava.Length; i++)
            {
                int stream = i % 3;
                float along = (i / 3 + 1) / 8f;
                var p = Flank(flowDir[stream], along, 0.012f * s);
                float shown = Ramp(front, along - 0.12f, along);
                float heat  = 1f - Ramp(front - along, 0.1f, 0.7f);
                Show(lava[i], p, new Vector3(0.09f, 0.035f, 0.09f) * s * (0.7f + 0.3f * heat), FxColors.Lava,
                     shown * Mathf.Max(heat, 0.25f) * (1f - Ramp(u, 0.92f, 1f)), Quaternion.LookRotation(flowDir[stream]));
            }
            for (int i = 0; i < crust.Length; i++)
            {
                int stream = i % 3;
                float along = (i / 3 + 1) / 7f;
                var p = Flank(flowDir[stream], along, 0.008f * s);
                float cooled = Ramp(front - along, 0.15f, 0.5f);
                Show(crust[i], p, new Vector3(0.05f, 0.02f, 0.05f) * s * cooled * (1f - Ramp(u, 0.95f, 1f)), FxColors.Basalt,
                     Quaternion.Euler(0f, i * 47f, 0f));
            }
        }
    }

    // ---- Tornado: a dark wall cloud spins down a churning funnel that tears across the plain,
    // throwing up a skirt of dust and whirling debris, with lightning in the cloud

    public class TornadoFx : PhenomenonFx
    {
        public Vector3 wind = Vector3.right;
        private const int Rings = 12, PerRing = 4;
        private Part[] funnel, cloud, skirt, debris, bolt;
        private Light boltLight;
        private Vector3 start, end, boltPos;
        private float wobble, boltAt = -10f;
        private Vector3[] debrisSeed;

        protected override void Build()
        {
            start  = -wind * 0.6f * s + Vector3.Cross(wind, Vector3.up) * R(-0.2f, 0.2f) * s;
            end    = wind * 1.4f * s;
            wobble = R(0f, 10f);
            funnel = AddSmoke(Rings * PerRing, "Funnel");
            cloud  = AddSmoke(14, "WallCloud");
            skirt  = AddSmoke(14, "DustSkirt");
            debris = AddRocks(16, "Debris");
            bolt   = AddGlow(1, "Lightning");
            boltLight = AddLight(new Color(0.75f, 0.8f, 1f), 5f);
            debrisSeed = new Vector3[debris.Length];
            for (int i = 0; i < debris.Length; i++) debrisSeed[i] = new Vector3(R(0f, 6.3f), R(0.4f, 1f), R(0.5f, 1.5f));
        }

        protected override void Animate(float u, float t)
        {
            var baseP = Vector3.Lerp(start, end, Ramp(u, 0.05f, 0.95f));
            baseP += new Vector3(Mathf.Sin(t * 0.9f + wobble), 0f, Mathf.Cos(t * 0.7f + wobble)) * 0.15f * s;
            float ground = Ground(baseP);
            float height = 1.7f * s;
            float down = Envelope(u, 0.15f, 0.15f);       // the funnel reaches down, then lifts back up
            float sky  = Envelope(u, 0.06f, 0.06f);
            var top = baseP + wind * 0.25f * s;           // the top lags behind, so the funnel leans

            for (int i = 0; i < cloud.Length; i++)
            {
                float a = i / (float)cloud.Length * Mathf.PI * 2f + t * 0.35f;
                float r = (i % 2 == 0 ? 0.25f : 0.5f) * s;
                var p = top + new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a)) * r;
                p.y = ground + height + (0.05f + 0.05f * (i % 3)) * s;
                Show(cloud[i], p, new Vector3(0.42f, 0.2f, 0.42f) * s, FxColors.DarkSmoke * 2.2f, 0.92f * sky, Quaternion.Euler(0f, a * 30f, 0f));
            }
            for (int r = 0; r < Rings; r++)
            {
                float h = r / (Rings - 1f);                   // 0 at the ground, 1 at the cloud
                if (h < 1f - down) { for (int k = 0; k < PerRing; k++) Hide(funnel[r * PerRing + k]); continue; }
                float radius = Mathf.Lerp(0.04f, 0.24f, h * h) * s;
                var centre = Vector3.Lerp(baseP, top, h) + new Vector3(Mathf.Sin(t * 3f + h * 4f), 0f, Mathf.Cos(t * 2.6f + h * 4f)) * 0.03f * s;
                centre.y = ground + h * height;
                for (int k = 0; k < PerRing; k++)
                {
                    float a = t * (11f - 5f * h) + k * Mathf.PI * 2f / PerRing + r * 0.7f;
                    var p = centre + new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a)) * radius;
                    var col = Color.Lerp(FxColors.Dust, FxColors.Storm, Ramp(h, 0f, 0.3f));
                    Show(funnel[r * PerRing + k], p, radius * 1.1f + 0.05f * s, col, 0.85f);
                }
            }
            // dust and debris skirt churning round the foot of the funnel
            for (int i = 0; i < skirt.Length; i++)
            {
                float a = t * 5f + i * Mathf.PI * 2f / skirt.Length;
                float rr = (0.15f + 0.1f * Mathf.Sin(t * 2f + i)) * s;
                var p = baseP + new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a)) * rr;
                p.y = ground + (0.06f + 0.05f * Mathf.Sin(t * 3f + i * 2f)) * s;
                Show(skirt[i], p, 0.16f * s, FxColors.Dust, 0.75f * Ramp(down, 0.85f, 1f));
            }
            for (int i = 0; i < debris.Length; i++)
            {
                var d = debrisSeed[i];
                float a  = t * 6f * d.z + d.x;
                float lift = Mathf.Repeat(t * 0.35f * d.z + d.x, 1f);
                float rr = (0.1f + 0.2f * lift) * s;
                var p = Vector3.Lerp(baseP, top, lift) + new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a)) * rr;
                p.y = ground + lift * height * 0.7f * d.y;
                Show(debris[i], p, Vector3.one * (0.015f + 0.01f * (i % 3)) * s * Ramp(down, 0.8f, 1f), i % 3 == 0 ? FxColors.Wood : FxColors.Debris,
                     Quaternion.Euler(t * 300f, i * 50f, t * 200f));
            }
            // lightning in the wall cloud now and then
            if (t - boltAt > 1.2f && sky > 0.5f && rng.NextDouble() < 0.03)
            {
                boltAt  = t;
                boltPos = top + new Vector3(R(-0.4f, 0.4f), 0f, R(-0.4f, 0.4f)) * s;
                boltPos.y = ground + height * R(0.55f, 0.85f);
                Shake(boltPos, 0.3f, 0.3f);
            }
            float on = Mathf.Clamp01(1f - (t - boltAt) / 0.12f);
            Show(bolt[0], boltPos, new Vector3(0.03f, 0.6f, 0.03f) * s, FxColors.Lightning, on, Quaternion.Euler(R(-20f, 20f), 0f, R(-20f, 20f)));
            SetLight(boltLight, boltPos, 30f * on);
        }
    }

    // ---- Sandstorm: a towering, billowing wall of sand rolls across the desert, sand streaming
    // along the ground ahead of it

    public class SandstormFx : PhenomenonFx
    {
        public Vector3 wind = Vector3.right;
        private Part[] wall, streaks;
        private Vector3[] home, streakHome;
        private float[] size, spin, streakOffset;

        protected override void Build()
        {
            wall    = AddSmoke(60, "SandWall");
            streaks = AddSmoke(24, "Streak");
            home = new Vector3[wall.Length];
            size = new float[wall.Length];
            spin = new float[wall.Length];
            var across = Vector3.Cross(Vector3.up, wind);
            for (int i = 0; i < wall.Length; i++)
            {
                // a band 3 cells wide and 0.9 deep, tallest at the front (a haboob's leading wall)
                float depth = R(0f, 1f);
                home[i] = across * R(-1.5f, 1.5f) * s - wind * depth * 0.9f * s + Vector3.up * R(0f, 1f) * (1.0f - 0.55f * depth) * s;
                size[i] = R(0.28f, 0.5f) * s;
                spin[i] = R(-40f, 40f);
            }
            streakHome   = new Vector3[streaks.Length];
            streakOffset = new float[streaks.Length];
            for (int i = 0; i < streaks.Length; i++)
            {
                streakHome[i]   = across * R(-1.4f, 1.4f) * s;
                streakOffset[i] = R(0f, 1f);
            }
        }

        protected override void Animate(float u, float t)
        {
            var front = Vector3.Lerp(-wind * 1.9f * s, wind * 2.1f * s, u);
            float env = Envelope(u, 0.12f, 0.2f);
            for (int i = 0; i < wall.Length; i++)
            {
                // puffs at the front roll up and over, the way a dust wall curls
                float roll = Mathf.Sin(t * 1.4f + i * 0.9f);
                var p = front + home[i] + wind * roll * 0.06f * s + Vector3.Cross(Vector3.up, wind) * Mathf.Cos(t * 1.1f + i) * 0.05f * s;
                p.y = Ground(p) + home[i].y + 0.05f * s * roll;
                float frontness = 1f - Mathf.Clamp01(Vector3.Dot(-home[i], wind) / (0.9f * s));
                var col = Color.Lerp(FxColors.Sand * 0.75f, FxColors.Sand * 1.05f, 0.5f + 0.5f * Mathf.Sin(i)) * Mathf.Lerp(0.85f, 1f, home[i].y / s);
                Show(wall[i], p, size[i] * (1f + 0.1f * roll), col, env * Mathf.Lerp(0.45f, 0.9f, frontness));
            }
            for (int i = 0; i < streaks.Length; i++)
            {
                float c = Mathf.Repeat(t / 1.4f + streakOffset[i], 1f);
                var p = front + streakHome[i] + wind * Mathf.Lerp(0.1f, 0.9f, c) * s;
                p.y = Ground(p) + 0.03f * s;
                Show(streaks[i], p, new Vector3(0.2f, 0.035f, 0.08f) * s, FxColors.Sand, 0.6f * env * Mathf.Sin(c * Mathf.PI), Quaternion.LookRotation(wind));
            }
        }
    }

    // ---- Blizzard: thick driving snow and a white-out haze sweep over the tile, with spindrift
    // racing along the ground

    public class BlizzardFx : PhenomenonFx
    {
        public Vector3 wind = Vector3.right;
        private Part[] flakes, haze, drift;
        private Vector3[] flakeHome, hazeHome;
        private float[] flakeOffset;

        protected override void Build()
        {
            flakes = AddSmoke(140, "Snow");
            haze   = AddSmoke(18, "WhiteOut");
            drift  = AddSmoke(16, "Spindrift");
            flakeHome   = new Vector3[flakes.Length];
            flakeOffset = new float[flakes.Length];
            for (int i = 0; i < flakes.Length; i++)
            {
                float a = R(0f, Mathf.PI * 2f), d = Mathf.Sqrt(R(0f, 1f)) * 1.3f * s;
                flakeHome[i]   = new Vector3(Mathf.Cos(a) * d, 0f, Mathf.Sin(a) * d);
                flakeOffset[i] = R(0f, 1f);
            }
            hazeHome = new Vector3[haze.Length];
            for (int i = 0; i < haze.Length; i++)
            {
                float a = R(0f, Mathf.PI * 2f), d = Mathf.Sqrt(R(0f, 1f)) * 1.1f * s;
                hazeHome[i] = new Vector3(Mathf.Cos(a) * d, R(0.1f, 0.6f) * s, Mathf.Sin(a) * d);
            }
        }

        protected override void Animate(float u, float t)
        {
            float env = Envelope(u, 0.15f, 0.2f);
            for (int i = 0; i < flakes.Length; i++)
            {
                float c = Mathf.Repeat(t / 1.3f + flakeOffset[i], 1f);    // top → ground, driven sideways
                var p = flakeHome[i] - wind * 0.6f * s + wind * c * 1.2f * s
                      + new Vector3(Mathf.Sin(t * 3f + i), 0f, Mathf.Cos(t * 2.7f + i)) * 0.02f * s;
                p.y = Ground(p) + (1f - c) * 1.1f * s;
                bool shown = i < flakes.Length * env;
                Show(flakes[i], p, new Vector3(0.016f, 0.016f, 0.03f) * s, FxColors.Snow, shown ? 0.95f : 0f, Quaternion.LookRotation(wind + Vector3.down * 0.6f));
            }
            for (int i = 0; i < haze.Length; i++)
            {
                var p = hazeHome[i] + wind * Mathf.Sin(t * 0.4f + i) * 0.2f * s;
                p.y = Ground(p) + hazeHome[i].y;
                Show(haze[i], p, 0.5f * s, FxColors.Snow, 0.3f * env);
            }
            for (int i = 0; i < drift.Length; i++)
            {
                float c = Mathf.Repeat(t / 2.2f + i / (float)drift.Length, 1f);
                var p = flakeHome[i * 7] - wind * 0.7f * s + wind * c * 1.4f * s;
                p.y = Ground(p) + 0.03f * s;
                Show(drift[i], p, new Vector3(0.22f, 0.06f, 0.14f) * s, FxColors.Snow, 0.7f * env * Mathf.Sin(c * Mathf.PI), Quaternion.LookRotation(wind));
            }
        }
    }

    // ---- Flood: churning brown water spreads over the river's tiles, foaming and carrying logs,
    // then drains away

    public class FloodFx : PhenomenonFx
    {
        public List<HexCell> area = new();
        public Vector3 flow = Vector3.right; // downstream
        private Part[] sheets, foam, swirl, logs;
        private Vector3[] centres;
        private float level;

        protected override void Build()
        {
            if (area.Count == 0) area.Add(cell);
            centres = new Vector3[area.Count];
            level = float.MaxValue;
            float highest = float.MinValue;
            for (int i = 0; i < area.Count; i++)
            {
                centres[i] = Toward(area[i]);
                level   = Mathf.Min(level, area[i].SurfaceHeight);
                highest = Mathf.Max(highest, area[i].SurfaceHeight);
            }
            level = Mathf.Lerp(level, highest, 0.5f);
            sheets = AddParts(Disc, area.Count, "Floodwater");
            foam   = AddSmoke(26, "Foam");
            swirl  = AddSmoke(14, "Silt");
            logs   = AddRocks(12, "Log");
        }

        protected override void Animate(float u, float t)
        {
            float rise = Envelope(u, 0.2f, 0.3f);
            float y = level + Mathf.Lerp(-0.03f, 0.1f, rise) * s;
            for (int i = 0; i < sheets.Length; i++)
                Show(sheets[i], new Vector3(centres[i].x, y + 0.004f * s * Mathf.Sin(t * 2f + i), centres[i].z), new Vector3(1.0f, 1f, 1.0f) * s * Ramp(rise, 0f, 0.12f),
                     Color.Lerp(FxColors.Muddy, FxColors.Debris * 1.3f, 0.35f + 0.1f * Mathf.Sin(t + i)), Quaternion.identity);
            // white water racing downstream
            for (int i = 0; i < foam.Length; i++)
            {
                var c = centres[i % centres.Length];
                float k = Mathf.Repeat(t / 2.5f + i * 0.37f, 1f);
                var p = c + Quaternion.Euler(0f, i * 67f, 0f) * Vector3.forward * 0.4f * s + flow * (k - 0.5f) * 0.9f * s;
                Show(foam[i], new Vector3(p.x, y + 0.01f * s, p.z), new Vector3(0.1f, 0.02f, 0.05f) * s, FxColors.Foam,
                     0.85f * Mathf.Sin(k * Mathf.PI) * rise, Quaternion.LookRotation(flow));
            }
            for (int i = 0; i < swirl.Length; i++)
            {
                var c = centres[i % centres.Length];
                float a = t * 0.8f + i * 1.9f;
                var p = c + new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a)) * 0.25f * s + flow * Mathf.Sin(t * 0.3f + i) * 0.2f * s;
                Show(swirl[i], new Vector3(p.x, y + 0.006f * s, p.z), new Vector3(0.16f, 0.015f, 0.16f) * s, FxColors.Debris, 0.5f * rise, Quaternion.identity);
            }
            // logs and branches tumbling along
            for (int i = 0; i < logs.Length; i++)
            {
                var c = centres[i % centres.Length];
                float k = Mathf.Repeat(t / 7f + i * 0.21f, 1f);
                var p = c + Quaternion.Euler(0f, i * 113f, 0f) * Vector3.forward * 0.3f * s + flow * (k - 0.5f) * 1.0f * s;
                Show(logs[i], new Vector3(p.x, y + 0.008f * s * Mathf.Sin(t * 3f + i), p.z), new Vector3(0.012f, 0.012f, 0.06f) * s * rise,
                     FxColors.Wood, Quaternion.Euler(Mathf.Sin(t * 2f + i) * 15f, t * 25f + i * 50f, t * 90f));
            }
        }
    }

    // ---- Rockslide and avalanche: the slope gives way with a rumble; boulders or snow blocks
    // bound down onto the tile below inside a billowing cloud of dust or powder snow

    public class SlideFx : PhenomenonFx
    {
        public HexCell toward;
        public bool snow;
        private Part[] rocks, cloud;
        private Vector3 from, to;
        private float[] offset, lane, sizes;
        private bool rumbled;

        protected override void Build()
        {
            var d = Toward(toward);
            from = d.normalized * 0.1f * s;
            to   = d * 1.1f;
            rocks = AddRocks(snow ? 16 : 24, snow ? "SnowBlock" : "Boulder");
            cloud = AddSmoke(snow ? 34 : 24, snow ? "Powder" : "Dust");
            offset = new float[rocks.Length + cloud.Length];
            lane   = new float[offset.Length];
            sizes  = new float[rocks.Length];
            for (int i = 0; i < offset.Length; i++) { offset[i] = R(0f, 0.3f); lane[i] = R(-1f, 1f); }
            for (int i = 0; i < sizes.Length; i++) sizes[i] = (snow ? R(0.02f, 0.04f) : R(0.018f, 0.06f)) * s;
        }

        // Position `k` (0..1) of the way down the slide in lane `l` (-1..1 across its width)
        private Vector3 Along(float k, float l)
        {
            var across = Vector3.Cross(Vector3.up, (to - from).normalized);
            float width = Mathf.Lerp(0.12f, 0.4f, k) * s;          // fans out at the bottom
            var p = Vector3.Lerp(from, to, k) + across * l * width;
            return OnGround(p);
        }

        protected override void Animate(float u, float t)
        {
            if (!rumbled && u > 0.02f) { rumbled = true; Shake(Vector3.Lerp(from, to, 0.5f), snow ? 0.8f : 1.2f, 2.5f); }
            float fade = 1f - Ramp(u, 0.82f, 1f);
            for (int i = 0; i < rocks.Length; i++)
            {
                float k = Mathf.Clamp01((u - offset[i]) / 0.45f);
                k = 1f - (1f - k) * (1f - k);                          // fast at first, slowing at the foot
                float bounce = Mathf.Abs(Mathf.Sin(k * 10f + i)) * 0.07f * s * (1f - k);
                var p = Along(k, lane[i]) + Vector3.up * (sizes[i] * 0.6f + bounce);
                Show(rocks[i], p, Vector3.one * sizes[i] * Ramp(u, offset[i], offset[i] + 0.02f) * fade,
                     snow ? FxColors.Snow : FxColors.Rock * (0.75f + 0.25f * Mathf.Sin(i * 1.3f)), Quaternion.Euler(k * 900f, i * 37f, k * 400f));
            }
            for (int i = 0; i < cloud.Length; i++)
            {
                float o = offset[rocks.Length + i];
                float k = Mathf.Clamp01((u - o) / 0.5f);
                var p = Along(k * 0.95f, lane[rocks.Length + i]) + Vector3.up * (0.05f + (snow ? 0.3f : 0.18f) * k) * s;
                float size = (snow ? 0.14f : 0.11f) * s * (0.6f + 1.6f * k);
                Show(cloud[i], p, size, snow ? FxColors.Snow : FxColors.Dust, 0.85f * Ramp(u, o, o + 0.05f) * (1f - Ramp(u, o + 0.4f, o + 0.7f)));
            }
        }
    }

    // ---- Earthquake: the ground shakes, dust bursts up, a fissure opens and rocks tumble

    public class EarthquakeFx : PhenomenonFx
    {
        public List<HexCell> area = new();
        private Part[] dust, crack;
        private Vector3[] dustAt;
        private float[] dustTime;
        private Vector3 crackDir;
        private readonly Dictionary<HexCell, Vector3> rest = new();
        private readonly Dictionary<HexCell, Quaternion> restRot = new();

        protected override void Build()
        {
            if (area.Count == 0) area.Add(cell);
            foreach (var c in area) { rest[c] = c.transform.localPosition; restRot[c] = c.transform.localRotation; }
            dust   = AddParts(Puff, 18, "Dust");
            crack  = AddParts(Chunk, 9, "Fissure");
            dustAt = new Vector3[dust.Length];
            dustTime = new float[dust.Length];
            for (int i = 0; i < dust.Length; i++)
            {
                var c = area[rng.Next(area.Count)];
                var p = Toward(c) + new Vector3(R(-0.4f, 0.4f), 0f, R(-0.4f, 0.4f)) * s;
                dustAt[i] = OnGround(p);
                dustTime[i] = R(0.05f, 0.6f);
            }
            float a = R(0f, Mathf.PI);
            crackDir = new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a));
        }

        protected override void Animate(float u, float t)
        {
            // jolts that fade out; tiles nearer the epicentre shake harder
            float shake = Mathf.Exp(-u * 3f) * (1f - Ramp(u, 0.85f, 1f)) * 0.018f * s;
            int n = 0;
            foreach (var c in area)
            {
                if (c == null) continue;
                float near = c == cell ? 1f : 0.55f;
                float k = shake * near;
                var basePos = rest[c];
                basePos.x = c.transform.localPosition.x; // the map wrap may move the tile sideways meanwhile
                c.transform.localPosition = basePos + new Vector3(0f, k * Mathf.Sin(t * 47f + n), 0f);
                c.transform.localRotation = restRot[c] * Quaternion.Euler(k * 40f * Mathf.Sin(t * 31f + n * 2f), 0f, k * 40f * Mathf.Cos(t * 37f + n));
                n++;
            }
            for (int i = 0; i < dust.Length; i++)
            {
                float k = Mathf.Clamp01((u - dustTime[i]) / 0.3f);
                Show(dust[i], dustAt[i] + Vector3.up * (0.02f + 0.15f * k) * s, 0.08f * s * Mathf.Sin(k * Mathf.PI), FxColors.Dust * PuffBoost);
            }
            for (int i = 0; i < crack.Length; i++)
            {
                float along = (i - (crack.Length - 1) * 0.5f) * 0.09f * s;
                var side = Vector3.Cross(Vector3.up, crackDir) * Mathf.Sin(i * 2.3f) * 0.03f * s;
                var p = OnGround(crackDir * along + side, -0.004f * s);
                float open = Ramp(u, 0.05f + i * 0.02f, 0.2f + i * 0.02f) * (1f - Ramp(u, 0.85f, 1f));
                Show(crack[i], p, new Vector3(0.012f, 0.006f, 0.06f) * s * open, new Color(0.1f, 0.08f, 0.07f),
                     Quaternion.LookRotation(crackDir) * Quaternion.Euler(0f, Mathf.Sin(i * 1.9f) * 25f, 0f));
            }
        }

        protected override bool ShowsUnderground => true;

        protected override void End() => Restore();
        private void OnDestroy() => Restore();

        private void Restore()
        {
            foreach (var kv in rest)
            {
                if (kv.Key == null) continue;
                var p = kv.Value;
                p.x = kv.Key.transform.localPosition.x;
                kv.Key.transform.localPosition = p;
                kv.Key.transform.localRotation = restRot[kv.Key];
            }
        }
    }

    // ---- Tsunami: the sea draws back, then a long wall of water rises as it nears the shore, curls
    // over in a line of spray, slams into the coast and surges inland before draining back

    public class TsunamiFx : PhenomenonFx
    {
        public HexCell coast;                 // the land tile the wave strikes
        public List<HexCell> flooded = new(); // low coastal tiles the surge runs over
        private Part wave;
        private Part[] spray, sheets, surgeFoam;
        private Vector3 dir, across, shore;
        private Vector3[] sheetAt;
        private bool slammed;
        private static Mesh waveMesh;

        protected override void Build()
        {
            var d = Toward(coast);
            dir    = d.normalized;
            across = Vector3.Cross(Vector3.up, dir);
            shore  = d * 0.5f;
            wave      = AddPart(waveMesh ??= CreateWave(), "Wave");
            spray     = AddSmoke(30, "Spray");
            sheets    = AddParts(Disc, flooded.Count, "Surge");
            surgeFoam = AddSmoke(20, "SurgeFoam");
            sheetAt = new Vector3[flooded.Count];
            for (int i = 0; i < flooded.Count; i++) sheetAt[i] = Toward(flooded[i]);
        }

        protected override void Animate(float u, float t)
        {
            float sea = cell.SurfaceHeight;
            float approach = Ramp(u, 0.05f, 0.45f);           // offshore → shoreline
            float surge    = Ramp(u, 0.45f, 0.58f) * (1f - Ramp(u, 0.72f, 0.95f));
            float breakK   = Ramp(u, 0.4f, 0.5f);             // the crest curls over and collapses
            if (!slammed && u > 0.47f) { slammed = true; Shake(shore, 1.8f, 1.8f); }

            var line = shore - dir * Mathf.Lerp(2f, 0f, approach) * s + dir * surge * 0.3f * s;
            float height = Mathf.Lerp(0.04f, 0.32f, approach * approach) * s * (1f - Ramp(u, 0.48f, 0.62f));
            Show(wave, new Vector3(line.x, sea - 0.01f * s, line.z), new Vector3(1.5f * s, Mathf.Max(height, 1e-4f), (0.18f + 0.1f * breakK) * s),
                 Color.white, Quaternion.LookRotation(dir));

            // spray blown off the crest, bursting high as it breaks
            for (int i = 0; i < spray.Length; i++)
            {
                float l = (i - (spray.Length - 1) * 0.5f) / (spray.Length - 1) * 2.6f * s;
                float taper = 1f - Mathf.Pow(Mathf.Abs(l) / (1.3f * s), 3f);
                float puff = Mathf.Repeat(t * 0.9f + i * 0.37f, 1f);
                var p = line + across * l + dir * (0.05f * s + surge * 0.6f * s);
                p.y = Mathf.Max(sea + height * taper * 1.05f, Ground(p) + 0.03f * s) + (0.05f + 0.25f * breakK * (1f - surge)) * s * puff;
                float size = (0.05f + 0.1f * approach + 0.12f * breakK) * s * taper * (0.7f + 0.6f * puff);
                Show(spray[i], p, size, FxColors.Spray, taper * (0.4f + 0.5f * approach) * (1f - puff * 0.6f) * (1f - Ramp(u, 0.75f, 0.95f)));
            }
            // water racing over the low coast, rising with the surge and draining back
            for (int i = 0; i < sheets.Length; i++)
            {
                float y = flooded[i].SurfaceHeight + Mathf.Lerp(-0.03f, 0.07f, surge) * s;
                Show(sheets[i], new Vector3(sheetAt[i].x, y, sheetAt[i].z), new Vector3(1f, 1f, 1f) * s * Ramp(surge, 0f, 0.1f),
                     Color.Lerp(FxColors.Sea, FxColors.Muddy, 0.45f), Quaternion.identity);
            }
            for (int i = 0; i < surgeFoam.Length && sheets.Length > 0; i++)
            {
                var c = sheetAt[i % sheetAt.Length];
                float k = Mathf.Repeat(t / 2f + i * 0.31f, 1f);
                var p = c + Quaternion.Euler(0f, i * 71f, 0f) * Vector3.forward * 0.35f * s + dir * (k - 0.3f) * 0.5f * s;
                float y = flooded[i % flooded.Count].SurfaceHeight + 0.08f * s * surge;
                Show(surgeFoam[i], new Vector3(p.x, y, p.z), new Vector3(0.12f, 0.025f, 0.07f) * s, FxColors.Foam, 0.85f * surge * Mathf.Sin(k * Mathf.PI), Quaternion.LookRotation(dir));
            }
        }

        // A breaking wave, 2 units long (x), 1 high, faces +z: a long back slope rising to a crest that
        // curls forward over a hollow front. Deep blue below, paler up the face, white foam on the lip.
        // The ends taper down to nothing.
        private static Mesh CreateWave()
        {
            Vector2[] profile = // (z forward, y up), from the back foot over the crest to the front foot
            {
                new(-1.2f, 0f), new(-0.75f, 0.25f), new(-0.35f, 0.62f), new(-0.05f, 0.92f), new(0.15f, 1f),
                new(0.36f, 0.9f), new(0.48f, 0.68f), new(0.36f, 0.6f), new(0.2f, 0.42f), new(0.16f, 0.15f), new(0.24f, 0f),
            };
            const int segments = 24;
            var verts = new List<Vector3>();
            var cols  = new List<Color>();
            var tris  = new List<int>();
            Vector3 P(int seg, int k)
            {
                float x = seg / (float)segments * 2f - 1f;
                float taper = 1f - Mathf.Pow(Mathf.Abs(x), 4f);
                var pr = profile[k];
                return new Vector3(x, pr.y * taper, pr.x * (0.4f + 0.6f * taper));
            }
            Color C(float y01) => y01 > 0.82f ? new Color(1.25f, 1.3f, 1.35f) : Color.Lerp(new Color(0.08f, 0.22f, 0.36f), new Color(0.28f, 0.55f, 0.66f), y01 / 0.82f);
            for (int seg = 0; seg < segments; seg++)
            for (int k = 0; k < profile.Length - 1; k++)
            {
                Vector3 a = P(seg, k), b = P(seg + 1, k), c = P(seg + 1, k + 1), d = P(seg, k + 1);
                float y01 = Mathf.Max(profile[k].y, profile[k + 1].y);
                var col = C(y01);
                foreach (var (p0, p1, p2) in new[] { (a, b, c), (a, c, d) })
                {
                    // outward = away from the inside of the profile (a point under the crest)
                    var inside = new Vector3(p0.x, 0.3f * (1f - Mathf.Pow(Mathf.Abs(p0.x), 4f)), 0f);
                    var n = Vector3.Cross(p1 - p0, p2 - p0);
                    int i0 = verts.Count;
                    if (Vector3.Dot(n, (p0 + p1 + p2) / 3f - inside) < 0f) { verts.Add(p0); verts.Add(p2); verts.Add(p1); }
                    else { verts.Add(p0); verts.Add(p1); verts.Add(p2); }
                    cols.Add(col); cols.Add(col); cols.Add(col);
                    tris.Add(i0); tris.Add(i0 + 1); tris.Add(i0 + 2);
                }
            }
            var mesh = new Mesh { name = "TsunamiWave" };
            mesh.SetVertices(verts);
            mesh.SetColors(cols);
            mesh.SetTriangles(tris, 0);
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            return mesh;
        }
    }

    // ---- Glacier calving: the ice front cracks with a jolt, great blocks topple into the sea in
    // towering splashes, waves ring out and the bergs drift away

    public class CalvingFx : PhenomenonFx
    {
        public HexCell sea;                    // the sea tile in front of the ice
        private Part[] blocks, splash, rings, mist;
        private Vector3 dir, edge;
        private Vector3[] home, driftTo;
        private float[] breakAt, size;
        private bool[] jolted;
        private float top, water;

        protected override void Build()
        {
            var d = Toward(sea);
            dir   = d.normalized;
            edge  = d * 0.5f;
            top   = cell.SurfaceHeight;
            water = sea.SurfaceHeight;
            blocks = AddRocks(7, "Iceberg");
            splash = AddSmoke(28, "Splash");
            rings  = AddSmoke(14, "Ripple");
            mist   = AddSmoke(8, "IceDust");
            home    = new Vector3[blocks.Length];
            driftTo = new Vector3[blocks.Length];
            breakAt = new float[blocks.Length];
            size    = new float[blocks.Length];
            jolted  = new bool[blocks.Length];
            var across = Vector3.Cross(Vector3.up, dir);
            for (int i = 0; i < blocks.Length; i++)
            {
                home[i]    = edge - dir * 0.05f * s + across * R(-0.4f, 0.4f) * s;
                driftTo[i] = home[i] + dir * R(0.5f, 0.9f) * s + across * R(-0.25f, 0.25f) * s;
                breakAt[i] = R(0.05f, 0.45f);
                size[i]    = R(0.06f, 0.11f) * s;
            }
        }

        protected override void Animate(float u, float t)
        {
            float fade = 1f - Ramp(u, 0.85f, 1f);
            for (int i = 0; i < blocks.Length; i++)
            {
                float k = Mathf.Clamp01((u - breakAt[i]) / 0.1f);            // tipping and falling
                if (k > 0.9f && !jolted[i]) { jolted[i] = true; Shake(home[i], size[i] / s * 6f, 0.7f); }
                float drift = Ramp(u, breakAt[i] + 0.1f, 1f);
                var p = Vector3.Lerp(home[i], driftTo[i], drift);
                float y = Mathf.Lerp(top + size[i] * 0.3f, water - size[i] * 0.2f, k * k);
                if (k >= 1f) y = water + size[i] * 0.05f * Mathf.Sin(t * 2f + i) - size[i] * 0.2f;
                var tilt = Quaternion.AngleAxis(Mathf.Lerp(0f, 80f, k) * (k < 1f ? 1f : 0.25f), Vector3.Cross(Vector3.up, dir));
                Show(blocks[i], new Vector3(p.x, y, p.z), new Vector3(1.1f, 1.3f, 1f) * size[i] * fade, FxColors.Ice, tilt * Quaternion.Euler(0f, i * 40f, 0f));
            }
            for (int i = 0; i < splash.Length; i++)
            {
                int b = i % blocks.Length;
                float k = Mathf.Clamp01((u - breakAt[b] - 0.08f) / 0.14f);
                float ang = i * 2.4f;
                var p = home[b] + dir * 0.1f * s + new Vector3(Mathf.Sin(ang), 0f, Mathf.Cos(ang)) * 0.08f * s * k;
                float h = Mathf.Sin(k * Mathf.PI) * (0.18f + 0.06f * (i % 3)) * s * (size[b] / (0.1f * s));
                Show(splash[i], new Vector3(p.x, water + h, p.z), (0.06f + 0.06f * k) * s, FxColors.Spray, 0.9f * Mathf.Sin(k * Mathf.PI));
            }
            for (int i = 0; i < rings.Length; i++)
            {
                int b = i % blocks.Length;
                float k = Mathf.Clamp01((u - breakAt[b] - 0.1f) / 0.35f);
                float ang = (i / 2) * 1.3f + (i % 2) * Mathf.PI;
                var p = home[b] + dir * 0.1f * s + new Vector3(Mathf.Sin(ang), 0f, Mathf.Cos(ang)) * k * 0.35f * s;
                Show(rings[i], new Vector3(p.x, water + 0.005f * s, p.z), new Vector3(0.12f, 0.012f, 0.05f) * s, FxColors.Foam,
                     0.8f * (1f - k) * Ramp(k, 0f, 0.05f), Quaternion.Euler(0f, ang * Mathf.Rad2Deg + 90f, 0f));
            }
            for (int i = 0; i < mist.Length; i++)
            {
                int b = i % blocks.Length;
                float k = Mathf.Clamp01((u - breakAt[b]) / 0.25f);
                var p = home[b] + Vector3.up * (top + 0.05f * s + k * 0.15f * s);
                Show(mist[i], p, (0.1f + 0.1f * k) * s, FxColors.Snow, 0.6f * Mathf.Sin(k * Mathf.PI));
            }
        }
    }
}
