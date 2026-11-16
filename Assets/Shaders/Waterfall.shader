// Falling and churning water for the waterfalls (WaterfallFx): the curtain, the rapids on the
// brink above it and the plunge pool below. Vertex colour is the water colour (alpha = opacity);
// uv runs across (x) and along the flow (y) in world units; uv2.x is how foamy the water is there
// (0 clear, 1 white water) and uv2.y how fast it moves. Streaks of foam race along the flow,
// break up where the water is rough and sparkle; both faces are drawn and lit.
Shader "NaturalHistory/Waterfall"
{
    Properties
    {
        _Color     ("Tint", Color) = (1, 1, 1, 1)
        _FoamColor ("Foam", Color) = (0.95, 0.98, 1, 1)
        _Speed     ("Flow speed (units per second)", Float) = 1
        _Streaks   ("Streak scale (across, along)", Vector) = (34, 6, 0, 0)
    }

    // Built-in render pipeline (what the project uses; see HexTerrain.shader)
    SubShader
    {
        Tags { "RenderType" = "Transparent" "Queue" = "Transparent-10" "IgnoreProjector" = "True" }

        Pass
        {
            Tags { "LightMode" = "ForwardBase" }
            Blend SrcAlpha OneMinusSrcAlpha
            ZWrite On
            Cull Off

            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma multi_compile_fog
            #include "UnityCG.cginc"
            #include "UnityLightingCommon.cginc"

            half4  _Color;
            half4  _FoamColor;
            float  _Speed;
            float4 _Streaks;

            struct appdata
            {
                float4 vertex : POSITION;
                float3 normal : NORMAL;
                half4  color  : COLOR;
                float2 uv     : TEXCOORD0;
                float2 uv2    : TEXCOORD1;
            };

            struct v2f
            {
                float4 pos      : SV_POSITION;
                half4  color    : COLOR;
                float2 uv       : TEXCOORD0;
                float2 uv2      : TEXCOORD1;
                float3 normalWS : TEXCOORD2;
                float3 viewWS   : TEXCOORD3;
                UNITY_FOG_COORDS(4)
            };

            float Hash(float2 p)
            {
                p = frac(p * float2(123.34, 456.21));
                p += dot(p, p + 45.32);
                return frac(p.x * p.y);
            }

            float Noise(float2 p)
            {
                float2 i = floor(p), f = frac(p);
                f = f * f * (3.0 - 2.0 * f);
                return lerp(lerp(Hash(i), Hash(i + float2(1, 0)), f.x),
                            lerp(Hash(i + float2(0, 1)), Hash(i + float2(1, 1)), f.x), f.y);
            }

            v2f vert(appdata v)
            {
                v2f o;
                o.pos      = UnityObjectToClipPos(v.vertex);
                o.color    = v.color;
                o.uv       = v.uv;
                o.uv2      = v.uv2;
                o.normalWS = UnityObjectToWorldNormal(v.normal);
                o.viewWS   = WorldSpaceViewDir(v.vertex);
                UNITY_TRANSFER_FOG(o, o.pos);
                return o;
            }

            half4 frag(v2f i) : SV_Target
            {
                float t = _Time.y * _Speed * i.uv2.y;
                float2 p = float2(i.uv.x * _Streaks.x, (i.uv.y - t) * _Streaks.y);
                // long streaks along the flow, broken up by finer, faster ones
                float n = Noise(p) * 0.55
                        + Noise(p * float2(2.3, 2.6) + float2(7.1, -t * 3.0)) * 0.3
                        + Noise(p * float2(5.2, 6.1) + float2(3.3, -t * 7.0)) * 0.15;
                half bias = i.uv2.x;
                half foam = smoothstep(0.62, 0.8, n + bias * 0.55);

                half3 col = lerp(i.color.rgb * (0.82 + 0.36 * n), _FoamColor.rgb, foam) * _Color.rgb;

                // lit from either side, never darker than the shade of the far side
                float3 nrm = normalize(i.normalWS);
                float3 view = normalize(i.viewWS);
                nrm *= dot(nrm, view) < 0 ? -1.0 : 1.0;
                half lambert = saturate(dot(nrm, normalize(_WorldSpaceLightPos0.xyz))) * 0.45 + 0.55;
                col *= lerp(half3(1, 1, 1), lambert * _LightColor0.rgb + half3(0.12, 0.14, 0.16), 0.55);
                col += pow(saturate(n + bias * 0.3), 9.0) * 0.6 * half3(0.9, 0.97, 1.0); // sparkle

                UNITY_APPLY_FOG(i.fogCoord, col);
                return half4(col, saturate(i.color.a + foam * 0.6) * _Color.a);
            }
            ENDCG
        }
    }

    FallBack Off
}
