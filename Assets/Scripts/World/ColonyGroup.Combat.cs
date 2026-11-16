using System.Collections.Generic;
using UnityEngine;

namespace NaturalHistory.World
{
    // How a group strikes when it attacks a neighbouring tile (species.json "mapAttack"; the default
    // depends on how it moves and what it eats, see DefaultAttack).
    public enum AttackStyle
    {
        Charge, // rush the border and butt / gore (big herbivores)
        Bite,   // close in and snap two or three times (most predators)
        Pounce, // stalk low, then leap at the target and spring back (cats, frogs)
        Strike, // a lightning-fast dart of the head (snakes)
        Dive,   // swoop down out of the sky and pull up (birds, pterosaurs)
        Sting,  // the swarm surges forward in a frenzy (insects, bats)
        Ram,    // a fast head-first rush (big swimmers)
        Shock,  // lunge with flashes of light (electric eels)
        Snap,   // a head-first tentacle grab with a pulse (squid, ammonites)
        Engulf, // swell and flow toward the target (microbes)
        Lash,   // lean out and sting without moving (corals, anemones, perched hunters)
    }

    // How a group reacts while it is being attacked (species.json "mapDefense").
    public enum DefenseStyle
    {
        Brace,   // face the attacker, crouch and give a little ground
        Rear,    // rear up facing the attacker (elephants, zebras, kangaroos)
        Scatter, // dash away in all directions, then drift back (small prey, fish schools)
        Coil,    // coil up tight with the head raised (snakes)
        Hide,    // withdraw: squash down into shell or burrow (turtles, snails, corals)
        Ink,     // jet backwards behind a cloud of ink (squid, ammonites)
        Tighten, // pull together into a tight ball (swarms, microbes)
        Mob,     // climb and wheel over the attacker (birds)
        Puff,    // inflate to look bigger (toads)
    }

    public partial class ColonyGroup
    {
        private const float DefenseTime = 1.8f; // seconds a defence lasts

        public AttackStyle AttackKind  { get; private set; }
        public DefenseStyle DefenseKind { get; private set; }

        // Fixed colonies (corals, anemones, perched hunters) can't move but still strike in place
        public bool CanAttack => members.Count > 0;

        private float strikeP = -1f;   // 0..1 through the strike while holding at the border; < 0 otherwise
        private float defenseStart = -1f;
        private Vector3 defenseDir;    // horizontal, toward the attacker
        private float defenseWeight;   // 0..1 how far into the defensive pose
        private bool inkReleased;
        private readonly List<(Transform puff, float born, float size)> ink = new();
        private static Mesh inkMesh;
        private static readonly int ColorId = Shader.PropertyToID("_Color");

        private void InitCombatStyles()
        {
            AttackKind  = Parse(Definition?.mapAttack, DefaultAttack());
            DefenseKind = Parse(Definition?.mapDefense, DefaultDefense());
        }

        private static T Parse<T>(string value, T fallback) where T : struct =>
            !string.IsNullOrEmpty(value) && System.Enum.TryParse(value, true, out T v) ? v : fallback;

        private bool Eats(string diet) => Definition != null && Definition.diet == diet;
        private bool Predator => Eats("Carnivore") || Eats("Omnivore") || Eats("Scavenger");

        private AttackStyle DefaultAttack() => Style switch
        {
            ColonyStyle.Fixed  => AttackStyle.Lash,
            ColonyStyle.Drift  => AttackStyle.Engulf,
            ColonyStyle.Float  => AttackStyle.Bite,
            ColonyStyle.Soar   => AttackStyle.Dive,
            ColonyStyle.Swarm  => AttackStyle.Sting,
            ColonyStyle.Swim   => Backward ? AttackStyle.Snap
                                : Definition != null && Definition.mapUndulate ? AttackStyle.Shock
                                : Predator ? AttackStyle.Bite : AttackStyle.Ram,
            _ => Gait switch // Ground
            {
                ColonyGait.Slither => AttackStyle.Strike,
                ColonyGait.Run or ColonyGait.Hop => AttackStyle.Pounce,
                _ => Predator ? AttackStyle.Bite : AttackStyle.Charge,
            },
        };

