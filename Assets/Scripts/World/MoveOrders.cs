using System.Collections.Generic;
using System.Linq;
using NaturalHistory.Core;
using UnityEngine;

namespace NaturalHistory.World
{
    // Moves to tiles further than one turn's reach, as in Civilization: the group goes as far as it
    // can this turn (MoveRange.FirstLeg) and keeps the order; at the start of each turn it carries
    // on along the shortest way there (found afresh, so it goes round what has moved into the way),
    // until it arrives or no way is left. A group under orders doesn't come up for orders
    // (UnitCycle); giving it another order, or a move or attack of its own, replaces it.
    public class MoveOrders : MonoBehaviour
    {
        private static MoveOrders instance;
        private readonly Dictionary<ColonyGroup, HexCell> orders = new();
        private int dueTurn = -1, dueFrame = -1;
        private bool hooked;

        private static MoveOrders Instance
        {
            get
            {
                if (instance == null) instance = new GameObject("MoveOrders").AddComponent<MoveOrders>();
                return instance;
            }
        }

        public static bool Has(ColonyGroup g) => instance != null && g != null && instance.orders.ContainsKey(g);
        public static HexCell TargetOf(ColonyGroup g) => instance != null && g != null && instance.orders.TryGetValue(g, out var c) ? c : null;
        public static void Cancel(ColonyGroup g) { if (instance != null && g != null) instance.orders.Remove(g); }

        // Sends the group towards `target`: this turn's part at once, the rest over the next turns.
        // False if it can't get there at all.
        public static bool Give(ColonyGroup group, HexCell target)
        {
            var colonies = SpeciesColonies.Instance;
            var path = MoveRange.FarPath(group, target, colonies);
            if (path == null || MoveRange.TurnsAlong(group, path, colonies) < 0) return false;
            var self = Instance;
            self.orders.Remove(group);
            var leg = MoveRange.FirstLeg(group, path, colonies);
            if (leg.Count > 0 && !colonies.MoveGroup(group, leg)) return false;
            if (leg.Count < path.Count) self.orders[group] = target;
            return true;
        }

        private void Update()
        {
            if (!hooked && TurnManager.Instance != null) { TurnManager.Instance.OnTurnBegin += OnTurnBegin; hooked = true; }
            // a frame after the turn begins, once every group has its actions back (Combat.BeginTurn)
            if (dueTurn >= 0 && Time.frameCount >= dueFrame) { dueTurn = -1; CarryOn(); }
        }

        private void OnDestroy()
        {
            if (hooked && TurnManager.Instance != null) TurnManager.Instance.OnTurnBegin -= OnTurnBegin;
            if (instance == this) instance = null;
        }

        private void OnTurnBegin(int turn) { dueTurn = turn; dueFrame = Time.frameCount + 1; }

        private void CarryOn()
        {
            var colonies = SpeciesColonies.Instance;
            foreach (var (group, target) in orders.ToList())
            {
                if (group == null || group.Cell == null || target == null || group.Cell == target) { orders.Remove(group); continue; }
                if (group.IsBusy) continue;
                var path = MoveRange.FarPath(group, target, colonies);
                if (path == null || MoveRange.TurnsAlong(group, path, colonies) < 0) { orders.Remove(group); continue; } // no way left
                var leg = MoveRange.FirstLeg(group, path, colonies);
                if (leg.Count == 0) continue; // nowhere to stop this turn: wait
                if (!colonies.MoveGroup(group, leg)) { orders.Remove(group); continue; }
                if (leg.Count == path.Count) orders.Remove(group); // arriving
            }
        }
    }
}
