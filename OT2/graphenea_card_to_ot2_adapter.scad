//substrate

max_thickness = 14.35;
max_length = 127.76;
max_width = 85.48;
bezel_width = 3;


// graphenea card: design dimensions

graphenea_card_max_width = 73.80;
graphenea_card_max_length = 90.00;
graphenea_card_small_width = 63.80;
graphenea_card_small_length = 21.10;
screw_holes_radius = 2.00;
pcb_thickness = 1.63;

// graphenea card: cut-out dimensions

tolerance=0.10;
cutout_max_width = graphenea_card_max_width + tolerance;
cutout_small_width = graphenea_card_small_width + (tolerance / 2);
cutout_max_length = graphenea_card_max_length + tolerance;
cutout_small_length = graphenea_card_small_length + (tolerance / 2);
prongs_radius = screw_holes_radius - (tolerance / 4);
curve_radius = 5;
solder_grooves_depth = 3;


module modWorkpiece(width, length, thickness) {
  cube([width, length, thickness]);
}


module modCardLargeCube(width, length, thickness) {
  cube([width, length, thickness]);
}


module modCardSmallCube(large_width, small_width, length, thickness) {
  translate([(large_width - small_width)/2,
             0,
             0]) {
    cube([small_width, length, thickness]);
  }
}


module modCurvedEdgeLeft(height, radius, x_offset, y_offset) {
  translate([x_offset, y_offset+radius, 0]) {// curved-edge offset
    difference() {
      translate([0,-radius,0]) {//cube offset
        cube([radius, radius, height]);
      }
      cylinder(h=height, r=radius, center=false);
    }
  }
}


module modCurvedEdgeRight(height, radius, x_offset, y_offset) {
  translate([x_offset, y_offset+radius, 0]) {//curved-edge offset
    difference() {
      translate([-radius,-radius,0]) {//cube offset
        cube([radius, radius, height]);
      }
      cylinder(h=height, r=radius, center=false);
    }
    
  }
}


module modProng(x, y, thickness, radius) {
  translate([x, y, 0]) {
    cylinder(h=thickness,
             r=radius,
             center=false);
  }
}


module modCardCutout(max_width, max_length, small_width, small_length, thickness, curve_radius, prongs_radius, tolerance = 0.10) {
  difference() {
    union() {
      modCardLargeCube(max_width,
                       small_length,
                       thickness);


      modCardSmallCube(max_width,
                       small_width,
                       max_length,
                       thickness);

      modCurvedEdgeLeft(thickness,
                        curve_radius,
                        ((max_width-small_width)/2)-curve_radius,
                        small_length);

      modCurvedEdgeRight(thickness,
                         curve_radius,
                         small_width+((max_width-small_width)/2)+curve_radius,
                         small_length);
    }
    modProng(max_width/2,
             max_length-(10 + (tolerance/2)),
             thickness,
             prongs_radius);
    modProng(max_width/2,
             max_length-(20 + (tolerance/2)),
             thickness,
             prongs_radius);
  }
}


module modSolderJointsGrooves(max_width, max_length, thickness,
                              dist_from_front, dist_from_back,
                              dist_from_sides,
                              groove_width=15) {
  groove_length = max_length-(dist_from_front+dist_from_back);
  difference() {
    cube([max_width, max_length, thickness]);
    translate([0, dist_from_front, 0]) {
      cube([dist_from_sides, groove_length, thickness]);
    }
    translate([max_width-dist_from_sides, dist_from_front, 0]) {
      cube([dist_from_sides, groove_length, thickness]);
    }
    translate([dist_from_sides+groove_width, dist_from_front, 0]) {
      cube([max_width-(2*(dist_from_sides+groove_width)),
            groove_length,
            thickness]);
    }
    translate([0, max_length-dist_from_back, 0]) {
      cube([max_width, dist_from_back, thickness]);
    }
  }
}


module modFullCutout(grooves_depth) {// pass in these values
  translate([0, 0, grooves_depth]) {
    children(0);
  }
  children(1);
}


module modBezel(width, height, length) {
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


module modFullBezel(width, length,
                    bezel_width, bezel_thickness) {
  union() {
    modBezel(bezel_width, bezel_thickness, length);

    translate([width, length, 0]) {
      rotate(180, [0,0,1]) {
        modBezel(bezel_width, bezel_thickness, length);
      }
    }

    translate([width, 0, 0]) {
      rotate(90, [0, 0, 1]) {
        modBezel(bezel_width, bezel_thickness, width);
      }
    }

    translate([0, length, 0]) {
      rotate(270, [0,0,1]) {
        modBezel(bezel_width, bezel_thickness, width);
      }
    }
  }
}


module modGrapheneaCardOT2Adapter() {
  difference() {
    modWorkpiece(max_width, max_length, max_thickness);

    translate([(max_width-cutout_max_width)/2,
               (max_length-cutout_max_length)/2,
               (max_thickness-(pcb_thickness+solder_grooves_depth))]) {
      modFullCutout(solder_grooves_depth) {
        modCardCutout(graphenea_card_max_width,
                      graphenea_card_max_length,
                      graphenea_card_small_width,
                      graphenea_card_small_length,
                      pcb_thickness+0.01,//add a tiny amount to fix render
                      prongs_radius,
                      tolerance=tolerance);
        modSolderJointsGrooves(cutout_max_width, cutout_max_length,
                               solder_grooves_depth,
                               20+(tolerance/2), 7.5+(tolerance/2),
                               10+(tolerance/2),
                               17);
      }
    }

    modFullBezel(max_width, max_length, bezel_width, max_thickness-10);
  }
}


modGrapheneaCardOT2Adapter();
