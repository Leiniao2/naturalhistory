using System;
using System.Collections.Generic;
using System.Linq;
using NaturalHistory.Core;
using NaturalHistory.Data;
using NaturalHistory.Evolution;
using NaturalHistory.Progression;
using NaturalHistory.Territory;
using NaturalHistory.World;
using UnityEngine;

namespace NaturalHistory.Players
{
    // The computer players and the wild animals, each turn (after the turn's actions come back,
    // Combat.BeginTurn).
    //
    // AI players play by the human's rules: they earn EP the same way (StartingPoints, PointsPerCenter
    // for each habitat center every turn, KillReward for wiping out a foreign group), spend it on their
    // own species' tree items (EvolutionManager.TraitsOf(player, …)), on evolving and on reproducing,
    // and their groups have the same actions. How they play comes from their faction's personality
    // (factions.json "personality"): aggression (attacking other players, then wild animals), expansion
    // (reproducing, spreading out), evolution (buying the items their next species needs, evolving)
    // and caution (how much a fight's risk puts them off). Each group, in turn:
    //  1. evolves if a link is ready, preferring the latest, strongest target
    //  2. attacks a neighbour (or one a few tiles off, moving there first) it can eat or beat
    //  3. reproduces onto a free neighbouring tile
    //  4. otherwise moves: to food if it is going hungry, else, now and then, outward to spread
    // Wild groups (no owner) do the same without evolving or EP: hunters go for their prey, hungry
    // groups move to food, and they reproduce now and then (capped so the map doesn't fill up).
    public class AiPlayers : MonoBehaviour
    {
        public static AiPlayers Instance { get; private set; }

        private const int WildPerSpecies = 6;    // wild groups of a species reproduce up to this many
        private const int WildTotal      = 220;  // and while the map has fewer wild groups than this
        private const float WildBreedChance = 0.12f;
        private const float WildHuntChance  = 0.6f;

        private readonly Dictionary<int, int> points = new();
        private System.Random rng = new();
        private bool hooked;

        public event Action Changed; // points changed

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Bootstrap()
        {
            if (FindAnyObjectByType<HexGrid>() == null || FindAnyObjectByType<AiPlayers>() != null) return;
            new GameObject("AiPlayers").AddComponent<AiPlayers>();
        }

        private void Awake() => Instance = this;

        private void Start()
        {
            Hook();
            if (PlayerManager.Instance != null) PlayerManager.Instance.PlayersChanged += ResetPoints;
        }

        private void Hook()
        {
            if (hooked || TurnManager.Instance == null) return;
            TurnManager.Instance.OnTurnBegin += OnTurnBegin;
            hooked = true;
        }

        private void Update() { if (!hooked) Hook(); }

        private void OnDestroy()
        {
            if (hooked && TurnManager.Instance != null) TurnManager.Instance.OnTurnBegin -= OnTurnBegin;
            if (PlayerManager.Instance != null) PlayerManager.Instance.PlayersChanged -= ResetPoints;
            if (Instance == this) Instance = null;
        }

        // ---------- EP ----------

        public int Points(int player)
        {
            if (!points.TryGetValue(player, out int p)) points[player] = p = ProgressionManager.Instance != null ? ProgressionManager.Instance.StartingPoints : 20;
            return p;
        }

        public void AddPoints(int player, int amount) { points[player] = Points(player) + amount; Changed?.Invoke(); }
        public void Spend(int player, int amount)     { points[player] = Mathf.Max(0, Points(player) - amount); Changed?.Invoke(); }

        private void ResetPoints() => points.Clear();

        public List<int> Capture()
        {
            var players = PlayerManager.Instance != null ? PlayerManager.Instance.Players : null;
            return players == null ? new List<int>() : players.Select(p => p.IsHuman ? 0 : Points(p.Index)).ToList();
        }

        public void Restore(List<int> saved)
        {
            points.Clear();
            if (saved == null) return;
            for (int i = 0; i < saved.Count; i++) points[i] = saved[i];
        }

        // ---------- Turns ----------

        private static EvolutionManager Evolution => EvolutionManager.Instance;
        private static SpeciesColonies Colonies => SpeciesColonies.Instance;

