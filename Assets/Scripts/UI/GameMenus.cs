using NaturalHistory.Climate;
using NaturalHistory.Core;
using NaturalHistory.Data;
using NaturalHistory.Evolution;
using NaturalHistory.Players;
using NaturalHistory.Progression;
using NaturalHistory.Save;
using NaturalHistory.World;
using UnityEngine;
using UnityEngine.UIElements;

namespace NaturalHistory.UI
{
    // In-game UI Toolkit menus: HUD buttons, pause menu (Esc), save/load slots and the
    // Functions / Behaviors tree panels, the selected animal's card, the Evolution Tree (ZoologyPanel) and the Encyclopedia. Layout: Resources/UI/GameMenus.uxml, styles: GameMenusStyle.uss.
    public class GameMenus : MonoBehaviour
    {
        private UIDocument document;
        private VisualElement root, pauseOverlay, slotsOverlay, slotList;
        private Label epLabel, slotsTitle, toast;
        private TreePanel treePanel;
        private AgePanel agePanel;
        private ClimateHud climateHud;
        private PlayersPanel playersPanel;
        private AdminPanel adminPanel;
        private UnitPanel unitPanel;
        private UnitCycle unitCycle;
        private AnimalPanel animalPanel;
        private NewGameOptions newGameOptions;
        private ZoologyPanel zoologyPanel;
        private EncyclopediaPanel encyclopedia;
        private MiniMap miniMap;
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

            // Panel settings come from an asset made in the editor (Editor/PanelSettingsAsset), copied so
            // the fonts set below don't change it: only that carries the ICU data text shaping needs,
            // and without it a build draws no text at all. The object starts inactive so the
            // UIDocument is fully configured before it enables.
            var asset = Resources.Load<PanelSettings>("UI/NHPanelSettings");
            if (asset == null) Debug.LogError("[GameMenus] Missing Resources/UI/NHPanelSettings: menu text won't show in builds");
            var panelSettings = asset != null ? Instantiate(asset) : ScriptableObject.CreateInstance<PanelSettings>();
            panelSettings.themeStyleSheet     = Resources.Load<ThemeStyleSheet>("UI/NHRuntimeTheme");
            panelSettings.scaleMode           = PanelScaleMode.ScaleWithScreenSize;
            panelSettings.referenceResolution = new Vector2Int(1920, 1080);
            panelSettings.match               = 0.5f;
            LocalizedUI.ApplyFonts(panelSettings);

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
            LocalizedUI.Register(root); // before the panels fill in their own text

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
            adminPanel   = new AdminPanel(root);
            unitPanel    = new UnitPanel(root);
            unitCycle    = new UnitCycle(root);
            animalPanel  = new AnimalPanel(root);
            newGameOptions = new NewGameOptions(root);
            zoologyPanel = new ZoologyPanel(root);
            encyclopedia = new EncyclopediaPanel(root);
            miniMap      = new MiniMap(root);
            CameraController.IsPointerOverUI = PointerOverUI;
            unitPanel.OpenTree   += tree => { CloseSidePanels(); treePanel.Open(tree); };
            unitPanel.OpenEvolve += copy => { CloseSidePanels(); zoologyPanel.Open(copy); };
            unitPanel.Message    += ShowToast;
            zoologyPanel.Message += ShowToast;
            zoologyPanel.OpenEncyclopedia += id => { CloseSidePanels(); encyclopedia.Open(id); };
            encyclopedia.OpenTree         += id => { CloseSidePanels(); zoologyPanel.Open(start: id); };
            NaturalEvents.Announced += OnPhenomenon;
            Combat.Reported += OnPhenomenon;
            playersPanel.NewGameStarted += () => { SetPauseOpen(false); ShowToast(Loc.T("New game started")); };
            playersPanel.SetupClosed    += () => pauseOverlay.RemoveFromClassList("hidden");

            root.Q<Button>("morphology-button").clicked += () => ToggleTree(Progression?.Morphology);
            root.Q<Button>("ethology-button").clicked   += () => ToggleTree(Progression?.Ethology);
            root.Q<Button>("zoology-button").clicked    += ToggleZoology;
            layerButtons = new[]
            {
                (root.Q<Button>("sky-button"),     MapLayer.Sky),
                (root.Q<Button>("surface-button"), MapLayer.Surface),
                (root.Q<Button>("under-button"),   MapLayer.Under),
            };
            foreach (var (button, layer) in layerButtons) button.clicked += () => UnderView.Set(layer);
            UnderView.Changed   += OnUnderViewChanged;
            OnUnderViewChanged();
            root.Q<Button>("menu-button").clicked       += () => SetPauseOpen(true);
            root.Q<Button>("resume-button").clicked     += () => SetPauseOpen(false);
            root.Q<Button>("encyclopedia-button").clicked += () => { SetPauseOpen(false); encyclopedia.Open(); };
            root.Q<Button>("new-game-button").clicked   += OpenNewGame;
            root.Q<Button>("save-button").clicked       += () => OpenSlots(saving: true);
            root.Q<Button>("load-button").clicked       += () => OpenSlots(saving: false);
            root.Q<Button>("quit-button").clicked       += Quit;
            root.Q<Button>("slots-back-button").clicked += CloseSlots;
            root.Q<Button>("age-button").clicked        += ToggleAges;
            SetUpLanguageDropdown();
            Loc.Changed += OnLanguageChanged;

