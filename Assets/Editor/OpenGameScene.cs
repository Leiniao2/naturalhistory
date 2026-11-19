using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;

namespace NaturalHistory.EditorTools
{
    // The editor always works in Game.unity: when it starts up (or reloads scripts) on an empty,
    // unsaved scene ("Untitled", as after a crash or a fresh checkout) it opens the game scene, and
    // Play always starts from the game scene whatever is open.
    [InitializeOnLoad]
    public static class OpenGameScene
    {
        private const string GameScene = "Assets/Scenes/Game.unity";

        static OpenGameScene()
        {
            EditorSceneManager.playModeStartScene = AssetDatabase.LoadAssetAtPath<SceneAsset>(GameScene);
            EditorApplication.delayCall += OpenIfUntitled;
        }

        private static void OpenIfUntitled()
        {
            if (EditorApplication.isPlayingOrWillChangePlaymode) return;
            var active = SceneManager.GetActiveScene();
            if (!string.IsNullOrEmpty(active.path) || active.isDirty || SceneManager.sceneCount > 1) return;
            if (AssetDatabase.LoadAssetAtPath<SceneAsset>(GameScene) == null) return;
            EditorSceneManager.OpenScene(GameScene);
        }

        [MenuItem("Natural History/Open Game Scene")]
        private static void Open()
        {
            if (EditorApplication.isPlaying) EditorApplication.isPlaying = false;
            if (EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) EditorSceneManager.OpenScene(GameScene);
        }
    }
}
