// Parametric Hex Wrench Tool for Tight Spaces
// This tool has an opening on one side to allow insertion into tight spaces

// Parameters
hex_size = 16.5;
wrench_depth = 8;     // Thickness of the working part of the wrench (mm)
opening_size = 80;    // Angle to open up one side (degrees)
wall_thickness = 7.5; // Wall thickness of the wrench body (mm)

// to deal with z fighting 
poop = 0.1;

// Main wrench body
module hex_wrench(hex_size_param = hex_size) {
    hex_radius_param = hex_size_param / 2;
    outer_radius_param = hex_radius_param + wall_thickness;
    
    difference() {
        // Outer cylinder
        cylinder(h = wrench_depth, r = outer_radius_param, $fn = 60);
        
        // Inner hex cutout
        translate([0,0,-poop])
        cylinder(h = wrench_depth + 2*poop, r = hex_radius_param, $fn = 6);
        
        // Opening cutout with offset starting point and angle
        rotate([0, 0, -opening_size/2]) // Offset starting point to the corner of the hex
        translate([0, 0, -0.5])
        linear_extrude(height = wrench_depth + 1)
        polygon([
            [0, 0],
            [outer_radius_param * 2, 0],
            [outer_radius_param * 2 * cos(opening_size), outer_radius_param * 2 * sin(opening_size)],
            [0, 0]
        ]);
    }
}

// Add grip pattern to the main wrench body
module wrench_with_grip(hex_size_param = hex_size) {
    hex_radius_param = hex_size_param / 2;
    outer_radius_param = hex_radius_param + wall_thickness;
    
    union() {
        // Main wrench body
        hex_wrench(hex_size_param);
        
        // Subtle grip pattern on the outer surface
        for (i = [0:5]) {
            angle = i * 60;
            // Skip protrusions that would be in the opening cutout area
            if (angle < 360 - opening_size/2 && angle > opening_size/2) {
                rotate([0, 0, angle])
                translate([outer_radius_param, 0, 0])
                cylinder(h = wrench_depth, r = 1.5, $fn = 6);
            }
        }
    }
}

// Render the complete wrench
wrench_with_grip(hex_size);

// Echo parameters for verification
echo("Hex Wrench Parameters:");
echo("Hex size (face to face):", hex_size, "mm");
echo("Wrench depth:", wrench_depth, "mm");
echo("Opening angle:", opening_size, "degrees");
echo("Wall thickness:", wall_thickness, "mm");
