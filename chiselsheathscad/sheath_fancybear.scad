// Chisel Sheath by 吕 minimaple 
// CHISEL PARAMETERS
// width of chisel in mm
chisel_width = 19;

// thickness of chisel right where the bevel starts in mm
chisel_tip_thickness = 4.9;

// thickness of chisel at end of sheath in mm
chisel_end_thickness = 6.5;

// The length of the bevel (tapering to 0mm). You can set this to 0 if you don't want the chisel shape in the mortise.
chisel_bevel_length = 5;


// SHEATH PARAMETERS
// length of the chisel (measured from the tip) you want inside the sheath in mm
chisel_length = 62;

// wall thickness (top/bottom) in mm
sheath_wall_thickness = 2;

// side wall thickness in mm
sheath_side_thickness = 3;

// thickness in front of the chisel in mm
sheath_front_thickness = 4;

// add the bevel shape at the front of the chisel sheath
enable_sheath_bevel = true;

// round-over radius of the sheath in mm
minkowski_radius = 1;

// (don't change me) the tip goes to 0 thickness but we buffer it to this thickness instead
very_tip_thickness_buffer = 1;

// add some cute ears 🐻 
enable_ears = true;

// distance between the ears in mm
ear_distance = 12;
// height of the cylinder in the sheath length plane in mm
ear_height = 2;
// width of the cylinder in mm
ear_width = 3;
// position relative to the tip of the sheath (0 = at tip, positive = above tip, negative = below tip) in mm
ear_position = 0;
// depth of the cylinder extrusion in mm
ear_depth = 3;

// add some cute eye holes 👀(these are for preventing rust)
enable_eyes = true;
// height of the eye cylinder in mm
eye_height = 1.5;
// width of the eye cylinder in mm
eye_width = 1.7;
// distance between the eyes in mm
eye_distance = 10;
// position of the eyes relative to the height of the sheath (0 at the bottom, 1 at the top)
eye_position_ratio = 0.8;



// add the minimaple logo 吕 
enable_logo = true;
// scale factor for the logo (1.0 = original size)
logo_scale = 0.8;
// depth of emboss (engrave) in mm
logo_depth = 0.8;            
// "emboss" or "engrave"
logo_style = "emboss"; 
// "bevel" or "back"
logo_side = "bevel"; 


// openscad has lots of z fighting type issues so offset to prevent them
poop = 1;

// Chisel quadrilateral:
// - vertical left side (X = -lower_width/2)
// - tapered right side (X = +lower_width/2 → +upper_width/2)
// - profile in XZ, extruded along Y
// - fully centered on X axis and Y axis
module chisel_quadrilateral(lower_width = 10, upper_width = 5, height = 20, depth = 4) {
    translate([0, depth/2, 0])  // Center extrusion along X axis
    rotate([90, 0, 0])           // XZ -> XY so extrusion is along Y
    linear_extrude(height = depth, center = false)
        polygon(points = [
            [ 0, 0 ],         // Bottom left (vertical side)
            [ lower_width, 0 ],          // Bottom right
            [ upper_width, height ],     // Top right
            [ 0, height ]      // Top left (vertical side)
        ]);
}

// Example usage:
//chisel_quadrilateral(lower_width = 10, upper_width = 5, height = 20, depth = 40);


// Example usage
// Combined chisel shape: bevel on top
module chisel_shape(
    chisel_width = 37.7,
    chisel_tip_thickness = 3.5,
    chisel_end_thickness = 6.5,
    chisel_bevel_length = 5,
    chisel_length = 50,
    very_tip_thickness_buffer = 1,
) {
    chisel_body_height = chisel_length - chisel_bevel_length;
    union() {
        chisel_quadrilateral(
            lower_width = chisel_end_thickness,
            upper_width = chisel_tip_thickness,
            height = chisel_body_height,
            depth = chisel_width
        );

        // Bevel at the top
        translate([0, 0, chisel_body_height])
        chisel_quadrilateral(
            lower_width = chisel_tip_thickness,
            upper_width = very_tip_thickness_buffer,
            height = chisel_bevel_length,
            depth = chisel_width
        );
    }
}


// 🐻 Bear ears module
module bear_ears() {
    // Position ears at the tip of the sheath plus the specified offset
    z_offset = chisel_length + sheath_front_thickness + ear_position;
    // Center the ears horizontally on the sheath
    x_offset = (very_tip_thickness_buffer + sheath_wall_thickness * 2) / 2;
    // Position ears at half the distance from center
    y_offset = ear_distance / 2;
    
