using System;
using System.Collections;
using System.Linq;
using NaturalHistory.Core;
using NaturalHistory.Data;
using UnityEngine;
using UnityEngine.UIElements;

namespace NaturalHistory.UI
{
    // Shown while a new world is made or a saved game is loaded (both take a few seconds): one of
    // the title screen's murals behind a dark veil, what is happening, and a species to read about
    // meanwhile (its painting, name, period and the start of its description), with Previous / Next
    // to browse others. Run puts it up, lets it be drawn, then does the work in steps that give the
    // frame back now and then (so the window stays responsive and the species can be browsed
    // meanwhile), then waits for Continue so the player can go on reading, and takes it down.
    // Keys: ← / → browse, Enter or Space continues.
    public class LoadingScreen
    {
        private static readonly string[] Paintings = { "early_land_plants", "permian_reptiles", "cretaceous_seas", "triceratops_tyrannosaurus" };

        private readonly VisualElement overlay, art, portrait;
        private readonly Label title, speciesName, speciesMeta, speciesText;
        private readonly MonoBehaviour host;
        private readonly Button prev, next, continueButton;
        private bool running, working, waiting;
        private System.Collections.Generic.List<SpeciesDefinition> order; // shuffled, browsed with Previous / Next
        private int index;

        public bool IsOpen => !overlay.ClassListContains("hidden");
        public event Action Closed; // the map is on show again (messages held back meanwhile can go out)

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
            prev           = root.Q<Button>("loading-prev");
            next           = root.Q<Button>("loading-next");
            continueButton = root.Q<Button>("loading-continue");
            prev.clicked           += () => Browse(-1);
            next.clicked           += () => Browse(+1);
            continueButton.clicked += () => waiting = false;
        }

        // Keys while it is up (GameMenus.Update has no other use for them then)
        public void HandleKeys()
        {
            if (!IsOpen || !(working || waiting)) return;
            if (Input.GetKeyDown(KeyCode.RightArrow)) Browse(+1);
            if (Input.GetKeyDown(KeyCode.LeftArrow))  Browse(-1);
            if (waiting && (Input.GetKeyDown(KeyCode.Return) || Input.GetKeyDown(KeyCode.KeypadEnter) || Input.GetKeyDown(KeyCode.Space)))
                waiting = false;
        }

        // titleKey: e.g. "Creating the world…"; work runs once the screen is on display
        public void Run(string titleKey, Action work) => Run(titleKey, () => Once(work));

        // work in steps: each yield gives the frame back
        public void Run(string titleKey, Func<IEnumerator> work)
        {
            if (running) return;
            host.StartCoroutine(Show(titleKey, work));
        }

        private static IEnumerator Once(Action work) { work(); yield break; }

        private IEnumerator Show(string titleKey, Func<IEnumerator> work)
        {
            running = true;
            title.text = Loc.T(titleKey);
            var rng = new System.Random();
            var tex = Resources.Load<Texture2D>("UI/MainMenu/" + Paintings[rng.Next(Paintings.Length)]);
            art.style.backgroundImage = tex != null ? new StyleBackground(tex) : new StyleBackground(StyleKeyword.None);
            // (portraits are loaded one at a time as they are shown: loading all of them here would stall the game)
            order = GameDataLoader.Species?.Where(s => !string.IsNullOrEmpty(s.model)).OrderBy(_ => rng.Next()).ToList();
            index = 0;
            ShowSpecies();
            continueButton.AddToClassList("hidden");
            prev.RemoveFromClassList("hidden");
            next.RemoveFromClassList("hidden");
            overlay.RemoveFromClassList("hidden");
            overlay.BringToFront();
            // two frames, so the screen is really on display before the main thread is busy
            yield return null;
            yield return new WaitForEndOfFrame();
            yield return null;
            working = true;
            IEnumerator steps = null;
            while (true)
            {
                try
                {
                    steps ??= work();
                    if (!steps.MoveNext()) break;
                }
                catch (Exception e) { Debug.LogException(e); break; }
                yield return null;
            }
            working = false;
            yield return null; // the map's groups and territory settle in the frame after
            // ready: the player can read on, and goes in with Continue
            title.text = Loc.T("Ready");
            continueButton.RemoveFromClassList("hidden");
            waiting = true;
            while (waiting) yield return null;
            overlay.AddToClassList("hidden");
            Closed?.Invoke();
            running = false;
        }

        private void Browse(int step)
        {
            if (order == null || order.Count == 0) return;
            index = ((index + step) % order.Count + order.Count) % order.Count;
            ShowSpecies();
        }

        private void ShowSpecies()
        {
            if (order == null || order.Count == 0) { portrait.style.backgroundImage = new StyleBackground(StyleKeyword.None); return; }
            var def = order[index];
            var painting = SpeciesPortraits.Painting(def);
            portrait.style.backgroundImage = painting != null ? Background.FromTexture2D(painting) : new StyleBackground(StyleKeyword.None);
            speciesName.text = Loc.T(def.commonName);
            var span = string.IsNullOrEmpty(def.lastAge) ? Loc.F("{0} – today", Loc.T(def.firstAge))
                     : def.firstAge == def.lastAge ? Loc.T(def.firstAge) : $"{Loc.T(def.firstAge)} – {Loc.T(def.lastAge)}";
            speciesMeta.text = $"{def.scientificName}  ·  {span}";
            var text = Loc.T(def.description ?? "");
            speciesText.text = text.Length > 320 ? text.Substring(0, 320).TrimEnd() + "…" : text;
        }
    }
}
