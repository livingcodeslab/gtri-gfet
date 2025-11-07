// GFET Adapter with 1/4-28 UNF Threads
// Auto-generated from STL analysis

// Thread hole positions [x, y, z_start, depth]
thread_holes = [
  [13.899, 14.699, 5.895, 16.150],
  [13.982, 1.124, 10.985, 5.969],
  [13.996, 16.943, 5.895, 16.150],
  [13.970, 12.410, 10.731, 6.477],
  [4.732, 6.731, 0.000, 27.940],
  [15.260, 18.634, 5.895, 16.150],
  [12.027, 18.634, 5.942, 16.057],
  [4.118, 25.984, 3.153, 21.634],
  [23.546, 6.825, 3.153, 21.634],
  [23.889, 25.984, 3.153, 21.634],
  [11.926, 27.423, 0.000, 27.940],
  [16.012, 27.423, 0.000, 27.940],
  [18.831, 27.176, 3.897, 20.147],
  [9.713, 27.232, 3.629, 20.682],
  [13.981, 27.195, 6.132, 15.677],
  [13.970, 20.692, 0.000, 27.940],
  [21.692, 27.015, 3.304, 21.331],
  [7.507, 27.058, 3.304, 21.331],
  [2.647, 6.731, 0.000, 27.940],
  [25.841, 6.731, 0.000, 27.940],
  [11.518, 0.440, 10.731, 6.477],
  [16.422, 0.440, 10.731, 6.477],
  [11.198, 16.634, 6.993, 13.953],
  [16.742, 16.634, 6.993, 13.953],
  [25.970, 25.984, 0.000, 27.940],
  [2.023, 26.637, 0.000, 27.940],
  [17.140, 2.327, 7.620, 12.700],
  [17.324, 19.859, 4.937, 18.065],
  [5.403, 27.518, 5.695, 16.549],
  [27.940, 6.731, 0.000, 27.940],
  [0.000, 25.984, 0.000, 27.940],
];

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
