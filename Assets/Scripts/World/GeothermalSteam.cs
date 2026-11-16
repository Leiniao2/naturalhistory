using UnityEngine;

namespace NaturalHistory.World
{
    // Steam over a geothermal field: soft wisps curling up from the hot springs and fumaroles, and
    // the geyser blowing a tall white column every 15-25 seconds for a few seconds. Under the sea
    // the same points send up streams of small bubbles instead. Points come from the mesh
    // (MapFeatureMeshes.TryGetSteamVents); added by HexGrid to the feature or under object.
    public class GeothermalSteam : MonoBehaviour
    {
        private const int Wisps = 3;      // per point
        private const int Column = 12;    // puffs in the geyser's column

        private static readonly int ColorId = Shader.PropertyToID("_Color");
        private static Material smoke;

        private Vector3[] points;
        private int geyser;
        private bool underwater;
        private float cell, period, phase;
        private Transform[] puffs;
        private MeshRenderer[] renderers;
        private float[] offsets;
        private MaterialPropertyBlock block;

        public void Init(float cellSize, int seed, Vector3[] steamPoints, int geyserIndex, bool underwater)
        {
            cell = cellSize;
            points = steamPoints;
            geyser = geyserIndex;
            this.underwater = underwater;
            var rng = new System.Random(seed);
            period = 15f + (float)rng.NextDouble() * 10f;
            phase  = (float)rng.NextDouble() * period;
            smoke ??= Resources.Load<Material>("Materials/FxSmoke");
            block = new MaterialPropertyBlock();

            int count = points.Length * Wisps + (geyser >= 0 ? Column : 0);
            puffs = new Transform[count];
            renderers = new MeshRenderer[count];
            offsets = new float[count];
            for (int i = 0; i < count; i++)
            {
                var go = new GameObject(underwater ? "Bubble" : "Steam");
                go.transform.SetParent(transform, false);
                go.AddComponent<MeshFilter>().sharedMesh = PhenomenonFx.Ball;
                var mr = go.AddComponent<MeshRenderer>();
                mr.sharedMaterial = smoke;
                mr.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
                mr.receiveShadows = false;
                puffs[i] = go.transform;
                renderers[i] = mr;
                offsets[i] = (float)rng.NextDouble();
            }
            Update();
        }

        private void Show(int i, Vector3 at, Vector3 scale, Color color, float alpha)
        {
            alpha = Mathf.Clamp01(alpha);
            bool on = alpha > 0.004f && scale.x > 1e-4f;
            renderers[i].enabled = on;
            if (!on) return;
            puffs[i].localPosition = at;
            puffs[i].localScale = scale;
            color.a = alpha;
            block.SetColor(ColorId, color);
            renderers[i].SetPropertyBlock(block);
        }

        private void Update()
        {
            if (puffs == null || smoke == null) return;
            float time = Time.time;
            var white = underwater ? new Color(0.85f, 0.95f, 1f) : new Color(0.95f, 0.96f, 0.98f);
            int n = 0;
            for (int p = 0; p < points.Length; p++)
            {
                bool isGeyser = p == geyser;
                for (int w = 0; w < Wisps; w++, n++)
                {
                    float life = underwater ? 2.2f : isGeyser ? 3.5f : 4.5f;
                    float t = Mathf.Repeat(time / life + offsets[n] + w / (float)Wisps, 1f);
                    if (underwater)
                    {
                        // bubbles: small, rising quickly and wobbling
                        var at = points[p] + new Vector3(Mathf.Sin(t * 9f + n) * 0.012f, t * 0.35f, Mathf.Cos(t * 7f + n) * 0.012f) * cell;
                        Show(n, at, Vector3.one * (0.008f + 0.008f * t) * cell, white, 0.7f * (1f - t));
                    }
                    else
                    {
                        // steam: swelling and thinning as it curls up and drifts
                        var at = points[p] + new Vector3(Mathf.Sin(t * 3f + n) * 0.03f + t * 0.06f, t * 0.28f, Mathf.Cos(t * 2.5f + n) * 0.03f) * cell;
                        Show(n, at, Vector3.one * (0.025f + 0.07f * t) * cell, white, 0.32f * Mathf.Sin(t * Mathf.PI));
                    }
                }
            }
            if (geyser < 0) return;

            // the geyser: a white column shooting up, then collapsing into drifting steam
            float e = Mathf.Repeat(time + phase, period);
            const float blow = 5f;
            var vent = points[geyser];
            for (int i = 0; i < Column; i++, n++)
            {
                if (e > blow + 2f) { renderers[n].enabled = false; continue; }
                float rise = Mathf.SmoothStep(0f, 1f, Mathf.Clamp01(e / 0.6f));      // the column climbs at the start
                float fade = 1f - Mathf.Clamp01((e - blow) / 2f);                    // and dies away at the end
                float c = Mathf.Repeat(e / 0.9f + i / (float)Column, 1f);            // puffs racing up the column
                float y = c * 0.85f * cell * rise;
                float spread = 0.015f + 0.06f * c * c;
                var at = vent + new Vector3(Mathf.Sin(i * 2.1f + e * 4f) * spread, y, Mathf.Cos(i * 1.7f + e * 3f) * spread) * (1f) + new Vector3(0.05f * c * c, 0f, 0f) * cell;
                float size = (0.03f + 0.09f * c) * cell;
                Show(n, at, new Vector3(size, size * 1.3f, size), white, 0.75f * fade * (1f - 0.6f * c));
            }
        }
    }
}
