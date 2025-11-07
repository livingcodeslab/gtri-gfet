#!/usr/bin/env python3
"""
STL Thread Analyzer
Analyzes an STL file to determine if it has printed threads or smooth holes that need tapping.
"""

import sys
import re
from collections import defaultdict
import math
import struct

def is_ascii_stl(filename):
    """Check if STL file is ASCII format."""
    with open(filename, 'rb') as f:
        # Read first 1000 bytes to check format
        sample = f.read(1000)
        try:
            # Try to decode as ASCII
            text = sample.decode('ascii')
            # Check for ASCII STL keywords
            if 'facet normal' in text and 'vertex' in text:
                return True
        except:
            pass
        return False

def parse_binary_stl(filename):
    """Parse binary STL file and extract vertices and normals."""
    facets = []

    with open(filename, 'rb') as f:
        # Read header (80 bytes)
        header = f.read(80)

        # Read number of triangles (4 bytes, unsigned int)
        num_triangles = struct.unpack('<I', f.read(4))[0]

        # Read each triangle
        for _ in range(num_triangles):
            # Normal vector (3 floats, 12 bytes)
            normal = struct.unpack('<fff', f.read(12))

            # Vertex 1 (3 floats, 12 bytes)
            v1 = struct.unpack('<fff', f.read(12))

            # Vertex 2 (3 floats, 12 bytes)
            v2 = struct.unpack('<fff', f.read(12))

            # Vertex 3 (3 floats, 12 bytes)
            v3 = struct.unpack('<fff', f.read(12))

            # Attribute byte count (2 bytes)
            f.read(2)

            facets.append({
                'normal': list(normal),
                'vertices': [list(v1), list(v2), list(v3)]
            })

    return facets

def parse_ascii_stl(filename):
    """Parse ASCII STL file and extract vertices and normals."""
    facets = []

    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Extract all facets
    facet_pattern = r'facet normal\s+([-\d.e+]+)\s+([-\d.e+]+)\s+([-\d.e+]+).*?outer loop\s+vertex\s+([-\d.e+]+)\s+([-\d.e+]+)\s+([-\d.e+]+)\s+vertex\s+([-\d.e+]+)\s+([-\d.e+]+)\s+([-\d.e+]+)\s+vertex\s+([-\d.e+]+)\s+([-\d.e+]+)\s+([-\d.e+]+)'

    matches = re.finditer(facet_pattern, content, re.DOTALL)

    for match in matches:
        normal = [float(match.group(i)) for i in range(1, 4)]
        v1 = [float(match.group(i)) for i in range(4, 7)]
        v2 = [float(match.group(i)) for i in range(7, 10)]
        v3 = [float(match.group(i)) for i in range(10, 13)]

        facets.append({
            'normal': normal,
            'vertices': [v1, v2, v3]
        })

    return facets

def parse_stl(filename):
    """Parse STL file (auto-detect ASCII or binary)."""
    if is_ascii_stl(filename):
        print("  Format: ASCII STL")
        return parse_ascii_stl(filename)
    else:
        print("  Format: Binary STL")
        return parse_binary_stl(filename)

def find_cylindrical_features(facets, tolerance=0.5):
    """
    Identify cylindrical features in the mesh.
    Returns clusters of vertices that appear to form cylinders.
    """
    # Collect all unique vertices
    vertices = []
    for facet in facets:
        vertices.extend(facet['vertices'])

    # Get Z-axis coordinates (assuming Z is the vertical axis)
    z_coords = sorted(set(round(v[2], 2) for v in vertices))

    # Analyze each Z-level for circular patterns
    circular_features = []

    for z in z_coords:
        # Get vertices at this Z level
        level_verts = [v for v in vertices if abs(v[2] - z) < tolerance]

        if len(level_verts) < 8:  # Need enough points to form a circle
            continue

        # Calculate center
        if level_verts:
            cx = sum(v[0] for v in level_verts) / len(level_verts)
            cy = sum(v[1] for v in level_verts) / len(level_verts)

            # Calculate radii
            radii = [math.sqrt((v[0]-cx)**2 + (v[1]-cy)**2) for v in level_verts]
            avg_radius = sum(radii) / len(radii)
            radius_variance = sum((r - avg_radius)**2 for r in radii) / len(radii)

            # If radii are consistent, this might be a circular feature
            if radius_variance < 2.0 and avg_radius > 1.0:  # Threshold for circularity
                circular_features.append({
                    'z': z,
                    'center': (cx, cy),
                    'radius': avg_radius,
                    'variance': radius_variance,
                    'num_points': len(level_verts)
                })

    return circular_features

