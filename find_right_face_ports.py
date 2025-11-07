#!/usr/bin/env python3
"""
Find 2 HPLC ports on the RIGHT face (X≈27-28, high X values).
Looking for holes in the middle of that face.
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

def find_ports_on_right_face(facets):
    """Find 2 large holes on the right face (X≈27-28)."""

    all_verts = []
    for f in facets:
        all_verts.extend(f['vertices'])

    xs = [v[0] for v in all_verts]
    ys = [v[1] for v in all_verts]
    zs = [v[2] for v in all_verts]

    x_max = max(xs)
    y_middle = (min(ys) + max(ys)) / 2
    z_middle = (min(zs) + max(zs)) / 2

    print(f"Part: X[{min(xs):.1f}, {x_max:.1f}]  Y[{min(ys):.1f}, {max(ys):.1f}]  Z[{min(zs):.1f}, {max(zs):.1f}]")
    print(f"Middle: Y={y_middle:.1f}, Z={z_middle:.1f}")
    print()
    print(f"Searching RIGHT face (X > 24mm) for 2 large holes...")
    print("="*70)

    # Get all vertices on the right face
    right_face_verts = [v for v in all_verts if v[0] > 24]

    print(f"Found {len(right_face_verts)} vertices on right face (X > 24)")

    # On the right face, holes would appear as circles in the YZ plane
    # Group by Y and Z to find circular patterns

    # Try many potential centers in YZ plane
    y_min_face = min(v[1] for v in right_face_verts)
    y_max_face = max(v[1] for v in right_face_verts)
    z_min_face = min(v[2] for v in right_face_verts)
    z_max_face = max(v[2] for v in right_face_verts)

    print(f"Right face spans: Y[{y_min_face:.1f}, {y_max_face:.1f}]  Z[{z_min_face:.1f}, {z_max_face:.1f}]")
    print()

    holes = []

    # Grid search for hole centers
    for cy in range(int(y_min_face), int(y_max_face)+1, 1):  # 1mm steps
        for cz in range(int(z_min_face), int(z_max_face)+1, 1):

            # For this center, find vertices at various radii
            radial_data = defaultdict(list)

            for v in right_face_verts:
                r = math.sqrt((v[1] - cy)**2 + (v[2] - cz)**2)

                if 3 < r < 15:  # Reasonable hole size
                    r_key = round(r * 2) / 2  # 0.5mm buckets
                    radial_data[r_key].append(v)

            # Check each radius for significant vertex count
            for radius, verts in radial_data.items():
                if len(verts) > 40:  # Strong circular feature

                    # Check X-depth (how far into the part)
                    x_coords = [v[0] for v in verts]
                    x_depth = max(x_coords) - min(x_coords)

                    if x_depth > 3:  # Goes at least 3mm into part

                        # Refine center
                        refined_cy = sum(v[1] for v in verts) / len(verts)
                        refined_cz = sum(v[2] for v in verts) / len(verts)

                        holes.append({
                            'y': refined_cy,
                            'z': refined_cz,
                            'x_max': max(x_coords),
                            'x_min': min(x_coords),
                            'radius': radius,
                            'diameter': radius * 2,
                            'depth': x_depth,
                            'num_verts': len(verts)
                        })

    # Merge duplicates
    unique_holes = []

    for h in sorted(holes, key=lambda x: x['num_verts'], reverse=True):
        merged = False

        for uh in unique_holes:
            dist = math.sqrt((h['y'] - uh['y'])**2 + (h['z'] - uh['z'])**2)

            if dist < 3:  # Same hole
                uh['num_verts'] += h['num_verts']
                if h['diameter'] > uh['diameter']:
                    uh['diameter'] = h['diameter']
                    uh['radius'] = h['radius']
                merged = True
                break

        if not merged:
            unique_holes.append(h)

    return unique_holes, y_middle, z_middle

def main():
    print("="*70)
    print("Finding 2 HPLC Ports on RIGHT Face (High X)")
    print("="*70)
    print()

    facets = parse_binary_stl('CAD/gfet_adapter.STL')

    holes, y_mid, z_mid = find_ports_on_right_face(facets)

    print(f"\nFound {len(holes)} holes on right face")

    if holes:
        print("\nAll holes sorted by diameter:")
        print("="*70)

        sorted_holes = sorted(holes, key=lambda h: h['diameter'], reverse=True)

        for i, h in enumerate(sorted_holes, 1):
            print(f"\n#{i}: Ø{h['diameter']:.1f}mm")
            print(f"    Position (Y, Z): ({h['y']:.2f}, {h['z']:.2f})")
            print(f"    X-range: {h['x_min']:.2f} to {h['x_max']:.2f} ({h['depth']:.1f}mm deep)")
            print(f"    Distance from middle: Y±{abs(h['y'] - y_mid):.1f}, Z±{abs(h['z'] - z_mid):.1f}")
            print(f"    Confidence: {h['num_verts']} vertices")

        if len(sorted_holes) >= 2:
            print("\n" + "="*70)
            print("THE 2 LARGEST HOLES (LIKELY HPLC PORTS):")
            print("="*70)

            for i, port in enumerate(sorted_holes[:2], 1):
                print(f"\nPort #{i}:")
                print(f"  Position: X={port['x_max']:.2f}, Y={port['y']:.2f}, Z={port['z']:.2f}")
                print(f"  Diameter: {port['diameter']:.1f}mm")
                print(f"  Depth into part: {port['depth']:.1f}mm")

            dist = math.sqrt((sorted_holes[0]['y'] - sorted_holes[1]['y'])**2 +
                           (sorted_holes[0]['z'] - sorted_holes[1]['z'])**2)
            print(f"\nDistance between ports: {dist:.2f}mm")

            print("\n" + "="*70)
            print("OpenSCAD Positions:")
            print("="*70)
            print("\n// HPLC ports on right face")
            print("// Connectors point in -X direction (into part)")
            print("hplc_ports = [")
            for port in sorted_holes[:2]:
                print(f"  [{port['x_max']:.2f}, {port['y']:.2f}, {port['z']:.2f}, {port['depth']:.2f}],  // Ø{port['diameter']:.0f}mm")
            print("];")

            print("\n✓ Found the 2 HPLC ports on the right face!")

    else:
        print("\n! No holes found")

if __name__ == "__main__":
    main()
