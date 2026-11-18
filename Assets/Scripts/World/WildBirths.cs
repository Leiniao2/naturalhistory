using System.Collections.Generic;
using System.Linq;
using NaturalHistory.Core;
using NaturalHistory.Data;
using NaturalHistory.Evolution;
using UnityEngine;

namespace NaturalHistory.World
{
    // The wild animals of the map. The game starts with none: each player has only the three founding
    // protists (TerritoryManager). At the end of each turn, now and then, a wild group of a new species
    // is born, far from every habitat center: always a sibling of one of the players' species on the
    // evolution tree (another species evolving from the same ancestor), alive in the period the map
    // shows, on a tile it can live and eat on. So the wild world fills up along the branches the
    // players have taken, with their nearest relatives as rivals.
    //
    // The wild groups outlive the period: when the map is rebuilt for another period
    // (SpeciesColonies.PlaceColonies), those whose species still lives are put back where they were,
    // or on another far tile that suits them. Saved with the game (SaveData.wild).
    public class WildBirths : MonoBehaviour
    {
        public static WildBirths Instance { get; private set; }

        private const float BirthChance = 0.45f; // per turn
        private const int   FarFromCenters = 6;  // tiles from every habitat center, at least

        private SpeciesColonies colonies;
        private HexGrid grid;
        private bool turnsHooked;
        // the wild groups to put back once the map's groups are rebuilt (species id, offset col, row)
        private readonly List<(string species, int col, int row)> pending = new();

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Bootstrap()
        {
            if (FindAnyObjectByType<HexGrid>() == null || FindAnyObjectByType<WildBirths>() != null) return;
            new GameObject("WildBirths").AddComponent<WildBirths>();
        }

        private void Awake() => Instance = this;

        private void Start()
        {
            grid     = HexGrid.Instance;
            colonies = SpeciesColonies.Instance;
            if (colonies != null)
            {
                colonies.ColoniesClearing += Remember;
                colonies.ColoniesPlaced   += PutBack;
            }
            if (grid != null) grid.Generated += Forget;
            HookTurns();
        }

        private void OnDestroy()
        {
            if (colonies != null) { colonies.ColoniesClearing -= Remember; colonies.ColoniesPlaced -= PutBack; }
            if (grid != null) grid.Generated -= Forget;
            if (turnsHooked && TurnManager.Instance != null) TurnManager.Instance.OnTurnEnd -= OnTurnEnd;
            if (Instance == this) Instance = null;
        }

        // TurnManager may start after this component
        private void HookTurns()
        {
            if (turnsHooked || TurnManager.Instance == null) return;
            TurnManager.Instance.OnTurnEnd += OnTurnEnd;
            turnsHooked = true;
        }

        private void Update() { if (!turnsHooked) HookTurns(); }

        // A new map (a new game or a loaded one): no wild groups from the old one
        private void Forget() => pending.Clear();

        // ---------- Births ----------

        private void OnTurnEnd(int turn)
        {
            if (colonies == null || grid == null || !grid.IsGenerated) return;
            var rng = new System.Random(grid.WorldSeed ^ (turn * 7349));
            if (rng.NextDouble() >= BirthChance) return;
            BirthOne(rng);
        }

        // Tries the candidate species in random order until one has a far tile to be born on
        public ColonyGroup BirthOne(System.Random rng)
        {
            var candidates = Siblings().ToList();
            while (candidates.Count > 0)
            {
                int i = rng.Next(candidates.Count);
                var def = candidates[i];
                candidates.RemoveAt(i);
                var cells = FarCells(def);
                if (cells.Count == 0) continue;
                var cell = cells[rng.Next(cells.Count)];
                var group = colonies.SpawnColony(def, cell, null, rng.Next());
                if (group == null) continue;
                Debug.Log($"[WildBirths] A wild {def.commonName} is born far from the habitat centers.");
                return group;
            }
            return null;
        }

