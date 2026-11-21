using System;
using System.Collections.Generic;
using System.Linq;
using NaturalHistory.Core;
using NaturalHistory.Data;
using NaturalHistory.Evolution;
using NaturalHistory.Players;
using NaturalHistory.World;
using UnityEngine;

namespace NaturalHistory.Progression
{
    // Discoveries: the first time a new kind of ground (microbial mats, reefs, seamounts, vents,
    // salt lakes…), a new plant or a new animal comes into the human player's sight, a card tells
    // about it (UI/DiscoveryPanel) and brings a reward, picked at random among those that fit:
    //  - EP (more for animals; grows with the periods, EpCosts)
    //  - a Function or Behavior the nearest of your species can acquire now, for free
    //  - your groups nearby healed to full HP
    //  - an animal: a group of that species joins you, next to your nearest group
    //  - food (a plant, or an animal your nearest group can eat): that group raises young for free
    //  - a second wind: every group of yours gets an extra action this turn
    //  - fertile ground: your groups nearby can reproduce again at once
    // Only a move of one of your groups discovers things, and only in the tiles the move brought into
    // its sight, in the layers it can see (OnTravelled, Scan): what is around you when a game begins
    // or at the start of a turn brings nothing, and what is in sight when a game begins counts as
    // known already (everything seen in its first moments, BaselineSeconds, while the founders and
    // territory appear: Baseline), so moving there later brings nothing either. Animals of a species you have bring nothing; the first wild group you ever meet, of whatever species, brings a
    // "first encounter" card instead of a new-species one. Off in Safari Mode. Saved.
    public class Discoveries : MonoBehaviour
    {
        public static Discoveries Instance { get; private set; }

        public const int Nearby = 3; // tiles: "your groups nearby"
        private const string FirstWildKey = "wild:first";
        private const float BaselineSeconds = 2f; // seen this soon after the game begins: known already

        public enum Kind { Terrain, Plant, Animal }

        public class Discovery
        {
            public Kind kind;
            public string key, title, text, reward;
            public string species; // an animal's species id
            public Texture picture;
            public HexCell cell;
            public MapLayer layer; // the layer it is in (the view switches there to show it)
        }

        public event Action<Discovery> Found;

        private readonly HashSet<string> known = new();
        private System.Random rng = new();
        private bool baselineDue = true;
        private float baselineUntil = -1f;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Bootstrap()
        {
            if (FindAnyObjectByType<HexGrid>() == null || FindAnyObjectByType<Discoveries>() != null) return;
            new GameObject("Discoveries").AddComponent<Discoveries>();
        }

        private void Awake() => Instance = this;

        private void Start()
        {
            ColonyGroup.Travelled += OnTravelled;
            if (HexGrid.Instance != null) HexGrid.Instance.Generated += OnNewMap;
        }

        private void OnDestroy()
        {
            ColonyGroup.Travelled -= OnTravelled;
            if (HexGrid.Instance != null) HexGrid.Instance.Generated -= OnNewMap;
            if (Instance == this) Instance = null;
        }

        private int lastSeed;
        private void OnNewMap()
        {
            if (HexGrid.Instance.WorldSeed == lastSeed) return;
            lastSeed = HexGrid.Instance.WorldSeed;
            known.Clear();
            baselineDue = true;
            baselineUntil = -1f;
        }

        // The opening: what is in sight (in either layer) once your founders are there, and for a
        // moment after while the rest appears, is known already, with no cards
        private void LateUpdate()
        {
            if (baselineDue || Time.unscaledTime < baselineUntil) Baseline();
        }

        private void Baseline()
        {
            var grid = HexGrid.Instance;
            var colonies = SpeciesColonies.Instance;
            var human = Human;
            if (grid == null || !grid.IsGenerated || colonies == null || human == null || !FogOfWar.Active) return;
            if (!colonies.Groups.Any(g => g != null && g.Owner == human)) return; // before the game has begun
            if (baselineDue) { baselineDue = false; baselineUntil = Time.unscaledTime + BaselineSeconds; }
            for (int r = 0; r < grid.Height; r++)
            for (int q = 0; q < grid.Width; q++)
            {
                var cell = grid.GetCell(q, r);
                if (cell?.Terrain == null || !FogOfWar.IsVisible(cell)) continue;
                known.Add("terrain:" + cell.Terrain.kind);
                known.Add("feature:" + cell.Feature);
                known.Add("under:" + cell.UnderFeature);
                if (grid.ShowsStromatoliteFloor(cell)) known.Add("floor:stromatolites");
                foreach (var p in cell.Plants.Concat(cell.UnderPlants))
                    if (p != null) known.Add("plant:" + p.id);
                foreach (var g in colonies.GroupsAt(cell))
                    if (g?.Definition != null && g.Owner != human) known.Add("species:" + g.Definition.id);
            }
        }

