using System.IO;
using UnityEditor;
using UnityEngine;

namespace NaturalHistory.EditorTools
{
    // Debugging aid: while playing in the editor, a file Temp/nh_shot.request makes it save a short
    // burst of Game view screenshots (Temp/nh_shot_0.png …, a few frames apart) and the camera's
    // position each time (Temp/nh_shot.txt), so a visual problem can be looked at from outside.
    [InitializeOnLoad]
    public static class ShotOnRequest
    {
        private const string Request = "Temp/nh_shot.request";
        private const int Count = 4, FramesApart = 6;
        private static int taking = -1, frame;

        static ShotOnRequest() => EditorApplication.update += Tick;

        private static void Tick()
        {
            if (!EditorApplication.isPlaying) { taking = -1; return; }
            if (taking < 0)
            {
                if (!File.Exists(Request)) return;
                File.Delete(Request);
                File.WriteAllText("Temp/nh_shot.txt", "");
                taking = 0;
                frame = Time.frameCount;
            }
            if (Time.frameCount < frame) return;
            ScreenCapture.CaptureScreenshot($"Temp/nh_shot_{taking}.png");
            var cam = Camera.main;
            if (cam != null) File.AppendAllText("Temp/nh_shot.txt", $"{taking} frame {Time.frameCount} cam {cam.transform.position:F4} rot {cam.transform.eulerAngles:F2}\n");
            taking++;
            frame = Time.frameCount + FramesApart;
            if (taking >= Count) taking = -1;
        }
    }
}
