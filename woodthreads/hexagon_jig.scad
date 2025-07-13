// Hexagon Nut Table Saw Jig
// Parameters for the jig

// Face to face diameter of hexagon
outer_diameter = 50.8; // 2 inches = 50.8mm
// Diameter of the center hole
inner_hole_diameter = 21.9; // 7/8 inches = 22.225mm, minus 0.3mm = 21.925mm, rounded to 21.9mm 

// Thickness of the base plate
jig_thickness = 8; 
// Height of the dowel pin
dowel_height = 20; 

// for removable fence
recess_depth = 3;


// Calculated dimensions
jig_width = outer_diameter + 35; // Width of the jig base
jig_length = 250; // Length of the jig base
dowel_offset_from_top = 50; // 3 inches in mm
dowel_offset_from_left = outer_diameter / 2; // Center of hexagon from left edge

poop = 0.01;

module hexagon_jig() {

    
    // Angled fence for hexagon cutting
    // The fence is positioned to guide the workpiece at the correct angle
    fence_thickness = 30;
    fence_length = 200;
    corner_to_corner = outer_diameter * 1.1547; // cos(30°) = 0.866, so 1/cos(30°) = 1.1547


    difference() {
        // Main base plate
        cube([jig_length, jig_width, jig_thickness]);
        
        // Dowel hole
        //translate([dowel_offset_from_top, dowel_offset_from_left, 0]) {
        //    cylinder(h = jig_thickness, d = inner_hole_diameter, $fn = 50);
        //}


        // create recess for the rest of the hexagon
        /*
        translate([dowel_offset_from_top, dowel_offset_from_left, jig_thickness-3])
            rotate([0, 0, 90])
                // now translate at a -120 degree angle by corner_to_corner/2
                translate([0,corner_to_corner/2, 0])
                    rotate([0, 0, -30])
                        cube([jig_width, fence_thickness, 3+poop]);
        */

        // create recess for second fence
        /*
        translate([dowel_offset_from_top, dowel_offset_from_left, jig_thickness-recess_depth])
            rotate([0, 0, 60])
                // now translate at a -120 degree angle by corner_to_corner/2
                translate([corner_to_corner/2, 0,0])
                    rotate([0, 0, -120])
                        translate([-jig_width, 0, 0])
                            cube([jig_width*2, fence_thickness, recess_depth+poop]);
        */

    }


    
    // Dowel pin
    translate([dowel_offset_from_top, dowel_offset_from_left, jig_thickness]) {
        cylinder(h = dowel_height, d = inner_hole_diameter, $fn = 50);
    }
    
    // hexagon face length
    face_length = outer_diameter * 1.1547; // cos(30°) = 0.866, so 1/cos(30°) = 1.1547

    
    // Position fence by rotating 120° and translating from dowel center
    // to the corner-to-corner distance at -120° angle
    
    
    
    difference(){
        union(){
            translate([dowel_offset_from_top, dowel_offset_from_left, 0])
                rotate([0, 0, -120])
                    // now translate at a -120 degree angle by corner_to_corner/2
                    translate([corner_to_corner/2, 0,0])
                        rotate([0, 0, -120])
                            cube([jig_width*2, fence_thickness, dowel_height+jig_thickness]);

            //second fence
            /*
            translate([dowel_offset_from_top, dowel_offset_from_left, jig_thickness-recess_depth])
                rotate([0, 0, 60])
                    // now translate at a -120 degree angle by corner_to_corner/2
                    translate([corner_to_corner/2, 0,0])
                        rotate([0, 0, -120])
                            translate([-jig_width, 0, 0])
                                cube([jig_width*2, fence_thickness, dowel_height+recess_depth]);
            */
        }
        

        // crop off stuff overhanging the jig
        translate([-poop,-jig_width*2,-poop])
            cube([jig_length+poop*2, jig_width*2, 100]);
        translate([-poop,jig_width,-poop])
            cube([jig_length+poop*2, jig_width*2, 100]);
        // crop off +x and -x sides
        translate([-jig_width,-poop,-poop])  
            cube([jig_width, jig_width*3 + poop*2, 100]);

        
    }

    // expand the platform for safety
    translate([jig_length/3 ,-jig_width*1.3,-poop])
        cube([jig_length*2/3, jig_width*1.3, jig_thickness]);

}
// Render the jig
hexagon_jig();
