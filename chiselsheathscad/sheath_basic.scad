// Chisel Sheath by 吕 minimaple 

// PARAMETERS
chisel_width = 18.6;         // Width of chisel in mm
sheath_length = 52;        // Length of chisel you want inside the sheath in mm
chisel_tip_thickness = 4.7;  // Thickness of chisel at tip in mm
chisel_end_thickness = 6.6;  // Thickness of chisel at end of sheath in mm
sheath_wall_thickness = 3; // Wall thickness (top/bottom) in mm
tip_thickness = 5;         // Extra tip clearance thickness in mm
sheath_side_thickness = 5; // Side wall thickness in mm
round_radius = 1;          // Round-over radius in mm

// Logo parameters
logo_width = 7;           // Width of the bottom box
logo_height = 4;           // Height of the bottom box
logo_top_scale = 0.8;      // Ratio of top box width to bottom box
logo_spacing = 1.5;          // Vertical gap between the two boxes
logo_depth = 0.5;            // Depth of emboss (engrave) in mm

// MAIN CALL
sheath();

module sheath() {
    difference() {
        // Outer tapered sheath with round-over
        minkowski() {
            tapered_box(
                w = chisel_width + 2 * sheath_side_thickness,
                t1 = chisel_end_thickness + 2 * sheath_wall_thickness,
                t2 = chisel_tip_thickness + 2 * sheath_wall_thickness,
                l = sheath_length + tip_thickness
            );
            sphere(r = round_radius, $fn=48);
        }

        // ✅ Inner cavity — extend by +1mm so it fully pierces the mouth
        translate([0, 0, -1])
            tapered_box(
                w = chisel_width,
                t1 = chisel_end_thickness + 0.5,  // slightly larger to pierce
                t2 = chisel_tip_thickness,
                l = sheath_length + 1   // extend by +1mm
            );

        // Engrave the logo on the front face (centered)
        logo();
    }
}

// Creates a front-to-back tapered box using hull
module tapered_box(w, t1, t2, l) {
    hull() {
        // Opening end (thicker)
        translate([0, 0, 0])
            cube([w, t1, 0.01], center = true);
        // Tip end (thinner)
        translate([0, 0, l])
            cube([w, t2, 0.01], center = true);
    }
}

// Engrave the 吕 logo on the front face
module logo() {
    // Calculate position: front face = +Y side
    // Place logo slightly inset so it cuts into the wall
    translate([0, (chisel_end_thickness + 2*sheath_wall_thickness)/2 + 1, sheath_length/2])
    rotate([90,0,0]) {
        union() {
            // Bottom box
            translate([-logo_width/2, -logo_height/2, 0])
                cube([logo_width, logo_height, logo_depth+1]);
            
            // Top box
            translate([-logo_width*logo_top_scale/2, logo_height/2 + logo_spacing, 0])
                cube([logo_width*logo_top_scale, logo_height, logo_depth+1]);
        }
    }
}
