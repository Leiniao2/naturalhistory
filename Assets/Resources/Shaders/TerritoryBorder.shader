// Territory border bands (see TerritoryBorders.cs): unlit vertex colour with alpha, drawn over the
// tiles. No LightMode tag and plain UnityCG, so it renders in both the built-in pipeline and URP.
// Lives in Resources so it is included in builds and found by Resources.Load.
Shader "NaturalHistory/TerritoryBorder"
{
    SubShader
    {
        Tags { "Queue" = "Transparent" "RenderType" = "Transparent" "IgnoreProjector" = "True" }

        Pass
        {
            Blend SrcAlpha OneMinusSrcAlpha
            ZWrite Off
            Cull Off
            Offset -1, -1
            // not over the animals (they mark themselves 1, see MapFeature), so they stand on top of
            // the border even where it lies above them, as over the sea
            Stencil { Ref 1 Comp NotEqual }

            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"

            struct appdata
            {
                float4 vertex : POSITION;
                fixed4 color  : COLOR;
            };

            struct v2f
            {
                float4 pos   : SV_POSITION;
                fixed4 color : COLOR;
            };

            v2f vert(appdata v)
            {
                v2f o;
                o.pos   = UnityObjectToClipPos(v.vertex);
                o.color = v.color;
                return o;
            }

            fixed4 frag(v2f i) : SV_Target
            {
                return i.color;
            }
            ENDCG
        }
    }
}
