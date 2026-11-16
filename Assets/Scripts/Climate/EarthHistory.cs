using NaturalHistory.Core;
using NaturalHistory.World;
using UnityEngine;

namespace NaturalHistory.Climate
{
    // Turns a date into how the map looks then (WorldGenerator.Conditions) and how often volcanoes
    // erupt and meteors fall. Sea level, temperature and aridity come from climate_history.json
    // (ClimateSystem.SampleHistory); vegetation from the period and how wet it was; volcanism and
    // impacts from the dated record of large igneous provinces and impact events.
    public static class EarthHistory
    {
        // Share of the map per metre of sea level: +250 m (Cretaceous peak) floods about a fifth of
        // today's land; −125 m (Last Glacial Maximum) exposes the continental shelves.
        private const float SeaPerMetreUp   = 0.0004f;
        private const float SeaPerMetreDown = 0.00035f;
        private const float TodayC          = 14f;
        private const float WarmthPerDegree = 0.012f;
        private const float AridityPerPoint = 0.025f; // climate_history humidityOffset points

        // Forest cover by period, before the wetness adjustment: the first forests in the Devonian,
        // the coal forests of the Carboniferous, arid Pangaea, forests to the poles in the Eocene,
        // grasslands taking over in the Neogene.
        private static float PeriodVegetation(GeologicalAge age) => age switch
        {
            GeologicalAge.Devonian      => 0.55f,
            GeologicalAge.Carboniferous => 1.35f,
            GeologicalAge.Permian       => 0.8f,
            GeologicalAge.Triassic      => 0.7f,
            GeologicalAge.Jurassic      => 1.0f,
            GeologicalAge.Cretaceous    => 1.05f,
            GeologicalAge.Paleogene     => 1.25f,
            GeologicalAge.Neogene       => 0.9f,
            GeologicalAge.Quaternary    => 0.85f,
            _                           => 1f, // no forests before the Devonian anyway (EraFlora)
        };

        // (millions of years ago, extra activity at the peak, spread in My)
        private static readonly (float ma, float amount, float width)[] VolcanicPulses =
        {
            (510f, 1.0f, 3f),   // Kalkarindji
            (372f, 1.0f, 3f),   // Viluy traps, Late Devonian
            (260f, 1.0f, 2f),   // Emeishan traps
            (252f, 3.0f, 3f),   // Siberian Traps, end-Permian
            (201.5f, 2.5f, 2f), // Central Atlantic Magmatic Province
            (183f, 1.2f, 3f),   // Karoo–Ferrar
            (133f, 1.0f, 3f),   // Paraná–Etendeka
            (120f, 1.5f, 4f),   // Ontong Java Plateau
            (94f, 1.0f, 3f),    // Caribbean plateau
            (66.5f, 2.5f, 2f),  // Deccan Traps
            (56f, 1.2f, 2f),    // North Atlantic Igneous Province
            (16.5f, 0.8f, 2f),  // Columbia River basalts
        };

        private static readonly (float ma, float amount, float width)[] ImpactPulses =
        {
            (467f, 4.0f, 6f),   // Ordovician meteor event: an asteroid break-up showered the Earth
            (377f, 1.2f, 3f),   // Late Devonian impacts (Siljan, Alamo)
            (214f, 1.5f, 2f),   // Manicouagan
            (145f, 1.0f, 2f),   // Morokweng
            (66f, 6.0f, 1.5f),  // Chicxulub
            (35.5f, 2.5f, 2f),  // Popigai and Chesapeake Bay
        };

        // Multiplier on how often volcanoes erupt, and how many there are (1 = an ordinary time)
        public static float Volcanism(float ma) => 1f + Pulses(VolcanicPulses, ma) + 0.25f * Mathf.Clamp01((ClimateSystem.SampleHistory(ma).Co2Ppm - 500f) / 3000f);

        // Multiplier on how often meteors fall (1 = an ordinary time)
        public static float MeteorRate(float ma) => 1f + Pulses(ImpactPulses, ma);

        private static float Pulses((float ma, float amount, float width)[] pulses, float ma)
        {
            float sum = 0f;
            foreach (var (at, amount, width) in pulses)
            {
                float d = (ma - at) / width;
                sum += amount * Mathf.Exp(-d * d);
            }
            return sum;
        }

        public static WorldGenerator.Conditions ConditionsAt(float ma, GeologicalAge age)
        {
            var g = SampleHistory(ma);
            float sea = g.SeaLevelM >= 0f ? g.SeaLevelM * SeaPerMetreUp : g.SeaLevelM * SeaPerMetreDown;
            float wet = g.Humidity; // the history's humidity offset (aridity nudge), −6 … +5
            return new WorldGenerator.Conditions
            {
                sea        = sea,
                warmth     = (g.TemperatureC - TodayC) * WarmthPerDegree,
                aridity    = -wet * AridityPerPoint,
                vegetation = Mathf.Clamp(PeriodVegetation(age) * (1f + wet * 0.04f), 0.3f, 1.6f),
                volcanism  = Volcanism(ma),
            };
        }

        // Whether the map should be re-dressed: the climate has moved enough to show
        public static bool Differs(WorldGenerator.Conditions a, WorldGenerator.Conditions b) =>
            Mathf.Abs(a.sea - b.sea) > 0.012f || Mathf.Abs(a.warmth - b.warmth) > 0.025f ||
            Mathf.Abs(a.aridity - b.aridity) > 0.04f || Mathf.Abs(a.vegetation - b.vegetation) > 0.15f ||
            Mathf.Abs(a.volcanism - b.volcanism) > 0.5f;

        private static GlobalClimate SampleHistory(float ma) => ClimateSystem.SampleHistory(ma);
    }
}
