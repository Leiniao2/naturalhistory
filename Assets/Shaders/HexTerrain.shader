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
    }

    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" "Queue" = "Geometry" }

        HLSLINCLUDE
        #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

        TEXTURE2D(_BaseMap); SAMPLER(sampler_BaseMap);

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

            half4 frag(Varyings i) : SV_Target
            {
                float3 n  = normalize(i.normalWS);
                float3 p  = (i.positionWS - float3(_WrapShift, 0, 0)) * _Tiling;
                bool   top = n.y > 0.5;

                float2 uv = top ? p.xz : (abs(n.x) > abs(n.z) ? p.zy : p.xy);
                half3 albedo = SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, uv * _BaseMap_ST.xy + _BaseMap_ST.zw).rgb;

                if (top)
                {
                    // Mesh UVs are radial on the top face: 0.5 at the centre, corners at distance 0.5.
                    // Darken towards the rim so individual hexes stay readable.
                    float r = length(i.uv - 0.5) * 2.0;
                    albedo *= 1.0 - _EdgeDarken * smoothstep(0.72, 1.0, r);
                }
                else
                {
                    albedo *= 1.0 - _SideDarken;
                }
                albedo *= _Color.rgb;

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
