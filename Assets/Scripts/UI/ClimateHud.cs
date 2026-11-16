using NaturalHistory.Climate;
using NaturalHistory.Core;
using NaturalHistory.World;
using UnityEngine.UIElements;

namespace NaturalHistory.UI
{
    // Date bar (period, Ma, turn, End Turn), world climate averages, and the selected tile's climate.
    public class ClimateHud
    {
        private readonly Label ageLabel, dateLabel, worldStats, worldNote, tileTitle, tileZone, tileStats;
        private readonly VisualElement tilePanel;
        private readonly Button endTurnButton;

        private GlobalClimate previous;
        private bool hasPrevious;
        private HexCell shownCell;
        private string shownNiches;

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
            endTurnButton.clicked += EndTurn;
        }

        public static void EndTurn() => TurnManager.Instance?.EndTurn();

        // Called when the turn / climate changes
        public void Refresh()
        {
            var ages = AgeManager.Instance;
            if (ages != null && ages.CurrentAgeData != null)
            {
                ageLabel.text  = ages.IsPresentDay ? "Present day" : ages.CurrentAgeData.displayName;
                dateLabel.text = ages.IsPresentDay
                    ? $"0 Ma · Turn {ages.CurrentTurn}"
                    : $"{FormatMa(ages.MillionYearsAgo)} · Turn {ages.CurrentTurn} / {ages.TotalTurns}";
                endTurnButton.SetEnabled(!ages.IsPresentDay);
            }

            var climate = ClimateSystem.Instance;
            if (climate != null)
            {
                var g = climate.Global;
                worldStats.text =
                    $"Temperature: {g.TemperatureC:0.0} °C {Trend(g.TemperatureC, previous.TemperatureC, 0.05f)}\n" +
                    $"Humidity: {g.Humidity:0} % {Trend(g.Humidity, previous.Humidity, 0.2f)}\n" +
                    $"Oxygen: {g.O2Percent:0.0} % {Trend(g.O2Percent, previous.O2Percent, 0.05f)}\n" +
                    $"CO2: {g.Co2Ppm:0} ppm {Trend(g.Co2Ppm, previous.Co2Ppm, 2f)}\n" +
                    $"Sea level: {g.SeaLevelM:+0;-0;0} m";
                worldNote.text = string.IsNullOrEmpty(g.Note) ? "" : $"Near: {g.Note}";
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
            var occupants = NicheLines(cell);
            if (cell == shownCell && occupants == shownNiches) return; // also redraw when groups come and go
            shownCell   = cell;
            shownNiches = occupants;

            var t = climate.Get(cell);
            tilePanel.RemoveFromClassList("hidden");
            var (col, row) = cell.Coordinates.ToOffsetCoordinates();
            tileTitle.text = $"{(cell.Terrain != null ? EraFlora.DisplayName(cell.Terrain.kind) : "?")}  ·  ({col}, {row})";
            tileZone.text  = ClimateSystem.ZoneName(t.Zone);
            // Named species on the tile; otherwise a description (bare rock, reefs, oases…)
            var flora = cell.Plants.Count > 0 ? string.Join(", ", System.Linq.Enumerable.Select(cell.Plants, p => p.Label))
                      : HexGrid.Instance != null ? EraFlora.FloraOf(cell, HexGrid.Instance.DisplayedAge) : null;
            tileStats.text = (flora != null ? $"Plants: {flora}\n" : "") +
                $"Temperature: {t.TemperatureC:0.0} °C\n" +
                $"Humidity: {t.Humidity:0} %\n" +
                $"Oxygen: {t.O2Percent:0.00} %\n" +
                $"CO2: {t.Co2Ppm:0} ppm\n" +
                $"Elevation    level {cell.Elevation}" +
                NicheLines(cell);
        }

        // The tile's six niches and the animal group holding each (Niches)
        private static string NicheLines(HexCell cell)
        {
            if (cell.IsMountain) return "";
            var colonies = SpeciesColonies.Instance;
            var sb = new System.Text.StringBuilder("\nNiches:");
            foreach (var niche in Niches.All)
            {
                var g = colonies != null ? colonies.GroupAt(cell, niche) : null;
                var who = g?.Definition == null ? "free"
                        : g.Definition.commonName + (g.Owner != null ? $" ({(g.Owner.IsHuman ? "yours" : g.Owner.Name)})" : "");
                sb.Append($"\n  {Niches.Name(niche, cell)}: {who}");
            }
            return sb.ToString();
        }

        private string Trend(float now, float before, float threshold)
        {
            if (!hasPrevious) return "";
            float d = now - before;
            return d > threshold ? "↑" : d < -threshold ? "↓" : "";
        }

        public static string FormatMa(float ma) => ma switch
        {
            >= 10f  => $"{ma:0.0} Ma",
            >= 0.1f => $"{ma:0.00} Ma",
            _       => $"{ma * 1000f:0.0} ka",
        };
    }
}
