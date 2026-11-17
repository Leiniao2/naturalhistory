using System.Collections.Generic;
using UnityEngine;

namespace NaturalHistory.World
{
    // The sky layer (UnderView.Sky): a deck of drifting clouds over the whole map, just above the
    // tallest land and its forests. The land shows dimly through it; the fliers and the summit
    // animals are lifted above it (HexGrid.Under.ShowGroupsForView), so they are what stands out.
    //
    // The clouds follow the climate (ClimateSystem): a weather map, one texel row per half tile
    // row, tells the shader (SkyVeil) how cloudy each region is and where thunderstorms (warm,
    // humid) and blizzards (freezing, moist) are this turn, and where the land is (for the
    // monsoons); storms move from turn to turn. The shader adds the winds, thin and thick cloud
    // and the odd gold or pink cloud. Under the storms and blizzards rain and snow fall on the
    // surface (WeatherFall).
    public class SkyLayer : MonoBehaviour
    {
        // World height of the cloud deck
        public static float DeckHeight { get; private set; }

        private const float AboveLand = 0.45f; // clears the trees on the highest tiles
        private const float HighClearance = 0.15f; // how far the lowest high summit rises above the deck, at least
        private const float DeckSize  = 400f;  // follows the camera, so it always covers the view

        private const int TexelsPerCell = 2; // weather map resolution

        private HexGrid grid;
        private GameObject deck;
        private Material material;
        private Texture2D weather, weatherPrev; // this turn's and last turn's, cross-faded
        private Texture2D peaks;                // high mountains: the clouds part around their summits
        private const float WeatherFade = 6f;   // seconds for new weather to drift in
        private float weatherChanged = -100f;
        private int weatherTurn; // reseeds where the storms are, each climate update
        private WeatherFall fall;
        private readonly SkyFeatures features = new(); // typhoons, fronts, ash plumes, events seen from above
        private float nextRainRefresh;
        private bool eventsHooked;

        public static SkyLayer Instance { get; private set; }
        private void Awake() => Instance = this;

        // Admin panel: set off one of SkyFeatures.AdminNames near the middle of the view
        public void TriggerAdmin(int index)
        {
            var cam = Camera.main;
            Vector2 near = default;
            if (cam != null)
            {
                var p = cam.transform.position; var f = cam.transform.forward;
                float y = grid != null ? grid.transform.position.y : 0f;
                float t = Mathf.Abs(f.y) > 1e-3f ? (y - p.y) / f.y : 0f;
                var g = p + f * Mathf.Max(0f, t);
                near = new Vector2(g.x, g.z);
            }
            features.Trigger(index, near);
        }

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Bootstrap()
        {
            if (FindAnyObjectByType<HexGrid>() == null || FindAnyObjectByType<SkyLayer>() != null) return;
            new GameObject("SkyLayer").AddComponent<SkyLayer>();
        }

        private void Start()
        {
            grid = HexGrid.Instance;
            if (grid == null) return;
            grid.Generated      += Measure;
            grid.TerrainChanged += Measure;
            UnderView.Changed   += Apply;
            HookClimate();
            HookEvents();
            Measure();
            Apply();
        }

        private void OnDestroy()
        {
            if (grid != null) { grid.Generated -= Measure; grid.TerrainChanged -= Measure; }
            UnderView.Changed -= Apply;
            if (climateHooked && Climate.ClimateSystem.Instance != null) Climate.ClimateSystem.Instance.Updated -= OnClimate;
            if (weather != null) Destroy(weather);
            if (weatherPrev != null) Destroy(weatherPrev);
            if (peaks != null) Destroy(peaks);
            fall?.Clear();
            if (eventsHooked && NaturalEvents.Instance != null) NaturalEvents.Instance.Occurred -= features.OnPhenomenon;
            if (Instance == this) Instance = null;
        }

        // Ground events (meteors, eruptions, tornadoes...) also show in the sky, in step with them
        private void HookEvents()
        {
            if (eventsHooked || NaturalEvents.Instance == null) return;
            NaturalEvents.Instance.Occurred += features.OnPhenomenon;
            eventsHooked = true;
        }

