using System;
using System.Collections.Generic;
using NaturalHistory.Data;
using UnityEngine;

namespace NaturalHistory.World
{
    // One species' group on the map (built by SpeciesColonies). Settled, every member plays its
    // style's idle motion around the tile centre: wandering, circling, bobbing. MoveTo / MoveAlong /
    // Attack blend each member out of that idle pose into a travelling formation facing the way the
    // group goes, carry the group across the tile borders with a travel animation (faster gait,
    // steady wing beats, tail wag...) and blend back into the idle motion on arrival. Every pose is
    // a blend of continuous motions, so nothing ever jumps.
    //
    // The group root stays a child of the tile it set out from until it arrives, and its path is
    // stored as offsets from that tile, so the east–west wrap (which moves whole cells) carries a
    // travelling group along with it.
    public class ColonyGroup : MonoBehaviour
    {
        // Seconds to fall into formation / to break formation after arriving
        private const float GatherTime = 0.6f;
        private const float SettleTime = 0.9f;
        private const float SetOffDelay = 0.3f;  // the group starts moving while members are still falling in
        private const float RampTime   = 0.45f;  // accelerating / slowing down at each end of a leg
        private const float TurnRate   = 220f;   // degrees per second the formation turns at corners

        // Attack: charge to just short of the border, strike, back off facing the target
        private const float StrikeReach  = 0.42f; // fraction of the way to the target tile's centre
        private const float StrikeHold   = 0.55f; // seconds at the border
        private const float ChargeSpeed  = 1.7f;  // multiplier on the travel speed
        private const float BackOffSpeed = 0.6f;

        private static readonly int FlapId        = Shader.PropertyToID("_Flap");
        private static readonly int StrideId      = Shader.PropertyToID("_Stride");
        private static readonly int StridePhaseId = Shader.PropertyToID("_StridePhase");

        public SpeciesDefinition Definition { get; private set; }
        public ColonyStyle Style { get; private set; }
        public ColonyGait Gait { get; private set; }
        public HexCell Cell { get; private set; }       // the group's tile (its destination while travelling)
        public float MemberSpan { get; private set; }   // size of one member, in cells

        public bool CanMove => Style != ColonyStyle.Fixed && members.Count > 0;
        public bool Backward => Definition != null && Definition.mapBackward; // swims tail first
        public bool IsBusy  => trip != null;

        public event Action<ColonyGroup> Arrived;            // finished a move or an attack and settled in
        public event Action<ColonyGroup, HexCell> Struck;    // reached the border of the tile it attacks

        public class Member
        {
            public Transform transform;
            public Vector3 basePosition;
            public Quaternion baseRotation;
            public Vector3 axis;   // Drift: tumble axis
            public float phase;
            public float speed;    // Soar/Swim: radians per second around the cell (sign = direction)
                                   // Ground: cells per second
            public float radius;   // Soar/Swim: circle radius; Ground: how far it strays from basePosition
            public float span;     // size on the map, in cells

            // Ground wandering
            public Vector3 position, target;
            public float heading;  // yaw in degrees
            public bool moving;
            public float restUntil;

            // Wing beat
            public MeshRenderer renderer;
            public MaterialPropertyBlock block;
            public float flapRate;      // radians per second; 0 = no flapping
            public float flapAmplitude;
            public float flapPhase;     // accumulated, so the beat can speed up without a jump

            // Legs (Ground walkers and hoppers): the shader swings everything below the hips. The
            // cycle advances with the distance actually covered, so feet don't slide.
            public float strideAmplitude; // radians at full stride; 0 = no legs
            public float legLength;       // hip height, in cells
            public float stridePhase;
            public float strideFactor;    // 0 standing .. 1 full stride
            public float gaitSpeed;       // smoothed ground speed, cells per second
            public Vector3 lastPosition;
            public bool hasLastPosition;

            // Travelling: place in the formation (x = right, z = forward of the heading)
            public Vector3 slot;
        }

        private readonly List<Member> members = new();
        private readonly System.Random motionRng = new();
        private Trip trip;
        private float heading; // travel direction, degrees (0 = +Z)

        private class Leg
        {
            public List<Vector3> points = new(); // offsets from the start tile (y = surface height)
            public float length, duration, speed;
            public float startTime;              // since the trip began
            public bool faceForward = true;      // false: keep facing the way it was (backing off)
            public float pauseAfter;             // attack: strike at the end of the charge leg
        }

