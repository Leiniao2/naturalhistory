using System.Collections.Generic;
using UnityEngine;

namespace NaturalHistory.World
{
    // Where a selected group can go and what it can attack with the actions it has left this turn
    // (one action per tile, ColonyGroup.MoveAlong; an attack needs an action left on arrival). A
    // breadth-first search from its tile through tiles it can enter, not through a foe; a tile is a
    // destination if the group can live there and its niche is free. A foe it can fight next to the
    // start or to a destination is a target, struck from the nearest such tile. Fixed colonies don't
    // move but strike their neighbours in place. Shown by MovePathView; SpeciesColonies orders it.
    public sealed class MoveRange
    {
        public ColonyGroup Group { get; }
        public HashSet<HexCell> Destinations { get; } = new();
        public Dictionary<HexCell, HexCell> AttackFrom { get; } = new(); // foe's tile -> tile to strike from

        private readonly Dictionary<HexCell, int> steps = new();
        private readonly Dictionary<HexCell, HexCell> parent = new();

        private MoveRange(ColonyGroup group) => Group = group;

        public bool Contains(HexCell cell) => cell != null && (Destinations.Contains(cell) || AttackFrom.ContainsKey(cell));
        public int StepsTo(HexCell cell) => cell != null && steps.TryGetValue(cell, out int s) ? s : -1;

        // The tiles from the group's (not included) to `cell`
        public List<HexCell> PathTo(HexCell cell)
        {
            var path = new List<HexCell>();
            if (cell == null || !steps.ContainsKey(cell)) return path;
            for (var c = cell; c != null && c != Group.Cell; c = parent.TryGetValue(c, out var p) ? p : null) path.Add(c);
            path.Reverse();
            return path;
        }

        public static MoveRange For(ColonyGroup group, SpeciesColonies colonies)
        {
            var range = new MoveRange(group);
            var grid = HexGrid.Instance;
            if (group == null || group.Cell == null || grid == null || colonies == null || group.JustBorn) return range;

            int actions = group.ActionsLeft;
            int reach = group.CanMove ? actions : 0;
            range.steps[group.Cell] = 0;
            var frontier = new Queue<HexCell>();
            frontier.Enqueue(group.Cell);
            while (frontier.Count > 0)
            {
                var c = frontier.Dequeue();
                int s = range.steps[c];
                if (s >= reach) continue;
                foreach (var n in grid.GetNeighbors(c))
                {
                    if (n == null || range.steps.ContainsKey(n) || !group.CanEnter(n)) continue;
                    if (SpeciesColonies.Attackable(group, n) != null) continue; // a foe's tile: a target, not a way through
                    range.steps[n] = s + 1;
                    range.parent[n] = c;
                    frontier.Enqueue(n);
                    if (group.CanLiveAt(n) && colonies.GroupAt(n, Niches.Of(group.Definition, n)) == null) range.Destinations.Add(n);
                }
            }

            if (!group.CanStrike) return range;
            // strike from the start or a destination, with an action still left once there
            var from = new List<HexCell> { group.Cell };
            from.AddRange(range.Destinations);
            from.Sort((a, b) => range.steps[a].CompareTo(range.steps[b]));
            foreach (var c in from)
            {
                if (actions - range.steps[c] < 1) continue;
                foreach (var n in grid.GetNeighbors(c))
                {
                    if (n == null || range.AttackFrom.ContainsKey(n)) continue;
                    if (!(group.CanEnter(n) || !group.CanMove)) continue; // fixed colonies strike in place
                    if (!FogOfWar.IsVisible(n)) continue; // no striking at what can't be seen (fog of war)
                    if (SpeciesColonies.Attackable(group, n) != null) range.AttackFrom[n] = c;
                }
            }
            return range;
        }

        // ---------- Beyond this turn (MoveOrders) ----------

        // Whether the group may end a turn on `cell`: it can live there and its niche is free
        public static bool CanStop(ColonyGroup group, HexCell cell, SpeciesColonies colonies)
        {
            if (group == null || cell == null || colonies == null || !group.CanLiveAt(cell)) return false;
            var holder = colonies.GroupAt(cell, Niches.Of(group.Definition, cell));
            return holder == null || holder == group;
        }

        // The shortest way over the whole map from the group's tile to `target` (not included its
        // own tile), through tiles it can enter and not through a foe; null if there is none or
        // it can't stop there. A breadth-first search: one action per tile, as MoveAlong spends.
        public static List<HexCell> FarPath(ColonyGroup group, HexCell target, SpeciesColonies colonies)
        {
            var grid = HexGrid.Instance;
            if (group == null || group.Cell == null || target == null || target == group.Cell || grid == null || !group.CanMove) return null;
            if (!CanStop(group, target, colonies)) return null;
            var parent = new Dictionary<HexCell, HexCell> { [group.Cell] = null };
            var frontier = new Queue<HexCell>();
            frontier.Enqueue(group.Cell);
            while (frontier.Count > 0)
            {
                var c = frontier.Dequeue();
                if (c == target) break;
                foreach (var n in grid.GetNeighbors(c))
                {
                    if (n == null || parent.ContainsKey(n) || !group.CanEnter(n)) continue;
                    if (SpeciesColonies.Attackable(group, n) != null) continue;
                    parent[n] = c;
                    frontier.Enqueue(n);
                }
            }
            if (!parent.ContainsKey(target)) return null;
            var path = new List<HexCell>();
            for (var c = target; c != null && c != group.Cell; c = parent[c]) path.Add(c);
            path.Reverse();
            return path;
        }

        // How many turns walking `path` takes, this one counting as the first: the actions left
        // now, then a full turn's moves (CombatStats.moves) each turn, every turn ending on a tile
        // it can stop on (CanStop), so a turn may fall short. `legs` gets the number of path tiles
        // covered by the end of each turn. -1 if it can't get there.
        public static int TurnsAlong(ColonyGroup group, List<HexCell> path, SpeciesColonies colonies, List<int> legs = null)
        {
            legs?.Clear();
            if (group == null || path == null || path.Count == 0) return path != null && path.Count == 0 ? 0 : -1;
            int perTurn = Mathf.Max(1, group.Stats.moves);
            int actions = group.JustBorn ? 0 : group.ActionsLeft;
            int at = 0, turn = 1;
            for (int guard = 0; guard < 200; guard++)
            {
                int to = Mathf.Min(path.Count, at + actions);
                while (to > at && !CanStop(group, path[to - 1], colonies)) to--;
                if (to == at && actions >= perTurn) return -1; // a full turn can't reach a tile to stop on
                at = to;
                legs?.Add(at);
                if (at == path.Count) return turn;
                turn++;
                actions = perTurn;
            }
            return -1;
        }

        // The tiles to walk this turn along `path` (TurnsAlong's first leg)
        public static List<HexCell> FirstLeg(ColonyGroup group, List<HexCell> path, SpeciesColonies colonies)
        {
            var legs = new List<int>();
            if (TurnsAlong(group, path, colonies, legs) < 0 || legs.Count == 0) return new List<HexCell>();
            return path.GetRange(0, legs[0]);
        }
    }
}
