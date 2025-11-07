// GFET Adapter with 1/4-28 UNF Threads (Simple approach)
// Ports detected at (8, 23) and (18, 23)

// Port positions [x, y, z_top]
port_1 = [8, 23, 27.94];
port_2 = [18, 23, 27.94];

// 1/4-28 UNF specifications
thread_od = 6.35;        // Major diameter (1/4" = 6.35mm)
thread_id = 5.49;        // Minor diameter
thread_pitch = 0.907;    // 25.4/28 = 0.907mm
thread_depth = 15;       // Thread depth
thread_height = 0.428;   // Thread height (60° profile)

echo("=== GFET Adapter with Simple Threads ===");
echo("Port 1:", port_1);
echo("Port 2:", port_2);
echo("Thread: 1/4-28 UNF");
echo("Thread OD:", thread_od, "mm");
echo("Thread pitch:", thread_pitch, "mm");

// Simple threaded hole using helix and difference
module simple_threaded_hole(depth) {
    turns = depth / thread_pitch;

    union() {
        // Core hole at minor diameter
        cylinder(h=depth, d=thread_id, $fn=60);

        // Helical thread groove
        for (i = [0:turns-1]) {
            rotate([0, 0, i * 360])
            translate([0, 0, i * thread_pitch])
            rotate([0, 0, 60])  // 60° thread angle
            linear_extrude(height=thread_pitch * 1.1, twist=360, slices=20, $fn=60)
            translate([thread_id/2, 0, 0])
            circle(d=thread_height, $fn=6);
        }
    }
}

// Main adapter with threaded ports
difference() {
    import("CAD/gfet_adapter.STL");

    // Port 1 - thread pointing down
    translate([port_1[0], port_1[1], port_1[2]])
    rotate([180, 0, 0])
    simple_threaded_hole(thread_depth);

    // Port 2 - thread pointing down
    translate([port_2[0], port_2[1], port_2[2]])
    rotate([180, 0, 0])
    simple_threaded_hole(thread_depth);
}
