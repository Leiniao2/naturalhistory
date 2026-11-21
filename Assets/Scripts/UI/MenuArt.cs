using System.Collections.Generic;
using System.Linq;
using NaturalHistory.Core;
using UnityEngine;

namespace NaturalHistory.UI
{
    // The paintings behind the title screen and the loading screen: public-domain paleoart listed in
    // Resources/UI/MainMenu/paintings.json (file, title, artist; sources in CREDITS.txt). They are
    // dealt from a shuffled deck kept in PlayerPrefs, so every one is shown before any comes back,
    // across sessions too.
    public static class MenuArt
    {
        [System.Serializable]
        public class Painting
        {
            public string file, title, artist, source;

            public Texture2D Load() => Resources.Load<Texture2D>($"UI/MainMenu/{file}");

            // "Painting: Charles R. Knight, Woolly Mammoths, public domain"
            public string Credit => Loc.F("Painting: {0}, {1}, public domain", artist, Loc.T(title));
        }

        [System.Serializable] private class Catalog { public List<Painting> paintings; }

        private const string DeckKey = "menuArtDeck"; // indices still to deal, comma-separated

        private static List<Painting> all;

        public static IReadOnlyList<Painting> All
        {
            get
            {
                if (all != null) return all;
                var asset = Resources.Load<TextAsset>("UI/MainMenu/paintings");
                all = asset != null ? JsonUtility.FromJson<Catalog>(asset.text)?.paintings : null;
                all ??= new List<Painting>();
                if (all.Count == 0) Debug.LogWarning("[MenuArt] Resources/UI/MainMenu/paintings.json is missing or empty.");
                return all;
            }
        }

        // The next painting from the deck; a new shuffled deck once it runs out (not starting with
        // the one just shown)
        public static Painting Next()
        {
            if (All.Count == 0) return null;
            var deck = PlayerPrefs.GetString(DeckKey, "").Split(',')
                .Select(s => int.TryParse(s, out int i) ? i : -1)
                .Where(i => i >= 0 && i < All.Count).ToList();
            if (deck.Count == 0)
            {
                int last = PlayerPrefs.GetInt(DeckKey + "Last", -1);
                deck = Enumerable.Range(0, All.Count).OrderBy(_ => Random.value).ToList();
                if (deck.Count > 1 && deck[0] == last) (deck[0], deck[^1]) = (deck[^1], deck[0]);
            }
            int next = deck[0];
            deck.RemoveAt(0);
            PlayerPrefs.SetString(DeckKey, string.Join(",", deck));
            PlayerPrefs.SetInt(DeckKey + "Last", next);
            PlayerPrefs.Save();
            return All[next];
        }
    }
}
