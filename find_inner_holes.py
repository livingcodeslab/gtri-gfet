#!/usr/bin/env python3
"""
Find inner threaded holes within larger features.
Look for small-diameter cylinders that would be the actual threaded ports.
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

def find_thread_holes_locally(facets):
    """
    Find small threaded holes by looking at local centers,
    not just the part center.
    """

    all_verts = []
    for f in facets:
        all_verts.extend(f['vertices'])

    # Grid search: divide part into regions and find cylindrical features in each
    xs = [v[0] for v in all_verts]
    ys = [v[1] for v in all_verts]

    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)

    print(f"Part bounds: X[{x_min:.1f}, {x_max:.1f}], Y[{y_min:.1f}, {y_max:.1f}]")

    # Test grid of potential hole centers
    step = 1  # 1mm grid
    holes = []

    for cx in [x for x in range(int(x_min), int(x_max)+1, step)]:
        for cy in [y for y in range(int(y_min), int(y_max)+1, step)]:

            # Check if vertices cluster at small radii from this point
            radial_verts = defaultdict(list)

            for v in all_verts:
                dx = v[0] - cx
                dy = v[1] - cy
                r = math.sqrt(dx**2 + dy**2)

                # Only look at small radii (thread hole size)
                if 2 < r < 4:  # 4-8mm diameter holes
                    r_bucket = round(r * 2) / 2  # Round to 0.5mm
                    radial_verts[r_bucket].append(v)

            # If we have significant vertices at a consistent radius, it's a hole
            for radius, verts in radial_verts.items():
                if len(verts) > 50:  # Significant feature
                    z_coords = [v[2] for v in verts]
                    z_span = max(z_coords) - min(z_coords)

                    if z_span > 5:  # Hole depth > 5mm
                        # Calculate exact center
                        exact_cx = sum(v[0] for v in verts) / len(verts)
                        exact_cy = sum(v[1] for v in verts) / len(verts)

                        holes.append({
                            'center_x': exact_cx,
                            'center_y': exact_cy,
                            'z_min': min(z_coords),
                            'z_max': max(z_coords),
                            'depth': z_span,
                            'radius': radius,
                            'diameter': radius * 2,
                            'num_verts': len(verts)
                        })

    # Remove duplicates
    unique_holes = []
    for h in sorted(holes, key=lambda x: x['num_verts'], reverse=True):
        is_dup = False
        for uh in unique_holes:
            dist = math.sqrt((h['center_x'] - uh['center_x'])**2 +
                           (h['center_y'] - uh['center_y'])**2)
            if dist < 2:
                is_dup = True
                break
        if not is_dup:
            unique_holes.append(h)

    return unique_holes

def main():
    print("Finding Inner Thread Holes (HPLC fitting ports)")
    print("="*65)

    facets = parse_binary_stl('CAD/gfet_adapter.STL')
    print(f"Loaded {len(facets)} facets\n")

    holes = find_thread_holes_locally(facets)

    print(f"\n{'='*65}")
    print(f"FOUND {len(holes)} THREAD HOLE(S):")
    print("="*65)

    for i, h in enumerate(sorted(holes, key=lambda x: x['num_verts'], reverse=True), 1):
        print(f"\nThread Hole #{i}:")
        print(f"  Position (X, Y): ({h['center_x']:.2f}, {h['center_y']:.2f})")
        print(f"  Z range: {h['z_min']:.2f} to {h['z_max']:.2f} mm")
        print(f"  Depth: {h['depth']:.2f} mm")
        print(f"  Current diameter: {h['diameter']:.2f} mm (smooth hole)")
        print(f"  Data quality: {h['num_verts']} vertices")

        # Check against 1/4-28 tap drill (5.41mm)
        expected_drill = 5.5
        if abs(h['diameter'] - expected_drill) < 1.0:
            print(f"  ✓ MATCHES 1/4-28 UNF tap drill size!")
            print(f"    Thread major diameter: 6.35mm (0.250\")")
            print(f"    Thread pitch: 0.907mm (28 TPI)")

    if holes:
        print(f"\n{'='*65}")
        print("OpenSCAD Module for Threaded Adapter:")
        print("="*65)

        print("\n// Auto-detected thread hole positions")
        print("thread_holes = [")
        for h in holes:
            print(f"  [{h['center_x']:.3f}, {h['center_y']:.3f}, {h['z_min']:.3f}, {h['depth']:.3f}],")
        print("];")

        # Save complete OpenSCAD file
        scad_code = """// GFET Adapter with 1/4-28 UNF Threads
// Auto-generated from STL analysis

// Thread hole positions [x, y, z_start, depth]
thread_holes = [
"""
        for h in holes:
            scad_code += f"  [{h['center_x']:.3f}, {h['center_y']:.3f}, {h['z_min']:.3f}, {h['depth']:.3f}],\n"

        scad_code += """];

// 1/4-28 UNF thread parameters
unf_major_d = 6.35;    // 0.250" major diameter
unf_minor_d = 5.49;    // Minor diameter
unf_pitch = 0.907;     // 25.4mm / 28 TPI

module thread_profile(h) {
    // Simple V-thread profile for 1/4-28
    thread_depth = (unf_major_d - unf_minor_d) / 2;

    for (z = [0 : unf_pitch/2 : h]) {
        angle = (z / unf_pitch) * 360;
        rotate([0, 0, angle])
        translate([unf_major_d/2 - thread_depth*0.6, 0, z])
        rotate([0, 90, 0])
        cylinder(h=thread_depth, r=thread_depth*0.5, center=true, $fn=6);
    }
}

module threaded_hole_1_4_28(depth) {
    difference() {
        cylinder(h=depth, d=unf_major_d, $fn=64);
        thread_profile(depth);
    }
}

// Create adapter with threaded holes
difference() {
    // Import original adapter
    import("gfet_adapter.STL");

    // Remove smooth holes and add threaded ones
    for (hole = thread_holes) {
        translate([hole[0], hole[1], hole[2]])
        threaded_hole_1_4_28(hole[3]);
    }
}
"""

        with open('gfet_adapter_threaded.scad', 'w') as f:
            f.write(scad_code)

        print("\n✓ Created gfet_adapter_threaded.scad")
        print("  Run: openscad gfet_adapter_threaded.scad -o gfet_adapter_threaded.stl")

if __name__ == "__main__":
    main()
