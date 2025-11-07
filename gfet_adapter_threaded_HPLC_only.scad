// GFET Adapter with 1/4-28 UNF Threaded HPLC Ports
// Refined version - only high-confidence HPLC port locations
// Auto-generated from STL analysis

// Primary HPLC port locations [x, y, z_start, depth]
// These are the most confident matches for 5.5mm tap drill holes
hplc_ports = [
  // Main port (center, high confidence)
  [13.982, 1.124, 10.985, 5.969],

  // Additional ports with good confidence
  [13.996, 16.943, 5.895, 16.150],
  [11.926, 27.423, 0.000, 27.940],
  [16.012, 27.423, 0.000, 27.940],
  [11.518, 0.440, 10.731, 6.477],
  [16.422, 0.440, 10.731, 6.477],
  [11.198, 16.634, 6.993, 13.953],
  [16.742, 16.634, 6.993, 13.953],
];

// 1/4-28 UNF thread parameters (standard HPLC fitting)
unf_major_d = 6.35;    // 0.250" major diameter (1/4")
unf_minor_d = 5.49;    // Minor diameter
unf_pitch = 0.907;     // Thread pitch: 25.4mm / 28 TPI
thread_angle = 60;     // UNF thread angle

echo("=== 1/4-28 UNF Thread Specifications ===");
echo("Major Diameter: ", unf_major_d, " mm (0.250 in)");
echo("Minor Diameter: ", unf_minor_d, " mm");
echo("Pitch: ", unf_pitch, " mm");
echo("TPI: ", 28);
echo("Number of HPLC ports: ", len(hplc_ports));

module unf_thread_profile(length) {
    // Create helical thread groove for internal threads
    thread_depth = (unf_major_d - unf_minor_d) / 2;
    steps_per_turn = 32;  // Resolution
    step_height = unf_pitch / steps_per_turn;

    for (z = [0 : step_height : length]) {
        angle = (z / unf_pitch) * 360;
        rotate([0, 0, angle])
        translate([unf_major_d/2 - thread_depth*0.5, 0, z])
        rotate([0, 90, 0])
        cylinder(h=thread_depth*1.2, r=thread_depth*0.65, center=true, $fn=6);
    }
}

module threaded_hole_1_4_28_unf(depth) {
    // Create 1/4-28 UNF female threaded hole
    difference() {
        // Major diameter cylinder
        cylinder(h=depth, d=unf_major_d, $fn=64);
        // Subtract helical groove
        unf_thread_profile(depth);
    }
}

// Main model: Original adapter with threaded HPLC ports
difference() {
    // Import original smooth-hole adapter
    import("CAD/gfet_adapter.STL");

    // Drill out and thread each HPLC port
    for (port = hplc_ports) {
        translate([port[0], port[1], port[2]])
        threaded_hole_1_4_28_unf(port[3]);
    }
}

// Uncomment to render just a single test thread
/*
echo("Rendering test thread...");
threaded_hole_1_4_28_unf(15);  // 15mm deep test thread
*/
