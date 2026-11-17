// Flat-shaded props on top of hex tiles (mountain peaks, trees).
// Albedo comes from mesh vertex colors, so every prop shares this one material.
// _Flap bends everything beyond |x| > _FlapRoot (object space) up or down about the body's long
// axis, so a single static mesh can beat its wings or fins; _Stride swings everything below the hips
// back and forth as legs; _Undulate / _Coil bend a straight body into a travelling wave or a
// resting coil (snakes, eels). ColonyGroup
// drives them per renderer. _Sway rocks tall props gently back and forth, more toward the top
// (water plants on the seabed: HexGrid.Under uses a material with it set). _Fur draws a coat of
// hair on mammals (MapFeatureFur.cginc; World/AnimalFur sets it per renderer).
Shader "NaturalHistory/MapFeature"
{
    Properties
    {
        _Color ("Tint", Color) = (1, 1, 1, 1)
        _Flap ("Wing angle (radians)", Float) = 0
        _FlapRoot ("Wing root (half body width)", Float) = 0
        _FlapSpan ("Wing tip (half span)", Float) = 1
        [HideInInspector] _Stride ("Leg swing (radians)", Float) = 0
        [HideInInspector] _StridePhase ("Leg cycle phase", Float) = 0
        [HideInInspector] _StrideLegs ("Hip height, leg length, leg z min, leg z max", Vector) = (0, 1, -1, 1)
        [HideInInspector] _StrideMode ("Leg pairs, all legs together", Vector) = (2, 0, 0, 0)
        [HideInInspector] _Undulate ("Body wave amplitude (fraction of length)", Float) = 0
        [HideInInspector] _UndulatePhase ("Body wave phase", Float) = 0
        [HideInInspector] _UndulateBody ("Tail z, snout z, waves along the body, growth toward the tail", Vector) = (-1, 1, 1, 0.5)
        [HideInInspector] _Coil ("Coiled (0..1), inner radius, ring spacing, head rise", Vector) = (0, 0.06, 0.055, 0.07)
        _Sway ("Sway: amplitude, full-sway height, speed, wavelength", Vector) = (0, 1, 1, 1)
        [HideInInspector] _Fur ("Fur: amount, strands per unit", Vector) = (0, 0, 0, 0)
        [HideInInspector] _StencilRef ("Stencil: 1 for animals, so borders skip them", Int) = 0
    }

    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" "Queue" = "Geometry" }
        Stencil { Ref [_StencilRef] Comp Always Pass Replace } // see the built-in SubShader

        HLSLINCLUDE
        #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

        CBUFFER_START(UnityPerMaterial)
            half4 _Color;
            float _Flap;
            float _FlapRoot;
            float _FlapSpan;
            float _Stride;
            float _StridePhase;
            float4 _StrideLegs;
            float4 _StrideMode;
            float _Undulate;
            float _UndulatePhase;
            float4 _UndulateBody;
            float4 _Coil;
            float4 _Sway;
            float4 _Fur;
        CBUFFER_END

        #include "MapFeatureFlap.cginc"
        #include "MapFeatureFur.cginc"
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
                float2 band       : TEXCOORD2; // banded rock (BandColor)
                float2 flex       : TEXCOORD3; // bending in the wind (ApplyWind)
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
                float3 normalWS   : TEXCOORD1;
                half4  color      : COLOR;
                float  fogFactor  : TEXCOORD2;
                float2 band       : TEXCOORD3;
                float3 furPos     : TEXCOORD4; // object space before any bending (MapFeatureFur)
                float3 furNormal  : TEXCOORD5;
            };

            Varyings vert(Attributes v)
            {
                Varyings o;
                o.furPos    = v.positionOS.xyz;
                o.furNormal = v.normalOS;
                ApplyFlap(v.positionOS.xyz, v.normalOS);
                ApplyUndulate(v.positionOS.xyz, v.normalOS);
                ApplyStride(v.positionOS.xyz);
                ApplyGroundFit(v.positionOS.xyz);
                ApplySway(v.positionOS.xyz, v.flex.x);
                ApplyWind(v.positionOS.xyz, v.flex.x);
                VertexPositionInputs pos = GetVertexPositionInputs(v.positionOS.xyz);
                o.positionCS = pos.positionCS;
                o.positionWS = pos.positionWS;
                o.normalWS   = TransformObjectToWorldNormal(v.normalOS);
                o.color      = v.color;
                o.fogFactor  = ComputeFogFactor(pos.positionCS.z);
                o.band       = v.band;
                return o;
            }

            half4 frag(Varyings i) : SV_Target
            {
                float3 n      = normalize(i.normalWS);
                half3  albedo = i.color.rgb * _Color.rgb;
                if (i.band.y > 0.5) albedo *= BandColor(i.band);
                albedo *= FurShade(i.furPos, i.furNormal);

                Light mainLight = GetMainLight(TransformWorldToShadowCoord(i.positionWS));
                half3 viewDir   = GetWorldSpaceNormalizeViewDir(i.positionWS);
                half3 direct    = FurLight(albedo, n, mainLight.direction, viewDir, _Fur.x) * mainLight.color * mainLight.shadowAttenuation;

                return half4(MixFog(direct + albedo * SampleSH(n), i.fogFactor), 1);
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

            struct Attributes { float4 positionOS : POSITION; float3 normalOS : NORMAL; float2 flex : TEXCOORD3; };

            float4 vert(Attributes v) : SV_POSITION
            {
                ApplyFlap(v.positionOS.xyz, v.normalOS);
                ApplyUndulate(v.positionOS.xyz, v.normalOS);
                ApplyStride(v.positionOS.xyz);
                ApplyGroundFit(v.positionOS.xyz);
                ApplySway(v.positionOS.xyz, v.flex.x);
                ApplyWind(v.positionOS.xyz, v.flex.x);
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

            struct Attributes { float4 positionOS : POSITION; float2 flex : TEXCOORD3; };

            float4 vert(Attributes v) : SV_POSITION
            {
                float3 normalOS = float3(0, 1, 0);
                ApplyFlap(v.positionOS.xyz, normalOS);
                ApplyUndulate(v.positionOS.xyz, normalOS);
                ApplyStride(v.positionOS.xyz);
                ApplyGroundFit(v.positionOS.xyz);
                ApplySway(v.positionOS.xyz, v.flex.x);
                ApplyWind(v.positionOS.xyz, v.flex.x);
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
        // animals write 1 (SpeciesColonies), everything else 0: territory borders skip the 1s
        Stencil { Ref [_StencilRef] Comp Always Pass Replace }

        CGPROGRAM
        #pragma surface surf Fur fullforwardshadows addshadow vertex:vert
        #pragma target 3.0

        fixed4 _Color;
        float _Flap;
        float _FlapRoot;
        float _FlapSpan;
        float _Stride;
        float _StridePhase;
        float4 _StrideLegs;
        float4 _StrideMode;
        float _Undulate;
        float _UndulatePhase;
        float4 _UndulateBody;
        float4 _Coil;
        float4 _Sway;
        float4 _Fur;
        #include "MapFeatureFlap.cginc"
        #include "MapFeatureFur.cginc"

        struct Input
        {
            float4 color : COLOR;
            // object-space position and normal before any bending (MapFeatureFur), with the banded
            // rock coordinates (BandColor) in w, packed to stay within shader model 3's interpolators
            float4 nhFurPosBand;
            float4 nhFurNormalBand;
        };

        // Lambert, or with _Fur the wrapped light and sheen of a coat (Gloss carries the amount)
        half4 LightingFur(SurfaceOutput s, half3 lightDir, half3 viewDir, half atten)
        {
            return half4(FurLight(s.Albedo, s.Normal, lightDir, viewDir, s.Gloss) * _LightColor0.rgb * atten, s.Alpha);
        }

        void vert(inout appdata_full v, out Input o)
        {
            UNITY_INITIALIZE_OUTPUT(Input, o);
            o.nhFurPosBand    = float4(v.vertex.xyz, v.texcoord2.x);
            o.nhFurNormalBand = float4(v.normal, v.texcoord2.y);
            ApplyFlap(v.vertex.xyz, v.normal);
            ApplyUndulate(v.vertex.xyz, v.normal);
            ApplyStride(v.vertex.xyz);
            ApplyGroundFit(v.vertex.xyz);
            float flex = v.texcoord2.y > 0.5 ? 0 : v.texcoord3.x; // banded rock never bends
            ApplySway(v.vertex.xyz, flex);
            ApplyWind(v.vertex.xyz, flex);
        }

        void surf(Input IN, inout SurfaceOutput o)
        {
            o.Albedo = IN.color.rgb * _Color.rgb;
            float2 band = float2(IN.nhFurPosBand.w, IN.nhFurNormalBand.w);
            if (band.y > 0.5) o.Albedo *= BandColor(band);
            o.Albedo *= FurShade(IN.nhFurPosBand.xyz, IN.nhFurNormalBand.xyz);
            o.Gloss  = _Fur.x;
            o.Alpha  = 1;
        }
        ENDCG
    }

    FallBack "Diffuse"
}