        // Only a move of one of your groups discovers anything, and only in the tiles the move brought
        // into its sight (not at the start of a turn, nor what others see)
        private void OnTravelled(ColonyGroup g, HexCell from)
        {
            var human = Human;
            var grid = HexGrid.Instance;
            if (g == null || g.Owner != human || human == null || g.Cell == null || from == null || grid == null || SpeciesColonies.SafariMode) return;
            if (baselineDue || Time.unscaledTime < baselineUntil) return; // still the opening
            int bonus = Abilities.VisionBonus(g);
            var before = new HashSet<HexCell>(grid.GetCellsInRange(from, FogOfWar.Vision(g.Definition, from, !g.CanMove) + bonus));
            var fresh = grid.GetCellsInRange(g.Cell, FogOfWar.Vision(g)).Where(c => c != null && !before.Contains(c)).ToList();
            if (fresh.Count > 0) Scan(g, fresh);
        }

        public List<string> Capture() => known.ToList();

        public void Restore(List<string> saved)
        {
            known.Clear();
            if (saved != null) known.UnionWith(saved);
            baselineDue = saved == null || saved.Count == 0; // an older save: what is in sight now counts as known
            baselineUntil = -1f;
            lastSeed = HexGrid.Instance != null ? HexGrid.Instance.WorldSeed : 0;
        }

        // ---------- Looking ----------

        private static Player Human => PlayerManager.Instance != null ? PlayerManager.Instance.Human : null;

        // What `mover` sees in `cells` that is new to you. What it can see depends on where it lives:
        // the surface's ground, landforms, plants and animals only from the surface or the sky, the
        // seabed's and underground's only from there (from the seabed you can't see a mesa on the
        // shore); open water from both. If something is found in another layer than the one on view,
        // the view switches to it and the camera goes there.
        private void Scan(ColonyGroup mover, List<HexCell> cells)
        {
            var grid = HexGrid.Instance;
            var colonies = SpeciesColonies.Instance;
            var human = Human;
            if (grid == null || !grid.IsGenerated || colonies == null || human == null) return;
            var moverLayer = Niches.LayerOf(mover.Niche);
            bool seesSurface = moverLayer != MapLayer.Under || Niches.IsFlyer(mover.Definition) || Niches.IsSurfacer(mover.Definition);
            bool seesUnder   = moverLayer == MapLayer.Under || Niches.IsBurrower(mover.Definition);

            var found = new List<Discovery>();
            void See(Kind kind, string key, HexCell cell, MapLayer layer, Func<Discovery> make)
            {
                if (!known.Add(key)) return;
                var d = make();
                if (d == null) return;
                d.kind = kind; d.key = key; d.cell = cell; d.layer = layer;
                found.Add(d);
            }

            foreach (var cell in cells)
            {
                if (cell?.Terrain == null) continue;
                var kind = cell.Terrain.kind;
                bool surface = seesSurface || cell.IsWater; // open water is seen from below as well
                var terrainLayer = seesSurface ? MapLayer.Surface : MapLayer.Under;
                if (surface && Grounds.Terrains.ContainsKey(kind)) See(Kind.Terrain, "terrain:" + kind, cell, terrainLayer, () => Grounds.Card(kind));
                if (seesSurface && Grounds.Features.ContainsKey(cell.Feature)) See(Kind.Terrain, "feature:" + cell.Feature, cell, MapLayer.Surface, () => Grounds.Card(cell.Feature));
                if (seesUnder && Grounds.UnderFeatures.ContainsKey(cell.UnderFeature)) See(Kind.Terrain, "under:" + cell.UnderFeature, cell, MapLayer.Under, () => Grounds.Card(cell.UnderFeature));
                if (seesUnder && grid.ShowsStromatoliteFloor(cell)) See(Kind.Terrain, "floor:stromatolites", cell, MapLayer.Under, Grounds.StromatoliteCard);
                if (seesSurface)
                    foreach (var p in cell.Plants)
                        if (p != null && !UnderView.IsFloor(p)) See(Kind.Plant, "plant:" + p.id, cell, MapLayer.Surface, () => PlantCard(p));
                if (seesUnder)
                    foreach (var p in cell.UnderPlants)
                        if (p != null && !UnderView.IsFloor(p)) See(Kind.Plant, "plant:" + p.id, cell, MapLayer.Under, () => PlantCard(p));
                foreach (var g in colonies.GroupsAt(cell))
                {
                    if (g?.Definition == null || g.Owner == human) continue;
                    var layer = Niches.LayerOf(g.Niche);
                    if (layer == MapLayer.Under ? !seesUnder : !seesSurface) continue; // in a layer it can't see
                    var def = g.Definition;
                    string key = "species:" + def.id;
                    if (g.Owner == null && !known.Contains(FirstWildKey))
                    {
                        // the first wild group ever met: a card for the meeting itself, whatever the species
                        known.Add(key);
                        See(Kind.Animal, FirstWildKey, cell, layer, () => FirstWildCard(def));
                        continue;
                    }
                    if (Owns(human, def.id)) { known.Add(key); continue; } // a species of yours is no discovery
                    See(Kind.Animal, key, cell, layer, () => AnimalCard(def));
                }
            }
            if (found.Count == 0) return;

            // something in another layer: show that layer, and go to it
            var elsewhere = found.FirstOrDefault(d => d.layer != UnderView.Layer);
            if (elsewhere != null)
            {
                UnderView.Set(elsewhere.layer);
                CameraController.Main?.GlideTo(elsewhere.cell.transform.position, 0.6f);
            }
            foreach (var d in found)
            {
                d.reward = Reward(d);
                Found?.Invoke(d);
            }
        }

