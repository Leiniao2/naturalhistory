// The sky layer's cloud deck (see World/SkyLayer.cs): drifting clouds over the map, unlit. Clear
// sky lets the land show dimly below; thin cloud veils it; thick cloud cores hide it. The clouds
// are value noise in world space, so they line up across the deck.
//
// - Weather (_Weather, from the tiles' climate): R cloud cover, G thunderstorm, B blizzard.
//   Thunderstorms are dark towering cores with lightning flashes; blizzards are dense white cloud
//   with snow streaming along the wind.
// - Wind: the planet's belts by latitude (trade winds blowing west near the equator, westerlies in
//   mid-latitudes, polar easterlies), carrying the clouds (a two-phase flow map, so the bands can
//   shear without stretching the noise) and drawn as faint streaks over clear sky.
// - Sunset: a band of gold, orange, pink and violet sweeping slowly round the map, with a dimmer,
//   bluer night behind it and a sunrise ahead.
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
        _DayLength ("Seconds per day", Float) = 240
        _Weather ("Weather (R cover, G storm, B blizzard)", 2D) = "black" {}
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
            #include "UnityCG.cginc"

            fixed4 _Color, _CloudColor;
            float _Scale, _Speed, _Clear, _DayLength;
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

            float fbm(float2 p)
            {
                float v = 0.0, a = 0.5;
                for (int k = 0; k < 5; k++) { v += a * noise(p); p = p * 2.03 + 17.1; a *= 0.5; }
                return v;
            }

            // Prevailing wind at a point: east–west belts by latitude (0 equator .. 1 pole), with a
            // little drift toward or away from the equator
            float2 Wind(float2 w)
            {
                float mid = _WeatherRect.y + _WeatherRect.w * 0.5;
                float lat = saturate(abs(w.y - mid) / (_WeatherRect.w * 0.5));
                float l = min(lat, 0.85);
                float east = -cos(l * 9.42478);                    // -1 trades, +1 westerlies, -1 polar easterlies
                float north = sin(l * 9.42478) * 0.25 * sign(w.y - mid);
                return float2(east, north);
            }

            // Cloud field carried by the wind: two phases of a flow map, blended so the jump when
            // each phase restarts is never seen
            float Clouds(float2 w, float2 wind, out float lit)
            {
                const float period = 30.0;
                float t = _Time.y / period;
                float ph0 = frac(t), ph1 = frac(t + 0.5);
                float2 move = wind * _Speed * period;
                float2 p0 = (w - move * ph0) * _Scale;
                float2 p1 = (w - move * ph1) * _Scale + float2(37.2, 11.9);
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
                float2 wind = Wind(w);

                float lit;
                float n = Clouds(w, wind, lit);

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

                // Wind streaks over clear sky: thin lines stretched along the belt, racing with it
                float strength = abs(wind.x);
                float2 dir = normalize(wind + float2(1e-4, 0));
                float2 perp = float2(-dir.y, dir.x);
                float along = dot(w, dir), across = dot(w, perp);
                float streak = noise(float2(across * 3.0, along * 0.18 - _Time.y * _Speed * 1.6));
                streak = smoothstep(0.78, 0.95, streak) * strength * (1.0 - veil) * (1.0 - storm);
                col = lerp(col, float3(1, 1, 1), streak * 0.7);
                alpha += streak * 0.22;

                // Sunset band sweeping round the map: day, gold-to-violet dusk, bluer night, dawn
                float phase = frac((w.x - _WeatherRect.x) / _WeatherRect.z + _Time.y / _DayLength);
                float dusk = phase - 0.5, dawn = phase < 0.5 ? phase : phase - 1.0;
                float3 sunset = dusk < 0
                    ? lerp(float3(1.0, 0.62, 0.28), float3(1.0, 0.82, 0.45), saturate(-dusk / 0.08))   // orange to gold, day side
                    : lerp(float3(0.98, 0.45, 0.55), float3(0.55, 0.40, 0.75), saturate(dusk / 0.08));  // pink to violet, night side
                float3 sunrise = lerp(float3(1.0, 0.55, 0.45), float3(1.0, 0.85, 0.55), saturate(dawn / 0.06 + 0.5));
                float gDusk = exp(-dusk * dusk / 0.004), gDawn = exp(-dawn * dawn / 0.002);
                float night = smoothstep(0.52, 0.6, phase) * (1.0 - smoothstep(0.92, 0.99, phase));
                col *= lerp(float3(1, 1, 1), float3(0.62, 0.68, 0.88), night * 0.6);
                float catchLight = 0.45 + 0.55 * veil; // clouds take the colour more than clear haze
                col = lerp(col, col * sunset * 1.35, gDusk * catchLight);
                col = lerp(col, col * sunrise * 1.3, gDawn * catchLight * 0.8);

                return fixed4(col, saturate(alpha));
            }
            ENDCG
        }
    }
}
