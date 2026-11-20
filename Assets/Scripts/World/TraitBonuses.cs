using System.Collections.Generic;
using NaturalHistory.Data;
using NaturalHistory.Evolution;
using NaturalHistory.Progression;
using UnityEngine;

namespace NaturalHistory.World
{
    // What the Functions and Behaviors items a player's species has acquired add to its groups'
    // combat stats (TreeNodeDefinition.bonus, from tools/trees/bonuses.py: +1 attack, +1 defence,
    // +2 HP or +1 action a turn each). Like the base stats they grow with the era factor of the
    // species (CombatStats.Era), so an item is worth the same share of a later species' strength.
    // Only players' groups get them (the items are a player's, EvolutionManager.TraitsOf); wild
    // groups fight with their base stats. Version changes whenever items may have changed, and
    // ColonyGroup.Stats works its bonus out again then.
    public static class TraitBonuses
    {
        public static int Version { get; private set; }

        private static ProgressionManager hookedProgression;
        private static EvolutionManager hookedEvolution;
        private static readonly Dictionary<(int player, string species), (int version, CombatStats bonus)> cache = new();

        // The bonus `owner`'s groups of `def` get, era factor included (all zero for wild groups)
        public static CombatStats For(SpeciesDefinition def, Players.Player owner)
        {
            Hook();
            if (def == null || owner == null) return default;
            var key = (owner.Index, def.id);
            if (cache.TryGetValue(key, out var known) && known.version == Version) return known.bonus;

            var sum = new TraitBonus();
            var progression = ProgressionManager.Instance;
            var traits = EvolutionManager.Instance != null ? EvolutionManager.Instance.TraitsOf(owner.Index, def.id) : null;
            if (progression != null && traits != null)
            {
                foreach (var id in traits.functions) Add(sum, progression.Morphology.Get(id));
                foreach (var id in traits.behaviors) Add(sum, progression.Ethology.Get(id));
            }
            float era = CombatStats.Era(def);
            var bonus = new CombatStats
            {
                attack  = Mathf.RoundToInt(sum.attack  * era),
                defense = Mathf.RoundToInt(sum.defense * era),
                hp      = Mathf.RoundToInt(sum.hp      * era),
                moves   = sum.moves, // actions a turn don't grow with the era
            };
            cache[key] = (Version, bonus);
            return bonus;
        }

        // The bonus one item gives a species, era factor included (for the trees' cards)
        public static TraitBonus Scaled(TreeNodeDefinition node, SpeciesDefinition def)
        {
            if (node?.bonus == null || !node.bonus.Any) return null;
            float era = CombatStats.Era(def);
            return new TraitBonus
            {
                attack  = Mathf.RoundToInt(node.bonus.attack  * era),
                defense = Mathf.RoundToInt(node.bonus.defense * era),
                hp      = Mathf.RoundToInt(node.bonus.hp      * era),
                moves   = node.bonus.moves,
            };
        }

        private static void Add(TraitBonus sum, TreeNodeDefinition node)
        {
            var b = node?.bonus;
            if (b == null) return;
            sum.attack += b.attack; sum.defense += b.defense; sum.hp += b.hp; sum.moves += b.moves;
        }

        // Items change when one is acquired, a copy evolves (granted items) or a game is loaded
        private static void Hook()
        {
            var progression = ProgressionManager.Instance;
            if (progression != hookedProgression)
            {
                if (progression != null) { progression.NodeUnlocked += (_, _) => Version++; progression.Changed += () => Version++; }
                hookedProgression = progression;
                Version++;
            }
            var evolution = EvolutionManager.Instance;
            if (evolution != hookedEvolution)
            {
                if (evolution != null) evolution.Changed += () => Version++;
                hookedEvolution = evolution;
                Version++;
            }
        }
    }
}
