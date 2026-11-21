using NaturalHistory.Core;
using NaturalHistory.World;
using UnityEngine;
using UnityEngine.UIElements;

namespace NaturalHistory.UI
{
    // With a group selected, pointing at a foe it can attack (MovePathView.HoveredTarget) shows,
    // beside the pointer, the two sides' strength (attack, defense, HP) side by side and what the
    // attack is expected to do (Combat.Predict): the damage each side takes, and whether the foe is
    // eaten or wiped out, or the attacker dies of the counterattack.
    public class AttackPreview
    {
        private static readonly Color Good = new(0.55f, 0.9f, 0.5f), Bad = new(1f, 0.45f, 0.4f), Dim = new(0.75f, 0.75f, 0.7f);

        private readonly VisualElement root, box;
        private readonly Label nameA, nameD, atkA, atkD, defA, defD, hpA, hpD, dealt, back, outcome;
        private HexCell shownFor;

        public AttackPreview(VisualElement root)
        {
            this.root = root;
            box = new VisualElement { pickingMode = PickingMode.Ignore };
            box.AddToClassList("zoology-tip");
            box.AddToClassList("hidden");
            box.style.minWidth = 260;

            (nameA, nameD) = Row(null, true);
            (atkA, atkD) = Row(Loc.T("Attack"));
            (defA, defD) = Row(Loc.T("Defense"));
            (hpA, hpD) = Row(Loc.T("HP"));
            dealt   = Line(); dealt.style.marginTop = 6;
            back    = Line();
            outcome = Line(); outcome.style.unityFontStyleAndWeight = FontStyle.Bold; outcome.style.marginTop = 4;
            root.Add(box);
        }

        private (Label, Label) Row(string caption, bool header = false)
        {
            var row = new VisualElement { pickingMode = PickingMode.Ignore };
            row.style.flexDirection = FlexDirection.Row;
            var c = Cell(caption ?? "", 70, TextAnchor.MiddleLeft);
            c.style.color = Dim;
            var a = Cell("", 110, TextAnchor.MiddleCenter);
            var d = Cell("", 110, TextAnchor.MiddleCenter);
            if (header)
            {
                a.style.unityFontStyleAndWeight = FontStyle.Bold;
                d.style.unityFontStyleAndWeight = FontStyle.Bold;
                a.style.whiteSpace = WhiteSpace.Normal;
                d.style.whiteSpace = WhiteSpace.Normal;
                row.style.marginBottom = 4;
            }
            row.Add(c); row.Add(a); row.Add(d);
            box.Add(row);
            return (a, d);
        }

        private static Label Cell(string text, float width, TextAnchor align)
        {
            var l = new Label(text) { pickingMode = PickingMode.Ignore };
            l.style.width = width;
            l.style.unityTextAlign = align;
            l.style.paddingLeft = 0; l.style.paddingRight = 0;
            return l;
        }

        private Label Line()
        {
            var l = new Label { pickingMode = PickingMode.Ignore };
            l.style.whiteSpace = WhiteSpace.Normal;
            box.Add(l);
            return l;
        }

        // Polled every frame
        public void Update()
        {
            var range = MovePathView.Range;
            var target = MovePathView.HoveredTarget;
            var attacker = range?.Group;
            var defender = target != null && attacker != null ? Combat.Defender(attacker, target) : null;
            if (defender == null || attacker.Definition == null || defender.Definition == null)
            {
                if (shownFor != null) { box.AddToClassList("hidden"); shownFor = null; }
                return;
            }
            bool moved = range.AttackFrom.TryGetValue(target, out var from) && from != attacker.Cell;
            Fill(attacker, defender, Combat.Predict(attacker, defender, moved));
            shownFor = target;
            box.RemoveFromClassList("hidden");
            box.BringToFront();
            Place();
        }

        private void Fill(ColonyGroup a, ColonyGroup d, Combat.Forecast f)
        {
            nameA.text = Loc.T(a.Definition.commonName);
            nameD.text = Loc.T(d.Definition.commonName);
            Compare(atkA, atkD, a.Stats.attack, d.Stats.attack);
            Compare(defA, defD, a.Stats.defense, d.Stats.defense);
            hpA.text = $"{Hp(a.Hp)}/{Hp(a.MaxHp)}";
            hpD.text = $"{Hp(d.Hp)}/{Hp(d.MaxHp)}";
            hpA.style.color = hpD.style.color = new StyleColor(StyleKeyword.Null);

            if (!f.canFight)
            {
                dealt.text = Loc.F("{0} and {1} are too different in size to fight", nameA.text, nameD.text);
                back.text = ""; outcome.text = "";
                return;
            }
            if (f.eats)
            {
                dealt.text = Loc.F("Eats it whole (+{0} HP)", Hp(Mathf.Min(f.dealt, a.MaxHp - a.Hp)));
                dealt.style.color = Good;
                back.text = "";
                outcome.text = Loc.T("Expected: the foe is eaten");
                outcome.style.color = Good;
                return;
            }
            dealt.text = Loc.F("Expected damage dealt: {0} ({1} → {2} HP)", Hp(f.dealt), Hp(d.Hp), Hp(Mathf.Max(0f, d.Hp - f.dealt)));
            dealt.style.color = Good;
            back.text = f.ambush ? Loc.T("An ambush: no counterattack")
                      : Loc.F("Expected damage taken: {0} ({1} → {2} HP)", Hp(f.back), Hp(a.Hp), Hp(Mathf.Max(0f, a.Hp - f.back)));
            back.style.color = f.back > 0f ? Bad : Good;
            bool kills = f.Kills(d), dies = f.back >= a.Hp;
            outcome.text = kills && dies ? Loc.T("Expected: both are wiped out")
                         : kills ? Loc.T("Expected: the foe is wiped out")
                         : dies ? Loc.T("Expected: your animal dies of the counterattack")
                         : Loc.T("Expected: both survive");
            outcome.style.color = dies ? Bad : kills ? Good : Dim;
        }

        // the better of the two in green, the worse in red
        private static void Compare(Label a, Label d, int va, int vd)
        {
            a.text = va.ToString(); d.text = vd.ToString();
            a.style.color = va > vd ? Good : va < vd ? Bad : Dim;
            d.style.color = vd > va ? Good : vd < va ? Bad : Dim;
        }

        private static string Hp(float v) => v.ToString(v < 10f ? "0.#" : "0");

        private void Place()
        {
            if (root.panel == null) return;
            var mouse = Input.mousePosition;
            var p = RuntimePanelUtils.ScreenToPanel(root.panel, new Vector2(mouse.x, Screen.height - mouse.y));
            var area = root.layout;
            var size = box.layout.size;
            float x = p.x + 22f, y = p.y + 22f;
            if (!float.IsNaN(size.x) && x + size.x > area.width - 8f) x = p.x - size.x - 22f;
            if (!float.IsNaN(size.y) && y + size.y > area.height - 8f) y = p.y - size.y - 22f;
            box.style.left = Mathf.Max(0f, x);
            box.style.top  = Mathf.Max(0f, y);
        }
    }
}
