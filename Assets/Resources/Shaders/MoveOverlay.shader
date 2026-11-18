// Movement overlay (see World/MovePathView.cs): the outline of where a selected group can go this
// turn and the arrow of the path to the tile under the mouse. Unlit vertex colours with alpha, drawn
// after everything and over it (no depth test), so trees and hills never hide it. No LightMode tag
// and plain UnityCG, so it renders in both the built-in pipeline and URP. Lives in Resources so it
// is included in builds and found by Resources.Load.
Shader "NaturalHistory/MoveOverlay"
{
    SubShader
    {
        Tags { "Queue" = "Overlay" "RenderType" = "Transparent" "IgnoreProjector" = "True" }

        Pass
        {
            Blend SrcAlpha OneMinusSrcAlpha
            ZWrite Off
            ZTest Always
            Cull Off

            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"

            struct appdata { float4 vertex : POSITION; fixed4 color : COLOR; };
            struct v2f { float4 pos : SV_POSITION; fixed4 color : COLOR; };

            v2f vert(appdata v)
            {
                v2f o;
                o.pos = UnityObjectToClipPos(v.vertex);
                o.color = v.color;
                return o;
            }

            fixed4 frag(v2f i) : SV_Target { return i.color; }
            ENDCG
        }
    }
}
