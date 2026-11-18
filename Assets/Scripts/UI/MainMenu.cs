using System.Collections.Generic;
using NaturalHistory.Core;
using NaturalHistory.Save;
using UnityEngine;
using UnityEngine.UIElements;

namespace NaturalHistory.UI
{
    // The title screen the game opens on, like Civilization's or Humankind's: one of Charles R.
    // Knight's prehistoric murals (Resources/UI/MainMenu, public domain) fills the screen and slowly
    // pans across, darkened on the left behind the title and the same menu as the pause menu.
    // The HUD is hidden while it shows; New Game, Load Game and the Encyclopedia open over it
    // (GameMenus wires the buttons). The map behind it is not shown, and no map input gets through.
    public class MainMenu
    {
        private const float PanSeconds = 90f; // one sweep across the painting and back

        // Painting, its title and where it hangs, for the credit line
        private static readonly (string file, string title)[] Paintings =
        {
            ("early_land_plants",         "Early Land Plants"),
            ("permian_reptiles",          "Permian Reptiles and Amphibians"),
            ("cretaceous_seas",           "Late Cretaceous Seas"),
            ("triceratops_tyrannosaurus", "Triceratops and Tyrannosaurus"),
        };

        private readonly VisualElement root, menu, art;
        private readonly Label credit;
        private readonly Button continueButton;
        private readonly List<(VisualElement element, StyleEnum<DisplayStyle> display)> hiddenHud = new();
        private Texture2D painting;
        private string paintingTitle;
        private float shownAt;

        public bool IsOpen => menu != null && !menu.ClassListContains("hidden");

        // A game has been started or loaded this session: Continue goes back to it
        public bool InGame { get; set; }

        public Button Continue => continueButton;
        public Button NewGame      => root.Q<Button>("main-new-game-button");
        public Button LoadGame     => root.Q<Button>("main-load-button");
        public Button Encyclopedia => root.Q<Button>("main-encyclopedia-button");
        public Button Quit         => root.Q<Button>("main-quit-button");

        public MainMenu(VisualElement root)
        {
            this.root = root;
            menu = root.Q("main-menu");
            if (menu == null) return;
            art    = root.Q("main-menu-art");
            credit = root.Q<Label>("main-menu-credit");
            continueButton = root.Q<Button>("main-continue-button");
            root.Q("main-menu-shade").style.backgroundImage = new StyleBackground(Shade());
            Loc.Changed += RefreshText;
        }

        public void Dispose() => Loc.Changed -= RefreshText;

        public void Show()
        {
            if (menu == null) return;
            if (painting == null) PickPainting();
            // Everything but the overlays (new game, load, encyclopedia...) steps aside
            hiddenHud.Clear();
            foreach (var child in menu.parent.Children()) // GameMenus.uxml's root: the HUD and the overlays
            {
                if (child == menu || child.ClassListContains("overlay")) continue;
                hiddenHud.Add((child, child.style.display));
                child.style.display = DisplayStyle.None;
            }
            menu.RemoveFromClassList("hidden");
            shownAt = Time.unscaledTime;
            RefreshText();
        }

        public void Hide()
        {
            if (!IsOpen) return;
            menu.AddToClassList("hidden");
            foreach (var (element, display) in hiddenHud) element.style.display = display;
            hiddenHud.Clear();
        }

        // Continue: the most recently saved game, if there is one
        public int LatestSlot()
        {
            int best = -1;
            System.DateTime when = System.DateTime.MinValue;
            for (int slot = 1; slot <= SaveSystem.SlotCount; slot++)
            {
                var data = SaveSystem.Peek(slot);
                if (data != null && data.SavedAt > when) { when = data.SavedAt; best = slot; }
            }
            return best;
        }

        private void RefreshText()
        {
            if (menu == null) return;
            continueButton.SetEnabled(InGame || LatestSlot() > 0);
            credit.text = paintingTitle == null ? "" :
                Loc.F("Painting: Charles R. Knight, {0} (Field Museum, 1926–1930), public domain", Loc.T(paintingTitle));
        }

        private void PickPainting()
        {
            var (file, title) = Paintings[Random.Range(0, Paintings.Length)];
            painting = Resources.Load<Texture2D>($"UI/MainMenu/{file}");
            paintingTitle = painting != null ? title : null;
            if (painting != null) art.style.backgroundImage = new StyleBackground(painting);
        }

        // Called every frame by GameMenus: the painting covers the screen at its own proportions and
        // pans slowly from one end to the other and back, easing at the ends
        public void Update()
        {
            if (!IsOpen || painting == null) return;
            float w = menu.resolvedStyle.width, h = menu.resolvedStyle.height;
            if (float.IsNaN(w) || float.IsNaN(h) || w <= 0f || h <= 0f) return;
            float aspect = (float)painting.width / painting.height;
            float artH = Mathf.Max(h, w / aspect), artW = artH * aspect;
            float t = (Time.unscaledTime - shownAt) / PanSeconds;
            float along = 0.5f - 0.5f * Mathf.Cos(t * Mathf.PI * 2f);
            art.style.width  = artW;
            art.style.height = artH;
            art.style.left   = -(artW - w) * along;
            art.style.top    = -(artH - h) * 0.5f;
        }

        // Dark on the left, behind the title and menu, clearing toward the middle of the painting
        private static Texture2D Shade()
        {
            const int size = 256;
            var tex = new Texture2D(size, 1, TextureFormat.RGBA32, false) { wrapMode = TextureWrapMode.Clamp, name = "MainMenuShade" };
            var pixels = new Color[size];
            for (int x = 0; x < size; x++)
            {
                float f = x / (size - 1f);
                float a = Mathf.Lerp(0.86f, 0f, Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(0.18f, 0.62f, f)));
                pixels[x] = new Color(0.04f, 0.05f, 0.04f, a);
            }
            tex.SetPixels(pixels);
            tex.Apply(false);
            return tex;
        }
    }
}
