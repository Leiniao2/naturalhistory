using System;
using System.Collections.Generic;
using NaturalHistory.Core;
using NaturalHistory.World;
using UnityEngine;

namespace NaturalHistory.Biology
{
    public enum RealmType { Land, Marine }

    [Serializable]
    public class BioRealm : ITurnListener
    {
        public string Id;
        public string DisplayName;
        public RealmType Type;
        public Color RealmColor = Color.white;

        // Species slots — starts at 5, expands with age progression
        public int SpeciesSlotCapacity { get; private set; } = 5;

        private readonly List<Species> species = new();
        public IReadOnlyList<Species> Species => species;

        // Controlled territory
        private readonly HashSet<HexCell> territory = new();
        public IReadOnlyCollection<HexCell> Territory => territory;

        public bool IsPlayerControlled;

        public bool CanAddSpecies => species.Count < SpeciesSlotCapacity;

        public bool TryAddSpecies(Species s)
        {
            if (!CanAddSpecies) return false;
            species.Add(s);
            s.AssignToRealm(this);
            s.OnExtinction += HandleExtinction;
            TurnManager.Instance?.Register(s);
            return true;
        }

        public void RemoveSpecies(Species s)
        {
            species.Remove(s);
            s.OnExtinction -= HandleExtinction;
            TurnManager.Instance?.Unregister(s);
        }

        public void ClaimCell(HexCell cell)
        {
            territory.Add(cell);
            cell.SetControllingRealm(this);
        }

        public void ReleaseCell(HexCell cell)
        {
            territory.Remove(cell);
        }

        public void ExpandSlotCapacity(int amount)
        {
            SpeciesSlotCapacity += amount;
            Debug.Log($"[BioRealm] {DisplayName} slot capacity → {SpeciesSlotCapacity}");
        }

        public void OnTurnBegin(int turn) { }

        public void OnTurnEnd(int turn)
        {
            // Realm-level bookkeeping each turn
        }

        private void HandleExtinction(Species extinct)
        {
            RemoveSpecies(extinct);
            Debug.Log($"[BioRealm] {DisplayName} lost species: {extinct.CommonName}");
        }

        public override string ToString() => $"{DisplayName} [{Type}] ({species.Count}/{SpeciesSlotCapacity} species)";
    }
}
