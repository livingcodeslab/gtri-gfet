// Standard HPLC Male Connector (1/4-28 UNF)
// Based on typical IDEX/Parker/Swagelok dimensions
// Adjustable parameters for different manufacturers

// ===== PARAMETERS (adjust these to match your specific fitting) =====

// Thread specifications
thread_major_d = 6.35;      // 1/4" = 6.35mm
thread_minor_d = 5.49;      // UNF minor diameter
thread_pitch = 0.907;       // 28 TPI = 0.907mm pitch
thread_length = 8.0;        // Typical thread engagement length

// Body dimensions
hex_across_flats = 11.1;    // 7/16" hex (11.11mm)
hex_height = 4.0;           // Height of hex body

body_diameter = 8.0;        // Diameter after hex
body_length = 6.0;          // Length of cylindrical body

// Stem/ferrule area (the part that goes into the port)
stem_diameter = 3.175;      // 1/8" OD tubing = 3.175mm
stem_length = 6.0;          // Typical stem length before thread

// Overall length calculation
total_length = hex_height + body_length + stem_length + thread_length;

echo("=== HPLC Male Connector Specifications ===");
echo("Thread: 1/4-28 UNF");
echo("Thread Major Diameter:", thread_major_d, "mm");
echo("Thread Length:", thread_length, "mm");
echo("Hex Size (across flats):", hex_across_flats, "mm");
echo("Total Length:", total_length, "mm");
echo("Stem Diameter:", stem_diameter, "mm");

// ===== MODULES =====

module hex_prism(across_flats, height) {
    // Create a hexagonal prism
    radius = across_flats / (2 * cos(30));
    cylinder(h=height, r=radius, $fn=6);
}

module unf_external_thread(major_d, pitch, length) {
    // Simplified external thread - helical ridge
    thread_depth = (major_d - thread_minor_d) / 2;
    core_d = major_d - 2*thread_depth;

    union() {
        // Core cylinder
        cylinder(h=length, d=core_d, $fn=64);

        // Helical thread
        steps_per_turn = 32;
        step_height = pitch / steps_per_turn;

        for (z = [0 : step_height : length]) {
            angle = (z / pitch) * 360;
            rotate([0, 0, angle])
            translate([0, 0, z])
            rotate([0, 0, 30])  // Align with hex
            cylinder(h=step_height*1.1, d1=major_d, d2=major_d, $fn=64);
        }
    }
}

module hplc_male_connector() {
    union() {
        // 1. Hex head (for wrench)
        hex_prism(hex_across_flats, hex_height);

        // 2. Cylindrical body
        translate([0, 0, hex_height])
        cylinder(h=body_length, d=body_diameter, $fn=64);

        // 3. Transition/shoulder
        translate([0, 0, hex_height + body_length])
        cylinder(h=stem_length, d1=body_diameter, d2=thread_major_d, $fn=64);

        // 4. Threaded section
        translate([0, 0, hex_height + body_length + stem_length])
        unf_external_thread(thread_major_d, thread_pitch, thread_length);

        // 5. Through bore for tubing
        translate([0, 0, -0.1])
        cylinder(h=total_length+0.2, d=stem_diameter*0.8, $fn=32);
    }
}

// ===== RENDER =====

// Main connector
hplc_male_connector();

// Optional: show cross-section
// difference() {
//     hplc_male_connector();
//     translate([-20, 0, -1])
//     cube([20, 40, 100]);
// }
