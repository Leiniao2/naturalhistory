// Soft, see-through parts for the natural-phenomenon effects (smoke, dust, spray, fire, glow).
// Every part is a smooth ball or disc; its edge fades out by how much the surface faces the camera,
// so a ball reads as a soft puff instead of a hard sphere. Two materials use it:
//   FxSmoke: alpha blended and lit (half-Lambert from the main light), fades by _Color.a;
//   FxGlow:  additive and unlit, for fire, lava, flashes and embers.
// Effects set _Color (HDR, alpha = opacity) per part with a MaterialPropertyBlock.
Shader "NaturalHistory/FxParticle"
{
    Properties
    {
        [HDR] _Color ("Color", Color) = (1, 1, 1, 1)
        _Soft ("Edge softness", Range(0, 4)) = 1.5
        _Lit ("Lighting", Range(0, 1)) = 0.7
        [Enum(UnityEngine.Rendering.BlendMode)] _SrcBlend ("Source blend", Float) = 5      // SrcAlpha
        [Enum(UnityEngine.Rendering.BlendMode)] _DstBlend ("Destination blend", Float) = 10 // OneMinusSrcAlpha
    }

    SubShader
    {
        Tags { "RenderType" = "Transparent" "Queue" = "Transparent" "RenderPipeline" = "UniversalPipeline" "IgnoreProjector" = "True" }

        Pass
        {
            Name "Fx"
            Tags { "LightMode" = "UniversalForward" }
            Blend [_SrcBlend] [_DstBlend]
            ZWrite Off
            Cull Back

            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma multi_compile_fog
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            CBUFFER_START(UnityPerMaterial)
                half4 _Color;
                half  _Soft;
                half  _Lit;
            CBUFFER_END

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS   : NORMAL;
                half4  color      : COLOR;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 normalWS   : TEXCOORD0;
                float3 viewWS     : TEXCOORD1;
                half4  color      : COLOR;
                float  fogFactor  : TEXCOORD2;
            };

            Varyings vert(Attributes v)
            {
                Varyings o;
                VertexPositionInputs p = GetVertexPositionInputs(v.positionOS.xyz);
                o.positionCS = p.positionCS;
                o.normalWS   = TransformObjectToWorldNormal(v.normalOS);
                o.viewWS     = GetWorldSpaceViewDir(p.positionWS);
                o.color      = v.color;
                o.fogFactor  = ComputeFogFactor(p.positionCS.z);
                return o;
            }

            half4 frag(Varyings i) : SV_Target
            {
                float3 n = normalize(i.normalWS);
                float3 v = normalize(i.viewWS);
                half edge = pow(saturate(dot(n, v)), _Soft); // fades toward the silhouette

                Light light = GetMainLight();
                half lambert = saturate(dot(n, light.direction)) * 0.6 + 0.4;
                half3 col = i.color.rgb * _Color.rgb * lerp(half3(1, 1, 1), lambert * light.color, _Lit);
                col = MixFog(col, i.fogFactor);
                return half4(col, saturate(_Color.a * i.color.a * edge));
            }
            ENDHLSL
        }
    }

    // Built-in render pipeline (what the project currently uses: no URP asset is assigned in
    // Graphics/Quality settings). Unity skips the URP SubShader above and uses this one.
    SubShader
    {
        Tags { "RenderType" = "Transparent" "Queue" = "Transparent" "IgnoreProjector" = "True" }

        Pass
        {
            Tags { "LightMode" = "ForwardBase" } // so the main directional light is set
            Blend [_SrcBlend] [_DstBlend]
            ZWrite Off
            Cull Back

            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma multi_compile_fog
            #include "UnityCG.cginc"
            #include "UnityLightingCommon.cginc"

            half4 _Color;
            half  _Soft;
            half  _Lit;

            struct appdata
            {
                float4 vertex : POSITION;
                float3 normal : NORMAL;
                half4  color  : COLOR;
            };

            struct v2f
            {
                float4 pos      : SV_POSITION;
                float3 normalWS : TEXCOORD0;
                float3 viewWS   : TEXCOORD1;
                half4  color    : COLOR;
                UNITY_FOG_COORDS(2)
            };

            v2f vert(appdata v)
            {
                v2f o;
                o.pos      = UnityObjectToClipPos(v.vertex);
                o.normalWS = UnityObjectToWorldNormal(v.normal);
                o.viewWS   = WorldSpaceViewDir(v.vertex);
                o.color    = v.color;
                UNITY_TRANSFER_FOG(o, o.pos);
                return o;
            }

            half4 frag(v2f i) : SV_Target
            {
                float3 n = normalize(i.normalWS);
                float3 v = normalize(i.viewWS);
                half edge = pow(saturate(dot(n, v)), _Soft); // fades toward the silhouette

                half lambert = saturate(dot(n, normalize(_WorldSpaceLightPos0.xyz))) * 0.6 + 0.4;
                half3 col = i.color.rgb * _Color.rgb * lerp(half3(1, 1, 1), lambert * _LightColor0.rgb, _Lit);
                UNITY_APPLY_FOG(i.fogCoord, col);
                return half4(col, saturate(_Color.a * i.color.a * edge));
            }
            ENDCG
        }
    }
}
