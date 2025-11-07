#!/usr/bin/env python3
"""
Improved hole detection using edge analysis.
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

def find_vertical_cylinders(facets):
    """
    Find cylindrical holes by looking for vertices with consistent radial distance
    from various center points.
    """

    all_verts = []
    for f in facets:
        all_verts.extend(f['vertices'])

    # Get rough center of part
    part_cx = sum(v[0] for v in all_verts) / len(all_verts)
    part_cy = sum(v[1] for v in all_verts) / len(all_verts)

    print(f"Part center estimate: ({part_cx:.2f}, {part_cy:.2f})")

    # Look for concentrations of vertices at specific radii from part center
    # Group vertices by (radius from center, Z-height)

    radial_analysis = defaultdict(lambda: {'z_levels': set(), 'positions': []})

    for v in all_verts:
        dx = v[0] - part_cx
        dy = v[1] - part_cy
        r = math.sqrt(dx**2 + dy**2)
        r_bucket = round(r * 2) / 2  # 0.5mm buckets

        if 2 < r < 12:  # Reasonable hole radii range
            z_bucket = round(v[2])
            radial_analysis[r_bucket]['z_levels'].add(z_bucket)
            radial_analysis[r_bucket]['positions'].append(v)

    # Find radii that span multiple Z levels (potential holes)
    print("\nRadial features analysis:")
    print(f"{'Radius (mm)':<15} {'Z-span (mm)':<15} {'# Z-levels':<15} {'# Vertices'}")
    print("-" * 65)

    hole_candidates = []

    for r, data in sorted(radial_analysis.items()):
        z_levels = sorted(data['z_levels'])
        if len(z_levels) > 3:  # Spans multiple Z levels
            z_span = max(z_levels) - min(z_levels)
            num_verts = len(data['positions'])

            print(f"{r:<15.2f} {z_span:<15.1f} {len(z_levels):<15} {num_verts}")

            if z_span > 5 and num_verts > 100:  # Significant feature
                # Calculate average center position
                positions = data['positions']
                avg_x = sum(p[0] for p in positions) / len(positions)
                avg_y = sum(p[1] for p in positions) / len(positions)
                avg_z_min = min(p[2] for p in positions)
                avg_z_max = max(p[2] for p in positions)

                # The hole center is at this XY position
                hole_candidates.append({
                    'center_x': avg_x,
                    'center_y': avg_y,
                    'z_min': avg_z_min,
                    'z_max': avg_z_max,
                    'depth': avg_z_max - avg_z_min,
                    'radius': r,
                    'diameter': r * 2,
                    'confidence': num_verts
                })

    return hole_candidates

def cluster_holes(holes, distance_threshold=3):
    """Merge holes that are at similar positions (likely same hole)."""
    if not holes:
        return []

    clustered = []

    for hole in sorted(holes, key=lambda h: h['confidence'], reverse=True):
        merged = False

        for cluster in clustered:
            dist = math.sqrt((hole['center_x'] - cluster['center_x'])**2 +
                           (hole['center_y'] - cluster['center_y'])**2)

            if dist < distance_threshold:
                # Merge into existing cluster (keep better estimate)
                if hole['confidence'] > cluster['confidence']:
                    cluster.update(hole)
                merged = True
                break

        if not merged:
            clustered.append(hole.copy())

    return clustered

def main():
    print("Advanced Hole Detection for gfet_adapter.STL")
    print("="*65)

    facets = parse_binary_stl('CAD/gfet_adapter.STL')
    print(f"Loaded {len(facets)} facets\n")

    holes = find_vertical_cylinders(facets)
    unique_holes = cluster_holes(holes)

    print(f"\n{'='*65}")
    print(f"DETECTED {len(unique_holes)} UNIQUE HOLE(S):")
    print("="*65)

    for i, h in enumerate(sorted(unique_holes, key=lambda x: x['confidence'], reverse=True), 1):
        print(f"\nHole #{i}:")
        print(f"  Center (X, Y): ({h['center_x']:.2f}, {h['center_y']:.2f})")
        print(f"  Z range: {h['z_min']:.2f} to {h['z_max']:.2f} mm")
        print(f"  Depth: {h['depth']:.2f} mm")
        print(f"  Current diameter: {h['diameter']:.2f} mm")

        # Check if it matches 1/4-28 tap drill
        if 5.0 < h['diameter'] < 6.0:
            print(f"  ✓ Matches 1/4-28 UNF tap drill size!")
            print(f"    → Will add 6.35mm (0.25\") threaded hole")
        elif h['diameter'] < 5.0:
            print(f"  ⚠ Smaller than expected for 1/4-28")
        else:
            print(f"  ⚠ Larger than expected for 1/4-28")

    # Output for OpenSCAD
    if unique_holes:
        print(f"\n{'='*65}")
        print("OpenSCAD code for threaded adapter:")
        print("="*65)
        print("\n// Hole definitions: [x, y, z_start, depth, target_diameter]")
        print("holes = [")
        for h in unique_holes:
            print(f"  [{h['center_x']:.3f}, {h['center_y']:.3f}, {h['z_min']:.3f}, {h['depth']:.3f}, 6.35],  // 1/4-28 UNF")
        print("];")
        print()

        # Save to file for OpenSCAD
        with open('hole_positions.txt', 'w') as f:
            f.write("// Auto-detected hole positions\n")
            f.write("holes = [\n")
            for h in unique_holes:
                f.write(f"  [{h['center_x']:.3f}, {h['center_y']:.3f}, {h['z_min']:.3f}, {h['depth']:.3f}, 6.35],\n")
            f.write("];\n")
        print("✓ Saved hole positions to hole_positions.txt")

if __name__ == "__main__":
    main()