        private DefenseStyle DefaultDefense() => Style switch
        {
            ColonyStyle.Fixed  => DefenseStyle.Hide,
            ColonyStyle.Drift  => DefenseStyle.Tighten,
            ColonyStyle.Float  => DefenseStyle.Scatter,
            ColonyStyle.Soar   => DefenseStyle.Mob,
            ColonyStyle.Swarm  => DefenseStyle.Tighten,
            ColonyStyle.Swim   => Backward ? DefenseStyle.Ink : MemberSpan > 0.9f ? DefenseStyle.Brace : DefenseStyle.Scatter,
            _ => Gait switch // Ground
            {
                ColonyGait.Slither => DefenseStyle.Coil,
                ColonyGait.Hop     => Definition != null && Definition.mapLegs == 1 ? DefenseStyle.Rear : DefenseStyle.Puff,
                _ => !Predator && MemberSpan <= 0.6f ? DefenseStyle.Scatter : DefenseStyle.Brace,
            },
        };

        // Seconds holding at the border, how far toward the target it gets (fraction of the way to
        // the target tile's centre) and the approach speed (multiple of the travel speed)
        private (float hold, float reach, float approach) StrikeTiming() => AttackKind switch
        {
            AttackStyle.Bite   => (0.8f, 0.4f, 1.6f),
            AttackStyle.Pounce => (0.6f, 0.26f, 0.6f), // stalks in slowly; the leap covers the rest
            AttackStyle.Strike => (0.5f, 0.32f, 1.2f),
            AttackStyle.Dive   => (0.9f, 0.4f, 1.4f),
            AttackStyle.Sting  => (1.0f, 0.42f, 1.8f),
            AttackStyle.Ram    => (0.6f, 0.38f, 2.0f),
            AttackStyle.Shock  => (0.9f, 0.36f, 1.4f),
            AttackStyle.Snap   => (0.6f, 0.36f, 1.6f),
            AttackStyle.Engulf => (1.2f, 0.4f, 1.0f),
            AttackStyle.Lash   => (0.8f, 0f, 1f),
            _                  => (0.55f, 0.42f, 1.7f), // Charge
        };

        // The defender in this group's niche on the tile reacts as the blow lands
        private void WarnDefender(HexCell target, float strikeIn)
        {
            var defender = SpeciesColonies.Instance != null ? SpeciesColonies.Instance.GroupAt(target, Niche) : null; // it competes for the same niche
            if (defender != null && defender != this) defender.Defend(Cell, Mathf.Max(0f, strikeIn - 0.35f));
        }

        // Plays this group's defence against an attack from a neighbouring tile, starting after `delay`.
        public void Defend(HexCell attackerCell, float delay = 0f)
        {
            if (attackerCell == null || attackerCell == Cell) return;
            var d = attackerCell.transform.position - (Cell != null ? Cell.transform.position : transform.position);
            d.y = 0f;
            var grid = HexGrid.Instance;
            if (grid != null) d.x -= Mathf.Round(d.x / grid.WrapWidth) * grid.WrapWidth; // across the wrap seam
            defenseDir   = d.sqrMagnitude > 1e-6f ? d.normalized : Vector3.forward;
            defenseStart = Time.time + delay;
            inkReleased  = false;
        }

        // Called once per frame before the members are posed
        private void UpdateDefense(float t)
        {
            defenseWeight = 0f;
            if (defenseStart < 0f || t < defenseStart) return;
            float tau = t - defenseStart;
            if (tau > DefenseTime) { defenseStart = -1f; return; }
            defenseWeight = Mathf.SmoothStep(0f, 1f, tau / 0.3f) * (1f - Mathf.SmoothStep(0f, 1f, (tau - (DefenseTime - 0.6f)) / 0.6f));
            if (DefenseKind == DefenseStyle.Ink && !inkReleased) ReleaseInk();
        }

