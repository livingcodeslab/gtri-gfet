#!/usr/bin/env python3
"""
Find the actual port OPENING diameter (where threads should be cut),
not the internal channel diameter.
"""

import struct
import math
import numpy as np

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

def analyze_port_opening(vertices, center_x, center_z, port_name):
    """
    Find vertices on the BACK FACE (Y ≈ 28) near the port.
    These represent the port opening diameter.
    """

    y_max = max(v[1] for v in vertices)

    # Get vertices ON the back face (not inside the barrel)
    back_face_verts = [v for v in vertices if v[1] > y_max - 0.5]

    print(f"\n{port_name} at X={center_x}, Z={center_z}")
    print(f"Analyzing back face vertices (Y > {y_max-0.5:.1f})")

    # Find vertices near this port on back face
    nearby = []
    for v in back_face_verts:
        dist_xz = math.sqrt((v[0] - center_x)**2 + (v[2] - center_z)**2)
        if dist_xz < 5.0:
            nearby.append((v, dist_xz))

    if len(nearby) < 20:
        print(f"  Too few vertices ({len(nearby)})")
        return None

    print(f"  Found {len(nearby)} vertices within 5mm on back face")

    # Analyze radial distribution
    radii = sorted([dist for v, dist in nearby])

    print(f"  Radial distribution:")
    print(f"    Min: {radii[0]:.2f}mm")
    print(f"    10th percentile: {radii[len(radii)//10]:.2f}mm")
    print(f"    25th percentile: {radii[len(radii)//4]:.2f}mm")
    print(f"    50th percentile (median): {radii[len(radii)//2]:.2f}mm")
    print(f"    75th percentile: {radii[3*len(radii)//4]:.2f}mm")
    print(f"    Max: {radii[-1]:.2f}mm")

    # The port opening is likely around the 75th percentile
    # (some vertices are inside, some at the rim, some outside)
    opening_radius = radii[3*len(radii)//4]
    opening_diameter = opening_radius * 2

    print(f"\n  Estimated opening diameter: {opening_diameter:.2f}mm")
    print(f"  Estimated opening radius: {opening_radius:.2f}mm")

    return {
        'diameter': opening_diameter,
        'radius': opening_radius,
        'center': (center_x, center_z)
    }

def main():
    print("="*70)
    print("Port Opening Diameter Detection")
    print("="*70)

    vertices = parse_binary_stl('CAD/gfet_adapter.STL')

    port1 = analyze_port_opening(vertices, center_x=8, center_z=9, port_name="Port 1 (lower)")
    port2 = analyze_port_opening(vertices, center_x=8, center_z=19, port_name="Port 2 (upper)")

    print("\n" + "="*70)
    print("THREAD COMPATIBILITY CHECK:")
    print("="*70)

    # Standard HPLC thread specs
    thread_specs = {
        "10-32 UNF": {"major": 4.826, "minor": 4.0},
        "1/4-28 UNF": {"major": 6.35, "minor": 5.49},
        "M6x1.0": {"major": 6.0, "minor": 5.0}
    }

    if port1:
        print(f"\nPort 1 opening: {port1['diameter']:.2f}mm diameter")
        for thread_name, specs in thread_specs.items():
            fits = port1['diameter'] >= specs['minor']
            status = "✓ FITS" if fits else "✗ TOO SMALL"
            print(f"  {thread_name} (minor ø{specs['minor']}mm): {status}")

    if port2:
        print(f"\nPort 2 opening: {port2['diameter']:.2f}mm diameter")
        for thread_name, specs in thread_specs.items():
            fits = port2['diameter'] >= specs['minor']
            status = "✓ FITS" if fits else "✗ TOO SMALL"
            print(f"  {thread_name} (minor ø{specs['minor']}mm): {status}")

if __name__ == "__main__":
    main()
