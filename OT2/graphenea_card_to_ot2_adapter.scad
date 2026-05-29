//substrate
max_height = 14.35;
max_length = 127.76;
max_width = 85.48;
bezel_width = 3;

// graphenea card
pcb_thickness = 1.57;
graphenea_card_width = 73.8;
graphenea_card_length = 90;

module workpiece (width, depth, height) {
  cube([width, depth, height]);
}

module grapheneaCardOutline() {
  module cardCutout() {
    translate([0, 5, 0]) {
      union() {
        cube([5, 63.9, pcb_thickness]);
        translate([0, 0, pcb_thickness]) {
          rotate(a=180, [1, 0, 0]){
            intersection() {
              cube([5, 5, pcb_thickness]);
              cylinder(h=pcb_thickness, r=5);
            }
          }
        }
      }
    }
  }

  difference() {
    cube([graphenea_card_width, graphenea_card_length, pcb_thickness]);
    translate([0, 21.1, 0]) {
      cardCutout();
    }
    translate([graphenea_card_width, 21.1, pcb_thickness]) {
      rotate(180, [0, 1, 0]) {
        cardCutout();
      }
    }
  }
}

module bezel(width, height, length) {
  translate([0, 0, height]) {
    difference() {
      cube([width, length, 10]);
      polyhedron(points=[[0, 0, 0],
                         [width, 0, 0],
                         [width, length, 0],
                         [0, length, 0],
                         [width, 0, 2],
                         [width, length, 2]],
                 faces=[
                        [0, 1, 2, 3], // bottom
                        [0, 1, 4],     // front
                        [4, 5],        // top
                        [1, 2, 5, 4], // right
                        [2, 3, 5],    // back
                        [0, 3, 5, 4]  // left
                        ]);
    }
  }
}

module grapheneaCardOT2Adapter() {
  difference() {
    union() {
      difference() {
        workpiece(max_width, max_length,max_height);
        translate([(max_width-graphenea_card_width)/2,
                   (max_length-graphenea_card_length)/2,
                   max_height-pcb_thickness]) {
          grapheneaCardOutline();
        }
      }

      translate([max_width/2,
                 (max_length - ((max_length-graphenea_card_length)/2)) - 10,
                 0]) {
        cylinder(h=max_height, r=1);
      }

      translate([max_width/2,
                 (max_length - ((max_length-graphenea_card_length)/2)) - 20,
                 0]) {
        cylinder(h=max_height, r=1);
      }
    }

    bezel(bezel_width, max_height-10, max_length);

    translate([max_width, max_length, 0]) {
      rotate(180, [0,0,1]) {
        bezel(bezel_width, max_height-10, max_length);
      }
    }

    translate([max_width, 0, 0]) {
      rotate(90, [0, 0, 1]) {
        bezel(bezel_width, max_height-10, max_width);
      }
    }

    translate([0, max_length, 0]) {
      rotate(270, [0,0,1]) {
        bezel(bezel_width, max_height-10, max_width);
      }
    }
  }
}


// Render complete adapter
grapheneaCardOT2Adapter();
