difference() {
  import("/home/frederick/livingcodeslab/guided-dna-synthesis-project/gtri-gfet/gfet_adapter_corrected_threaded.stl");

  translate([0, 25.731, 0]) {
    difference() {
      cube([27.94,0.2532,27.94]);
      translate([13.97, 0.2532, 13.97]) {
        rotate(a=90, [1,0,0]) {
          cylinder(0.2532, 10.43, 10.43);
        }
      }
    }
  }
}
