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
            if (cell == shownCell) return;
            shownCell = cell;

            var t = climate.Get(cell);
            tilePanel.RemoveFromClassList("hidden");
            var (col, row) = cell.Coordinates.ToOffsetCoordinates();
            tileTitle.text = $"{cell.Terrain?.kind}{(cell.IsForest ? " (forest)" : "")}  ·  ({col}, {row})";
            tileZone.text  = ClimateSystem.ZoneName(t.Zone);
            tileStats.text =
                $"Temperature: {t.TemperatureC:0.0} °C\n" +
                $"Humidity: {t.Humidity:0} %\n" +
                $"Oxygen: {t.O2Percent:0.00} %\n" +
                $"CO2: {t.Co2Ppm:0} ppm\n" +
                $"Elevation    level {cell.Elevation}";
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
