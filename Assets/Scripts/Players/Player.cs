using System;
using NaturalHistory.Core;
using NaturalHistory.Data;
using NaturalHistory.World;
using UnityEngine;

namespace NaturalHistory.Players
{
    // How a player is set up in the new-game screen, and how it is stored in a save.
    [Serializable]
    public class PlayerSetup
    {
        public string name;            // shown everywhere; defaults to the faction name
        public string faction;         // factions.json id
        public string primaryColor;    // colour band, hex
        public string secondaryColor;
        public bool human;
        public int startCol = -1;      // -1 = choose a start cell when the map is generated
        public int startRow = -1;

        public static PlayerSetup For(FactionDefinition faction, bool human) => new()
        {
            name           = faction.displayName,
            faction        = faction.id,
            primaryColor   = faction.primaryColor,
            secondaryColor = faction.secondaryColor,
            human          = human,
        };

        public PlayerSetup Clone() => (PlayerSetup)MemberwiseClone();
    }

    // One of the 1–10 players on the map. Comparable to a civilization in Civ: the faction gives
    // the default name, colour band and iconic animals.
    public class Player
    {
        public int Index { get; }
        public string Name { get; }
        public FactionDefinition Faction { get; }
        public Color Primary { get; }
        public Color Secondary { get; }
        public bool IsHuman { get; }
        public HexCell StartCell { get; internal set; }

        public Player(int index, PlayerSetup setup)
        {
            Index     = index;
            Faction   = GameDataLoader.GetFaction(setup.faction);
            Name      = string.IsNullOrWhiteSpace(setup.name) ? Faction?.displayName ?? $"Player {index + 1}" : setup.name.Trim();
            Primary   = ParseColor(setup.primaryColor, Faction?.primaryColor, Color.gray);
            Secondary = ParseColor(setup.secondaryColor, Faction?.secondaryColor, Color.white);
            IsHuman   = setup.human;
        }

        public string FactionName => Faction?.displayName ?? "No faction";

        // An iconic animal is active once the game has reached its period
        public static bool IsActive(IconicAnimalDefinition animal)
        {
            if (!Enum.TryParse<GeologicalAge>(animal.age, out var age)) return false;
            var current = AgeManager.Instance != null ? AgeManager.Instance.CurrentAge : GeologicalAge.Cambrian;
            return age <= current;
        }

        public PlayerSetup ToSetup()
        {
            var setup = new PlayerSetup
            {
                name           = Name,
                faction        = Faction?.id,
                primaryColor   = "#" + ColorUtility.ToHtmlStringRGB(Primary),
                secondaryColor = "#" + ColorUtility.ToHtmlStringRGB(Secondary),
                human          = IsHuman,
            };
            if (StartCell != null) (setup.startCol, setup.startRow) = StartCell.Coordinates.ToOffsetCoordinates();
            return setup;
        }

        private static Color ParseColor(string hex, string fallbackHex, Color fallback)
        {
            if (ColorUtility.TryParseHtmlString(hex, out var c)) return c;
            return ColorUtility.TryParseHtmlString(fallbackHex, out c) ? c : fallback;
        }
    }
}
