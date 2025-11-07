#!/usr/bin/env python3
"""
Detect barrel geometry: find the cylindrical axis, not just the opening.
Analyze vertex clustering along potential cylinder axes.
"""

import struct
import math
import numpy as np
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

def analyze_barrel(vertices, center_x, center_z, axis='y'):
    """
    Analyze vertices near (center_x, center_z) to find barrel geometry.
    For a horizontal barrel along Y-axis, vertices should:
    - Be distributed along Y (the barrel length)
    - Form circles in the XZ plane at each Y position
    """

    # Get vertices near the expected barrel location
    radius_search = 5.0  # Search within 5mm radius

    if axis == 'y':
        nearby = []
        for v in vertices:
            # Distance in XZ plane from center
            dist_xz = math.sqrt((v[0] - center_x)**2 + (v[2] - center_z)**2)
            if dist_xz < radius_search:
                nearby.append(v)

    if len(nearby) < 100:
        return None

    print(f"\nAnalyzing barrel at X={center_x}, Z={center_z}")
    print(f"Found {len(nearby)} vertices within {radius_search}mm radius")

    # Analyze distribution along Y axis
    y_coords = sorted([v[1] for v in nearby])
    y_min, y_max = min(y_coords), max(y_coords)
    print(f"Y range: [{y_min:.1f}, {y_max:.1f}] (length: {y_max-y_min:.1f}mm)")

    # Sample cross-sections along Y axis
    print("\nCross-section analysis:")
    for y in range(int(y_min), int(y_max)+1, 2):
        slice_verts = [v for v in nearby if y <= v[1] < y+2]
        if len(slice_verts) > 5:
            # Measure radius at this Y position
            radii = [math.sqrt((v[0]-center_x)**2 + (v[2]-center_z)**2) for v in slice_verts]
            avg_radius = sum(radii) / len(radii)
            min_radius = min(radii)
            max_radius = max(radii)
            print(f"  Y={y:2d}-{y+2:2d}mm: {len(slice_verts):3d} verts, "
                  f"radius: {avg_radius:.1f}mm (range {min_radius:.1f}-{max_radius:.1f}mm)")

    # Estimate barrel parameters
    # Find the section with smallest inner radius (the actual bore)
    best_y = None
    best_inner_radius = None

    for y in range(int(y_min), int(y_max)+1, 1):
        slice_verts = [v for v in nearby if y <= v[1] < y+1]
        if len(slice_verts) > 10:
            radii = [math.sqrt((v[0]-center_x)**2 + (v[2]-center_z)**2) for v in slice_verts]
            # Look for inner edge (minimum distance with some vertices)
            radii_sorted = sorted(radii)
            if len(radii_sorted) > 5:
                inner_radius = radii_sorted[5]  # 5th smallest
                if best_inner_radius is None or inner_radius < best_inner_radius:
                    best_inner_radius = inner_radius
                    best_y = y

    if best_inner_radius:
        print(f"\nEstimated bore:")
        print(f"  Center: X={center_x}, Z={center_z}")
        print(f"  Inner radius: {best_inner_radius:.2f}mm (diameter {best_inner_radius*2:.2f}mm)")
        print(f"  Best cross-section at Y={best_y}mm")
        print(f"  Y extent: {y_min:.1f} to {y_max:.1f}mm")

        return {
            'center': (center_x, center_z),
            'inner_radius': best_inner_radius,
            'y_min': y_min,
            'y_max': y_max,
            'axis': 'y',
            'direction': [0, 1, 0]  # Points in +Y direction
        }

    return None

def main():
    print("="*70)
    print("Barrel Geometry Detection")
    print("="*70)

    vertices = parse_binary_stl('CAD/gfet_adapter.STL')

    # From sphere-sweep, we found ports at:
    # Port 1: X=8, Z=9 (lower)
    # Port 2: X=8, Z=19 (upper)

    port_1_barrel = analyze_barrel(vertices, center_x=8, center_z=9, axis='y')
    port_2_barrel = analyze_barrel(vertices, center_x=8, center_z=19, axis='y')

    print("\n" + "="*70)
    print("SUMMARY:")
    print("="*70)

    if port_1_barrel:
        print(f"\nPort 1 (lower): X={port_1_barrel['center'][0]}, Z={port_1_barrel['center'][1]}")
        print(f"  Bore diameter: {port_1_barrel['inner_radius']*2:.2f}mm")
        print(f"  Y range: [{port_1_barrel['y_min']:.1f}, {port_1_barrel['y_max']:.1f}]")
        print(f"  Axis direction: {port_1_barrel['direction']}")

    if port_2_barrel:
        print(f"\nPort 2 (upper): X={port_2_barrel['center'][0]}, Z={port_2_barrel['center'][1]}")
        print(f"  Bore diameter: {port_2_barrel['inner_radius']*2:.2f}mm")
        print(f"  Y range: [{port_2_barrel['y_min']:.1f}, {port_2_barrel['y_max']:.1f}]")
        print(f"  Axis direction: {port_2_barrel['direction']}")

if __name__ == "__main__":
    main()
