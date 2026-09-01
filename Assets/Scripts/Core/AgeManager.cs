using System;
using System.Collections.Generic;
using UnityEngine;

namespace NaturalHistory.Core
{
    public enum GeologicalAge
    {
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

    [Serializable]
    public class AgeDefinition
    {
        public GeologicalAge age;
        public string displayName;
        [TextArea] public string description;
        // MYA = millions of years ago (approximate start)
        public float startMillionYearsAgo;
        // Transition triggers — set via inspector or driven by game events
        public List<string> transitionEventKeys;
    }

    public class AgeManager : MonoBehaviour
    {
        public static AgeManager Instance { get; private set; }

        public event Action<GeologicalAge, GeologicalAge> OnAgeTransition;

        public GeologicalAge CurrentAge { get; private set; }
        public AgeDefinition CurrentAgeDefinition => GetDefinition(CurrentAge);

        [SerializeField] private List<AgeDefinition> ageDefinitions;

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
        }

        public void Initialize()
        {
            CurrentAge = GeologicalAge.Cambrian;
            Debug.Log($"[AgeManager] Starting age: {CurrentAge}");
        }

        // Called by event system when a transition trigger fires
        public void TriggerAgeTransition(string eventKey)
        {
            var def = GetDefinition(CurrentAge);
            if (!def.transitionEventKeys.Contains(eventKey)) return;

            var next = CurrentAge + 1;
            if (!Enum.IsDefined(typeof(GeologicalAge), next)) return;

            var previous = CurrentAge;
            CurrentAge = next;
            Debug.Log($"[AgeManager] Age transition: {previous} → {CurrentAge}");
            OnAgeTransition?.Invoke(previous, CurrentAge);
        }

        private AgeDefinition GetDefinition(GeologicalAge age)
        {
            return ageDefinitions.Find(d => d.age == age);
        }
    }
}