        private class Trip
        {
            public readonly List<Leg> legs = new();
            public HexCell destination;
            public HexCell strikeTarget;
            public float started;
            public float marchEnd;  // trip time when the last leg ends
            public bool struck, arrived;
        }

        public IReadOnlyList<Member> Members => members;

        public void Init(SpeciesDefinition def, ColonyStyle style, ColonyGait gait, HexCell cell, float memberSpan)
        {
            Definition = def;
            Style      = style;
            Gait       = gait;
            Cell       = cell;
            MemberSpan = memberSpan;
        }

        public void AddMember(Member m) => members.Add(m);

        // Ground animals walk on land, swimmers, floaters and microbes stay in water, fliers go
        // anywhere. Only soaring birds cross mountains.
        public bool CanEnter(HexCell cell)
        {
            if (cell == null || cell.Terrain == null) return false;
            if (cell.IsMountain) return Style == ColonyStyle.Soar;
            return Style switch
            {
                ColonyStyle.Ground => !cell.Terrain.IsWater,
                ColonyStyle.Swim or ColonyStyle.Float or ColonyStyle.Drift => cell.Terrain.IsWater,
                ColonyStyle.Soar or ColonyStyle.Swarm => true,
                _ => false,
            };
        }

        // Moves to a neighbouring tile. Returns false if the group can't go there right now.
        public bool MoveTo(HexCell target) => MoveAlong(new[] { target });

        // Travels through a chain of tiles, each a neighbour of the one before it, without stopping
        // in between. The group belongs to the last tile from the moment it sets out.
        public bool MoveAlong(IReadOnlyList<HexCell> path)
        {
            if (!CanMove || IsBusy || path == null || path.Count == 0) return false;
            var points = new List<Vector3> { Vector3.up * Cell.SurfaceHeight };
            var prev = Cell;
            var offset = Vector3.zero;
            foreach (var next in path)
            {
                if (next == null || next == prev || !CanEnter(next) || !AreNeighbors(prev, next)) return false;
                offset += GridStep(prev, next);
                points.Add(new Vector3(offset.x, next.SurfaceHeight, offset.z));
                prev = next;
            }

            var t = new Trip { destination = prev };
            t.legs.Add(MakeLeg(points, TravelSpeed()));
            Begin(t);
            Cell = prev;
            return true;
        }

        // Charges a neighbouring tile up to its border, strikes and backs off home, still facing it.
        // Struck fires at the moment of the strike, so combat can resolve there.
        public bool Attack(HexCell target)
        {
            if (!CanMove || IsBusy || target == null || target == Cell || !AreNeighbors(Cell, target)) return false;
            var home   = Vector3.up * Cell.SurfaceHeight;
            var reach  = GridStep(Cell, target) * StrikeReach;
            var border = new Vector3(reach.x, Cell.SurfaceHeight, reach.z); // stays on its own tile's height

            var t = new Trip { destination = Cell, strikeTarget = target };
            var charge = MakeLeg(new List<Vector3> { home, border }, TravelSpeed() * ChargeSpeed);
            charge.pauseAfter = StrikeHold;
            var back = MakeLeg(new List<Vector3> { border, home }, TravelSpeed() * BackOffSpeed);
            back.faceForward = false;
            t.legs.Add(charge);
            t.legs.Add(back);
            Begin(t);
            return true;
        }

        // Cells per second when travelling; big animals take longer strides but each takes longer
        private float TravelSpeed() => Style switch
        {
            ColonyStyle.Ground => Gait switch
            {
                ColonyGait.Hop     => 1.1f,
                ColonyGait.Slither => 0.55f,
                _                  => Mathf.Lerp(0.85f, 0.65f, Mathf.InverseLerp(0.4f, 2.5f, MemberSpan)),
            },
            ColonyStyle.Soar  => 1.3f,
            ColonyStyle.Swarm => 1.0f,
            ColonyStyle.Swim  => 0.8f,
            ColonyStyle.Float => 0.5f,
            ColonyStyle.Drift => 0.35f,
            _                 => 0.8f,
        };

        private static Leg MakeLeg(List<Vector3> points, float speed)
        {
            var leg = new Leg { points = points, speed = speed };
            for (int i = 1; i < points.Count; i++)
                leg.length += Flat(points[i] - points[i - 1]).magnitude;
            leg.duration = leg.length / speed + RampTime;
            return leg;
        }

