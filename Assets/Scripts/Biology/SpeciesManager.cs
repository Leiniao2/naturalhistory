using System.Collections.Generic;
using UnityEngine;

namespace NaturalHistory.Biology
{
    public class SpeciesManager : MonoBehaviour
    {
        public static SpeciesManager Instance { get; private set; }

        private readonly List<Species> allSpecies = new();
        private readonly List<BioRealm> allRealms = new();

        public IReadOnlyList<Species> AllSpecies => allSpecies;
        public IReadOnlyList<BioRealm> AllRealms => allRealms;

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
        }

        public void RegisterRealm(BioRealm realm)
        {
            if (!allRealms.Contains(realm))
                allRealms.Add(realm);
        }

        public void RegisterSpecies(Species species)
        {
            if (!allSpecies.Contains(species))
                allSpecies.Add(species);
        }

        public void UnregisterSpecies(Species species)
        {
            allSpecies.Remove(species);
        }

        // Triggers a speciation event — spawns a child species with a random mutation
        public Species TriggerSpeciation(Species parent, string childName)
        {
            var child = parent.Speciate(childName);
            var mutation = new Mutation
            {
                geneId = PickRandomGeneId(parent),
                delta = Random.Range(-0.15f, 0.25f),
                sourceEvent = "speciation"
            };
            child.Genes.ApplyMutation(mutation);
            RegisterSpecies(child);
            Debug.Log($"[SpeciesManager] Speciation: {parent.CommonName} → {child.CommonName}");
            return child;
        }

        private string PickRandomGeneId(Species species)
        {
            var genes = new List<Biology.Gene>(species.Genes.AllGenes);
            if (genes.Count == 0) return string.Empty;
            return genes[Random.Range(0, genes.Count)].id;
        }
    }
}
