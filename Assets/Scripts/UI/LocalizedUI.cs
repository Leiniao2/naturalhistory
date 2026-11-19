using System.Collections.Generic;
using NaturalHistory.Core;
using UnityEngine;
using FontAsset = UnityEngine.TextCore.Text.FontAsset;
using UnityEngine.UIElements;

namespace NaturalHistory.UI
{
    // Translates the text written in GameMenus.uxml, and provides fonts that can show every
    // supported language (the default UI font has no Chinese, Japanese or Korean).
    public static class LocalizedUI
    {
        // English text of each UXML element, remembered so it can be translated again after the
        // language changes
        private static readonly Dictionary<VisualElement, string> texts  = new();
        private static readonly Dictionary<BaseField<string>, string> labels = new();
        private static readonly Dictionary<VisualElement, string> fieldLabels = new(); // sliders and toggles

        public static void Register(VisualElement root)
        {
            texts.Clear();
            labels.Clear();
            fieldLabels.Clear();
            root.Query<Slider>().ForEach(s => { if (!string.IsNullOrEmpty(s.label)) fieldLabels[s] = s.label; });
            root.Query<Toggle>().ForEach(t => { if (!string.IsNullOrEmpty(t.label)) fieldLabels[t] = t.label; });
            root.Query<TextElement>().ForEach(e => { if (!string.IsNullOrEmpty(e.text)) texts[e] = e.text; });
            root.Query<Foldout>().ForEach(f => { if (!string.IsNullOrEmpty(f.text)) texts[f] = f.text; });
            root.Query<DropdownField>().ForEach(d => { if (!string.IsNullOrEmpty(d.label)) labels[d] = d.label; });
            Apply();
        }

        public static void Apply()
        {
            foreach (var (element, english) in texts)
            {
                if (element is TextElement t) t.text = Loc.T(english);
                else if (element is Foldout f) f.text = Loc.T(english);
            }
            foreach (var (field, english) in labels) field.label = Loc.T(english);
            foreach (var (field, english) in fieldLabels)
            {
                if (field is Slider s) s.label = Loc.T(english);
                else if (field is Toggle t) t.label = Loc.T(english);
            }
        }

        // ---------- Fonts ----------

        // Installed fonts covering the CJK scripts, the one for the current language first so shared
        // characters (kanji / hanzi) are drawn in that language's style. Mac, Windows, Linux names.
        private static readonly Dictionary<string, string[]> cjkFonts = new()
        {
            ["zh"] = new[] { "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", "Heiti SC" },
            ["ja"] = new[] { "Hiragino Sans", "Hiragino Kaku Gothic ProN", "Yu Gothic", "Meiryo", "Noto Sans CJK JP" },
            ["ko"] = new[] { "Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans CJK KR" },
        };
        private static readonly string[] otherFonts = { "Arial", "Segoe UI", "Arial Unicode MS", "Apple Symbols", "Segoe UI Symbol" };

        private static readonly Dictionary<string, FontAsset> fontAssets = new();
        private static PanelTextSettings textSettings;

        // Fallback fonts for the menus, in the order for the current language
        public static void ApplyFonts(PanelSettings panelSettings)
        {
            if (textSettings == null)
            {
                textSettings = panelSettings.textSettings != null
                    ? Object.Instantiate(panelSettings.textSettings)
                    : ScriptableObject.CreateInstance<PanelTextSettings>();
                panelSettings.textSettings = textSettings;
            }
            textSettings.fallbackFontAssets ??= new List<FontAsset>();
            foreach (var asset in fontAssets.Values) textSettings.fallbackFontAssets.Remove(asset);
            int at = 0;
            foreach (var family in FontOrder())
            {
                var asset = OsFontAsset(family);
                if (asset != null) textSettings.fallbackFontAssets.Insert(at++, asset);
            }
        }

        private static IEnumerable<string> FontOrder()
        {
            var order = new List<string>();
            if (cjkFonts.TryGetValue(Loc.Current, out var mine)) order.AddRange(mine);
            foreach (var (lang, families) in cjkFonts)
                if (lang != Loc.Current) order.AddRange(families);
            order.AddRange(otherFonts);
            return order;
        }

        private static FontAsset OsFontAsset(string family)
        {
            if (fontAssets.TryGetValue(family, out var cached)) return cached;
            FontAsset asset = null;
            try { asset = FontAsset.CreateFontAsset(family, "Regular"); }
            catch (System.Exception) { }
            if (asset != null) asset.name = family;
            fontAssets[family] = asset; // null too, so a missing font is only looked up once
            return asset;
        }

        // Dynamic font for the world-space name tags (TextMesh), falling back across the installed
        // fonts so any language shows
        private static Font worldFont;
        private static string worldFontLanguage;
        public static Font WorldFont
        {
            get
            {
                if (worldFont == null || worldFontLanguage != Loc.Current)
                {
                    var names = new List<string> { "Arial" };
                    names.AddRange(FontOrder());
                    worldFont = Font.CreateDynamicFontFromOSFont(names.ToArray(), 48);
                    worldFontLanguage = Loc.Current;
                }
                return worldFont;
            }
        }
    }
}
