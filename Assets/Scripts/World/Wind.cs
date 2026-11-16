using UnityEngine;

namespace NaturalHistory.World
{
    // The breeze that bends slender land plants (MapFeature.shader ApplyWind reads _NHWind).
    public static class Wind
    {
        public static float Strength = 0.035f; // how far the tip of a fully bending plant leans, in cells
        public static float Speed    = 1.7f;   // sway cycles: radians per second
        public static float Gusts    = 3f;     // gust wavelength, in cells

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        public static void Apply()
        {
            var grid = HexGrid.Instance;
            float cell = grid != null && grid.Width > 0 ? grid.WrapWidth / (Mathf.Sqrt(3f) * grid.Width) : 1f;
            Shader.SetGlobalVector("_NHWind", new Vector4(Strength * cell, Speed, Gusts * cell, 0f));
        }
    }
}