        // A species the player has (or had: its trees exist) is no discovery
        private static bool Owns(Player human, string speciesId)
        {
            var colonies = SpeciesColonies.Instance;
            if (colonies != null && colonies.Groups.Any(g => g != null && g.Owner == human && g.Definition?.id == speciesId)) return true;
            return EvolutionManager.Instance != null && EvolutionManager.Instance.HumanOwns(speciesId);
        }

        private static Discovery FirstWildCard(SpeciesDefinition def) => new()
        {
            species = def.id,
            title   = Loc.T("First encounter with the wild"),
            text    = Loc.F("Your animals meet a wild group for the first time: {0} ({1}). Others share this world with you.", Loc.T(def.commonName), def.scientificName),
            picture = UI.SpeciesPortraits.Painting(def),
        };

        private static Discovery PlantCard(PlantDefinition p) => new()
        {
            title = Loc.T(p.commonName),
            text  = (string.IsNullOrEmpty(p.scientificName) ? "" : p.scientificName + "\n") + Loc.T(p.description ?? ""),
        };

        private static Discovery AnimalCard(SpeciesDefinition def) => new()
        {
            species = def.id,
            title   = Loc.T(def.commonName),
            text    = $"{def.scientificName}\n{Loc.T(def.description ?? "")}",
            picture = UI.SpeciesPortraits.Painting(def),
        };

        // ---------- Rewards ----------

        private enum Gift { Points, Item, Heal, Join, Feast, SecondWind, Fertile }

        private string Reward(Discovery d)
        {
            var weights = d.kind switch
            {
                Kind.Animal => new[] { (Gift.Points, 3), (Gift.Join, 2), (Gift.Item, 2), (Gift.Feast, 1), (Gift.SecondWind, 1) },
                Kind.Plant  => new[] { (Gift.Points, 2), (Gift.Feast, 3), (Gift.Heal, 2), (Gift.Item, 1) },
                _           => new[] { (Gift.Points, 3), (Gift.Item, 2), (Gift.Heal, 2), (Gift.SecondWind, 1), (Gift.Fertile, 1) },
            };
            var bag = weights.ToList();
            while (bag.Count > 0)
            {
                int total = bag.Sum(w => w.Item2), pick = rng.Next(total), i = 0;
                while (pick >= bag[i].Item2) { pick -= bag[i].Item2; i++; }
                var gift = bag[i].Item1;
                bag.RemoveAt(i);
                var text = Give(gift, d);
                if (text != null) return text;
            }
            return Give(Gift.Points, d);
        }

