using System.Collections.Generic;
using System.Linq;
using NaturalHistory.Core;
using NaturalHistory.Data;
using NaturalHistory.Evolution;
using UnityEngine;

namespace NaturalHistory.World
{
    // The wild animals of the map. The game starts with only the three founding protists: a group of
    // each for every player (TerritoryManager) and a few wild groups of each far from the habitat
    // centers. At the end of each turn, wild groups are born on BirthShare of the tiles no player can
    // see (out of every player's groups' vision and territory; half as many by the late periods), one on each such tile that something
    // suits: one of the players' species, or a relative of one on the evolution tree (a sibling: another
    // species evolving from the same ancestor; for the founders, which have none, what they evolve
    // into), alive in the period the map shows, able to live and eat there with its niche free. In
    // the Ediacaran and the Cambrian only on the sea floor. So the wild world fills up along the
    // branches the players have taken, with their nearest relatives as rivals.
    //
    // The wild groups outlive the period: when the map is rebuilt for another period
    // (SpeciesColonies.PlaceColonies), those whose species still lives are put back where they were,
    // or on another far tile that suits them. Saved with the game (SaveData.wild).
    public class WildBirths : MonoBehaviour
    {
        public static WildBirths Instance { get; private set; }

        private const float BirthShare = 0.025f; // of the tiles out of every player's sight, each turn (early periods)
        private const float LateBirthFactor = 0.5f; // …falling steadily to half that by the present (BirthShareNow)
        private const int   FarFromCenters = 6;  // tiles from every habitat center, at least
        private const int   WildFounders   = 3;  // wild groups of each founding protist at the start

        private SpeciesColonies colonies;
        private HexGrid grid;
        private bool turnsHooked;
        private bool foundersDue; // a new map: the wild founders go out once the habitat centers are set
        // the game's own wild groups, set aside while Safari Mode fills the map with every species
        private readonly List<(string species, int col, int row)> beforeSafari = new();
        private bool safariEnding;
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
            SpeciesColonies.SafariModeChanging += OnSafari;
            if (grid != null) grid.Generated += Forget;
            HookTurns();
        }

