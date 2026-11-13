using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;

namespace NaturalHistory.Editor
{
    // One-click desktop builds into <project>/Builds/<Platform>/.
    // Also callable headless (Unity editor must be closed):
    //   Unity -batchmode -quit -projectPath <path> -executeMethod NaturalHistory.Editor.BuildMenu.BuildMacBatch
    public static class BuildMenu
    {
        const string BuildRoot = "Builds";

        [MenuItem("NaturalHistory/Build/Mac")]
        public static void BuildMacMenu() => BuildMac();

        [MenuItem("NaturalHistory/Build/Windows")]
        public static void BuildWindowsMenu() => BuildWindows();

        [MenuItem("NaturalHistory/Build/Mac and Windows")]
        public static void BuildAllMenu()
        {
            if (BuildMac()) BuildWindows();
        }

        // -executeMethod entry points: exit code 1 on failure so scripts can detect it.
        public static void BuildMacBatch()     => ExitWith(BuildMac());
        public static void BuildWindowsBatch() => ExitWith(BuildWindows());
        public static void BuildAllBatch()     => ExitWith(BuildMac() && BuildWindows());

        public static bool BuildMac()
        {
            SetMacUniversalArchitecture();
            var path = Path.Combine(BuildRoot, "Mac", $"{PlayerSettings.productName}.app");
            return Build(BuildTarget.StandaloneOSX, path);
        }

        public static bool BuildWindows()
        {
            var path = Path.Combine(BuildRoot, "Windows", $"{PlayerSettings.productName}.exe");
            return Build(BuildTarget.StandaloneWindows64, path);
        }

        static bool Build(BuildTarget target, string path)
        {
            var scenes = EditorBuildSettings.scenes.Where(s => s.enabled).Select(s => s.path).ToArray();
            if (scenes.Length == 0)
            {
                Debug.LogError("[BuildMenu] No scenes enabled in Build Settings. Run NaturalHistory/Setup Game Scene first.");
                return false;
            }

            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes           = scenes,
                locationPathName = path,
                target           = target,
                options          = BuildOptions.None,
            });

            var summary = report.summary;
            if (summary.result == BuildResult.Succeeded)
            {
                Debug.Log($"[BuildMenu] {target} build succeeded: {Path.GetFullPath(path)} " +
                          $"({summary.totalSize / (1024 * 1024)} MB, {summary.totalTime.TotalSeconds:F0}s)");
                if (!Application.isBatchMode) EditorUtility.RevealInFinder(path);
                return true;
            }

            Debug.LogError($"[BuildMenu] {target} build {summary.result} with {summary.totalErrors} error(s).");
            return false;
        }

        // Intel + Apple silicon. Set via reflection because UserBuildSettings lives in the
        // Mac Build Support module, which isn't installed on every machine.
        static void SetMacUniversalArchitecture()
        {
            var settings = Type.GetType("UnityEditor.OSXStandalone.UserBuildSettings, UnityEditor.OSXStandalone.Extensions");
            var prop = settings?.GetProperty("architecture");
            if (prop == null)
            {
                Debug.LogWarning("[BuildMenu] Mac architecture setting not found; using the current Build Profile value.");
                return;
            }
            prop.SetValue(null, Enum.Parse(prop.PropertyType, "x64ARM64"));
        }

        static void ExitWith(bool success)
        {
            if (Application.isBatchMode) EditorApplication.Exit(success ? 0 : 1);
        }
    }
}
