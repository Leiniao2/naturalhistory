using System.Collections.Generic;
using System.Linq;
using NaturalHistory.Data;
using NaturalHistory.Evolution;
using UnityEngine;

namespace NaturalHistory.World
{
    // A species' combat numbers, from its diet, genes (species.json "genes", expression 0..1), how it
    // moves on the map and its size; species.json "attack", "defense", "hp", "moves" override them.
    //  - attack 1..10 before the era factor, physical only (venom will be its own mechanic): what it
    //    eats (hunters hit hardest) plus carnivory, electric sense and a little for big jaws
    //  - defense 1..10 before the era factor: armour, group defence, camouflage, burrowing, the hide
    //    and bones of big animals; sessile colonies and herbivores a little more
    //  - hp 3..15 before the era factor: mostly the same for all, more for regenerators and a little
    //    more for big animals
    //  - era factor (Era): attack, defense and hp grow by EraGrowth (20%) for each period after the
    //    Ediacaran in which the species first appears, so later species outclass earlier ones and
    //    evolving pays (about ×9 by the Quaternary); the species.json overrides are values before
    //    it too (same ranges), so a hand-tuned species still grows with its period
    //  - moves 1..4: actions per turn (a tile moved, an attack, reproducing): sessile and drifting
    //    life 1, walkers and swimmers 2, soaring fliers 3, one more for fast ones
    //  - balance (Balanced): within a period the strongest and weakest are drawn toward the
    //    period's median (BalanceSpread), and an evolved species is always at least LineageStep
    //    (10%) stronger than every species it evolves from (evolution.json), so evolving never
    //    makes a player's animal weaker; attack, defense and hp are scaled together for both
    // Size itself counts in every fight (Combat): damage grows with the attacker's size over the
    // defender's, and animals more than ten times apart in size can't fight at all.
    public struct CombatStats
    {
        public int attack, defense, hp, moves;

        private const float EraGrowth = 1.2f;

        private const float LineageStep   = 1.1f; // an evolved species' strength over its ancestor's, at least
        private const float BalanceSpread = 0.5f; // exponent on the strength / period median: 0.5 turns 16× apart into 4×

        private static readonly Dictionary<string, CombatStats> cache = new();
        private static readonly Dictionary<string, CombatStats> rawCache = new();
        private static readonly Dictionary<string, float> balancedPower = new();
        private static Dictionary<string, float> periodMedian;

        // One number for how strong a species is: its HP times its mean of attack and defense
        public static float Power(CombatStats s) => s.hp * (s.attack + s.defense) * 0.5f;

        // The species' stats, balanced (see the header): its own numbers scaled by one factor so its
        // strength is the balanced one
        public static CombatStats Of(SpeciesDefinition def)
        {
            if (def == null) return new CombatStats { attack = 1, defense = 1, hp = 5, moves = 1 };
            if (cache.TryGetValue(def.id, out var known)) return known;
            var raw = Raw(def);
            float k = Mathf.Sqrt(BalancedPower(def, new HashSet<string>()) / Mathf.Max(0.01f, Power(raw)));
            var stats = new CombatStats
            {
                attack  = Mathf.Max(1, Mathf.RoundToInt(raw.attack  * k)),
                defense = Mathf.Max(1, Mathf.RoundToInt(raw.defense * k)),
                hp      = Mathf.Max(1, Mathf.RoundToInt(raw.hp      * k)),
                moves   = raw.moves,
            };
            // small numbers round off the margin: an HP more at a time until it beats every ancestor
            inProgress.Add(def.id);
            float ancestors = 0f;
            foreach (var link in EvolutionData.To(def.id))
            {
                var parent = GameDataLoader.GetSpecies(link.from);
                if (parent != null && !inProgress.Contains(parent.id)) ancestors = Mathf.Max(ancestors, Power(Of(parent)));
            }
            inProgress.Remove(def.id);
            while (Power(stats) <= ancestors) stats.hp++;
            cache[def.id] = stats;
            return stats;
        }
        private static readonly HashSet<string> inProgress = new();

