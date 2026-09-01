using System;
using System.Collections.Generic;
using NaturalHistory.Core;
using NaturalHistory.World;
using UnityEngine;

namespace NaturalHistory.Biology
{
    public enum SpeciesKingdom { Animalia, Plantae, Fungi }
    public enum SpeciesStatus { Thriving, Stable, Threatened, Extinct }

    [Serializable]
    public class Species : ITurnListener
    {
        public string Id { get; } = Guid.NewGuid().ToString();
        public string CommonName;
        public string ScientificName;
        public SpeciesKingdom Kingdom;
        public SpeciesStatus Status { get; private set; } = SpeciesStatus.Stable;

        public GeneMap Genes { get; } = new();

        // Current population across all inhabited cells
        public int Population { get; private set; }

        // Cells this species inhabits
        private readonly HashSet<HexCell> habitat = new();
        public IReadOnlyCollection<HexCell> Habitat => habitat;

        // Owning realm
        public BioRealm Realm { get; private set; }

        public event Action<Species> OnExtinction;

        public void AssignToRealm(BioRealm realm)
        {
            Realm = realm;
        }

        public void Colonize(HexCell cell, int initialPop = 100)
        {
            if (!cell.Terrain.IsHabitable) return;
            habitat.Add(cell);
            cell.AddInhabitant(this);
            Population += initialPop;
        }

        public void Abandon(HexCell cell)
        {
            habitat.Remove(cell);
            cell.RemoveInhabitant(this);
        }

        public void OnTurnBegin(int turn) { }

        public void OnTurnEnd(int turn)
        {
            Reproduce();
            UpdateStatus();
        }

        private void Reproduce()
        {
            var repro = Genes.GetGene("reproduction_rate");
            float rate = repro != null ? repro.expressionLevel * 0.1f : 0.02f;
            Population = Mathf.RoundToInt(Population * (1f + rate));
        }

        private void UpdateStatus()
        {
            Status = Population switch
            {
                0 => SpeciesStatus.Extinct,
                < 50 => SpeciesStatus.Threatened,
                < 500 => SpeciesStatus.Stable,
                _ => SpeciesStatus.Thriving
            };

            if (Status == SpeciesStatus.Extinct)
            {
                Debug.Log($"[Species] {CommonName} has gone extinct.");
                OnExtinction?.Invoke(this);
            }
        }

        public Species Speciate(string newName)
        {
            var child = new Species
            {
                CommonName = newName,
                Kingdom = Kingdom,
                Population = Population / 2
            };
            var childGenes = Genes.Clone();
            // Caller applies mutations before registering
            foreach (var g in childGenes.AllGenes)
                child.Genes.AddGene(g);
            Population /= 2;
            return child;
        }

        public override string ToString() => $"{CommonName} ({Status}, pop:{Population})";
    }
}
