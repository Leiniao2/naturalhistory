using System;
using System.Collections.Generic;
using System.Linq;
using NaturalHistory.Core;
using NaturalHistory.Data;
using NaturalHistory.Progression;
using NaturalHistory.World;
using UnityEngine;

namespace NaturalHistory.Players
{
    // The 1–10 players of the current game. Picks spread-out start cells when the map is generated,
    // plants each player's banner, and activates the factions' iconic animals as periods begin.
    // Player 1 is the human; the others are AI seats (they don't act yet).
    public class PlayerManager : MonoBehaviour
    {
        public const int MinPlayers = 1;
        public const int MaxPlayers = 10;
        public const int DefaultPlayerCount = 4;

        public static PlayerManager Instance { get; private set; }

        public IReadOnlyList<Player> Players => players;
        public Player Human => players.FirstOrDefault(p => p.IsHuman);

        public event Action PlayersChanged;
        public event Action<Player, IconicAnimalDefinition> AnimalActivated;

        private readonly List<Player> players = new();
        private List<PlayerSetup> setups = new();
        private HexGrid grid;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Bootstrap()
        {
            if (FindAnyObjectByType<HexGrid>() == null || FindAnyObjectByType<PlayerManager>() != null) return;
            new GameObject("PlayerManager").AddComponent<PlayerManager>();
        }

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
            if (GameDataLoader.Factions == null) GameDataLoader.Initialize();
            SetSetups(RandomSetup(DefaultPlayerCount, new System.Random()));
        }

        private void Start()
        {
            grid = HexGrid.Instance;
            if (grid != null)
            {
                grid.Generated += OnMapGenerated;
                if (grid.IsGenerated) OnMapGenerated();
            }
            if (TurnManager.Instance != null) TurnManager.Instance.OnTurnBegin += OnTurnBegin;
            if (AgeManager.Instance != null) AgeManager.Instance.OnAgeTransition += OnAgeTransition;
        }

        private void OnDestroy()
        {
            if (grid != null) grid.Generated -= OnMapGenerated;
            if (TurnManager.Instance != null) TurnManager.Instance.OnTurnBegin -= OnTurnBegin;
            if (AgeManager.Instance != null) AgeManager.Instance.OnAgeTransition -= OnAgeTransition;
            if (Instance == this) Instance = null;
        }

        // ---------- Setup ----------

        // count players on distinct random factions; the first one is human
        public static List<PlayerSetup> RandomSetup(int count, System.Random rng)
        {
            var factions = GameDataLoader.Factions.OrderBy(_ => rng.Next()).ToList();
            count = Mathf.Clamp(count, MinPlayers, Mathf.Min(MaxPlayers, factions.Count));
            return factions.Take(count).Select((f, i) => PlayerSetup.For(f, human: i == 0)).ToList();
        }

        public List<PlayerSetup> CurrentSetups() => players.Select(p => p.ToSetup()).ToList();

        // New game: these players on a fresh map, back to turn 1 and the starting Evolution Points.
        public void StartNewGame(List<PlayerSetup> newSetups)
        {
            SetSetups(newSetups.Select(s => { var c = s.Clone(); c.startCol = c.startRow = -1; return c; }));
            ProgressionManager.Instance?.Restore(ProgressionManager.Instance.StartingPoints, Array.Empty<string>(), Array.Empty<string>());
            if (grid != null) grid.Generate(grid.Width, grid.Height, UnityEngine.Random.Range(1, int.MaxValue)); // places everyone
            TurnManager.Instance?.Restore(1); // turn 1 activates the first period's iconic animals
        }

        // Loading a save: call before the map is regenerated so the saved start cells are used.
        // Old saves without players keep the current players on new start cells.
        public void Restore(List<PlayerSetup> saved)
        {
            if (saved != null && saved.Count > 0) SetSetups(saved);
            else SetSetups(setups.Select(s => { var c = s.Clone(); c.startCol = c.startRow = -1; return c; }));
        }

        private void SetSetups(IEnumerable<PlayerSetup> newSetups)
        {
            setups = newSetups.Take(MaxPlayers).Select(s => s.Clone()).ToList();
            if (setups.Count > 0 && !setups.Any(s => s.human)) setups[0].human = true;
            players.Clear();
            for (int i = 0; i < setups.Count; i++) players.Add(new Player(i, setups[i]));
            PlayersChanged?.Invoke();
        }

