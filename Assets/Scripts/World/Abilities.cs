using System;
using System.Collections.Generic;
using System.Linq;
using NaturalHistory.Core;
using NaturalHistory.Data;
using NaturalHistory.Evolution;
using NaturalHistory.Progression;
using UnityEngine;

namespace NaturalHistory.World
{
    [Serializable]
    public class AbilityDefinition
    {
        public string id, name, description;
        public List<string> unlockFunctions = new(); // any one of these Functions (morphology) unlocks it
        public List<string> unlockBehaviors = new(); // or any one of these Behaviors (ethology)
        public List<string> groups = new();          // species.json groups that have it
        public List<string> species = new();         // and single species
        public List<string> tags = new();            // and species with one of these species.json tags
        public string gene;                          // and species expressing this gene
        public float minGene;                        //   at least this much
        public bool NeedsUnlock => unlockFunctions.Count > 0 || unlockBehaviors.Count > 0;
    }

    [Serializable]
    public class AbilitiesFile { public List<AbilityDefinition> abilities; }

    // Special abilities of animals, as in the real ones (Resources/Data/abilities.json): a species can
    // have none, one or several. What each does in a fight is in Combat and ColonyGroup.Stats:
    //  venom, stinging cells        their hits poison (HP lost each turn); stinging cells sting attackers back
    //  poisonous                    whatever attacks it is poisoned, except its predators
    //  electric shock               hits get through half the defense and stun (no actions next turn)
    //  sticky web, constriction     hits hold the target (no actions next turn)
    //  ink cloud, roll up           less damage taken; can't be swallowed whole
    //  spines                       attackers take damage back; can't be swallowed whole
    //  chemical spray               attackers lose HP and their actions next turn
    //  tail weapon                  counterattacks twice as hard
    //  pack hunting                 more damage with a friend next to the target
    //  ambush                       no counterattack before it has moved that turn
    //  regeneration                 heals twice as fast
    //  shed a limb                  survives one killing blow at 1 HP
    //  echolocation, electroreception, keen eyes   see a tile further (FogOfWar); the first two see
    //                               through camouflage, electroreception through burrows too
    //  camouflage, burrow, shell retreat           less damage taken (a shell: no swallowing whole)
    //  herd, school                 less damage taken with a friend next to it
    //  vigilance                    can't be ambushed
    //  charge                       more damage after moving that turn
    //  crushing bite                ignores rolling up and shells, swallows spiny and shelled prey
    //  trample                      hurts a second foreign group on the target tile
    //  sprint                       one more action a turn
    //  swarm, blood feeding         attack animals of any bigger size; blood feeding heals by its bites
    //  spreads disease              hits infect (HP lost each turn)
    //  dormancy, blubber            no / half HP lost when it has no food
    //  prolific breeder             reproduces every 2 turns
    // Some need a Function or Behavior first: a player's groups use them only once their species has
    // acquired it (unless the species can't acquire it at all); wild groups always have them.
    public static class Abilities
    {
        public const string Venom = "venom", StingingCells = "stinging_cells", Poisonous = "poisonous",
                            ElectricShock = "electric_shock", StickyWeb = "sticky_web", InkCloud = "ink_cloud",
                            ChemicalSpray = "chemical_spray", Spines = "spines", RollUp = "roll_up",
                            TailWeapon = "tail_weapon", PackHunting = "pack_hunting", Ambush = "ambush",
                            Constriction = "constriction", Regeneration = "regeneration", Autotomy = "autotomy",
                            Echolocation = "echolocation", Electroreception = "electroreception", KeenEyes = "keen_eyes",
                            Camouflage = "camouflage", Burrow = "burrow", ShellRetreat = "shell_retreat",
                            Herding = "herding", Schooling = "schooling", Vigilance = "vigilance", Charge = "charge",
                            CrushingBite = "crushing_bite", Trample = "trample", Sprint = "sprint", Swarm = "swarm",
                            BloodFeeding = "blood_feeding", Disease = "disease", Dormancy = "dormancy",
                            Blubber = "blubber", Prolific = "prolific";

        private static List<AbilityDefinition> all;
        private static readonly Dictionary<string, List<AbilityDefinition>> bySpecies = new();

        public static IReadOnlyList<AbilityDefinition> All
        {
            get
            {
                if (all != null) return all;
                var asset = Resources.Load<TextAsset>("Data/abilities");
                all = asset != null ? JsonUtility.FromJson<AbilitiesFile>(asset.text)?.abilities ?? new() : new();
                if (asset == null) Debug.LogWarning("[Abilities] Resources/Data/abilities.json not found.");
                return all;
            }
        }

        private static float Gene(SpeciesDefinition def, string id)
        {
            if (def.genes == null) return 0f;
            foreach (var g in def.genes) if (g.gene == id) return g.expression;
            return 0f;
        }

        public static AbilityDefinition Get(string id) => All.FirstOrDefault(a => a.id == id);

