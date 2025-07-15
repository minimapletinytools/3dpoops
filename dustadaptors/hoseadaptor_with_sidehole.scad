// Parametric Dust Hose Adapter
// Creates a dust hose adapter with conical transition between different diameters
// 吕 minimaple 

// ===== PARAMETERS =====

// Top section parameters
inner_diameter_TOP = 35;    // Inner diameter of top section
outer_diameter_TOP = 40;    // Outer diameter of top section
top_length = 30;            // Length of top section

// Bottom section parameters
inner_diameter_BOT = 25;    // Inner diameter of bottom section
outer_diameter_BOT = 30;    // Outer diameter of bottom section
bot_length = 25;            // Length of bottom section

// Mid section parameters
mid_length = 20;            // Length of conical mid section

// Side port parameters
inner_diameter_SIDE = 20;   // Inner diameter of side port
outer_diameter_SIDE = 25;   // Outer diameter of side port
side_length = 45;           // Length of side port
side_angle = 45;            // Angle at which side port sticks out (degrees)

// General parameters
wall_thickness = 2;         // Wall thickness (calculated from inner/outer diameters)
poop = 0.1;                 // Small overlap for boolean operations

// ===== DUST HOSE ADAPTER =====

module dust_hose_adapter() {
    difference() {
        union() {
            // Top cylinder
            translate([0, 0, 0]) {
                cylinder(h = top_length, d = outer_diameter_TOP, center = false);
            }
            
            // Conical mid section
            translate([0, 0, top_length]) {
                cylinder(h = mid_length, d1 = outer_diameter_TOP, d2 = outer_diameter_BOT, center = false);
            }
            
            // Bottom cylinder
            translate([0, 0, top_length + mid_length]) {
                cylinder(h = bot_length, d = outer_diameter_BOT, center = false);
            }
            
            // Side port
            translate([(inner_diameter_TOP + inner_diameter_BOT)/4, 0, top_length + mid_length/2]) {
                rotate([0, side_angle, 0]) {
                    translate([0, 0, -side_length/2]) {
                        cylinder(h = side_length, d = outer_diameter_SIDE, center = false);
                    }
                }
            }
        }
        
        // Cut out inner passages
        // Top inner passage
        translate([0, 0, -poop]) {
            cylinder(h = top_length + poop, d = inner_diameter_TOP, center = false);
        }
        
        // Conical inner passage
        translate([0, 0, top_length - poop]) {
            cylinder(h = mid_length + 2*poop, d1 = inner_diameter_TOP, d2 = inner_diameter_BOT, center = false);
        }
        
        // Bottom inner passage
        translate([0, 0, top_length + mid_length - poop]) {
            cylinder(h = bot_length + poop*2, d = inner_diameter_BOT, center = false);
        }
        
        // Side port inner passage
        translate([(inner_diameter_TOP + inner_diameter_BOT)/4, 0, top_length + mid_length/2]) {
            rotate([0, side_angle, 0]) {
                translate([0, 0, -side_length/2 - poop]) {
                    cylinder(h = side_length + 2*poop, d = inner_diameter_SIDE, center = false);
                }
            }
        }
    }
}

// ===== RENDERING =====

dust_hose_adapter(); 