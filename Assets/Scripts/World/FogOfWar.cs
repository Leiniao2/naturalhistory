using System;
using NaturalHistory.Data;
using NaturalHistory.Players;
using NaturalHistory.Territory;
using UnityEngine;

namespace NaturalHistory.World
{
    // Fog of war for the human player, as in Civilization: tiles never seen lie under cloud; tiles
    // seen before but out of sight now are dimmed and show no animals (their changes go unseen);
    // tiles in sight show everything. What is in sight: every tile within each of your groups'
    // vision (Vision: the tile itself and Vision - 1 rings round it) and your territory.
    // Explored tiles are kept for the game (saved; a new map starts unexplored). Off in Safari Mode,
    // and before the game has begun (no animals or territory of yours yet): everything is in sight.
    //
    // Drawn by FogOfWarEffect (a screen pass over the camera, Shaders/FogOfWar) from a texture of
    // the tiles' states; animals out of sight are hidden and unclickable (UnderView.Shows).
    public class FogOfWar : MonoBehaviour
    {
        public const int DefaultVision = 3; // the tile itself and two rings

        public static FogOfWar Instance { get; private set; }

        // Explored or visible tiles changed (the minimap redraws)
        public static event Action Changed;

        private const float RefreshEvery = 0.2f; // seconds

        private bool[,] explored, visible;
        private int width, height, mapSeed;
        private Texture2D texture;
        private Color32[] pixels;
        private float refreshAt;
        private bool active, textureStale;

        private static readonly int FogTexId    = Shader.PropertyToID("_NHFogTex");
        private static readonly int FogParamsId = Shader.PropertyToID("_NHFogParams");
        private static readonly int FogOriginId = Shader.PropertyToID("_NHFogOrigin");

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Bootstrap()
        {
            if (FindAnyObjectByType<HexGrid>() == null || FindAnyObjectByType<FogOfWar>() != null) return;
            new GameObject("FogOfWar").AddComponent<FogOfWar>();
        }

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
        }

        private void Start()
        {
            // a new game starts unexplored even on the same map (a loaded save restores its own right after)
            if (PlayerManager.Instance != null) PlayerManager.Instance.PlayersChanged += OnPlayersChanged;
        }

        private void OnPlayersChanged()
        {
            var grid = HexGrid.Instance;
            if (grid != null && grid.IsGenerated) ResetMap(grid);
        }

        private void OnDestroy()
        {
            if (PlayerManager.Instance != null) PlayerManager.Instance.PlayersChanged -= OnPlayersChanged;
            if (Instance == this) Instance = null;
            if (texture != null) Destroy(texture);
            Shader.SetGlobalVector(FogParamsId, Vector4.zero);
        }

        // ---------- Queries ----------

        // Whether the fog is on at all (off: everything counts as visible)
        public static bool Active => Instance != null && Instance.active;

        public static bool IsVisible(HexCell cell) => !Active || Instance.Get(Instance.visible, cell);
        public static bool IsExplored(HexCell cell) => !Active || Instance.Get(Instance.explored, cell);

        // Whether a group is shown to the human player: their own always, others only in sight
        public static bool Reveals(ColonyGroup g) =>
            g == null || (g.Owner != null && g.Owner.IsHuman) || IsVisible(g.Cell);

        private bool Get(bool[,] map, HexCell cell)
        {
            if (cell == null || map == null) return false;
            var (col, row) = cell.Coordinates.ToOffsetCoordinates();
            col = ((col % width) + width) % width;
            return row >= 0 && row < height && map[col, row];
        }

        // How far a species sees, counting its own tile: 3 by default (microbes too, so the opening
        // isn't a pinhole); colonies fixed in place 2; big animals 4; long necks (sauropods,
        // giraffes) and fliers 5 or 4. One more from a mountain top.
        public static int Vision(SpeciesDefinition def, HexCell at = null, bool fixedInPlace = false)
        {
            if (def == null) return DefaultVision;
            int v = DefaultVision;
            string group = def.group ?? "";
            if (group == "Sauropod dinosaur" || group == "Giraffid") v = 5;
            else if (Niches.IsFlyer(def)) v = def.sizeCm >= 300f ? 5 : 4;
            else if (def.sizeCm >= 400f) v = 4;
            if (fixedInPlace) v = Mathf.Min(v, 2);
            if (at != null && at.IsMountain) v++;
            return v;
        }

        public static int Vision(ColonyGroup g) => g == null ? DefaultVision : Vision(g.Definition, g.Cell, !g.CanMove) + Abilities.VisionBonus(g) + TraitBonuses.Effects(g).vision;

        // ---------- Update ----------

