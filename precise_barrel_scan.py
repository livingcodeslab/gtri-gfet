#!/usr/bin/env python3
"""
More precise scanning to find exact barrel extents.
Use smaller test radius and scan entire XZ grid at back face.
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

def find_all_ports_on_back_face(vertices):
    """
    Scan entire back face to find ALL port openings.
    """

    y_max = max(v[1] for v in vertices)

    # Get back face vertices
    back_face = [v for v in vertices if v[1] > y_max - 1]

    print(f"Back face vertices (Y > {y_max-1:.1f}): {len(back_face)}")

    # Grid scan with small test radius
    test_radius = 3.0

    ports = []

    for x in range(2, 27, 2):  # 2mm steps
        for z in range(2, 27, 2):
            center_verts = 0
            perimeter_verts = 0

            for v in back_face:
                dist = math.sqrt((v[0] - x)**2 + (v[2] - z)**2)

                if dist < test_radius * 0.5:
                    center_verts += 1
                elif test_radius * 0.8 < dist < test_radius * 1.5:
                    perimeter_verts += 1

            if center_verts < 10 and perimeter_verts > 40:
                ports.append({
                    'x': x,
                    'z': z,
                    'perimeter': perimeter_verts,
                    'center': center_verts
                })

    return ports

def scan_depth_at_position(vertices, x, z, test_radii=[2.0, 2.5, 3.0, 3.5]):
    """
    Scan depth profile at a specific X,Z position with multiple radii.
    """

    print(f"\n{'='*60}")
    print(f"Depth scan at X={x}, Z={z}")
    print('='*60)

    for test_radius in test_radii:
        print(f"\nTest radius: {test_radius}mm")

        # Scan from Y=28 (back face) going inward toward Y=0
        void_regions = []
        in_void = False
        void_start = None

        for y in range(28, -1, -1):  # Scan from back toward front
            center_verts = 0
            perimeter_verts = 0

            for v in vertices:
                if abs(v[1] - y) < 0.5:  # At this Y slice
                    dist_xz = math.sqrt((v[0] - x)**2 + (v[2] - z)**2)

                    if dist_xz < test_radius * 0.5:
                        center_verts += 1
                    elif test_radius * 0.8 < dist_xz < test_radius * 1.5:
                        perimeter_verts += 1

            is_void = center_verts < 5 and perimeter_verts > 15

            if is_void:
                if not in_void:
                    void_start = y
                    in_void = True
                    print(f"  Void starts at Y={y}mm")
            else:
                if in_void:
                    void_end = y + 1
                    depth = void_start - void_end
                    print(f"  Void ends at Y={void_end}mm (depth: {depth}mm)")
                    void_regions.append((void_start, void_end, depth))
                    in_void = False

        if in_void:
            print(f"  Void extends to Y=0mm (depth: {void_start}mm)")
            void_regions.append((void_start, 0, void_start))

def main():
    print("="*70)
    print("Precise Barrel Scanning")
    print("="*70)

    vertices = parse_binary_stl('CAD/gfet_adapter.STL')

    # First, find all ports on back face
    print("\n" + "="*70)
    print("STEP 1: Find all port openings on back face")
    print("="*70)

    ports = find_all_ports_on_back_face(vertices)

    ports.sort(key=lambda p: p['perimeter'], reverse=True)

    print(f"\nFound {len(ports)} potential ports:")
    for i, p in enumerate(ports[:5], 1):
        print(f"  #{i}: X={p['x']}, Z={p['z']}, perimeter={p['perimeter']} verts")

    # Scan depth at top 2 ports
    if len(ports) >= 2:
        print("\n" + "="*70)
        print("STEP 2: Scan depth profiles")
        print("="*70)

        scan_depth_at_position(vertices, ports[0]['x'], ports[0]['z'])
        scan_depth_at_position(vertices, ports[1]['x'], ports[1]['z'])

if __name__ == "__main__":
    main()
