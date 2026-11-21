using System.Collections.Generic;
using NaturalHistory.Core;
using NaturalHistory.Data;
using NaturalHistory.Evolution;
using NaturalHistory.Progression;
using UnityEngine;

namespace NaturalHistory.World
{
    // What the Functions and Behaviors items a player's species has acquired do for its groups
    // (tools/trees/bonuses.py chooses each from what the item is):
    //  - effects (TreeNodeDefinition.effects, most items): healing, resisting poison, hunger and
    //    disasters, taking less damage at home or among friends, cheaper or quicker breeding, cheaper
    //    evolution, eating without ending the turn, EP income... summed over the items to the caps in
    //    Effects, and applied in ColonyGroup.Stats, Combat, DisasterEffects, FogOfWar,
    //    EvolutionManager and ProgressionManager
    //  - flat stats (TreeNodeDefinition.bonus, a few items: +1 attack, +1 defence, +2 HP or +1 action
    //    a turn). Like the base stats they grow with the era factor of the species
    //    (CombatStats.Era), so an item is worth the same share of a later species' strength.
    // Only players' groups get them (the items are a player's, EvolutionManager.TraitsOf); wild
    // groups fight with their base stats. Version changes whenever items may have changed, and
    // ColonyGroup.Stats works its bonus out again then.
    public static class TraitBonuses
    {
        public static int Version { get; private set; }

        private static ProgressionManager hookedProgression;
        private static EvolutionManager hookedEvolution;
        private static readonly Dictionary<(int player, string species), (int version, CombatStats bonus)> cache = new();
        private static readonly Dictionary<(int player, string species), (int version, TraitEffects effects)> effectCache = new();
        private static readonly TraitEffects None = new();

        // Caps on the summed effects
        private const float MaxHeal = 0.3f, MaxFieldHeal = 0.15f, MaxResist = 0.8f, MaxGuard = 0.5f,
                            MaxCounterBoost = 1f, MaxKillHeal = 0.5f, MaxKillEp = 1f, MaxBreedDiscount = 0.75f,
                            MaxEvolveDiscount = 0.5f;
        private const int MaxBreedCooldown = 2, MaxVision = 2;

        // What `owner`'s items of `def` do for its groups (all off for wild groups)
        public static TraitEffects Effects(SpeciesDefinition def, Players.Player owner) =>
            def == null || owner == null ? None : Effects(def, owner.Index);

        public static TraitEffects Effects(ColonyGroup g) => g == null ? None : Effects(g.Definition, g.Owner);

        // player: the player's index (-1: the human's)
        public static TraitEffects Effects(SpeciesDefinition def, int player)
        {
            Hook();
            if (def == null) return None;
            var key = (player, def.id);
            if (effectCache.TryGetValue(key, out var known) && known.version == Version) return known.effects;

            var sum = new TraitEffects();
            var progression = ProgressionManager.Instance;
            var traits = EvolutionManager.Instance != null ? EvolutionManager.Instance.TraitsOf(player, def.id) : null;
            if (progression != null && traits != null)
            {
                foreach (var id in traits.functions) Add(sum, progression.Morphology.Get(id)?.effects);
                foreach (var id in traits.behaviors) Add(sum, progression.Ethology.Get(id)?.effects);
            }
            sum.heal           = Mathf.Min(sum.heal, MaxHeal);
            sum.fieldHeal      = Mathf.Min(sum.fieldHeal, MaxFieldHeal);
            sum.poisonResist   = Mathf.Min(sum.poisonResist, MaxResist);
            sum.starveResist   = Mathf.Min(sum.starveResist, MaxResist);
            sum.disasterResist = Mathf.Min(sum.disasterResist, MaxResist);
            sum.guard          = Mathf.Min(sum.guard, MaxGuard);
            sum.homeGuard      = Mathf.Min(sum.homeGuard, MaxGuard);
            sum.friendGuard    = Mathf.Min(sum.friendGuard, MaxGuard);
            sum.counterResist  = Mathf.Min(sum.counterResist, MaxGuard);
            sum.counterBoost   = Mathf.Min(sum.counterBoost, MaxCounterBoost);
            sum.killHeal       = Mathf.Min(sum.killHeal, MaxKillHeal);
            sum.killEp         = Mathf.Min(sum.killEp, MaxKillEp);
            sum.breedDiscount  = Mathf.Min(sum.breedDiscount, MaxBreedDiscount);
            sum.evolveDiscount = Mathf.Min(sum.evolveDiscount, MaxEvolveDiscount);
            sum.breedCooldown  = Mathf.Min(sum.breedCooldown, MaxBreedCooldown);
            sum.vision         = Mathf.Min(sum.vision, MaxVision);
            effectCache[key] = (Version, sum);
            return sum;
        }

