using UnityEngine;

namespace NaturalHistory.World
{
    public partial class ColonyGroup
    {
        private Niche? niche;

        // The niche the group takes on its tile (see Niches): one group per niche per tile.
        public Niche Niche => niche ??= Niches.Of(Definition);

        // Where on its tile the group stands (offset from the tile centre), so groups in different
        // niches of the same tile don't pile up on each other.
        private Vector3 Spot => Niches.Spot(Niche);
    }
}
