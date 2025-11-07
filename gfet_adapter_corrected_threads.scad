// GFET Adapter with CORRECTED Thread Positions
// Based on precise scanning: X=14 (not X=8), ~14mm deep counterbores

// Corrected port positions [x, y_entrance, z]
port_1 = [14, 28, 9];     // Lower port
port_2 = [14, 28, 19];    // Upper port

// 1/4-28 UNF specifications
thread_major_d = 6.35;
thread_minor_d = 5.49;
thread_pitch = 0.907;
thread_depth = 10;          // 10mm deep - stops before bottom of counterbore
thread_groove_depth = 1.2;

echo("=== GFET Adapter CORRECTED Positions ===");
echo("Port 1 (lower):", port_1, "- counterbore ~14mm deep");
echo("Port 2 (upper):", port_2, "- counterbore ~14mm deep");
echo("Thread depth:", thread_depth, "mm (stops just before bottom of barrel)");
echo("Thread: 1/4-28 UNF for standard HPLC fittings");

// V-groove thread profile
module v_groove_thread(depth) {
    turns = depth / thread_pitch;

    union() {
        cylinder(h=depth, d=thread_minor_d, $fn=120);

        for (i = [0:turns]) {
            z_pos = i * thread_pitch;

            if (z_pos < depth) {
                translate([0, 0, z_pos])
                rotate_extrude($fn=120)
                translate([thread_minor_d/2, 0, 0])
                polygon([
                    [0, -thread_pitch/2],
                    [thread_groove_depth, 0],
                    [0, thread_pitch/2]
                ]);
            }
        }
    }
}

// Main adapter with corrected threaded ports
difference() {
    import("CAD/gfet_adapter.STL");

    // Port 1 - counterbore with threads
    translate([port_1[0], port_1[1], port_1[2]])
    rotate([90, 0, 0])
    v_groove_thread(thread_depth);

    // Port 2 - counterbore with threads
    translate([port_2[0], port_2[1], port_2[2]])
    rotate([90, 0, 0])
    v_groove_thread(thread_depth);
}
