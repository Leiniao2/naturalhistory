using NaturalHistory.Climate;
using NaturalHistory.Core;
using NaturalHistory.Data;
using NaturalHistory.Players;
using NaturalHistory.Progression;
using NaturalHistory.Save;
using NaturalHistory.World;
using UnityEngine;
using UnityEngine.UIElements;

namespace NaturalHistory.UI
{
    // In-game UI Toolkit menus: HUD buttons, pause menu (Esc), save/load slots and the
    // Morphology / Ethology tree panels. Layout: Resources/UI/GameMenus.uxml, styles: GameMenusStyle.uss.
    public class GameMenus : MonoBehaviour
    {
        private UIDocument document;
        private VisualElement root, pauseOverlay, slotsOverlay, slotList;
        private Label epLabel, slotsTitle, toast;
        private TreePanel treePanel;
        private AgePanel agePanel;
        private ClimateHud climateHud;
        private PlayersPanel playersPanel;
        private bool slotsAreForSaving;
        private float toastHideTime;
        private int toastFrame = -1;

        private CellSelector cellSelector;
        private CameraController cameraController;

        private static ProgressionManager Progression => ProgressionManager.Instance;

        // Like PlayerBall: spawn in any scene with a map, so Game.unity doesn't need editing.
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Bootstrap()
        {
            if (FindAnyObjectByType<HexGrid>() == null || FindAnyObjectByType<GameMenus>() != null) return;

            // Panel settings are built at runtime so no scene/asset wiring is needed. The object starts
            // inactive so the UIDocument is fully configured before it enables.
            var panelSettings = ScriptableObject.CreateInstance<PanelSettings>();
            panelSettings.themeStyleSheet     = Resources.Load<ThemeStyleSheet>("UI/NHRuntimeTheme");
            panelSettings.scaleMode           = PanelScaleMode.ScaleWithScreenSize;
            panelSettings.referenceResolution = new Vector2Int(1920, 1080);
            panelSettings.match               = 0.5f;

            var go = new GameObject("GameMenus");
            go.SetActive(false);
            var doc = go.AddComponent<UIDocument>();
            doc.panelSettings   = panelSettings;
            doc.visualTreeAsset = Resources.Load<VisualTreeAsset>("UI/GameMenus");
            go.AddComponent<GameMenus>();
            go.SetActive(true);
        }

        private void Awake() => document = GetComponent<UIDocument>();

        private void Start()
        {
            // GameManager normally does this, but it isn't in Game.unity yet
            if (GameDataLoader.Genes == null) GameDataLoader.Initialize();

            root = document.rootVisualElement;
            root.styleSheets.Add(Resources.Load<StyleSheet>("UI/GameMenusStyle"));
            root.pickingMode = PickingMode.Ignore;

            epLabel      = root.Q<Label>("ep-label");
            pauseOverlay = root.Q("pause-overlay");
            slotsOverlay = root.Q("slots-overlay");
            slotList     = root.Q("slot-list");
            slotsTitle   = root.Q<Label>("slots-title");
            toast        = root.Q<Label>("toast");
            treePanel    = new TreePanel(root);
            agePanel     = new AgePanel(root);
            climateHud   = new ClimateHud(root);
            playersPanel = new PlayersPanel(root);
            playersPanel.NewGameStarted += () => { SetPauseOpen(false); ShowToast("New game started"); };
            playersPanel.SetupClosed    += () => pauseOverlay.RemoveFromClassList("hidden");

            root.Q<Button>("morphology-button").clicked += () => ToggleTree(Progression?.Morphology);
            root.Q<Button>("ethology-button").clicked   += () => ToggleTree(Progression?.Ethology);
            root.Q<Button>("menu-button").clicked       += () => SetPauseOpen(true);
            root.Q<Button>("resume-button").clicked     += () => SetPauseOpen(false);
            root.Q<Button>("new-game-button").clicked   += OpenNewGame;
            root.Q<Button>("save-button").clicked       += () => OpenSlots(saving: true);
            root.Q<Button>("load-button").clicked       += () => OpenSlots(saving: false);
            root.Q<Button>("quit-button").clicked       += Quit;
            root.Q<Button>("slots-back-button").clicked += CloseSlots;
            root.Q<Button>("age-button").clicked        += ToggleAges;

            cellSelector     = FindAnyObjectByType<CellSelector>();
            cameraController = FindAnyObjectByType<CameraController>();

            if (Progression != null) Progression.Changed += OnProgressionChanged;
            if (ClimateSystem.Instance != null) ClimateSystem.Instance.Updated += OnClimateUpdated;
            if (AgeManager.Instance != null) AgeManager.Instance.OnAgeTransition += OnAgeTransition;
            if (PlayerManager.Instance != null)
            {
                PlayerManager.Instance.PlayersChanged  += playersPanel.RefreshBar;
                PlayerManager.Instance.AnimalActivated += OnAnimalActivated;
            }
            playersPanel.RefreshBar();
            OnProgressionChanged();
            OnClimateUpdated();
        }

