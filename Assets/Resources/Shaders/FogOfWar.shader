// Fog of war over the map camera's image (FogOfWarEffect, FogOfWar). Each pixel's ground point
// comes from the depth buffer; the pointy-top hex under it (odd rows shifted right, the map
// wrapping east–west) is looked up in _NHFogTex: R in sight, G explored. Seven taps around the
// point soften the tile edges. Unexplored: drifting cloud with a pale rim where it meets explored
// land; explored but out of sight: dimmed, greyed colours; in sight: untouched.
Shader "Hidden/NH/FogOfWar"
{
    Properties
    {
        _MainTex ("Source", 2D) = "white" {}
    }
    SubShader
    {
        Cull Off ZWrite Off ZTest Always

        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma target 3.0
            #include "UnityCG.cginc"

            sampler2D _MainTex;
            float4 _MainTex_TexelSize;
            UNITY_DECLARE_DEPTH_TEXTURE(_CameraDepthTexture);
            sampler2D _NHFogTex;
            float4 _NHFogParams;  // on, cell size, width, height
            float4 _NHFogOrigin;  // grid origin x, z
            float4x4 _FrustumCorners; // rows: bottom-left, bottom-right, top-left, top-right

            struct v2f
            {
                float4 pos : SV_POSITION;
                float2 uv : TEXCOORD0;
                float2 uvDepth : TEXCOORD1;
                float3 ray : TEXCOORD2;
            };

            v2f vert(appdata_img v)
            {
                v2f o;
                o.pos = UnityObjectToClipPos(v.vertex);
                o.uv = v.texcoord;
                o.uvDepth = v.texcoord;
                #if UNITY_UV_STARTS_AT_TOP
                if (_MainTex_TexelSize.y < 0) o.uvDepth.y = 1 - o.uvDepth.y;
                #endif
                float2 s = o.uvDepth;
                float3 bottom = lerp(_FrustumCorners[0].xyz, _FrustumCorners[1].xyz, s.x);
                float3 top    = lerp(_FrustumCorners[2].xyz, _FrustumCorners[3].xyz, s.x);
                o.ray = lerp(bottom, top, s.y);
                return o;
            }

            // Fog state (in sight, explored) of the tile under a ground point
            float2 TileState(float2 xz)
            {
                float size = _NHFogParams.y;
                float2 p = (xz - _NHFogOrigin.xy) / size;
                float q = 0.57735027 * p.x - p.y / 3.0;
                float r = p.y * (2.0 / 3.0);
                // cube rounding
                float3 c = float3(q, r, -q - r);
                float3 rc = round(c);
                float3 d = abs(rc - c);
                if (d.x > d.y && d.x > d.z) rc.x = -rc.y - rc.z;
                else if (d.y > d.z) rc.y = -rc.x - rc.z;
                float row = rc.y;
                float col = rc.x + floor(row * 0.5);
                if (row < 0 || row >= _NHFogParams.w) return float2(0, 0); // past the poles
                float2 uv = float2((col + 0.5) / _NHFogParams.z, (row + 0.5) / _NHFogParams.w);
                return tex2Dlod(_NHFogTex, float4(uv, 0, 0)).rg; // wraps east–west (repeat)
            }

            float hash(float2 p) { return frac(sin(dot(p, float2(127.1, 311.7))) * 43758.5453); }
            float noise(float2 p)
            {
                float2 i = floor(p), f = frac(p);
                f = f * f * (3 - 2 * f);
                return lerp(lerp(hash(i), hash(i + float2(1, 0)), f.x), lerp(hash(i + float2(0, 1)), hash(i + float2(1, 1)), f.x), f.y);
            }
            float fbm(float2 p)
            {
                float v = 0, a = 0.5;
                for (int k = 0; k < 4; k++) { v += a * noise(p); p = p * 2.03 + 17.1; a *= 0.5; }
                return v;
            }

            fixed4 frag(v2f i) : SV_Target
            {
                fixed4 col = tex2D(_MainTex, i.uv);
                if (_NHFogParams.x < 0.5) return col;

                float raw = SAMPLE_DEPTH_TEXTURE(_CameraDepthTexture, i.uvDepth);
                float depth = LinearEyeDepth(raw);
                float3 world = _WorldSpaceCameraPos + i.ray * depth;
                float size = _NHFogParams.y;

                // soft tile edges: the tile under the point and six around it
                float2 s = TileState(world.xz) * 2.0;
                float rad = 0.42 * size;
                [unroll] for (int k = 0; k < 6; k++)
                {
                    float a = k * 1.0471976 + 0.5236;
                    s += TileState(world.xz + float2(cos(a), sin(a)) * rad);
                }
                s /= 8.0;
                float seen = s.x, known = s.y;

                // explored but out of sight: greyed and dimmed
                float lum = dot(col.rgb, float3(0.3, 0.59, 0.11));
                float3 dim = lerp(col.rgb, lum * float3(0.82, 0.88, 1.0), 0.6) * 0.5;
                float3 c = lerp(dim, col.rgb, seen);

                // unexplored: drifting cloud, lighter towards its edge
                float t = _Time.y;
                float2 cp = world.xz / (size * 2.2);
                float n = fbm(cp + float2(t * 0.03, t * 0.012));
                float n2 = fbm(cp * 2.7 - float2(t * 0.02, -t * 0.025));
                float3 cloud = lerp(float3(0.09, 0.11, 0.13), float3(0.30, 0.32, 0.35), saturate(n * 1.2 - 0.1));
                cloud += n2 * 0.06;
                float edge = saturate(1.0 - abs(known - 0.5) * 2.0);  // where explored meets unexplored
                cloud += float3(0.16, 0.16, 0.15) * edge * smoothstep(0.35, 0.75, n);
                // ragged edge: the cloud reaches a little into explored land where it is thick
                float cover = saturate((1.0 - known) * 1.6 + (n - 0.5) * 0.9 * edge);
                c = lerp(c, cloud, smoothstep(0.25, 0.75, cover));
                return fixed4(c, col.a);
            }
            ENDCG
        }
    }
    Fallback Off
}
