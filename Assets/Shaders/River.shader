// Rivers (HexGrid.Rivers): vertex colour is the water or bank colour, alpha 1 on the water and 0 on
// the banks. uv.x runs across the river (0..1), uv.y along it in world units, increasing downstream
// and continuous from tile to tile, so ripples and glints drift down the whole river.
Shader "NaturalHistory/River"
{
    Properties
    {
        _Color     ("Tint", Color) = (1, 1, 1, 1)
        _FlowSpeed ("Flow speed (units per second)", Float) = 0.12
        _Ripple    ("Ripple strength", Range(0, 1)) = 0.22
    }

    // Built-in render pipeline (what the project uses; see HexTerrain.shader)
    SubShader
    {
        Tags { "RenderType" = "Opaque" "Queue" = "Geometry" }

        CGPROGRAM
        #pragma surface surf Lambert vertex:vert fullforwardshadows
        #pragma target 3.0

        fixed4 _Color;
        float  _FlowSpeed;
        half   _Ripple;

        struct Input
        {
            float4 color : COLOR;
            float2 flow;
        };

        void vert(inout appdata_full v, out Input o)
        {
            UNITY_INITIALIZE_OUTPUT(Input, o);
            o.flow = v.texcoord.xy;
        }

        void surf(Input IN, inout SurfaceOutput o)
        {
            half  water = IN.color.a;
            float u = IN.flow.x, v = IN.flow.y;
            float t = _Time.y * _FlowSpeed;
            // long streaks carried downstream, wobbling across the channel, and a finer chop
            float s1 = sin((v - t) * 26.0 + sin(u * 6.0 + v * 7.0) * 1.6);
            float s2 = sin((v - t * 1.35) * 47.0 + u * 13.0 + sin(v * 11.0) * 2.0);
            half  ripple = saturate(s1 * 0.5 + 0.5) * saturate(s2 * 0.5 + 0.5);
            half  mid    = 1.0 - abs(u * 2.0 - 1.0); // 1 in the middle of the channel, 0 at the banks
            half3 col    = IN.color.rgb * _Color.rgb;
            col *= 1.0 + water * (ripple - 0.25) * _Ripple * (0.4 + 0.6 * mid);
            o.Albedo   = col;
            o.Emission = water * pow(ripple, 6.0) * 0.12 * mid * half3(0.85, 0.95, 1.0); // glints
            o.Alpha    = 1;
        }
        ENDCG
    }

    FallBack "Diffuse"
}