        // Attack pose on top of the blended pose; k = how much of it applies (the travel weight)
        private void StrikePose(Member m, float t, Quaternion hq, float k, ref Vector3 pos, ref Quaternion rot, ref Vector3 scale)
        {
            if (strikeP < 0f || k <= 0f) return;
            float p = strikeP, arc = Mathf.Sin(p * Mathf.PI) * k;
            float s = Mathf.Max(m.span, 0.3f);
            var forward = hq * Vector3.forward;
            switch (AttackKind)
            {
                case AttackStyle.Bite:
                {
                    float jab = Mathf.Max(0f, Mathf.Sin(p * Mathf.PI * 3f)) * k; // three snaps
                    pos += forward * jab * 0.12f * s;
                    rot  = rot * Quaternion.Euler(jab * 10f, 0f, 0f);
                    break;
                }
                case AttackStyle.Pounce:
                    pos += forward * arc * 0.35f * s + Vector3.up * arc * 0.18f * s;
                    rot  = rot * Quaternion.Euler(-25f * Mathf.Sin(p * Mathf.PI * 2f) * k, 0f, 0f);
                    break;
                case AttackStyle.Strike:
                {
                    // darts out in a quarter of the time, recoils slowly
                    float dart = (p < 0.25f ? Mathf.SmoothStep(0f, 1f, p / 0.25f) : 1f - Mathf.SmoothStep(0f, 1f, (p - 0.25f) / 0.75f)) * k;
                    pos += forward * dart * 0.3f * s;
                    break;
                }
                case AttackStyle.Dive:
                    pos += forward * arc * 0.15f;
                    pos.y -= arc * Mathf.Max(m.basePosition.y - 0.05f, 0f);
                    rot  = rot * Quaternion.Euler(35f * Mathf.Sin(p * Mathf.PI * 2f) * k, 0f, 0f); // nose down, then up
                    break;
                case AttackStyle.Sting:
                    pos += forward * arc * 0.2f
                         + new Vector3(Mathf.Sin(t * 23f + m.phase), Mathf.Sin(t * 19f + m.phase * 2f), Mathf.Cos(t * 21f + m.phase)) * (0.03f * arc);
                    break;
                case AttackStyle.Ram:
                    pos += forward * arc * 0.25f * s;
                    break;
                case AttackStyle.Shock:
                    pos += forward * arc * 0.06f * s;
                    Flash(m, arc * (0.5f + 0.5f * Mathf.Sin(t * 40f + m.phase)));
                    break;
                case AttackStyle.Snap:
                    pos   += forward * arc * 0.15f * s;
                    scale *= 1f + 0.1f * arc;
                    break;
                case AttackStyle.Engulf:
                    pos   += forward * arc * 0.08f;
                    scale *= 1f + 0.35f * arc;
                    break;
                case AttackStyle.Lash:
                {
                    // lean toward the target and back, with a quick contraction
                    var axis = Vector3.Cross(Vector3.up, forward);
                    rot   = Quaternion.AngleAxis(25f * arc, axis) * rot;
                    scale = Vector3.Scale(scale, new Vector3(1f, 1f + 0.15f * Mathf.Sin(p * Mathf.PI * 2f) * k, 1f));
                    break;
                }
                // Charge: the head-down rush is part of TravelPose (lunge)
            }
        }

        // Defensive pose on top of everything else
        private void DefensePose(Member m, float t, ref Vector3 pos, ref Quaternion rot, ref Vector3 scale)
        {
            float dw = defenseWeight;
            if (dw <= 0f) return;
            float s   = Mathf.Max(m.span, 0.3f);
            var away  = -defenseDir;
            var face  = Quaternion.LookRotation(defenseDir);
            switch (DefenseKind)
            {
                case DefenseStyle.Brace:
                    rot  = Quaternion.Slerp(rot, face * Quaternion.Euler(8f, 0f, 0f), dw);
                    pos += away * 0.03f * s * dw + Vector3.down * 0.01f * s * dw;
                    break;
                case DefenseStyle.Rear:
                    rot  = Quaternion.Slerp(rot, face * Quaternion.Euler(-28f, 0f, 0f), dw);
                    pos += away * 0.04f * s * dw;
                    break;
                case DefenseStyle.Scatter:
                {
                    // each runs off a different way, mostly away from the attacker
                    var flat = new Vector3(pos.x, 0f, pos.z);
                    var dir  = (away + (flat.sqrMagnitude > 1e-6f ? flat.normalized : Quaternion.Euler(0f, m.phase * 57f, 0f) * Vector3.forward) * 0.8f).normalized;
                    pos += dir * 0.22f * dw;
                    rot  = Quaternion.Slerp(rot, Quaternion.LookRotation(dir), dw * 0.9f);
                    break;
                }
                case DefenseStyle.Coil: // the coil itself is set in Locomote (defenseWeight)
                    rot = Quaternion.Slerp(rot, face, dw);
                    break;
                case DefenseStyle.Hide:
                    scale = Vector3.Scale(scale, new Vector3(1f + 0.1f * dw, 1f - 0.45f * dw, 1f + 0.1f * dw));
                    break;
                case DefenseStyle.Ink: // jets off backwards, still facing the attacker
                    pos += away * 0.3f * dw;
                    rot  = Quaternion.Slerp(rot, face, dw);
                    break;
                case DefenseStyle.Tighten:
                    pos = new Vector3(Mathf.Lerp(pos.x, pos.x * 0.4f, dw), pos.y, Mathf.Lerp(pos.z, pos.z * 0.4f, dw));
                    break;
                case DefenseStyle.Mob:
                    pos += Vector3.up * 0.15f * dw + defenseDir * 0.08f * dw;
                    rot  = Quaternion.Slerp(rot, face * Quaternion.Euler(0f, 0f, 25f * Mathf.Sin(t * 3f + m.phase)), dw * 0.7f);
                    break;
                case DefenseStyle.Puff:
                    scale *= 1f + 0.35f * dw;
                    rot    = Quaternion.Slerp(rot, face, dw * 0.6f);
                    break;
            }
        }