            cellSelector     = FindAnyObjectByType<CellSelector>();
            cameraController = FindAnyObjectByType<CameraController>();

            if (Progression != null) Progression.Changed += OnProgressionChanged;
            if (Progression != null) Progression.Earned += ShowToast;
            if (EvolutionManager.Instance != null) EvolutionManager.Instance.Changed += OnProgressionChanged;
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

        private void OnPhenomenon(string message, HexCell cell) => ShowToast(message);

        // The layer switch over the minimap: sky, surface, underground; the one shown is lit
        private (Button button, MapLayer layer)[] layerButtons;
        private void OnUnderViewChanged()
        {
            foreach (var (button, layer) in layerButtons)
            {
                button.text = Loc.T(layer switch { MapLayer.Sky => "Sky", MapLayer.Under => "Underground", _ => "Surface" });
                button.EnableInClassList("selected", layer == UnderView.Layer);
                button.SetEnabled(layer == MapLayer.Under || UnderView.SurfaceOpen); // Ediacaran: under only
            }
        }

        // ---------- Language ----------

        private void SetUpLanguageDropdown()
        {
            var dropdown = root.Q<DropdownField>("language-dropdown");
            if (dropdown == null) return;
            dropdown.choices = new System.Collections.Generic.List<string>();
            foreach (var (_, name) in Loc.Languages) dropdown.choices.Add(name);
            dropdown.index = System.Array.FindIndex(Loc.Languages, l => l.code == Loc.Current);
            dropdown.RegisterValueChangedCallback(_ =>
            {
                if (dropdown.index >= 0) Loc.SetLanguage(Loc.Languages[dropdown.index].code);
            });
        }

        // Everything showing text is filled in again in the new language
        private void OnLanguageChanged()
        {
            LocalizedUI.ApplyFonts(document.panelSettings);
            LocalizedUI.Apply();
            OnUnderViewChanged();
            playersPanel.RefreshBar();
            OnProgressionChanged();
            OnClimateUpdated();
            if (IsOpen(slotsOverlay)) OpenSlots(slotsAreForSaving);
        }

        private void OnDestroy()
        {
            UnderView.Changed -= OnUnderViewChanged;
            Loc.Changed -= OnLanguageChanged;
            miniMap?.Dispose();
            CameraController.IsPointerOverUI = null;
            NaturalEvents.Announced -= OnPhenomenon;
            Combat.Reported -= OnPhenomenon;
            if (Progression != null) Progression.Changed -= OnProgressionChanged;
            if (Progression != null) Progression.Earned -= ShowToast;
            if (EvolutionManager.Instance != null) EvolutionManager.Instance.Changed -= OnProgressionChanged;
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
            var bonus = animal.bonusEvolutionPoints > 0 ? Loc.F(" (+{0} EP)", animal.bonusEvolutionPoints) : "";
            ShowToast(Loc.F("{0}: {1} appears{2}", player.Name, Loc.T(animal.name), bonus));
        }

        // Fires after every turn (date → climate) and after loading
        private void OnClimateUpdated()
        {
            climateHud.Refresh();
            adminPanel.Refresh();
            if (agePanel.IsOpen) agePanel.Refresh();
        }

        private void OnAgeTransition(GeologicalAge from, GeologicalAge to)
        {
            treePanel.Close();
            zoologyPanel.Close();
            encyclopedia.Close();
            playersPanel.CloseFaction();
            agePanel.Open(newAge: true);
        }

        private void ToggleAges()
        {
            if (agePanel.IsOpen) { agePanel.Close(); return; }
            treePanel.Close();
            zoologyPanel.Close();
            encyclopedia.Close();
            playersPanel.CloseFaction();
            agePanel.Open();
        }

