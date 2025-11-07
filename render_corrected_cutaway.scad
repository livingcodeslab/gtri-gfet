// Cutaway view of corrected thread positions

port_1 = [14, 28, 9];
port_2 = [14, 28, 19];
thread_minor_d = 5.49;
thread_pitch = 0.907;
thread_depth = 10;
thread_groove_depth = 1.2;

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
                polygon([[0, -thread_pitch/2], [thread_groove_depth, 0], [0, thread_pitch/2]]);
            }
        }
    }
}

// Cutaway view - slice at X=14
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