        private void Begin(Trip t)
        {
            float time = SetOffDelay;
            foreach (var leg in t.legs)
            {
                leg.startTime = time;
                time += leg.duration + leg.pauseAfter;
            }
            t.marchEnd = time - t.legs[t.legs.Count - 1].pauseAfter;
            t.started  = Time.time;

            var first = t.legs[0];
            heading = Yaw(first.points[1] - first.points[0]);
            AssignSlots();
            trip = t;
        }

        // A compact pack facing the travel direction; members already ahead take the front rows,
        // members on the left the left side, so nobody crosses through the group to get to its place.
        private void AssignSlots()
        {
            var toHeading = Quaternion.Euler(0f, -heading, 0f);
            if (Style is ColonyStyle.Swarm or ColonyStyle.Drift)
            {
                // clouds just tighten up around the centre
                foreach (var m in members) m.slot = toHeading * Flat(m.transform.localPosition) * 0.6f;
                return;
            }

            int n = members.Count;
            int cols = Mathf.CeilToInt(Mathf.Sqrt(n));
            int rows = Mathf.CeilToInt(n / (float)cols);
            float spacing = Mathf.Max(MemberSpan * (Style == ColonyStyle.Soar ? 1.1f : 0.8f), 0.08f);
            // keep the pack inside about one tile; big animals overlap a little
            spacing = Mathf.Min(spacing, 0.75f / Mathf.Max(1, Mathf.Max(cols, rows) - 1));

            var order = new List<Member>(members);
            order.Sort((a, b) => (toHeading * b.transform.localPosition).z.CompareTo((toHeading * a.transform.localPosition).z));
            for (int r = 0, i = 0; r < rows; r++)
            {
                int inRow = Mathf.Min(cols, n - i);
                var row = order.GetRange(i, inRow);
                row.Sort((a, b) => (toHeading * a.transform.localPosition).x.CompareTo((toHeading * b.transform.localPosition).x));
                for (int c = 0; c < inRow; c++, i++)
                {
                    float x = (c - (inRow - 1) * 0.5f) * spacing;
                    float z = ((rows - 1) * 0.5f - r) * spacing * 1.1f;
                    if (Style == ColonyStyle.Soar) z -= Mathf.Abs(x) * 0.6f; // loose V
                    // a little irregularity so it doesn't read as a parade
                    x += (float)(motionRng.NextDouble() - 0.5) * spacing * 0.25f;
                    z += (float)(motionRng.NextDouble() - 0.5) * spacing * 0.25f;
                    row[c].slot = new Vector3(x, 0f, z);
                }
            }
        }

        private void Update()
        {
            float t = Time.time, dt = Time.deltaTime;
            float w = 0f, lunge = 0f;
            float turnRate = 0f;

            if (trip != null)
            {
                float tt = t - trip.started;
                w = Mathf.SmoothStep(0f, 1f, tt / GatherTime) *
                    (1f - Mathf.SmoothStep(0f, 1f, (tt - trip.marchEnd) / SettleTime));
                // The path is relative to the start tile, so stop following it once the group has
                // been handed over to its destination tile (Arrive), or it lands one tile too far.
                if (!trip.arrived)
                {
                    float before = heading;
                    transform.localPosition = SamplePath(tt, dt, out lunge);
                    turnRate = dt > 0f ? Mathf.DeltaAngle(before, heading) / dt : 0f;
                    if (tt >= trip.marchEnd) Arrive();
                }
                if (tt >= trip.marchEnd + SettleTime)
                {
                    trip = null;
                    w = 0f;
                    Arrived?.Invoke(this);
                }
            }

            var hq = Quaternion.Euler(0f, heading, 0f);
            foreach (var m in members)
            {
                if (m.transform == null) continue;
                if (m.flapRate > 0f) Flap(m, t, dt, w);

                Vector3 pos;
                Quaternion rot;
                if (w < 0.999f) IdlePose(m, t, dt, out pos, out rot);
                else { pos = m.transform.localPosition; rot = m.transform.localRotation; }
                if (w > 0.001f)
                {
                    TravelPose(m, t, hq, turnRate, lunge, out var tpos, out var trot);
                    pos = Vector3.Lerp(pos, tpos, w);
                    rot = Quaternion.Slerp(rot, trot, w);
                }
                m.transform.localPosition = pos;
                m.transform.localRotation = rot;
                if (m.strideAmplitude > 0f) Stride(m, dt);
            }
        }

