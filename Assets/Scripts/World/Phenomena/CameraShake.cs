using System.Collections.Generic;
using UnityEngine;

namespace NaturalHistory.World
{
    // Shakes the main camera for violent phenomena (impacts, eruptions, slides). CameraController
    // keeps its state in the camera's own position, so the shake is taken off again before anything
    // else moves the camera (Update, very early) and put back on after (LateUpdate): it never drifts.
    [DefaultExecutionOrder(-1000)]
    public class CameraShake : MonoBehaviour
    {
        private struct Kick { public Vector3 at; public float strength, start, length; }

        private readonly List<Kick> kicks = new();
        private Vector3 applied;

        // A jolt of `strength` (world units at the source, fading with distance from the view)
        // lasting `length` seconds, felt from a world position.
        public static void Add(Vector3 worldPosition, float strength, float length)
        {
            var cam = Camera.main;
            if (cam == null) return;
            var shake = cam.GetComponent<CameraShake>() ?? cam.gameObject.AddComponent<CameraShake>();
            shake.kicks.Add(new Kick { at = worldPosition, strength = strength, start = Time.time, length = Mathf.Max(length, 0.05f) });
        }

        private void Update()
        {
            transform.position -= applied;
            applied = Vector3.zero;
        }

        private void LateUpdate()
        {
            if (kicks.Count == 0) return;
            float t = Time.time, total = 0f;
            PhenomenaUtil.CameraFocus(out var focus, out float view);
            for (int i = kicks.Count - 1; i >= 0; i--)
            {
                var k = kicks[i];
                float a = (t - k.start) / k.length;
                if (a >= 1f) { kicks.RemoveAt(i); continue; }
                var d = k.at - focus;
                d.y = 0f;
                float near = view > 0f ? Mathf.Clamp01(1.2f - d.magnitude / (view * 1.5f)) : 1f;
                total += k.strength * (1f - a) * (1f - a) * near;
            }
            if (total <= 0f) return;
            // a little of the camera's height, so it reads the same at every zoom
            total *= Mathf.Clamp(transform.position.y * 0.08f, 0.3f, 3f);
            applied = new Vector3(Mathf.PerlinNoise(t * 25f, 0.3f) - 0.5f, (Mathf.PerlinNoise(0.7f, t * 25f) - 0.5f) * 0.6f,
                                  Mathf.PerlinNoise(t * 25f, 4.1f) - 0.5f) * 2f * total;
            transform.position += applied;
        }
    }
}
