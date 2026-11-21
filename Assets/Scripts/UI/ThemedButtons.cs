using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;

namespace NaturalHistory.UI
{
    // The buttons of the three trees in their colours, wherever they are (HUD, the selected animal's
    // card, the Encyclopedia): Functions blue, Behaviors purple, Evolution green, each with its icon
    // (UiIcons). While there is something to do in that tree (an item that can be acquired, an
    // evolution that can be made) a glow swells and fades round the button.
    public static class ThemedButtons
    {
        public enum Theme { Functions, Behaviors, Evolution }

        private sealed class Entry
        {
            public Button button;
            public Theme theme;
            public Func<bool> ready;
            public bool lit;
        }

        private static readonly List<Entry> entries = new();
        private static IVisualElementScheduledItem pulse;
        private static float nextCheck;

        private static readonly Dictionary<Theme, Color> glow = new()
        {
            { Theme.Functions, new Color(0.55f, 0.80f, 1f) },
            { Theme.Behaviors, new Color(0.85f, 0.65f, 1f) },
            { Theme.Evolution, new Color(0.60f, 1f, 0.55f) },
        };

        public static Texture2D IconOf(Theme theme) => theme switch
        {
            Theme.Functions => UiIcons.Functions,
            Theme.Behaviors => UiIcons.Behaviors,
            _               => UiIcons.Evolve,
        };

        // Colours `button` for `theme`, puts the icon in front of its label, and lights it while
        // `ready` says there is something to do (null: never lit)
        public static void Apply(Button button, Theme theme, Func<bool> ready = null, Texture2D icon = null)
        {
            if (button == null) return;
            button.AddToClassList("themed-button");
            button.AddToClassList(theme switch { Theme.Functions => "theme-btn-functions", Theme.Behaviors => "theme-btn-behaviors", _ => "theme-btn-evolution" });
            UiIcons.Decorate(button, icon ?? IconOf(theme));
            entries.Add(new Entry { button = button, theme = theme, ready = ready });
            if (pulse == null) pulse = button.schedule.Execute(Pulse).Every(33);
        }

        private static void Pulse()
        {
            float now = Time.unscaledTime;
            if (now >= nextCheck) // what can be done changes slowly: look twice a second
            {
                nextCheck = now + 0.5f;
                foreach (var e in entries)
                {
                    bool lit = false;
                    try { lit = e.ready != null && e.button.panel != null && e.ready(); } catch (Exception) { }
                    if (!lit && e.lit) Unlight(e.button);
                    e.lit = lit;
                }
            }
            float t = 0.5f + 0.5f * Mathf.Sin(now * 4f);
            foreach (var e in entries)
            {
                if (!e.lit || e.button.resolvedStyle.display == DisplayStyle.None) continue;
                var c = glow[e.theme];
                var ring = new Color(c.r, c.g, c.b, Mathf.Lerp(0.35f, 1f, t));
                var b = e.button.style;
                b.borderTopColor = b.borderBottomColor = b.borderLeftColor = b.borderRightColor = ring;
                float w = Mathf.Lerp(2f, 4f, t);
                b.borderTopWidth = b.borderBottomWidth = b.borderLeftWidth = b.borderRightWidth = w;
            }
        }

        // Something in `tree` the species on show can acquire now
        public static bool TraitsReady(Progression.ProgressionTree tree)
        {
            var p = Progression.ProgressionManager.Instance;
            if (p == null || p.Species == null || tree == null) return false;
            foreach (var n in tree.Nodes) if (p.UnlockBlocker(tree, n) == null) return true;
            return false;
        }

        // One of `copies` can evolve now
        public static bool EvolutionReady(IEnumerable<Evolution.OwnedCopy> copies)
        {
            var evolution = Evolution.EvolutionManager.Instance;
            if (evolution == null || copies == null) return false;
            foreach (var c in copies)
                foreach (var link in Evolution.EvolutionData.From(c.species))
                    if (evolution.CanEvolve(link, c)) return true;
            return false;
        }

        private static Evolution.EvolutionManager Evo => Evolution.EvolutionManager.Instance;
        public static IEnumerable<Evolution.OwnedCopy> HumanCopies =>
            Evo == null ? new List<Evolution.OwnedCopy>() : Evo.CopiesOf(Players.PlayerManager.Instance?.Human);

        private static void Unlight(Button button)
        {
            var b = button.style;
            b.borderTopColor = b.borderBottomColor = b.borderLeftColor = b.borderRightColor = StyleKeyword.Null;
            b.borderTopWidth = b.borderBottomWidth = b.borderLeftWidth = b.borderRightWidth = StyleKeyword.Null;
        }
    }
}