        private void OnDestroy()
        {
            if (Progression != null) Progression.Changed -= OnProgressionChanged;
            if (ClimateSystem.Instance != null) ClimateSystem.Instance.Updated -= OnClimateUpdated;
            if (AgeManager.Instance != null) AgeManager.Instance.OnAgeTransition -= OnAgeTransition;
            if (PlayerManager.Instance != null)
            {
                PlayerManager.Instance.PlayersChanged  -= playersPanel.RefreshBar;
                PlayerManager.Instance.AnimalActivated -= OnAnimalActivated;
            }
        }

        private void OnAnimalActivated(Player player, IconicAnimalDefinition animal)
        {
            if (!player.IsHuman) return;
            var bonus = animal.bonusEvolutionPoints > 0 ? $" (+{animal.bonusEvolutionPoints} EP)" : "";
            ShowToast($"{player.Name}: {animal.name} appears{bonus}");
        }

        // Fires after every turn (date → climate) and after loading
        private void OnClimateUpdated()
        {
            climateHud.Refresh();
            if (agePanel.IsOpen) agePanel.Refresh();
        }

        private void OnAgeTransition(GeologicalAge from, GeologicalAge to)
        {
            treePanel.Close();
            playersPanel.CloseFaction();
            agePanel.Open(newAge: true);
        }

        private void ToggleAges()
        {
            if (agePanel.IsOpen) { agePanel.Close(); return; }
            treePanel.Close();
            playersPanel.CloseFaction();
            agePanel.Open();
        }

        private void Update()
        {
            if (root == null) return;

            if (Input.GetKeyDown(KeyCode.Escape)) HandleEscape();
            if ((Input.GetKeyDown(KeyCode.Return) || Input.GetKeyDown(KeyCode.KeypadEnter)) && !AnyModalOpen())
                ClimateHud.EndTurn();
            climateHud.RefreshTile();
            if (toastHideTime > 0f && Time.unscaledTime > toastHideTime)
            {
                toast.AddToClassList("hidden");
                toastHideTime = 0f;
            }
            UpdateMapInput();
        }

        // Esc closes the top-most panel, or opens the pause menu if nothing is open
        private void HandleEscape()
        {
            if (IsOpen(slotsOverlay))  CloseSlots();
            else if (playersPanel.SetupOpen) { playersPanel.CloseSetup(); pauseOverlay.RemoveFromClassList("hidden"); }
            else if (playersPanel.FactionOpen) playersPanel.CloseFaction();
            else if (treePanel.IsOpen) treePanel.Close();
            else if (agePanel.IsOpen)  agePanel.Close();
            else SetPauseOpen(!IsOpen(pauseOverlay));
        }

        // Keep map clicks / camera input from happening through the UI. Only switched while no
        // mouse button is held so an in-progress camera drag isn't cut off.
        private void UpdateMapInput()
        {
            if (Input.GetMouseButton(0) || Input.GetMouseButton(1) || Input.GetMouseButton(2)) return;

            bool modal = AnyModalOpen();
            bool mapInput = !modal && !PointerOverUI();
            if (cellSelector != null)     cellSelector.enabled     = mapInput;
            if (cameraController != null) cameraController.enabled = !modal; // keep edge/WASD panning near the HUD
        }

        private bool AnyModalOpen() => IsOpen(pauseOverlay) || IsOpen(slotsOverlay) || treePanel.IsOpen || agePanel.IsOpen
                                       || playersPanel.FactionOpen || playersPanel.SetupOpen;

        private bool PointerOverUI()
        {
            var panel = root.panel;
            if (panel == null) return false;
            var mouse = Input.mousePosition;
            var panelPos = RuntimePanelUtils.ScreenToPanel(panel, new Vector2(mouse.x, Screen.height - mouse.y));
            return panel.Pick(panelPos) != null;
        }

