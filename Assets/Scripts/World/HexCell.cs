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

        // The layer under sea level below this tile (HexGrid.Under) and the water plants growing there
        public UnderKind Under { get; private set; }
        public UnderFeature UnderFeature { get; private set; }
        public void SetUnder(UnderKind kind, UnderFeature feature) { Under = kind; UnderFeature = feature; }
        public IReadOnlyList<PlantDefinition> UnderPlants => underPlants;
        private readonly List<PlantDefinition> underPlants = new();
        public void SetUnderPlants(params PlantDefinition[] list)
        {
            underPlants.Clear();
            if (list == null) return;
            foreach (var p in list) if (p != null && !underPlants.Contains(p)) underPlants.Add(p);
        }

        // Plant species drawn on this tile (dominant first), for the tile panel. Visual only.
        public IReadOnlyList<PlantDefinition> Plants => plants;
        private readonly List<PlantDefinition> plants = new();
        public void SetPlants(params PlantDefinition[] list)
        {
            plants.Clear();
            if (list == null) return;
            foreach (var p in list) if (p != null && !plants.Contains(p)) plants.Add(p);
        }

        // High enough to be drawn as mountain peaks; units can't enter these cells
        public bool IsMountain => Terrain != null &&
            (Terrain.kind == TerrainKind.Mountain ||
             Terrain.kind == TerrainKind.IceSheet && Elevation >= WorldGenerator.MountainElevation);

        // One of the map's tallest mountains, peaking above the sky layer's clouds (HexGrid.HighMountains)
        public bool IsHighMountain { get; set; }
        // World height of the tile's highest point (its mountain's peak; else its top face)
        public float PeakY { get; set; }

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
            ShowingUnder = false; // back to the surface skin; HexGrid re-applies the under view if it is on
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

        // The generator's inputs for this tile, so it can be reclassified for another date's climate
        public WorldGenerator.CellInputs Inputs { get; private set; }
        public bool HasInputs { get; private set; }
        public void SetInputs(WorldGenerator.CellInputs inputs) { Inputs = inputs; HasInputs = true; }

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

        // Water only: 0 for the shallowest water, 1 for the deepest (set by WorldGenerator).
        public float Depth { get; private set; }
        public void SetDepth(float depth) => Depth = depth;

        // Rivers (set by HexGrid): the edge the river leaves by (-1 = none), a bit per edge it comes
        // in by, and how many river tiles drain through here (1 at a source), which sets its width.
        // Edge e faces 60e + 30 degrees clockwise from +Z.
        public int RiverOut { get; private set; } = -1;
        public int RiverIn { get; private set; }
        public int RiverFlow { get; private set; }
        public bool HasRiver => RiverOut >= 0 || RiverIn != 0;

        // Tiles left to the river's mouth (1 on the tile where it meets the water), the mouth tile's
        // index (which river system it belongs to), and whether it lies on the floodplain or delta
        // near the mouth of a big river.
        public int RiverToMouth { get; private set; }
        public int RiverSystem { get; private set; }
        public bool Floodplain { get; private set; }

        public void SetRiver(int outEdge, int inEdges, int flow, int toMouth = 0, int system = 0)
        {
            RiverOut     = outEdge;
            RiverIn      = inEdges;
            RiverFlow    = flow;
            RiverToMouth = toMouth;
            RiverSystem  = system;
        }

        public void SetFloodplain(bool on) => Floodplain = on;

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
            wrapShift = shift;
            meshRenderer.GetPropertyBlock(propBlock);
            propBlock.SetFloat("_WrapShift", shift);
            meshRenderer.SetPropertyBlock(propBlock);
        }

        public bool IsWater => Terrain != null && Terrain.kind is TerrainKind.SaltWater or TerrainKind.FreshWater;

        // Colour and texture this cell shows; neighbours blend toward them across the shared edge.
        public Color BlendTint => baseColor * tintVariation;
        public Texture BlendTexture
        {
            get
            {
                if (surfaceTexture != null) return surfaceTexture; // the ground material of this region (SetSurface)
                var mat = meshRenderer != null && meshRenderer.sharedMaterial != null ? meshRenderer.sharedMaterial : Terrain?.material;
                return mat != null && mat.HasProperty(BaseMapId) ? mat.GetTexture(BaseMapId) : null;
            }
        }

        // Draw the tile with another terrain's skin without changing what the cell is (Terrain).
        // Mountain tiles use the land around them, so a massif rises straight out of that ground.
        // Reset by the next SetTerrain.
        public void SetGroundMaterial(Material material)
        {
            if (meshRenderer != null && material != null) meshRenderer.sharedMaterial = material;
        }

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

        static readonly int CliffTexId  = Shader.PropertyToID("_CliffTex");
        private Texture surfaceTexture;

        // What the ground of this tile is made of when it differs from its terrain's own texture
        // (dune sand, desert pavement, salt flat, lava field...; null = the terrain texture), and the
        // rock of its cliff faces (null = the shared mountain rock). Set by HexGrid.SetGroundLook.
        public void SetSurface(Texture ground, Texture cliff)
        {
            surfaceTexture = ground;
            if (meshRenderer == null) return;
            meshRenderer.GetPropertyBlock(propBlock);
            var own = meshRenderer.sharedMaterial != null && meshRenderer.sharedMaterial.HasProperty(BaseMapId) ? meshRenderer.sharedMaterial.GetTexture(BaseMapId) : null;
            var tex = ground != null ? ground : own;
            if (tex != null) propBlock.SetTexture(BaseMapId, tex);
            var rock = cliff != null ? cliff : Shader.GetGlobalTexture(CliffTexId);
            if (rock != null) propBlock.SetTexture(CliffTexId, rock);
            meshRenderer.SetPropertyBlock(propBlock);
        }

        // The sand/soil recolour last set by SetGroundLook (kept while the under view hides it), so
        // props can match the ground's colour (WaterfallFx)
        public Vector4 GroundRecolor { get; private set; }

        static readonly int RecolorId   = Shader.PropertyToID("_Recolor");
        static readonly int CliffTintId = Shader.PropertyToID("_CliffTint");
        static readonly int ShoreId     = Shader.PropertyToID("_Shore");
        static readonly int FloodId     = Shader.PropertyToID("_Flood");

        // What kind of sand, soil or rock this tile shows (set by HexGrid, see the terrain shader):
        // recolor.rgb repaints the ground texture's shading in that colour by recolor.a (white or red
        // sand, black gravel…), cliff tints its rock faces (granite, sandstone, basalt, chalk) and
        // shore.rgb is the colour of the beach where it meets the sea, shore.a 1 for sand, 0 for rock.
        // flood: how much of the ground shows wet hollows and pools (floodplains, deltas).
        public void SetGroundLook(Vector4 recolor, Color cliff, Vector4 shore, float flood = 0f)
        {
            GroundRecolor = recolor;
            if (meshRenderer == null) return;
            meshRenderer.GetPropertyBlock(propBlock);
            propBlock.SetFloat(FloodId, flood);
            propBlock.SetVector(RecolorId, recolor);
            propBlock.SetColor(CliffTintId, cliff);
            propBlock.SetVector(ShoreId, shore);
            meshRenderer.SetPropertyBlock(propBlock);
        }

        // ---------- Under view ----------

        // Showing the layer under sea level instead of the surface (see HexGrid.Under)
        public bool ShowingUnder { get; private set; }
        private Material surfaceMaterial;
        private MaterialPropertyBlock surfaceBlock;
        private Color underTint = Color.white;
        private float wrapShift;

        // Swaps the tile's skin to the under layer's: its own material and tint, without the surface's
        // edge blending, sand/rock recolouring or shore. ShowSurface puts everything back.
        // edgeTextures / edgeTints / edgeScales (6 each, may be null): the neighbouring under tiles to
        // blend into across each edge (tint.a = 0: none), and their textures' world tiling.
        public void ShowUnder(Material material, Color tint, Texture[] edgeTextures = null, Vector4[] edgeTints = null, float[] edgeScales = null,
                              bool waterBed = false)
        {
            if (meshRenderer == null || material == null) return;
            if (!ShowingUnder)
            {
                surfaceMaterial = meshRenderer.sharedMaterial;
                surfaceBlock ??= new MaterialPropertyBlock();
                meshRenderer.GetPropertyBlock(surfaceBlock);
            }
            ShowingUnder = true;
            underTint = tint;
            meshRenderer.sharedMaterial = material;
            propBlock.Clear();
            propBlock.SetFloat("_WrapShift", wrapShift);
            propBlock.SetVectorArray(EdgeTintsId, edgeTints ?? new Vector4[6]); // never into the surface neighbours
            if (edgeTextures != null)
                for (int e = 0; e < 6; e++) propBlock.SetTexture(EdgeTexIds[e], edgeTextures[e] != null ? edgeTextures[e] : Texture2D.whiteTexture);
            propBlock.SetFloatArray(EdgeScaleId, edgeScales ?? new float[6]);
            propBlock.SetFloat(EdgeDarkenId, 0.06f); // only a hint of the tile rim, so beds run on into each other
            if (waterBed) propBlock.SetFloat(LandId, 0f); // below sea level: no beach, surf or cliff rock colouring
            propBlock.SetFloat(AntiTileId, waterBed ? 1f : 0f); // no rows or stripes in the mats and beds
            meshRenderer.SetPropertyBlock(propBlock);
            ApplyColor();
        }

        static readonly int EdgeScaleId  = Shader.PropertyToID("_EdgeScale");
        static readonly int CellBlendId  = Shader.PropertyToID("_CellBlend");

        // Blend this surface tile into its neighbours across its edges (the built-in terrain shader
        // only does it where asked: deserts and the land round them, see HexGrid.Desert)
        public void SetCellBlend(bool on)
        {
            if (meshRenderer == null) return;
            meshRenderer.GetPropertyBlock(propBlock);
            propBlock.SetFloat(CellBlendId, on ? 1f : 0f);
            meshRenderer.SetPropertyBlock(propBlock);
        }
        static readonly int LandId       = Shader.PropertyToID("_Land");
        static readonly int AntiTileId   = Shader.PropertyToID("_AntiTile");
        static readonly int EdgeDarkenId = Shader.PropertyToID("_EdgeDarken");

        public void ShowSurface()
        {
            if (!ShowingUnder || meshRenderer == null) return;
            ShowingUnder = false;
            meshRenderer.sharedMaterial = surfaceMaterial;
            meshRenderer.SetPropertyBlock(surfaceBlock);
            meshRenderer.GetPropertyBlock(propBlock);
            propBlock.SetFloat("_WrapShift", wrapShift); // it may have moved round the map meanwhile
            meshRenderer.SetPropertyBlock(propBlock);
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
            var color = ShowingUnder ? underTint : baseColor * tintVariation;
            if (moveTarget)  color = Color.Lerp(color, new Color(1f, 0.92f, 0.4f), 0.35f);
            // where a selected group can go (MoveRange) or strike: a strong wash, so the range reads at a glance
            if (groupTarget == GroupTarget.Move)   color = Color.Lerp(color, new Color(0.40f, 1f, 0.45f), 0.65f);
            if (groupTarget == GroupTarget.Attack) color = Color.Lerp(color, new Color(1f, 0.22f, 0.18f), 0.7f);
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
