// Parametric Dust Hose Adapter with Tapered Fittings 🛠️
// Creates a dust hose adapter with tapered sections and conical transition
// 吕 minimaple 

// ===== PARAMETERS =====

// Top section parameters
// Diameter at the tip of top section
top_taper_diameter_tip = 63.5;     
// Diameter at the base of top section
top_taper_diameter_base = 63;     
// Length of top section
top_length = 50;                 
// Set to true if this is an outer fitting, false for inner fitting. If outer fitting then diameter is inner diameter + taper inside (reducing). Otherwise diameter is outer diameter + taper outside (increasing)
top_is_outer_fitting = true;    
// Wall thickness for top section
top_wall_thickness = 3;          

// Bottom section parameters
// Diameter at the tip of bottom section (connects to mid section)
bot_taper_diameter_tip = 106;     
// Diameter at the base of bottom section (free end)
bot_taper_diameter_base = 106;     
// Length of bottom section
bot_length = 50;                 
// Set to true if this is an outer fitting, false for inner fitting
bot_is_outer_fitting = false;    
// Wall thickness for bottom section
bot_wall_thickness = 3;          

// Length of conical mid section connecting top and bottom sections
mid_length = 40;                 

// Side port parameters
// Diameter at the tip of side port
side_taper_diameter_tip = 38;    
// Diameter at the base of side port
side_taper_diameter_base = 39;   
// Length of side port, make this a little longer than you need as part of it is sticking into the mid section
side_length = 85;                
// Angle at which side port sticks out (degrees)
side_angle = -45;                 
// Set to true if this is an outer fitting, false for inner fitting
side_is_outer_fitting = false; 
// Wall thickness for side port
side_wall_thickness = 3;         

// Cylinder resolution (number of facets)
cylinder_resolution = 64;        

// add the minimaple logo 吕 
enable_logo = true;
// scale factor for the logo (1.0 = original size)
logo_scale = 1;
// depth of emboss (engrave) in mm
logo_depth = 1;    

// Account for OpenSCAD Z fighting issues, do not change
poop = 0.1;                     


// ===== HELPER FUNCTIONS =====


// Engrave the 吕 logo on the front face
module logo() {
    logo_width = 7;           // Width of the bottom box
    logo_height = 4;           // Height of the bottom box
    logo_top_scale = 0.8;      // Ratio of top box width to bottom box
    logo_spacing = 1.5;          // Vertical gap between the two boxes

     minkowski() {
        rotate([90,0,0]) {
            scale([logo_scale, logo_scale, 1]) {  // scale X and Y, keep Z (depth) unchanged
                union() {
                    // Bottom box
                    translate([-logo_width/2, -logo_height/2, 0])
                        cube([logo_width, logo_height, logo_depth+poop]);
                    
                    // Top box
                    translate([-logo_width*logo_top_scale/2, logo_height/2 + logo_spacing, 0])
                        cube([logo_width*logo_top_scale, logo_height, logo_depth+poop]);
                }
            }
        };
        sphere(r = 0.2, $fn = 24); 
    }
    
}


// Generate the additive geometry (outer shell) for tapered cylinder
module tapered_cylinder_additive(length, diameter_A, diameter_B, wall_thickness, is_outer_fitting) {
    if (is_outer_fitting) {
        // Diameters are inside diameters, so add wall thickness for outer shell
        cylinder(h = length, d1 = diameter_A + 2*wall_thickness, d2 = diameter_B + 2*wall_thickness, center = false, $fn = cylinder_resolution);
    } else {
        // Diameters are outside diameters, so use as-is for outer shell
        cylinder(h = length, d1 = diameter_A, d2 = diameter_B, center = false, $fn = cylinder_resolution);
    }
}

// Generate the subtractive geometry (inner bore) for tapered cylinder
module tapered_cylinder_subtractive(length, diameter_A, diameter_B, wall_thickness, is_outer_fitting) {
    if (is_outer_fitting) {
        // Diameters are inside diameters, so use as-is for inner bore
        translate([0, 0, -poop]) {
            cylinder(h = length + poop*2, d1 = diameter_A, d2 = diameter_B, center = false, $fn = cylinder_resolution);
        }
    } else {
        // Diameters are outside diameters, so subtract wall thickness for inner bore
        translate([0, 0, -poop]) {
            cylinder(h = length + poop*2, d1 = diameter_A - 2*wall_thickness, d2 = diameter_B - 2*wall_thickness, center = false, $fn = cylinder_resolution);
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


    mid_middle_outer_diameter = (top_base_outer_diameter + bot_base_outer_diameter) / 2;


    
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
                cylinder(h = mid_length, d1 = top_base_outer_diameter, d2 = bot_base_outer_diameter, center = false, $fn = cylinder_resolution);
            }

            // Logo emboss on conical section
            if (enable_logo) {
                // Calculate the angle of the conical section
                cone_angle = atan2(mid_length, (bot_base_outer_diameter - top_base_outer_diameter) / 2);
                
                translate([-mid_middle_outer_diameter/2, 0, top_length + mid_length/2]) {
                    
                    rotate([0, 0, 90])
                        rotate([90+cone_angle, 0, 0])
                            logo();
                }
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
            cylinder(h = mid_length + 2*poop, d1 = top_base_inner_diameter, d2 = bot_base_inner_diameter, center = false, $fn = cylinder_resolution);
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