        // ---------- Map ----------

        private void OnMapGenerated()
        {
            var starts = ChooseStartCells();
            for (int i = 0; i < players.Count; i++)
            {
                var player = players[i];
                player.StartCell = starts[i];
                if (player.StartCell == null) continue;

                if (player.IsHuman)
                {
                    var ball = FindAnyObjectByType<PlayerBall>();
                    if (ball != null)
                    {
                        ball.SetColors(player.Primary, player.Secondary, player.Name);
                        ball.PlaceAt(player.StartCell);
                    }
                }
                else
                {
                    var cell = player.StartCell.transform;
                    PlayerMarker.Create(player, cell, cell.InverseTransformPoint(player.StartCell.SurfacePosition));
                }
            }
            PlayersChanged?.Invoke();
        }

        // Saved start cells where available; the rest spread out as far from each other as possible
        // (farthest-point sampling over land, seeded by the world seed so it repeats for a map).
        private HexCell[] ChooseStartCells()
        {
            var result = new HexCell[players.Count];
            if (grid == null || !grid.IsGenerated) return result;

            for (int i = 0; i < setups.Count; i++)
            {
                var cell = setups[i].startCol >= 0 ? grid.GetCell(setups[i].startCol, setups[i].startRow) : null;
                if (cell != null && !cell.IsMountain) result[i] = cell;
            }

            var candidates = new List<HexCell>();
            int margin = Mathf.RoundToInt(grid.Height * 0.12f); // keep away from the polar edges
            for (int r = margin; r < grid.Height - margin; r++)
            for (int q = 0; q < grid.Width; q++)
            {
                var cell = grid.GetCell(q, r);
                if (cell?.Terrain == null || cell.IsWater || cell.IsMountain || cell.Terrain.kind == TerrainKind.IceSheet) continue;
                candidates.Add(cell);
            }
            if (candidates.Count == 0) // all-water map: any non-mountain cell
                for (int r = 0; r < grid.Height; r++)
                for (int q = 0; q < grid.Width; q++)
                    if (grid.GetCell(q, r) is { IsMountain: false } c) candidates.Add(c);

            var rng = new System.Random(grid.WorldSeed);
            var chosen = result.Where(c => c != null).ToList();
            for (int i = 0; i < result.Length; i++)
            {
                if (result[i] != null || candidates.Count == 0) continue;
                HexCell best = null;
                float bestScore = float.MinValue;
                foreach (var cell in candidates)
                {
                    if (chosen.Contains(cell)) continue;
                    float score = chosen.Count == 0 ? (float)rng.NextDouble() : chosen.Min(c => WrappedDistance(c, cell)) + (float)rng.NextDouble() * 0.5f;
                    if (score > bestScore) { bestScore = score; best = cell; }
                }
                result[i] = best;
                if (best != null) chosen.Add(best);
            }
            return result;
        }

        // Hex distance on the east–west cylinder
        private int WrappedDistance(HexCell a, HexCell b)
        {
            var (col, row) = b.Coordinates.ToOffsetCoordinates();
            int best = int.MaxValue;
            for (int shift = -1; shift <= 1; shift++)
                best = Mathf.Min(best, a.Coordinates.DistanceTo(HexCoordinates.FromOffsetCoordinates(col + shift * grid.Width, row)));
            return best;
        }

        // ---------- Iconic animals ----------

        private void OnTurnBegin(int turn)
        {
            // Animals of the opening period wake up with the first turn of a game (not when loading)
            if (turn == 1 && AgeManager.Instance != null) ActivateAnimals(AgeManager.Instance.CurrentAge);
        }

        private void OnAgeTransition(GeologicalAge from, GeologicalAge to) => ActivateAnimals(to);

        private void ActivateAnimals(GeologicalAge age)
        {
            foreach (var player in players)
            {
                if (player.Faction == null) continue;
                foreach (var animal in player.Faction.iconicAnimals)
                {
                    if (!Enum.TryParse<GeologicalAge>(animal.age, out var animalAge) || animalAge != age) continue;
                    if (player.IsHuman) ProgressionManager.Instance?.AddPoints(animal.bonusEvolutionPoints);
                    Debug.Log($"[Players] {player.Name}: iconic animal {animal.name} ({animal.scientificName}) is now active");
                    AnimalActivated?.Invoke(player, animal);
                }
            }
        }
    }
}