        // Species evolving from the same ancestor as one of the players' species, alive now, that
        // no player has (the players' own lines are theirs to evolve)
        private IEnumerable<SpeciesDefinition> Siblings()
        {
            var owned = new HashSet<string>(colonies.Groups.Where(g => g != null && g.Owner != null).Select(g => g.Definition.id));
            var seen  = new HashSet<string>();
            foreach (var id in owned)
                foreach (var parent in EvolutionData.To(id).Select(l => l.from).Distinct())
                    foreach (var link in EvolutionData.From(parent))
                    {
                        if (owned.Contains(link.to) || !seen.Add(link.to)) continue;
                        var def = GameDataLoader.GetSpecies(link.to);
                        if (def != null && !string.IsNullOrEmpty(def.model) && colonies.IsAliveNow(def)) yield return def;
                    }
        }

        // Tiles `def` can live and eat on, its niche free, at least FarFromCenters from every habitat center
        private List<HexCell> FarCells(SpeciesDefinition def)
        {
            var centers = Territory.TerritoryManager.Instance != null
                ? Territory.TerritoryManager.Instance.Centers.Select(c => c.Cell).Where(c => c != null).ToList()
                : new List<HexCell>();
            var result = new List<HexCell>();
            for (int r = 0; r < grid.Height; r++)
            for (int q = 0; q < grid.Width; q++)
            {
                var cell = grid.GetCell(q, r);
                if (cell == null || !SpeciesColonies.FitsHabitat(def, cell)) continue;
                if (colonies.GroupAt(cell, Niches.Of(def, cell)) != null || !FoodWeb.HasFood(def, cell, colonies, null)) continue;
                if (centers.Any(c => Distance(c, cell) < FarFromCenters)) continue;
                result.Add(cell);
            }
            return result;
        }

        // Hex distance, the short way round the east–west wrap
        private int Distance(HexCell a, HexCell b)
        {
            var (ac, ar) = a.Coordinates.ToOffsetCoordinates();
            var (bc, br) = b.Coordinates.ToOffsetCoordinates();
            int best = int.MaxValue;
            for (int shift = -1; shift <= 1; shift++)
                best = Mathf.Min(best, HexCoordinates.FromOffsetCoordinates(ac, ar)
                    .DistanceTo(HexCoordinates.FromOffsetCoordinates(bc + shift * grid.Width, br)));
            return best;
        }

        // ---------- Across periods ----------

        // Before the map's groups are cleared: where the wild ones are
        private void Remember()
        {
            pending.Clear();
            foreach (var g in colonies.Groups)
                if (g != null && g.Owner == null && g.Definition != null && g.Cell != null)
                {
                    var (col, row) = g.Cell.Coordinates.ToOffsetCoordinates();
                    pending.Add((g.Definition.id, col, row));
                }
        }

        // After: the ones still alive back on their tile if it still suits them, else on another far one
        private void PutBack()
        {
            if (pending.Count == 0 || grid == null) return;
            var rng = new System.Random(grid.WorldSeed ^ 0x3a1d ^ pending.Count);
            foreach (var (species, col, row) in pending)
            {
                var def = GameDataLoader.GetSpecies(species);
                if (def == null || string.IsNullOrEmpty(def.model) || !colonies.IsAliveNow(def)) continue;
                var cell = grid.GetCell(col, row);
                if (cell == null || !SpeciesColonies.FitsHabitat(def, cell) || colonies.GroupAt(cell, Niches.Of(def, cell)) != null)
                {
                    var cells = FarCells(def);
                    if (cells.Count == 0) continue;
                    cell = cells[rng.Next(cells.Count)];
                }
                colonies.SpawnColony(def, cell, null, rng.Next());
            }
            pending.Clear();
        }

        // ---------- Saving ----------

        public void Capture(Save.SaveData data)
        {
            data.wild.Clear();
            if (colonies == null) return;
            foreach (var g in colonies.Groups)
                if (g != null && g.Owner == null && g.Definition != null && g.Cell != null)
                {
                    var (col, row) = g.Cell.Coordinates.ToOffsetCoordinates();
                    data.wild.Add(new WildSave { species = g.Definition.id, col = col, row = row });
                }
        }

        // After the map and the players' copies are back
        public void Restore(Save.SaveData data)
        {
            if (data?.wild == null || colonies == null) return;
            foreach (var g in colonies.Groups.Where(g => g != null && g.Owner == null).ToList()) colonies.DespawnColony(g);
            pending.Clear();
            foreach (var w in data.wild) pending.Add((w.species, w.col, w.row));
            PutBack();
        }
    }

    [System.Serializable]
    public class WildSave
    {
        public string species;
        public int col = -1;
        public int row = -1;
    }
}
