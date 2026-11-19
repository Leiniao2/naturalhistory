using NaturalHistory.Core;
using UnityEngine;

namespace NaturalHistory.Progression
{
    // EP prices grow with the periods, along the Fibonacci numbers from 5: the Ediacaran is 5, the
    // Cambrian 8, the Ordovician 13, then 21, 34, 55... up to 1597 in the Quaternary. Every price
    // (Functions and Behaviors items, evolving; not reproducing) is its base, the Ediacaran price,
    // times that number over 5, so ×1.6 in the Cambrian, ×2.6 in the Ordovician, ×319 in the
    // Quaternary. The period is the one the game is in.
    public static class EpCosts
    {
        private const int First = 5; // the Ediacaran's Fibonacci number

        // The Fibonacci number of the period (Ediacaran = 0): 5, 8, 13, 21...
        public static long FibonacciOf(int period)
        {
            long a = 3, b = First; // the two numbers before and at the Ediacaran
            for (int i = 0; i < period; i++) (a, b) = (b, a + b);
            return b;
        }

        public static float Factor => FibonacciOf(Period) / (float)First;

        public static int Of(int baseCost) => baseCost <= 0 ? baseCost : Mathf.Max(1, Mathf.RoundToInt(baseCost * Factor));

        private static int Period
        {
            get
            {
                var ages = AgeManager.Instance;
                if (ages == null) return 0;
                return (int)(ages.IsPresentDay ? GeologicalAge.Quaternary : ages.CurrentAge);
            }
        }
    }
}
