using System;
using System.Collections.Generic;
using System.Linq;
using NaturalHistory.Core;
using NaturalHistory.Evolution;
using NaturalHistory.Players;
using NaturalHistory.World;
using UnityEngine;

namespace NaturalHistory.UI
{
    // When the map is redrawn for a new date (HexGrid.TerrainChanging / TerrainChanged: a new period,
    // or the climate within one moving far enough), tells the player what changed: the sea rising or
    // falling, deserts, ice and forests spreading or shrinking, and which of their animals had to
    // move because their tile no longer suits them (or found nowhere to go). Not while a game loads.
    public class ClimateNotice
    {
        private const int SettleFrames = 3; // the players' copies are put back in a LateUpdate after the change

        private readonly Action<string> show;
        private readonly Func<bool> loading;
        private HexGrid grid;

        private struct Tile { public bool water, desert, ice, forest; }
        private Dictionary<HexCell, Tile> before;
        private Dictionary<OwnedCopy, HexCell> homes;
        private GeologicalAge ageBefore;
        private int dueFrame = -1;

        public ClimateNotice(Action<string> show, Func<bool> loading)
        {
            this.show = show;
            this.loading = loading;
        }

        private static Tile Of(HexCell c) => new()
        {
            water  = c.IsWater,
            desert = c.Terrain.kind == TerrainKind.Desert,
            ice    = c.Biome == TerrainKind.IceSheet || c.Terrain.kind == TerrainKind.IceSheet,
            forest = c.IsForest || c.Feature == TerrainFeature.Jungle,
        };

        private static Player Human => PlayerManager.Instance != null ? PlayerManager.Instance.Human : null;

        private void OnChanging()
        {
            if (loading()) { before = null; return; }
            before = new Dictionary<HexCell, Tile>();
            for (int r = 0; r < grid.Height; r++)
            for (int q = 0; q < grid.Width; q++)
            {
                var c = grid.GetCell(q, r);
                if (c?.Terrain != null) before[c] = Of(c);
            }
            ageBefore = grid.DisplayedAge;
            homes = EvolutionManager.Instance == null ? new() :
                EvolutionManager.Instance.CopiesOf(Human).Where(c => c.group != null && c.group.Cell != null).ToDictionary(c => c, c => c.group.Cell);
        }

        private void OnChanged()
        {
            if (before != null) dueFrame = Time.frameCount + SettleFrames;
        }

        // Polled every frame
        public void Update()
        {
            if (grid == null && HexGrid.Instance != null)
            {
                grid = HexGrid.Instance;
                grid.TerrainChanging += OnChanging;
                grid.TerrainChanged  += OnChanged;
            }
            if (dueFrame < 0 || Time.frameCount < dueFrame) return;
            dueFrame = -1;
            if (before == null || grid == null) return;
            var message = Describe();
            before = null; homes = null;
            if (!string.IsNullOrEmpty(message)) show(message);
        }

        private string Describe()
        {
            int flooded = 0, emerged = 0, desert = 0, ice = 0, forest = 0;
            foreach (var (c, was) in before)
            {
                if (c == null || c.Terrain == null) continue;
                var now = Of(c);
                if (was.water != now.water) { if (now.water) flooded++; else emerged++; continue; }
                if (now.water) continue;
                desert += (now.desert ? 1 : 0) - (was.desert ? 1 : 0);
                ice    += (now.ice    ? 1 : 0) - (was.ice    ? 1 : 0);
                forest += (now.forest ? 1 : 0) - (was.forest ? 1 : 0);
            }

            var parts = new List<string>();
            if (flooded > emerged) parts.Add(Loc.F("the sea rose and flooded {0} land tiles", flooded - emerged));
            else if (emerged > flooded) parts.Add(Loc.F("the sea fell and {0} tiles of shallow sea became land", emerged - flooded));
            const int Notable = 3; // small shifts aren't worth a word
            if (desert >= Notable) parts.Add(Loc.F("deserts spread over {0} tiles", desert));
            else if (desert <= -Notable) parts.Add(Loc.F("deserts shrank by {0} tiles", -desert));
            if (ice >= Notable) parts.Add(Loc.F("ice spread over {0} tiles", ice));
            else if (ice <= -Notable) parts.Add(Loc.F("ice retreated from {0} tiles", -ice));
            if (forest >= Notable) parts.Add(Loc.F("forests grew over {0} tiles", forest));
            else if (forest <= -Notable) parts.Add(Loc.F("forests were lost from {0} tiles", -forest));

            int moved = 0, lost = 0;
            foreach (var (copy, home) in homes ?? new Dictionary<OwnedCopy, HexCell>())
            {
                if (copy.group == null || copy.group.Cell == null) lost++;
                else if (copy.group.Cell != home) moved++;
            }

            bool newPeriod = grid.DisplayedAge != ageBefore;
            if (parts.Count == 0 && moved == 0 && lost == 0) return null;
            string head = newPeriod
                ? Loc.F("The land changes with the {0}", Loc.T(grid.DisplayedAge.ToString()))
                : Loc.F("The climate has changed ({0} million years ago)", grid.DisplayedMillionYearsAgo.ToString("0.#"));
            var text = parts.Count > 0 ? Loc.F("{0}: {1}", head, string.Join(Loc.T(", "), parts)) : head;
            if (moved > 0) text += "\n" + Loc.F(moved == 1 ? "{0} of your groups had to move: its tile no longer suits it" : "{0} of your groups had to move: their tiles no longer suit them", moved);
            if (lost > 0) text += "\n" + Loc.F(lost == 1 ? "{0} of your groups found nowhere to live and is off the map until things change" : "{0} of your groups found nowhere to live and are off the map until things change", lost);
            return text;
        }
    }
}
