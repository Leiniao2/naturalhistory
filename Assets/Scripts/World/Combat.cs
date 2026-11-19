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

        // Sizes close enough to fight, or a swarm or blood feeder going for something bigger (Abilities)
        public static bool CanFight(ColonyGroup attacker, ColonyGroup defender) =>
            SizesMatch(attacker, defender) || Overwhelms(attacker, defender);

        private static bool Overwhelms(ColonyGroup attacker, ColonyGroup defender) =>
            SizeRatio(attacker, defender) < 1f && (Abilities.Has(attacker, Abilities.Swarm) || Abilities.Has(attacker, Abilities.BloodFeeding));

        public static bool IsPredation(ColonyGroup attacker, ColonyGroup defender) =>
            attacker.Definition != null && defender.Definition != null
            && FoodWeb.SourceOf(attacker.Definition) is FoodWeb.FoodSource.Prey or FoodWeb.FoodSource.ForageOrPrey
            && FoodWeb.IsPrey(attacker.Definition, defender.Definition);

        // attack / defense × size ratio, times the attacker's era factor: HP grows with the era too,
        // so equals still need as many blows in every period, and a later species hits an earlier one
        // all the harder (CombatStats.Era); the counterattack goes the same way
        // and rival or wild animals hit the human player's harder on harder difficulties
        public static float Damage(ColonyGroup from, ColonyGroup to) =>
            (float)from.Stats.attack / Mathf.Max(1, to.Stats.defense) * SizeRatio(from, to) * CombatStats.Era(from.Definition)
            * (to.Owner != null && to.Owner.IsHuman && from.Owner != to.Owner ? GameOptions.FoeDamageShare : 1f);

        // Called when the attacker's blow lands on `cell`. Abilities (see Abilities) change the fight:
        //  - swallowing whole: spines, rolling up, a shell or ink stop it (a crushing bite gets through
        //    all but ink); poison only hurts attackers that don't eat the defender
        //  - damage: a pack, a charge or a shock add to it; ink, camouflage, a burrow, a shell, rolling
        //    up or a herd or school take from it (to no less than a quarter)
        //  - the hit poisons, infects, stuns or holds the survivor, blood feeding heals the attacker,
        //    trampling hurts a second group; touching a poisonous, stinging, spiny or spraying defender
        //    hurts the attacker back
        //  - an ambush (not on the vigilant) gets no counterattack; a tail weapon doubles it
        // Swarms and blood feeders can take on animals of any bigger size.
        public static void Strike(ColonyGroup attacker, HexCell cell)
        {
            var defender = Defender(attacker, cell);
            if (attacker == null || defender == null) return;
            string A = Loc.T(attacker.Definition.commonName), D = Loc.T(defender.Definition.commonName);
            bool overwhelm = !SizesMatch(attacker, defender) && Overwhelms(attacker, defender);
            if (!SizesMatch(attacker, defender) && !overwhelm)
            {
                Report(Loc.F("{0} and {1} are too different in size to fight", A, D), cell);
                return;
            }
            var notes = new List<string>();
            bool crush = Abilities.Has(attacker, Abilities.CrushingBite);

            bool predation = IsPredation(attacker, defender);
            if (predation)
            {
                if (!Unswallowable(defender, crush))
                {
                    float gained = Mathf.Max(0f, defender.Hp);
                    attacker.Hp = Mathf.Min(attacker.MaxHp, attacker.Hp + gained);
                    Destroy(defender);
                    Report(Loc.F("{0} ate the {1} (+{2} HP)", A, D, Hp(gained)) + Notes(notes) + Reward(attacker, defender), cell);
                    return;
                }
                notes.Add(Loc.F("the {0} couldn't swallow it whole", A));
            }

            float dealt = Damage(attacker, defender);
            if (overwhelm) dealt = Mathf.Max(dealt, 0.1f * defender.MaxHp); // many small bites still add up
            if (Abilities.Has(attacker, Abilities.ElectricShock)) dealt *= 1.5f; // through half the defense, about
            if (Abilities.Has(attacker, Abilities.PackHunting) && FriendNear(attacker, defender.Cell, defender)) { dealt *= 1.5f; notes.Add(Loc.T("a pack attack")); }
            if (Abilities.Has(attacker, Abilities.Charge) && attacker.ActedThisTurn) { dealt *= 1.5f; notes.Add(Loc.F("the {0} charged", A)); }

            bool senses = Abilities.Has(attacker, Abilities.Echolocation) || Abilities.Has(attacker, Abilities.Electroreception);
            float guard = 1f;
            if (Abilities.Has(defender, Abilities.InkCloud)) { guard *= 0.5f; notes.Add(Loc.F("the {0} hid in a cloud of ink", D)); }
            if (Abilities.Has(defender, Abilities.Camouflage) && !senses) { guard *= 0.7f; notes.Add(Loc.F("the {0} was hard to see", D)); }
            if (Abilities.Has(defender, Abilities.Burrow) && !Abilities.Has(attacker, Abilities.Electroreception)) { guard *= 0.5f; notes.Add(Loc.F("the {0} dived into its burrow", D)); }
            if (Abilities.Has(defender, Abilities.ShellRetreat) && !crush) { guard *= 0.5f; notes.Add(Loc.F("the {0} pulled into its shell", D)); }
            else if (Abilities.Has(defender, Abilities.RollUp) && !crush) { guard *= 0.6f; notes.Add(Loc.F("the {0} rolled up", D)); }
            if ((Abilities.Has(defender, Abilities.Herding) || Abilities.Has(defender, Abilities.Schooling)) && FriendNear(defender, defender.Cell, attacker))
            {
                guard *= 0.7f;
                notes.Add(Loc.F("the {0} had safety in numbers", D));
            }
            if (crush && (Abilities.Has(defender, Abilities.ShellRetreat) || Abilities.Has(defender, Abilities.RollUp)))
                notes.Add(Loc.F("the {0} bit straight through", A));
            dealt *= Mathf.Max(0.25f, guard);

            defender.Hp -= dealt;
            if (defender.Hp <= 0f && !defender.LimbShed && Abilities.Has(defender, Abilities.Autotomy))
            {
                defender.Hp = 1f;
                defender.LimbShed = true;
                notes.Add(Loc.F("the {0} shed a limb and got away", D));
            }
            if (Abilities.Has(attacker, Abilities.BloodFeeding))
            {
                attacker.Hp = Mathf.Min(attacker.MaxHp, attacker.Hp + 0.5f * dealt);
                notes.Add(Loc.F("the {0} fed on its blood", A));
            }
            if (Abilities.Has(attacker, Abilities.Trample)) Trample(attacker, defender, 0.5f * dealt, notes);

            // touching the defender: what that costs the attacker, whether or not the defender survives
            float hurt = 0f;
            if (!predation && Abilities.Has(defender, Abilities.Poisonous)) Poison(attacker, A, notes);
            if (Abilities.Has(defender, Abilities.StingingCells)) { hurt += 0.25f * dealt; notes.Add(Loc.F("the {0} was stung", A)); }
            if (Abilities.Has(defender, Abilities.Spines)) { hurt += 0.33f * dealt; notes.Add(Loc.F("the {0} was pricked by the spines", A)); }
            if (Abilities.Has(defender, Abilities.ChemicalSpray))
            {
                hurt += 0.1f * attacker.MaxHp;
                attacker.Hold();
                notes.Add(Loc.F("the {0} was sprayed and loses its next turn", A));
            }

            if (defender.Hp <= 0f)
            {
                Destroy(defender);
                attacker.Hp -= hurt;
                string won = Loc.F("{0} attacked the {1} ({2} damage) and wiped it out", A, D, Hp(dealt)) + Reward(attacker, defender);
                if (attacker.Hp <= 0f) { Destroy(attacker); notes.Add(Loc.F("the {0} died of its wounds", A)); }
                Report(won + Notes(notes), cell);
                return;
            }

            // what the hit does to the survivor
            if (Abilities.Has(attacker, Abilities.Venom)) Poison(defender, D, notes);
            else if (Abilities.Has(attacker, Abilities.StingingCells)) { defender.Poison(0.25f * defender.MaxHp, 1); notes.Add(Loc.F("the {0} is poisoned", D)); }
            if (Abilities.Has(attacker, Abilities.Disease)) { defender.Poison(0.1f * defender.MaxHp, 3); notes.Add(Loc.F("the {0} is infected", D)); }
            if (Abilities.Has(attacker, Abilities.ElectricShock)) { defender.Hold(); notes.Add(Loc.F("the {0} is stunned and loses its next turn", D)); }
            else if (Abilities.Has(attacker, Abilities.StickyWeb)) { defender.Hold(); notes.Add(Loc.F("the {0} is caught in the web and loses its next turn", D)); }
            else if (Abilities.Has(attacker, Abilities.Constriction)) { defender.Hold(); notes.Add(Loc.F("the {0} is held in its coils and loses its next turn", D)); }

            bool ambush = Abilities.Has(attacker, Abilities.Ambush) && !attacker.ActedThisTurn;
            if (ambush && Abilities.Has(defender, Abilities.Vigilance)) { ambush = false; notes.Add(Loc.F("the {0} saw the ambush coming", D)); }
            float back = ambush ? 0f : Damage(defender, attacker) * (Abilities.Has(defender, Abilities.TailWeapon) ? 2f : 1f);
            if (ambush) notes.Add(Loc.T("an ambush: no counterattack"));
            else if (Abilities.Has(defender, Abilities.TailWeapon)) notes.Add(Loc.F("the {0} swung its tail", D));
            attacker.Hp -= back + hurt;
            if (attacker.Hp <= 0f)
            {
                Destroy(attacker);
                Report(Loc.F("{0} attacked the {1} ({2} damage) but was wiped out by its counterattack", A, D, Hp(dealt)) + Notes(notes) + Reward(defender, attacker), cell);
                return;
            }
            Report(Loc.F("{0} attacked the {1}: {2} damage, {3} back", A, D, Hp(dealt), Hp(back + hurt)) + Notes(notes), cell);
        }

        // Spiny, rolled-up, shelled or ink-hidden prey can't be eaten in one go: it is fought instead.
        // A crushing bite gets through all but ink.
        private static bool Unswallowable(ColonyGroup g, bool crush) =>
            Abilities.Has(g, Abilities.InkCloud) ||
            (!crush && (Abilities.Has(g, Abilities.Spines) || Abilities.Has(g, Abilities.RollUp) || Abilities.Has(g, Abilities.ShellRetreat)));

        // Venom or a poisonous bite: a fifth of the victim's HP a turn for 2 turns
        private static void Poison(ColonyGroup g, string name, List<string> notes)
        {
            g.Poison(0.2f * g.MaxHp, 2);
            notes.Add(Loc.F("the {0} is poisoned", name));
        }

        // Another group of g's side (of its species, for wild ones) on or next to `at`, other than `except`
        private static bool FriendNear(ColonyGroup g, HexCell at, ColonyGroup except)
        {
            var colonies = SpeciesColonies.Instance;
            var grid = HexGrid.Instance;
            if (colonies == null || grid == null || at == null) return false;
            var tiles = new List<HexCell>(grid.GetNeighbors(at)) { at };
            foreach (var t in tiles)
                foreach (var other in colonies.GroupsAt(t))
                    if (other != g && other != except &&
                        (g.Owner != null ? other.Owner == g.Owner : other.Owner == null && other.Definition == g.Definition))
                        return true;
            return false;
        }

        // Another foreign group in the defender's layer on its tile takes `damage` too
        private static void Trample(ColonyGroup attacker, ColonyGroup defender, float damage, List<string> notes)
        {
            var colonies = SpeciesColonies.Instance;
            if (colonies == null || defender.Cell == null) return;
            var other = colonies.GroupsAt(defender.Cell)
                .FirstOrDefault(g => g != null && g != defender && g.Definition != null && Foes(attacker, g) && SameLayer(attacker, g));
            if (other == null) return;
            string O = Loc.T(other.Definition.commonName);
            other.Hp -= damage;
            if (other.Hp > 0f) { notes.Add(Loc.F("the {0} was trampled ({1} damage)", O, Hp(damage))); return; }
            Destroy(other);
            notes.Add(Loc.F("the {0} was trampled to death", O) + Reward(attacker, other));
        }

        private static string Notes(List<string> notes) => notes.Count == 0 ? "" : " — " + string.Join("; ", notes);

        // The human player earns KillReward EP when one of their groups wipes out a foreign one
        // (attacking, eating it, or in a counterattack); the text to add to the report
        private static string Reward(ColonyGroup winner, ColonyGroup loser)
        {
            var progression = Progression.ProgressionManager.Instance;
            if (winner.Owner != null && !winner.Owner.IsHuman && loser.Owner != winner.Owner) // AI players earn the same
            {
                Players.AiPlayers.Instance?.AddPoints(winner.Owner.Index, Progression.ProgressionManager.KillReward);
                return "";
            }
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
                bool fed = !Diets.Starving(g), poisoned = g.PoisonTurns > 0;
                g.BeginTurn(fed);
                if (g.Hp > 0f) continue;
                var name = Loc.T(g.Definition.commonName);
                var cell = g.Cell;
                bool yours = g.Owner != null && g.Owner.IsHuman;
                Destroy(g);
                if (yours) Report(fed && poisoned ? Loc.F("Your {0} died of poison", name)
                                                  : Loc.F("Your {0} starved: no food on its tile or next to it", name), cell);
                else Debug.Log($"[Combat] A {g.Definition.commonName} starved");
            }
        }
    }
}
