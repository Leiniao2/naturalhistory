using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using NaturalHistory.Core;
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

        public int turn;                   // 0 when no TurnManager is running
        public string age;                 // GeologicalAge name (informational; restored from turn)

        public int evolutionPoints;
        public List<string> morphology = new();
        public List<string> ethology   = new();

        public DateTime SavedAt => DateTime.TryParse(savedAtUtc, null, System.Globalization.DateTimeStyles.RoundtripKind, out var t) ? t.ToLocalTime() : DateTime.MinValue;
    }

    // JSON save files in {persistentDataPath}/Saves/slot{N}.json
    public static class SaveSystem
    {
        public const int SlotCount = 3;

        private static string Folder => Path.Combine(Application.persistentDataPath, "Saves");
        private static string PathFor(int slot) => Path.Combine(Folder, $"slot{slot}.json");

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
            var data = Peek(slot);
            if (data == null) return false;
            if (data.version > SaveData.CurrentVersion)
            {
                Debug.LogError($"[SaveSystem] Slot {slot} is from a newer version ({data.version}).");
                return false;
            }
            Apply(data);
            Debug.Log($"[SaveSystem] Loaded slot {slot} (seed {data.worldSeed}, turn {data.turn})");
            return true;
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
            };

            if (PlayerManager.Instance != null) data.players = PlayerManager.Instance.CurrentSetups();

            var player = UnityEngine.Object.FindAnyObjectByType<PlayerBall>();
            if (player != null && player.Cell != null)
                (data.playerCol, data.playerRow) = player.Cell.Coordinates.ToOffsetCoordinates();

            var progression = ProgressionManager.Instance;
            if (progression != null)
            {
                data.evolutionPoints = progression.EvolutionPoints;
                data.morphology = progression.Morphology.UnlockedIds.ToList();
                data.ethology   = progression.Ethology.UnlockedIds.ToList();
            }
            return data;
        }

        private static void Apply(SaveData data)
        {
            // Before the map: PlayerManager places everyone when it is generated
            PlayerManager.Instance?.Restore(data.players);

            var grid = HexGrid.Instance;
            if (grid != null)
            {
                // Generated listeners (PlayerBall, camera) run inside this call
                grid.Generate(data.mapWidth, data.mapHeight, data.worldSeed);

                var player = UnityEngine.Object.FindAnyObjectByType<PlayerBall>();
                var cell   = grid.GetCell(data.playerCol, data.playerRow);
                if (player != null && cell != null) player.PlaceAt(cell);
            }

            // The period, date and climate all follow from the turn number
            if (TurnManager.Instance != null && data.turn > 0)
                TurnManager.Instance.Restore(data.turn);

            ProgressionManager.Instance?.Restore(data.evolutionPoints, data.morphology, data.ethology);
        }
    }
}
