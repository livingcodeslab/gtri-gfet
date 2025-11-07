#!/usr/bin/env python3
"""
Helical Pattern Detector
Specifically looks for spiral/helical vertex patterns that indicate threads.
"""

import sys
import struct
import math
from collections import defaultdict

def parse_binary_stl(filename):
    """Parse binary STL file."""
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
            facets.append({
                'normal': list(normal),
                'vertices': [list(v1), list(v2), list(v3)]
            })
    return facets

def find_cylinder_axis(facets):
    """Find the main cylindrical features and their axes."""
    all_verts = []
    for f in facets:
        all_verts.extend(f['vertices'])

    # Bounding box center as initial guess
    cx = sum(v[0] for v in all_verts) / len(all_verts)
    cy = sum(v[1] for v in all_verts) / len(all_verts)

    return cx, cy

def detect_helical_pattern(facets, cx, cy, radius_range=(2, 8)):
    """
    Detect helical patterns by looking for vertices that:
    1. Are at a consistent radius from center axis
    2. Follow a spiral path (angle changes with Z)
    3. Have regular pitch (Z advancement per rotation)
    """

    print(f"\nSearching for helical patterns around axis ({cx:.2f}, {cy:.2f})")
    print(f"Looking at radius range: {radius_range[0]}-{radius_range[1]}mm")
    print("="*60)

    # Extract all vertices with their cylindrical coordinates
    cylindrical_verts = []
    for f in facets:
        for v in f['vertices']:
            dx = v[0] - cx
            dy = v[1] - cy
            r = math.sqrt(dx**2 + dy**2)
            theta = math.atan2(dy, dx)  # Angle in radians
            z = v[2]

            if radius_range[0] <= r <= radius_range[1]:
                cylindrical_verts.append({
                    'x': v[0], 'y': v[1], 'z': z,
                    'r': r, 'theta': theta
                })

    if not cylindrical_verts:
        print(f"No vertices found in radius range {radius_range}")
        return None

    print(f"Found {len(cylindrical_verts)} vertices in radius range")

    # Group by Z-height and check if angle varies systematically with Z
    z_angle_data = defaultdict(list)
    for v in cylindrical_verts:
        z_bucket = round(v['z'] * 5) / 5  # 0.2mm buckets
        z_angle_data[z_bucket].append((v['theta'], v['r']))

    # Check for helical pattern: angle should correlate with Z
    z_sorted = sorted(z_angle_data.keys())

    if len(z_sorted) < 5:
        print("Insufficient Z-levels for helix detection")
        return None

    print(f"\nAnalyzing {len(z_sorted)} Z-levels for helical progression...")

    # For each Z level, find the dominant angle
    z_angle_progression = []
    for z in z_sorted:
        angles = [theta for theta, r in z_angle_data[z]]
        if len(angles) > 3:
            # Look for multiple angles at this Z (indicates vertex spread around cylinder)
            avg_angle = sum(angles) / len(angles)
            angle_spread = max(angles) - min(angles)
            avg_radius = sum(r for theta, r in z_angle_data[z]) / len(z_angle_data[z])

            z_angle_progression.append({
                'z': z,
                'avg_angle': avg_angle,
                'angle_spread': angle_spread,
                'num_verts': len(angles),
                'avg_radius': avg_radius
            })

    # Analyze angle progression
    if len(z_angle_progression) < 5:
        print("Insufficient data for helix detection")
        return None

    print("\nZ vs Angle analysis:")
    print(f"{'Z (mm)':<10} {'Avg Angle (rad)':<18} {'Angle Spread':<15} {'Vertices':<10} {'Radius (mm)'}")
    print("-"*75)

    for i, data in enumerate(z_angle_progression[::max(1, len(z_angle_progression)//10)]):
        print(f"{data['z']:<10.2f} {data['avg_angle']:<18.3f} {data['angle_spread']:<15.3f} {data['num_verts']:<10} {data['avg_radius']:.2f}")

    # Check if angles form a progression (helix indicator)
    # For a helix: theta = (z - z0) / pitch * 2*pi + theta0
    # So d(theta)/d(z) should be roughly constant

    angle_z_derivatives = []
    for i in range(len(z_angle_progression) - 1):
        z1 = z_angle_progression[i]['z']
        z2 = z_angle_progression[i+1]['z']
        a1 = z_angle_progression[i]['avg_angle']
        a2 = z_angle_progression[i+1]['avg_angle']

        dz = z2 - z1
        if dz > 0.01:  # Avoid division by tiny numbers
            # Handle angle wrapping
            da = a2 - a1
            if da > math.pi:
                da -= 2*math.pi
            elif da < -math.pi:
                da += 2*math.pi

            derivative = da / dz
            angle_z_derivatives.append(derivative)

    if angle_z_derivatives:
        avg_derivative = sum(angle_z_derivatives) / len(angle_z_derivatives)
        derivative_variance = sum((d - avg_derivative)**2 for d in angle_z_derivatives) / len(angle_z_derivatives)

        print(f"\n" + "="*60)
        print("HELICAL PATTERN ANALYSIS:")
        print("="*60)
        print(f"Average d(angle)/d(z): {avg_derivative:.4f} rad/mm")
        print(f"Derivative variance: {derivative_variance:.6f}")

        # If derivative is consistent (low variance) and non-zero, it's a helix
        is_helical = derivative_variance < 0.01 and abs(avg_derivative) > 0.01

        if is_helical:
            # Calculate thread pitch
            # pitch = 2π / (d(theta)/d(z))
            if abs(avg_derivative) > 0.001:
                pitch = 2 * math.pi / abs(avg_derivative)
                print(f"\n✓ HELICAL PATTERN DETECTED!")
                print(f"  Thread pitch: {pitch:.3f} mm")
                print(f"  Direction: {'Right-hand' if avg_derivative > 0 else 'Left-hand'}")

                # Get average radius
                avg_r = sum(d['avg_radius'] for d in z_angle_progression) / len(z_angle_progression)
                print(f"  Average radius: {avg_r:.2f} mm")
                print(f"  Approximate thread diameter: {avg_r * 2:.2f} mm")

                return {
                    'is_helical': True,
                    'pitch': pitch,
                    'radius': avg_r,
                    'diameter': avg_r * 2,
                    'handedness': 'right' if avg_derivative > 0 else 'left'
                }

        print(f"\n✗ NO CLEAR HELICAL PATTERN")
        print(f"  Reason: {'Angle doesn\'t vary with Z' if abs(avg_derivative) < 0.01 else 'Irregular angle progression'}")
        print(f"  This suggests a SMOOTH CYLINDER (no threads)")

        return {'is_helical': False}

    return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 detect_helical.py <stl_file>")
        sys.exit(1)

    filename = sys.argv[1]
    print(f"Helical Thread Detection: {filename}")
    print("="*60)

    facets = parse_binary_stl(filename)
    print(f"Loaded {len(facets)} facets")

    cx, cy = find_cylinder_axis(facets)

    # Check multiple radius ranges for potential threaded holes
    radius_ranges = [
        (2, 5, "Small hole ~4mm diameter"),
        (4, 7, "Medium hole ~6mm diameter"),
        (6, 9, "Medium-large hole ~8mm diameter"),
        (8, 11, "Large hole ~10mm diameter")
    ]

    detected_helices = []

    for r_min, r_max, desc in radius_ranges:
        print(f"\n{'='*60}")
        print(f"Testing: {desc}")
        result = detect_helical_pattern(facets, cx, cy, (r_min, r_max))

        if result and result.get('is_helical'):
            detected_helices.append((desc, result))

    # Final summary
    print("\n" + "="*60)
    print("FINAL RESULTS:")
    print("="*60)

    if detected_helices:
        print(f"\n✓ Found {len(detected_helices)} threaded feature(s) with PRINTED THREADS:\n")
        for desc, result in detected_helices:
            print(f"  • {desc}")
            print(f"    - Diameter: {result['diameter']:.2f} mm")
            print(f"    - Pitch: {result['pitch']:.2f} mm")
            print(f"    - Hand: {result['handedness']}-hand thread")
            print()
    else:
        print("\n✗ NO HELICAL PATTERNS DETECTED")
        print("\nConclusion: Part likely has SMOOTH HOLES that need TAPPING")
        print("(Cylindrical features present but no spiral thread geometry)")

    print()

if __name__ == "__main__":
    main()
