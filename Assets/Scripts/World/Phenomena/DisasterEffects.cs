using System.Collections.Generic;
using System.Linq;
using NaturalHistory.Core;
using NaturalHistory.Evolution;
using NaturalHistory.Players;
using NaturalHistory.Progression;
using NaturalHistory.Territory;
using UnityEngine;

namespace NaturalHistory.World
{
    // What a natural event (NaturalEvents.Struck) does to the animals on the tiles it hits: every
    // group there loses a share of its maximum health, by default half. Some events hit one layer of
    // life harder, up to three quarters: winds (tornadoes, sandstorms, blizzards) the fliers in the
    // sky, tsunamis everything living in the water, earthquakes the animals underground. A group
    // at 0 HP is wiped out.
    //
    // Hard times drive evolution: for each of its groups that lives through the event, a player
    // gains EP (SurvivorPoints, up to MaxPointsPerEvent an event), the human through
    // ProgressionManager, the AI players through AiPlayers.
    public class DisasterEffects : MonoBehaviour
    {
        private const float Harder = 0.75f;          // the share for the layer an event hits hardest
        private const int SurvivorPoints = 8;        // EP per group of a player that lives through it
        private const int MaxPointsPerEvent = 24;

        // Share of maximum HP lost by every group on the tiles hit
        private static readonly Dictionary<Phenomenon, float> loss = new()
        {
            { Phenomenon.Meteor, 0.6f }, { Phenomenon.Eruption, 0.6f },
            { Phenomenon.Tornado, 0.5f }, { Phenomenon.Sandstorm, 0.4f }, { Phenomenon.Blizzard, 0.4f },
            { Phenomenon.Flood, 0.5f }, { Phenomenon.Rockslide, 0.5f }, { Phenomenon.Avalanche, 0.5f },
            { Phenomenon.Earthquake, 0.5f }, { Phenomenon.Tsunami, 0.5f }, { Phenomenon.GlacierCalving, 0.3f },
        };

        private NaturalEvents events;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Bootstrap()
        {
            if (FindAnyObjectByType<HexGrid>() == null || FindAnyObjectByType<DisasterEffects>() != null) return;
            new GameObject("DisasterEffects").AddComponent<DisasterEffects>();
        }

        private void Update()
        {
            if (events != null || NaturalEvents.Instance == null) return;
            events = NaturalEvents.Instance; // it may start after this component
            events.Struck += OnStruck;
        }

        private void OnDestroy()
        {
            if (events != null) events.Struck -= OnStruck;
        }

        // The share `g` loses to `kind`
        public static float LossFor(Phenomenon kind, ColonyGroup g)
        {
            float share = loss.TryGetValue(kind, out var s) ? s : 0.5f;
            bool harder = kind switch
            {
                Phenomenon.Tornado or Phenomenon.Sandstorm or Phenomenon.Blizzard => Niches.IsFlyer(g.Definition) || Niches.LayerOf(g.Niche) == MapLayer.Sky,
                Phenomenon.Tsunami    => g.Cell != null && g.Cell.IsWater,
                Phenomenon.Earthquake => g.Niche == Niche.Underground || Niches.InSoil(g.Definition),
                _ => false,
            };
            return harder ? Mathf.Max(share, Harder) : share;
        }

        private void OnStruck(Phenomenon kind, HexCell center, IReadOnlyList<HexCell> area)
        {
            var colonies = SpeciesColonies.Instance;
            if (colonies == null || area == null) return;
            var hit = new HashSet<HexCell>(area.Where(c => c != null));
            var groups = colonies.Groups.Where(g => g != null && g.Definition != null && g.Cell != null && hit.Contains(g.Cell)).ToList();
            if (groups.Count == 0) return;

            string name = NaturalEvents.InSentence(Loc.T(NaturalEvents.Names[(int)kind]));
            var survivors = new Dictionary<int, int>(); // player index -> groups that lived through it
            int humanLost = 0, humanWiped = 0;
            bool changed = false;
            foreach (var g in groups)
            {
                float dealt = g.MaxHp * LossFor(kind, g) * (1f - TraitBonuses.Effects(g).disasterResist); // its items may soften it
                g.Hp -= dealt;
                bool human = g.Owner != null && g.Owner.IsHuman;
                if (human) humanLost++;
                if (g.Hp <= 0f)
                {
                    if (human) humanWiped++;
                    EvolutionManager.Instance?.RemoveCopy(g);
                    colonies.DespawnColony(g);
                    changed = true;
                    continue;
                }
                if (g.Owner != null) survivors[g.Owner.Index] = survivors.TryGetValue(g.Owner.Index, out int n) ? n + 1 : 1;
            }
            if (changed) TerritoryManager.Instance?.Refresh();

            var humanPlayer = PlayerManager.Instance != null ? PlayerManager.Instance.Human : null;
            foreach (var (player, count) in survivors)
            {
                int ep = Mathf.Min(MaxPointsPerEvent, count * SurvivorPoints);
                if (humanPlayer != null && player == humanPlayer.Index)
                {
                    ProgressionManager.Instance?.AddPoints(ep);
                    NaturalEvents.Announce(Loc.F("Your animals lived through the {0}: hardship drives evolution (+{1} EP)", name, ep), center);
                }
                else AiPlayers.Instance?.AddPoints(player, ep);
            }
            if (humanWiped > 0)
                NaturalEvents.Announce(Loc.F("The {0} wiped out {1} of your groups", name, humanWiped), center);
            else if (humanLost > 0 && !survivors.ContainsKey(humanPlayer?.Index ?? -1))
                NaturalEvents.Announce(Loc.F("The {0} hit {1} of your groups", name, humanLost), center);
        }
    }
}