        // Its strength drawn toward its period's median, then raised over each ancestor's
        private static float BalancedPower(SpeciesDefinition def, HashSet<string> visiting)
        {
            if (balancedPower.TryGetValue(def.id, out var known)) return known;
            float own = Power(Raw(def));
            float median = MedianOf(def.firstAge);
            float power = median > 0f ? median * Mathf.Pow(own / median, BalanceSpread) : own;
            visiting.Add(def.id);
            foreach (var link in EvolutionData.To(def.id))
            {
                var parent = GameDataLoader.GetSpecies(link.from);
                if (parent != null && !visiting.Contains(parent.id))
                    power = Mathf.Max(power, BalancedPower(parent, visiting) * LineageStep);
            }
            visiting.Remove(def.id);
            balancedPower[def.id] = power;
            return power;
        }

        private static float MedianOf(string age)
        {
            if (periodMedian == null)
            {
                if (GameDataLoader.Species == null || GameDataLoader.Species.Count == 0) return 0f; // not loaded yet: no balancing
                periodMedian = new Dictionary<string, float>();
                foreach (var period in GameDataLoader.Species.GroupBy(d => d.firstAge ?? ""))
                {
                    var powers = period.Select(d => Power(Raw(d))).OrderBy(p => p).ToList();
                    int n = powers.Count;
                    periodMedian[period.Key] = n % 2 == 1 ? powers[n / 2] : 0.5f * (powers[n / 2 - 1] + powers[n / 2]);
                }
            }
            return periodMedian.TryGetValue(age ?? "", out var m) ? m : 0f;
        }

        // EraGrowth to the power of the species' first period (Ediacaran = 0)
        public static float Era(SpeciesDefinition def) =>
            def != null && System.Enum.TryParse(def.firstAge, true, out Core.GeologicalAge age) ? Mathf.Pow(EraGrowth, (int)age) : 1f;

        // Its own numbers, before balancing: from diet, genes, size and period (or species.json)
        private static CombatStats Raw(SpeciesDefinition def)
        {
            if (rawCache.TryGetValue(def.id, out var known)) return known;

            float Gene(string id)
            {
                if (def.genes == null) return 0f;
                foreach (var g in def.genes) if (g.gene == id) return g.expression;
                return 0f;
            }

            float diet = def.diet switch
            {
                "Carnivore" => 2.5f,
                "Omnivore"  => 1.5f,
                "Scavenger" => 1.5f,
                "Parasite"  => 1f,
                "Herbivore" => 1f,
                _           => 0f, // filter feeders, detritivores, photosynthesisers
            };
            // physical only: venom and toxins will be a mechanic of their own, not attack
            float bulk    = Mathf.Log10(Mathf.Max(def.sizeCm, 0.001f) / 10f); // 0 at 10 cm, 1 at 1 m, 2 at 10 m
            float attack  = 1f + diet + 2.5f * Gene("carnivory") + Gene("electroreception") + Mathf.Clamp(0.5f * bulk, 0f, 1.5f);
            bool sessile  = def.mapStyle == "Fixed";
            float defense = 1.5f + 3.5f * Gene("armor_thickness") + 1.5f * Gene("group_defense") + Gene("camouflage")
                          + 0.5f * Gene("burrowing") + (sessile ? 1f : 0f) + (def.diet == "Herbivore" ? 1f : 0f) // grazers: hides, horns, herds
                          + Mathf.Clamp(0.7f * bulk, 0f, 2f); // thick hide and heavy bones of big animals
            float hp      = 4f + 3f * Gene("regeneration") + 1.5f * Mathf.Log10(Mathf.Max(def.sizeCm, 0.001f) + 1f);
            int moves     = def.mapStyle switch
            {
                "Fixed" or "Drift" or "Float" => 1,
                "Soar"                        => 3,
                null or ""                    => 1,
                _                             => 2, // Ground, Swim, Swarm
            };
            float speed = Mathf.Max(Gene("land_speed"), Gene("swimming_speed"), Gene("flight_capability"));
            if (moves > 1 && speed >= 0.7f) moves++;

            float era = Era(def);
            int Scaled(float v, int lo, int hi) => Mathf.Max(1, Mathf.RoundToInt(Mathf.Clamp(Mathf.Round(v), lo, hi) * era));
            var stats = new CombatStats
            {
                attack  = Scaled(def.attack  > 0 ? def.attack  : attack, 1, 10),
                defense = Scaled(def.defense > 0 ? def.defense : defense, 1, 10),
                hp      = Scaled(def.hp      > 0 ? def.hp      : hp, 3, 15),
                moves   = def.moves   > 0 ? def.moves   : Mathf.Clamp(moves, 1, 4),
            };
            rawCache[def.id] = stats;
            return stats;
        }
    }
}
