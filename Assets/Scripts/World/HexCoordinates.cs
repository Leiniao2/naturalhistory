using System;
using UnityEngine;

namespace NaturalHistory.World
{
    // Cube coordinates: q + r + s == 0 always
    [Serializable]
    public struct HexCoordinates : IEquatable<HexCoordinates>
    {
        public int Q { get; private set; }
        public int R { get; private set; }
        public int S => -Q - R;

        public HexCoordinates(int q, int r) { Q = q; R = r; }

        public static HexCoordinates FromOffsetCoordinates(int col, int row)
        {
            int q = col - (row - (row & 1)) / 2;
            return new HexCoordinates(q, row);
        }

        // Inverse of FromOffsetCoordinates (odd rows shifted right)
        public (int col, int row) ToOffsetCoordinates() => (Q + (R - (R & 1)) / 2, R);

        public static HexCoordinates operator +(HexCoordinates a, HexCoordinates b)
            => new(a.Q + b.Q, a.R + b.R);

        public int DistanceTo(HexCoordinates other)
        {
            return (Math.Abs(Q - other.Q) + Math.Abs(R - other.R) + Math.Abs(S - other.S)) / 2;
        }

        public static readonly HexCoordinates[] Directions =
        {
            new( 1,  0), new( 1, -1), new( 0, -1),
            new(-1,  0), new(-1,  1), new( 0,  1)
        };

        public HexCoordinates Neighbor(int direction) => this + Directions[direction % 6];

        public Vector3 ToWorldPosition(float size = 1f)
        {
            float x = size * (Mathf.Sqrt(3f) * Q + Mathf.Sqrt(3f) / 2f * R);
            float z = size * (3f / 2f * R);
            return new Vector3(x, 0f, z);
        }

        public bool Equals(HexCoordinates other) => Q == other.Q && R == other.R;
        public override bool Equals(object obj) => obj is HexCoordinates h && Equals(h);
        public override int GetHashCode() => HashCode.Combine(Q, R);
        public override string ToString() => $"({Q}, {R}, {S})";
    }
}
