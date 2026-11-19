using System.Linq;
using System.Text;
using NaturalHistory.World;
using UnityEditor;
using UnityEngine;

namespace NaturalHistory.EditorTools
{
    // Debugging aid: while playing in the editor, writes the map's animal groups (owner, species,
    // tile, layer, whether they are shown) to Temp/nh_groups.txt every few seconds.
    [InitializeOnLoad]
    public static class GroupsDump
    {
        private static double next;

        static GroupsDump() => EditorApplication.update += Tick;

        private static void Tick()
        {
            if (!EditorApplication.isPlaying || EditorApplication.timeSinceStartup < next) return;
            next = EditorApplication.timeSinceStartup + 3;
            var colonies = SpeciesColonies.Instance;
            var sb = new StringBuilder();
            sb.AppendLine($"time {Time.time:0}  layer {UnderView.Layer}  safari {SpeciesColonies.SafariMode}  fog {FogOfWar.Active}");
            if (colonies == null) { sb.AppendLine("no SpeciesColonies"); }
            else
            {
                var groups = colonies.Groups.Where(g => g != null).ToList();
                sb.AppendLine($"{groups.Count} groups, {groups.Count(g => g.Owner != null)} owned");
                foreach (var g in groups.OrderBy(g => g.Owner == null).Take(40))
                {
                    var r = g.GetComponentsInChildren<Renderer>(true);
                    sb.AppendLine($"{(g.Owner != null ? g.Owner.Name : "wild"),-10} {g.Definition?.id,-28} cell {(g.Cell != null ? g.Cell.Coordinates.ToString() : "-"),-10} niche {g.Niche,-12} inLayer {UnderView.InLayer(g, UnderView.Layer),-5} shows {UnderView.Shows(g),-5} active {g.gameObject.activeInHierarchy,-5} renderers {r.Length} on {r.Count(x => x.enabled)} members {g.Members.Count} pos {g.transform.position}");
                }
            }
            var pm = NaturalHistory.Players.PlayerManager.Instance;
            var ev = NaturalHistory.Evolution.EvolutionManager.Instance;
            var tm = NaturalHistory.Territory.TerritoryManager.Instance;
            sb.AppendLine($"turn {(NaturalHistory.Core.TurnManager.Instance != null ? NaturalHistory.Core.TurnManager.Instance.CurrentTurn : -1)}  state {NaturalHistory.Core.GameManager.Instance?.State}");
            if (pm != null)
                foreach (var p in pm.Players)
                {
                    var copies = ev != null ? ev.CopiesOf(p).ToList() : new System.Collections.Generic.List<NaturalHistory.Evolution.OwnedCopy>();
                    sb.AppendLine($"player {p.Index} {p.Name} human {p.IsHuman} start {(p.StartCell != null ? p.StartCell.Coordinates.ToString() : "null")} copies {copies.Count}: " +
                        string.Join(", ", copies.Select(c => $"{c.species}@{(c.cell != null ? c.cell.Coordinates.ToString() : "-")} group {(c.group != null ? "ok" : "none")}")));
                }
            if (tm != null)
            {
                var f = typeof(NaturalHistory.Territory.TerritoryManager).GetField("playerColonies", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
                if (f?.GetValue(tm) is System.Collections.IDictionary d)
                    foreach (System.Collections.DictionaryEntry e in d)
                        sb.AppendLine($"territory colony of {e.Key}: {((e.Value as Object) != null ? ((ColonyGroup)e.Value).Definition?.id : "destroyed/null")}");
            }
            System.IO.File.WriteAllText("Temp/nh_groups.txt", sb.ToString());
        }
    }
}
