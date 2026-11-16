using System;
using System.Collections.Generic;
using NaturalHistory.Data;
using UnityEngine;

namespace NaturalHistory.Core
{
    // The Ediacaran and the 12 periods of the Phanerozoic Eon, oldest first (names/order match ages.json).
    public enum GeologicalAge
    {
        Ediacaran,      // the last period of the Proterozoic: the first large, complex organisms
        Cambrian,
        Ordovician,
        Silurian,
        Devonian,
        Carboniferous,
        Permian,
        Triassic,
        Jurassic,
        Cretaceous,
        Paleogene,
        Neogene,
        Quaternary
    }

    // Maps turns onto geological time. Each period in ages.json has a number of turns; the date
    // (millions of years ago) advances evenly through the period, so it is continuous across turns
    // and period boundaries. The turn after the last one is the present day (0 Ma).
    public class AgeManager : MonoBehaviour
    {
        public static AgeManager Instance { get; private set; }

        public event Action<GeologicalAge, GeologicalAge> OnAgeTransition;
        // Raised every time the date changes (each turn, and on load); listeners read MillionYearsAgo
        public event Action TimeChanged;

        public GeologicalAge CurrentAge { get; private set; }
        public AgeDefinition CurrentAgeData => ages.Count > 0 ? ages[(int)CurrentAge] : null;
        public IReadOnlyList<AgeDefinition> Ages => ages;
        public float MillionYearsAgo { get; private set; }
        public int TotalTurns { get; private set; }
        public int CurrentTurn { get; private set; }
        public bool IsPresentDay => CurrentTurn > TotalTurns;
        public int TurnInAge { get; private set; }   // 1-based
        public int TurnsInAge => TurnsOf((int)CurrentAge);

        // Turns a period lasts in this game: ages.json's count × the game length (GameOptions)
        public int TurnsOf(int index) => index >= 0 && index < turnsOf.Count ? turnsOf[index] : 0;
        private readonly List<int> turnsOf = new();

        // Re-reads the periods with the current game length (a new game, or loading a save)
        public void ReloadAges() => LoadAges();

        private readonly List<AgeDefinition> ages = new();
        private readonly List<int> firstTurnOfAge = new();
        private bool subscribed;

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
        }

        private void OnDestroy()
        {
            if (subscribed && TurnManager.Instance != null) TurnManager.Instance.OnTurnBegin -= SetTurn;
            if (Instance == this) Instance = null;
        }

        // Called by GameManager.BeginPlay before TurnManager.Initialize
        public void Initialize()
        {
            LoadAges();
            if (!subscribed && TurnManager.Instance != null)
            {
                TurnManager.Instance.OnTurnBegin += SetTurn;
                subscribed = true;
            }
            CurrentTurn = 0;
            SetTurn(1);
            Debug.Log($"[AgeManager] {ages.Count} periods, {TotalTurns} turns. Starting in the {CurrentAge} ({MillionYearsAgo:0.#} Ma)");
        }

        public int FirstTurnOf(GeologicalAge age) => (int)age < firstTurnOfAge.Count ? firstTurnOfAge[(int)age] : 1;

        // Admin: jump straight to a turn (e.g. the first turn of a period, or TotalTurns + 1 for the
        // present day) without playing the turns in between. Goes through TurnManager like loading
        // a save, so the turn counter stays in step; no period-transition announcement.
        public void JumpToTurn(int turn)
        {
            if (ages.Count == 0) return;
            turn = Mathf.Clamp(turn, 1, TotalTurns + 1);
            if (TurnManager.Instance != null) TurnManager.Instance.Restore(turn);
            else SetTurn(turn);
        }

        public float MillionYearsAgoAt(int turn)
        {
            if (ages.Count == 0) return 0f;
            int i = AgeIndexAt(turn);
            if (turn > TotalTurns) return 0f;
            var age = ages[i];
            float t = (turn - firstTurnOfAge[i]) / (float)Mathf.Max(1, turnsOf[i]);
            return Mathf.Lerp(age.startMillionYearsAgo, age.endMillionYearsAgo, t);
        }

        // Updates the date for a turn; fires OnAgeTransition when the period changes.
        private void SetTurn(int turn)
        {
            if (ages.Count == 0) return;
            var previous = CurrentAge;
            // Only a normal one-turn step announces a new period (not starting or loading a save)
            bool stepped = CurrentTurn > 0 && turn == CurrentTurn + 1;

            CurrentTurn     = Mathf.Max(1, turn);
            int index       = AgeIndexAt(CurrentTurn);
            CurrentAge      = (GeologicalAge)index;
            TurnInAge       = Mathf.Min(CurrentTurn - firstTurnOfAge[index] + 1, turnsOf[index]);
            MillionYearsAgo = MillionYearsAgoAt(CurrentTurn);

            if (stepped && previous != CurrentAge)
            {
                Debug.Log($"[AgeManager] Age transition: {previous} → {CurrentAge}");
                OnAgeTransition?.Invoke(previous, CurrentAge);
            }
            TimeChanged?.Invoke();
        }

        private int AgeIndexAt(int turn)
        {
            for (int i = ages.Count - 1; i >= 0; i--)
                if (turn >= firstTurnOfAge[i]) return i;
            return 0;
        }

        private void LoadAges()
        {
            if (GameDataLoader.Ages == null) GameDataLoader.Initialize();
            ages.Clear();
            firstTurnOfAge.Clear();
            turnsOf.Clear();
            TotalTurns = 0;
            foreach (GeologicalAge age in Enum.GetValues(typeof(GeologicalAge)))
            {
                var def = GameDataLoader.GetAge(age.ToString());
                if (def == null) { Debug.LogError($"[AgeManager] ages.json has no entry for {age}"); continue; }
                ages.Add(def);
                firstTurnOfAge.Add(TotalTurns + 1);
                int turns = Mathf.Max(1, Mathf.RoundToInt(def.turns * GameOptions.LengthFactor));
                turnsOf.Add(turns);
                TotalTurns += turns;
            }
        }
    }
}
