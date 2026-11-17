using System.Collections.Generic;
using NaturalHistory.Data;
using NaturalHistory.Evolution;
using UnityEngine;

namespace NaturalHistory.World
{
    // How furry a species' model is drawn (the MapFeature shader's _Fur): fine strands combed down
    // and back, tufted clumps, a soft sheen at the silhouette and light that wraps round the body
    // instead of the smooth plastic shading. Mammals and the hairy cynodonts get it; the naked or
    // armoured mammals (whales, sirenians, elephants, most rhinos, glyptodonts) little or none.
    public static class AnimalFur
    {
        public static readonly int FurId = Shader.PropertyToID("_Fur");

        // Strands along the body's length; the shader fades them out where they'd be finer than a pixel
        private const float StrandsPerLength = 70f;

        // Groups with no or little hair (0 = none)
        private static readonly Dictionary<string, float> groupFur = new()
        {
            { "Archaeocete whale", 0f }, { "Baleen whale", 0f }, { "Toothed whale", 0f }, { "Oceanic dolphin", 0f },
            { "Sirenian", 0f }, { "Glyptodont", 0f }, { "Desmostylian", 0.3f },
            { "Proboscidean", 0.25f }, { "Rhinocerotoid", 0.25f }, { "Embrithopod", 0.2f }, { "Dinocerate", 0.3f },
            { "Brontothere", 0.35f }, { "Notoungulate", 0.4f }, { "Pantodont", 0.4f }, { "Entelodont", 0.6f },
            { "Cynodont therapsid", 0.7f },
        };

        // Species that differ from their group: the Ice Age's woolly giants, the land-walking first whale
        private static readonly Dictionary<string, float> speciesFur = new()
        {
            { "woolly_mammoth", 1.25f }, { "coelodonta_antiquitatis", 1.25f }, { "elasmotherium_sibiricum", 0.9f },
            { "pakicetus_attocki", 0.8f }, { "ambulocetus_natans", 0.4f },
        };

        // (amount 0..1.25, strands per model unit); amount 0 = no fur
        public static Vector4 Of(SpeciesDefinition def, Mesh mesh)
        {
            float amount = Amount(def);
            if (amount <= 0f || mesh == null) return Vector4.zero;
            float length = Mathf.Max(mesh.bounds.size.x, mesh.bounds.size.y, mesh.bounds.size.z, 1e-4f);
            return new Vector4(amount, StrandsPerLength / length, 0f, 0f);
        }

        public static float Amount(SpeciesDefinition def)
        {
            if (def == null) return 0f;
            if (speciesFur.TryGetValue(def.id, out float f)) return f;
            if (def.group != null && groupFur.TryGetValue(def.group, out f)) return f;
            return System.Linq.Enumerable.Contains(EvolutionData.TagsOf(def), "Mammal") ? 1f : 0f;
        }
    }
}