        // Advances the leg cycle by the ground the animal covered since last frame: one full cycle
        // per stride length (each foot sweeps 2 · legLength · tan(amplitude) while planted).
        private static void Stride(Member m, float dt)
        {
            var p = m.transform.position;
            if (m.hasLastPosition && dt > 0f)
            {
                var d = p - m.lastPosition;
                d.y = 0f;
                float v = d.magnitude / dt;
                if (v < 5f) // larger: the map wrap moved the whole tile, not the animal
                {
                    m.gaitSpeed    = Mathf.Lerp(m.gaitSpeed, v, 1f - Mathf.Exp(-dt * 10f));
                    float strideLength = 2f * m.legLength * Mathf.Tan(m.strideAmplitude);
                    m.stridePhase += v * dt / Mathf.Max(strideLength, 1e-4f) * Mathf.PI * 2f;
                }
            }
            m.lastPosition    = p;
            m.hasLastPosition = true;
            // full stride from about one and a half leg lengths per second
            m.strideFactor = Mathf.Clamp01(m.gaitSpeed / Mathf.Max(m.legLength * 1.5f, 1e-4f));
            m.block.SetFloat(StrideId, m.strideAmplitude * m.strideFactor);
            m.block.SetFloat(StridePhaseId, m.stridePhase);
            m.renderer.SetPropertyBlock(m.block);
        }

        // Where the group centre is at trip time tt (relative to the tile it set out from), turning
        // the heading towards the way it's going. lunge = 0..1 strike pose while holding at a border.
        private Vector3 SamplePath(float tt, float dt, out float lunge)
        {
            lunge = 0f;
            Leg leg = trip.legs[0];
            foreach (var l in trip.legs)
            {
                leg = l;
                if (tt < l.startTime + l.duration + l.pauseAfter) break;
            }
            float into = tt - leg.startTime;
            if (into > leg.duration && leg.pauseAfter > 0f)
            {
                float p = (into - leg.duration) / leg.pauseAfter;
                lunge = Mathf.Sin(Mathf.Clamp01(p) * Mathf.PI);
                if (!trip.struck)
                {
                    trip.struck = true;
                    Struck?.Invoke(this, trip.strikeTarget);
                }
            }
            float u = Mathf.Clamp01(into / leg.duration);

            float d = leg.length * Progress(u, Mathf.Min(0.5f, RampTime / leg.duration));
            var pts = leg.points;
            int seg = 1;
            float along = d;
            while (seg < pts.Count - 1 && along > Flat(pts[seg] - pts[seg - 1]).magnitude)
            {
                along -= Flat(pts[seg] - pts[seg - 1]).magnitude;
                seg++;
            }
            var a = pts[seg - 1];
            var b = pts[seg];
            float segLen = Flat(b - a).magnitude;
            float s = segLen > 1e-4f ? Mathf.Clamp01(along / segLen) : 1f;

            if (leg.faceForward && into >= 0f && into <= leg.duration)
            {
                // look ahead along the next segment once past the middle of a tile crossing
                var dir = s > 0.85f && seg < pts.Count - 1 ? pts[seg + 1] - b : b - a;
                heading = Mathf.MoveTowardsAngle(heading, Yaw(dir), TurnRate * dt);
            }

            var pos = Vector3.Lerp(a, b, s);
            // stay on each tile's top and step up or down around the border
            pos.y = Mathf.Lerp(a.y, b.y, Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(0.35f, 0.65f, s)));
            return pos;
        }

        // Fraction of the way along a leg at time fraction u: speed ramps up, cruises, ramps down.
        private static float Progress(float u, float ramp)
        {
            if (ramp <= 0f) return u;
            float vPeak = 1f / (1f - ramp);
            if (u < ramp)      return 0.5f * vPeak * u * u / ramp;
            if (u < 1f - ramp) return vPeak * (u - ramp * 0.5f);
            return 1f - 0.5f * vPeak * (1f - u) * (1f - u) / ramp;
        }

