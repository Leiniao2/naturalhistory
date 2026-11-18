using System;
using System.Collections.Generic;
using System.Linq;
using NaturalHistory.Core;
using NaturalHistory.Data;
using NaturalHistory.Evolution;
using NaturalHistory.Territory;
using UnityEngine;

namespace NaturalHistory.World
{
    // Fights between groups (see CombatStats, ColonyGroup.Stats):
    //  - Moving at a tile that holds a wild group or another player's in the same layer is an attack.
    //    The tile's biggest such group defends first; the next only once it has been wiped out.
    //  - Animals more than MaxSizeRatio times apart in size can't fight: the attack can't be made.
    //  - A hunter attacking its prey (FoodWeb.IsPrey) eats it: the prey is wiped out whatever its HP,
    //    and the hunter heals by the HP the prey had left (up to its maximum).
    //  - Otherwise the defender loses attack / defense × (attacker size / defender size) × the
    //    attacker's era factor (CombatStats.Era) HP and, if it survives, strikes back the same way;
    //    a group at 0 HP is wiped out.
    //  - A group attacks at most once a turn, and attacking uses up the rest of its actions.
    // Each turn every group gets its actions back and heals a little, or, finding no food on its tile
    // or next to it, loses HP and may starve to death (BeginTurn, Diets).
    public static class Combat
    {
        public const float MaxSizeRatio = 10f;

        public static event Action<string, HexCell> Reported; // what happened, for the toast

        private static float Size(ColonyGroup g) => Mathf.Max(g?.Definition?.sizeCm ?? 1f, 0.0001f);

        public static float SizeRatio(ColonyGroup a, ColonyGroup b) => Size(a) / Size(b);

        public static bool SizesMatch(ColonyGroup a, ColonyGroup b)
        {
            float r = SizeRatio(a, b);
            return r <= MaxSizeRatio && r >= 1f / MaxSizeRatio;
        }

        private static bool Foes(ColonyGroup a, ColonyGroup b) =>
            a != b && (a.Owner == null || b.Owner == null || a.Owner != b.Owner);

        private static bool SameLayer(ColonyGroup a, ColonyGroup b) =>
            Niches.LayerOf(a.Niche) == Niches.LayerOf(b.Niche);

        // Who defends `cell` against `attacker`: the biggest foreign group in its layer there, or null
        public static ColonyGroup Defender(ColonyGroup attacker, HexCell cell)
        {
            var colonies = SpeciesColonies.Instance;
            if (attacker == null || cell == null || colonies == null) return null;
            return colonies.GroupsAt(cell)
                .Where(g => g != null && g.Definition != null && Foes(attacker, g) && SameLayer(attacker, g))
                .OrderByDescending(Size)
                .FirstOrDefault();
        }

        public static bool IsPredation(ColonyGroup attacker, ColonyGroup defender) =>
            attacker.Definition != null && defender.Definition != null
            && FoodWeb.SourceOf(attacker.Definition) is FoodWeb.FoodSource.Prey or FoodWeb.FoodSource.ForageOrPrey
            && FoodWeb.IsPrey(attacker.Definition, defender.Definition);

        // attack / defense × size ratio, times the attacker's era factor: HP grows with the era too,
        // so equals still need as many blows in every period, and a later species hits an earlier one
        // all the harder (CombatStats.Era); the counterattack goes the same way
        public static float Damage(ColonyGroup from, ColonyGroup to) =>
            (float)from.Stats.attack / Mathf.Max(1, to.Stats.defense) * SizeRatio(from, to) * CombatStats.Era(from.Definition);

