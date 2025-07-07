// Hexagon Nut Table Saw Jig
// Parameters for the jig

jig_thickness = 12; // Thickness of the base plate
dowel_height = 20; // Height of the dowel pin
outer_diameter = 25; // Face to face diameter of hexagon
inner_hole_diameter = 8; // Diameter of the center hole

// Calculated dimensions
jig_width = outer_diameter + 25; // Width of the jig base
jig_length = 300; // Length of the jig base
dowel_offset_from_top = 76.2; // 3 inches in mm
dowel_offset_from_left = outer_diameter / 2; // Center of hexagon from left edge

poop = 0.01;

module hexagon_jig() {

    
    // Angled fence for hexagon cutting
    // The fence is positioned to guide the workpiece at the correct angle
    fence_thickness = 30;
    fence_length = 100;
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
        translate([dowel_offset_from_top, dowel_offset_from_left, jig_thickness-3])
            rotate([0, 0, 60])
                // now translate at a -120 degree angle by corner_to_corner/2
                translate([corner_to_corner/2, 0,0])
                    rotate([0, 0, -120])
                        translate([-jig_width, 0, 0])
                            cube([jig_width*2, fence_thickness, 3+poop]);

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
                            cube([jig_width, fence_thickness, dowel_height+jig_thickness]);

            /* second fence
            translate([dowel_offset_from_top, dowel_offset_from_left, 0])
                rotate([0, 0, 60])
                    // now translate at a -120 degree angle by corner_to_corner/2
                    translate([corner_to_corner/2, 0,0])
                        rotate([0, 0, -120])
                            translate([-jig_width, 0, 0])
                                cube([jig_width*2, fence_thickness, dowel_height+jig_thickness]);
            */
        }
        

        // crop off stuff overhanging the jig
        translate([0,-jig_width,-poop])
            cube([jig_length, jig_width, 100]);
        translate([0,jig_width,-poop])
            cube([jig_length, jig_width, 100]);
        
        
    }

}
// Render the jig
hexagon_jig();