        // A couple of frames on: a new period rebuilds the map's groups as the turn begins, and the
        // players' copies are only put back at the end of that frame
        private void OnTurnBegin(int turn) => StartCoroutine(PlayLater(turn));

        private System.Collections.IEnumerator PlayLater(int turn)
        {
            yield return null;
            yield return null;
            Play(turn);
        }

        private void Play(int turn)
        {
            if (Colonies == null || GameManager.Instance != null && GameManager.Instance.State != GameState.Playing) return;
            rng = new System.Random((HexGrid.Instance != null ? HexGrid.Instance.WorldSeed : 0) ^ (turn * 7919));
            var players = PlayerManager.Instance != null ? PlayerManager.Instance.Players.Where(p => !p.IsHuman).ToList() : new List<Player>();
            if (turn > 1)
                foreach (var p in players) AddPoints(p.Index, Income(p));
            foreach (var p in players) PlayTurn(p);
            if (!SpeciesColonies.SafariMode) PlayWild();
        }

        private static int Income(Player p)
        {
            var progression = ProgressionManager.Instance;
            var territory = TerritoryManager.Instance;
            int centers = territory == null ? 1 : territory.Centers.Count(c => c.Owner == p);
            return (progression != null ? progression.PointsPerCenter : 5) * centers;
        }

        private static FactionPersonality Personality(Player p) => p.Faction?.personality ?? new FactionPersonality();

        // ---------- AI players ----------

        private void PlayTurn(Player player)
        {
            if (Evolution == null) return;
            var mood = Personality(player);
            BuyItems(player, mood);
            foreach (var copy in Evolution.CopiesOf(player).ToList())
            {
                var g = copy.group;
                if (g == null || !Colonies.Groups.Contains(g) || g.JustBorn || g.IsBusy) continue;
                if (TryEvolve(copy, mood)) continue;
                if (TryAttack(g, mood)) continue;
                if (TryReproduce(copy, mood)) continue;
                TryMove(g, mood.expansion);
            }
        }

        // Buys the items the player's species need for their next evolution, cheapest first,
        // keeping back enough to evolve once everything else is in place
        private void BuyItems(Player player, FactionPersonality mood)
        {
            var progression = ProgressionManager.Instance;
            if (progression == null) return;
            if (rng.NextDouble() > 0.35 + 0.65 * mood.evolution) return; // some turns it saves instead
            var age = AgeManager.Instance != null ? AgeManager.Instance.CurrentAge : GeologicalAge.Ediacaran;
            foreach (var species in Evolution.CopiesOf(player).Select(c => c.species).Distinct().ToList())
            {
                var def = GameDataLoader.GetSpecies(species);
                var traits = Evolution.TraitsOf(player.Index, species);
                if (def == null || traits == null) continue;
                var link = BestLink(species, age);
                if (link == null) continue;
                var wanted = link.functions.Select(id => (progression.Morphology, id, true))
                    .Concat(link.behaviors.Select(id => (progression.Ethology, id, false)))
                    .Where(w => !(w.Item3 ? traits.functions : traits.behaviors).Contains(w.id))
                    .ToList();
                // items whose prerequisites are missing: buy those prerequisites first
                foreach (var (tree, id, isFunction) in wanted)
                    BuyWithPrerequisites(player, def, traits, tree, tree.Get(id), isFunction, age, 0);
            }
        }

        private bool BuyWithPrerequisites(Player player, SpeciesDefinition def, SpeciesTraits traits, ProgressionTree tree,
                                          TreeNodeDefinition node, bool isFunction, GeologicalAge age, int depth)
        {
            if (node == null || depth > 6) return false;
            var owned = isFunction ? traits.functions : traits.behaviors;
            if (owned.Contains(node.id)) return true;
            if (!EvolutionData.CanAcquire(def, node, isFunction)) return false;
            if (Enum.TryParse(node.age, true, out GeologicalAge from) && from > age) return false;
            foreach (var pre in node.prerequisites ?? new List<string>())
                if (!BuyWithPrerequisites(player, def, traits, tree, tree.Get(pre), isFunction, age, depth + 1)) return false;
            if (Points(player.Index) < node.cost) return false;
            Spend(player.Index, node.cost);
            owned.Add(node.id);
            return true;
        }

