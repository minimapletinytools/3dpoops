// Bader B3 Small Wheels for 2x72 Knife Grinder
// Wheel with R4 bearings on each side for free spinning

// Parameters
bearing_outer_diameter = 5/8 * 25.4;  // Convert inches to mm
bearing_inner_diameter = 1/4 * 25.4;  // Convert inches to mm  
bearing_width = 3/16 * 25.4;          // Convert inches to mm

wheel_width = 2 * 25.4;               // Convert inches to mm
wheel_diameter = 1 * 25.4;            // Convert inches to mm
wheel_inner_diameter = bearing_inner_diameter + 1; // mm

outer_material_thickness = 1/16 * 25.4; // Convert inches to mm

// Rendering parameters
resolution = 128;                      // Cylinder resolution
poop = 0.1;                           // Clearance for z-fighting

// Assertion to check design constraints
assert(bearing_outer_diameter < wheel_diameter - outer_material_thickness, 
       "Error: Bearing outer diameter must be smaller than wheel diameter minus material thickness");

echo(str("Bearing outer diameter: ", bearing_outer_diameter, "mm"));
echo(str("Wheel diameter minus material thickness: ", wheel_diameter - outer_material_thickness, "mm"));

// Main wheel with bearing cutouts
module main_wheel() {
    difference() {
        // Main cylinder
        cylinder(h = wheel_width, 
                d = wheel_diameter - outer_material_thickness * 2, 
                center = true, $fn = resolution);
        
        // Center hole for rod
        cylinder(h = wheel_width + 1, 
                d = wheel_inner_diameter, 
                center = true, $fn = resolution);
        
        // Bearing cutouts on each side
        // Left side bearing recess
        translate([0, 0, wheel_width/2 - bearing_width/2])
            cylinder(h = bearing_width + poop, 
                    d = bearing_outer_diameter + poop, // Small clearance
                    center = true, $fn = resolution);
        
        // Right side bearing recess  
        translate([0, 0, -wheel_width/2 + bearing_width/2])
            cylinder(h = bearing_width + poop, 
                    d = bearing_outer_diameter + poop, // Small clearance
                    center = true, $fn = resolution);
    }
}

// Outer shell (hollow cylinder)
module outer_shell() {
    difference() {
        // Outer cylinder
        cylinder(h = wheel_width, 
                d = wheel_diameter, 
                center = true, $fn = resolution);
        
        // Inner cutout
        cylinder(h = wheel_width + 1, 
                d = wheel_diameter - outer_material_thickness * 2, 
                center = true, $fn = resolution);
    }
}

// Render parts
main_wheel();

// Outer shell - comment out this line to export main wheel separately
outer_shell();
