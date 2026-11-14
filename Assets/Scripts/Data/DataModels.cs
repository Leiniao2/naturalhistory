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
        public string id;             // GeologicalAge enum name
        public string displayName;
        public string era;            // Paleozoic | Mesozoic | Cenozoic
        public float startMillionYearsAgo;
        public float endMillionYearsAgo;
        public int turns;             // game turns spent in this period
        public string description;
        public List<string> keyEvents;
        public string vegetation;
        public AgeEnvironment environmentalConditions;
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

    // --- Progression trees (Morphology = tech tree, Ethology = civics tree) ---

    [Serializable]
    public class TreeNodeDefinition
    {
        public string id;
        public string displayName;
        public int tier;                  // column in the tree view (left → right)
        public int row;                   // vertical slot within the column
        public int cost;                  // Evolution Points to unlock; 0 = unlocked from the start
        public string age;                // earliest GeologicalAge it can be unlocked in
        public List<string> prerequisites;
        public List<string> unlocksGenes; // gene ids from genes.json
        public string description;
    }

    [Serializable]
    public class TreeNodeCollection
    {
        public List<TreeNodeDefinition> nodes;
    }

    // --- Climate history (climate_history.json) ---

    [Serializable]
    public class ClimateKeyframe
    {
        public float ma;              // millions of years ago
        public float temperatureC;    // global mean surface temperature
        public float co2ppm;
        public float o2Percent;
        public float seaLevelM;       // relative to today
        public float humidityOffset;  // aridity nudge, percentage points of relative humidity
        public string note;
    }

    [Serializable]
    public class ClimateHistoryCollection
    {
        public List<ClimateKeyframe> keyframes;
        public List<string> sources;
    }

    // --- Species templates (species.json) ---

    [Serializable]
    public class GeneValue
    {
        public string gene;           // gene id from genes.json
        public float expression;      // 0..1
    }

    [Serializable]
    public class SpeciesDefinition
    {
        public string id;
        public string commonName;
        public string scientificName;
        public string kingdom;        // matches SpeciesKingdom enum
        public string group;          // e.g. "Arthropod", "Chordate"
        public string firstAge;       // GeologicalAge name
        public string lastAge;        // GeologicalAge name; empty = extant
        public List<string> habitats; // TerrainKind names
        public string diet;
        public float sizeCm;
        public int startingPopulation;
        public bool playable;
        public string model;          // optional Resources path of a map model, e.g. "Models/Species/ActinophrysSol"
        public string mapStyle;       // ColonyStyle name: Drift, Fixed, Float, Ground, Soar, Swarm, Swim (default Drift)
        public string mapGait;        // Ground only: Walk (default), Hop or Slither
        public int colonySize;        // individuals shown on the map; 0 = the map style's default
        public float mapScale;        // size multiplier on the map (e.g. a bird modelled on a tall perch); 0 = 1
        public float wingBeat;        // wing/fin beats per second on the map; 0 = the model doesn't flap
        public float wingRoot;        // body half-width as a fraction of the model's half-span (what stays still); 0 = 0.15
        public List<GeneValue> genes;
        public string description;
    }

    [Serializable]
    public class SpeciesCollection
    {
        public List<SpeciesDefinition> species;
    }

    // --- Factions (factions.json) ---
    // A faction is what a player plays as, like a civilization in Civ: a name, a two-colour band
    // and iconic animals that activate when the game reaches their geological period.

    [Serializable]
    public class IconicAnimalDefinition
    {
        public string name;
        public string scientificName;
        public string age;                // GeologicalAge name; the animal activates when this period begins
        public string description;
        public int bonusEvolutionPoints;  // granted to the faction's player on activation
    }

    [Serializable]
    public class FactionDefinition
    {
        public string id;
        public string displayName;        // default player name; players can type their own
        public string category;           // "Modern realm" | "Paleocontinent" | "Ancient ocean"
        public string realm;              // optional realms.json id
        public string primaryColor;       // hex, e.g. "#2F6DB5"
        public string secondaryColor;
        public string description;
        public List<IconicAnimalDefinition> iconicAnimals;
    }

    [Serializable]
    public class FactionCollection
    {
        public List<FactionDefinition> factions;
    }
}