    union() {
        // Left ear
        translate([x_offset, -y_offset, z_offset])
            rotate([0, 90, 0])  // rotate to extrude in the thickness plane
                scale([ear_height, ear_width, ear_depth])
                    cylinder(h = 1, r = 1, center = true, $fn = 24);
        
        // Right ear
        translate([x_offset, y_offset, z_offset])
            rotate([0, 90, 0])  // rotate to extrude in the thickness plane
                scale([ear_height, ear_width, ear_depth])
                    cylinder(h = 1, r = 1, center = true, $fn = 24);
    }
}

// eyes module
module eyes() {
    eye_depth = chisel_tip_thickness + sheath_wall_thickness * 2 + 1;  // enough to cut through
    eye_offset_y = eye_distance / 2;   // half the distance for each eye
    eye_offset_z = (chisel_length + sheath_front_thickness) * eye_position_ratio;
    for (side = [-1, 1]) {
        translate([eye_depth, side * eye_offset_y, eye_offset_z])
            rotate([0, 90, 0])  // align along X-axis
                scale([eye_height, eye_width, eye_depth])
                    cylinder(h = 1, r = 1, center = true, $fn = 24);
    }
}

// Rounded sheath shape using Minkowski sum
module sheath_shape() {
    difference() {
        // OUTER: apply minkowski to outer sheath only
        union() {
            minkowski() {
                chisel_shape(
                    chisel_width = chisel_width + sheath_side_thickness * 2,
                    chisel_tip_thickness = chisel_tip_thickness + sheath_wall_thickness * 2,
                    chisel_end_thickness = chisel_end_thickness + sheath_wall_thickness * 2,
                    chisel_bevel_length = enable_sheath_bevel ? chisel_bevel_length + sheath_front_thickness : 0,
                    chisel_length = chisel_length + sheath_front_thickness,
                    very_tip_thickness_buffer = very_tip_thickness_buffer + sheath_wall_thickness * 2
                );
                sphere(r = minkowski_radius, $fn = 24);  // small sphere for smooth edges
            };
            // 🐻 Only add bear ears if enabled (with separate minkowski)
            if (enable_ears) {
                minkowski() {
                    bear_ears();
                    sphere(r = minkowski_radius, $fn = 24);
                }
            }
        }
        //
        if (enable_eyes) {
            eyes();
        }


        // INNER: the actual chisel cavity, offset for wall thickness
        translate([sheath_wall_thickness,0,-poop])
        chisel_shape(
            chisel_width = chisel_width,
            chisel_tip_thickness = chisel_tip_thickness,
            chisel_end_thickness = chisel_end_thickness,
            chisel_bevel_length = chisel_bevel_length,
            chisel_length = chisel_length,
            very_tip_thickness_buffer = very_tip_thickness_buffer
        );
    }
}



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

// Parametric logo placement: takes explicit args for style + side
module logo_on_sheath(style, side) {
    

    if (side == "back") {

        // Z: center height for simplicity
        z_offset = (chisel_length + sheath_front_thickness) / 2;

        // Flat left side
        x_offset = style == "emboss" ? -logo_depth - minkowski_radius: -poop;
        y_offset = 0;


        translate([x_offset, y_offset, z_offset])
            rotate([0, 0, 90])  // upright
                logo();
    }
    else if (side == "bevel") {
        // body slope angle
        taper_angle = atan((chisel_end_thickness - chisel_tip_thickness) / (chisel_length - chisel_bevel_length));

        // Right tapered side
        emboss_offset = style == "emboss" ? logo_depth : poop;

        // the total distance along the angle we want to offset the logo by, not entirely correct but whatever
        angled_offset = (chisel_tip_thickness + chisel_end_thickness) / 2 + sheath_wall_thickness * 2 + emboss_offset + minkowski_radius;

        z_offset = chisel_length / 2 - chisel_bevel_length - sheath_front_thickness + sin(taper_angle) * angled_offset;
        x_offset = cos(taper_angle) * angled_offset;
        y_offset = 0;

        translate([x_offset, y_offset, z_offset])
            rotate([0, -taper_angle, 0]) // match slope
            rotate([0, 0, -90])          // face outward
                logo();
    }
}


// Example usage in difference() for engraving:
if (logo_style == "emboss") {
    union() {
        sheath_shape();
        if (enable_logo) {
            logo_on_sheath("emboss", logo_side);
        }
    }
}
else {
    difference() {
        sheath_shape();
        if (enable_logo) {
            logo_on_sheath("engrave", logo_side);
        }
    }
}