        // An EP price for `player`'s `def` after its evolution discount
        public static int Discounted(int cost, SpeciesDefinition def, int player = -1)
        {
            if (cost <= 0 || def == null) return cost;
            float off = Effects(def, player).evolveDiscount;
            return off <= 0f ? cost : Mathf.Max(1, Mathf.RoundToInt(cost * (1f - off)));
        }

        // EP a turn the player's species give (TraitEffects.income), grown with the periods like the prices
        public static int Income(int player, IEnumerable<string> species)
        {
            int sum = 0;
            foreach (var id in new HashSet<string>(species))
                sum += Effects(GameDataLoader.GetSpecies(id), player).income;
            return sum <= 0 ? 0 : Mathf.RoundToInt(sum * EpCosts.Factor);
        }

        private static void Add(TraitEffects sum, TraitEffects e)
        {
            if (e == null) return;
            sum.heal += e.heal; sum.fieldHeal += e.fieldHeal;
            sum.poisonResist += e.poisonResist; sum.starveResist += e.starveResist; sum.disasterResist += e.disasterResist;
            sum.guard += e.guard; sum.homeGuard += e.homeGuard; sum.friendGuard += e.friendGuard;
            sum.counterResist += e.counterResist; sum.counterBoost += e.counterBoost;
            sum.killHeal += e.killHeal; sum.killEp += e.killEp;
            sum.breedDiscount += e.breedDiscount; sum.evolveDiscount += e.evolveDiscount;
            sum.breedCooldown += e.breedCooldown; sum.vision += e.vision; sum.income += e.income;
            sum.freeHunt |= e.freeHunt; sum.freeBreed |= e.freeBreed;
            sum.holdImmune |= e.holdImmune; sum.swallowImmune |= e.swallowImmune; sum.ambushImmune |= e.ambushImmune;
        }

        // One item's effects for the cards, one phrase each ("Heals 5% more when resting")
        public static List<string> EffectLines(TraitEffects e)
        {
            var lines = new List<string>();
            if (e == null) return lines;
            static string P(float f) => Mathf.RoundToInt(f * 100f).ToString();
            if (e.heal > 0f)           lines.Add(Loc.F("Heals {0}% more of its HP when resting", P(e.heal)));
            if (e.fieldHeal > 0f)      lines.Add(Loc.F("Heals {0}% of its HP each turn, even after acting", P(e.fieldHeal)));
            if (e.poisonResist > 0f)   lines.Add(Loc.F("{0}% less harm from poison and infection", P(e.poisonResist)));
            if (e.starveResist > 0f)   lines.Add(Loc.F("{0}% less HP lost when it finds no food", P(e.starveResist)));
            if (e.disasterResist > 0f) lines.Add(Loc.F("{0}% less harm from disasters", P(e.disasterResist)));
            if (e.guard > 0f)          lines.Add(Loc.F("{0}% less damage taken", P(e.guard)));
            if (e.homeGuard > 0f)      lines.Add(Loc.F("{0}% less damage taken in your territory", P(e.homeGuard)));
            if (e.friendGuard > 0f)    lines.Add(Loc.F("{0}% less damage taken with a friendly group next to it", P(e.friendGuard)));
            if (e.counterResist > 0f)  lines.Add(Loc.F("{0}% less damage back when it attacks", P(e.counterResist)));
            if (e.counterBoost > 0f)   lines.Add(Loc.F("Counterattacks {0}% harder", P(e.counterBoost)));
            if (e.killHeal > 0f)       lines.Add(Loc.F("Heals {0}% of its HP when it wipes out a foe", P(e.killHeal)));
            if (e.killEp > 0f)         lines.Add(Loc.F("{0}% more EP for wiping out a foe", P(e.killEp)));
            if (e.breedDiscount > 0f)  lines.Add(Loc.F("Reproducing costs {0}% less EP", P(e.breedDiscount)));
            if (e.evolveDiscount > 0f) lines.Add(Loc.F("This species' items and evolving cost {0}% less EP", P(e.evolveDiscount)));
            if (e.breedCooldown > 0)   lines.Add(Loc.F(e.breedCooldown == 1 ? "Reproduces {0} turn sooner" : "Reproduces {0} turns sooner", e.breedCooldown));
            if (e.vision > 0)          lines.Add(Loc.F(e.vision == 1 ? "Sees {0} tile further" : "Sees {0} tiles further", e.vision));
            if (e.income > 0)          lines.Add(Loc.F("+{0} EP a turn while you have the species", Mathf.RoundToInt(e.income * EpCosts.Factor)));
            if (e.freeHunt)            lines.Add(Loc.T("Eating prey doesn't end its turn"));
            if (e.freeBreed)           lines.Add(Loc.T("Reproducing takes no action"));
            if (e.holdImmune)          lines.Add(Loc.T("Can't be held or stunned"));
            if (e.swallowImmune)       lines.Add(Loc.T("Can't be swallowed whole"));
            if (e.ambushImmune)        lines.Add(Loc.T("Can't be ambushed"));
            return lines;
        }

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
