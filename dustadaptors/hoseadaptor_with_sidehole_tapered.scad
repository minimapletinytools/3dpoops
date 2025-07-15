// Parametric Dust Hose Adapter with Tapered Fittings
// Creates a dust hose adapter

// ===== PARAMETERS =====

// Top section parameters
// Diameter at the tip of top section (the part that sticks out)
top_taper_diameter_tip = 63.5;     
// Diameter at the base of top section (the part that connects to the mid section)
top_taper_diameter_base = 63;     
// Length of top section
top_length = 50;                 
// set to true if this is an outter fitting, false for inner fitting. If outer fitting then diameter is inner diameter + taper inside (reducing). Otherwise diameter is outer diameter + taper outside (increasing)
top_is_outer_fitting = true;    
// Wall thickness for top section
top_wall_thickness = 3;          

// Bottom section parameters
bot_taper_diameter_tip = 106;     
bot_taper_diameter_base = 106;     
bot_length = 50;                 
bot_is_outer_fitting = false;    
bot_wall_thickness = 3;          

// Length of conical mid section connecting top and bottom sections
mid_length = 40;                 

// Side port parameters
side_taper_diameter_tip = 38;    
side_taper_diameter_base = 39;   
// Length of side port, make this a little longer than you need as part of it is sticking into the mid section
side_length = 70;                
// Angle at which side port sticks out (degrees)
side_angle = -45;                 
side_is_outer_fitting = false; 
side_wall_thickness = 3;         

// account for OpenSCAD Z fighting issues, do not change
poop = 0.1;                     

// ===== HELPER FUNCTIONS =====

// Generate the additive geometry (outer shell) for tapered cylinder
module tapered_cylinder_additive(length, diameter_A, diameter_B, wall_thickness, is_outer_fitting) {
    if (is_outer_fitting) {
        // Diameters are inside diameters, so add wall thickness for outer shell
        cylinder(h = length, d1 = diameter_A + 2*wall_thickness, d2 = diameter_B + 2*wall_thickness, center = false);
    } else {
        // Diameters are outside diameters, so use as-is for outer shell
        cylinder(h = length, d1 = diameter_A, d2 = diameter_B, center = false);
    }
}

// Generate the subtractive geometry (inner bore) for tapered cylinder
module tapered_cylinder_subtractive(length, diameter_A, diameter_B, wall_thickness, is_outer_fitting) {
    if (is_outer_fitting) {
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
module tapered_cylinder(length, diameter_A, diameter_B, wall_thickness, is_outer_fitting) {
    difference() {
        tapered_cylinder_additive(length, diameter_A, diameter_B, wall_thickness, is_outer_fitting);
        tapered_cylinder_subtractive(length, diameter_A, diameter_B, wall_thickness, is_outer_fitting);
    }
}

// ===== DUST HOSE ADAPTER =====

module dust_hose_adapter() {
    // Assertions to ensure proper diameter ordering for each section
    if (top_is_outer_fitting) {
        assert(top_taper_diameter_tip >= top_taper_diameter_base, "Top section: For inside fitting, tip diameter must be larger than base diameter");
    } else {
        assert(top_taper_diameter_tip <= top_taper_diameter_base, "Top section: For outside fitting, tip diameter must be smaller than base diameter");
    }
    
    if (bot_is_outer_fitting) {
        assert(bot_taper_diameter_tip >= bot_taper_diameter_base, "Bottom section: For inside fitting, tip diameter must be larger than base diameter");
    } else {
        assert(bot_taper_diameter_tip <= bot_taper_diameter_base, "Bottom section: For outside fitting, tip diameter must be smaller than base diameter");
    }
    
    if (side_is_outer_fitting) {
        assert(side_taper_diameter_tip >= side_taper_diameter_base, "Side section: For inside fitting, tip diameter must be larger than base diameter");
    } else {
        assert(side_taper_diameter_tip <= side_taper_diameter_base, "Side section: For outside fitting, tip diameter must be smaller than base diameter");
    }

    top_base_outer_diameter = top_is_outer_fitting ? top_taper_diameter_base + 2*top_wall_thickness : top_taper_diameter_base;
    bot_base_outer_diameter = bot_is_outer_fitting ? bot_taper_diameter_base + 2*bot_wall_thickness : bot_taper_diameter_base;

    top_base_inner_diameter = top_is_outer_fitting ? top_taper_diameter_base : top_taper_diameter_base - 2*top_wall_thickness;
    bot_base_inner_diameter = bot_is_outer_fitting ? bot_taper_diameter_base : bot_taper_diameter_base - 2*bot_wall_thickness;
    
    difference() {
        union() {
            // Top tapered section (additive part only)
            translate([0, 0, 0]) {
                tapered_cylinder_additive(
                    top_length, 
                    top_taper_diameter_tip, 
                    top_taper_diameter_base, 
                    top_wall_thickness, 
                    top_is_outer_fitting
                );
            }
            
            // Conical mid section
            translate([0, 0, top_length]) {
                cylinder(h = mid_length, d1 = top_base_outer_diameter, d2 = bot_base_outer_diameter, center = false);
            }
            
            // Bottom tapered section (additive part only)
            translate([0, 0, top_length + mid_length]) {
                tapered_cylinder_additive(
                    bot_length, 
                    bot_taper_diameter_base, 
                    bot_taper_diameter_tip, 
                    bot_wall_thickness, 
                    bot_is_outer_fitting
                );
            }
            
            // Side port tapered section (additive part only)
            translate([(top_base_inner_diameter + bot_base_inner_diameter)/4, 0, top_length + mid_length/2]) {
                rotate([0, side_angle, 0]) {
                    translate([0, 0, -side_length/2]) {
                        tapered_cylinder_additive(
                            side_length, 
                            side_taper_diameter_base,
                            side_taper_diameter_tip, 
                            side_wall_thickness, 
                            side_is_outer_fitting
                        );
                    }
                }
            }
        }
        
        // Cut out inner passages for mid section connections
        // Top to mid connection
        translate([0, 0, top_length - poop]) {
            cylinder(h = mid_length + 2*poop, d1 = top_base_inner_diameter, d2 = bot_base_inner_diameter, center = false);
        }
        
        // Top section subtractive part
        translate([0, 0, -poop]) {
            tapered_cylinder_subtractive(
                top_length + poop*2, 
                top_taper_diameter_tip, 
                top_taper_diameter_base, 
                top_wall_thickness, 
                top_is_outer_fitting
            );
        }
        
        // Bottom section subtractive part
        translate([0, 0, top_length + mid_length - poop]) {
            tapered_cylinder_subtractive(
                bot_length + poop*2, 
                bot_taper_diameter_base, 
                bot_taper_diameter_tip, 
                bot_wall_thickness, 
                bot_is_outer_fitting
            );
        }
        
        // Side port subtractive part (only the portion that would be inside the adapter)
        translate([(top_base_inner_diameter + bot_base_inner_diameter)/4, 0, top_length + mid_length/2]) {
            rotate([0, side_angle, 0]) {
                translate([0, 0, -side_length/2 - poop]) {
                    tapered_cylinder_subtractive(
                        side_length + poop*2, 
                        side_taper_diameter_base,
                        side_taper_diameter_tip, 
                        side_wall_thickness, 
                        side_is_outer_fitting
                    );
                }
            }
        }
    }
}

dust_hose_adapter(); 