        // Every ability the species has (unlocked or not)
        public static IReadOnlyList<AbilityDefinition> Of(SpeciesDefinition def)
        {
            if (def == null) return Array.Empty<AbilityDefinition>();
            if (bySpecies.TryGetValue(def.id, out var list)) return list;
            list = All.Where(a => a.species.Contains(def.id) || a.groups.Contains(def.group ?? "")
                               || (def.tags != null && a.tags.Any(def.tags.Contains))
                               || (!string.IsNullOrEmpty(a.gene) && Gene(def, a.gene) >= a.minGene)).ToList();
            bySpecies[def.id] = list;
            return list;
        }

        // Whether the group can use the ability now
        public static bool Has(ColonyGroup g, string id)
        {
            if (g == null || g.Definition == null) return false;
            foreach (var a in Of(g.Definition))
                if (a.id == id) return g.Owner == null || Unlocked(g.Definition, a, g.Owner.Index);
            return false;
        }

        // Unlocked for the players' groups of the species: it needs nothing, its species has acquired
        // one of the items that unlock it, or it can't acquire any of them (then it's innate)
        // player: whose items count (an AI player's own; -1 the human's)
        public static bool Unlocked(SpeciesDefinition def, AbilityDefinition a, int player = -1)
        {
            if (!a.NeedsUnlock) return true;
            var progression = ProgressionManager.Instance;
            var traits = EvolutionManager.Instance != null ? EvolutionManager.Instance.TraitsOf(player, def.id) : null;
            if (progression == null || traits == null) return true;
            bool any = false;
            foreach (var id in a.unlockFunctions)
            {
                var node = progression.Morphology.Get(id);
                if (node == null || !EvolutionData.CanAcquire(def, node, true)) continue;
                any = true;
                if (traits.functions.Contains(id)) return true;
            }
            foreach (var id in a.unlockBehaviors)
            {
                var node = progression.Ethology.Get(id);
                if (node == null || !EvolutionData.CanAcquire(def, node, false)) continue;
                any = true;
                if (traits.behaviors.Contains(id)) return true;
            }
            return !any;
        }

        // Whether the species' players have to unlock it: it lists an item the species can acquire
        public static bool RequiresUnlock(SpeciesDefinition def, AbilityDefinition a)
        {
            if (!a.NeedsUnlock) return false;
            var progression = ProgressionManager.Instance;
            if (progression == null) return true;
            return a.unlockFunctions.Any(id => progression.Morphology.Get(id) is { } n && EvolutionData.CanAcquire(def, n, true))
                || a.unlockBehaviors.Any(id => progression.Ethology.Get(id) is { } n && EvolutionData.CanAcquire(def, n, false));
        }

        // What unlocks it, for the cards: "Function: Venom glands" / "Behavior: Silk traps", joined by "or"
        public static string UnlockText(AbilityDefinition a)
        {
            var progression = ProgressionManager.Instance;
            var parts = new List<string>();
            foreach (var id in a.unlockFunctions)
                parts.Add(Loc.F("Function: {0}", Loc.T(progression?.Morphology.Get(id)?.displayName ?? id)));
            foreach (var id in a.unlockBehaviors)
                parts.Add(Loc.F("Behavior: {0}", Loc.T(progression?.Ethology.Get(id)?.displayName ?? id)));
            return string.Join(" " + Loc.T("or") + " ", parts);
        }

        // The species' abilities for a card, one per line: name, what it does, and, for a player's
        // species, what it still needs (owned: judged for the player's groups)
        public static string Describe(SpeciesDefinition def, bool owned)
        {
            var list = Of(def);
            if (list.Count == 0) return "";
            var lines = new List<string>();
            foreach (var a in list)
            {
                string line = $"• {Loc.T(a.name)}: {Loc.T(a.description)}";
                if (RequiresUnlock(def, a) && !(owned && Unlocked(def, a)))
                    line += "\n   " + (owned ? Loc.F("Locked: needs {0}", UnlockText(a)) : Loc.F("Players need {0}", UnlockText(a)));
                lines.Add(line);
            }
            return Loc.T("Abilities") + "\n" + string.Join("\n", lines);
        }

        // What the abilities of others have done to the group: poisoned, held or stunned ("" if neither)
        // Tiles more it sees (FogOfWar.Vision)
        public static int VisionBonus(ColonyGroup g) =>
            (Has(g, Echolocation) || Has(g, Electroreception) || Has(g, KeenEyes)) ? 1 : 0;

        public static int ReproduceCooldown(ColonyGroup g, int normal) => Has(g, Prolific) ? normal - 1 : normal;

        public static string Status(ColonyGroup g)
        {
            var parts = new List<string>();
            if (g.PoisonTurns > 0)
                parts.Add(Loc.F(g.PoisonTurns == 1 ? "Poisoned: loses {0} HP next turn" : "Poisoned: loses {0} HP a turn for {1} turns",
                                Mathf.CeilToInt(g.PoisonPerTurn), g.PoisonTurns));
            if (g.HeldTurns > 0) parts.Add(Loc.T("Held or stunned: no actions next turn"));
            return string.Join("\n", parts);
        }
    }
}
