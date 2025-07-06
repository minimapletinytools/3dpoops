// Parametric Hex Wrench Tool for Tight Spaces
// This tool has an opening on one side to allow insertion into tight spaces

// Parameters
hex_size = 10;        // Face to face distance of hex nut (mm)
wrench_depth = 8;     // Thickness of the working part of the wrench (mm)
opening_size = 80;    // Angle to open up one side (degrees)
outer_diameter = 25;  // Outer diameter of the wrench body (mm)

// Calculated parameters
hex_radius = hex_size / 2;
outer_radius = outer_diameter / 2;
wall_thickness = outer_radius - hex_radius;

// to deal with z fighting 
poop = 0.1;

// Main wrench body
module hex_wrench() {
    difference() {
        // Outer cylinder
        cylinder(h = wrench_depth, r = outer_radius, $fn = 60);
        
        // Inner hex cutout
        translate([0,0,-poop])
        cylinder(h = wrench_depth + 2*poop, r = hex_radius, $fn = 6);
        
        // Opening cutout with offset starting point and angle
        rotate([0, 0, -opening_size/2]) // Offset starting point to the corner of the hex
        translate([0, 0, -0.5])
        linear_extrude(height = wrench_depth + 1)
        polygon([
            [0, 0],
            [outer_radius * 2, 0],
            [outer_radius * 2 * cos(opening_size), outer_radius * 2 * sin(opening_size)],
            [0, 0]
        ]);
    }
}

// Add grip pattern to the main wrench body
module wrench_with_grip() {
    union() {
        // Main wrench body
        hex_wrench();
        
        // Subtle grip pattern on the outer surface
        for (i = [0:5]) {
            angle = i * 60;
            // Skip protrusions that would be in the opening cutout area
            if (angle < 360 - opening_size/2 && angle > opening_size/2) {
                rotate([0, 0, angle])
                translate([outer_radius, 0, 0])
                cylinder(h = wrench_depth, r = 1.5, $fn = 6);
            }
        }
    }
}

// Render the complete wrench
wrench_with_grip();

// Echo parameters for verification
echo("Hex Wrench Parameters:");
echo("Hex size (face to face):", hex_size, "mm");
echo("Wrench depth:", wrench_depth, "mm");
echo("Opening angle:", opening_size, "degrees");
echo("Outer diameter:", outer_diameter, "mm");
echo("Wall thickness:", wall_thickness, "mm");
