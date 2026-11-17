// Rain and snow falling on the surface under the sky layer's storms (World/WeatherFall.cs). Each
// drop or flake is a quad baked once into a static mesh: its vertices all sit at the drop's spot at
// the top of the fall, with the corner in uv0 and the drop's phase and size in uv1. The vertex
// shader moves it down through the fall (looping), drifts it sideways, and opens it toward the
// camera: rain as a thin streak standing along the fall, snow as a soft round flake that sways.
// Unlit; plain UnityCG, so it renders in the built-in pipeline and URP. Lives in Resources so it
// is included in builds and found by Resources.Load.
Shader "NaturalHistory/WeatherFall"
{
    Properties
    {
        _Color ("Colour", Color) = (0.78, 0.84, 0.95, 0.55)
        _Round ("0 = rain streak, 1 = snow flake", Range(0, 1)) = 0
        _Fall ("Fall height (world)", Float) = 1
        _Speed ("Fall speed (world per second)", Float) = 2.5
        _Width ("Drop width (world)", Float) = 0.008
        _Length ("Drop length (world)", Float) = 0.12
        _Drift ("Sideways drift per unit fallen (x, z)", Vector) = (0.12, 0.05, 0, 0)
        _Sway ("Snow sway (world)", Float) = 0
    }
    SubShader
    {
        Tags { "Queue" = "Transparent" "RenderType" = "Transparent" "IgnoreProjector" = "True" "DisableBatching" = "True" }
        Pass
        {
            Blend SrcAlpha OneMinusSrcAlpha
            ZWrite Off
            Cull Off

            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"

            fixed4 _Color;
            float _Round, _Fall, _Speed, _Width, _Length, _Sway;
            float4 _Drift;

            struct appdata { float4 vertex : POSITION; float2 corner : TEXCOORD0; float2 drop : TEXCOORD1; };
            struct v2f { float4 pos : SV_POSITION; float2 uv : TEXCOORD0; float fade : TEXCOORD1; };

            v2f vert(appdata v)
            {
                v2f o;
                float phase = v.drop.x, size = v.drop.y;
                float t = frac(_Time.y * _Speed / _Fall + phase);
                float fallen = t * _Fall;
                float3 w = mul(unity_ObjectToWorld, v.vertex).xyz;
                w += float3(_Drift.x * fallen, -fallen, _Drift.y * fallen);
                w.x += sin(_Time.y * 1.7 + phase * 40.0) * _Sway;
                w.z += cos(_Time.y * 1.3 + phase * 23.0) * _Sway;

                float3 right = UNITY_MATRIX_V[0].xyz, camUp = UNITY_MATRIX_V[1].xyz;
                float3 along = lerp(normalize(float3(_Drift.x, -1.0, _Drift.y)), camUp, _Round);
                float width = _Width * size, len = lerp(_Length, _Width, _Round) * size;
                w += right * v.corner.x * width + along * v.corner.y * len;

                o.pos = mul(UNITY_MATRIX_VP, float4(w, 1.0));
                o.uv = v.corner * 0.5 + 0.5;
                o.fade = saturate(t * 6.0) * saturate((1.0 - t) * 6.0); // in at the top, out at the ground
                return o;
            }

            fixed4 frag(v2f i) : SV_Target
            {
                float2 d = i.uv - 0.5;
                float streak = saturate(1.0 - abs(d.x) * 2.0); streak *= streak;
                streak *= saturate(1.0 - abs(d.y) * 2.0);
                float disc = saturate(1.0 - length(d) * 2.0); disc *= disc;
                float a = lerp(streak, disc, _Round);
                return fixed4(_Color.rgb, _Color.a * a * i.fade);
            }
            ENDCG
        }
    }
}
