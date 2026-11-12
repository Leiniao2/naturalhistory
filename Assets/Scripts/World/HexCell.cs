using System.Collections.Generic;
using NaturalHistory.Biology;
using UnityEngine;

namespace NaturalHistory.World
{
    public class HexCell : MonoBehaviour
    {
        public HexCoordinates Coordinates { get; private set; }
        public TerrainType Terrain { get; private set; }

        // Terrace level: 0 = water surface, 1..WorldGenerator.MaxElevation = land
        public int Elevation { get; private set; }

        // Biorealm that currently controls this cell (null = unclaimed)
        public BioRealm ControllingRealm { get; private set; }

        // Species populations present on this cell
        private readonly List<Species> inhabitants = new();
        public IReadOnlyList<Species> Inhabitants => inhabitants;

        [SerializeField] private MeshRenderer meshRenderer;
        private MaterialPropertyBlock propBlock;
        private Color baseColor = Color.white;
        private bool highlighted;

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

        public void SetElevation(int elevation)
        {
            Elevation = elevation;
        }

        public void SetHighlight(bool on)
        {
            if (highlighted == on) return;
            highlighted = on;
            ApplyColor();
        }

        private void ApplyColor()
        {
            if (meshRenderer == null) return;
            meshRenderer.GetPropertyBlock(propBlock);
            propBlock.SetColor("_Color", highlighted ? Color.Lerp(baseColor, Color.white, 0.4f) : baseColor);
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

        public override string ToString() => $"HexCell{Coordinates}[{Terrain?.kind}, elev {Elevation}]";
    }
}