        // Called when the attacker's blow lands on `cell`
        public static void Strike(ColonyGroup attacker, HexCell cell)
        {
            var defender = Defender(attacker, cell);
            if (attacker == null || defender == null) return;
            string A = Loc.T(attacker.Definition.commonName), D = Loc.T(defender.Definition.commonName);
            if (!SizesMatch(attacker, defender))
            {
                Report(Loc.F("{0} and {1} are too different in size to fight", A, D), cell);
                return;
            }

            if (IsPredation(attacker, defender))
            {
                float gained = Mathf.Max(0f, defender.Hp);
                attacker.Hp = Mathf.Min(attacker.MaxHp, attacker.Hp + gained);
                Destroy(defender);
                Report(Loc.F("{0} ate the {1} (+{2} HP)", A, D, Hp(gained)) + Reward(attacker, defender), cell);
                return;
            }

            float dealt = Damage(attacker, defender);
            defender.Hp -= dealt;
            if (defender.Hp <= 0f)
            {
                Destroy(defender);
                Report(Loc.F("{0} attacked the {1} ({2} damage) and wiped it out", A, D, Hp(dealt)) + Reward(attacker, defender), cell);
                return;
            }
            float back = Damage(defender, attacker);
            attacker.Hp -= back;
            if (attacker.Hp <= 0f)
            {
                Destroy(attacker);
                Report(Loc.F("{0} attacked the {1} ({2} damage) but was wiped out by its counterattack", A, D, Hp(dealt)) + Reward(defender, attacker), cell);
                return;
            }
            Report(Loc.F("{0} attacked the {1}: {2} damage, {3} back", A, D, Hp(dealt), Hp(back)), cell);
        }

        // The human player earns KillReward EP when one of their groups wipes out a foreign one
        // (attacking, eating it, or in a counterattack); the text to add to the report
        private static string Reward(ColonyGroup winner, ColonyGroup loser)
        {
            var progression = Progression.ProgressionManager.Instance;
            if (progression == null || winner.Owner == null || !winner.Owner.IsHuman || loser.Owner == winner.Owner) return "";
            progression.AddPoints(Progression.ProgressionManager.KillReward);
            return Loc.F(" (+{0} EP)", Progression.ProgressionManager.KillReward);
        }

        private static string Hp(float v) => v.ToString(v < 10f ? "0.#" : "0");

        private static void Report(string message, HexCell cell)
        {
            Debug.Log($"[Combat] {message}");
            Reported?.Invoke(message, cell);
        }

        private static void Destroy(ColonyGroup g)
        {
            EvolutionManager.Instance?.RemoveCopy(g);
            SpeciesColonies.Instance?.DespawnColony(g);
            TerritoryManager.Instance?.Refresh();
        }

        // ---------- Turns ----------

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Hook()
        {
            if (TurnManager.Instance != null) TurnManager.Instance.OnTurnBegin += BeginTurn;
            if (SpeciesColonies.Instance != null) SpeciesColonies.Instance.ColoniesClearing += Remember;
            wild.Clear();
        }

        // ---------- Across re-spawns ----------

        // Just before the map's groups are cleared: the players' copies keep their group's state
        // (OwnedCopy.combat, put back by EvolutionManager.Respawn), the wild ones by species and
        // tile, picked up again as WildBirths puts them back (Carried).
        private static readonly Dictionary<(string species, HexCell cell), CombatState> wild = new();

        private static void Remember()
        {
            var colonies = SpeciesColonies.Instance;
            var evolution = EvolutionManager.Instance;
            wild.Clear();
            foreach (var g in colonies.Groups)
            {
                if (g == null || g.Definition == null) continue;
                var copy = evolution != null ? evolution.CopyOf(g) : null;
                if (copy != null) copy.combat = g.CombatNow;
                else if (g.Cell != null) wild[(g.Definition.id, g.Cell)] = g.CombatNow;
            }
        }

        // The state a wild group of `def` re-spawned on `cell` had (once), else one of its species
        internal static CombatState Carried(SpeciesDefinition def, HexCell cell)
        {
            if (def == null || wild.Count == 0) return null;
            (string species, HexCell cell) key = (def.id, cell);
            if (!wild.TryGetValue(key, out var state))
            {
                key = wild.Keys.FirstOrDefault(k => k.species == def.id);
                if (key.species == null || !wild.TryGetValue(key, out state)) return null;
            }
            wild.Remove(key);
            return state;
        }

        private static void BeginTurn(int turn)
        {
            wild.Clear(); // a turn on, the wild groups that were going to come back have
            var colonies = SpeciesColonies.Instance;
            if (colonies == null) return;
            foreach (var g in colonies.Groups.ToList())
            {
                if (g == null) continue;
                g.BeginTurn(fed: !Diets.Starving(g));
                if (g.Hp > 0f) continue;
                var name = Loc.T(g.Definition.commonName);
                var cell = g.Cell;
                bool yours = g.Owner != null && g.Owner.IsHuman;
                Destroy(g);
                if (yours) Report(Loc.F("Your {0} starved: no food on its tile or next to it", name), cell);
                else Debug.Log($"[Combat] A {g.Definition.commonName} starved");
            }
        }
    }
}