        // The climate system may start after this component
        private bool climateHooked;
        private void HookClimate()
        {
            if (climateHooked || Climate.ClimateSystem.Instance == null) return;
            Climate.ClimateSystem.Instance.Updated += OnClimate;
            climateHooked = true;
            UpdateWeather();
        }

        private void OnClimate()
        {
            weatherTurn++;
            UpdateWeather();
        }

        // The deck sits a little above the highest land that isn't a mountain, and above the peaks of
        // ordinary mountains too: only the high mountains (HexCell.IsHighMountain) rise through it
        private void Measure()
        {
            if (grid == null || !grid.IsGenerated) return;
            float top = float.MinValue, ordinary = float.MinValue, lowestHigh = float.MaxValue;
            for (int r = 0; r < grid.Height; r++)
            for (int q = 0; q < grid.Width; q++)
            {
                var cell = grid.GetCell(q, r);
                if (cell == null || cell.Terrain == null) continue;
                if (cell.IsHighMountain) lowestHigh = Mathf.Min(lowestHigh, cell.PeakY);
                else if (cell.IsMountain) { if (cell.Feature != TerrainFeature.Mesa) ordinary = Mathf.Max(ordinary, cell.PeakY); } // flat-topped mesas may break through
                else top = Mathf.Max(top, cell.transform.position.y + cell.SurfaceHeight);
            }
            DeckHeight = (top > float.MinValue ? top : grid.transform.position.y) + AboveLand;
            if (ordinary > float.MinValue)
            {
                // just over the tallest ordinary peak, so the high ones stand well clear of the clouds
                float gap = lowestHigh < float.MaxValue ? Mathf.Max(0f, lowestHigh - ordinary) : 0.3f;
                DeckHeight = Mathf.Max(DeckHeight, ordinary + Mathf.Clamp(gap * 0.12f, 0.02f, 0.08f));
            }
            // never so high that it hides the high mountains: their summits always stand clear (with
            // tall terraces, the highest plateau's trees would otherwise lift the deck past them)
            if (lowestHigh < float.MaxValue)
            {
                float cap = lowestHigh - HighClearance;
                if (DeckHeight > cap)
                    DeckHeight = ordinary > float.MinValue ? Mathf.Max(cap, Mathf.Min(ordinary + 0.02f, lowestHigh - HighClearance * 0.5f)) : cap;
            }
            if (deck != null) deck.transform.position = new Vector3(deck.transform.position.x, DeckHeight, deck.transform.position.z);
            UpdateWeather();
        }

        // Fills the weather map from the tiles' climate: R cloud cover, G thunderstorm, B blizzard,
        // A land (much more blurred: the monsoons blow across coasts, by its gradient). Texels cover the map's rectangle (wrapping east–west), each taking its nearest
        // tile, then blurred so weather fronts are soft.
        private void UpdateWeather()
        {
            if (grid == null || !grid.IsGenerated) return;
            var climate = Climate.ClimateSystem.Instance;
            int w = grid.Width, h = grid.Height;
            var c00 = grid.GetCell(0, 0);
            if (c00 == null || w <= 0 || h <= 0) return;
            float size = grid.WrapWidth / (Mathf.Sqrt(3f) * w);
            float dx = Mathf.Sqrt(3f) * size, dz = 1.5f * size;
            Vector3 origin = c00.transform.position;

            // per tile
            var cover = new float[w, h]; var storm = new float[w, h]; var snow = new float[w, h]; var land = new float[w, h];
            float seed = weatherTurn * 7.31f + grid.WorldSeed % 1000;
            for (int r = 0; r < h; r++)
            for (int q = 0; q < w; q++)
            {
                var cell = grid.GetCell(q, r);
                if (cell == null) continue;
                float t = 15f, hum = 60f;
                if (climate != null && climate.HasData) { var c = climate.Get(cell); t = c.TemperatureC; hum = c.Humidity; }
                // storms and blizzards only in some of the regions their climate allows, moving each turn
                float patchA = Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(0.52f, 0.7f, Mathf.PerlinNoise(q * 0.22f + seed, r * 0.22f + 31.7f)));
                float patchB = Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(0.5f, 0.68f, Mathf.PerlinNoise(q * 0.2f + 57.1f, r * 0.2f + seed)));
                cover[q, r] = Mathf.InverseLerp(30f, 90f, hum);
                storm[q, r] = Mathf.Clamp01((t - 18f) / 8f) * Mathf.Clamp01((hum - 62f) / 18f) * patchA;
                snow[q, r]  = Mathf.Clamp01((1f - t) / 8f) * Mathf.Clamp01((hum - 40f) / 25f) * patchB;
                land[q, r]  = cell.IsWater ? 0f : 1f;
            }

