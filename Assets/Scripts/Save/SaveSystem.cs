using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using NaturalHistory.Core;
using NaturalHistory.Evolution;
using NaturalHistory.Players;
using NaturalHistory.Progression;
using NaturalHistory.World;
using UnityEngine;

namespace NaturalHistory.Save
{
    // Everything needed to resume a game. The map is stored as seed + size and regenerated
    // on load (WorldGenerator is deterministic); add per-cell changes here once cells can change.
    [Serializable]
    public class SaveData
    {
        public const int CurrentVersion = 1;

        public int version = CurrentVersion;
        public string savedAtUtc;          // ISO 8601

        public int mapWidth;
        public int mapHeight;
        public int worldSeed;

        public int playerCol = -1;         // human player's unit
        public int playerRow = -1;

        public List<PlayerSetup> players = new(); // empty in saves from before players existed

        public GameSettings settings;      // New Game choices: land area, game length, starting period
        public bool hasSettings;           // false in saves from before them (defaults then)

        public int turn;                   // 0 when no TurnManager is running
        public string age;                 // GeologicalAge name (informational; restored from turn)

        public int evolutionPoints;
        public List<string> discovered;         // species the human player has seen (ProgressionManager); null in older saves
        public List<string> morphology = new(); // focused species' items (saves before per-species trees: the only ones)
        public List<string> ethology   = new();

        // Evolution (see EvolutionManager); empty in older saves
        public List<SpeciesTraitsSave> speciesTraits = new();
        public List<CopySave> copies = new();
        public List<WildSave> wild = new();     // wild groups born during the game (WildBirths)
        public List<string> evolved = new();    // "player:from>to" links each player has used (older saves: "from>to", the human's)
        public string focusSpecies;
        public List<string> everOwned;          // species the human player has ever had (EvolutionManager: Revive); null in older saves
        public List<int> aiPoints;
        public List<string> discoveries;        // grounds, plants and animals the human player has discovered (Progression/Discoveries); null in older saves              // each AI player's EP, by player index (Players/AiPlayers); null in older saves
        public string explored;                 // tiles the human player has explored, a bit per tile (FogOfWar); null in older saves

        public DateTime SavedAt => DateTime.TryParse(savedAtUtc, null, System.Globalization.DateTimeStyles.RoundtripKind, out var t) ? t.ToLocalTime() : DateTime.MinValue;
    }

    // JSON save files in {persistentDataPath}/Saves/slot{N}.json, and the autosave (AutoSlot), written
    // at the start of every turn, in autosave.json
    public static class SaveSystem
    {
        public const int SlotCount = 3;
        public const int AutoSlot  = 0;

        private static string Folder => Path.Combine(Application.persistentDataPath, "Saves");
        private static string PathFor(int slot) => Path.Combine(Folder, slot == AutoSlot ? "autosave.json" : $"slot{slot}.json");

        // Reads a slot without applying it (for the save/load list). Null if empty or unreadable.
        public static SaveData Peek(int slot)
        {
            var path = PathFor(slot);
            if (!File.Exists(path)) return null;
            try { return JsonUtility.FromJson<SaveData>(File.ReadAllText(path)); }
            catch (Exception e)
            {
                Debug.LogWarning($"[SaveSystem] Could not read {path}: {e.Message}");
                return null;
            }
        }

        public static bool Save(int slot)
        {
            var data = Capture();
            if (data == null) return false;

            try
            {
                Directory.CreateDirectory(Folder);
                // Write to a temp file first so a crash mid-write can't corrupt the existing save
                var path = PathFor(slot);
                var tmp  = path + ".tmp";
                File.WriteAllText(tmp, JsonUtility.ToJson(data, true));
                if (File.Exists(path)) File.Delete(path);
                File.Move(tmp, path);
                Debug.Log($"[SaveSystem] Saved slot {slot} → {path}");
                return true;
            }
            catch (Exception e)
            {
                Debug.LogError($"[SaveSystem] Save to slot {slot} failed: {e.Message}");
                return false;
            }
        }

        public static bool Load(int slot)
        {
            bool ok = false;
            var steps = LoadSteps(slot, r => ok = r, float.PositiveInfinity);
            while (steps.MoveNext()) { }
            return ok;
        }