        private void LateUpdate()
        {
            var grid = HexGrid.Instance;
            if (grid == null || !grid.IsGenerated) return;
            if (explored == null || width != grid.Width || height != grid.Height || mapSeed != grid.WorldSeed) ResetMap(grid);
            if (Time.unscaledTime < refreshAt) return;
            refreshAt = Time.unscaledTime + RefreshEvery;
            Refresh(grid);
        }

        private void ResetMap(HexGrid grid)
        {
            width = grid.Width;
            height = grid.Height;
            mapSeed = grid.WorldSeed;
            explored = new bool[width, height];
            visible = new bool[width, height];
            if (texture != null) Destroy(texture);
            texture = new Texture2D(width, height, TextureFormat.RGBA32, false, true)
            {
                filterMode = FilterMode.Point,
                wrapModeU = TextureWrapMode.Repeat, // the map wraps east–west
                wrapModeV = TextureWrapMode.Clamp,
                name = "NH Fog of war",
            };
            pixels = new Color32[width * height];
            refreshAt = 0f;
            textureStale = true;
        }

        // Recomputes what is in sight, explores it, and uploads the texture if anything changed
        public void Refresh(HexGrid grid = null)
        {
            grid ??= HexGrid.Instance;
            if (grid == null || explored == null) return;
            var human = PlayerManager.Instance != null ? PlayerManager.Instance.Human : null;
            var colonies = SpeciesColonies.Instance;
            var territory = TerritoryManager.Instance;

            var next = new bool[width, height];
            bool anySource = false;
            if (human != null && colonies != null)
                foreach (var g in colonies.Groups)
                {
                    if (g == null || g.Cell == null || g.Owner != human) continue;
                    anySource = true;
                    foreach (var c in grid.GetCellsInRange(g.Cell, Vision(g) - 1)) Mark(next, c);
                }
            if (human != null && territory != null)
                for (int r = 0; r < height; r++)
                for (int q = 0; q < width; q++)
                {
                    var cell = grid.GetCell(q, r);
                    if (cell != null && territory.OwnerOf(cell) == human) { next[q, r] = true; anySource = true; }
                }

            bool on = anySource && !SpeciesColonies.SafariMode;
            bool changed = on != active;
            active = on;
            for (int r = 0; r < height; r++)
            for (int q = 0; q < width; q++)
            {
                bool v = next[q, r];
                if (v != visible[q, r]) { visible[q, r] = v; changed = true; }
                if (v && !explored[q, r]) { explored[q, r] = true; changed = true; }
            }
            if (changed || textureStale) Upload(grid);
            if (changed) Changed?.Invoke();
        }

        private void Mark(bool[,] map, HexCell cell)
        {
            var (col, row) = cell.Coordinates.ToOffsetCoordinates();
            col = ((col % width) + width) % width;
            if (row >= 0 && row < height) map[col, row] = true;
        }

        private void Upload(HexGrid grid)
        {
            for (int r = 0; r < height; r++)
            for (int q = 0; q < width; q++)
                pixels[r * width + q] = new Color32(visible[q, r] ? (byte)255 : (byte)0, explored[q, r] ? (byte)255 : (byte)0, 0, 255);
            textureStale = false;
            texture.SetPixels32(pixels);
            texture.Apply(false);
            Shader.SetGlobalTexture(FogTexId, texture);
            Shader.SetGlobalVector(FogParamsId, new Vector4(active ? 1f : 0f, grid.CellSize, width, height));
            var origin = grid.transform.position;
            Shader.SetGlobalVector(FogOriginId, new Vector4(origin.x, origin.z, 0f, 0f));
            FogOfWarEffect.Ensure(active);
        }

        // ---------- Save / load: explored tiles as a bit string (base64) ----------

        public string CaptureExplored()
        {
            if (explored == null) return null;
            var bytes = new byte[(width * height + 7) / 8];
            for (int r = 0; r < height; r++)
            for (int q = 0; q < width; q++)
                if (explored[q, r]) { int i = r * width + q; bytes[i >> 3] |= (byte)(1 << (i & 7)); }
            return Convert.ToBase64String(bytes);
        }

        // Called after the map has been regenerated from the save
        public void RestoreExplored(string data)
        {
            var grid = HexGrid.Instance;
            if (grid == null || !grid.IsGenerated) return;
            ResetMap(grid);
            if (string.IsNullOrEmpty(data)) return; // older save: explored afresh from the animals' sight
            byte[] bytes;
            try { bytes = Convert.FromBase64String(data); } catch (FormatException) { return; }
            for (int r = 0; r < height; r++)
            for (int q = 0; q < width; q++)
            {
                int i = r * width + q;
                if ((i >> 3) < bytes.Length && (bytes[i >> 3] & (1 << (i & 7))) != 0) explored[q, r] = true;
            }
            refreshAt = 0f;
        }
    }
}
