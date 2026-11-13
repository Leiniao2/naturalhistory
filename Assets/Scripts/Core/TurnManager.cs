using System;
using System.Collections.Generic;
using UnityEngine;

namespace NaturalHistory.Core
{
    public class TurnManager : MonoBehaviour
    {
        public static TurnManager Instance { get; private set; }

        public event Action<int> OnTurnEnd;
        public event Action<int> OnTurnBegin;

        public int CurrentTurn { get; private set; }

        private List<ITurnListener> listeners = new();

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
        }

        public void Initialize()
        {
            CurrentTurn = 1;
            BroadcastTurnBegin();
        }

        // Resume from a save
        public void Restore(int turn)
        {
            CurrentTurn = turn;
            BroadcastTurnBegin();
        }

        public void Register(ITurnListener listener) => listeners.Add(listener);
        public void Unregister(ITurnListener listener) => listeners.Remove(listener);

        public void EndTurn()
        {
            if (GameManager.Instance != null && GameManager.Instance.State != GameState.Playing) return;
            if (AgeManager.Instance != null && AgeManager.Instance.IsPresentDay) return; // reached 0 Ma

            OnTurnEnd?.Invoke(CurrentTurn);
            foreach (var l in listeners) l.OnTurnEnd(CurrentTurn);

            CurrentTurn++;
            BroadcastTurnBegin();
        }

        private void BroadcastTurnBegin()
        {
            Debug.Log($"[TurnManager] Turn {CurrentTurn} begins");
            OnTurnBegin?.Invoke(CurrentTurn);
            foreach (var l in listeners) l.OnTurnBegin(CurrentTurn);
        }
    }

    public interface ITurnListener
    {
        void OnTurnBegin(int turn);
        void OnTurnEnd(int turn);
    }
}
