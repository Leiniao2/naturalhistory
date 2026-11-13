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

        public void SetElevation(int elevation)
        {
            Elevation = elevation;
        }

        public void SetSurfaceHeight(float height)
        {
            SurfaceHeight = height;
        }

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

        private void ApplyColor()
        {
            if (meshRenderer == null) return;
            var color = baseColor * tintVariation;
            if (moveTarget)  color = Color.Lerp(color, new Color(1f, 0.92f, 0.4f), 0.35f);
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
