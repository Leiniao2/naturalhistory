using System.Collections.Generic;
using System.Linq;
using NaturalHistory.Core;
using NaturalHistory.Evolution;
using NaturalHistory.World;
using UnityEngine;
using UnityEngine.UIElements;

namespace NaturalHistory.UI
{
    // Civilization-style turn flow for the human player's animals. Each turn the camera is brought
    // to each of your groups that still awaits orders in turn: one with actions left (ColonyGroup
    // .ActionsLeft) and somewhere to go, something to attack or the chance to reproduce, that isn't
    // new this turn (JustBorn) and hasn't been told to skip the turn. Once a group has used its
    // actions the next one is picked; one that still has some after a move stays picked.
    // While any await orders the turn button (beside the selected animal's orders) reads
    // "Next animal (n)" and moves on to the next; when none do it reads "Next Turn" and ends the turn. Shift+click or Shift+Enter ends the turn regardless.
    // Groups with no food within reach (Diets.Starving) come up first.
    public class UnitCycle
    {
        public static UnitCycle Instance { get; private set; }

        private const float RefreshEvery = 0.25f; // seconds between recounts of who awaits orders
        private const float AdvanceDelay = 0.35f; // after a group's turn is done, before the next is picked

        private readonly Button endTurnButton;
        private readonly HashSet<ColonyGroup> skipped = new();
        private readonly List<ColonyGroup> pending = new();
        private readonly Dictionary<ColonyGroup, (int turn, int actions, HexCell cell, bool can)> hasOrders = new();

        private ColonyGroup focus;        // the group the cycle (or the player) last picked
        private bool focusWasPending, focusMoved; // it awaited orders / has set out since it was picked
        private float refreshAt, advanceAt = -1f;
        private bool subscribed;

        public int PendingCount => pending.Count;

        private static SpeciesColonies Colonies => SpeciesColonies.Instance;
        private static int Turn => TurnManager.Instance != null ? TurnManager.Instance.CurrentTurn : 0;

        public UnitCycle(VisualElement root)
        {
            Instance = this;
            endTurnButton = root.Q<Button>("end-turn-button");
            Loc.Changed += () => refreshAt = 0f;
        }

        // Your group needs orders this turn
        public bool Awaits(ColonyGroup g)
        {
            if (g == null || g.Cell == null || g.Owner == null || !g.Owner.IsHuman) return false;
            if (g.JustBorn || !g.CanAttack || g.ActionsLeft <= 0 || skipped.Contains(g) || MoveOrders.Has(g)) return false; // under orders: on its way
            if (g.Stationed) return false; // staying put until given an order
            return HasOrders(g);
        }

        // Somewhere to move, something to attack or a free tile for its young (MoveRange, cached
        // until its tile or actions change)
        private bool HasOrders(ColonyGroup g)
        {
            if (hasOrders.TryGetValue(g, out var c) && c.turn == Turn && c.actions == g.ActionsLeft && c.cell == g.Cell) return c.can;
            var range = MoveRange.For(g, Colonies);
            bool can = range.Destinations.Count > 0 || range.AttackFrom.Count > 0;
            if (!can && EvolutionManager.Instance != null)
            {
                var copy = EvolutionManager.Instance.CopyOf(g);
                can = copy != null && EvolutionManager.Instance.TurnsUntilReproduce(copy) == 0 && EvolutionManager.Instance.ReproduceCell(copy) != null
                      && EvolutionManager.Instance.CanAffordReproduce(copy);
            }
            hasOrders[g] = (Turn, g.ActionsLeft, g.Cell, can);
            return can;
        }

        // The group sits this turn out
        public void Skip(ColonyGroup g)
        {
            if (g == null) return;
            skipped.Add(g);
            Recount();
            Next();
        }

        // End Turn button / Enter: the next group awaiting orders, or the end of the turn
        public void EndTurnOrNext(bool force = false)
        {
            Recount();
            if (!force && pending.Count > 0) { Next(); return; }
            TurnWait.Run(() => TurnManager.Instance?.EndTurn()); // the turning ring by the pointer while the world moves on
        }

        // Picks the next group awaiting orders after the current one, and brings the camera to it
        public void Next()
        {
            advanceAt = -1f;
            var current = Colonies != null ? Colonies.Selected : null;
            if (pending.Count == 0)
            {
                // none left: let go of one that needs no orders (stationed, skipped), so it doesn't
                // stay picked into the next turn as if it had come up
                if (current != null && !Awaits(current)) { Colonies.Deselect(); focus = null; }
                return;
            }
            int at = current != null ? pending.IndexOf(current) : -1;
            Pick(pending[(at + 1) % pending.Count], true);
        }

        private void Pick(ColonyGroup g, bool moveCamera)
        {
            if (g == null || Colonies == null) return;
            Colonies.Order(g);
            focus = g;
            focusWasPending = true;
            focusMoved = false;
            if (moveCamera && CameraController.Main != null) CameraController.Main.FocusUnit(g.transform.position); // close up on it, not the whole world
        }

        private void Recount()
        {
            refreshAt = Time.unscaledTime + RefreshEvery;
            pending.Clear();
            if (Colonies == null) return;
            pending.AddRange(Colonies.Groups.Where(Awaits)
                .OrderByDescending(Diets.Starving)                       // the hungry first: they lose HP each turn (Diets)
                .ThenByDescending(g => UnderView.InLayer(g, UnderView.Layer))); // then those in the layer shown, so the view doesn't jump (a seabed start stays on the seabed)
            skipped.RemoveWhere(g => g == null);
            foreach (var dead in hasOrders.Keys.Where(g => g == null).ToList()) hasOrders.Remove(dead);
        }

        private void OnTurnBegin(int turn)
        {
            skipped.Clear();
            hasOrders.Clear();
            focus = null;
            advanceAt = Time.unscaledTime + AdvanceDelay; // the first group of the new turn
            refreshAt = 0f;
        }

        // Polled every frame by GameMenus
        public void Update(bool modalOpen)
        {
            if (!subscribed && TurnManager.Instance != null) { TurnManager.Instance.OnTurnBegin += OnTurnBegin; subscribed = true; }
            if (Time.unscaledTime >= refreshAt) Recount();

            var colonies = Colonies;
            var selected = colonies != null ? colonies.Selected : null;
            if (selected != null && selected != focus) { focus = selected; focusWasPending = Awaits(selected); focusMoved = false; }
            if (focus != null && focus.IsBusy) focusMoved = true;

            // The picked group has moved, attacked or reproduced: once it has settled, it stays
            // picked if it has actions left, else the next group comes up
            if (focus != null && !focus.IsBusy && advanceAt < 0f && colonies != null && !colonies.IsChoosingTile)
            {
                bool awaits = Awaits(focus);
                if (focusWasPending && !awaits) advanceAt = Time.unscaledTime + AdvanceDelay;
                else if (awaits && selected == null && focusMoved) Pick(focus, false); // back to its orders
                focusWasPending = awaits;
            }

            if (advanceAt >= 0f && Time.unscaledTime >= advanceAt && !modalOpen)
            {
                advanceAt = -1f;
                focus = null;
                Recount();
                Next(); // or, with none awaiting orders, let go of the one picked
            }

            endTurnButton.text = pending.Count > 0 ? Loc.F("Next animal ({0})", pending.Count) : Loc.T("Next Turn");
            endTurnButton.EnableInClassList("next-unit", pending.Count > 0);
        }
    }
}
