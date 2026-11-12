using NaturalHistory.Core;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

namespace NaturalHistory.UI
{
    public class UIManager : MonoBehaviour
    {
        public static UIManager Instance { get; private set; }

        [Header("HUD")]
        [SerializeField] private TextMeshProUGUI ageLabelText;
        [SerializeField] private TextMeshProUGUI turnText;
        [SerializeField] private Button endTurnButton;

        [Header("Panels")]
        [SerializeField] private GameObject pausePanel;
        [SerializeField] private GameObject ageTransitionPanel;
        [SerializeField] private TextMeshProUGUI ageTransitionLabel;

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
        }

        private void Start()
        {
            endTurnButton.onClick.AddListener(OnEndTurnClicked);

            TurnManager.Instance.OnTurnBegin += RefreshTurnDisplay;
            AgeManager.Instance.OnAgeTransition += ShowAgeTransition;
        }

        private void OnDestroy()
        {
            if (TurnManager.Instance != null)
                TurnManager.Instance.OnTurnBegin -= RefreshTurnDisplay;
            if (AgeManager.Instance != null)
                AgeManager.Instance.OnAgeTransition -= ShowAgeTransition;
        }

        private void RefreshTurnDisplay(int turn)
        {
            turnText.text = $"Turn {turn}";
            ageLabelText.text = AgeManager.Instance.CurrentAge.ToString();
        }

        private void ShowAgeTransition(Core.GeologicalAge from, Core.GeologicalAge to)
        {
            ageTransitionLabel.text = $"{from} → {to}";
            ageTransitionPanel.SetActive(true);
        }

        public void DismissAgeTransition() => ageTransitionPanel.SetActive(false);

        private void OnEndTurnClicked() => TurnManager.Instance.EndTurn();

        public void ShowPause(bool show) => pausePanel.SetActive(show);
    }
}
