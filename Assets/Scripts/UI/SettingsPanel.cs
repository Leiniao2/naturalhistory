using System;
using NaturalHistory.Core;
using UnityEngine.UIElements;

namespace NaturalHistory.UI
{
    // The Settings panel, opened from the title screen and the pause menu: the language, the master,
    // music and sound effects volumes and fullscreen (UserSettings). Back (or Esc) returns to the
    // menu it was opened from.
    public class SettingsPanel
    {
        private readonly VisualElement overlay;
        private readonly DropdownField language;
        private readonly Slider master, music, effects;
        private readonly Toggle fullscreen;

        public event Action Closed;

        public bool IsOpen => !overlay.ClassListContains("hidden");

        public SettingsPanel(VisualElement root)
        {
            overlay    = root.Q("settings-overlay");
            language   = root.Q<DropdownField>("language-dropdown");
            master     = root.Q<Slider>("master-volume");
            music      = root.Q<Slider>("music-volume");
            effects    = root.Q<Slider>("effects-volume");
            fullscreen = root.Q<Toggle>("fullscreen-toggle");

            language.choices = new System.Collections.Generic.List<string>();
            foreach (var (_, name) in Loc.Languages) language.choices.Add(name);
            language.RegisterValueChangedCallback(_ =>
            {
                if (language.index >= 0) Loc.SetLanguage(Loc.Languages[language.index].code);
            });
            master.RegisterValueChangedCallback(e => UserSettings.SetMasterVolume(e.newValue));
            music.RegisterValueChangedCallback(e => UserSettings.SetMusicVolume(e.newValue));
            effects.RegisterValueChangedCallback(e => UserSettings.SetEffectsVolume(e.newValue));
            fullscreen.RegisterValueChangedCallback(e => UserSettings.SetFullscreen(e.newValue));
            root.Q<Button>("settings-back-button").clicked += Close;
            Refresh();
        }

        public void Open()
        {
            Refresh();
            overlay.RemoveFromClassList("hidden");
        }

        public void Close()
        {
            if (!IsOpen) return;
            overlay.AddToClassList("hidden");
            Closed?.Invoke();
        }

        // The controls show the current settings (and the language's name after it changes)
        public void Refresh()
        {
            int i = Array.FindIndex(Loc.Languages, l => l.code == Loc.Current);
            if (i >= 0) language.SetValueWithoutNotify(language.choices[i]);
            master.SetValueWithoutNotify(UserSettings.MasterVolume);
            music.SetValueWithoutNotify(UserSettings.MusicVolume);
            effects.SetValueWithoutNotify(UserSettings.EffectsVolume);
            fullscreen.SetValueWithoutNotify(UserSettings.Fullscreen);
        }
    }
}
