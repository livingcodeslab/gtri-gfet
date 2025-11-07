// GFET Adapter with 1/4-28 UNF Threaded Holes
// Generated to replace smooth holes with printed threads

// Import the original STL
// Note: We'll need to identify hole positions first

// Thread library - ISO/UNF thread generation
// Based on thread specifications

// 1/4-28 UNF thread parameters
unf_1_4_28_major_d = 6.35;      // 0.25" major diameter
unf_1_4_28_minor_d = 5.49;      // Minor diameter
unf_1_4_28_pitch = 0.907;       // Thread pitch (25.4mm / 28 TPI)

module iso_thread(diameter, pitch, length, internal=false) {
    // Simplified thread generation
    // For internal threads (holes), we need the tap drill size

    minor_d = diameter - (1.226 * pitch);
    pitch_r = diameter / 2;

    difference() {
        cylinder(h=length, r=pitch_r, $fn=50);

        if (internal) {
            // Internal thread - create helical groove
            for (i = [0 : pitch : length]) {
                rotate([0, 0, i / pitch * 360])
                translate([0, 0, i])
                rotate([0, 90, 0])
                cylinder(h=diameter, r=pitch*0.6, center=true, $fn=20);
            }
        }
    }
}

module unf_1_4_28_threaded_hole(depth, through=true) {
    // Creates a 1/4-28 UNF threaded hole
    // depth: depth of the hole in mm

    pitch = unf_1_4_28_pitch;
    major_d = unf_1_4_28_major_d;
    minor_d = unf_1_4_28_minor_d;

    // Create helical thread profile
    thread_depth = (major_d - minor_d) / 2;

    difference() {
        cylinder(h=depth, r=major_d/2, $fn=64);

        // Helical thread groove
        for (z = [0 : pitch/4 : depth]) {
            angle = (z / pitch) * 360;
            rotate([0, 0, angle])
            translate([major_d/2 - thread_depth/2, 0, z])
            rotate([0, 90, 0])
            cylinder(h=thread_depth*1.5, r=thread_depth*0.6, center=true, $fn=12);
        }
    }
}

// Test the thread
echo("1/4-28 UNF Thread Parameters:");
echo("  Major diameter: ", unf_1_4_28_major_d, "mm");
echo("  Minor diameter: ", unf_1_4_28_minor_d, "mm");
echo("  Pitch: ", unf_1_4_28_pitch, "mm");
echo("  TPI: ", 25.4/unf_1_4_28_pitch);

// Example: Create a test block with threaded hole
module test_threaded_block() {
    difference() {
        cube([20, 20, 15]);

        // Centered threaded hole
        translate([10, 10, 0])
        unf_1_4_28_threaded_hole(depth=15);
    }
}

// Uncomment to render test block
// test_threaded_block();

// To create the full adapter with threads:
// 1. Identify hole positions from the original STL
// 2. Import original STL
// 3. Union with thread geometry at hole locations

// Placeholder for actual adapter modification
// Once we know hole positions, we'll do:
/*
difference() {
    import("gfet_adapter.STL");

    // Remove smooth holes and add threaded ones
    for hole in hole_positions {
        translate([hole[0], hole[1], hole[2]])
        unf_1_4_28_threaded_hole(depth=hole[3]);
    }
}
*/
