#!/usr/bin/env python3
"""
Detailed STL Thread Analyzer
Provides more comprehensive analysis of cylindrical features.
"""

import sys
import struct
import math
from collections import defaultdict

def parse_binary_stl(filename):
    """Parse binary STL file."""
    facets = []
    with open(filename, 'rb') as f:
        f.read(80)  # Skip header
        num_triangles = struct.unpack('<I', f.read(4))[0]

        for _ in range(num_triangles):
            normal = struct.unpack('<fff', f.read(12))
            v1 = struct.unpack('<fff', f.read(12))
            v2 = struct.unpack('<fff', f.read(12))
            v3 = struct.unpack('<fff', f.read(12))
            f.read(2)  # Attribute

            facets.append({
                'normal': list(normal),
                'vertices': [list(v1), list(v2), list(v3)]
            })

    return facets

def analyze_cylindrical_holes(facets):
    """Detailed analysis of cylindrical features by examining vertex radii."""
    all_vertices = []
    for facet in facets:
        all_vertices.extend(facet['vertices'])

    # Calculate center of part
    cx = sum(v[0] for v in all_vertices) / len(all_vertices)
    cy = sum(v[1] for v in all_vertices) / len(all_vertices)

    print(f"\nPart center (X, Y): ({cx:.2f}, {cy:.2f})")

    # Group vertices by Z-height
    z_groups = defaultdict(list)
    for v in all_vertices:
        z_key = round(v[2], 1)
        radius = math.sqrt((v[0] - cx)**2 + (v[1] - cy)**2)
        z_groups[z_key].append(radius)

    # Look for holes (vertices at consistent small radii from center)
    print("\nAnalyzing radial distribution at different heights:")
    print("(Looking for internal holes/cylinders)\n")

    hole_candidates = []

    for z in sorted(z_groups.keys())[::5]:  # Sample every 0.5mm
        radii = z_groups[z]

        # Find clusters of radii (potential hole walls)
        radius_hist = defaultdict(int)
        for r in radii:
            r_key = round(r, 0)  # Bucket by 1mm
            radius_hist[r_key] += 1

        # Look for significant concentrations at specific radii
        significant_radii = [(r, count) for r, count in radius_hist.items()
                            if count > 10 and 2 < r < 15]  # Filter reasonable hole sizes

        if significant_radii and z % 2 == 0:  # Print every 2mm
            print(f"  Z={z:.1f}mm: Radii concentrations: {sorted(significant_radii)[:5]}")

        # Track potential holes
        for r, count in significant_radii:
            if count > 15:  # Strong signal
                hole_candidates.append((z, r, count))

    # Group hole candidates by similar radius
    if hole_candidates:
        print("\n" + "="*60)
        print("POTENTIAL CYLINDRICAL FEATURES:")
        print("="*60)

        radius_groups = defaultdict(list)
        for z, r, count in hole_candidates:
            r_key = round(r / 2) * 2  # Group by ~2mm radius ranges
            radius_groups[r_key].append((z, r, count))

        for avg_radius in sorted(radius_groups.keys()):
            features = radius_groups[avg_radius]
            z_min = min(z for z, _, _ in features)
            z_max = max(z for z, _, _ in features)
            z_span = z_max - z_min

            print(f"\nFeature at radius ~{avg_radius}mm:")
            print(f"  Z-range: {z_min:.1f} to {z_max:.1f} mm (span: {z_span:.1f}mm)")
            print(f"  Appears at {len(features)} Z-levels")
            print(f"  Diameter: ~{avg_radius * 2}mm")

    return hole_candidates

def analyze_thread_indicators(facets):
    """Look for indicators of threads vs smooth holes."""
    # Analyze normal vector distribution
    normals = [f['normal'] for f in facets]

    # For threads, expect varied Z-components in normals (helical surface)
    # For smooth holes, expect normals mostly radial (Z ~ 0)

    z_normals = [n[2] for n in normals]
    avg_z_normal = sum(abs(z) for z in z_normals) / len(z_normals)

    radial_normals = sum(1 for nz in z_normals if abs(nz) < 0.3)
    angled_normals = sum(1 for nz in z_normals if abs(nz) >= 0.3)

    print("\n" + "="*60)
    print("SURFACE NORMAL ANALYSIS:")
    print("="*60)
    print(f"Total facets: {len(facets)}")
    print(f"Radial normals (|Z|<0.3): {radial_normals} ({radial_normals/len(facets)*100:.1f}%)")
    print(f"Angled normals (|Z|>=0.3): {angled_normals} ({angled_normals/len(facets)*100:.1f}%)")

    if radial_normals > angled_normals * 2:
        print("\n→ Dominant radial surfaces detected")
        print("   This suggests mostly vertical walls (typical for holes)")
    else:
        print("\n→ Mixed surface orientations")
        print("   Could indicate threads or complex geometry")

    # Analyze for helical patterns
    vertices_with_normals = []
    for f in facets:
        for v in f['vertices']:
            vertices_with_normals.append((v, f['normal']))

    # Sample vertices at different Z heights and check normal variation
    z_levels = defaultdict(list)
    for v, n in vertices_with_normals:
        z_key = round(v[2] * 2) / 2  # Round to nearest 0.5
        z_levels[z_key].append(n)

    print("\nChecking for helical patterns (thread indicator)...")
    has_helical_pattern = False

    # Thread pitch detection - look for repeating normal patterns
    if len(z_levels) > 10:
        z_sorted = sorted(z_levels.keys())
        # Check normal variation at regular intervals
        for i in range(0, len(z_sorted) - 5, 2):
            z_level = z_sorted[i]
            normals_at_z = z_levels[z_level]

            if len(normals_at_z) > 20:
                z_components = [n[2] for n in normals_at_z]
                z_variance = sum((z - sum(z_components)/len(z_components))**2 for z in z_components)

                if z_variance > 0.1:  # High variation suggests thread features
                    has_helical_pattern = True
                    break

    return has_helical_pattern

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_threads_detailed.py <stl_file>")
        sys.exit(1)

    filename = sys.argv[1]
    print(f"Detailed Thread Analysis: {filename}")
    print("="*60)

    facets = parse_binary_stl(filename)
    print(f"Loaded {len(facets)} triangular facets")

    hole_candidates = analyze_cylindrical_holes(facets)
    has_helical = analyze_thread_indicators(facets)

    print("\n" + "="*60)
    print("FINAL ASSESSMENT:")
    print("="*60)

    if hole_candidates:
        print(f"\n✓ Found {len(set(round(h[1]/2)*2 for h in hole_candidates))} distinct cylindrical feature(s)")

        if has_helical:
            print("\n⚠ POSSIBLE PRINTED THREADS detected")
            print("  Reason: Helical normal variation patterns found")
            print("  Recommendation: Inspect closely - may have printed threads")
        else:
            print("\n✓ Likely SMOOTH HOLES - TAPPING REQUIRED")
            print("  Reason: Radial surfaces dominate, no clear helical patterns")
            print("  Recommendation: These holes will need to be tapped for threads")
    else:
        print("\n? No clear cylindrical features detected")
        print("  Part may not have simple threaded holes")
        print("  Or detection parameters need adjustment")

    print()

if __name__ == "__main__":
    main()
