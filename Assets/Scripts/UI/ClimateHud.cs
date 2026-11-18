using NaturalHistory.Climate;
using NaturalHistory.Core;
using NaturalHistory.World;
using UnityEngine;
using UnityEngine.UIElements;

namespace NaturalHistory.UI
{
    // Date bar (period, Ma, turn, End Turn), world climate averages (in the Geologic Time panel the
    // period button opens), and the selected tile's climate.
    public class ClimateHud
    {
        private readonly Label ageLabel, dateLabel, worldStats, worldNote, tileTitle, tileZone, tileStats;
        private readonly VisualElement tilePanel;
        private readonly Button endTurnButton;

        private GlobalClimate previous;
        private bool hasPrevious;
        private HexCell shownCell;
        private string shownNiches;
        private MapLayer shownLayer;

        public ClimateHud(VisualElement root)
        {
            ageLabel      = root.Q<Label>("age-label");
            dateLabel     = root.Q<Label>("date-label");
            worldStats    = root.Q<Label>("world-stats");
            worldNote     = root.Q<Label>("world-note");
            tilePanel     = root.Q("tile-panel");
            tileTitle     = root.Q<Label>("tile-title");
            tileZone      = root.Q<Label>("tile-zone");
            tileStats     = root.Q<Label>("tile-stats");
            endTurnButton = root.Q<Button>("end-turn-button");
            // Next animal awaiting orders, or End Turn when none do (UnitCycle); Shift+click ends it regardless
            endTurnButton.clicked += () => EndTurn(Input.GetKey(KeyCode.LeftShift) || Input.GetKey(KeyCode.RightShift));
        }

        public static void EndTurn(bool force = false)
        {
            if (UnitCycle.Instance != null) UnitCycle.Instance.EndTurnOrNext(force);
            else TurnManager.Instance?.EndTurn();
        }

        // Called when the turn / climate changes
        public void Refresh()
        {
            var ages = AgeManager.Instance;
            if (ages != null && ages.CurrentAgeData != null)
            {
                ageLabel.text  = Loc.T(ages.IsPresentDay ? "Present day" : ages.CurrentAgeData.displayName);
                dateLabel.text = ages.IsPresentDay
                    ? Loc.F("0 Ma · Turn {0}", ages.CurrentTurn)
                    : Loc.F("{0} · Turn {1} / {2}", FormatMa(ages.MillionYearsAgo), ages.CurrentTurn, ages.TotalTurns);
                endTurnButton.SetEnabled(!ages.IsPresentDay);
            }

            var climate = ClimateSystem.Instance;
            if (climate != null)
            {
                var g = climate.Global;
                worldStats.text =
                    Loc.F("Temperature: {0:0.0} °C {1}", g.TemperatureC, Trend(g.TemperatureC, previous.TemperatureC, 0.05f)) + "\n" +
                    Loc.F("Humidity: {0:0} % {1}", g.Humidity, Trend(g.Humidity, previous.Humidity, 0.2f)) + "\n" +
                    Loc.F("Oxygen: {0:0.0} % {1}", g.O2Percent, Trend(g.O2Percent, previous.O2Percent, 0.05f)) + "\n" +
                    Loc.F("CO2: {0:0} ppm {1}", g.Co2Ppm, Trend(g.Co2Ppm, previous.Co2Ppm, 2f)) + "\n" +
                    Loc.F("Sea level: {0:+0;-0;0} m", g.SeaLevelM) + LandLines();
                worldNote.text = string.IsNullOrEmpty(g.Note) ? "" : Loc.F("Near: {0}", Loc.T(g.Note));
                previous = g;
                hasPrevious = true;
            }
            shownCell = null; // force the tile panel to redraw
            RefreshTile();
        }

        // Polled every frame: follows CellSelector's selection
        public void RefreshTile()
        {
            var cell = CellSelector.Selected;
            var climate = ClimateSystem.Instance;
            if (cell == null || climate == null || !climate.HasData)
            {
                tilePanel.AddToClassList("hidden");
                shownCell = null;
                return;
            }
            var layer = UnderView.Layer;
            var occupants = NicheLines(cell, layer);
            // also redraw when groups come and go, or the view switches layer
            if (cell == shownCell && occupants == shownNiches && layer == shownLayer) return;
            shownCell   = cell;
            shownNiches = occupants;
            shownLayer  = layer;

            var t = climate.Get(cell);
            tilePanel.RemoveFromClassList("hidden");
            var (col, row) = cell.Coordinates.ToOffsetCoordinates();
            if (layer == MapLayer.Under)
            {
                ShowUnderTile(cell, col, row, occupants);
                return;
            }
            if (layer == MapLayer.Sky)
            {
                ShowSkyTile(cell, col, row, occupants);
                return;
            }
            var landform = EraFlora.LandformName(cell.Feature);
            var terrainName = cell.Terrain != null ? Loc.T(EraFlora.DisplayName(cell.Terrain.kind)) : "?";
            if (cell.IsHighMountain) terrainName = Loc.T("High mountain"); // above the clouds (HexGrid.HighMountains)
            tileTitle.text = $"{(landform != null ? $"{landform} ({terrainName})" : terrainName)}  ·  ({col}, {row})";
            tileZone.text  = Loc.T(ClimateSystem.ZoneName(t.Zone));
            // Named species on the tile; otherwise a description (bare rock, reefs, oases…)
            var flora = cell.Plants.Count > 0 ? string.Join(", ", System.Linq.Enumerable.Select(cell.Plants, p => Loc.T(p.Label)))
                      : HexGrid.Instance != null ? Loc.T(EraFlora.FloraOf(cell, HexGrid.Instance.DisplayedAge)) : null;
            // The layer under sea level below this tile, with any water plants or volcano there
            var below = Loc.T(UnderView.FloorName(cell));
            if (UnderView.Name(cell.UnderFeature) is string feature) below += $", {Loc.T(feature)}";
            var underPlants = System.Linq.Enumerable.ToList(System.Linq.Enumerable.Where(cell.UnderPlants, p => !UnderView.IsFloor(p)));
            if (underPlants.Count > 0) below += " · " + string.Join(", ", System.Linq.Enumerable.Select(underPlants, p => Loc.T(p.Label)));
            tileStats.text = (flora != null ? Loc.F("Plants: {0}", flora) + "\n" : "") +
                Loc.F("Below: {0}", below) + "\n" +
                Loc.F("Temperature: {0:0.0} °C", t.TemperatureC) + "\n" +
                Loc.F("Humidity: {0:0} %", t.Humidity) + "\n" +
                Loc.F("Oxygen: {0:0.00} %", t.O2Percent) + "\n" +
                Loc.F("CO2: {0:0} ppm", t.Co2Ppm) + "\n" +
                Loc.F("Elevation    level {0}", cell.Elevation) +
                occupants;
        }