        // Settle into the destination tile: reparent there (the position doesn't change) and let
        // ground animals pick up their wandering from where they stand.
        private void Arrive()
        {
            trip.arrived = true;
            if (trip.destination != null && transform.parent != trip.destination.transform)
            {
                transform.SetParent(trip.destination.transform, true);
                transform.localPosition = Vector3.up * trip.destination.SurfaceHeight;
            }
            if (Style != ColonyStyle.Ground) return;
            var hq = Quaternion.Euler(0f, heading, 0f);
            foreach (var m in members)
            {
                m.position  = m.target = hq * m.slot;
                m.heading   = heading;
                m.moving    = false;
                m.restUntil = Time.time + SettleTime + (float)(motionRng.NextDouble() * 2.5);
            }
        }

        // ---- Travelling poses ------------------------------------------------------------------

        private void TravelPose(Member m, float t, Quaternion hq, float turnRate, float lunge, out Vector3 pos, out Quaternion rot)
        {
            pos = hq * m.slot;
            pos.y = m.basePosition.y;
            rot = hq;
            float p = m.phase;
            var forward = hq * Vector3.forward;

            switch (Style)
            {
                case ColonyStyle.Ground:
                {
                    // a quicker, bouncier version of the wandering gait, in step with the legs
                    float step = GaitCycle(m, t, 9f);
                    float k    = GaitStrength(m);
                    float lift = 0f, roll = 0f, yaw = 0f, pitch = 0f;
                    switch (Gait)
                    {
                        case ColonyGait.Walk:
                            // highest as the legs pass under the body
                            lift  = Mathf.Abs(Mathf.Cos(step)) * 0.03f * k;
                            roll  = Mathf.Sin(step) * 3f * k;
                            pitch = Mathf.Sin(step * 2f) * 1.5f * k;
                            break;
                        case ColonyGait.Hop:
                        {
                            float h = Mathf.Sin(step * 0.5f);
                            lift  = Mathf.Abs(h) * 0.22f * k;
                            pitch = -h * 8f * k; // nose up taking off, down on landing
                            break;
                        }
                        case ColonyGait.Slither:
                            yaw = Mathf.Sin(step * 0.6f) * 22f;
                            pos += hq * Vector3.right * (Mathf.Sin(step * 0.6f - 1f) * 0.15f * m.span);
                            break;
                    }
                    pos += Vector3.up * (lift * m.span) + forward * (lunge * 0.12f * Mathf.Max(m.span, 0.4f));
                    rot = hq * Quaternion.Euler(pitch + lunge * 12f, yaw, roll);
                    break;
                }
                case ColonyStyle.Soar:
                {
                    // steady flight, banking into turns
                    float bank = Mathf.Clamp(-turnRate * 0.25f, -30f, 30f);
                    pos += Vector3.up * (Mathf.Sin(t * 1.2f + p) * 0.03f) + forward * (lunge * 0.2f);
                    pos.y -= lunge * 0.25f; // dive at the target
                    rot = hq * Quaternion.Euler(lunge * 25f, 0f, bank);
                    break;
                }
                case ColonyStyle.Swim:
                    pos += Vector3.up * (Mathf.Sin(t * 1.5f + p) * 0.006f) + forward * (lunge * 0.15f);
                    if (Backward && (trip == null || trip.strikeTarget == null))
                    {
                        // jetting tail first: surges with each mantle pulse instead of a tail wag
                        float pulse = Mathf.Sin(t * 4f + p);
                        pos += forward * (pulse * 0.02f * m.span);
                        rot = hq * Quaternion.Euler(pulse * 2f, 180f, 0f);
                    }
                    else // attacks are made head first; a backward swimmer then backs off, still facing the target
                        rot = hq * Quaternion.Euler(0f, Mathf.Sin(t * 7f + p * 3f) * 10f, 0f);
                    break;
                case ColonyStyle.Float:
                    pos += Vector3.up * (Mathf.Sin(t * 2.2f + p) * 0.008f) + forward * (lunge * 0.1f);
                    rot = hq * Quaternion.Euler(Mathf.Sin(t * 2.2f + p) * 5f - 3f, 0f, Mathf.Sin(t * 1.7f + p) * 4f);
                    break;
                case ColonyStyle.Swarm:
                {
                    var jitter = new Vector3(Mathf.Sin(t * 2.3f + p), Mathf.Sin(t * 1.7f + p * 2f), Mathf.Cos(t * 2.9f + p)) * 0.03f;
                    pos += jitter + forward * (lunge * 0.15f);
                    rot = hq * Quaternion.Euler(0f, Mathf.Sin(t * 1.9f + p) * 15f, 0f);
                    break;
                }
                case ColonyStyle.Drift:
                    // microbes don't face anywhere; they keep tumbling as they drift along
                    pos += Vector3.up * (Mathf.Sin(t * 0.8f + p) * 0.02f) + forward * (lunge * 0.08f);
                    rot = Quaternion.AngleAxis(t * 12f + p * 57f, m.axis) * m.baseRotation;
                    break;
            }
        }

