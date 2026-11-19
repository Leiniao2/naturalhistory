using System.Collections.Generic;
using NaturalHistory.Core;
using NaturalHistory.Progression;
using UnityEngine.UIElements;

namespace NaturalHistory.UI
{
    // The card for each discovery (Progression/Discoveries): what kind of thing it is, its name,
    // picture (an animal's painting) and introduction, and the reward it brought. Several found at
    // once come one after another; OK (or Enter / Esc) moves on.
    public class DiscoveryPanel
    {
        private readonly VisualElement overlay, picture;
        private readonly Label kind, title, text, reward;
        private readonly Queue<Discoveries.Discovery> queue = new();

        public bool IsOpen => !overlay.ClassListContains("hidden");

        public DiscoveryPanel(VisualElement root)
        {
            overlay = root.Q("discovery-overlay");
            picture = root.Q("discovery-picture");
            kind    = root.Q<Label>("discovery-kind");
            title   = root.Q<Label>("discovery-title");
            text    = root.Q<Label>("discovery-text");
            reward  = root.Q<Label>("discovery-reward");
            root.Q<Button>("discovery-ok-button").clicked += Next;
            if (Discoveries.Instance != null) Discoveries.Instance.Found += Show;
        }

        public void Dispose()
        {
            if (Discoveries.Instance != null) Discoveries.Instance.Found -= Show;
        }

        private void Show(Discoveries.Discovery d)
        {
            queue.Enqueue(d);
            if (!IsOpen) Next();
        }

        // The next card, or close when there are no more
        public void Next()
        {
            if (queue.Count == 0) { overlay.AddToClassList("hidden"); return; }
            var d = queue.Dequeue();
            kind.text = Loc.T(d.kind switch
            {
                Discoveries.Kind.Animal => "New animal discovered",
                Discoveries.Kind.Plant  => "New plant discovered",
                _                       => "New landscape discovered",
            });
            title.text  = d.title;
            text.text   = d.text;
            reward.text = string.IsNullOrEmpty(d.reward) ? "" : Loc.F("Reward: {0}", d.reward);
            picture.style.backgroundImage = d.picture is UnityEngine.Texture2D t ? Background.FromTexture2D(t) : new StyleBackground(StyleKeyword.None);
            picture.EnableInClassList("hidden", d.picture == null);
            overlay.RemoveFromClassList("hidden");
            overlay.BringToFront();
        }
    }
}
