// 3D Printable Spherical Shells
// Creates concentric spherical shells that can be printed in place

// Parameters
toy_thickness = 20;        // Thickness of the final toy
gap_thickness = 0.2;         // Thickness of gaps between shells
starting_radius = 10;      // Outer radius of the largest shell
ending_radius = 50;        // Inner radius of the smallest shell
number_shells = 5;         // Number of concentric shells

sphere_detail = 100;

// Calculate shell thickness based on available space
shell_thickness = (starting_radius - ending_radius - (gap_thickness * (number_shells - 1))) / number_shells;

// Main module for creating spherical shells
module spherical_shells() {
    // Create the main sphere at starting_radius
    difference() {
        // Outer sphere
        sphere(r = ending_radius, $fn = sphere_detail);
        
        
        
        shell_thickness = (ending_radius - starting_radius) / number_shells;

        // Subtract inner shells to create gaps
        for (i = [1 : number_shells-1]) {
            gap_radius = starting_radius + i * shell_thickness;
            difference(){
                sphere(r = gap_radius + gap_thickness/2, $fn = sphere_detail);
                sphere(r = gap_radius - gap_thickness/2, $fn = sphere_detail);
            }
        }
        
        // Symmetrically slice off top and bottom to achieve toy_thickness
        // Calculate how much to cut from top and bottom
        cut_height = toy_thickness / 2;
        
        // Cut off top
        translate([0, 0, cut_height + ending_radius])
            cube([ending_radius * 2, ending_radius * 2, ending_radius * 2], center = true);
        
        // Cut off bottom
        translate([0, 0, -cut_height - ending_radius])
            cube([ending_radius * 2, ending_radius * 2, ending_radius * 2], center = true);
            
    }
}

// Render the spherical shells
spherical_shells();

// Echo parameters for verification
echo("Parameters:");
echo("Toy thickness:", toy_thickness, "mm");
echo("Gap thickness:", gap_thickness, "mm");
echo("Starting radius:", starting_radius, "mm");
echo("Ending radius:", ending_radius, "mm");
echo("Number of shells:", number_shells);
echo("Calculated shell thickness:", shell_thickness, "mm");
echo("Final height:", toy_thickness, "mm");