            int tw = w * TexelsPerCell, th = h * TexelsPerCell;
            float zMin = origin.z - size, zSpan = dz * (h - 1) + 2f * size;
            float xMin = origin.x - dx * 0.5f;
            // typhoon nurseries (warm tropical sea), volcanoes and the land, for the moving systems
            var warmSea = new List<Vector2>();
            var volcanoes = new List<Vector2>();
            float midRow = (h - 1) * 0.5f;
            for (int r = 0; r < h; r++)
            for (int q = 0; q < w; q++)
            {
                var cell = grid.GetCell(q, r);
                if (cell == null || cell.Terrain == null) continue;
                var at = new Vector2(cell.transform.position.x, cell.transform.position.z);
                if (cell.Feature == TerrainFeature.Volcano) volcanoes.Add(at);
                float lat = Mathf.Abs(r - midRow) / Mathf.Max(1f, midRow);
                if (cell.Terrain.kind == TerrainKind.SaltWater && lat > 0.1f && lat < 0.4f && climate != null && climate.HasData && climate.Get(cell).TemperatureC >= 25f)
                    warmSea.Add(at);
            }
            bool IsLand(Vector2 p)
            {
                int row = Mathf.Clamp(Mathf.RoundToInt((p.y - origin.z) / dz), 0, h - 1);
                int col = Mathf.RoundToInt((p.x - origin.x) / dx - 0.5f * (row & 1));
                return land[((col % w) + w) % w, row] > 0.5f;
            }
            features.SetMap(origin.x - dx * 0.5f, origin.z - size, grid.WrapWidth, dz * (h - 1) + 2f * size, size,
                            warmSea, IsLand, volcanoes, Climate.EarthHistory.Volcanism(grid.DisplayedMillionYearsAgo));

            fall ??= new WeatherFall(transform);
            fall.Rebuild(grid, storm, snow, size);
            if (material == null) return; // the deck isn't built until the sky view first opens

            var px = new Color[tw * th];
            var landPx = new Color[tw * th];
            var peakPx = new Color[tw * th];
            for (int j = 0; j < th; j++)
            for (int i = 0; i < tw; i++)
            {
                float x = xMin + (i + 0.5f) / tw * grid.WrapWidth, z = zMin + (j + 0.5f) / th * zSpan;
                int row = Mathf.Clamp(Mathf.RoundToInt((z - origin.z) / dz), 0, h - 1);
                int col = Mathf.RoundToInt((x - origin.x) / dx - 0.5f * (row & 1));
                col = ((col % w) + w) % w;
                px[j * tw + i] = new Color(cover[col, row], storm[col, row], snow[col, row], 0f);
                landPx[j * tw + i] = new Color(land[col, row], 0f, 0f, 0f);
                var c = grid.GetCell(col, row);
                peakPx[j * tw + i] = new Color(c != null && c.IsHighMountain ? 1f : 0f, 0f, 0f, 0f);
            }
            for (int pass = 0; pass < 2; pass++) px = Blur(px, tw, th);
            for (int pass = 0; pass < 8; pass++) landPx = Blur(landPx, tw, th);
            for (int k = 0; k < px.Length; k++) px[k].a = landPx[k].r;
            peakPx = Blur(peakPx, tw, th);
            if (peaks == null || peaks.width != tw || peaks.height != th)
            {
                if (peaks != null) Destroy(peaks);
                peaks = NewWeatherTexture(tw, th);
                peaks.name = "SkyPeaks";
            }
            peaks.SetPixels(peakPx);
            peaks.Apply(false);
            material.SetTexture("_Peaks", peaks);

