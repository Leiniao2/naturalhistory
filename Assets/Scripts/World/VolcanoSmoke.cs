using UnityEngine;

namespace NaturalHistory.World
{
    // Animated smoke over a volcano: a steady stream of puffs leaves the crater, rises, drifts
    // downwind with a slow wobble, swells and pales, then shrinks away (the map material is opaque,
    // so puffs vanish by shrinking rather than fading). Added by HexGrid to each volcano feature
    // object; the crater is taken to be at the top of the volcano mesh.
    public class VolcanoSmoke : MonoBehaviour
    {
        private const int   Puffs    = 7;
        private const float Lifetime = 7f;    // seconds from the crater until a puff has gone
        private const float Rise     = 0.75f; // height gained over a lifetime, in cells
        private const float Drift    = 0.35f; // distance blown downwind over a lifetime, in cells

        private static readonly int ColorId = Shader.PropertyToID("_Color");
        private static Mesh puffMesh;

        private Transform[] puffs;
        private MeshRenderer[] renderers;
        private float[] offsets, sizes, spins;
        private MaterialPropertyBlock block;
        private Vector3 vent, wind;
        private float cell, windPhase;

        public void Init(float cellSize, int seed)
        {
            cell = cellSize;
            var rng = new System.Random(seed);
            float R(float min, float max) => min + (float)rng.NextDouble() * (max - min);

            var filter = GetComponent<MeshFilter>();
            var bounds = filter != null && filter.sharedMesh != null ? filter.sharedMesh.bounds : new Bounds(Vector3.zero, Vector3.one * 0.5f);
            vent = filter != null && MapFeatureMeshes.TryGetVent(filter.sharedMesh, out var v)
                 ? v + Vector3.up * 0.01f * cell                          // the active cone's crater
                 : new Vector3(0f, bounds.max.y - 0.02f * cell, 0f);

            float a = R(0f, Mathf.PI * 2f);
            wind = new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a));
            windPhase = R(0f, 100f);

            puffMesh ??= MapFeatureMeshes.CreateSmokePuff(new System.Random(7));
            var material = GetComponent<MeshRenderer>()?.sharedMaterial;
            block = new MaterialPropertyBlock();

            puffs     = new Transform[Puffs];
            renderers = new MeshRenderer[Puffs];
            offsets   = new float[Puffs];
            sizes     = new float[Puffs];
            spins     = new float[Puffs];
            for (int i = 0; i < Puffs; i++)
            {
                var go = new GameObject("SmokePuff");
                go.transform.SetParent(transform, false);
                go.AddComponent<MeshFilter>().sharedMesh = puffMesh;
                var mr = go.AddComponent<MeshRenderer>();
                mr.sharedMaterial = material;
                mr.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
                puffs[i]     = go.transform;
                renderers[i] = mr;
                // evenly spread through the cycle (a little irregular), so the column is always full
                offsets[i] = (i + R(-0.2f, 0.2f)) / Puffs;
                sizes[i]   = R(0.85f, 1.2f);
                spins[i]   = R(-25f, 25f);
            }
            Update();
        }

        private void Update()
        {
            if (puffs == null) return;
            float time = Time.time;
            // the wind veers slowly back and forth
            float veer = Mathf.Sin(time * 0.05f + windPhase) * 0.6f;
            var down = Quaternion.Euler(0f, veer * Mathf.Rad2Deg, 0f) * wind;
            // puffs are children of the volcano object; undo its scale so they keep their shape
            var s = transform.lossyScale;
            var inv = new Vector3(1f / Mathf.Max(Mathf.Abs(s.x), 1e-4f), 1f / Mathf.Max(Mathf.Abs(s.y), 1e-4f), 1f / Mathf.Max(Mathf.Abs(s.z), 1e-4f));

            for (int i = 0; i < Puffs; i++)
            {
                float t = Mathf.Repeat(time / Lifetime + offsets[i], 1f); // 0 = leaving the crater, 1 = gone
                // rises quickly at first, then slows and bends over as the wind takes it
                float up   = Rise * (1f - (1f - t) * (1f - t)) * cell;
                float away = Drift * t * t * cell;
                var wobble = new Vector3(Mathf.Sin(time * 0.7f + i * 2.1f), 0f, Mathf.Cos(time * 0.6f + i * 1.7f)) * (0.03f * t * cell);
                var world  = vent + Vector3.up * up + down * away + wobble;
                puffs[i].localPosition = Vector3.Scale(world, inv);

                // swells as it rises, pops in at the vent and shrinks away at the end
                float r = cell * sizes[i] * Mathf.Lerp(0.05f, 0.16f, t)
                        * Mathf.SmoothStep(0f, 1f, t / 0.08f) * (1f - Mathf.SmoothStep(0f, 1f, (t - 0.72f) / 0.28f));
                puffs[i].localScale    = Vector3.Scale(Vector3.one * Mathf.Max(r, 1e-4f), inv);
                puffs[i].localRotation = Quaternion.Euler(0f, spins[i] * time + i * 50f, spins[i] * 0.3f * time);

                // dark and sooty at the crater, paling as it thins out
                float v = Mathf.Lerp(0.45f, 1.05f, Mathf.SmoothStep(0f, 1f, t * 1.4f));
                block.SetColor(ColorId, new Color(v, v * 0.98f, v * 0.96f));
                renderers[i].SetPropertyBlock(block);
            }
        }
    }
}
