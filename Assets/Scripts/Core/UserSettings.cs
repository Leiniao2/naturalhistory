using UnityEngine;

namespace NaturalHistory.Core
{
    // The player's settings, kept between sessions (PlayerPrefs) and set from the Settings panel
    // (UI/SettingsPanel). The language is kept by Loc itself.
    //  - Master volume scales everything heard (AudioListener.volume).
    //  - Music and sound effects volumes are for whatever plays music or effects: they should play
    //    at MusicVolume / EffectsVolume (the master volume is applied on top by the listener).
    //  - Fullscreen switches between borderless fullscreen and a window (not in the Editor).
    public static class UserSettings
    {
        private const string MasterKey = "settings.masterVolume", MusicKey = "settings.musicVolume",
                             EffectsKey = "settings.effectsVolume", FullscreenKey = "settings.fullscreen";

        public static event System.Action Changed;

        public static float MasterVolume  => PlayerPrefs.GetFloat(MasterKey, 1f);
        public static float MusicVolume   => PlayerPrefs.GetFloat(MusicKey, 0.7f);
        public static float EffectsVolume => PlayerPrefs.GetFloat(EffectsKey, 0.8f);
        public static bool  Fullscreen    => PlayerPrefs.GetInt(FullscreenKey, Screen.fullScreen ? 1 : 0) == 1;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
        private static void ApplyOnStart()
        {
            AudioListener.volume = MasterVolume;
            if (PlayerPrefs.HasKey(FullscreenKey)) ApplyFullscreen(Fullscreen);
        }

        public static void SetMasterVolume(float v)  { Save(MasterKey, v); AudioListener.volume = Mathf.Clamp01(v); }
        public static void SetMusicVolume(float v)   => Save(MusicKey, v);
        public static void SetEffectsVolume(float v) => Save(EffectsKey, v);

        public static void SetFullscreen(bool on)
        {
            PlayerPrefs.SetInt(FullscreenKey, on ? 1 : 0);
            PlayerPrefs.Save();
            ApplyFullscreen(on);
            Changed?.Invoke();
        }

        private static void ApplyFullscreen(bool on)
        {
            if (Application.isEditor) return;
            if (on) Screen.SetResolution(Display.main.systemWidth, Display.main.systemHeight, FullScreenMode.FullScreenWindow);
            else Screen.fullScreenMode = FullScreenMode.Windowed;
        }

        private static void Save(string key, float v)
        {
            PlayerPrefs.SetFloat(key, Mathf.Clamp01(v));
            PlayerPrefs.Save();
            Changed?.Invoke();
        }
    }
}
