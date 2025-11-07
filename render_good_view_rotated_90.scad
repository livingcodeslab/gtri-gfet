// Same exact cutaway that works, rotated 90 degrees

port_1 = [14, 28, 9];
port_2 = [14, 28, 19];
thread_minor_d = 5.49;
thread_pitch = 0.907;
thread_depth = 10;
thread_groove_depth = 1.2;

module v_groove_thread(depth) {
    turns = depth / thread_pitch;
    union() {
        cylinder(h=depth, d=thread_minor_d, $fn=80);
        for (i = [0:turns]) {
            z_pos = i * thread_pitch;
            if (z_pos < depth) {
                translate([0, 0, z_pos])
                rotate_extrude($fn=80)
                translate([thread_minor_d/2, 0, 0])
                polygon([[0, -thread_pitch/2], [thread_groove_depth, 0], [0, thread_pitch/2]]);
            }
        }
    }
}

// Rotate the entire assembly 90 degrees clockwise (viewed from top)
rotate([0, 0, -90])
difference() {
    difference() {
        import("CAD/gfet_adapter.STL");

        translate([port_1[0], port_1[1], port_1[2]])
        rotate([90, 0, 0])
        v_groove_thread(thread_depth);

        translate([port_2[0], port_2[1], port_2[2]])
        rotate([90, 0, 0])
        v_groove_thread(thread_depth);
    }

    // Cut away right half
    translate([14, 0, -10])
    cube([50, 50, 100]);
}
