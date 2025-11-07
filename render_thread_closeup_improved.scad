// Close-up of thread detail showing V-groove profile

port_1 = [14, 28, 9];
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

// Just the threaded section with a cutaway to see profile
difference() {
    translate([port_1[0], port_1[1], port_1[2]])
    rotate([90, 0, 0])
    v_groove_thread(thread_depth);

    // Cut away half to see thread profile
    translate([14, 0, -10])
    cube([50, 50, 100]);
}
