// The sky layer's cloud deck (see World/SkyLayer.cs): drifting clouds over the map, unlit. Clear
// sky lets the land show dimly below; thin cloud veils it; thick cloud cores hide it. The clouds
// are value noise in world space, so they line up across the deck.
//
// - Weather (_Weather, from the tiles' climate): R cloud cover, G thunderstorm, B blizzard.
//   Thunderstorms are dark towering cores with lightning flashes; blizzards are dense white cloud
//   with snow streaming along the wind.
// - Wind: a mix of the latitude belts (trade winds, westerlies, polar easterlies), monsoons that
//   blow onto the continents and then, half a season later, off them (_Weather A is the land), and
//   big wandering eddies (curl noise), so directions vary from region to region and over time. It
//   carries the clouds (a two-phase flow map, so the flow can shear without stretching the noise)
//   and shows as faint streaks over clear sky. The clouds themselves are domain-warped noise, so
//   they don't line up in rows.
// - Colour: a few clouds glow gold or pink, more of them pink toward one side of the world and gold
//   toward the other, the sides turning slowly with no visible line between them.
// No LightMode tag and plain UnityCG, so it renders in both the built-in pipeline and URP. Lives in
// Resources so it is included in builds and found by Resources.Load.
Shader "NaturalHistory/SkyVeil"
{
    Properties
    {
        _Color ("Haze", Color) = (0.72, 0.80, 0.92, 1)
        _CloudColor ("Clouds", Color) = (0.97, 0.98, 1.0, 1)
        _Scale ("Cloud scale (per unit)", Float) = 0.18
        _Speed ("Wind (units per second)", Float) = 0.35
        _Clear ("Clear-sky opacity", Range(0, 1)) = 0.12
        _DayLength ("Seconds per pink/gold turn", Float) = 400
        _SeasonLength ("Seconds per monsoon season cycle", Float) = 300
        _Weather ("Weather (R cover, G storm, B blizzard, A land)", 2D) = "black" {}
        _WeatherRect ("Weather rect (x, z, width, depth)", Vector) = (0, 0, 1, 1)
    }
    SubShader
    {
        Tags { "Queue" = "Transparent" "RenderType" = "Transparent" "IgnoreProjector" = "True" }

        Pass
        {
            Blend SrcAlpha OneMinusSrcAlpha
            ZWrite Off
            Cull Off

            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma target 3.0
            #include "UnityCG.cginc"

            fixed4 _Color, _CloudColor;
            float _Scale, _Speed, _Clear, _DayLength, _SeasonLength;
            float4 _Weather_TexelSize;
            sampler2D _Weather;
            float4 _WeatherRect;

            struct appdata { float4 vertex : POSITION; };
            struct v2f { float4 pos : SV_POSITION; float2 world : TEXCOORD0; };

            v2f vert(appdata v)
            {
                v2f o;
                o.pos = UnityObjectToClipPos(v.vertex);
                o.world = mul(unity_ObjectToWorld, v.vertex).xz;
                return o;
            }

            float hash(float2 p) { return frac(sin(dot(p, float2(127.1, 311.7))) * 43758.5453); }

            float noise(float2 p)
            {
                float2 i = floor(p), f = frac(p);
                float2 u = f * f * (3.0 - 2.0 * f);
                return lerp(lerp(hash(i), hash(i + float2(1, 0)), u.x),
                            lerp(hash(i + float2(0, 1)), hash(i + float2(1, 1)), u.x), u.y);
            }

            float fbm3(float2 p)
            {
                return 0.5 * noise(p) + 0.25 * noise(p * 2.03 + 17.1) + 0.125 * noise(p * 4.1 + 5.3);
            }

            float fbm(float2 p)
            {
                float v = 0.0, a = 0.5;
                for (int k = 0; k < 5; k++) { v += a * noise(p); p = p * 2.03 + 17.1; a *= 0.5; }
                return v;
            }

            // Wind at a point (world units per unit of _Speed): latitude belts, monsoons and eddies
            float2 Wind(float2 w, float2 uv)
            {
                float mid = _WeatherRect.y + _WeatherRect.w * 0.5;
                float lat = saturate(abs(w.y - mid) / (_WeatherRect.w * 0.5));
                float l = min(lat, 0.85);
                float2 belt = float2(-cos(l * 9.42478), sin(l * 9.42478) * 0.25 * sign(w.y - mid));

                // monsoon: onto the land in one half of the season cycle, off it in the other
                float2 e = _Weather_TexelSize.xy * 3.0;
                float2 grad = float2(tex2D(_Weather, uv + float2(e.x, 0)).a - tex2D(_Weather, uv - float2(e.x, 0)).a,
                                     tex2D(_Weather, uv + float2(0, e.y)).a - tex2D(_Weather, uv - float2(0, e.y)).a);
                float season = sin(_Time.y * 6.28318 / _SeasonLength);
                float2 monsoon = grad * 4.0 * season;

                // eddies: the curl of a slowly changing potential (always swirls, never converges)
                float2 q = w * 0.035 + float2(_Time.y * 0.004, -_Time.y * 0.003);
                const float d = 0.35;
                float pc = fbm3(q), px = fbm3(q + float2(d, 0)), pz = fbm3(q + float2(0, d));
                float2 eddy = float2(pz - pc, -(px - pc)) / d * 6.0;

                float2 wind = belt * 0.45 + monsoon + eddy;
                float len = length(wind);
                return len > 1.6 ? wind * (1.6 / len) : wind;
            }

            // Cloud field carried by the wind: two phases of a flow map, blended so the jump when
            // each phase restarts is never seen
            float Clouds(float2 w, float2 wind, float2 warp, out float lit)
            {
                const float period = 30.0;
                float t = _Time.y / period;
                float ph0 = frac(t), ph1 = frac(t + 0.5);
                float2 move = wind * _Speed * period;
                float2 p0 = (w - move * ph0) * _Scale + warp;
                float2 p1 = (w - move * ph1) * _Scale + float2(37.2, 11.9) + warp;
                float k = abs(1.0 - 2.0 * ph0);
                float n = lerp(fbm(p1), fbm(p0), k);
                // the sun side of each billow is brighter: compare with a sample toward the light
                float2 toSun = float2(-0.6, 0.8) * 0.08;
                float m = lerp(fbm(p1 + toSun), fbm(p0 + toSun), k);
                lit = saturate(0.55 + (n - m) * 5.0);
                return n;
            }

            fixed4 frag(v2f i) : SV_Target
            {
                float2 w = i.world;
                float2 uv = (w - _WeatherRect.xy) / _WeatherRect.zw;
                float4 wx = tex2D(_Weather, uv);
                float cover = wx.r, storm = wx.g, snow = wx.b;
                float2 wind = Wind(w, uv);

                // domain warp: billows, streets and holes instead of evenly spread noise
                float2 wq = w * _Scale * 0.35 + _Time.y * 0.006;
                float2 warp = float2(fbm3(wq), fbm3(wq + float2(5.2, 1.3))) * 2.2 - 1.1;

                float lit;
                float n = Clouds(w, wind, warp, lit);

                // more cover (and any storm) lowers the threshold: clear gaps, thin veils, thick cores
                float lo = lerp(0.6, 0.36, saturate(cover + storm * 0.6 + snow * 0.6));
                float veil  = smoothstep(lo, lo + 0.18, n);
                float thick = smoothstep(lo + 0.12, lo + 0.34, n);
                float alpha = lerp(_Clear, 0.5, veil) + thick * 0.45;

                float3 shadow = float3(0.60, 0.66, 0.76);
                float3 col = lerp(_Color.rgb, lerp(shadow, _CloudColor.rgb, lit), veil);

                // Thunderstorms: dark, towering, nearly opaque, lit from inside by lightning
                float core = storm * thick;
                col = lerp(col, lerp(float3(0.22, 0.24, 0.32), float3(0.45, 0.47, 0.55), lit), saturate(core * 1.1));
                alpha = max(alpha, lerp(alpha, 0.97, core));
                float2 bolt = floor(w * 0.4);
                float flick = hash(bolt + floor(_Time.y * 7.0) * 0.731);
                float2 spot = frac(w * 0.4) - (0.3 + 0.4 * float2(hash(bolt + 3.1), hash(bolt + 7.7)));
                float flash = step(0.975, flick) * saturate(1.0 - length(spot) * 2.2) * core;
                col += float3(0.85, 0.88, 1.0) * flash * 1.6;

                // Blizzards: dense white cloud, snow streaming fast along the wind
                col = lerp(col, float3(0.92, 0.95, 1.0), snow * 0.8);
                alpha = lerp(alpha, max(alpha, 0.85), snow);
                float2 flow = w * 5.0 - wind * _Time.y * 6.0;
                float flakes = smoothstep(0.82, 0.98, noise(flow)) * snow;
                col = lerp(col, float3(1, 1, 1), flakes);
                alpha = max(alpha, flakes * 0.95);

                // Wind streaks over clear sky: thin lines along the local wind, racing with it. Each
                // point of a coarse grid draws them in its own frame (its own wind direction), and the
                // four around a pixel are blended, so the streaks turn with the wind without bending
                // into rings far from the origin.
                const float cellW = 14.0;
                float2 g = w / cellW - 0.5, g0 = floor(g), f = frac(g);
                float streak = 0.0;
                for (int k = 0; k < 4; k++)
                {
                    float2 o = float2(fmod((float)k, 2.0), floor(k * 0.5));
                    float2 c = (g0 + o + 0.5) * cellW;
                    float2 cw = Wind(c, (c - _WeatherRect.xy) / _WeatherRect.zw);
                    float sp = length(cw);
                    float2 dir = cw / max(sp, 1e-3), perp = float2(-dir.y, dir.x);
                    float2 r = w - c;
                    float s1 = noise(float2(dot(r, perp) * 3.0 + c.x, dot(r, dir) * 0.18 - _Time.y * _Speed * 1.6 * sp + c.y));
                    float wgt = (o.x > 0 ? f.x : 1 - f.x) * (o.y > 0 ? f.y : 1 - f.y);
                    streak += smoothstep(0.8, 0.96, s1) * saturate(sp) * wgt;
                }
                streak *= (1.0 - veil) * (1.0 - storm);
                col = lerp(col, float3(1, 1, 1), streak * 0.7);
                alpha += streak * 0.22;

                // Gold and pink clouds: a few patches of cloud catch a warm colour; toward one side of
                // the world (turning slowly) they lean pink, toward the other gold, blending smoothly
                float side = 0.5 + 0.5 * cos(((w.x - _WeatherRect.x) / _WeatherRect.z + _Time.y / _DayLength) * 6.28318);
                float2 tq = w * 0.045 + float2(-_Time.y * 0.01, _Time.y * 0.007);
                float pinkness = saturate(side * 0.8 + (fbm3(tq * 1.7 + 9.1) - 0.45) * 1.6);
                float3 warm = lerp(float3(1.0, 0.84, 0.50), float3(1.0, 0.62, 0.74), pinkness);
                float patch = smoothstep(0.5, 0.66, fbm3(tq)) * veil * (1.0 - storm) * (1.0 - snow);
                col = lerp(col, col * warm * 1.12, patch * 0.85);

                return fixed4(col, saturate(alpha));
            }
            ENDCG
        }
    }
}
