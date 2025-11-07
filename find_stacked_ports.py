#!/usr/bin/env python3
"""
Sphere-sweep on back face to find horizontally-oriented ports at X=8 and X=18.
Ports should be stacked vertically at different Z heights.
"""

import struct
import math

def parse_binary_stl(filename):
    facets = []
    with open(filename, 'rb') as f:
        f.read(80)
        num_triangles = struct.unpack('<I', f.read(4))[0]
        for _ in range(num_triangles):
            normal = struct.unpack('<fff', f.read(12))
            v1 = struct.unpack('<fff', f.read(12))
            v2 = struct.unpack('<fff', f.read(12))
            v3 = struct.unpack('<fff', f.read(12))
            f.read(2)
            facets.extend([v1, v2, v3])
    return facets

def find_circular_voids_on_back_face(vertices, test_radius=3.0):
    """
    Sphere-sweep on back face (Y-max) looking for circular voids.
    Returns positions in (X, Z) coordinates on the back face.
    """

    y_max = max(v[1] for v in vertices)

    # Back face vertices (Y near max)
    back_verts = [v for v in vertices if v[1] > y_max - 2]

    print(f"Back face (Y > {y_max-2:.1f}): {len(back_verts)} vertices")
    print(f"Testing for circular voids with radius = {test_radius:.1f}mm")
    print()

    # Extract X,Z coordinates from back face
    xz_coords = [(v[0], v[2]) for v in back_verts]

    x_coords = [xz[0] for xz in xz_coords]
    z_coords = [xz[1] for xz in xz_coords]

    x_min, x_max = min(x_coords), max(x_coords)
    z_min, z_max = min(z_coords), max(z_coords)

    holes_found = []

    # Grid search on X,Z plane of back face
    for cx in range(int(x_min) + 1, int(x_max), 1):  # 1mm steps
        for cz in range(int(z_min) + 1, int(z_max), 1):

            center_verts = 0
            perimeter_verts = 0

            for (vx, vz) in xz_coords:
                dist = math.sqrt((vx - cx)**2 + (vz - cz)**2)

                if dist < test_radius * 0.5:  # Inside center
                    center_verts += 1
                elif test_radius * 0.8 < dist < test_radius * 1.5:  # At perimeter
                    perimeter_verts += 1

            # Hole signature: few center vertices, many perimeter vertices
            if center_verts < 10 and perimeter_verts > 40:
                holes_found.append({
                    'x': cx,
                    'z': cz,
                    'center_count': center_verts,
                    'perimeter_count': perimeter_verts,
                    'ratio': perimeter_verts / max(center_verts, 1)
                })

    return holes_found, y_max

def main():
    print("="*70)
    print("Sphere-Sweep on Back Face for Horizontal Ports")
    print("="*70)
    print()

    vertices = parse_binary_stl('CAD/gfet_adapter.STL')

    # Try different radii
    test_radii = [2.5, 3.0, 3.5, 4.0]

    all_detections = {}

    for radius in test_radii:
        print(f"{'='*70}")
        print(f"Testing with sphere radius = {radius}mm")
        print("="*70)

        holes, y_max = find_circular_voids_on_back_face(vertices, test_radius=radius)

        if holes:
            print(f"Found {len(holes)} potential holes")

            holes.sort(key=lambda h: h['perimeter_count'], reverse=True)

            for i, h in enumerate(holes[:8], 1):  # Top 8
                print(f"\n  #{i}: X={h['x']}, Z={h['z']} on back face (Y≈{y_max:.1f})")
                print(f"       Center: {h['center_count']} verts, Perimeter: {h['perimeter_count']} verts")
                print(f"       Ratio: {h['ratio']:.1f}x")

            all_detections[radius] = holes
        else:
            print("  No holes detected\n")

        print()

    # Find best candidates at X=8 and X=18
    print("="*70)
    print("PORTS AT X=8 and X=18:")
    print("="*70)

    for target_x in [8, 18]:
        print(f"\nAt X={target_x}:")
        for radius, holes in all_detections.items():
            at_x = [h for h in holes if h['x'] == target_x]
            if at_x:
                at_x.sort(key=lambda h: h['z'])
                print(f"  Radius {radius}mm:")
                for h in at_x:
                    print(f"    Z={h['z']}, perimeter={h['perimeter_count']} verts")

if __name__ == "__main__":
    main()
