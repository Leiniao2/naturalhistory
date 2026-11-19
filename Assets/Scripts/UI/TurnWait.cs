using System;
using System.Collections;
using UnityEngine;
using UnityEngine.UIElements;

namespace NaturalHistory.UI
{
    // While a turn ends (the world moves on, AI players and wild animals act), a turning gold ring
    // by the mouse pointer shows the game is busy, instead of the system's wait cursor: Run shows it,
    // lets it be drawn, then ends the turn; it goes once the AI players are done (AiPlayers.Thinking)
    // and has shown for at least MinSeconds. Further End Turn clicks meanwhile are ignored.
    public static class TurnWait
    {
        private const float MinSeconds = 0.5f;
        private const float Size = 34f;

        private static VisualElement root, ring;
        private static MonoBehaviour host;
        private static float angle;

        public static bool Busy { get; private set; }

        public static void Init(VisualElement panelRoot, MonoBehaviour coroutineHost)
        {
            root = panelRoot;
            host = coroutineHost;
            ring = new VisualElement { pickingMode = PickingMode.Ignore, name = "turn-wait" };
            ring.style.position = Position.Absolute;
            ring.style.width = ring.style.height = Size;
            ring.style.display = DisplayStyle.None;
            ring.generateVisualContent += Draw;
            root.Add(ring);
        }

        public static void Run(Action endTurn)
        {
            if (Busy) return;
            if (host == null) { endTurn(); return; }
            host.StartCoroutine(Wait(endTurn));
        }

        private static IEnumerator Wait(Action endTurn)
        {
            Busy = true;
            ring.style.display = DisplayStyle.Flex;
            ring.BringToFront();
            Follow();
            float shown = Time.unscaledTime;
            yield return null; // drawn before the main thread gets busy
            yield return new WaitForEndOfFrame();
            try { endTurn(); }
            catch (Exception e) { Debug.LogException(e); }
            yield return null;
            while (Players.AiPlayers.Instance != null && Players.AiPlayers.Instance.Thinking) yield return null;
            while (Time.unscaledTime - shown < MinSeconds) yield return null;
            ring.style.display = DisplayStyle.None;
            Busy = false;
        }

        // Called every frame (GameMenus.Update): turn, and stay by the pointer
        public static void Update()
        {
            if (!Busy || ring == null) return;
            angle = (angle + Time.unscaledDeltaTime * 300f) % 360f;
            ring.style.rotate = new Rotate(angle);
            Follow();
        }

        private static void Follow()
        {
            if (root?.panel == null) return;
            var mouse = Input.mousePosition;
            var p = RuntimePanelUtils.ScreenToPanel(root.panel, new Vector2(mouse.x, Screen.height - mouse.y));
            ring.style.left = p.x + 14f;
            ring.style.top  = p.y + 14f;
        }

        // A dark track with a bright gold arc on it, like the frames' brass
        private static void Draw(MeshGenerationContext ctx)
        {
            var p = ctx.painter2D;
            var c = new Vector2(Size * 0.5f, Size * 0.5f);
            float r = Size * 0.5f - 4f;
            p.lineWidth = 5f;
            p.lineCap = LineCap.Round;
            p.strokeColor = new Color(0.03f, 0.05f, 0.04f, 0.8f);
            p.BeginPath(); p.Arc(c, r, 0f, 360f); p.Stroke();
            p.strokeColor = new Color(0.87f, 0.75f, 0.49f, 1f);
            p.BeginPath(); p.Arc(c, r, 0f, 250f); p.Stroke();
            p.lineWidth = 2f;
            p.strokeColor = new Color(1f, 0.93f, 0.7f, 0.9f);
            p.BeginPath(); p.Arc(c, r, 200f, 250f); p.Stroke();
        }
    }
}