        // Load in steps, giving the frame back now and then while the map is rebuilt (the loading
        // screen runs it as a coroutine); `done` gets whether it worked
        public static System.Collections.IEnumerator LoadSteps(int slot, Action<bool> done, float budget = 0.04f)
        {
            var data = Peek(slot);
            if (data == null) { done(false); yield break; }
            if (data.version > SaveData.CurrentVersion)
            {
                Debug.LogError($"[SaveSystem] Slot {slot} is from a newer version ({data.version}).");
                done(false);
                yield break;
            }
            var apply = Apply(data, budget);
            while (apply.MoveNext()) yield return apply.Current;
            Debug.Log($"[SaveSystem] Loaded slot {slot} (seed {data.worldSeed}, turn {data.turn})");
            done(true);
        }

        public static void Delete(int slot)
        {
            var path = PathFor(slot);
            if (File.Exists(path)) File.Delete(path);
        }

        private static SaveData Capture()
        {
            var grid = HexGrid.Instance;
            if (grid == null || !grid.IsGenerated)
            {
                Debug.LogWarning("[SaveSystem] Nothing to save: no generated map.");
                return null;
            }

            var data = new SaveData
            {
                savedAtUtc = DateTime.UtcNow.ToString("o"),
                mapWidth   = grid.Width,
                mapHeight  = grid.Height,
                worldSeed  = grid.WorldSeed,
                turn       = TurnManager.Instance != null ? TurnManager.Instance.CurrentTurn : 0,
                age        = AgeManager.Instance != null ? AgeManager.Instance.CurrentAge.ToString() : "",
                settings   = GameOptions.Current,
                hasSettings = true,
            };

            if (PlayerManager.Instance != null) data.players = PlayerManager.Instance.CurrentSetups();

            var player = UnityEngine.Object.FindAnyObjectByType<PlayerBall>();
            if (player != null && player.Cell != null)
                (data.playerCol, data.playerRow) = player.Cell.Coordinates.ToOffsetCoordinates();

            var progression = ProgressionManager.Instance;
            if (progression != null)
            {
                data.evolutionPoints = progression.EvolutionPoints;
                data.discovered      = progression.Discovered.ToList();
                data.morphology = progression.Morphology.UnlockedIds.ToList();
                data.ethology   = progression.Ethology.UnlockedIds.ToList();
            }
            EvolutionManager.Instance?.Capture(data);
            data.aiPoints = Players.AiPlayers.Instance?.Capture();
            data.discoveries = Discoveries.Instance?.Capture();
            WildBirths.Instance?.Capture(data);
            data.explored = FogOfWar.Instance?.CaptureExplored();
            return data;
        }

        private static System.Collections.IEnumerator Apply(SaveData data, float budget)
        {
            // The game's settings first: the land area shapes the regenerated map, the game length
            // how turns map onto dates
            GameOptions.Current = GameOptions.Next = GameOptions.FromSave(data.settings, data.hasSettings);
            AgeManager.Instance?.ReloadAges();

            // Before the map: PlayerManager places everyone when it is generated
            PlayerManager.Instance?.Restore(data.players);

            var grid = HexGrid.Instance;
            if (grid != null)
            {
                // Generated listeners (PlayerBall, camera) run inside this call
                var generate = grid.GenerateSteps(data.mapWidth, data.mapHeight, data.worldSeed, budget);
                while (generate.MoveNext()) yield return generate.Current;

                var player = UnityEngine.Object.FindAnyObjectByType<PlayerBall>();
                var cell   = grid.GetCell(data.playerCol, data.playerRow);
                if (player != null && cell != null) player.PlaceAt(cell);
            }

            // The period, date and climate all follow from the turn number
            if (TurnManager.Instance != null && data.turn > 0)
                TurnManager.Instance.Restore(data.turn);
            // a game saved before the Devonian goes on on the seabed
            if (AgeManager.Instance != null) UnderView.Set(GameOptions.StartsUnderSea(AgeManager.Instance.CurrentAge));

            ProgressionManager.Instance?.Restore(data.evolutionPoints, data.morphology, data.ethology, data.discovered);
            EvolutionManager.Instance?.Restore(data); // after the map: puts the copies back on it
            Players.AiPlayers.Instance?.Restore(data.aiPoints);
            Discoveries.Instance?.Restore(data.discoveries);
            WildBirths.Instance?.Restore(data);       // and the wild groups
            FogOfWar.Instance?.RestoreExplored(data.explored);
        }
    }
}