        // ---- Idle poses (settled on the tile) --------------------------------------------------

        private void IdlePose(Member m, float t, float dt, out Vector3 pos, out Quaternion rot)
        {
            pos = m.basePosition;
            rot = m.baseRotation;
            switch (Style)
            {
                case ColonyStyle.Ground:
                    Wander(m, t, dt, out pos, out rot);
                    break;
                case ColonyStyle.Drift:
                    rot = Quaternion.AngleAxis(t * 12f + m.phase * 57f, m.axis) * m.baseRotation;
                    pos = m.basePosition + Vector3.up * (Mathf.Sin(t * 0.8f + m.phase) * 0.02f);
                    break;
                case ColonyStyle.Float:
                    rot = m.baseRotation * Quaternion.Euler(Mathf.Sin(t * 1.1f + m.phase) * 4f, 0f,
                                                            Mathf.Sin(t * 0.9f + m.phase * 2f) * 5f);
                    pos = m.basePosition + Vector3.up * (Mathf.Sin(t * 1.3f + m.phase) * 0.006f);
                    break;
                case ColonyStyle.Soar:
                {
                    float a   = m.phase + t * m.speed;
                    var ahead = new Vector3(-Mathf.Sin(a), 0f, Mathf.Cos(a)) * Mathf.Sign(m.speed);
                    pos = new Vector3(Mathf.Cos(a) * m.radius, m.basePosition.y + Mathf.Sin(t * 0.5f + m.phase) * 0.04f, Mathf.Sin(a) * m.radius);
                    rot = Quaternion.LookRotation(ahead) * Quaternion.Euler(0f, 0f, 22f * Mathf.Sign(m.speed));
                    break;
                }
                case ColonyStyle.Swim:
                {
                    float a   = m.phase + t * m.speed;
                    var ahead = new Vector3(-Mathf.Sin(a), 0f, Mathf.Cos(a)) * Mathf.Sign(m.speed);
                    pos = new Vector3(Mathf.Cos(a) * m.radius, m.basePosition.y + Mathf.Sin(t * 0.9f + m.phase) * 0.008f, Mathf.Sin(a) * m.radius);
                    rot = Backward
                        ? Quaternion.LookRotation(-ahead) * Quaternion.Euler(Mathf.Sin(t * 2f + m.phase) * 2f, 0f, 0f)
                        : Quaternion.LookRotation(ahead) * Quaternion.Euler(0f, Mathf.Sin(t * 3f + m.phase * 3f) * 6f, 0f);
                    break;
                }
                case ColonyStyle.Swarm:
                {
                    float p = m.phase;
                    var jitter = new Vector3(Mathf.Sin(t * 2.3f + p) + 0.5f * Mathf.Sin(t * 5.1f + p * 3f),
                                             Mathf.Sin(t * 1.7f + p * 2f),
                                             Mathf.Cos(t * 2.9f + p) + 0.5f * Mathf.Cos(t * 4.3f + p * 5f)) * 0.05f;
                    pos = m.basePosition + jitter;
                    rot = m.baseRotation * Quaternion.Euler(0f, Mathf.Sin(t * 1.9f + p) * 40f, 0f);
                    break;
                }
            }
        }

        // Wing / fin beat. Soarers glide most of the time when settled and beat steadily when
        // travelling; everything beats a little faster on the move.
        private void Flap(Member m, float t, float dt, float w)
        {
            m.flapPhase += dt * m.flapRate * (1f + 0.4f * w);
            float burst = Style == ColonyStyle.Soar ? Mathf.SmoothStep(0f, 1f, (Mathf.Sin(t * 0.5f + m.phase) - 0.35f) * 3f) : 1f;
            burst = Mathf.Lerp(burst, 1f, w);
            m.block.SetFloat(FlapId, Mathf.Sin(m.flapPhase + m.phase) * m.flapAmplitude * burst);
            m.renderer.SetPropertyBlock(m.block);
        }