        // The link worth working towards: its target alive by now, the latest and strongest first
        private static EvolutionLink BestLink(string species, GeologicalAge age) =>
            EvolutionData.From(species)
                .Select(l => (l, d: GameDataLoader.GetSpecies(l.to)))
                .Where(x => x.d != null && !string.IsNullOrEmpty(x.d.model) && (!Enum.TryParse(x.d.firstAge, true, out GeologicalAge a) || a <= age))
                .OrderByDescending(x => Strength(x.d))
                .Select(x => x.l)
                .FirstOrDefault();

        private static float Strength(SpeciesDefinition d)
        {
            var s = CombatStats.Of(d);
            return s.attack + s.defense + s.hp * 0.5f + s.moves * 2f;
        }

        private bool TryEvolve(OwnedCopy copy, FactionPersonality mood)
        {
            var ready = EvolutionData.From(copy.species).Where(l => Evolution.CanEvolve(l, copy))
                .OrderByDescending(l => Strength(GameDataLoader.GetSpecies(l.to))).FirstOrDefault();
            if (ready == null || rng.NextDouble() > 0.4 + 0.6 * mood.evolution) return false;
            return Evolution.Evolve(ready, copy, out _);
        }

        private bool TryReproduce(OwnedCopy copy, FactionPersonality mood)
        {
            if (Evolution.TurnsUntilReproduce(copy) > 0 || !Evolution.CanAffordReproduce(copy)) return false;
            if (rng.NextDouble() > 0.2 + 0.7 * mood.expansion) return false;
            var cells = Evolution.ReproduceCells(copy);
            if (cells.Count == 0) return false;
            return Evolution.Reproduce(copy, out _, cells[0]);
        }

        // ---------- Fighting ----------

        // Attacks the most worthwhile foe it can reach this turn, if any is worth it
        private bool TryAttack(ColonyGroup g, FactionPersonality mood)
        {
            if (!g.CanAttack || !g.CanStrike) return false;
            var range = MoveRange.For(g, Colonies);
            ColonyGroup best = null;
            HexCell bestTile = null, bestFrom = null;
            float bestScore = 0f;
            foreach (var kv in range.AttackFrom)
            {
                var foe = Combat.Defender(g, kv.Key);
                if (foe == null || !Combat.SizesMatch(g, foe)) continue;
                float score = AttackScore(g, foe, mood);
                if (score > bestScore) { bestScore = score; best = foe; bestTile = kv.Key; bestFrom = kv.Value; }
            }
            if (best == null) return false;
            if (bestFrom == null || bestFrom == g.Cell) return g.Attack(bestTile);
            // move next to it first, then strike on arrival
            var path = range.PathTo(bestFrom);
            if (path == null || path.Count == 0 || !Colonies.Travel(g, path)) return false;
            void Strike(ColonyGroup arrived)
            {
                arrived.Arrived -= Strike;
                if (arrived != null && Colonies.Groups.Contains(arrived)) arrived.Attack(bestTile);
            }
            g.Arrived += Strike;
            return true;
        }

        // How good an attack looks, 0 = not worth it: eating prey is always good; a fight is judged
        // by the damage dealt against the counterattack to come, weighed by the personality
        private static float AttackScore(ColonyGroup g, ColonyGroup foe, FactionPersonality mood)
        {
            bool predation = Combat.IsPredation(g, foe);
            float dealt = Combat.Damage(g, foe);
            bool kills = predation || dealt >= foe.Hp;
            float back = kills ? 0f : Combat.Damage(foe, g);
            float risk = back / Mathf.Max(0.1f, g.Hp); // 1 = the counterattack would kill it
            if (risk >= 1f) return 0f;
            float gain = predation ? 1.5f : kills ? 1.2f : dealt / Mathf.Max(1f, foe.MaxHp);
            float value = gain - risk * (0.5f + mood.caution);
            // whom it's keen to fight
            float keen = foe.Owner == null ? 0.4f + 0.6f * mood.aggression   // wild animals
                       : foe.Owner.IsHuman ? mood.aggression * 1.1f         // the human player
                       : mood.aggression;                                   // other AI players
            if (predation && Diets.Starving(g)) keen = 1f;                  // hungry: it hunts
            return value * keen > 0.15f ? value * keen : 0f;
        }

