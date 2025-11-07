#!/usr/bin/env python3
"""
Find the exact positions and dimensions of cylindrical holes in the STL.
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
            facets.append({'normal': list(normal), 'vertices': [list(v1), list(v2), list(v3)]})
    return facets

def find_holes(facets):
    """Find cylindrical holes by analyzing vertex clustering."""
    all_verts = []
    for f in facets:
        all_verts.extend(f['vertices'])

    # Find bounding box and center
    xs = [v[0] for v in all_verts]
    ys = [v[1] for v in all_verts]
    zs = [v[2] for v in all_verts]

    print(f"Part dimensions:")
    print(f"  X: {min(xs):.2f} to {max(xs):.2f}")
    print(f"  Y: {min(ys):.2f} to {max(ys):.2f}")
    print(f"  Z: {min(zs):.2f} to {max(zs):.2f}")

    # Analyze vertices in cylindrical coordinates
    # For HPLC adapters, holes typically go through vertically (Z-axis)

    # Group vertices by XY position to find hole centers
    xy_clusters = defaultdict(list)

    for v in all_verts:
        x_key = round(v[0] * 2) / 2  # 0.5mm grid
        y_key = round(v[1] * 2) / 2
        xy_clusters[(x_key, y_key)].append(v)

    # Find clusters that span significant Z range (through-holes)
    hole_candidates = []

    for (x, y), verts in xy_clusters.items():
        if len(verts) > 50:  # Significant number of vertices
            z_min = min(v[2] for v in verts)
            z_max = max(v[2] for v in verts)
            z_span = z_max - z_min

            if z_span > 5:  # Hole goes through at least 5mm
                # Calculate radius variation at this XY position
                radii = []
                for v in verts:
                    r = math.sqrt((v[0] - x)**2 + (v[1] - y)**2)
                    radii.append(r)

                avg_r = sum(radii) / len(radii)

                if 2 < avg_r < 6:  # HPLC fitting size range
                    hole_candidates.append({
                        'center_x': x,
                        'center_y': y,
                        'z_min': z_min,
                        'z_max': z_max,
                        'depth': z_span,
                        'radius': avg_r,
                        'diameter': avg_r * 2,
                        'num_verts': len(verts)
                    })

    # Remove duplicates (merge nearby centers)
    unique_holes = []
    for h in hole_candidates:
        is_duplicate = False
        for uh in unique_holes:
            dist = math.sqrt((h['center_x'] - uh['center_x'])**2 +
                           (h['center_y'] - uh['center_y'])**2)
            if dist < 2:  # Same hole
                is_duplicate = True
                # Keep the one with more vertices (better data)
                if h['num_verts'] > uh['num_verts']:
                    unique_holes.remove(uh)
                    unique_holes.append(h)
                break

        if not is_duplicate:
            unique_holes.append(h)

    return sorted(unique_holes, key=lambda h: h['num_verts'], reverse=True)

def main():
    print("Analyzing gfet_adapter.STL for hole positions...")
    print("="*60)

    facets = parse_binary_stl('CAD/gfet_adapter.STL')
    print(f"\nLoaded {len(facets)} facets\n")

    holes = find_holes(facets)

    print(f"\n{'='*60}")
    print(f"FOUND {len(holes)} HOLE(S):")
    print("="*60)

    for i, h in enumerate(holes, 1):
        print(f"\nHole #{i}:")
        print(f"  Position (X, Y): ({h['center_x']:.2f}, {h['center_y']:.2f})")
        print(f"  Z range: {h['z_min']:.2f} to {h['z_max']:.2f}")
        print(f"  Depth: {h['depth']:.2f} mm")
        print(f"  Radius: {h['radius']:.2f} mm")
        print(f"  Diameter: {h['diameter']:.2f} mm")
        print(f"  Confidence: {h['num_verts']} vertices")

        # Suggest tap drill size
        if 4.5 < h['diameter'] < 6.5:
            print(f"  → Matches 1/4-28 UNF tap drill size (~5.5mm)")
            print(f"     Major diameter after tapping: ~6.35mm (0.25\")")

    # Generate OpenSCAD code snippet
    print(f"\n{'='*60}")
    print("OpenSCAD hole positions (for threaded version):")
    print("="*60)
    print("\n// Hole positions [x, y, z_start, depth, diameter]")
    print("holes = [")
    for h in holes:
        print(f"  [{h['center_x']:.2f}, {h['center_y']:.2f}, {h['z_min']:.2f}, {h['depth']:.2f}, {h['diameter']:.2f}],")
    print("];")
    print()

if __name__ == "__main__":
    main()
