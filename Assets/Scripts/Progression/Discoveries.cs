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
    // What is in sight when a game begins counts as known already (everything seen in its first
    // moments, BaselineSeconds, while the founders and territory appear). Animals of a species you
    // have bring nothing; the first wild group you ever meet, of whatever species, brings a
    // "first encounter" card instead of a new-species one. Off in Safari Mode. Saved.
    public class Discoveries : MonoBehaviour
    {
        public static Discoveries Instance { get; private set; }

        public const int Nearby = 3; // tiles: "your groups nearby"
        private const float BaselineSeconds = 2f; // seen this soon after the game begins: known already
        private const string FirstWildKey = "wild:first";

        public enum Kind { Terrain, Plant, Animal }

        public class Discovery
        {
            public Kind kind;
            public string key, title, text, reward;
            public string species; // an animal's species id
            public Texture picture;
            public HexCell cell;
        }

        public event Action<Discovery> Found;

        private readonly HashSet<string> known = new();
        private bool pending, baselineDue = true;
        private float baselineUntil = -1f;
        private System.Random rng = new();

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Bootstrap()
        {
            if (FindAnyObjectByType<HexGrid>() == null || FindAnyObjectByType<Discoveries>() != null) return;
            new GameObject("Discoveries").AddComponent<Discoveries>();
        }

        private void Awake() => Instance = this;

        private void Start()
        {
            FogOfWar.Changed += Request;
            if (HexGrid.Instance != null) HexGrid.Instance.Generated += OnNewMap;
        }

        private void OnDestroy()
        {
            FogOfWar.Changed -= Request;
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

        private void Request() => pending = true;

        private void LateUpdate()
        {
            // while the opening's baseline lasts, keep looking as the founders and territory appear
            if (baselineUntil >= 0f && Time.unscaledTime < baselineUntil) pending = true;
            if (!pending) return;
            pending = false;
            Scan();
        }

        // ---------- Save ----------

        public List<string> Capture() => known.ToList();

        public void Restore(List<string> saved)
        {
            known.Clear();
            if (saved != null) known.UnionWith(saved);
            baselineDue = saved == null; // an older save: what is in sight now counts as known
            baselineUntil = -1f;
            lastSeed = HexGrid.Instance != null ? HexGrid.Instance.WorldSeed : 0;
        }

        // ---------- Looking ----------

        private static Player Human => PlayerManager.Instance != null ? PlayerManager.Instance.Human : null;

        private void Scan()
        {
            var grid = HexGrid.Instance;
            var colonies = SpeciesColonies.Instance;
            var human = Human;
            if (grid == null || !grid.IsGenerated || colonies == null || human == null || !FogOfWar.Active || SpeciesColonies.SafariMode) return;
            if (!colonies.Groups.Any(g => g != null && g.Owner == human)) return; // before the game has begun
            if (baselineDue) { baselineDue = false; baselineUntil = Time.unscaledTime + BaselineSeconds; }
            bool baseline = Time.unscaledTime < baselineUntil;

            var found = new List<Discovery>();
            void See(Kind kind, string key, HexCell cell, Func<Discovery> make)
            {
                if (!known.Add(key) || baseline) return;
                var d = make();
                if (d == null) return;
                d.kind = kind; d.key = key; d.cell = cell;
                found.Add(d);
            }

            for (int r = 0; r < grid.Height; r++)
            for (int q = 0; q < grid.Width; q++)
            {
                var cell = grid.GetCell(q, r);
                if (cell?.Terrain == null || !FogOfWar.IsVisible(cell)) continue;
                var kind = cell.Terrain.kind;
                if (Grounds.Terrains.ContainsKey(kind)) See(Kind.Terrain, "terrain:" + kind, cell, () => Grounds.Card(kind));
                if (Grounds.Features.ContainsKey(cell.Feature)) See(Kind.Terrain, "feature:" + cell.Feature, cell, () => Grounds.Card(cell.Feature));
                if (Grounds.UnderFeatures.ContainsKey(cell.UnderFeature)) See(Kind.Terrain, "under:" + cell.UnderFeature, cell, () => Grounds.Card(cell.UnderFeature));
                if (grid.ShowsStromatoliteFloor(cell)) See(Kind.Terrain, "floor:stromatolites", cell, Grounds.StromatoliteCard);
                foreach (var p in cell.Plants.Concat(cell.UnderPlants))
                    if (p != null && !UnderView.IsFloor(p)) See(Kind.Plant, "plant:" + p.id, cell, () => PlantCard(p));
                foreach (var g in colonies.GroupsAt(cell))
                {
                    if (g?.Definition == null || g.Owner == human || !FogOfWar.Reveals(g)) continue;
                    var def = g.Definition;
                    string key = "species:" + def.id;
                    if (g.Owner == null && !known.Contains(FirstWildKey))
                    {
                        // the first wild group ever met: a card for the meeting itself, whatever the species
                        known.Add(key);
                        See(Kind.Animal, FirstWildKey, cell, () => FirstWildCard(def));
                        continue;
                    }
                    if (Owns(human, def.id)) { known.Add(key); continue; } // a species of yours is no discovery
                    See(Kind.Animal, key, cell, () => AnimalCard(def));
                }
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
            var cell = cells.FirstOrDefault(c => c != null && SpeciesColonies.FitsHabitat(def, c)
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
