// The sky layer's cloud deck (see World/SkyLayer.cs): drifting clouds over the map, unlit. Clear
// sky lets the land show dimly below; thin cloud veils it; thick cloud and the big cloud banks hide it. The clouds
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
// - Cloud types: typhoons (spiral bands round a clear eye), fronts (long arcs of cloud), cumulus
//   (separate puffy cells over land on fair days), cirrus (high feathery wisps along the wind) and
//   volcanic ash plumes streaming downwind. Typhoons, fronts and plumes move and come and go on
//   the C# side (World/SkyFeatures.cs), passed in as small arrays.
// - Ground events seen from above (SkyFeatures, in step with NaturalEvents): a meteor's fireball
//   and trail over the clouds, the glow and smoke of its impact; a dark spinning cell over a
//   tornado, dust over a sandstorm, a white swirl over a blizzard.
// - Aurora: now and then, over part of a polar region, wavering green curtains fringed with pink
//   and violet shimmer above the clouds, then fade away. Each pole has its own spells.
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
        _WeatherPrev ("Previous weather (fading out)", 2D) = "black" {}
        _Peaks ("High mountains (R)", 2D) = "black" {}
        _WeatherBlend ("Previous to current weather", Range(0, 1)) = 1
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
            #pragma target 3.5
            #include "UnityCG.cginc"

            fixed4 _Color, _CloudColor;
            float _Scale, _Speed, _Clear, _DayLength, _SeasonLength;
            float4 _Weather_TexelSize;
            sampler2D _Weather, _WeatherPrev, _Peaks;
            float _WeatherBlend; // 0 = last turn's weather .. 1 = this turn's (SkyLayer fades it in)
            float4 _WeatherRect;
            float4 _Typhoons[4];             // x, z, radius, strength × spin (+1 north, -1 south); 0 = none
            float4 _FrontsA[6], _FrontsB[6]; // arc head (x, z), middle (x, z) | tail (x, z), width, strength
            float4 _Plumes[6];               // volcano x, z, strength, length
            float4 _Events[4];               // x, z, kind (1 tornado, 2 sandstorm, 3 blizzard), strength
            float4 _MeteorHead;              // x, z, brightness (0 = none)
            float4 _MeteorDir;               // direction of flight (x, z), trail length
            float4 _Impact;                  // x, z, glow, smoke
            float4 _AuroraBoost;             // admin: north, south strength
            float4 _CumulusBoost, _CirrusBoost; // admin: x, z, radius, strength

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
                // (tex2Dlod: no derivatives needed, so Wind can be called inside loops and branches)
                float2 grad = float2(tex2Dlod(_Weather, float4(uv + float2(e.x, 0), 0, 0)).a - tex2Dlod(_Weather, float4(uv - float2(e.x, 0), 0, 0)).a,
                                     tex2Dlod(_Weather, float4(uv + float2(0, e.y), 0, 0)).a - tex2Dlod(_Weather, float4(uv - float2(0, e.y), 0, 0)).a);
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
                // k = weight of phase 1: full when phase 0 restarts (ph0 = 0 or 1), none when phase 1 does
                float k = abs(1.0 - 2.0 * ph0);
                float n = lerp(fbm(p0), fbm(p1), k);
                // the sun side of each billow is brighter: compare with a sample toward the light
                float2 toSun = float2(-0.6, 0.8) * 0.08;
                float m = lerp(fbm(p0 + toSun), fbm(p1 + toSun), k);
                lit = saturate(0.55 + (n - m) * 5.0);
                return n;
            }

            // Offset from a point to a centre, taking the shorter way round the east–west wrap
            float2 Wrapped(float2 r)
            {
                r.x -= round(r.x / _WeatherRect.z) * _WeatherRect.z;
                return r;
            }

            // Typhoons: dense spiral bands winding in to a ring of towering cloud round a clear eye.
            // Returns the cloud they add; `eye` how much of the eye's clear air is here.
            float Typhoons(float2 w, out float eye)
            {
                float cloud = 0.0; eye = 0.0;
                for (int k = 0; k < 4; k++)
                {
                    float4 t = _Typhoons[k];
                    float strength = abs(t.w);
                    if (strength < 0.001) continue;
                    float2 r = Wrapped(w - t.xy);
                    float d = length(r) / t.z;
                    if (d > 1.4) continue;
                    float spin = sign(t.w);
                    float ang = atan2(r.y, r.x);
                    // log-spiral arms turning with the storm
                    float arms = sin(ang * 2.0 * spin + log(d + 0.04) * 5.0 + _Time.y * 0.5);
                    float band = smoothstep(-0.3, 0.7, arms) * (1.0 - smoothstep(0.55, 1.3, d));
                    float core = 1.0 - smoothstep(0.18, 0.5, d);
                    float2 rot = float2(cos(_Time.y * 0.25 * spin), sin(_Time.y * 0.25 * spin));
                    float2 rr = float2(r.x * rot.x - r.y * rot.y, r.x * rot.y + r.y * rot.x) / t.z;
                    float tex = 0.7 + 0.3 * noise(rr * 6.0 + k * 7.0);
                    float clear = 1.0 - smoothstep(0.05, 0.1, d);
                    cloud = max(cloud, saturate(max(band, core) * tex) * strength * (1.0 - clear));
                    eye = max(eye, clear * strength);
                }
                return cloud;
            }

            // Fronts: long arcs of cloud (a quadratic curve, measured as a few straight pieces)
            float Fronts(float2 w)
            {
                float cloud = 0.0;
                for (int k = 0; k < 6; k++)
                {
                    float strength = _FrontsB[k].w;
                    if (strength < 0.001) continue;
                    float2 mid = _FrontsA[k].zw;
                    float2 q = mid + Wrapped(w - mid);
                    float2 a = _FrontsA[k].xy, b = mid, c = _FrontsB[k].xy;
                    float best = 1e9, along = 0.0;
                    float2 prev = a;
                    for (int s = 1; s <= 8; s++)
                    {
                        float u = s / 8.0;
                        float2 pt = lerp(lerp(a, b, u), lerp(b, c, u), u);
                        float2 seg = pt - prev, rel = q - prev;
                        float h = saturate(dot(rel, seg) / max(dot(seg, seg), 1e-4));
                        float dd = length(rel - seg * h);
                        if (dd < best) { best = dd; along = (s - 1 + h) / 8.0; }
                        prev = pt;
                    }
                    float width = _FrontsB[k].z * (1.2 - 0.6 * along); // broad at the low, narrow at the tail
                    float band = exp(-best * best / (width * width));
                    float lumps = 0.6 + 0.4 * noise(q * 0.9 + k * 3.0);
                    cloud = max(cloud, band * lumps * strength * smoothstep(0.0, 0.08, along) * (1.0 - smoothstep(0.85, 1.0, along)));
                }
                return cloud;
            }

            // Cumulus: separate puffy cells (cellular noise), drifting slowly
            float Cumulus(float2 w)
            {
                float2 p = (w + float2(-_Time.y * 0.06, _Time.y * 0.02)) / 1.1;
                float2 i = floor(p), f = frac(p);
                float puff = 0.0;
                for (int y = -1; y <= 1; y++)
                for (int x = -1; x <= 1; x++)
                {
                    float2 o = float2(x, y);
                    float h = hash(i + o);
                    if (h < 0.35) continue; // not every cell has a cloud
                    float2 centre = o + 0.2 + 0.6 * float2(hash(i + o + 1.7), hash(i + o + 4.3));
                    float rad = 0.22 + 0.22 * hash(i + o + 9.1);
                    float d = length(f - centre) + (noise((p + o) * 5.0) - 0.5) * 0.12; // lumpy edges
                    puff = max(puff, smoothstep(rad, rad * 0.45, d));
                }
                return puff;
            }

            // Volcanic ash: plumes widening and thinning downwind from each smoking volcano
            float Ash(float2 w, out float glow)
            {
                float ash = 0.0; glow = 0.0;
                for (int k = 0; k < 6; k++)
                {
                    float4 v = _Plumes[k];
                    if (v.z < 0.001) continue;
                    float2 r = Wrapped(w - v.xy);
                    float2 cw = Wind(v.xy, (v.xy - _WeatherRect.xy) / _WeatherRect.zw);
                    float2 dir = normalize(cw + float2(1e-3, 0)), perp = float2(-dir.y, dir.x);
                    float along = dot(r, dir), across = dot(r, perp);
                    if (along < -1.0 || along > v.w * 1.2) continue;
                    float width = 0.25 + max(along, 0.0) * 0.22;
                    float body = exp(-across * across / (width * width)) * smoothstep(-0.5, 0.2, along) * (1.0 - smoothstep(v.w * 0.5, v.w, along));
                    float billow = 0.55 + 0.45 * fbm3(r * 0.9 - dir * _Time.y * 0.35 + k * 5.0);
                    ash = max(ash, saturate(body * billow * min(v.z, 1.2)));
                    glow = max(glow, exp(-dot(r, r) / 0.08) * saturate(v.z - 0.8)); // the vent, during an eruption
                }
                return ash;
            }

            // Ground events seen from above: cloud added (tornado cell, blizzard swirl), how dark
            // (tornado), how dusty (sandstorm), how snowy (blizzard)
            float Events(float2 w, out float dark, out float dust, out float blizzard)
            {
                float cloud = 0.0; dark = 0.0; dust = 0.0; blizzard = 0.0;
                for (int k = 0; k < 4; k++)
                {
                    float4 e = _Events[k];
                    if (e.w < 0.001) continue;
                    float2 r = Wrapped(w - e.xy);
                    float d = length(r);
                    float ang = atan2(r.y, r.x);
                    if (e.z < 1.5)      // tornado: a tight, dark, spinning storm cell
                    {
                        float rr = d / 1.3;
                        float swirl = 0.6 + 0.4 * sin(ang * 3.0 + log(rr + 0.05) * 4.0 + _Time.y * 2.5);
                        float c = (1.0 - smoothstep(0.3, 1.0, rr)) * swirl * e.w;
                        cloud = max(cloud, c); dark = max(dark, c);
                    }
                    else if (e.z < 2.5) // sandstorm: a billowing wall of dust
                    {
                        float c = (1.0 - smoothstep(0.6, 2.2, d)) * (0.55 + 0.45 * fbm3(r * 0.8 + _Time.y * 0.3)) * e.w;
                        dust = max(dust, c);
                    }
                    else                // blizzard: a white swirl
                    {
                        float swirl = 0.65 + 0.35 * sin(ang * 2.0 + d * 2.0 - _Time.y * 1.5);
                        float c = (1.0 - smoothstep(0.5, 2.0, d)) * swirl * e.w;
                        cloud = max(cloud, c); blizzard = max(blizzard, c);
                    }
                }
                return cloud;
            }

            fixed4 frag(v2f i) : SV_Target
            {
                float2 w = i.world;
                float2 uv = (w - _WeatherRect.xy) / _WeatherRect.zw;
                float4 wx = lerp(tex2D(_WeatherPrev, uv), tex2D(_Weather, uv), _WeatherBlend);
                float cover = wx.r, storm = wx.g, snow = wx.b;
                float2 wind = Wind(w, uv);

                // domain warp: billows, streets and holes instead of evenly spread noise
                float2 wq = w * _Scale * 0.35 + _Time.y * 0.006;
                float2 warp = float2(fbm3(wq), fbm3(wq + float2(5.2, 1.3))) * 2.2 - 1.1;

                float lit;
                float n = Clouds(w, wind, warp, lit);

                // Cloud banks: big slow masses where the cloud thickens into an opaque sheet that
                // hides the land below (more of them where the air is humid)
                float bank = smoothstep(0.42, 0.6, fbm3(w * _Scale * 0.2 + warp * 0.6 + float2(3.7, 1.9)))
                           * (0.55 + 0.45 * cover);

                // more cover (and any storm, and the banks) lowers the threshold: clear gaps, thin
                // veils, thick cores
                float lo = lerp(0.54, 0.32, saturate(cover + storm * 0.6 + snow * 0.6)) - bank * 0.16;
                float veil  = smoothstep(lo, lo + 0.16, n);
                float thick = smoothstep(lo + 0.06, lo + 0.22, n);

                // the cloud types: typhoons and fronts thicken the deck; cumulus pops up over land in
                // fair, moderately humid weather; a typhoon's eye is clear
                float eye;
                float spiral = Typhoons(w, eye);
                float front = Fronts(w);
                float fair = wx.a * smoothstep(0.15, 0.35, cover) * (1.0 - smoothstep(0.6, 0.85, cover)) * (1.0 - storm) * (1.0 - snow)
                           * smoothstep(0.35, 0.55, fbm3(w * 0.04 + 3.3));
                float2 cb = Wrapped(w - _CumulusBoost.xy);
                fair = max(fair, _CumulusBoost.w * (1.0 - smoothstep(_CumulusBoost.z * 0.5, _CumulusBoost.z, length(cb))));
                float puffs = fair > 0.01 ? Cumulus(w) * fair : 0.0;
                veil  = max(max(veil, spiral), max(front, puffs));
                thick = max(max(thick, spiral * spiral), max(front * front, puffs * 0.8));
                float evDark, evDust, evSnow;
                float evCloud = Events(w, evDark, evDust, evSnow);
                veil = max(veil, evCloud); thick = max(thick, evCloud);
                snow = max(snow, evSnow);
                veil *= 1.0 - eye; thick *= 1.0 - eye;
                lit = lerp(lit, 0.8, saturate(puffs * 1.5)); // cumulus tops catch the sun

                float alpha = lerp(_Clear, 0.5, veil) + thick * 0.48;
                alpha *= 1.0 - eye * 0.7;

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

                // the tornado's cell is dark like a thunderstorm's, the sandstorm a tan veil
                col = lerp(col, lerp(float3(0.18, 0.19, 0.24), float3(0.38, 0.39, 0.45), lit), saturate(evDark * 1.2));
                col = lerp(col, float3(0.80, 0.66, 0.44) * (0.85 + 0.25 * lit), evDust);
                alpha = max(alpha, max(evDark, evDust) * 0.92);

                // Blizzards: dense white cloud, snow streaming fast along the wind
                col = lerp(col, float3(0.92, 0.95, 1.0), snow * 0.8);
                alpha = lerp(alpha, max(alpha, 0.85), snow);
                float2 flow = w * 5.0 - wind * _Time.y * 6.0;
                float flakes = smoothstep(0.82, 0.98, noise(flow)) * snow;
                col = lerp(col, float3(1, 1, 1), flakes);
                alpha = max(alpha, flakes * 0.95);

                // Volcanic ash: dark grey-brown, nearly opaque, glowing at the vent during an eruption
                float vent;
                float ash = Ash(w, vent);
                col = lerp(col, lerp(float3(0.30, 0.27, 0.24), float3(0.46, 0.42, 0.38), lit), ash);
                alpha = max(alpha, ash * 0.93);
                col += float3(1.0, 0.45, 0.15) * vent * 1.2;

                // Wind streaks over clear sky: thin lines along the local wind, racing with it. Each
                // point of a coarse grid draws them in its own frame (its own wind direction), and the
                // four around a pixel are blended, so the streaks turn with the wind without bending
                // into rings far from the origin.
                const float cellW = 14.0;
                float2 g = w / cellW - 0.5, g0 = floor(g), f = frac(g);
                float streak = 0.0, cirrus = 0.0;
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
                    // cirrus: high feathery wisps, long along the wind, with fine fibres across them
                    float2 cq = float2(dot(r, perp) * 0.35 + c.y, dot(r, dir) * 0.05 - _Time.y * 0.01 + c.x);
                    float wisp = smoothstep(0.5, 0.75, fbm3(cq + warp * 0.3));
                    float fibre = 0.5 + 0.5 * noise(float2(dot(r, perp) * 4.0 + dot(r, dir) * 0.6, c.x));
                    cirrus += wisp * fibre * wgt;
                }
                // high cloud drifts over everything else, in some regions only
                float cirrusBoost = _CirrusBoost.w * (1.0 - smoothstep(_CirrusBoost.z * 0.5, _CirrusBoost.z, length(Wrapped(w - _CirrusBoost.xy))));
                cirrus *= max(smoothstep(0.45, 0.62, fbm3(w * 0.02 + float2(8.1, -_Time.y * 0.002))), cirrusBoost) * (1.0 - storm);
                col = lerp(col, float3(0.97, 0.98, 1.0), cirrus * 0.55);
                alpha = max(alpha, lerp(alpha, 0.6, cirrus * 0.6));
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

                // Past the poles (off the map's north and south edges) the cloud closes into a solid
                // polar cap, so the view never shows beyond the world
                float pole = max(_WeatherRect.y - w.y, w.y - (_WeatherRect.y + _WeatherRect.w));
                float cap = smoothstep(-1.5, 2.0, pole);
                col = lerp(col, lerp(float3(0.82, 0.86, 0.92), float3(0.95, 0.97, 1.0), lit), cap);
                alpha = lerp(alpha, 1.0, cap);

                // High mountains: the cloud parts around their summits so they stand out above it
                float peak = saturate(tex2D(_Peaks, uv).r * 1.6);
                alpha *= 1.0 - peak * 0.8;

                // Meteor: a white-hot head with a fiery trail behind it, then the impact's glow
                // through the clouds and its dark smoke spreading
                if (_MeteorHead.z > 0.001)
                {
                    float2 r = Wrapped(w - _MeteorHead.xy);
                    float2 dir = _MeteorDir.xy;
                    float behind = -dot(r, dir), side = dot(r, float2(-dir.y, dir.x));
                    float trail = saturate(1.0 - behind / _MeteorDir.z) * step(0.0, behind) * exp(-side * side / (0.02 + behind * 0.02));
                    float head = exp(-dot(r, r) / 0.03);
                    float3 fire = lerp(float3(1.0, 0.45, 0.12), float3(1.0, 0.95, 0.8), head);
                    float m = saturate(head + trail * 0.8) * _MeteorHead.z;
                    col = lerp(col, fire, m); col += fire * head * _MeteorHead.z;
                    alpha = max(alpha, m);
                }
                if (_Impact.z + _Impact.w > 0.001)
                {
                    float2 r = Wrapped(w - _Impact.xy);
                    float d2 = dot(r, r);
                    float smoke = _Impact.w * (1.0 - smoothstep(0.3, 1.6 + _Impact.w, sqrt(d2))) * (0.6 + 0.4 * fbm3(r * 1.2 + _Time.y * 0.2));
                    col = lerp(col, float3(0.28, 0.25, 0.23), smoke);
                    alpha = max(alpha, smoke * 0.9);
                    float glow = _Impact.z * exp(-d2 / 1.2);
                    col += float3(1.0, 0.55, 0.2) * glow * 1.6;
                    alpha = max(alpha, glow);
                }

                // Aurora: curtains of light along a wavering oval near each pole, on now and then
                {
                    float mid = _WeatherRect.y + _WeatherRect.w * 0.5, hspan = _WeatherRect.w * 0.5;
                    float north = w.y > mid ? 1.0 : 0.0;
                    float lat = saturate(abs(w.y - mid) / hspan);
                    // spells come and go over minutes, each pole on its own, and over some longitudes
                    float spell = smoothstep(0.5, 0.64, noise(float2(_Time.y / 70.0, north * 13.7 + 2.1)));
                    float boost = north > 0.5 ? _AuroraBoost.x : _AuroraBoost.y; // admin trigger
                    float along = (w.x - _WeatherRect.x) / _WeatherRect.z * 6.28318;
                    float reach = smoothstep(0.25, 0.5, noise(float2(cos(along) * 2.0 + north * 9.0, sin(along) * 2.0 + _Time.y * 0.01)));
                    float strength = max(spell * reach, boost * max(reach, 0.7));
                    if (strength > 0.001)
                    {
                        float aurora = 0.0, fringe = 0.0;
                        for (int c = 0; c < 2; c++)
                        {
                            // the curtain's line: a latitude that wavers along the oval and slowly writhes
                            float ridge = 0.8 - 0.06 * c
                                + 0.035 * sin(w.x * 0.11 + _Time.y * 0.07 + c * 2.0)
                                + 0.05 * (fbm3(float2(w.x * 0.035 + _Time.y * 0.02, c * 4.3 + north * 7.0)) - 0.5);
                            float d = (lat - ridge) * hspan;                 // world units across the curtain
                            float width = 1.3 + 0.6 * c;
                            float band = exp(-d * d / (width * width));
                            float tail = exp(-max(d, 0.0) / (width * 2.5)) * step(0.0, d); // trails poleward
                            float rays = 0.45 + 0.55 * noise(float2(w.x * 1.4 + _Time.y * 0.35 + c * 11.0, _Time.y * 0.6));
                            aurora += (band + tail * 0.5) * rays;
                            fringe += tail * rays;
                        }
                        aurora = saturate(aurora) * strength;
                        float3 green = float3(0.35, 1.0, 0.55), pink = float3(0.95, 0.35, 0.75), violet = float3(0.55, 0.35, 1.0);
                        float3 glow = lerp(green, lerp(pink, violet, 0.5 + 0.5 * sin(w.x * 0.05 + _Time.y * 0.05)), saturate(fringe * 0.7));
                        col = lerp(col, col * 0.5, aurora * 0.5) + glow * aurora * 1.5; // the sky around darkens a little, the light glows
                        alpha = max(alpha, aurora * 0.9);
                    }
                }

                return fixed4(col, saturate(alpha));
            }
            ENDCG
        }
    }
}