        // Rests a few seconds, turns towards a nearby spot and walks, hops or slithers there.
        private void Wander(Member m, float t, float dt, out Vector3 pos, out Quaternion rot)
        {
            if (!m.moving)
            {
                if (t >= m.restUntil) PickTarget(m);
                // idle: glance around a little
                pos = m.position;
                rot = Quaternion.Euler(0f, m.heading + Mathf.Sin(t * 0.4f + m.phase) * 5f, 0f);
                return;
            }

            var to = m.target - m.position;
            to.y = 0f;
            float dist = to.magnitude;
            float turn = Mathf.DeltaAngle(m.heading, Mathf.Atan2(to.x, to.z) * Mathf.Rad2Deg);
            m.heading += Mathf.Clamp(turn, -70f * dt, 70f * dt);
            // turn mostly on the spot, then set off
            if (Mathf.Abs(turn) < 30f)
                m.position += Quaternion.Euler(0f, m.heading, 0f) * Vector3.forward * Mathf.Min(m.speed * dt, dist);
            if (dist < 0.005f)
            {
                m.moving    = false;
                m.restUntil = t + (float)(2.0 + motionRng.NextDouble() * 6.0);
            }

            // gait: a small bob and sway while walking, bounds for hoppers, an S-wag for snakes
            float step = GaitCycle(m, t, 6f);
            float k    = GaitStrength(m);
            float lift = 0f, roll = 0f, yaw = 0f;
            switch (Gait)
            {
                case ColonyGait.Walk:    lift = Mathf.Abs(Mathf.Cos(step)) * 0.015f * k; roll = Mathf.Sin(step) * 2f * k; break;
                case ColonyGait.Hop:     lift = Mathf.Abs(Mathf.Sin(step * 0.5f)) * 0.18f * k; break;
                case ColonyGait.Slither: yaw = Mathf.Sin(step * 0.6f) * 14f; break;
            }
            pos = m.position + Vector3.up * (lift * m.span);
            rot = Quaternion.Euler(0f, m.heading + yaw, roll);
        }

        // A random spot around the animal's home, not too close to where its colony-mates are or are heading.
        private void PickTarget(Member m)
        {
            for (int attempt = 0; attempt < 6; attempt++)
            {
                float a = (float)(motionRng.NextDouble() * Mathf.PI * 2.0);
                float r = m.radius * Mathf.Sqrt((float)motionRng.NextDouble());
                var spot = m.basePosition + new Vector3(Mathf.Cos(a) * r, 0f, Mathf.Sin(a) * r);
                bool clear = true;
                foreach (var other in members)
                {
                    float room = (m.span + other.span) * 0.4f;
                    if (other != m && (Vector3.Distance(spot, other.position) < room || Vector3.Distance(spot, other.target) < room))
                    {
                        clear = false;
                        break;
                    }
                }
                if (!clear) continue;
                m.target = spot;
                m.moving = true;
                return;
            }
            m.restUntil = Time.time + 1f; // boxed in; try again shortly
        }

        // ---- Helpers ---------------------------------------------------------------------------

        // Where an animal is in its gait: the leg cycle for animals with legs, otherwise a steady
        // beat that is slower for big animals (rate = beats per second at span 1).
        private static float GaitCycle(Member m, float t, float rate) =>
            m.strideAmplitude > 0f ? m.stridePhase : t * rate / Mathf.Sqrt(Mathf.Max(m.span, 0.3f)) + m.phase;

        // How much the body bobs: with legs, only as much as it is actually striding
        private static float GaitStrength(Member m) => m.strideAmplitude > 0f ? m.strideFactor : 1f;

        private static bool AreNeighbors(HexCell a, HexCell b)
        {
            var grid = HexGrid.Instance;
            return grid != null && grid.GetNeighbors(a).Contains(b);
        }

        // Offset from one tile's centre to a neighbour's, taking the short way across the wrap seam
        private static Vector3 GridStep(HexCell from, HexCell to)
        {
            var d = Flat(to.transform.localPosition - from.transform.localPosition);
            var grid = HexGrid.Instance;
            if (grid != null) d.x -= Mathf.Round(d.x / grid.WrapWidth) * grid.WrapWidth;
            return d;
        }

        private static Vector3 Flat(Vector3 v) => new(v.x, 0f, v.z);
        private static float Yaw(Vector3 dir) => Mathf.Atan2(dir.x, dir.z) * Mathf.Rad2Deg;
    }
}
