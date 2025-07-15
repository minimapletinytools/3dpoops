// Parametric Dust Hose Adapter with Tapered Fittings
// Creates a dust hose adapter with tapered sections and conical transition

// ===== PARAMETERS =====

// Top section parameters
top_taper_diameter_tip = 63.5;     // Diameter at the tip of top section
top_taper_diameter_end = 63;     // Diameter at the end of top section
top_length = 40;                 // Length of top section
top_is_inside_fitting = true;    // If true, then diameter is inner diameter + taper inside (reducing); else diameter is outer diameter + taper outside (increasing)
top_wall_thickness = 2;          // Wall thickness for top section

// Bottom section parameters
bot_taper_diameter_tip = 105.4;     // Diameter at the tip of bottom section (connects to mid section)
bot_taper_diameter_end = 105.5;     // Diameter at the end of bottom section (free end)
bot_length = 40;                 // Length of bottom section
bot_is_inside_fitting = false;    // If true, taper inside (reducing), else outside (increasing)
bot_wall_thickness = 2;          // Wall thickness for bottom section

// Mid section parameters
mid_length = 40;                 // Length of conical mid section

// Side port parameters
side_taper_diameter_tip = 37;    // Diameter at the tip of side port
side_taper_diameter_end = 38;    // Diameter at the end of side port
side_length = 70;                // Length of side port
side_angle = -45;                 // Angle at which side port sticks out (degrees)
side_is_inside_fitting = false;   // If true, taper inside (reducing), else outside (increasing)
side_wall_thickness = 2;         // Wall thickness for side port

// General parameters
poop = 0.1;                      // Small overlap for boolean operations

// ===== HELPER FUNCTIONS =====

// Generate the additive geometry (outer shell) for tapered cylinder
module tapered_cylinder_additive(length, diameter_A, diameter_B, wall_thickness, is_inside_fitting) {
    if (is_inside_fitting) {
        // Diameters are inside diameters, so add wall thickness for outer shell
        cylinder(h = length, d1 = diameter_A + 2*wall_thickness, d2 = diameter_B + 2*wall_thickness, center = false);
    } else {
        // Diameters are outside diameters, so use as-is for outer shell
        cylinder(h = length, d1 = diameter_A, d2 = diameter_B, center = false);
    }
}

// Generate the subtractive geometry (inner bore) for tapered cylinder
module tapered_cylinder_subtractive(length, diameter_A, diameter_B, wall_thickness, is_inside_fitting) {
    if (is_inside_fitting) {
        // Diameters are inside diameters, so use as-is for inner bore
        translate([0, 0, -poop]) {
            cylinder(h = length + poop*2, d1 = diameter_A, d2 = diameter_B, center = false);
        }
    } else {
        // Diameters are outside diameters, so subtract wall thickness for inner bore
        translate([0, 0, -poop]) {
            cylinder(h = length + poop*2, d1 = diameter_A - 2*wall_thickness, d2 = diameter_B - 2*wall_thickness, center = false);
        }
    }
}

// Generate a tapered cylinder with specified parameters
module tapered_cylinder(length, diameter_A, diameter_B, wall_thickness, is_inside_fitting) {
    difference() {
        tapered_cylinder_additive(length, diameter_A, diameter_B, wall_thickness, is_inside_fitting);
        tapered_cylinder_subtractive(length, diameter_A, diameter_B, wall_thickness, is_inside_fitting);
    }
}

// ===== DUST HOSE ADAPTER =====

module dust_hose_adapter() {
    // Assertions to ensure proper diameter ordering for each section
    if (top_is_inside_fitting) {
        assert(top_taper_diameter_tip > top_taper_diameter_end, "Top section: For inside fitting, tip diameter must be larger than end diameter");
    } else {
        assert(top_taper_diameter_tip < top_taper_diameter_end, "Top section: For outside fitting, tip diameter must be smaller than end diameter");
    }
    
