using UnityEngine;
using UnityEngine.UIElements;

namespace NaturalHistory.UI
{
    // The buttons' icons: painted images (generated in Google Flow) in Resources/UI/Icons/<name>.png.
    //  - encyclopedia: an open book
    //  - revive: a circular arrow round a seedling (bringing a lost species back)
    //  - evolve: a DNA double helix (evolving)
    //  - functions / behaviors: the two trait trees
    //  - reproduce: a cell dividing in two
    //  - the Evolution Tree uses the evolve icon too (a DNA double helix)
    // Until an image is there, a plain white shape drawn here stands in (signed distances,
    // antialiased over about a pixel), so the buttons always show something.
    public static class UiIcons
    {
        private const int Size = 64;

        private static Texture2D book, revive, upgrade, functions, behaviors, reproduce, evolve;
        public static Texture2D Book      => book      ??= Load("encyclopedia") ?? Draw("IconBook", BookShape);
        public static Texture2D Revive    => revive    ??= Load("revive") ?? Draw("IconRevive", ReviveShape);
        public static Texture2D Upgrade   => upgrade   ??= Load("evolve") ?? Draw("IconUpgrade", UpgradeShape);
        public static Texture2D Functions => functions ??= Load("functions");
        public static Texture2D Behaviors => behaviors ??= Load("behaviors");
        public static Texture2D Reproduce => reproduce ??= Load("reproduce");
        public static Texture2D Evolve    => evolve    ??= Load("evolve"); // the painting only (no stand-in)
        public static Texture2D Tree      => Evolve;

        // Whether the painted image exists (a drawn stand-in is white: tint it; a painting isn't)
        public static bool Painted(Texture2D icon) => icon != null && !icon.name.StartsWith("Icon");

        private static Texture2D Load(string name) => Resources.Load<Texture2D>("UI/Icons/" + name);

        // Puts `icon` in front of a button's label (the Functions / Behaviors buttons); nothing
        // until the painted image is there
        public static void Decorate(UnityEngine.UIElements.Button button, Texture2D icon)
        {
            if (button == null || icon == null || button.Q(className: "button-icon") != null) return;
            var image = new UnityEngine.UIElements.VisualElement { pickingMode = UnityEngine.UIElements.PickingMode.Ignore };
            image.AddToClassList("button-icon");
            image.style.backgroundImage = new UnityEngine.UIElements.StyleBackground(icon);
            button.style.flexDirection = UnityEngine.UIElements.FlexDirection.Row;
            button.style.alignItems = UnityEngine.UIElements.Align.Center;
            button.Insert(0, image);
        }

        // shape(p) < 0 inside; p in -1..1, y up
        private static Texture2D Draw(string name, System.Func<Vector2, float> shape)
        {
            var tex = new Texture2D(Size, Size, TextureFormat.RGBA32, false) { name = name, wrapMode = TextureWrapMode.Clamp, filterMode = FilterMode.Bilinear };
            var px = new Color32[Size * Size];
            float aa = 1.5f / Size;
            for (int y = 0; y < Size; y++)
            for (int x = 0; x < Size; x++)
            {
                var p = new Vector2((x + 0.5f) / Size * 2f - 1f, (y + 0.5f) / Size * 2f - 1f);
                float a = Mathf.Clamp01(0.5f - shape(p) / aa);
                px[y * Size + x] = new Color32(255, 255, 255, (byte)(a * 255));
            }
            tex.SetPixels32(px);
            tex.Apply(false, true);
            return tex;
        }

        private static float Box(Vector2 p, Vector2 c, Vector2 half)
        {
            var d = new Vector2(Mathf.Abs(p.x - c.x) - half.x, Mathf.Abs(p.y - c.y) - half.y);
            return new Vector2(Mathf.Max(d.x, 0f), Mathf.Max(d.y, 0f)).magnitude + Mathf.Min(Mathf.Max(d.x, d.y), 0f);
        }

        private static float Segment(Vector2 p, Vector2 a, Vector2 b, float r)
        {
            var pa = p - a; var ba = b - a;
            float h = Mathf.Clamp01(Vector2.Dot(pa, ba) / Vector2.Dot(ba, ba));
            return (pa - ba * h).magnitude - r;
        }

        // two pages, slightly tilted up toward the spine, with a gap for the spine
        private static float BookShape(Vector2 p)
        {
            var q = new Vector2(Mathf.Abs(p.x), p.y + Mathf.Abs(p.x) * -0.12f);
            float page  = Box(q, new Vector2(0.44f, 0f), new Vector2(0.36f, 0.56f));
            float inner = Box(q, new Vector2(0.44f, 0.05f), new Vector2(0.27f, 0.46f));
            float frame = Mathf.Max(page, -inner);
            float lines = Mathf.Min(Mathf.Min(Box(q, new Vector2(0.44f, 0.25f), new Vector2(0.2f, 0.035f)),
                                              Box(q, new Vector2(0.44f, 0.05f), new Vector2(0.2f, 0.035f))),
                                    Box(q, new Vector2(0.44f, -0.15f), new Vector2(0.2f, 0.035f)));
            return Mathf.Min(frame, lines);
        }

        // a ring open at the top right, with an arrowhead at the open end
        private static float ReviveShape(Vector2 p)
        {
            float ring = Mathf.Abs(p.magnitude - 0.6f) - 0.12f;
            float angle = Mathf.Atan2(p.y, p.x) * Mathf.Rad2Deg; // the gap: 20°..80°
            float gap = angle > 15f && angle < 85f ? 1f : -1f;
            ring = Mathf.Max(ring, -gap * 0.2f);
            // arrowhead at the ring's end near 85°, pointing along the circle (clockwise: rightward)
            var tip = new Vector2(Mathf.Cos(85f * Mathf.Deg2Rad), Mathf.Sin(85f * Mathf.Deg2Rad)) * 0.6f;
            float head = Mathf.Min(Segment(p, tip + new Vector2(0.28f, 0f), tip + new Vector2(-0.02f, 0.24f), 0.07f),
                                   Segment(p, tip + new Vector2(0.28f, 0f), tip + new Vector2(-0.02f, -0.24f), 0.07f));
            return Mathf.Min(ring, head);
        }

        // a DNA double helix standing upright: two strands twisting round each other, with rungs
        private static float UpgradeShape(Vector2 p)
        {
            if (Mathf.Abs(p.y) > 0.88f) return Mathf.Abs(p.y) - 0.88f + 0.05f; // ends
            const float amp = 0.36f, k = 4.2f, w = 0.075f;
            float f = amp * Mathf.Sin(k * p.y), slope = amp * k * Mathf.Cos(k * p.y);
            float norm = Mathf.Sqrt(1f + slope * slope);
            float strands = Mathf.Min(Mathf.Abs(p.x - f), Mathf.Abs(p.x + f)) / norm - w;
            // rungs between the strands, where they are apart
            float rungs = float.MaxValue;
            for (int i = -3; i <= 3; i++)
            {
                float y = i * 0.25f;
                float half = Mathf.Abs(amp * Mathf.Sin(k * y));
                if (half < 0.12f) continue;
                rungs = Mathf.Min(rungs, Box(p, new Vector2(0f, y), new Vector2(half, 0.035f)));
            }
            return Mathf.Min(strands, rungs);
        }
    }
}