        private void OnDestroy()
        {
            if (colonies != null) { colonies.ColoniesClearing -= Remember; colonies.ColoniesPlaced -= PutBack; }
            if (grid != null) grid.Generated -= Forget;
            SpeciesColonies.SafariModeChanging -= OnSafari;
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
        private void Forget() { pending.Clear(); foundersDue = true; }

        // The habitat centers are set up by TerritoryManager in a later frame than the map
        private void LateUpdate()
        {
            if (!foundersDue || colonies == null || grid == null || !grid.IsGenerated) return;
            var territory = Territory.TerritoryManager.Instance;
            // (and not the old map's: their tiles were destroyed with it)
            if (territory == null || territory.Centers.Count == 0 || territory.Centers.Any(c => c.Cell == null)) return;
            foundersDue = false;
            PlaceWildFounders();
        }

        // A few wild groups of each founding protist, far from every habitat center
        private void PlaceWildFounders()
        {
            var rng = new System.Random(grid.WorldSeed ^ 0x51f7);
            foreach (var id in Territory.TerritoryManager.Starters)
            {
                var def = GameDataLoader.GetSpecies(id);
                if (def == null || string.IsNullOrEmpty(def.model) || !colonies.IsAliveNow(def)) continue;
                for (int i = 0; i < WildFounders; i++)
                {
                    var cells = FarCells(def);
                    if (cells.Count == 0) break;
                    colonies.SpawnColony(def, cells[rng.Next(cells.Count)], null, rng.Next());
                }
            }
        }

        // ---------- Births ----------

        private void OnTurnEnd(int turn)
        {
            if (colonies == null || grid == null || !grid.IsGenerated || SpeciesColonies.SafariMode) return;
            var rng = new System.Random(grid.WorldSeed ^ (turn * 7349));
            var candidates = Siblings().ToList();
            if (candidates.Count == 0) return;
            var blind = BlindCells();
            int births = 0, tries = Mathf.RoundToInt(blind.Count * BirthShareNow);
            for (int i = 0; i < tries && blind.Count > 0; i++)
            {
                int k = rng.Next(blind.Count);
                var cell = blind[k];
                blind[k] = blind[blind.Count - 1];
                blind.RemoveAt(blind.Count - 1);
                var fits = candidates.Where(d => CanBeBornAt(d, cell)).ToList();
                if (fits.Count == 0) continue;
                if (colonies.SpawnColony(fits[rng.Next(fits.Count)], cell, null, rng.Next()) != null) births++;
            }
            if (births > 0) Debug.Log($"[WildBirths] {births} wild groups born out of the players' sight.");
        }

        // The birth rate: BirthShare up to the Cambrian, then less each period, down to half by the Quaternary
        private static float BirthShareNow
        {
            get
            {
                var age = AgeManager.Instance != null ? AgeManager.Instance.CurrentAge : GeologicalAge.Ediacaran;
                float t = Mathf.Clamp01((float)(age - GeologicalAge.Cambrian) / (GeologicalAge.Quaternary - GeologicalAge.Cambrian));
                return BirthShare * Mathf.Lerp(1f, LateBirthFactor, t);
            }
        }

        // Tiles no player sees: out of the full vision of every player's groups (as the fog of war
        // reckons it), off their territory, and out of what the human sees right now
        private List<HexCell> BlindCells()
        {
            var seen = new HashSet<HexCell>();
            foreach (var g in colonies.Groups)
                if (g != null && g.Owner != null && g.Cell != null)
                    foreach (var c in grid.GetCellsInRange(g.Cell, FogOfWar.Vision(g))) seen.Add(c);
            var territory = Territory.TerritoryManager.Instance;
            var blind = new List<HexCell>();
            for (int r = 0; r < grid.Height; r++)
            for (int q = 0; q < grid.Width; q++)
            {
                var cell = grid.GetCell(q, r);
                if (cell == null || seen.Contains(cell) || (territory != null && territory.OwnerOf(cell) != null)) continue;
                if (FogOfWar.Active && FogOfWar.IsVisible(cell)) continue;
                blind.Add(cell);
            }
            return blind;
        }

        // Ediacaran and Cambrian: only sea-floor life (no wild animals on land or at the sea surface yet)
        private static bool EarlyPeriod =>
            AgeManager.Instance != null && AgeManager.Instance.CurrentAge <= GeologicalAge.Cambrian;

        public bool CanBeBornAt(SpeciesDefinition def, HexCell cell)
        {
            if (!ColonyGroup.CanPlace(def, cell)) return false; // its habitat, where it can move
            var niche = Niches.Of(def, cell);
            if (EarlyPeriod && (!cell.IsWater || Niches.LayerOf(niche) != MapLayer.Under)) return false;
            return colonies.GroupAt(cell, niche) == null && !colonies.HeldByOther(cell, null) && FoodWeb.HasFood(def, cell, colonies, null);
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

        // The players' species themselves, and the species evolving from the same ancestor as one of
        // them (for a species without one, the founders at the root of the tree: what it evolves
        // into), alive now
        private IEnumerable<SpeciesDefinition> Siblings()
        {
            var owned = new HashSet<string>(colonies.Groups.Where(g => g != null && g.Owner != null).Select(g => g.Definition.id));
            var seen  = new HashSet<string>();
            foreach (var id in owned)
            {
                var own = GameDataLoader.GetSpecies(id);
                if (seen.Add(id) && own != null && !string.IsNullOrEmpty(own.model) && colonies.IsAliveNow(own)) yield return own;
                var parents = EvolutionData.To(id).Select(l => l.from).Distinct().ToList();
                var relatives = parents.Count > 0 ? parents.SelectMany(p => EvolutionData.From(p)) : EvolutionData.From(id);
                foreach (var link in relatives)
                {
                    if (!seen.Add(link.to)) continue;
                    var def = GameDataLoader.GetSpecies(link.to);
                    if (def != null && !string.IsNullOrEmpty(def.model) && colonies.IsAliveNow(def)) yield return def;
                }
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
                if (cell == null || !CanBeBornAt(def, cell)) continue;
                if (centers.Any(c => Distance(c, cell) < FarFromCenters)) continue;
                if (FogOfWar.Active && FogOfWar.IsVisible(cell)) continue; // never in the human's sight
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

        // Before the map's groups are cleared: where the wild ones are (in Safari Mode the map places
        // every species itself; leaving it, the groups set aside on entering come back)
        private void Remember()
        {
            pending.Clear();
            if (safariEnding) { pending.AddRange(beforeSafari); beforeSafari.Clear(); safariEnding = false; return; }
            if (SpeciesColonies.SafariMode) return;
            pending.AddRange(WildNow());
        }

        private List<(string species, int col, int row)> WildNow()
        {
            var list = new List<(string, int, int)>();
            foreach (var g in colonies.Groups)
                if (g != null && g.Owner == null && g.Definition != null && g.Cell != null)
                {
                    var (col, row) = g.Cell.Coordinates.ToOffsetCoordinates();
                    list.Add((g.Definition.id, col, row));
                }
            return list;
        }

        private void OnSafari(bool on)
        {
            if (colonies == null) return;
            if (on) { beforeSafari.Clear(); beforeSafari.AddRange(WildNow()); }
            else safariEnding = true;
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
                if (cell == null || !ColonyGroup.CanPlace(def, cell) || colonies.GroupAt(cell, Niches.Of(def, cell)) != null || colonies.HeldByOther(cell, null))
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
            // in Safari Mode the game's own wild groups are the ones set aside
            foreach (var (species, col, row) in SpeciesColonies.SafariMode ? beforeSafari : WildNow())
                data.wild.Add(new WildSave { species = species, col = col, row = row });
        }

        // After the map and the players' copies are back
        public void Restore(Save.SaveData data)
        {
            if (data?.wild == null || colonies == null) return;
            foundersDue = false; // the saved game has its own wild groups
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