    if (bot_is_inside_fitting) {
        assert(bot_taper_diameter_tip > bot_taper_diameter_end, "Bottom section: For inside fitting, tip diameter must be larger than end diameter");
    } else {
        assert(bot_taper_diameter_tip < bot_taper_diameter_end, "Bottom section: For outside fitting, tip diameter must be smaller than end diameter");
    }
    
    if (side_is_inside_fitting) {
        assert(side_taper_diameter_tip > side_taper_diameter_end, "Side section: For inside fitting, tip diameter must be larger than end diameter");
    } else {
        assert(side_taper_diameter_tip < side_taper_diameter_end, "Side section: For outside fitting, tip diameter must be smaller than end diameter");
    }

    top_end_outer_diameter = top_is_inside_fitting ? top_taper_diameter_end + 2*top_wall_thickness : top_taper_diameter_end;
    bot_end_outer_diameter = bot_is_inside_fitting ? bot_taper_diameter_end + 2*bot_wall_thickness : bot_taper_diameter_end;

    top_end_inner_diameter = top_is_inside_fitting ? top_taper_diameter_end : top_taper_diameter_end - 2*top_wall_thickness;
    bot_end_inner_diameter = bot_is_inside_fitting ? bot_taper_diameter_end : bot_taper_diameter_end - 2*bot_wall_thickness;
    
    difference() {
        union() {
            // Top tapered section (additive part only)
            translate([0, 0, 0]) {
                tapered_cylinder_additive(
                    top_length, 
                    top_taper_diameter_tip, 
                    top_taper_diameter_end, 
                    top_wall_thickness, 
                    top_is_inside_fitting
                );
            }
            
            // Conical mid section
            translate([0, 0, top_length]) {
                cylinder(h = mid_length, d1 = top_end_outer_diameter, d2 = bot_end_outer_diameter, center = false);
            }
            
            // Bottom tapered section (additive part only)
            translate([0, 0, top_length + mid_length]) {
                tapered_cylinder_additive(
                    bot_length, 
                    bot_taper_diameter_end, 
                    bot_taper_diameter_tip, 
                    bot_wall_thickness, 
                    bot_is_inside_fitting
                );
            }
            
            // Side port tapered section (additive part only)
            translate([(top_end_inner_diameter + bot_end_inner_diameter)/4, 0, top_length + mid_length/2]) {
                rotate([0, side_angle, 0]) {
                    translate([0, 0, -side_length/2]) {
                        tapered_cylinder_additive(
                            side_length, 
                            side_taper_diameter_end,
                            side_taper_diameter_tip, 
                            side_wall_thickness, 
                            side_is_inside_fitting
                        );
                    }
                }
            }
        }
        
        // Cut out inner passages for mid section connections
        // Top to mid connection
        translate([0, 0, top_length - poop]) {
            cylinder(h = mid_length + 2*poop, d1 = top_end_inner_diameter, d2 = bot_end_inner_diameter, center = false);
        }
        
        // Top section subtractive part
        translate([0, 0, -poop]) {
            tapered_cylinder_subtractive(
                top_length + poop*2, 
                top_taper_diameter_tip, 
                top_taper_diameter_end, 
                top_wall_thickness, 
                top_is_inside_fitting
            );
        }
        
        // Bottom section subtractive part
        translate([0, 0, top_length + mid_length - poop]) {
            tapered_cylinder_subtractive(
                bot_length + poop*2, 
                bot_taper_diameter_end, 
                bot_taper_diameter_tip, 
                bot_wall_thickness, 
                bot_is_inside_fitting
            );
        }
        
        // Side port subtractive part (only the portion that would be inside the adapter)
        translate([(top_end_inner_diameter + bot_end_inner_diameter)/4, 0, top_length + mid_length/2]) {
            rotate([0, side_angle, 0]) {
                translate([0, 0, -side_length/2 - poop]) {
                    tapered_cylinder_subtractive(
                        side_length + poop*2, 
                        side_taper_diameter_end,
                        side_taper_diameter_tip, 
                        side_wall_thickness, 
                        side_is_inside_fitting
                    );
                }
            }
        }
    }
}

// ===== RENDERING =====

dust_hose_adapter(); 