            // the old weather becomes the one fading out (the first map has nothing to fade from)
            bool fresh = weather == null || weather.width != tw || weather.height != th;
            if (fresh)
            {
                if (weather != null) Destroy(weather);
                if (weatherPrev != null) Destroy(weatherPrev);
                weather = NewWeatherTexture(tw, th);
                weatherPrev = NewWeatherTexture(tw, th);
            }
            else (weather, weatherPrev) = (weatherPrev, weather);
            weather.SetPixels(px);
            weather.Apply(false);
            if (fresh) { weatherPrev.SetPixels(px); weatherPrev.Apply(false); }
            material.SetTexture("_Weather", weather);
            material.SetTexture("_WeatherPrev", weatherPrev);
            material.SetFloat("_WeatherBlend", fresh ? 1f : 0f);
            weatherChanged = fresh ? -100f : Time.time;
            material.SetVector("_WeatherRect", new Vector4(xMin, zMin, grid.WrapWidth, zSpan));
        }

        private static Texture2D NewWeatherTexture(int w, int h) =>
            new(w, h, TextureFormat.RGBA32, false, true)
                { name = "SkyWeather", wrapModeU = TextureWrapMode.Repeat, wrapModeV = TextureWrapMode.Clamp, filterMode = FilterMode.Bilinear };

        // 3×3 box blur, wrapping east–west
        private static Color[] Blur(Color[] src, int w, int h)
        {
            var dst = new Color[src.Length];
            for (int j = 0; j < h; j++)
            for (int i = 0; i < w; i++)
            {
                Color sum = default; int n = 0;
                for (int b = -1; b <= 1; b++)
                {
                    int jj = j + b;
                    if (jj < 0 || jj >= h) continue;
                    for (int a = -1; a <= 1; a++) { sum += src[jj * w + (i + a + w) % w]; n++; }
                }
                dst[j * w + i] = sum / n;
            }
            return dst;
        }

        private void Apply()
        {
            if (UnderView.Sky && deck == null) { deck = CreateDeck(); UpdateWeather(); }
            if (deck != null) deck.SetActive(UnderView.Sky);
            fall?.SetVisible(UnderView.Layer == MapLayer.Surface);
        }

        private GameObject CreateDeck()
        {
            var shader = Resources.Load<Shader>("Shaders/SkyVeil");
            if (shader == null) { Debug.LogWarning("[SkyLayer] Shaders/SkyVeil not found."); return null; }
            var go = GameObject.CreatePrimitive(PrimitiveType.Quad);
            go.name = "SkyDeck";
            Destroy(go.GetComponent<Collider>()); // clicks go through to the tiles
            go.transform.SetParent(transform, false);
            go.transform.rotation = Quaternion.Euler(90f, 0f, 0f);
            go.transform.localScale = new Vector3(DeckSize, DeckSize, 1f);
            go.transform.position = new Vector3(0f, DeckHeight, 0f);
            var rend = go.GetComponent<MeshRenderer>();
            rend.sharedMaterial = material = new Material(shader) { name = "SkyVeil" };
            rend.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            rend.receiveShadows = false;
            return go;
        }

        // Keep the deck under the camera (the map wraps east–west, so the view can be anywhere)
        private void LateUpdate()
        {
            if (!climateHooked) HookClimate();
            if (!eventsHooked) HookEvents();
            features.Tick(material);
            if (fall != null && Time.time >= nextRainRefresh)
            {
                nextRainRefresh = Time.time + 2f;
                fall.Refresh(features.RainAt); // rain under the moving typhoons and fronts
            }
            if (material != null && Time.time - weatherChanged < WeatherFade + 0.5f)
                material.SetFloat("_WeatherBlend", Mathf.SmoothStep(0f, 1f, (Time.time - weatherChanged) / WeatherFade));
            if (deck == null || !deck.activeSelf) return;
            var cam = Camera.main;
            if (cam == null) return;
            var p = cam.transform.position;
            deck.transform.position = new Vector3(p.x, DeckHeight, p.z);
        }
    }
}
