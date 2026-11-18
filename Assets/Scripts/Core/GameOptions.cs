using System;
using UnityEngine;

namespace NaturalHistory.Core
{
    // The choices made when starting a game (New Game screen), kept in its save
    [Serializable]
    public struct GameSettings
    {
        public int landTier;    // index into GameOptions.LandShares
        public int lengthTier;  // index into GameOptions.LengthFactors
        public string startAge; // GeologicalAge name
        // By name, so saves from before these existed (no value) read as the defaults
        public string mapSize;    // GameOptions.MapSizeNames
        public string difficulty; // GameOptions.DifficultyNames

        public static GameSettings Default => new() { landTier = 3, lengthTier = 1, startAge = nameof(GeologicalAge.Ediacaran),
                                                      mapSize = "Standard", difficulty = "Normal" };
    }

    // Current game's settings and the ones the New Game screen will start with (Next)
    public static class GameOptions
    {
        public static readonly string[] LandNames   = { "Very small", "Small", "Medium", "Large", "Huge" };
        public static readonly float[]  LandShares  = { 0.2f, 0.3f, 0.4f, 0.5f, 0.6f }; // share of the map that is land today

        // Turns per period × this; tier 2 ("Fast") is the base table in ages.json
        public static readonly string[] LengthNames   = { "Very fast", "Fast", "Standard", "Long", "Epic" };
        public static readonly float[]  LengthFactors = { 0.6f, 1f, 1.5f, 2f, 3f };

        // Map size: columns × rows of hexes, and how many players fit on it
        public static readonly string[]     MapSizeNames = { "Tiny", "Small", "Standard", "Large", "Huge" };
        public static readonly Vector2Int[] MapSizes     = { new(30, 18), new(40, 24), new(50, 30), new(62, 38), new(76, 46) };
        public static readonly int[]        MapPlayers   = { 4, 6, 8, 10, 10 };
        public const int DefaultMapSize = 2;

        // Difficulty: the EP you start with and earn each turn, and how hard rival and wild animals
        // hit yours (CombatStats damage, see Combat.Damage)
        public static readonly string[] DifficultyNames  = { "Easy", "Normal", "Hard", "Brutal" };
        public static readonly float[]  StartPointShares = { 1.5f, 1f, 0.75f, 0.5f };
        public static readonly float[]  IncomeShares     = { 1.25f, 1f, 0.85f, 0.7f };
        public static readonly float[]  FoeDamageShares  = { 0.8f, 1f, 1.15f, 1.3f };
        public const int DefaultDifficulty = 1;

        public static int MapSizeTier(GameSettings s)    => Index(MapSizeNames, s.mapSize, DefaultMapSize);
        public static int DifficultyTier(GameSettings s) => Index(DifficultyNames, s.difficulty, DefaultDifficulty);
        private static int Index(string[] names, string name, int fallback)
        {
            int i = Array.IndexOf(names, name);
            return i >= 0 ? i : fallback;
        }

        public static Vector2Int MapSize(GameSettings s) => MapSizes[MapSizeTier(s)];
        public static int MaxPlayers(GameSettings s)     => MapPlayers[MapSizeTier(s)];
        public static float StartPointShare => StartPointShares[DifficultyTier(Current)];
        public static float IncomeShare     => IncomeShares[DifficultyTier(Current)];
        public static float FoeDamageShare  => FoeDamageShares[DifficultyTier(Current)];

        public static GameSettings Current = GameSettings.Default;
        public static GameSettings Next    = GameSettings.Default;

        public static float LandShare    => LandShares[Mathf.Clamp(Current.landTier, 0, LandShares.Length - 1)];
        public static float LengthFactor => LengthFactors[Mathf.Clamp(Current.lengthTier, 0, LengthFactors.Length - 1)];

        public static GeologicalAge StartAge =>
            Enum.TryParse(Current.startAge, true, out GeologicalAge a) ? a : GeologicalAge.Ediacaran;

        // Until the Devonian life is mostly in the sea: games starting then begin on the seabed, in
        // the layer under sea level; from the Devonian on they begin on the surface. (The surface
        // can be shown from the Cambrian on, see UnderView.SurfaceOpen.)
        public static bool StartsUnderSea(GeologicalAge age) => age < GeologicalAge.Devonian;

        // Saves from before these settings existed: the defaults (Large land, Fast)
        public static GameSettings FromSave(GameSettings saved, bool present) =>
            present ? saved : new GameSettings { landTier = 3, lengthTier = 1, startAge = nameof(GeologicalAge.Ediacaran) };
    }
}