        // In the under view the panel describes only the layer below the tile: its floor (seabed,
        // lakebed, caves, bedrock…), what grows there and the niches seen in that view, nothing of
        // the land surface above it.
        private void ShowUnderTile(HexCell cell, int col, int row, string occupants)
        {
            var title = Loc.T(UnderView.FloorName(cell));
            if (UnderView.Name(cell.UnderFeature) is string feature) title += $", {Loc.T(feature)}";
            tileTitle.text = $"{title}  ·  ({col}, {row})";
            tileZone.text  = "";
            var underPlants = System.Linq.Enumerable.ToList(System.Linq.Enumerable.Where(cell.UnderPlants, p => !UnderView.IsFloor(p)));
            var flora = underPlants.Count > 0 ? Loc.F("Plants: {0}", string.Join(", ", System.Linq.Enumerable.Select(underPlants, p => Loc.T(p.Label)))) : "";
            tileStats.text = (flora + occupants).TrimStart('\n');
        }

        // In the sky view: the sky over the tile, its summit niche on a mountain and the fliers
        private void ShowSkyTile(HexCell cell, int col, int row, string occupants)
        {
            var terrainName = cell.Terrain != null ? Loc.T(EraFlora.DisplayName(cell.Terrain.kind)) : "?";
            if (cell.IsHighMountain) terrainName = Loc.T("High mountain"); // above the clouds (HexGrid.HighMountains)
            tileTitle.text = $"{Loc.F("Sky over {0}", terrainName)}  ·  ({col}, {row})";
            tileZone.text  = "";
            tileStats.text = occupants.TrimStart('\n');
        }

        // The tile's niches in the layer shown and the animal group holding each (Niches), then the
        // animals visiting the layer from a niche of another (fliers in the sky, air-breathers at
        // the sea surface, burrowers underground).
        private static string NicheLines(HexCell cell, MapLayer layer)
        {
            var colonies = SpeciesColonies.Instance;
            var sb = new System.Text.StringBuilder();
            bool any = false;
            foreach (var niche in Niches.On(cell, layer))
            {
                if (!any) { sb.Append("\n" + Loc.T("Niches:")); any = true; }
                var g = colonies != null ? colonies.GroupAt(cell, niche) : null;
                sb.Append($"\n  {Niches.Name(niche)}: {(g?.Definition == null ? Loc.T("free") : Who(g))}");
            }
            if (colonies != null)
            {
                var visitors = new System.Collections.Generic.List<string>();
                foreach (var g in colonies.GroupsAt(cell))
                    if (Niches.LayerOf(g.Niche) != layer && UnderView.InLayer(g, layer)) visitors.Add(Who(g));
                if (visitors.Count > 0)
                    sb.Append("\n" + Loc.F(layer == MapLayer.Sky ? "Fliers: {0}" : "Visiting: {0}", string.Join(", ", visitors)));
            }
            return sb.ToString();
        }

        private static string Who(ColonyGroup g) =>
            Loc.T(g.Definition.commonName) + (g.Owner != null ? $" ({(g.Owner.IsHuman ? Loc.T("yours") : g.Owner.Name)})" : "");

        // What the map shows of that climate (HexGrid.Climate): shares of the land, volcanoes, impacts
        private static string LandLines()
        {
            var grid = HexGrid.Instance;
            if (grid == null || !grid.IsGenerated) return "";
            var s  = grid.Shares;
            float ma = grid.DisplayedMillionYearsAgo;
            return "\n" + Loc.F("Land: {0:0} % of the map", s.Land * 100f) +
                   "\n" + Loc.F("Desert {0:0} % · Tundra {1:0} % · Ice {2:0} %", s.Desert * 100f, s.Tundra * 100f, s.Ice * 100f) +
                   "\n" + Loc.F("Vegetated {0:0} % · Forest {1:0} %", s.Vegetated * 100f, s.Forest * 100f) +
                   "\n" + Loc.F("Volcanism ×{0:0.0} ({1} volcanoes) · Meteors ×{2:0.0}",
                                 Climate.EarthHistory.Volcanism(ma), s.Volcanoes, Climate.EarthHistory.MeteorRate(ma));
        }

        private string Trend(float now, float before, float threshold)
        {
            if (!hasPrevious) return "";
            float d = now - before;
            return d > threshold ? "↑" : d < -threshold ? "↓" : "";
        }

        public static string FormatMa(float ma) => ma switch
        {
            >= 10f  => Loc.F("{0:0.0} Ma", ma),
            >= 0.1f => Loc.F("{0:0.00} Ma", ma),
            _       => Loc.F("{0:0.0} ka", ma * 1000f),
        };
    }
}
