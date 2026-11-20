using System.Collections.Generic;
using UnityEngine;

namespace NaturalHistory.UI
{
    // The paintings of the Functions and Behaviors items, shown on their cards in the trees
    // (TreePanel): Resources/TraitIcons/Functions/<id> and Resources/TraitIcons/Behaviors/<id>
    // (generated in Google Flow, tools/trait_icons). Null while an item has none yet.
    public static class TraitIcons
    {
        private static readonly Dictionary<string, Texture2D> cache = new();

        public static Texture2D Get(bool function, string id)
        {
            if (string.IsNullOrEmpty(id)) return null;
            string path = (function ? "TraitIcons/Functions/" : "TraitIcons/Behaviors/") + id;
            if (cache.TryGetValue(path, out var known)) return known;
            var image = Resources.Load<Texture2D>(path);
            cache[path] = image;
            return image;
        }
    }
}
