// The solid bedrock of the under view (HexGrid.Under.CreateBedrockMesh): one mass of rock across
// the tiles, skinned with real rock textures projected from three sides (top, and the two wall
// directions), so tops read as rock surfaces and walls as rock faces with their layers. Four skins
// (granite, limestone, basalt, sandstone) are mixed by region: the mesh's vertex colour carries
// each skin's weight (r, g, b, a). The texture coordinates are the map position (uv0 = x, z;
// uv1.x = height), not the world position, so they stay put when tiles move round the wrap.
Shader "NaturalHistory/RockMass"
{
    Properties
    {
        _SkinA ("Skin A (granite)", 2D) = "gray" {}
        _SkinB ("Skin B (limestone)", 2D) = "gray" {}
        _SkinC ("Skin C (basalt)", 2D) = "gray" {}
        _SkinD ("Skin D (sandstone)", 2D) = "gray" {}
        _Tiling ("Texture repeats per unit", Float) = 0.5
        _Tint ("Tint", Color) = (0.85, 0.85, 0.85, 1)
    }

    SubShader
    {
        Tags { "RenderType" = "Opaque" "Queue" = "Geometry" }

        CGPROGRAM
        #pragma surface surf Lambert fullforwardshadows addshadow vertex:vert
        #pragma target 3.5

        sampler2D _SkinA, _SkinB, _SkinC, _SkinD;
        float _Tiling;
        fixed4 _Tint;

        struct Input
        {
            float4 color : COLOR;
            float3 mapPos;
            float3 mapNormal;
        };

        void vert(inout appdata_full v, out Input o)
        {
            UNITY_INITIALIZE_OUTPUT(Input, o);
            o.mapPos = float3(v.texcoord.x, v.texcoord1.x, v.texcoord.y);
            o.mapNormal = v.normal;
        }

        fixed3 Tri(sampler2D tex, float3 p, float3 w)
        {
            return tex2D(tex, p.xz).rgb * w.y + tex2D(tex, p.zy).rgb * w.x + tex2D(tex, p.xy).rgb * w.z;
        }

        void surf(Input IN, inout SurfaceOutput o)
        {
            float3 w = pow(abs(normalize(IN.mapNormal)), 4);
            w /= w.x + w.y + w.z;
            float3 p = IN.mapPos * _Tiling;
            float4 k = IN.color / max(dot(IN.color, 1), 1e-4);
            fixed3 c = 0;
            if (k.r > 0.01) c += Tri(_SkinA, p, w) * k.r;
            if (k.g > 0.01) c += Tri(_SkinB, p, w) * k.g;
            if (k.b > 0.01) c += Tri(_SkinC, p, w) * k.b;
            if (k.a > 0.01) c += Tri(_SkinD, p, w) * k.a;
            o.Albedo = c * _Tint.rgb;
            o.Alpha = 1;
        }
        ENDCG
    }

    FallBack "Diffuse"
}
