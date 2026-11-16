using UnityEngine;

namespace NaturalHistory.Core
{
    // Caps the frame rate. The map's animations (walking animals, swaying plants, drifting smoke,
    // waves) are slow, so 30 frames a second looks the same as an uncapped rate while the GPU and
    // CPU do a fraction of the work: laptops stay cool and quiet. Unity ignores targetFrameRate
    // while vsync is on (the higher quality levels turn it on), so vsync is switched off here.
    // In the Editor this applies to the Game view in Play mode.
    public static class FrameRateLimiter
    {
        public const int TargetFps = 30;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
        private static void Apply()
        {
            QualitySettings.vSyncCount  = 0;
            Application.targetFrameRate = TargetFps;
        }
    }
}
