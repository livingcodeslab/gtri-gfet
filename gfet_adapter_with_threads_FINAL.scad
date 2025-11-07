// GFET Adapter with 1/4-28 UNF Threaded HPLC Ports
// FINAL VERSION - Correct port locations identified
//
// Ports are on the RIGHT face (X≈28) at:
// - Port 1: Y=20.71, Z=11.58
// - Port 2: Y=16.92, Z=12.29

// HPLC port positions [y, z, depth_into_part]
// These are 30mm counterbores on the right face
hplc_ports = [
  [20.71, 11.58, 15.0],  // Port 1 - extend threads deeper than counterbore
  [16.92, 12.29, 15.0],  // Port 2
];

// 1/4-28 UNF thread parameters
unf_major_d = 6.35;    // 0.250" major diameter
unf_minor_d = 5.49;    // Minor diameter
unf_pitch = 0.907;     // 25.4mm / 28 TPI
thread_angle = 60;     // Standard V-thread

echo("=== GFET Adapter with 1/4-28 UNF Threads ===");
echo("Number of HPLC ports:", len(hplc_ports));
echo("Thread: 1/4-28 UNF");
echo("Major Diameter:", unf_major_d, "mm (0.250 in)");
echo("Pitch:", unf_pitch, "mm (28 TPI)");

module unf_thread_1_4_28(length) {
    // Create female 1/4-28 UNF internal thread
    // This is a helical groove that螺纹 into the hole

    thread_depth = (unf_major_d - unf_minor_d) / 2;
    steps_per_turn = 32;
    step_height = unf_pitch / steps_per_turn;

    // Helical thread groove
    for (z = [0 : step_height : length]) {
        angle = (z / unf_pitch) * 360;

        rotate([0, 0, angle])
        translate([unf_major_d/2 - thread_depth*0.5, 0, z])
        rotate([0, 90, 0])
        cylinder(h=thread_depth*1.2, r=thread_depth*0.65, center=true, $fn=6);
    }
}

module threaded_hole_1_4_28(depth) {
    // Female threaded hole
    difference() {
        cylinder(h=depth, d=unf_major_d, $fn=64);
        unf_thread_1_4_28(depth);
    }
}

module adapter_with_threads() {
    difference() {
        // Original adapter
        import("CAD/gfet_adapter.STL");

        // Add threaded holes on right face (pointing in -X direction)
        for (port = hplc_ports) {
            // Position at right face, point inward (-X direction)
            translate([28, port[0], port[1]])  // Right face is at X≈28
            rotate([0, -90, 0])  // Point in -X direction
            threaded_hole_1_4_28(port[2]);
        }
    }
}

// Render the final adapter
adapter_with_threads();

// Uncomment to render just a test thread
/*
echo("Rendering test thread only...");
threaded_hole_1_4_28(15);
*/