        private void Update()
        {
            if (root == null) return;

            if (Input.GetKeyDown(KeyCode.Escape)) HandleEscape();
            if (Input.GetKeyDown(KeyCode.BackQuote)) adminPanel.Toggle();
            if (Input.GetKeyDown(KeyCode.U) && !AnyModalOpen()) UnderView.Toggle();    // the layer under sea level
            if (Input.GetKeyDown(KeyCode.K) && !AnyModalOpen()) UnderView.ToggleSky(); // the sky layer
            if (Input.GetKeyDown(KeyCode.Tab) && !AnyModalOpen()) SpeciesColonies.Instance?.CycleFocus(); // the selected tile's next animal
            if ((Input.GetKeyDown(KeyCode.Return) || Input.GetKeyDown(KeyCode.KeypadEnter)) && !AnyModalOpen())
                ClimateHud.EndTurn(Input.GetKey(KeyCode.LeftShift) || Input.GetKey(KeyCode.RightShift));
            climateHud.RefreshTile();
            unitPanel.Update();
            unitCycle.Update(AnyModalOpen());
            animalPanel.Update();
            miniMap.Update();
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
            else if (encyclopedia.IsOpen) encyclopedia.Close();
            else if (zoologyPanel.IsOpen) zoologyPanel.Close();
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

        private bool AnyModalOpen() => IsOpen(pauseOverlay) || IsOpen(slotsOverlay) || treePanel.IsOpen || agePanel.IsOpen || zoologyPanel.IsOpen || encyclopedia.IsOpen
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
            if (epLabel != null && Progression != null) epLabel.text = Loc.F("EP {0} (+{1})", Progression.EvolutionPoints, Progression.Income);
            if (treePanel != null && treePanel.IsOpen) treePanel.Refresh();
            if (zoologyPanel != null && zoologyPanel.IsOpen) zoologyPanel.Refresh();
        }

        // ---------- Trees ----------

        // Panels that replace each other in the middle of the screen
        private void CloseSidePanels()
        {
            treePanel.Close();
            agePanel.Close();
            zoologyPanel.Close();
            encyclopedia.Close();
            playersPanel.CloseFaction();
        }

        private void ToggleZoology()
        {
            if (zoologyPanel.IsOpen) { zoologyPanel.Close(); return; }
            CloseSidePanels();
            zoologyPanel.Open();
        }

        private void ToggleTree(ProgressionTree tree)
        {
            if (tree == null) return;
            zoologyPanel.Close();
            encyclopedia.Close();
            agePanel.Close();
            playersPanel.CloseFaction();
            if (treePanel.IsOpen && treePanel.CurrentTree == tree) treePanel.Close();
            else treePanel.Open(tree);
        }

        // ---------- Pause menu ----------

        private void SetPauseOpen(bool open)
        {
            if (open) CloseSidePanels();
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
            slotsTitle.text = Loc.T(saving ? "Save Game" : "Load Game");
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
                info.Add(new Label(Loc.F("Slot {0}", slot)).WithClass("slot-name"));
                info.Add(new Label(Describe(data)).WithClass("slot-detail"));
                row.Add(info);

                int captured = slot;
                if (slotsAreForSaving)
                {
                    row.Add(new Button(() => SaveTo(captured)) { text = Loc.T(data == null ? "Save" : "Overwrite") }.WithClass("slot-button"));
                }
                else if (data != null)
                {
                    row.Add(new Button(() => LoadFrom(captured)) { text = Loc.T("Load") }.WithClass("slot-button"));
                    row.Add(new Button(() => { SaveSystem.Delete(captured); RebuildSlots(); }) { text = Loc.T("Delete") }
                        .WithClass("slot-button").WithClass("danger"));
                }
                slotList.Add(row);
            }
        }

        private static string Describe(SaveData data)
        {
            if (data == null) return Loc.T("Empty");
            var when = data.SavedAt.ToString("yyyy-MM-dd HH:mm");
            var turn = data.turn > 0 ? "  ·  " + Loc.F("Turn {0}", data.turn) : "";
            var age  = string.IsNullOrEmpty(data.age) ? "" : $"  ·  {AgeName(data.age)}";
            var human   = data.players?.Find(p => p.human);
            var players = data.players is { Count: > 0 } ? "  ·  " + Loc.F("{0} + {1} AI", human?.name ?? "?", data.players.Count - 1) : "";
            return $"{when}{turn}{age}{players}  ·  " + Loc.F("{0} EP", data.evolutionPoints);
        }

        private static string AgeName(string id) => Loc.T(GameDataLoader.GetAge(id)?.displayName ?? id);

        private void SaveTo(int slot)
        {
            bool ok = SaveSystem.Save(slot);
            ShowToast(ok ? Loc.F("Saved to slot {0}", slot) : Loc.T("Save failed (see Console)"));
            if (ok) SetPauseOpen(false);
            else RebuildSlots();
        }

        private void LoadFrom(int slot)
        {
            bool ok = SaveSystem.Load(slot);
            ShowToast(ok ? Loc.F("Loaded slot {0}", slot) : Loc.T("Load failed (see Console)"));
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