        // Applies a pose's scale factor on top of the member's own size
        private static void ApplyScale(Member m, Vector3 scale)
        {
            if (!m.scaleInit) { m.baseScale = m.transform.localScale; m.scaleInit = true; }
            if (scale == Vector3.one && !m.scaled) return;
            m.transform.localScale = Vector3.Scale(m.baseScale, scale);
            m.scaled = scale != Vector3.one;
        }

        // Brightens the member (electric discharge); 0 = its own colour
        private static void Flash(Member m, float amount)
        {
            if (!m.tintInit) { m.baseTint = m.block.GetColor(ColorId); m.tintInit = true; }
            var c = Color.Lerp(m.baseTint, new Color(1.2f, 1.6f, 2.2f), Mathf.Clamp01(amount));
            m.block.SetColor(ColorId, c);
            m.renderer.SetPropertyBlock(m.block);
        }

        // A few dark puffs left behind where the group was, swelling and then shrinking away
        private void ReleaseInk()
        {
            inkReleased = true;
            if (members.Count == 0 || rootCell == null) return;
            inkMesh ??= MapFeatureMeshes.CreateSmokePuff(new System.Random(11));
            var material = members[0].renderer != null ? members[0].renderer.sharedMaterial : null;
            var block = new MaterialPropertyBlock();
            block.SetColor(ColorId, new Color(0.12f, 0.1f, 0.13f));
            for (int i = 0; i < 4; i++)
            {
                var go = new GameObject("Ink");
                go.transform.SetParent(rootCell.transform, false);
                var m = members[i % members.Count];
                go.transform.position = m.transform.position + new Vector3((i - 1.5f) * 0.03f, 0.01f, (i % 2) * 0.03f);
                go.transform.localScale = Vector3.one * 1e-4f;
                go.AddComponent<MeshFilter>().sharedMesh = inkMesh;
                var mr = go.AddComponent<MeshRenderer>();
                mr.sharedMaterial = material;
                mr.SetPropertyBlock(block);
                ink.Add((go.transform, Time.time + i * 0.08f, Mathf.Max(MemberSpan, 0.2f) * (0.35f + 0.1f * i)));
            }
        }

        private void UpdateInk(float t)
        {
            for (int i = ink.Count - 1; i >= 0; i--)
            {
                var (puff, born, size) = ink[i];
                float a = (t - born) / 2.2f;
                if (puff == null || a >= 1f)
                {
                    if (puff != null) Destroy(puff.gameObject);
                    ink.RemoveAt(i);
                    continue;
                }
                float r = size * Mathf.SmoothStep(0f, 1f, a / 0.2f) * (1f - Mathf.SmoothStep(0f, 1f, (a - 0.5f) / 0.5f));
                puff.localScale = Vector3.one * Mathf.Max(r, 1e-4f);
                puff.position += Vector3.up * 0.01f * Time.deltaTime;
            }
        }

        private void OnDestroy()
        {
            foreach (var (puff, _, _) in ink) if (puff != null) Destroy(puff.gameObject);
            ink.Clear();
        }
    }
}
