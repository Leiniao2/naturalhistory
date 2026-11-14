using System.Collections.Generic;
using NaturalHistory.Biology;
using UnityEngine;

namespace NaturalHistory.World
{
    public class HexCell : MonoBehaviour
    {
        public HexCoordinates Coordinates { get; private set; }
        public TerrainType Terrain { get; private set; }

        // Forest or other overlay on the terrain
        public TerrainFeature Feature { get; private set; }

        // What the climate makes this cell, as it would look today (set by WorldGenerator).
        // Terrain and Feature are the same place in the period currently shown (EraFlora).
        public TerrainKind Biome { get; private set; }
        public TerrainFeature BiomeFeature { get; private set; }
        public float Moisture { get; private set; } // 0..1, share of the map that is drier
        public bool IsForest => Feature is TerrainFeature.BroadleafForest or TerrainFeature.ConiferForest;

        // High enough to be drawn as mountain peaks; units can't enter these cells
        public bool IsMountain => Terrain != null &&
            (Terrain.kind == TerrainKind.Mountain ||
             Terrain.kind == TerrainKind.IceSheet && Elevation >= WorldGenerator.MountainElevation);

        // Terrace level: 0 = water surface, 1..WorldGenerator.MaxElevation = land
        public int Elevation { get; private set; }

        // Local Y of the tile's top face; units stand on this
        public float SurfaceHeight { get; private set; }

        // Biorealm that currently controls this cell (null = unclaimed)
        public BioRealm ControllingRealm { get; private set; }

        // Species populations present on this cell
        private readonly List<Species> inhabitants = new();
        public IReadOnlyList<Species> Inhabitants => inhabitants;

        [SerializeField] private MeshRenderer meshRenderer;
        private MaterialPropertyBlock propBlock;
        private Color baseColor = Color.white;
        private Color tintVariation = Color.white; // per-cell jitter so identical terrain doesn't look stamped
        private bool highlighted;
        private bool moveTarget;
        private GroupTarget groupTarget;

        public enum GroupTarget { None, Move, Attack }

        private void Awake() => EnsureRenderer();

        // Awake does not run for cells created by the Edit-mode map preview, so this
        // is also called from Initialize.
        private void EnsureRenderer()
        {
            if (meshRenderer == null)
                meshRenderer = GetComponent<MeshRenderer>();
            propBlock ??= new MaterialPropertyBlock();
            if (meshRenderer == null)
                Debug.LogError("[HexCell] MeshRenderer is NULL");
        }

        public void Initialize(HexCoordinates coords, TerrainType terrain)
        {
            EnsureRenderer();
            Coordinates = coords;
            SetTerrain(terrain);
        }

        public void SetTerrain(TerrainType terrain)
        {
            Terrain = terrain;
            if (meshRenderer == null) return;
            if (terrain.material != null)
            {
                meshRenderer.sharedMaterial = terrain.material;
                baseColor = Color.white;
            }
            else
            {
                baseColor = terrain.color;
            }
            ApplyColor();
        }

        public void SetFeature(TerrainFeature feature)
        {
            Feature = feature;
        }

        public void SetClimate(TerrainKind biome, TerrainFeature feature, float moisture)
        {
            Biome        = biome;
            BiomeFeature = feature;
            Moisture     = moisture;
        }

        public void SetElevation(int elevation)
        {
            Elevation = elevation;
        }

        public void SetSurfaceHeight(float height)
        {
            SurfaceHeight = height;
        }

        // Height of the sloped rim above the base, set by HexGrid: corner i at [2i], the midpoint
        // of edge e at [2e + 1]. Null for flat tiles (water).
        public float[] RimHeights { get; private set; }

        public void SetRimHeights(float[] rim) => RimHeights = rim;

        public Vector3 SurfacePosition => transform.position + Vector3.up * SurfaceHeight;

