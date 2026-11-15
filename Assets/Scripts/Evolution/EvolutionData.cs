using System;
using System.Collections.Generic;
using System.Linq;
using NaturalHistory.Data;
using UnityEngine;

namespace NaturalHistory.Evolution
{
    // --- trait_rules.json: which tree items each species can acquire ---

    [Serializable]
    public class TraitTagRule
    {
        public string group;          // species.json group (in "groups")
        public string item;           // tree node id (in "functions" / "behaviors")
        public List<string> tags;
    }

    [Serializable]
    public class TraitRulesFile
    {
        public List<TraitTagRule> groups;
        public List<TraitTagRule> functions;
        public List<TraitTagRule> behaviors;
    }

    // --- evolution.json: which species evolve into which ---

    [Serializable]
    public class EvolutionLink
    {
        public string from;                 // species id
        public string to;
        public List<string> functions;      // required items of the origin species' Function (morphology) tree
        public List<string> behaviors;      // … and Behavior (ethology) tree
        public List<string> grantFunctions; // acquired automatically on evolving
        public List<string> grantBehaviors;
        public string description;

        public string Key => $"{from}>{to}";
    }

    [Serializable]
    public class EvolutionFile
    {
        public List<EvolutionLink> links;
    }

    // Loads trait_rules.json and evolution.json (Resources/Data) on first use.
    //
    // A species' tags come from its group (e.g. "Theropod dinosaur" → Animal, Vertebrate, Amniote,
    // Reptile, Archosaur, Dinosaur, Theropod). A Function or Behavior item can be acquired by a
    // species that has any of the item's tags; items not listed need "Animal".
    public static class EvolutionData
    {
        private static Dictionary<string, HashSet<string>> groupTags;
        private static Dictionary<string, HashSet<string>> functionTags;
        private static Dictionary<string, HashSet<string>> behaviorTags;
        private static List<EvolutionLink> links;
        private static readonly HashSet<string> Animal = new() { "Animal" };

        public static IReadOnlyList<EvolutionLink> Links { get { Load(); return links; } }

        public static IEnumerable<EvolutionLink> From(string speciesId) => Links.Where(l => l.from == speciesId);
        public static IEnumerable<EvolutionLink> To(string speciesId)   => Links.Where(l => l.to == speciesId);

        public static IReadOnlyCollection<string> TagsOf(SpeciesDefinition species)
        {
            Load();
            return species != null && species.group != null && groupTags.TryGetValue(species.group, out var tags) ? tags : Animal;
        }

        // Whether `species` can ever acquire `node` (isFunction: Function/morphology tree, else Behavior/ethology).
        public static bool CanAcquire(SpeciesDefinition species, TreeNodeDefinition node, bool isFunction)
        {
            if (species == null || node == null) return true;
            Load();
            var table = isFunction ? functionTags : behaviorTags;
            var needed = table.TryGetValue(node.id, out var t) ? t : Animal;
            var tags = TagsOf(species);
            return needed.Any(tags.Contains);
        }

        private static void Load()
        {
            if (links != null) return;
            groupTags    = new Dictionary<string, HashSet<string>>();
            functionTags = new Dictionary<string, HashSet<string>>();
            behaviorTags = new Dictionary<string, HashSet<string>>();
            links        = new List<EvolutionLink>();

            var rules = Read<TraitRulesFile>("Data/trait_rules");
            if (rules != null)
            {
                Fill(groupTags,    rules.groups,    r => r.group);
                Fill(functionTags, rules.functions, r => r.item);
                Fill(behaviorTags, rules.behaviors, r => r.item);
            }

            var evolution = Read<EvolutionFile>("Data/evolution");
            if (evolution?.links != null)
                foreach (var l in evolution.links)
                {
                    if (string.IsNullOrEmpty(l.from) || string.IsNullOrEmpty(l.to)) continue;
                    l.functions      ??= new List<string>();
                    l.behaviors      ??= new List<string>();
                    l.grantFunctions ??= new List<string>();
                    l.grantBehaviors ??= new List<string>();
                    links.Add(l);
                }
            Debug.Log($"[EvolutionData] {links.Count} evolution links, {groupTags.Count} species groups with trait tags");
        }

        private static void Fill(Dictionary<string, HashSet<string>> into, List<TraitTagRule> rules, Func<TraitTagRule, string> key)
        {
            if (rules == null) return;
            foreach (var r in rules)
                if (!string.IsNullOrEmpty(key(r))) into[key(r)] = new HashSet<string>(r.tags ?? new List<string>());
        }

        private static T Read<T>(string path) where T : class
        {
            var asset = Resources.Load<TextAsset>(path);
            if (asset == null) { Debug.LogError($"[EvolutionData] Missing Resources/{path}.json"); return null; }
            try { return JsonUtility.FromJson<T>(asset.text); }
            catch (Exception e) { Debug.LogError($"[EvolutionData] Could not parse {path}.json: {e.Message}"); return null; }
        }
    }
}
