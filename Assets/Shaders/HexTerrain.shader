// Terrain skin for hex tiles (URP).
// The texture is projected in world space (top: XZ, sides: XY/ZY), so it tiles
// seamlessly across neighbouring hexes instead of repeating per tile.
// _Color is a tint driven per-cell by HexCell's MaterialPropertyBlock (highlight, move targets).
// Also per cell (HexGrid.SetGroundLook): _Recolor repaints the ground texture's shading in another
// colour (white or red sand, dark gravel…), _CliffTint colours its rock faces, _Shore its beach.
// A large-scale pattern sampled from the same texture breaks up the repeats across wide areas.
Shader "NaturalHistory/HexTerrain"
{
    Properties
    {
        _BaseMap      ("Texture", 2D) = "white" {}
        _Color        ("Tint", Color) = (1, 1, 1, 1)
        _Tiling       ("World Tiling (texture repeats per unit)", Float) = 0.35
        _SideDarken   ("Side Darken", Range(0, 1)) = 0.35
        _EdgeDarken   ("Hex Edge Darken", Range(0, 1)) = 0.25
        _CliffTint    ("Cliff Rock Tint", Color) = (1, 0.97, 0.93, 1)
        _Land         ("Land (rock faces, surf)", Float) = 1
        [HideInInspector] _Recolor ("Ground recolour (rgb colour, a amount)", Vector) = (1, 1, 1, 0)
        [HideInInspector] _Shore   ("Beach (rgb sand colour, a 1 sand / 0 rock)", Vector) = (0.93, 0.8, 0.55, 0)
        [HideInInspector] _Flood   ("Floodplain wet hollows", Float) = 0
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
            half4  _CliffTint;
            half   _Land;
            float  _WrapShift;
            float4 _Recolor;
            float4 _Shore;
            half   _Flood;
        CBUFFER_END

        // Floodplains: dark, wet hollows and pools of standing water where the large-scale pattern
        // dips, with a second, finer pattern breaking up their outlines.
        half3 WetHollows(half3 albedo, half macroDip, half fineDip)
        {
            half wet  = smoothstep(0.04, 0.1, macroDip + fineDip * 0.5) * _Flood;
            half pool = smoothstep(0.11, 0.16, macroDip + fineDip * 0.5) * _Flood;
            albedo = lerp(albedo, albedo * half3(0.62, 0.7, 0.6), wet * 0.8);
            return lerp(albedo, half3(0.3, 0.42, 0.45), pool * 0.85);
        }

        // Ground texture repainted in _Recolor (land only): its light and shade kept, relative to the
        // texture's average (the smallest mip), so any texture gives the colour asked for on average.
        half3 Recolor(half3 tex, half avg)
        {
            half l = dot(tex, half3(0.299, 0.587, 0.114));
            return lerp(tex, _Recolor.rgb * (l / max(avg, 0.05)), _Recolor.a * _Land);
        }

        // Large, soft patches: the same texture sampled ~12x larger and at an angle, as a shade
        // multiplier around 1, so a wide stretch of one terrain doesn't look stamped.
        float2 MacroUV(float3 p) { return float2(p.x * 0.083 + p.z * 0.047, p.z * 0.083 - p.x * 0.047); }
        half MacroShade(half macroLum, half avg) { return 1.0 + clamp(macroLum - avg, -0.25, 0.25) * lerp(0.6, 1.1, _Land); }

        // Rock texture for steep land faces (the Mountain terrain's), set globally by HexGrid
        TEXTURE2D(_CliffTex); SAMPLER(sampler_CliffTex);

        // Steep land faces (sea cliffs, steep slopes) are bare rock, projected like the rest of the
        // terrain and darker, wet rock near the waterline.
        half3 CliffRock(float3 worldPos, float3 p, float3 n, half4 tint)
        {
            float2 uv = n.y > 0.5 ? p.xz : (abs(n.x) > abs(n.z) ? p.zy : p.xy);
            half3 rock = SAMPLE_TEXTURE2D(_CliffTex, sampler_CliffTex, uv * 1.5).rgb * tint.rgb;
            return rock * lerp(0.7, 1.0, saturate((worldPos.y - 0.02) / 0.1));
        }

        // On land: bare rock just above the sea (cliff foot, boulder apron) and a white line of surf
        // where the land meets the water. Returns the rock amount (x) and the surf amount (y).
        half2 Shoreline(float y, half land)
        {
            half rock = (1.0 - smoothstep(0.035, 0.055, y)) * land;
            half surf = smoothstep(0.012, 0.024, y) * (1.0 - smoothstep(0.034, 0.065, y)) * land;
            return half2(rock, surf);
        }
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
                half   avgLum  = dot(SAMPLE_TEXTURE2D_LOD(_BaseMap, sampler_BaseMap, topUV, 12).rgb, half3(0.299, 0.587, 0.114));
                half   macroDev = dot(SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, MacroUV(p)).rgb, half3(0.299, 0.587, 0.114)) - avgLum;
                topTex  = Recolor(topTex, avgLum) * MacroShade(macroDev + avgLum, avgLum);
                if (_Flood > 0.01)
                {
                    half fineDev = dot(SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, MacroUV(p.zyx) * 2.7).rgb, half3(0.299, 0.587, 0.114)) - avgLum;
                    topTex = WetHollows(topTex, -macroDev, -fineDev);
                }
                sideTex = Recolor(sideTex, avgLum);
                // On land only true cliffs (steeper than ~65°) turn to rock: the slopes between tiles
                // of different height (up to ~45°) keep the ground texture, so the land reads as
                // one continuous surface instead of a band of stones along every big height step.
                half   topW    = smoothstep(lerp(0.3, 0.25, _Land), lerp(0.9, 0.45, _Land), n.y);

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
                half3 rockCol = CliffRock(i.positionWS, p, n, _CliffTint);
                half3 side    = lerp(sideTex * (1.0 - _SideDarken), rockCol, _Land) * _Color.rgb;
                half3 albedo  = lerp(side, top, topW);
                half2 shore   = Shoreline(i.positionWS.y, _Land);
                // low coasts: a beach of sand (or shingle and rock) on the slope down to the water
                half3 sand    = _Shore.rgb * lerp(0.9, 1.08, saturate(dot(topTex, half3(0.299, 0.587, 0.114)) / max(avgLum, 0.05) * 0.5));
                half3 shoreCol = lerp(rockCol, sand, _Shore.a) * _Color.rgb;
                half  beach   = (1.0 - smoothstep(0.085, 0.115, i.positionWS.y)) * _Land * _Shore.a;
                albedo = lerp(albedo, shoreCol, max(shore.x, beach));
                albedo = lerp(albedo, half3(0.93, 0.95, 0.97), shore.y * 0.85);

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
        fixed4    _CliffTint;
        sampler2D _CliffTex; // rock texture for steep land faces (the Mountain terrain's), set globally by HexGrid
        half      _Land;
        float     _WrapShift;
        float4    _Recolor;
        float4    _Shore;
        half      _Flood;

        // Blending into the neighbouring tiles across each edge (as the URP pass does). Here it runs
        // only while _BuiltinEdgeBlend is on (the under view, set by HexGrid); _EdgeScale[e] is the
        // neighbour texture's world tiling (0 = this tile's), so each texture keeps its own size.
        sampler2D _EdgeTex0, _EdgeTex1, _EdgeTex2, _EdgeTex3, _EdgeTex4, _EdgeTex5;
        float4    _EdgeTint[6];
        float     _EdgeScale[6];
        float     _HexApothem;
        float     _HexBlendWidth;
        float     _BuiltinEdgeBlend;
        float     _AntiTile; // 1 on under-view seabed/lakebed tiles (HexCell.ShowUnder): hide the texture's repetition
        float     _CellBlend; // 1: blend this tile into its neighbours on the surface too (deserts, HexGrid.Desert)

        half3 EdgeTex(int e, float2 uv)
        {
            if (e == 0) return tex2D(_EdgeTex0, uv).rgb;
            if (e == 1) return tex2D(_EdgeTex1, uv).rgb;
            if (e == 2) return tex2D(_EdgeTex2, uv).rgb;
            if (e == 3) return tex2D(_EdgeTex3, uv).rgb;
            if (e == 4) return tex2D(_EdgeTex4, uv).rgb;
            return tex2D(_EdgeTex5, uv).rgb;
        }

        float EdgeDist(int e, float2 local)
        {
            float a = radians(60.0 * e + 30.0);
            return _HexApothem - dot(local, float2(sin(a), cos(a)));
        }

        // Same as the URP pass: bare rock on steep land faces, darker and wet near the waterline
        half3 CliffRock(float3 worldPos, float3 p, float3 n)
        {
            float2 uv = n.y > 0.5 ? p.xz : (abs(n.x) > abs(n.z) ? p.zy : p.xy);
            half3 rock = tex2D(_CliffTex, uv * 1.5).rgb * _CliffTint.rgb;
            return rock * lerp(0.7, 1.0, saturate((worldPos.y - 0.02) / 0.1));
        }

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
            bool   top = n.y > (_Land > 0.5 ? 0.35 : 0.5); // land slopes keep the ground texture; only cliffs are rock

            float2 uv = top ? p.xz : (abs(n.x) > abs(n.z) ? p.zy : p.xy);
            half3 albedo = tex2D(_BaseMap, uv * _BaseMap_ST.xy + _BaseMap_ST.zw).rgb;
            // Anti-tiling: mix in a copy turned 37° and scaled 0.79, the mix wandering over the
            // floor, so a small repeating pattern (mats, stromatolites) shows no rows or stripes
            if (top && _AntiTile > 0.5)
            {
                float2 ruv = float2(uv.x * 0.799 - uv.y * 0.602, uv.x * 0.602 + uv.y * 0.799) * 0.79 + 0.37;
                half3 other = tex2D(_BaseMap, ruv * _BaseMap_ST.xy).rgb;
                float wander = sin(p.x * 0.9 + sin(p.z * 0.7) * 1.3) * sin(p.z * 0.8 + sin(p.x * 0.6) * 1.1) * 0.5 + 0.5;
                albedo = lerp(albedo, other, smoothstep(0.2, 0.8, wander));
            }

            // Repaint in this tile's sand/soil colour (land only), keeping the texture's light and
            // shade relative to its average (the smallest mip)
            half avgLum = Luminance(tex2Dlod(_BaseMap, float4(uv * _BaseMap_ST.xy, 0, 12)).rgb);
            half lum    = Luminance(albedo);
            albedo = lerp(albedo, _Recolor.rgb * (lum / max(avgLum, 0.05)), _Recolor.a * _Land);
            // Large, soft patches: the same texture ~12x larger, at an angle, as a shade around 1
            float2 macroUV = float2(p.x * 0.083 + p.z * 0.047, p.z * 0.083 - p.x * 0.047);
            half macroDev = top ? Luminance(tex2D(_BaseMap, macroUV).rgb) - avgLum : 0;
            if (top) albedo *= 1.0 + clamp(macroDev, -0.25, 0.25) * lerp(0.6, 1.1, _Land) * (_AntiTile > 0.5 ? 0.25 : 1.0); // big diagonal bands of a patterned bed: barely
            // Floodplains: dark, wet hollows and pools of standing water where the large-scale
            // pattern dips, a finer pattern breaking up their outlines
            if (top && _Flood > 0.01)
            {
                half fineDev = Luminance(tex2D(_BaseMap, float2(p.z * 0.083 + p.x * 0.047, p.x * 0.083 - p.z * 0.047) * 2.7).rgb) - avgLum;
                half dip  = -macroDev - fineDev * 0.5;
                half wet  = smoothstep(0.04, 0.1, dip) * _Flood;
                half pool = smoothstep(0.11, 0.16, dip) * _Flood;
                albedo = lerp(albedo, albedo * half3(0.62, 0.7, 0.6), wet * 0.8);
                albedo = lerp(albedo, half3(0.3, 0.42, 0.45), pool * 0.85);
            }

            // Fade toward the neighbours' textures near each edge (nearest edge and, near a corner,
            // the next one), so adjacent tiles meet without a hard line
            if (top && (_BuiltinEdgeBlend > 0.5 || _CellBlend > 0.5))
            {
                float2 local  = IN.worldPos.xz - float2(unity_ObjectToWorld._m03, unity_ObjectToWorld._m23);
                float  angle  = atan2(local.x, local.y);
                float  sector = (angle < 0 ? angle + 6.2831853 : angle) / 1.0471976;
                int    e1     = (int)floor(sector) % 6;
                int    e2     = frac(sector) < 0.5 ? (e1 + 5) % 6 : (e1 + 1) % 6;
                half   w1     = _EdgeTint[e1].a * (1.0 - smoothstep(0.0, _HexBlendWidth, EdgeDist(e1, local)));
                half   w2     = _EdgeTint[e2].a * (1.0 - smoothstep(0.0, _HexBlendWidth, EdgeDist(e2, local)));
                if (w1 + w2 > 0.001)
                {
                    float2 wp = (IN.worldPos - float3(_WrapShift, 0, 0)).xz;
                    half3 n1 = EdgeTex(e1, wp * (_EdgeScale[e1] > 0 ? _EdgeScale[e1] : _Tiling)) * _EdgeTint[e1].rgb / max(_Color.rgb, 0.01);
                    half3 n2 = EdgeTex(e2, wp * (_EdgeScale[e2] > 0 ? _EdgeScale[e2] : _Tiling)) * _EdgeTint[e2].rgb / max(_Color.rgb, 0.01);
                    albedo = (albedo + n1 * w1 + n2 * w2) / (1.0 + w1 + w2);
                }
            }

            if (top)
            {
                float r = length(IN.hexUV - 0.5) * 2.0;
                albedo *= 1.0 - _EdgeDarken * smoothstep(0.72, 1.0, r);
            }
            else
            {
                albedo = lerp(albedo * (1.0 - _SideDarken), CliffRock(IN.worldPos, p, n), _Land);
            }
            albedo *= _Color.rgb;

            // On land: bare rock just above the sea (cliff foot, boulder apron), then a line of surf
            float y   = IN.worldPos.y;
            half rock = (1.0 - smoothstep(0.035, 0.055, y)) * _Land;
            half surf = smoothstep(0.012, 0.024, y) * (1.0 - smoothstep(0.034, 0.065, y)) * _Land;
            // Low coasts: a beach of sand (or shingle and rock) on the slope down to the water
            half3 sand     = _Shore.rgb * lerp(0.9, 1.08, saturate(lum / max(avgLum, 0.05) * 0.5));
            half3 shoreCol = lerp(CliffRock(IN.worldPos, p, n), sand, _Shore.a) * _Color.rgb;
            half  beach    = (1.0 - smoothstep(0.085, 0.115, y)) * _Land * _Shore.a;
            albedo = lerp(albedo, shoreCol, max(rock, beach));
            albedo = lerp(albedo, half3(0.93, 0.95, 0.97), surf * 0.85);

            o.Albedo = albedo;
            o.Alpha  = 1;
        }
        ENDCG
    }

    FallBack "Diffuse"
}
