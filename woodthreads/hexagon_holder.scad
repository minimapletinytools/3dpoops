// Hexagon Nut Table Saw Jig
// Parameters for the jig

// Face to face diameter of hexagon
outer_diameter = 50.8; // 2 inches = 50.8mm
// Diameter of the center hole
inner_hole_diameter = 22.25; // 7/8 inches = 22.225mm, minus 0.3mm = 21.925mm, rounded to 21.9mm 

// Thickness of the base plate
jig_thickness = 10; 
// Height of the dowel pin
dowel_height = 3; 


minkowski_radius = 2;

// Calculated dimensions
jig_diameter = 180;
jig_handle_diameter = 60;
jig_handle_height = 25;

poop = 0.01;

module hexagon_holder_jig() {

    
    // Angled fence for hexagon cutting
    // The fence is positioned to guide the workpiece at the correct angle
    fence_thickness = 30;
    fence_length = 200;
    corner_to_corner = outer_diameter * 1.1547; // cos(30°) = 0.866, so 1/cos(30°) = 1.1547

    difference()
    {
        union()
        {
            // main base circle
            cylinder(h = jig_thickness, d = jig_diameter, $fn = 50);

            // handle
            translate([0, 0, jig_thickness])
            {
                cylinder(h = jig_handle_height, d = jig_handle_diameter, $fn = 50);
                // Add grip holes around the handle
                grip_circle_count = 6;
                grip_circle_radius = 10; // 8mm diameter
                grip_ring_radius = jig_handle_diameter/2 - 5; // slightly inset from edge
                grip_circle_z = jig_handle_height - 4;
                for (i = [0:grip_circle_count-1]) {
                    angle = 360/grip_circle_count * i;
                    x = grip_ring_radius * cos(angle);
                    y = grip_ring_radius * sin(angle);
                    translate([x, y, grip_circle_z])
                        rotate([0,0,0])
                            cylinder(h = 4, d = grip_circle_radius*2, $fn = 30); // through hole
                }
            }
        }


        // Dowel pin
        translate([0, 0, -poop]) 
        {
            cylinder(h = dowel_height+poop, d = inner_hole_diameter, $fn = 50);
        }
        
        // hexagon face length
        face_length = outer_diameter * 1.1547; // cos(30°) = 0.866, so 1/cos(30°) = 1.1547

        
        // Position fence by rotating 120° and translating from dowel center
        // to the corner-to-corner distance at -120° angle
        
        translate([0, 0, -poop])
        {
            intersection()
            {
                    
                        rotate([0, 0, -120])
                            // now translate at a -120 degree angle by corner_to_corner/2
                            translate([corner_to_corner/2, 0,0])
                                rotate([0, 0, -120])
                                    translate([-50,0,0])
                                        cube([130, 10, dowel_height+poop]);

                    
                    cylinder(h = dowel_height, d = jig_diameter, $fn = 50);
            }
        }
    }
    
}

module insets()
{

    cylinder(h = dowel_height, d = inner_hole_diameter, $fn = 50);

    translate([0, 20, 0])
        cube([130, 10, dowel_height]);

}

// Render the jig
//hexagon_holder_jig();

insets();