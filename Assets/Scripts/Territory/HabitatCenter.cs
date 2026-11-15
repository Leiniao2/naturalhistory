using System.Collections.Generic;
using NaturalHistory.Players;
using NaturalHistory.World;

namespace NaturalHistory.Territory
{
    // A player's home range: a named center hex and its 6 neighbours, which always belong to the
    // player. More hexes are claimed around the player's colonies (see TerritoryManager).
    public class HabitatCenter
    {
        public Player Owner { get; }
        public HexCell Cell { get; }
        public IReadOnlyList<HexCell> Core { get; } // Cell and its neighbours
        public string Name { get; }

        public HabitatCenter(Player owner, HexCell cell, IReadOnlyList<HexCell> core, string name)
        {
            Owner = owner;
            Cell  = cell;
            Core  = core;
            Name  = name;
        }
    }
}
