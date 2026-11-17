using UnityEngine;

namespace NaturalHistory.World
{
    // Fliers that live on the ground or the water (avocets, flamingos, ducks, pelicans, kingfishers,
    // ladybirds: Niches.IsFlyer, but a Ground, Float or Fixed map style) walk, swim or sit in their
    // colony, but in the sky view they are always on the wing: they take off over a second, circle
    // over the tile (banking into the turn, wings beating) and fly in a loose V when the group moves
    // to another tile, landing again when the view leaves the sky. The lift to the cloud deck
    // (DepthOffset, set by HexGrid.ShowGroupsForView) still comes on top.
    public partial class ColonyGroup
    {
        private const float FlightHeight = 0.35f; // above the group's root (and so above the deck in the sky view)
        private const float TakeOffTime  = 1.1f;  // seconds to take off / land

        private float air;       // 0 settled in the colony .. 1 flying
        private int canFly = -1; // -1 not worked out yet

        private bool Grounded => Style is ColonyStyle.Ground or ColonyStyle.Float or ColonyStyle.Fixed;

        private bool CanFly
        {
            get
            {
                if (canFly < 0) canFly = Definition != null && Grounded && Niches.IsFlyer(Definition) ? 1 : 0;
                return canFly == 1;
            }
        }

        private bool WantsAir => CanFly && UnderView.Layer == MapLayer.Sky;

        private void UpdateAir(float dt)
        {
            float to = WantsAir ? 1f : 0f;
            air = Mathf.MoveTowards(air, to, dt / TakeOffTime);
        }

        private float Airborne => Mathf.SmoothStep(0f, 1f, air);

        // Blends the member from its colony pose into flight: circling the tile when settled, in
        // formation behind the heading when travelling (w)
        private void FlightPose(Member m, float t, float w, Quaternion hq, float turnRate, ref Vector3 pos, ref Quaternion rot)
        {
            float k = Airborne;
            if (k <= 0.001f) return;
            float height = FlightHeight + m.span * 0.3f + 0.05f * Mathf.Sin(m.phase * 3f);

            // settled: each member circles the tile on its own ring, about half of them the other way
            float flat   = new Vector2(m.basePosition.x, m.basePosition.z).magnitude;
            float radius = Mathf.Clamp(flat, 0.1f, 0.3f) + 0.06f;
            float dir    = Mathf.Sin(m.phase * 7.1f) >= 0f ? 1f : -1f;
            float a      = m.phase + t * 0.55f * dir;
            var ahead    = new Vector3(-Mathf.Sin(a), 0f, Mathf.Cos(a)) * dir;
            var circlePos = new Vector3(Mathf.Cos(a) * radius, height + Mathf.Sin(t * 0.7f + m.phase) * 0.03f, Mathf.Sin(a) * radius);
            var circleRot = Quaternion.LookRotation(ahead) * Quaternion.Euler(0f, 0f, 20f * dir);

            // travelling: the formation slot, flying level and banking into turns
            var travelPos = hq * m.slot;
            travelPos.y = height + Mathf.Sin(t * 1.2f + m.phase) * 0.03f;
            var travelRot = hq * Quaternion.Euler(0f, 0f, Mathf.Clamp(-turnRate * 0.25f, -30f, 30f));

            var flyPos = Vector3.Lerp(circlePos, travelPos, w);
            var flyRot = Quaternion.Slerp(circleRot, travelRot, w);
            pos = Vector3.Lerp(pos, flyPos, k);
            rot = Quaternion.Slerp(rot, flyRot, k);
        }

        // Wing beat amplitude: the member's own on the ground or water, a steady beat in the air
        // once its flight model (wings spread) is showing; a folded-wing model doesn't beat
        private float FlapAmplitude(Member m) => m.showingFlight ? m.airFlapAmplitude : m.flapAmplitude;

        // The take-off: a moment after leaving the ground the resting model gives way to the flight
        // model, its wings opening out from folded against the body to full span over a few tenths
        // of a second (the reverse on landing), so the change reads as the bird spreading its wings
        private const float SwapAt = 0.25f, UnfoldTime = 0.3f; // in units of `air`

        private void FlightModel(Member m, ref Vector3 scale)
        {
            if (m.flightMesh == null || m.filter == null) return;
            bool fly = air > SwapAt;
            if (fly != m.showingFlight)
            {
                m.filter.sharedMesh = fly ? m.flightMesh : m.restMesh;
                m.showingFlight = fly;
            }
            if (!fly) return;
            float open = Mathf.SmoothStep(0f, 1f, (air - SwapAt) / UnfoldTime);
            scale.x *= Mathf.Lerp(0.15f, 1f, open);              // wings opening out
            scale.z *= Mathf.Lerp(0.85f, 1f, open);              // neck and legs stretching out
        }
    }
}
