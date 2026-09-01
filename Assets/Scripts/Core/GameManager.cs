using NaturalHistory.Data;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace NaturalHistory.Core
{
    public enum GameState { MainMenu, Setup, Playing, Paused, AgeTransition, GameOver }

    public class GameManager : MonoBehaviour
    {
        public static GameManager Instance { get; private set; }

        public GameState State { get; private set; }

        [SerializeField] private AgeManager ageManager;
        [SerializeField] private TurnManager turnManager;

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }

        private void Start()
        {
            GameDataLoader.Initialize();
            TransitionTo(GameState.MainMenu);
        }

        public void StartNewGame()
        {
            SceneManager.LoadScene("Game");
            TransitionTo(GameState.Setup);
        }

        public void BeginPlay()
        {
            ageManager.Initialize();
            turnManager.Initialize();
            TransitionTo(GameState.Playing);
        }

        public void TransitionTo(GameState next)
        {
            State = next;
            Debug.Log($"[GameManager] State → {next}");
        }

        public void PauseToggle()
        {
            if (State == GameState.Playing) TransitionTo(GameState.Paused);
            else if (State == GameState.Paused) TransitionTo(GameState.Playing);
        }

        public void QuitToMenu()
        {
            TransitionTo(GameState.MainMenu);
            SceneManager.LoadScene("MainMenu");
        }
    }
}
