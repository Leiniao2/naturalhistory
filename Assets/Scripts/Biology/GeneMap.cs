using System;
using System.Collections.Generic;
using UnityEngine;

namespace NaturalHistory.Biology
{
    public enum GeneCategory { Locomotion, Diet, Reproduction, Defense, Perception, Thermoregulation }

    [Serializable]
    public class Gene
    {
        public string id;
        public string displayName;
        public GeneCategory category;
        [Range(0f, 1f)] public float expressionLevel;
        [TextArea] public string description;
    }

    [Serializable]
    public class Mutation
    {
        public string geneId;
        public float delta;
        public string sourceEvent;
    }

    // Data model — not a MonoBehaviour so it can be serialized standalone
    [Serializable]
    public class GeneMap
    {
        private readonly Dictionary<string, Gene> genes = new();

        public IEnumerable<Gene> AllGenes => genes.Values;

        public void AddGene(Gene gene)
        {
            genes[gene.id] = gene;
        }

        public Gene GetGene(string id) => genes.TryGetValue(id, out var g) ? g : null;

        public void ApplyMutation(Mutation mutation)
        {
            if (!genes.TryGetValue(mutation.geneId, out var gene)) return;
            gene.expressionLevel = Mathf.Clamp01(gene.expressionLevel + mutation.delta);
            Debug.Log($"[GeneMap] Mutation applied: {gene.displayName} {mutation.delta:+0.00;-0.00} → {gene.expressionLevel:0.00}");
        }

        public GeneMap Clone()
        {
            var clone = new GeneMap();
            foreach (var g in genes.Values)
            {
                clone.AddGene(new Gene
                {
                    id = g.id,
                    displayName = g.displayName,
                    category = g.category,
                    expressionLevel = g.expressionLevel,
                    description = g.description
                });
            }
            return clone;
        }
    }
}
