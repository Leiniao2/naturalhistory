// Terrain skin for hex tiles (URP).
// The texture is projected in world space (top: XZ, sides: XY/ZY), so it tiles
// seamlessly across neighbouring hexes instead of repeating per tile.
// _Color is a tint driven per-cell by HexCell's MaterialPropertyBlock (highlight, move targets).
Shader "NaturalHistory/HexTerrain"
{
    Properties
    {
        _BaseMap      ("Texture", 2D) = "white" {}
        _Color        ("Tint", Color) = (1, 1, 1, 1)
        _Tiling       ("World Tiling (texture repeats per unit)", Float) = 0.35
        _SideDarken   ("Side Darken", Range(0, 1)) = 0.35
        _EdgeDarken   ("Hex Edge Darken", Range(0, 1)) = 0.25
        [HideInInspector] _WrapShift ("Map wrap shift (set per cell)", Float) = 0
        // Neighbour terrain textures, one per edge (set per cell by HexGrid for border blending)
        [HideInInspector] _EdgeTex0 ("Edge 0", 2D) = "white" {}
        [HideInInspector] _EdgeTex1 ("Edge 1", 2D) = "white" {}
        [HideInInspector] _EdgeTex2 ("Edge 2", 2D) = "white" {}
        [HideInInspector] _EdgeTex3 ("Edge 3", 2D) = "white" {}
        [HideInInspector] _EdgeTex4 ("Edge 4", 2D) = "white" {}
        [HideInInspector] _EdgeTex5 ("Edge 5", 2D) = "white" {}
    }

    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" "Queue" = "Geometry" }

        HLSLINCLUDE
        #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

        TEXTURE2D(_BaseMap); SAMPLER(sampler_BaseMap);
        TEXTURE2D(_EdgeTex0); TEXTURE2D(_EdgeTex1); TEXTURE2D(_EdgeTex2);
        TEXTURE2D(_EdgeTex3); TEXTURE2D(_EdgeTex4); TEXTURE2D(_EdgeTex5);

        // Per cell: neighbour tint for each edge (a = 1 → blend across that edge). Globals: tile geometry.
        float4 _EdgeTint[6];
        float  _HexApothem;
        float  _HexBlendWidth;

        CBUFFER_START(UnityPerMaterial)
            float4 _BaseMap_ST;
            half4  _Color;
            float  _Tiling;
            half   _SideDarken;
            half   _EdgeDarken;
            float  _WrapShift;
        CBUFFER_END
        ENDHLSL

        Pass
        {
            Name "ForwardLit"
            Tags { "LightMode" = "UniversalForward" }

            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE _MAIN_LIGHT_SHADOWS_SCREEN
            #pragma multi_compile_fragment _ _SHADOWS_SOFT
            #pragma multi_compile_fog

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS   : NORMAL;
                float2 uv         : TEXCOORD0;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
                float3 normalWS   : TEXCOORD1;
                float2 uv         : TEXCOORD2;
                float  fogFactor  : TEXCOORD3;
            };

            Varyings vert(Attributes v)
            {
                Varyings o;
                VertexPositionInputs pos = GetVertexPositionInputs(v.positionOS.xyz);
                o.positionCS = pos.positionCS;
                o.positionWS = pos.positionWS;
                o.normalWS   = TransformObjectToWorldNormal(v.normalOS);
                o.uv         = v.uv;
                o.fogFactor  = ComputeFogFactor(pos.positionCS.z);
                return o;
            }

            // Explicit gradients: the sample sits inside a branch that varies across the tile.
            half3 SampleEdgeTex(int e, float2 uv, float2 dx, float2 dy)
            {
                switch (e)
                {
                    case 0:  return SAMPLE_TEXTURE2D_GRAD(_EdgeTex0, sampler_BaseMap, uv, dx, dy).rgb;
                    case 1:  return SAMPLE_TEXTURE2D_GRAD(_EdgeTex1, sampler_BaseMap, uv, dx, dy).rgb;
                    case 2:  return SAMPLE_TEXTURE2D_GRAD(_EdgeTex2, sampler_BaseMap, uv, dx, dy).rgb;
                    case 3:  return SAMPLE_TEXTURE2D_GRAD(_EdgeTex3, sampler_BaseMap, uv, dx, dy).rgb;
                    case 4:  return SAMPLE_TEXTURE2D_GRAD(_EdgeTex4, sampler_BaseMap, uv, dx, dy).rgb;
                    default: return SAMPLE_TEXTURE2D_GRAD(_EdgeTex5, sampler_BaseMap, uv, dx, dy).rgb;
                }
            }

            // Distance from the tile's edge e (facing 60e + 30 degrees clockwise from +Z) toward the centre.
            float EdgeDistance(int e, float2 local)
            {
                float a = radians(60.0 * e + 30.0);
                return _HexApothem - dot(local, float2(sin(a), cos(a)));
            }

            half4 frag(Varyings i) : SV_Target
            {
                float3 n  = normalize(i.normalWS);
                float3 p  = (i.positionWS - float3(_WrapShift, 0, 0)) * _Tiling;

                // Top and side projections are blended by surface angle, so the rounded tile edge
                // fades from the top texture into the darker wall instead of switching at a hard line.
                float2 topUV   = p.xz * _BaseMap_ST.xy + _BaseMap_ST.zw;
                float2 sideUV  = abs(n.x) > abs(n.z) ? p.zy : p.xy;
                half3  topTex  = SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, topUV).rgb;
                half3  sideTex = SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, sideUV * _BaseMap_ST.xy + _BaseMap_ST.zw).rgb;
                half   topW    = smoothstep(0.3, 0.9, n.y);

                // Border blending: fade toward the terrain across the nearest edge and, near a corner,
                // the next edge too. Each neighbour weighs 1 at the border and 0 at _HexBlendWidth in,
                // against 1 for this tile, so both sides of an edge meet at 50/50 and corners at a
                // three-way mix. Textures are world-projected, so the two sides line up exactly.
                float2 local  = i.positionWS.xz - UNITY_MATRIX_M._m03_m23;
                float  angle  = atan2(local.x, local.y);
                float  sector = (angle < 0 ? angle + TWO_PI : angle) / (PI / 3.0);
                int    e1     = (int)floor(sector) % 6;
                int    e2     = frac(sector) < 0.5 ? (e1 + 5) % 6 : (e1 + 1) % 6;
                half   w1     = _EdgeTint[e1].a * (1.0 - smoothstep(0.0, _HexBlendWidth, EdgeDistance(e1, local)));
                half   w2     = _EdgeTint[e2].a * (1.0 - smoothstep(0.0, _HexBlendWidth, EdgeDistance(e2, local)));
                half3  top    = topTex * _Color.rgb;
                float2 dx     = ddx(topUV), dy = ddy(topUV); // outside the branch: derivatives need uniform flow
                [branch] if (w1 + w2 > 0.001)
                {
                    half3 n1 = SampleEdgeTex(e1, topUV, dx, dy) * _EdgeTint[e1].rgb;
                    half3 n2 = SampleEdgeTex(e2, topUV, dx, dy) * _EdgeTint[e2].rgb;
                    top = (top + n1 * w1 + n2 * w2) / (1.0 + w1 + w2);
                }
                half3 albedo = lerp(sideTex * (1.0 - _SideDarken) * _Color.rgb, top, topW);

                // Mesh UVs are radial: 0.5 at the centre, corners at distance 0.5. A wide, gentle
                // darkening toward the rim keeps hexes readable; it eases off where terrain blends
                // into a neighbour so blended borders don't get an outline.
                float r = length(i.uv - 0.5) * 2.0;
                albedo *= 1.0 - _EdgeDarken * topW * smoothstep(0.55, 1.05, r) * (1.0 - 0.7 * saturate(max(w1, w2)));

                Light mainLight = GetMainLight(TransformWorldToShadowCoord(i.positionWS));
                half  ndotl     = saturate(dot(n, mainLight.direction));
                half3 lighting  = mainLight.color * ndotl * mainLight.shadowAttenuation + SampleSH(n);

                half3 color = MixFog(albedo * lighting, i.fogFactor);
                return half4(color, 1);
            }
            ENDHLSL
        }

        Pass
        {
            Name "ShadowCaster"
            Tags { "LightMode" = "ShadowCaster" }
            ZWrite On
            ColorMask 0

            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma multi_compile_vertex _ _CASTING_PUNCTUAL_LIGHT_SHADOW

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Shadows.hlsl"

            float3 _LightDirection;
            float3 _LightPosition;

            struct Attributes { float4 positionOS : POSITION; float3 normalOS : NORMAL; };

            float4 vert(Attributes v) : SV_POSITION
            {
                float3 posWS    = TransformObjectToWorld(v.positionOS.xyz);
                float3 normalWS = TransformObjectToWorldNormal(v.normalOS);
            #if _CASTING_PUNCTUAL_LIGHT_SHADOW
                float3 lightDir = normalize(_LightPosition - posWS);
            #else
                float3 lightDir = _LightDirection;
            #endif
                float4 posCS = TransformWorldToHClip(ApplyShadowBias(posWS, normalWS, lightDir));
                return ApplyShadowClamping(posCS);
            }

            half4 frag() : SV_Target { return 0; }
            ENDHLSL
        }

        Pass
        {
            Name "DepthOnly"
            Tags { "LightMode" = "DepthOnly" }
            ZWrite On
            ColorMask R

            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag

            struct Attributes { float4 positionOS : POSITION; };

            float4 vert(Attributes v) : SV_POSITION { return TransformObjectToHClip(v.positionOS.xyz); }
            half4 frag() : SV_Target { return 0; }
            ENDHLSL
        }
    }

    // Built-in render pipeline (what the project currently uses: no URP asset is assigned
    // in Graphics/Quality settings). Unity skips the URP SubShader above and uses this one.
    SubShader
    {
        Tags { "RenderType" = "Opaque" "Queue" = "Geometry" }

        CGPROGRAM
        #pragma surface surf Lambert vertex:vert fullforwardshadows addshadow
        #pragma target 3.0

        sampler2D _BaseMap;
        float4    _BaseMap_ST;
        fixed4    _Color;
        float     _Tiling;
        half      _SideDarken;
        half      _EdgeDarken;
        float     _WrapShift;

        struct Input
        {
            float3 worldPos;
            float3 worldNormal;
            float2 hexUV;
        };

        void vert(inout appdata_full v, out Input o)
        {
            UNITY_INITIALIZE_OUTPUT(Input, o);
            o.hexUV = v.texcoord.xy;
        }

        void surf(Input IN, inout SurfaceOutput o)
        {
            float3 n   = normalize(IN.worldNormal);
            float3 p   = (IN.worldPos - float3(_WrapShift, 0, 0)) * _Tiling;
            bool   top = n.y > 0.5;

            float2 uv = top ? p.xz : (abs(n.x) > abs(n.z) ? p.zy : p.xy);
            half3 albedo = tex2D(_BaseMap, uv * _BaseMap_ST.xy + _BaseMap_ST.zw).rgb;

            if (top)
            {
                float r = length(IN.hexUV - 0.5) * 2.0;
                albedo *= 1.0 - _EdgeDarken * smoothstep(0.72, 1.0, r);
            }
            else
            {
                albedo *= 1.0 - _SideDarken;
            }

            o.Albedo = albedo * _Color.rgb;
            o.Alpha  = 1;
        }
        ENDCG
    }

    FallBack "Diffuse"
}
