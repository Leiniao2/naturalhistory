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
        // Abilities (see Abilities): poison still to come, turns held or stunned, a limb already shed
        public int poisonTurns, heldTurns;
        public float poisonPerTurn;
        public bool limbShed;
        public bool acted; // moved, attacked or reproduced in that turn: no healing at the next
        public bool stationed; // staying put until ordered (the only state that heals)
    }

    // A group's combat state for the turn (see CombatStats, Combat): its hit points, and how many
    // actions (CombatStats.moves: a tile moved, an attack, reproducing) and attacks (one) it has
    // left. Each turn (Combat.BeginTurn) the actions come back and, if it is stationed (Stationed)
    // and took none the turn before, it heals a tenth of its HP, or, with no food on its tile or next
    // to it, loses a quarter (Diets) and may starve. Abilities
    // (Abilities, Combat) add: poison, which takes HP each turn instead of healing; being held or
    // stunned, which costs the next turn's actions; regeneration, which heals twice as fast.
    // Only groups the player orders are held to their actions: their own, or any in Safari Mode;
    // wild groups moved by the game (WildBirths, migrations) aren't.
    public partial class ColonyGroup
    {
        public const float HealPerTurn = 0.1f; // of the maximum HP (twice that with Regeneration)

        // The species' stats plus what its owner's Functions and Behaviors items add (TraitBonuses),
        // worked out again when those change or the group changes hands; HP it gains comes on top
        public CombatStats Stats
        {
            get
            {
                if (bonusVersion != TraitBonuses.Version || bonusOwner != Owner) ApplyBonus();
                return stats;
            }
            private set { baseStats = value; stats = value; bonusVersion = -1; }
        }
        private CombatStats baseStats, stats;
        private int bonusVersion = -1;
        private Players.Player bonusOwner;

        private void ApplyBonus()
        {
            var b = TraitBonuses.For(Definition, Owner);
            int before = stats.hp;
            bool first = bonusVersion < 0 && bonusOwner == null && Owner == null;
            stats = new CombatStats
            {
                attack  = baseStats.attack  + b.attack,
                defense = baseStats.defense + b.defense,
                hp      = baseStats.hp      + b.hp,
                moves   = Mathf.Min(baseStats.moves + b.moves, 5),
            };
            bonusVersion = TraitBonuses.Version;
            bonusOwner   = Owner;
            if (!first && stats.hp != before) Hp = Mathf.Clamp(Hp + (stats.hp - before), 1f, stats.hp);
        }
        public float Hp { get; set; }
        public int MaxHp => Stats.hp;
        public int ActionsLeft { get; private set; }
        public int AttacksLeft { get; private set; }
        private int actionsTurn = -1; // the turn ActionsLeft / AttacksLeft (and its healing) are for

        public int PoisonTurns { get; private set; }
        public float PoisonPerTurn { get; private set; }
        public int HeldTurns { get; private set; }
        public bool LimbShed { get; set; }       // Abilities.Autotomy used up
        public bool ActedThisTurn { get; private set; } // moved or reproduced (Abilities.Ambush)
        public bool FoughtThisTurn { get; private set; } // attacked
        // Stationed: staying put until given an order (the Station button). Only a stationed group
        // that didn't act the turn before heals; any action (a move, an attack, young) ends it.
        public bool Stationed { get; set; }
        // Who attacked it last, and in which turn (wild groups strike back: Players/AiPlayers.PlayWild)
        public ColonyGroup LastAttacker { get; set; }
        public int LastAttackedTurn { get; set; } = -99;

        // Poisoned: loses perTurn HP at the start of each of the next `turns` turns (the stronger dose wins)
        public void Poison(float perTurn, int turns)
        {
            PoisonPerTurn = Mathf.Max(PoisonPerTurn, perTurn);
            PoisonTurns   = Mathf.Max(PoisonTurns, turns);
        }

        // Held (a web, coils) or stunned: no actions next turn
        public void Hold()
        {
            if (!TraitBonuses.Effects(this).holdImmune) HeldTurns = Mathf.Max(HeldTurns, 1);
        }

        private bool Ordered => Owner != null || SpeciesColonies.SafariMode;

        // Actions a turn: the species' moves, one more with Abilities.Sprint
        public int MaxActions => Stats.moves + (Abilities.Has(this, Abilities.Sprint) ? 1 : 0);

        private void InitStats()
        {
            Stats = CombatStats.Of(Definition);
            Hp = Stats.hp;
            ActionsLeft = MaxActions;
            AttacksLeft = 1;
            actionsTurn = CurrentTurn;
        }

        private static int CurrentTurn => Core.TurnManager.Instance != null ? Core.TurnManager.Instance.CurrentTurn : 0;

        public CombatState CombatNow => new()
        {
            hp = Hp, actionsLeft = ActionsLeft, attacksLeft = AttacksLeft, turn = actionsTurn,
            poisonTurns = PoisonTurns, poisonPerTurn = PoisonPerTurn, heldTurns = HeldTurns, limbShed = LimbShed,
            acted = ActedThisTurn || FoughtThisTurn,
            stationed = Stationed,
        };

        // Back to a state taken earlier (null: as new). Taken in an earlier turn: the turns since
        // have given it its actions back and healed it once.
        public void RestoreCombat(CombatState state)
        {
            if (state == null) return;
            Hp = Mathf.Clamp(state.hp, 0.1f, MaxHp);
            PoisonTurns = state.poisonTurns; PoisonPerTurn = state.poisonPerTurn;
            HeldTurns = state.heldTurns; LimbShed = state.limbShed;
            Stationed = state.stationed;
            if (state.turn == CurrentTurn)
            {
                ActionsLeft = Mathf.Clamp(state.actionsLeft, 0, MaxActions);
                AttacksLeft = Mathf.Clamp(state.attacksLeft, 0, 1);
                actionsTurn = CurrentTurn;
                ActedThisTurn = state.acted; // so a rebuild of the map doesn't let it heal after acting
            }
            else
            {
                // taken before this turn began (the map is rebuilt as a turn begins, when another
                // period or climate shows): this turn's actions and healing
                actionsTurn = state.turn;
                BeginTurn();
            }
        }

        // fed: it found food on its tile or next to it (Diets.Starving): it heals, else it goes hungry
        // Once a turn, whether the group was re-spawned before or after Combat.BeginTurn reached it
        public void BeginTurn(bool fed = true)
        {
            if (actionsTurn == CurrentTurn) return;
            actionsTurn = CurrentTurn;
            // only a stationed group that sat the last turn out (no move, attack or young) heals
            bool rested = Stationed && !ActedThisTurn && !FoughtThisTurn;
            ActionsLeft = MaxActions;
            AttacksLeft = 1;
            ActedThisTurn = false;
            FoughtThisTurn = false;
            if (HeldTurns > 0) { HeldTurns--; ActionsLeft = 0; AttacksLeft = 0; }
            // items (TraitBonuses.Effects) heal more at rest, heal a little anyway, and soften hunger and poison
            var effects = TraitBonuses.Effects(this);
            float heal = (rested ? (HealPerTurn + effects.heal) * (Abilities.Has(this, Abilities.Regeneration) ? 2f : 1f) : 0f) + effects.fieldHeal;
            // hungry: dormancy sleeps it off, blubber halves the loss
            if (!fed && !Abilities.Has(this, Abilities.Dormancy))
                Hp -= MaxHp * Diets.StarveLoss * (Abilities.Has(this, Abilities.Blubber) ? 0.5f : 1f) * (1f - effects.starveResist);
            else if (PoisonTurns == 0) Hp = Mathf.Min(MaxHp, Hp + MaxHp * heal);
            if (PoisonTurns > 0)
            {
                Hp -= PoisonPerTurn * (1f - effects.poisonResist);
                if (--PoisonTurns == 0) PoisonPerTurn = 0f;
            }
        }

        // Eating prey with TraitEffects.freeHunt: the actions it had before the attack come back
        // (not the attack: one a turn still)
        private int actionsBeforeAttack;
        public void RefundHuntActions()
        {
            if (Ordered) ActionsLeft = Mathf.Max(ActionsLeft, actionsBeforeAttack);
        }

        // Extra actions this turn (a discovery's second wind, Progression/Discoveries)
        public void GrantActions(int n) => ActionsLeft += Mathf.Max(0, n);

        // Whether it can still move `tiles` tiles / attack this turn
        public bool HasActions(int tiles = 1) => !Ordered || ActionsLeft >= tiles;
        public bool CanStrike => !Ordered || (AttacksLeft > 0 && ActionsLeft > 0);

        public void SpendActions(int n)
        {
            ActedThisTurn = true;
            Stationed = false;
            if (Ordered) ActionsLeft = Mathf.Max(0, ActionsLeft - n);
        }

        // An attack ends the group's turn
        private void SpendAttack()
        {
            FoughtThisTurn = true;
            Stationed = false;
            actionsBeforeAttack = ActionsLeft;
            if (!Ordered) return;
            AttacksLeft = 0;
            ActionsLeft = 0;
        }
    }
}
