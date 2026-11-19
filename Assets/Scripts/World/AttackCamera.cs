using UnityEngine;

namespace NaturalHistory.World
{
    // When an enemy (another player's group or a wild one) attacks one of the human player's groups,
    // the camera glides there and the view switches to the layer the fight is in, so the attack is
    // seen as it plays out. Busy while it does, so whoever plays the enemy turn (AiPlayers) can wait
    // and show its attacks one at a time.
    public class AttackCamera : MonoBehaviour
    {
        private const float GlideSeconds = 0.6f;
        private const float WatchSeconds = 1.6f; // the glide, the charge and the blow

        private static float busyUntil;
        public static bool Busy => Time.unscaledTime < busyUntil;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Bootstrap()
        {
            if (FindAnyObjectByType<HexGrid>() == null || FindAnyObjectByType<AttackCamera>() != null) return;
            new GameObject("AttackCamera").AddComponent<AttackCamera>();
        }

        // the enemy turn waits while an attack on the player is being watched
        private void Awake() => Players.AiPlayers.HoldForCamera = () => Busy;

        private void OnEnable()  => ColonyGroup.AttackStarted += OnAttack;
        private void OnDisable() => ColonyGroup.AttackStarted -= OnAttack;

        private static void OnAttack(ColonyGroup attacker, HexCell target)
        {
            if (attacker == null || target == null || (attacker.Owner != null && attacker.Owner.IsHuman)) return;
            var defender = Combat.Defender(attacker, target);
            if (defender == null || defender.Owner == null || !defender.Owner.IsHuman) return;

            // the layer the fight is in
            if (!UnderView.InLayer(defender, UnderView.Layer))
                UnderView.Set(UnderView.InLayer(defender, MapLayer.Surface) ? MapLayer.Surface
                            : UnderView.InLayer(defender, MapLayer.Under) ? MapLayer.Under : MapLayer.Sky);
            var cam = CameraController.Main;
            if (cam != null) cam.GlideTo(target.transform.position, GlideSeconds);
            busyUntil = Time.unscaledTime + WatchSeconds;
        }
    }
}
