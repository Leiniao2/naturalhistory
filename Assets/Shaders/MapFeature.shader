// Flat-shaded props on top of hex tiles (mountain peaks, trees).
// Albedo comes from mesh vertex colors, so every prop shares this one material.
// _Flap bends everything beyond |x| > _FlapRoot (object space) up or down about the body's long
// axis, so a single static mesh can beat its wings or fins; SpeciesColonies drives it per renderer.
Shader "NaturalHistory/MapFeature"
{
    Properties
    {
        _Color ("Tint", Color) = (1, 1, 1, 1)
        _Flap ("Wing angle (radians)", Float) = 0
        _FlapRoot ("Wing root (half body width)", Float) = 0
        _FlapSpan ("Wing tip (half span)", Float) = 1
    }

    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" "Queue" = "Geometry" }

        HLSLINCLUDE
        #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

        CBUFFER_START(UnityPerMaterial)
            half4 _Color;
            float _Flap;
            float _FlapRoot;
            float _FlapSpan;
        CBUFFER_END

        #include "MapFeatureFlap.cginc"
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
                half4  color      : COLOR;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
                float3 normalWS   : TEXCOORD1;
                half4  color      : COLOR;
                float  fogFactor  : TEXCOORD2;
            };

            Varyings vert(Attributes v)
            {
                Varyings o;
                ApplyFlap(v.positionOS.xyz, v.normalOS);
                VertexPositionInputs pos = GetVertexPositionInputs(v.positionOS.xyz);
                o.positionCS = pos.positionCS;
                o.positionWS = pos.positionWS;
                o.normalWS   = TransformObjectToWorldNormal(v.normalOS);
                o.color      = v.color;
                o.fogFactor  = ComputeFogFactor(pos.positionCS.z);
                return o;
            }

            half4 frag(Varyings i) : SV_Target
            {
                float3 n      = normalize(i.normalWS);
                half3  albedo = i.color.rgb * _Color.rgb;

                Light mainLight = GetMainLight(TransformWorldToShadowCoord(i.positionWS));
                half  ndotl     = saturate(dot(n, mainLight.direction));
                half3 lighting  = mainLight.color * ndotl * mainLight.shadowAttenuation + SampleSH(n);

                return half4(MixFog(albedo * lighting, i.fogFactor), 1);
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
                ApplyFlap(v.positionOS.xyz, v.normalOS);
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

            float4 vert(Attributes v) : SV_POSITION
            {
                float3 normalOS = float3(0, 1, 0);
                ApplyFlap(v.positionOS.xyz, normalOS);
                return TransformObjectToHClip(v.positionOS.xyz);
            }
            half4 frag() : SV_Target { return 0; }
            ENDHLSL
        }
    }

    // Built-in render pipeline (what the project currently uses), same as HexTerrain.
    SubShader
    {
        Tags { "RenderType" = "Opaque" "Queue" = "Geometry" }

        CGPROGRAM
        #pragma surface surf Lambert fullforwardshadows addshadow vertex:vert
        #pragma target 3.0

        fixed4 _Color;
        float _Flap;
        float _FlapRoot;
        float _FlapSpan;
        #include "MapFeatureFlap.cginc"

        struct Input
        {
            float4 color : COLOR;
        };

        void vert(inout appdata_full v)
        {
            ApplyFlap(v.vertex.xyz, v.normal);
        }

        void surf(Input IN, inout SurfaceOutput o)
        {
            o.Albedo = IN.color.rgb * _Color.rgb;
            o.Alpha  = 1;
        }
        ENDCG
    }

    FallBack "Diffuse"
}
