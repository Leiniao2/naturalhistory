using System;
using System.Collections.Generic;
using UnityEngine;

namespace NaturalHistory.Core
{
    // Game text translation. The English text is the key: everything shown on screen goes through
    // Loc.T("End Turn") or Loc.F("Turn {0}", turn), and data names too (Loc.T(age.displayName)).
    // Translations live in Resources/Localization/<code>.json; text missing there stays English.
    public static class Loc
    {
        public static readonly (string code, string name)[] Languages =
        {
            ("en", "English"),
            ("zh", "中文"),
            ("ja", "日本語"),
            ("ko", "한국어"),
            ("fr", "Français"),
            ("it", "Italiano"),
            ("es", "Español"),
            ("pt", "Português"),
            ("ru", "Русский"),
            ("de", "Deutsch"),
        };

        private const string PrefKey = "language";

        public static event Action Changed;

        public static string Current
        {
            get { EnsureLoaded(); return current; }
        }

        private static string current;
        private static Dictionary<string, string> table;

        public static string T(string english)
        {
            if (string.IsNullOrEmpty(english)) return english;
            EnsureLoaded();
            return table != null && table.TryGetValue(english, out var text) && !string.IsNullOrEmpty(text) ? text : english;
        }

        // English format string with {0}, {1}... placeholders, translated then filled in
        public static string F(string englishFormat, params object[] args)
        {
            var format = T(englishFormat);
            try { return string.Format(format, args); }
            catch (FormatException) { return string.Format(englishFormat, args); } // a broken translation
        }

        public static void SetLanguage(string code)
        {
            if (Array.FindIndex(Languages, l => l.code == code) < 0) code = "en";
            if (code == current && table != null) return;
            PlayerPrefs.SetString(PrefKey, code);
            PlayerPrefs.Save();
            Load(code);
            Changed?.Invoke();
        }

        private static void EnsureLoaded()
        {
            if (current != null) return;
            Load(PlayerPrefs.GetString(PrefKey, FromSystem()));
        }

        private static void Load(string code)
        {
            current = code;
            table = new Dictionary<string, string>();
            if (code == "en") return;
            var asset = Resources.Load<TextAsset>($"Localization/{code}");
            if (asset == null) { Debug.LogWarning($"[Loc] Resources/Localization/{code}.json not found."); return; }
            var file = JsonUtility.FromJson<LocFile>(asset.text);
            if (file?.entries == null) return;
            foreach (var e in file.entries)
                if (!string.IsNullOrEmpty(e.k)) table[e.k] = e.v;
        }

        private static string FromSystem() => Application.systemLanguage switch
        {
            SystemLanguage.Chinese or SystemLanguage.ChineseSimplified or SystemLanguage.ChineseTraditional => "zh",
            SystemLanguage.Japanese   => "ja",
            SystemLanguage.Korean     => "ko",
            SystemLanguage.French     => "fr",
            SystemLanguage.Italian    => "it",
            SystemLanguage.Spanish    => "es",
            SystemLanguage.Portuguese => "pt",
            SystemLanguage.Russian    => "ru",
            SystemLanguage.German     => "de",
            _                         => "en",
        };

        [Serializable] private class LocEntry { public string k; public string v; }
        [Serializable] private class LocFile { public List<LocEntry> entries; }
    }
}
