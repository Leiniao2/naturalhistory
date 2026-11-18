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

        public static GameSettings Default => new() { landTier = 3, lengthTier = 1, startAge = nameof(GeologicalAge.Ediacaran) };
    }

    // Current game's settings and the ones the New Game screen will start with (Next)
    public static class GameOptions
    {
        public static readonly string[] LandNames   = { "Very small", "Small", "Medium", "Large", "Huge" };
        public static readonly float[]  LandShares  = { 0.2f, 0.3f, 0.4f, 0.5f, 0.6f }; // share of the map that is land today

        // Turns per period × this; tier 2 ("Fast") is the base table in ages.json
        public static readonly string[] LengthNames   = { "Very fast", "Fast", "Standard", "Long", "Epic" };
        public static readonly float[]  LengthFactors = { 0.6f, 1f, 1.5f, 2f, 3f };

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