        // The reward's text, or null if it can't be given here
        private string Give(Gift gift, Discovery d)
        {
            var human = Human;
            var evolution = EvolutionManager.Instance;
            var progression = ProgressionManager.Instance;
            var colonies = SpeciesColonies.Instance;
            var mine = colonies.Groups.Where(g => g != null && g.Owner == human && g.Cell != null).ToList();
            var nearest = mine.OrderBy(g => g.Cell.Coordinates.DistanceTo(d.cell.Coordinates)).FirstOrDefault();
            var near = mine.Where(g => g.Cell.Coordinates.DistanceTo(d.cell.Coordinates) <= Nearby).ToList();
            switch (gift)
            {
                case Gift.Points:
                {
                    int ep = EpCosts.Of(d.kind == Kind.Animal ? 8 : 6);
                    progression?.AddPoints(ep);
                    return Loc.F("+{0} EP", ep);
                }
                case Gift.Item:
                {
                    if (nearest == null || evolution == null || progression == null) return null;
                    var def = nearest.Definition;
                    var traits = evolution.TraitsOf(def.id);
                    var age = AgeManager.Instance != null ? AgeManager.Instance.CurrentAge : GeologicalAge.Ediacaran;
                    var options = Available(progression.Morphology, def, traits.functions, true, age)
                        .Select(n => (n, true)).Concat(Available(progression.Ethology, def, traits.behaviors, false, age).Select(n => (n, false))).ToList();
                    if (options.Count == 0) return null;
                    var (node, isFunction) = options[rng.Next(options.Count)];
                    (isFunction ? traits.functions : traits.behaviors).Add(node.id);
                    progression.AddPoints(0); // the trees and panels refresh
                    return Loc.F("Your {0} gains {1} for free", Loc.T(def.commonName), Loc.T(node.displayName));
                }
                case Gift.Heal:
                {
                    var hurt = near.Where(g => g.Hp < g.MaxHp).ToList();
                    if (hurt.Count == 0) return null;
                    foreach (var g in hurt) g.Hp = g.MaxHp;
                    return Loc.F(hurt.Count == 1 ? "{0} group of yours nearby is healed" : "{0} groups of yours nearby are healed", hurt.Count);
                }
                case Gift.Join:
                {
                    var def = (d.species == null ? null : GameDataLoader.GetSpecies(d.species));
                    if (def == null || nearest == null || evolution == null) return null;
                    if (Owns(human, def.id)) return null; // the first wild group met may be of a species you have already
                    var group = SpawnNear(nearest, def, human);
                    return group == null ? null : Loc.F("A group of {0} joins you", Loc.T(def.commonName));
                }
                case Gift.Feast:
                {
                    if (nearest == null) return null;
                    if (d.kind == Kind.Animal)
                    {
                        var prey = (d.species == null ? null : GameDataLoader.GetSpecies(d.species));
                        if (prey == null || !FoodWeb.IsPrey(nearest.Definition, prey)) return null;
                    }
                    else if (FoodWeb.SourceOf(nearest.Definition) == FoodWeb.FoodSource.Prey) return null; // a plant feeds plant-eaters only
                    var young = SpawnNear(nearest, nearest.Definition, human);
                    return young == null ? null : Loc.F("A feast: your {0} raises young for free", Loc.T(nearest.Definition.commonName));
                }
                case Gift.SecondWind:
                {
                    if (mine.Count == 0) return null;
                    foreach (var g in mine) g.GrantActions(1);
                    return Loc.T("A second wind: every group of yours gets an extra action this turn");
                }
                case Gift.Fertile:
                {
                    var copies = evolution == null ? new List<OwnedCopy>() : near.Select(evolution.CopyOf).Where(c => c != null && evolution.TurnsUntilReproduce(c) > 0).ToList();
                    if (copies.Count == 0) return null;
                    foreach (var c in copies) c.lastBred = -999;
                    return Loc.T("Fertile ground: your groups nearby can reproduce again at once");
                }
            }
            return null;
        }

        // Items the species can acquire now: not had yet, its prerequisites had, its period begun
        private static IEnumerable<TreeNodeDefinition> Available(ProgressionTree tree, SpeciesDefinition def, HashSet<string> owned, bool isFunction, GeologicalAge age) =>
            tree.Nodes.Where(n => n.cost > 0 && !owned.Contains(n.id)
                && (n.prerequisites ?? new List<string>()).All(owned.Contains)
                && (!Enum.TryParse(n.age, true, out GeologicalAge from) || from <= age)
                && EvolutionData.CanAcquire(def, n, isFunction));

        // A new group of `def` for the player on a free tile next to `by` (or under it) that suits it
        private static ColonyGroup SpawnNear(ColonyGroup by, SpeciesDefinition def, Player owner)
        {
            var colonies = SpeciesColonies.Instance;
            var grid = HexGrid.Instance;
            var cells = new List<HexCell> { by.Cell };
            cells.AddRange(grid.GetNeighbors(by.Cell));
            var cell = cells.FirstOrDefault(c => c != null && ColonyGroup.CanPlace(def, c) // where it can move
                && colonies.GroupAt(c, Niches.Of(def, c)) == null && FoodWeb.HasFood(def, c, colonies, null));
            if (cell == null) return null;
            var group = colonies.SpawnColony(def, cell, owner, Environment.TickCount);
            if (group == null) return null;
            group.BornTurn = TurnManager.Instance != null ? TurnManager.Instance.CurrentTurn : 0;
            EvolutionManager.Instance?.RegisterFounder(owner, group);
            Territory.TerritoryManager.Instance?.Refresh();
            return group;
        }
    }
}
