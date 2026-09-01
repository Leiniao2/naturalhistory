using System;
using System.Collections.Generic;

namespace NaturalHistory.Data
{
    // --- Realm ---

    [Serializable]
    public class RealmDefinition
    {
        public string id;
        public string displayName;
        public string type;           // "Land" | "Marine"
        public string thermalZone;    // "Polar" | "Temperate" | "Tropical" (marine only)
        public string description;
        public List<string> subrealms;
        public List<string> dominantTerrains;
        public int startingSlots;
        public string color;          // hex color string e.g. "#4A90D9"
    }

    [Serializable]
    public class RealmCollection
    {
        public List<RealmDefinition> realms;
    }

    // --- Age ---

    [Serializable]
    public class AgeEnvironment
    {
        public string globalTemp;
        public string seaLevel;
        public string oxygenLevel;
        public string landCoverage;
    }

    [Serializable]
    public class AgeDefinition
    {
        public string id;
        public string displayName;
        public float startMillionYearsAgo;
        public float endMillionYearsAgo;
        public string description;
        public List<string> keyEvents;
        public AgeEnvironment environmentalConditions;
        public List<string> transitionEventKeys;
        public int slotExpansionAmount;
        public List<string> availableTerrains;
    }

    [Serializable]
    public class AgeCollection
    {
        public List<AgeDefinition> ages;
    }

    // --- Gene ---

    [Serializable]
    public class GeneDefinition
    {
        public string id;
        public string displayName;
        public string category;       // matches GeneCategory enum
        public float defaultExpression;
        public string description;
        public string unlockAge;      // GeologicalAge enum name
    }

    [Serializable]
    public class GeneCollection
    {
        public List<GeneDefinition> genes;
    }
}
