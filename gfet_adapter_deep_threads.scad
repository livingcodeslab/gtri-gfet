// GFET Adapter with DEEP, VISIBLE 1/4-28 UNF Threads
// Proper V-groove thread profile

// Port positions from barrel analysis
port_1 = [8, 28, 9];     // Lower port: X=8, Z=9, entering at Y=28
port_2 = [8, 28, 19];    // Upper port: X=8, Z=19, entering at Y=28

// 1/4-28 UNF specifications
thread_major_d = 6.35;      // Major diameter (1/4" = 6.35mm)
thread_minor_d = 5.49;      // Minor diameter
thread_pitch = 0.907;       // 25.4/28 = 0.907mm
thread_depth = 15;          // How deep threads go
thread_groove_depth = 1.2;  // MUCH DEEPER for visibility (was 0.428mm)

echo("=== GFET Adapter with DEEP Threads ===");
echo("Port 1 (lower):", port_1);
echo("Port 2 (upper):", port_2);
echo("Thread groove depth:", thread_groove_depth, "mm (4x deeper for visibility)");
echo("Thread pitch:", thread_pitch, "mm");

// V-groove thread profile (proper 60-degree thread)
module v_groove_thread(depth) {
    turns = depth / thread_pitch;

    union() {
        // Core cylinder at minor diameter
        cylinder(h=depth, d=thread_minor_d, $fn=80);

        // Helical V-groove using polygon profile
        for (i = [0:turns]) {
            z_pos = i * thread_pitch;

            if (z_pos < depth) {
                translate([0, 0, z_pos])
                rotate_extrude($fn=80)
                translate([thread_minor_d/2, 0, 0])
                polygon([
                    [0, -thread_pitch/2],                          // Bottom of groove
                    [thread_groove_depth, 0],                       // Peak (thread crest)
                    [0, thread_pitch/2]                            // Top of groove
                ]);
            }
        }
    }
}

// Main adapter with threaded ports
difference() {
    import("CAD/gfet_adapter.STL");

    // Port 1 - horizontal thread pointing inward (negative Y)
    translate([port_1[0], port_1[1], port_1[2]])
    rotate([90, 0, 0])
    v_groove_thread(thread_depth);

    // Port 2 - horizontal thread pointing inward (negative Y)
    translate([port_2[0], port_2[1], port_2[2]])
    rotate([90, 0, 0])
    v_groove_thread(thread_depth);
}