def analyze_thread_pattern(facets):
    """
    Analyze mesh for helical patterns that would indicate printed threads.
    """
    # Look for repeating patterns in the normals that might indicate threads
    normals = [tuple(round(n, 3) for n in facet['normal']) for facet in facets]

    # Count normal directions
    normal_counts = defaultdict(int)
    for n in normals:
        normal_counts[n] += 1

    # Analyze vertex distribution for spiral patterns
    all_vertices = []
    for facet in facets:
        all_vertices.extend(facet['vertices'])

    # Group vertices by Z height
    z_groups = defaultdict(list)
    for v in all_vertices:
        z_rounded = round(v[2], 1)
        z_groups[z_rounded].append((v[0], v[1]))

    # Check for consistent Z-level spacing (thread pitch)
    z_levels = sorted(z_groups.keys())
    if len(z_levels) > 10:
        z_diffs = [z_levels[i+1] - z_levels[i] for i in range(len(z_levels)-1)]
        avg_z_diff = sum(z_diffs) / len(z_diffs)
        z_diff_variance = sum((d - avg_z_diff)**2 for d in z_diffs) / len(z_diffs)

        print(f"\nZ-level analysis:")
        print(f"  Number of Z-levels: {len(z_levels)}")
        print(f"  Average Z-spacing: {avg_z_diff:.3f}")
        print(f"  Z-spacing variance: {z_diff_variance:.3f}")

        # Regular spacing might indicate threads
        if z_diff_variance < 0.1 and 0.3 < avg_z_diff < 2.0:
            return "POSSIBLE_PRINTED_THREADS"

    return "UNCLEAR"

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_stl.py <stl_file>")
        sys.exit(1)

    filename = sys.argv[1]

    print(f"Analyzing STL file: {filename}")
    print("="*60)

    # Parse STL
    print("\nParsing STL file...")
    facets = parse_stl(filename)
    print(f"Found {len(facets)} facets")

    # Get bounding box
    all_verts = []
    for facet in facets:
        all_verts.extend(facet['vertices'])

    x_coords = [v[0] for v in all_verts]
    y_coords = [v[1] for v in all_verts]
    z_coords = [v[2] for v in all_verts]

    print(f"\nBounding box:")
    print(f"  X: {min(x_coords):.2f} to {max(x_coords):.2f} (size: {max(x_coords)-min(x_coords):.2f})")
    print(f"  Y: {min(y_coords):.2f} to {max(y_coords):.2f} (size: {max(y_coords)-min(y_coords):.2f})")
    print(f"  Z: {min(z_coords):.2f} to {max(z_coords):.2f} (height: {max(z_coords)-min(z_coords):.2f})")

    # Find cylindrical features
    print("\nSearching for cylindrical features (potential threaded holes)...")
    circular_features = find_cylindrical_features(facets)

    if circular_features:
        print(f"\nFound {len(circular_features)} potential circular cross-sections:")

        # Group by similar radius to identify continuous holes
        radius_groups = defaultdict(list)
        for cf in circular_features:
            radius_key = round(cf['radius'], 1)
            radius_groups[radius_key].append(cf)

        print(f"\nIdentified {len(radius_groups)} distinct cylindrical features by radius:")
        for radius, features in sorted(radius_groups.items()):
            print(f"\n  Radius ~{radius:.1f} mm:")
            print(f"    Number of cross-sections: {len(features)}")
            z_range = max(f['z'] for f in features) - min(f['z'] for f in features)
            print(f"    Z-range: {min(f['z'] for f in features):.2f} to {max(f['z'] for f in features):.2f} (depth: {z_range:.2f})")
            print(f"    Average variance: {sum(f['variance'] for f in features)/len(features):.3f}")
    else:
        print("  No clear cylindrical features detected")

    # Analyze for thread patterns
    print("\nAnalyzing for helical thread patterns...")
    thread_analysis = analyze_thread_pattern(facets)

    print("\n" + "="*60)
    print("CONCLUSION:")
    print("="*60)

    if circular_features:
        avg_variance = sum(f['variance'] for f in circular_features) / len(circular_features)

        if avg_variance < 0.5:
            print("\n✓ Detected smooth cylindrical holes")
            print("  These appear to be SMOOTH HOLES that will need TAPPING")
            print("  The circular cross-sections are very regular without thread patterns")
        elif thread_analysis == "POSSIBLE_PRINTED_THREADS":
            print("\n✓ Detected possible printed threads")
            print("  Regular Z-spacing suggests helical thread pattern")
            print("  These may be PRINTED THREADS")
        else:
            print("\n? Inconclusive - manual inspection recommended")
            print("  Geometry detected but thread pattern unclear")
            print("  Check the STL in a viewer and look for:")
            print("    - Spiral patterns on cylinder walls = printed threads")
            print("    - Smooth cylinder walls = needs tapping")
    else:
        print("\n! No clear threaded features detected")
        print("  The part may not have threaded connectors")
        print("  Or the features are too complex for automatic detection")

    print("\n")

if __name__ == "__main__":
    main()