        private void OnProgressionChanged()
        {
            if (epLabel != null && Progression != null) epLabel.text = $"EP {Progression.EvolutionPoints}";
            if (treePanel != null && treePanel.IsOpen) treePanel.Refresh();
        }

        // ---------- Trees ----------

        private void ToggleTree(ProgressionTree tree)
        {
            if (tree == null) return;
            agePanel.Close();
            playersPanel.CloseFaction();
            if (treePanel.IsOpen && treePanel.CurrentTree == tree) treePanel.Close();
            else treePanel.Open(tree);
        }

        // ---------- Pause menu ----------

        private void SetPauseOpen(bool open)
        {
            if (open) { treePanel.Close(); agePanel.Close(); playersPanel.CloseFaction(); }
            pauseOverlay.EnableInClassList("hidden", !open);
            if (!open) { slotsOverlay.AddToClassList("hidden"); playersPanel.CloseSetup(); }
        }

        private void OpenNewGame()
        {
            pauseOverlay.AddToClassList("hidden");
            playersPanel.OpenSetup();
        }

        private void Quit()
        {
#if UNITY_EDITOR
            UnityEditor.EditorApplication.isPlaying = false;
#else
            Application.Quit();
#endif
        }

        // ---------- Save / load ----------

        private void OpenSlots(bool saving)
        {
            slotsAreForSaving = saving;
            slotsTitle.text = saving ? "Save Game" : "Load Game";
            RebuildSlots();
            pauseOverlay.AddToClassList("hidden");
            slotsOverlay.RemoveFromClassList("hidden");
        }

        private void CloseSlots()
        {
            if (!IsOpen(slotsOverlay)) return;
            slotsOverlay.AddToClassList("hidden");
            pauseOverlay.RemoveFromClassList("hidden");
        }

        private void RebuildSlots()
        {
            slotList.Clear();
            for (int slot = 1; slot <= SaveSystem.SlotCount; slot++)
            {
                var data = SaveSystem.Peek(slot);
                var row  = new VisualElement().WithClass("slot-row");

                var info = new VisualElement().WithClass("slot-info");
                info.Add(new Label($"Slot {slot}").WithClass("slot-name"));
                info.Add(new Label(Describe(data)).WithClass("slot-detail"));
                row.Add(info);

                int captured = slot;
                if (slotsAreForSaving)
                {
                    row.Add(new Button(() => SaveTo(captured)) { text = data == null ? "Save" : "Overwrite" }.WithClass("slot-button"));
                }
                else if (data != null)
                {
                    row.Add(new Button(() => LoadFrom(captured)) { text = "Load" }.WithClass("slot-button"));
                    row.Add(new Button(() => { SaveSystem.Delete(captured); RebuildSlots(); }) { text = "Delete" }
                        .WithClass("slot-button").WithClass("danger"));
                }
                slotList.Add(row);
            }
        }

        private static string Describe(SaveData data)
        {
            if (data == null) return "Empty";
            var when = data.SavedAt.ToString("yyyy-MM-dd HH:mm");
            var turn = data.turn > 0 ? $"  ·  Turn {data.turn}" : "";
            var age  = string.IsNullOrEmpty(data.age) ? "" : $"  ·  {data.age}";
            var human   = data.players?.Find(p => p.human);
            var players = data.players is { Count: > 0 } ? $"  ·  {human?.name ?? "?"} + {data.players.Count - 1} AI" : "";
            return $"{when}{turn}{age}{players}  ·  {data.evolutionPoints} EP";
        }

        private void SaveTo(int slot)
        {
            bool ok = SaveSystem.Save(slot);
            ShowToast(ok ? $"Saved to slot {slot}" : "Save failed (see Console)");
            if (ok) SetPauseOpen(false);
            else RebuildSlots();
        }

        private void LoadFrom(int slot)
        {
            bool ok = SaveSystem.Load(slot);
            ShowToast(ok ? $"Loaded slot {slot}" : "Load failed (see Console)");
            if (ok) SetPauseOpen(false);
        }

        // Messages shown in the same frame (e.g. two animals arriving together) are combined
        private void ShowToast(string message)
        {
            toast.text = toastFrame == Time.frameCount && !toast.ClassListContains("hidden") ? toast.text + "\n" + message : message;
            toastFrame = Time.frameCount;
            toast.RemoveFromClassList("hidden");
            toastHideTime = Time.unscaledTime + 2.5f;
        }

        private static bool IsOpen(VisualElement overlay) => !overlay.ClassListContains("hidden");
    }
}
