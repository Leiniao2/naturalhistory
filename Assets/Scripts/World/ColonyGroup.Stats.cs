using UnityEngine;

namespace NaturalHistory.World
{
    // A group's HP and actions left, kept while it is off the map: the map's groups are re-spawned
    // when the period or the climate shown changes (SpeciesColonies.PlaceColonies), and saved games
    // keep them too, so neither heals a group or gives it its actions back.
    public class CombatState
    {
        public float hp;
        public int actionsLeft, attacksLeft;
        public int turn; // TurnManager.CurrentTurn they were taken in
    }

    // A group's combat state for the turn (see CombatStats, Combat): its hit points, and how many
    // actions (CombatStats.moves: a tile moved, an attack, reproducing) and attacks (one) it has
    // left. Each turn (Combat.BeginTurn) the actions come back and it heals a fifth of its HP, or,
    // with no food on its tile or next to it, loses a quarter (Diets) and may starve.
    // Only groups the player orders are held to their actions: their own, or any in Safari Mode;
    // wild groups moved by the game (WildBirths, migrations) aren't.
    public partial class ColonyGroup
    {
        public const float HealPerTurn = 0.2f; // of the maximum HP

        public CombatStats Stats { get; private set; }
        public float Hp { get; set; }
        public int MaxHp => Stats.hp;
        public int ActionsLeft { get; private set; }
        public int AttacksLeft { get; private set; }

        private bool Ordered => Owner != null || SpeciesColonies.SafariMode;

        private void InitStats()
        {
            Stats = CombatStats.Of(Definition);
            Hp = Stats.hp;
            ActionsLeft = Stats.moves;
            AttacksLeft = 1;
        }

        private static int CurrentTurn => Core.TurnManager.Instance != null ? Core.TurnManager.Instance.CurrentTurn : 0;

        public CombatState CombatNow => new() { hp = Hp, actionsLeft = ActionsLeft, attacksLeft = AttacksLeft, turn = CurrentTurn };

        // Back to a state taken earlier (null: as new). Taken in an earlier turn: the turns since
        // have given it its actions back and healed it once.
        public void RestoreCombat(CombatState state)
        {
            if (state == null) return;
            Hp = Mathf.Clamp(state.hp, 0.1f, MaxHp);
            if (state.turn == CurrentTurn)
            {
                ActionsLeft = Mathf.Clamp(state.actionsLeft, 0, Stats.moves);
                AttacksLeft = Mathf.Clamp(state.attacksLeft, 0, 1);
            }
            else BeginTurn();
        }

        // fed: it found food on its tile or next to it (Diets.Starving): it heals, else it goes hungry
        public void BeginTurn(bool fed = true)
        {
            ActionsLeft = Stats.moves;
            AttacksLeft = 1;
            Hp = fed ? Mathf.Min(MaxHp, Hp + MaxHp * HealPerTurn) : Hp - MaxHp * Diets.StarveLoss;
        }

        // Whether it can still move `tiles` tiles / attack this turn
        public bool HasActions(int tiles = 1) => !Ordered || ActionsLeft >= tiles;
        public bool CanStrike => !Ordered || (AttacksLeft > 0 && ActionsLeft > 0);

        public void SpendActions(int n)
        {
            if (Ordered) ActionsLeft = Mathf.Max(0, ActionsLeft - n);
        }

        // An attack ends the group's turn
        private void SpendAttack()
        {
            if (!Ordered) return;
            AttacksLeft = 0;
            ActionsLeft = 0;
        }
    }
}
