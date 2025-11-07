#!/usr/bin/env python3
"""
Sphere-sweep hole detection.
Look for circular voids on the top face where a sphere of expected radius fits.
"""

import struct
import math
from collections import defaultdict

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

def find_circular_voids_on_top(vertices, test_radius=3.0):
    """
    Sphere-sweep: test if a sphere of given radius can fit at various XY positions.
    Holes will have vertices AROUND the perimeter but EMPTY in the center.
    """

    z_max = max(v[2] for v in vertices)

    # Only look at top face
    top_verts = [v for v in vertices if v[2] > z_max - 5]

    print(f"Top face (Z > {z_max-5:.1f}): {len(top_verts)} vertices")
    print(f"Testing for circular voids with test radius = {test_radius:.1f}mm")
    print()

    # Grid search for potential hole centers
    x_coords = [v[0] for v in top_verts]
    y_coords = [v[1] for v in top_verts]

    x_min, x_max = min(x_coords), max(x_coords)
    y_min, y_max = min(y_coords), max(y_coords)

    holes_found = []

    # Test grid of positions
    for cx in range(int(x_min) + 1, int(x_max), 1):  # 1mm steps
        for cy in range(int(y_min) + 1, int(y_max), 1):

            # Count vertices in center (should be LOW for a hole)
            center_verts = 0
            # Count vertices at perimeter (should be HIGH for a hole)
            perimeter_verts = 0

            for v in top_verts:
                dist = math.sqrt((v[0] - cx)**2 + (v[1] - cy)**2)

                if dist < test_radius * 0.5:  # Inside center
                    center_verts += 1
                elif test_radius * 0.8 < dist < test_radius * 1.5:  # At perimeter
                    perimeter_verts += 1

            # Hole signature: few center vertices, many perimeter vertices
            if center_verts < 10 and perimeter_verts > 50:
                holes_found.append({
                    'x': cx,
                    'y': cy,
                    'center_count': center_verts,
                    'perimeter_count': perimeter_verts,
                    'ratio': perimeter_verts / max(center_verts, 1)
                })

    return holes_found

def main():
    print("="*70)
    print("Sphere-Sweep Hole Detection")
    print("="*70)
    print()

    vertices = parse_binary_stl('CAD/gfet_adapter.STL')

    # Try different test radii (hole sizes)
    test_radii = [3.0, 4.0, 5.0, 6.0]  # Expected hole radii

    all_detections = {}

    for radius in test_radii:
        print(f"\n{'='*70}")
        print(f"Testing with sphere radius = {radius}mm (diameter ~{radius*2}mm)")
        print("="*70)

        holes = find_circular_voids_on_top(vertices, test_radius=radius)

        if holes:
            print(f"Found {len(holes)} potential holes")

            # Sort by perimeter count (confidence)
            holes.sort(key=lambda h: h['perimeter_count'], reverse=True)

            for i, h in enumerate(holes[:5], 1):  # Top 5
                print(f"\n  #{i}: ({h['x']}, {h['y']})")
                print(f"       Center: {h['center_count']} verts, Perimeter: {h['perimeter_count']} verts")
                print(f"       Ratio: {h['ratio']:.1f}x")

            all_detections[radius] = holes
        else:
            print("  No holes detected at this radius")

    # Find best candidates across all radii
    print("\n" + "="*70)
    print("BEST HOLE CANDIDATES:")
    print("="*70)

    best_holes = []
    for radius, holes in all_detections.items():
        for h in holes[:3]:  # Top 3 from each radius
            # Check if already found
            is_dup = False
            for bh in best_holes:
                dist = math.sqrt((h['x'] - bh['x'])**2 + (h['y'] - bh['y'])**2)
                if dist < 3:
                    is_dup = True
                    break

            if not is_dup:
                h['test_radius'] = radius
                best_holes.append(h)

    best_holes.sort(key=lambda h: h['perimeter_count'], reverse=True)

    for i, h in enumerate(best_holes[:5], 1):
        print(f"\n#{i}: Position ({h['x']}, {h['y']})")
        print(f"    Detected at test radius: {h['test_radius']}mm")
        print(f"    Confidence: {h['perimeter_count']} perimeter vertices")

    if len(best_holes) >= 2:
        print("\n" + "="*70)
        print("TOP 2 HOLES (FOR OPENSCAD):")
        print("="*70)
        print("\nport_1 = [", best_holes[0]['x'], ",", best_holes[0]['y'], ", 28];")
        print("port_2 = [", best_holes[1]['x'], ",", best_holes[1]['y'], ", 28];")

if __name__ == "__main__":
    main()
