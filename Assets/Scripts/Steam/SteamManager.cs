// Requires Steamworks.NET package: https://steamworks.github.io/
// Add via Package Manager → Add package from git URL:
//   https://github.com/rlabrecque/Steamworks.NET.git?path=/com.rlabrecque.steamworks.net
//
// Also requires steam_appid.txt in the project root with your Steam App ID.

using UnityEngine;

#if STEAMWORKS_ENABLED
using Steamworks;
#endif

namespace NaturalHistory.Steam
{
    public class SteamManager : MonoBehaviour
    {
        public static SteamManager Instance { get; private set; }

        public bool IsSteamInitialized { get; private set; }

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
            DontDestroyOnLoad(gameObject);
            InitializeSteam();
        }

        private void InitializeSteam()
        {
#if STEAMWORKS_ENABLED
            if (!Packsize.Test())
            {
                Debug.LogError("[SteamManager] Packsize test failed — wrong Steamworks.NET assembly.");
                return;
            }
            if (!DllCheck.Test())
            {
                Debug.LogError("[SteamManager] DllCheck failed — wrong Steam API DLL.");
                return;
            }
            try
            {
                IsSteamInitialized = SteamAPI.Init();
                if (!IsSteamInitialized)
                    Debug.LogWarning("[SteamManager] SteamAPI.Init() returned false. Running without Steam.");
                else
                    Debug.Log($"[SteamManager] Steam initialized. Player: {SteamFriends.GetPersonaName()}");
            }
            catch (System.DllNotFoundException e)
            {
                Debug.LogError($"[SteamManager] Could not load steam_api: {e.Message}");
            }
#else
            Debug.Log("[SteamManager] Steamworks not enabled (STEAMWORKS_ENABLED not defined).");
#endif
        }

        private void Update()
        {
#if STEAMWORKS_ENABLED
            if (IsSteamInitialized) SteamAPI.RunCallbacks();
#endif
        }

        private void OnDestroy()
        {
#if STEAMWORKS_ENABLED
            if (IsSteamInitialized) SteamAPI.Shutdown();
#endif
        }

        // --- Achievements ---

        public void UnlockAchievement(string achievementId)
        {
#if STEAMWORKS_ENABLED
            if (!IsSteamInitialized) return;
            SteamUserStats.SetAchievement(achievementId);
            SteamUserStats.StoreStats();
            Debug.Log($"[SteamManager] Achievement unlocked: {achievementId}");
#endif
        }

        // --- Cloud Save (stub) ---

        public void SaveToCloud(string filename, byte[] data)
        {
#if STEAMWORKS_ENABLED
            if (!IsSteamInitialized) return;
            SteamRemoteStorage.FileWrite(filename, data, data.Length);
            Debug.Log($"[SteamManager] Cloud save written: {filename} ({data.Length} bytes)");
#endif
        }

        public byte[] LoadFromCloud(string filename)
        {
#if STEAMWORKS_ENABLED
            if (!IsSteamInitialized) return null;
            if (!SteamRemoteStorage.FileExists(filename)) return null;
            int size = SteamRemoteStorage.GetFileSize(filename);
            var buffer = new byte[size];
            SteamRemoteStorage.FileRead(filename, buffer, size);
            return buffer;
#else
            return null;
#endif
        }
    }
}
