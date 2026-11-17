using UnityEngine;

namespace NaturalHistory.World
{
    public partial class ColonyGroup
    {
        private Niche? niche;

        // The niche the group holds on its tile (see Niches): one group per niche per tile. Set by
        // SpeciesColonies when it takes the slot; it depends on the tile (land or water, plants).
        public Niche Niche
        {
            get => niche ??= Niches.Of(Definition, Cell);
            internal set => niche = value;
        }

        // Where on its tile the group stands (offset from the tile centre), so groups in different
        // niches of the same tile don't pile up on each other.
        private Vector3 Spot => Niches.Spot(Niche);

        // How far below its tile's surface the group is drawn: in the under view, seafloor dwellers
        // sit on the seabed and swimmers in the water column; in the sky view fliers rise above the
        // clouds (negative) (set by HexGrid.Under)
        public float DepthOffset { get; set; }
    }
}