        // How far this cell has been moved from its base position by map wrapping. The terrain
        // shader subtracts it so world-projected textures stay continuous across the seam.
        public void SetWrapShift(float shift)
        {
            if (meshRenderer == null) return;
            meshRenderer.GetPropertyBlock(propBlock);
            propBlock.SetFloat("_WrapShift", shift);
            meshRenderer.SetPropertyBlock(propBlock);
        }

        public bool IsWater => Terrain != null && Terrain.kind is TerrainKind.SaltWater or TerrainKind.FreshWater;

        // Colour and texture this cell shows; neighbours blend toward them across the shared edge.
        public Color BlendTint => baseColor * tintVariation;
        public Texture BlendTexture =>
            Terrain != null && Terrain.material != null && Terrain.material.HasProperty(BaseMapId) ? Terrain.material.GetTexture(BaseMapId) : null;

        static readonly int BaseMapId = Shader.PropertyToID("_BaseMap");
        static readonly int EdgeTintsId = Shader.PropertyToID("_EdgeTint");
        static readonly int[] EdgeTexIds =
        {
            Shader.PropertyToID("_EdgeTex0"), Shader.PropertyToID("_EdgeTex1"), Shader.PropertyToID("_EdgeTex2"),
            Shader.PropertyToID("_EdgeTex3"), Shader.PropertyToID("_EdgeTex4"), Shader.PropertyToID("_EdgeTex5"),
        };

        // Neighbour terrain for each of the 6 edges, read by the terrain shader to blend across borders.
        // Edge e faces the direction 60e + 30 degrees clockwise from +Z. tint.a = 0 disables blending on that edge.
        public void SetEdgeBlends(Texture[] textures, Vector4[] tints)
        {
            if (meshRenderer == null) return;
            meshRenderer.GetPropertyBlock(propBlock);
            for (int e = 0; e < 6; e++)
                propBlock.SetTexture(EdgeTexIds[e], textures[e] != null ? textures[e] : Texture2D.whiteTexture);
            propBlock.SetVectorArray(EdgeTintsId, tints);
            meshRenderer.SetPropertyBlock(propBlock);
        }

        public void SetTintVariation(Color tint)
        {
            tintVariation = tint;
            ApplyColor();
        }

        public void SetHighlight(bool on)
        {
            if (highlighted == on) return;
            highlighted = on;
            ApplyColor();
        }

        // Marks a hex the player's unit can move to this turn (lighter yellow tint)
        public void SetMoveTarget(bool on)
        {
            if (moveTarget == on) return;
            moveTarget = on;
            ApplyColor();
        }

        // Marks a hex the selected animal group can move to (green) or attack (red)
        public void SetGroupTarget(GroupTarget target)
        {
            if (groupTarget == target) return;
            groupTarget = target;
            ApplyColor();
        }

        private void ApplyColor()
        {
            if (meshRenderer == null) return;
            var color = baseColor * tintVariation;
            if (moveTarget)  color = Color.Lerp(color, new Color(1f, 0.92f, 0.4f), 0.35f);
            if (groupTarget == GroupTarget.Move)   color = Color.Lerp(color, new Color(0.45f, 1f, 0.5f), 0.4f);
            if (groupTarget == GroupTarget.Attack) color = Color.Lerp(color, new Color(1f, 0.25f, 0.2f), 0.5f);
            if (highlighted) color = Color.Lerp(color, Color.white, 0.4f);
            meshRenderer.GetPropertyBlock(propBlock);
            propBlock.SetColor("_Color", color);
            meshRenderer.SetPropertyBlock(propBlock);
        }

        public void SetControllingRealm(BioRealm realm)
        {
            ControllingRealm = realm;
        }

        public void AddInhabitant(Species species)
        {
            if (!inhabitants.Contains(species))
                inhabitants.Add(species);
        }

        public void RemoveInhabitant(Species species)
        {
            inhabitants.Remove(species);
        }

        public override string ToString() =>
            $"HexCell{Coordinates}[{Terrain?.kind}{(Feature != TerrainFeature.None ? $" + {Feature}" : "")}, elev {Elevation}]";
    }
}