        // ---------- Moving ----------

        // Hungry: to the nearest tile with food. Otherwise, with chance `wander`, outward: to a free
        // tile it can live on, away from its own kind
        private bool TryMove(ColonyGroup g, float wander)
        {
            if (!g.CanMove || !g.HasActions()) return false;
            bool hungry = Diets.Starving(g);
            if (!hungry && rng.NextDouble() > wander * 0.5) return false;
            var range = MoveRange.For(g, Colonies);
            var options = range.Destinations.Where(c => c != g.Cell && g.CanLiveAt(c)).ToList();
            if (options.Count == 0) return false;
            HexCell to;
            if (hungry) to = options.OrderBy(c => range.StepsTo(c)).First();
            else
            {
                // spread out: the tile with the fewest groups of the same owner around it
                int Crowd(HexCell c) => HexGrid.Instance.GetNeighbors(c).Sum(n => Colonies.GroupsAt(n).Count(o => o != g && o.Owner == g.Owner));
                int least = options.Min(Crowd);
                var spread = options.Where(c => Crowd(c) == least).ToList();
                to = spread[rng.Next(spread.Count)];
            }
            var path = range.PathTo(to);
            return path != null && path.Count > 0 && Colonies.Travel(g, path);
        }

        // ---------- Wild animals ----------

        private void PlayWild()
        {
            var wild = Colonies.Groups.Where(g => g != null && g.Owner == null && g.Definition != null && g.Cell != null).ToList();
            int total = wild.Count;
            var perSpecies = wild.GroupBy(g => g.Definition.id).ToDictionary(x => x.Key, x => x.Count());
            var calm = new FactionPersonality { aggression = 0.3f, caution = 0.8f };
            foreach (var g in wild)
            {
                if (!Colonies.Groups.Contains(g) || g.IsBusy || g.JustBorn) continue;
                // hunters go for their prey; others only defend themselves (when attacked)
                if (IsHunter(g) && rng.NextDouble() < WildHuntChance && TryHunt(g, calm)) continue;
                if (Diets.Starving(g) && TryMove(g, 0f)) continue;
                if (total < WildTotal && perSpecies[g.Definition.id] < WildPerSpecies && rng.NextDouble() < WildBreedChance && Breed(g))
                {
                    total++;
                    perSpecies[g.Definition.id]++;
                }
            }
        }

        private static bool IsHunter(ColonyGroup g) =>
            FoodWeb.SourceOf(g.Definition) is FoodWeb.FoodSource.Prey or FoodWeb.FoodSource.ForageOrPrey;

        // A wild hunter only goes for what it can eat
        private bool TryHunt(ColonyGroup g, FactionPersonality mood)
        {
            if (!g.CanAttack) return false;
            foreach (var n in HexGrid.Instance.GetNeighbors(g.Cell))
            {
                var foe = Combat.Defender(g, n);
                if (foe == null || !Combat.SizesMatch(g, foe) || !Combat.IsPredation(g, foe)) continue;
                if ((g.CanMove && !g.CanEnter(n))) continue;
                return g.Attack(n);
            }
            return false;
        }

        // A wild group's young on a free neighbouring tile it can live on
        private bool Breed(ColonyGroup g)
        {
            var def = g.Definition;
            var cells = HexGrid.Instance.GetNeighbors(g.Cell)
                .Where(c => SpeciesColonies.FitsHabitat(def, c) && Colonies.GroupAt(c, Niches.Of(def, c)) == null && FoodWeb.HasFood(def, c, Colonies, null))
                .ToList();
            if (cells.Count == 0) return false;
            var young = Colonies.SpawnColony(def, cells[rng.Next(cells.Count)], null, rng.Next());
            if (young == null) return false;
            young.BornTurn = TurnManager.Instance != null ? TurnManager.Instance.CurrentTurn : 0;
            return true;
        }
    }
}
