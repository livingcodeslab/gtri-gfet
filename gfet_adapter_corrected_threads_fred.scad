module plug(height=11.737, plugRadius=4, bottomChannelRadius=0.79375, //bottomChannelRadius=0.4572,
            topChannelRadius=0.79375) {
  difference() {
    cylinder(h=height, r1=plugRadius, r2=plugRadius, center=false);
    cylinder(h=height, r1=bottomChannelRadius, r2=topChannelRadius,
             center=false);
  }
}

module barb(height=9, numberOfBarbs=1, bodyRadius=1, barbRadius=1.1938, channelRadius=0.79375) {
  barbHeight = floor(height/(numberOfBarbs + 1));
  bodyHeight = height-(numberOfBarbs * barbHeight);
  difference() {
    union() {// solid part of the barb
      cylinder(h=bodyHeight, r1=bodyRadius, r2=bodyRadius, center=0);
      translate([0, 0, bodyHeight]) {
        for(i = [0: 1: numberOfBarbs-1]) {
          translate([0, 0, i*barbHeight]) {
            cylinder(h=barbHeight, r1=barbRadius, r2=bodyRadius, center=false);
          }
        }
      }
    }
    cylinder(// channel
             h=height, r1=channelRadius, r2=channelRadius, center=false);
  }
}

module barbedPlug() {
  union() {
    plugHeight = 11.737;
    plug(height=plugHeight);
    translate([0, 0, plugHeight]) {
      barb();
    }
  }
}

module flowcell() {
  union() {
    difference() {
      import("/home/frederick/livingcodeslab/guided-dna-synthesis-project/gtri-gfet/gfet_adapter_corrected_threaded.stl");

      translate([0, 25.731, 0]) {//trim from height of main body of flowcell
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

    translate([13.97, 16.2472, 8.95618]) {//plug hole 1 with barbed plug
      rotate([-90, 0, 0]) {
        barbedPlug();
      }
    }
    translate([13.97, 16.2472, 14.99+4]) {//plug hole 2 with barbed plug
      rotate([-90, 0, 0]) {
        barbedPlug();
      }
    }
  }
}

flowcell(); // comment this out and remove comment below to see cut-out view
// difference() {flowcell();cube([13.97, 19+6.731+2.5232+9, 27.94]);} //cut-out view
