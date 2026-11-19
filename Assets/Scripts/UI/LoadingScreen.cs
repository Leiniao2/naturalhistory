using System;
using System.Collections;
using System.Linq;
using NaturalHistory.Core;
using NaturalHistory.Data;
using UnityEngine;
using UnityEngine.UIElements;

namespace NaturalHistory.UI
{
    // Shown while a new world is made or a saved game is loaded (both take a few seconds on the
    // main thread): one of the title screen's murals behind a dark veil, what is happening, and a
    // species to read about meanwhile (its painting, name, period and the start of its description).
    // Run puts it up, lets it be drawn, then does the work, then takes it down.
    public class LoadingScreen
    {
        private static readonly string[] Paintings = { "early_land_plants", "permian_reptiles", "cretaceous_seas", "triceratops_tyrannosaurus" };

        private readonly VisualElement overlay, art, portrait;
        private readonly Label title, speciesName, speciesMeta, speciesText;
        private readonly MonoBehaviour host;
        private bool running;

        public bool IsOpen => !overlay.ClassListContains("hidden");

        public LoadingScreen(VisualElement root, MonoBehaviour host)
        {
            this.host   = host;
            overlay     = root.Q("loading-overlay");
            art         = root.Q("loading-art");
            portrait    = root.Q("loading-portrait");
            title       = root.Q<Label>("loading-title");
            speciesName = root.Q<Label>("loading-species-name");
            speciesMeta = root.Q<Label>("loading-species-meta");
            speciesText = root.Q<Label>("loading-species-text");
        }

        // titleKey: e.g. "Creating the world…"; work runs once the screen is on display
        public void Run(string titleKey, Action work)
        {
            if (running) return;
            host.StartCoroutine(Show(titleKey, work));
        }

        private IEnumerator Show(string titleKey, Action work)
        {
            running = true;
            title.text = Loc.T(titleKey);
            var rng = new System.Random();
            var tex = Resources.Load<Texture2D>("UI/MainMenu/" + Paintings[rng.Next(Paintings.Length)]);
            art.style.backgroundImage = tex != null ? new StyleBackground(tex) : new StyleBackground(StyleKeyword.None);
            ShowSpecies(rng);
            overlay.RemoveFromClassList("hidden");
            overlay.BringToFront();
            // two frames, so the screen is really on display before the main thread is busy
            yield return null;
            yield return new WaitForEndOfFrame();
            yield return null;
            try { work(); }
            catch (Exception e) { Debug.LogException(e); }
            yield return null; // the map's groups and territory settle in the frame after
            overlay.AddToClassList("hidden");
            running = false;
        }

        private void ShowSpecies(System.Random rng)
        {
            var all = GameDataLoader.Species?.Where(s => SpeciesPortraits.Painting(s) != null).ToList();
            if (all == null || all.Count == 0) { portrait.style.backgroundImage = new StyleBackground(StyleKeyword.None); return; }
            var def = all[rng.Next(all.Count)];
            portrait.style.backgroundImage = Background.FromTexture2D(SpeciesPortraits.Painting(def));
            speciesName.text = Loc.T(def.commonName);
            var span = string.IsNullOrEmpty(def.lastAge) ? Loc.F("{0} – today", Loc.T(def.firstAge))
                     : def.firstAge == def.lastAge ? Loc.T(def.firstAge) : $"{Loc.T(def.firstAge)} – {Loc.T(def.lastAge)}";
            speciesMeta.text = $"{def.scientificName}  ·  {span}";
            var text = Loc.T(def.description ?? "");
            speciesText.text = text.Length > 320 ? text.Substring(0, 320).TrimEnd() + "…" : text;
        }
    }
}
