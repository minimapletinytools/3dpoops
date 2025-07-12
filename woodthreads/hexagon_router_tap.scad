// Wooden Thread Router Jig
// Creates a jig for making wooden threads with a 1/4 palm router

// Include BOSL2 library for threads
include <BOSL2/std.scad>
include <BOSL2/threading.scad>

// ===== PARAMETERS =====

// Router block parameters
block_thickness = 25;           // Thickness of the router mounting block
block_width = 150;               // Width of the block
block_height = 150;              // Height of the block
threaded_hole_diameter = 110;    // Diameter of the threaded hole
thread_tpi = 6;                 // Threads per inch

// Router mounting parameters
mount_hole_diameter = 4;        // Diameter of mounting holes
mount_hole_distance = 60;       // Distance between mounting holes (center to center)
mount_hole_offset = 10;         // Offset from edge to first hole

// Hexagon screw parameters
screw_length = block_thickness*5/3;             // Total length of the screw
hex_cutout_length = block_thickness*7/6;
hex_face_to_face = 50.8;         // Face-to-face distance of the hexagon (make this ever so slightly smaller than the hex nut)
hex_taper_angle = 1;            // Taper out angle in degrees
hex_offset = (7/8 - 1/8) * 25.4 /2; // offset from the center of the hexagon to the center of the screw, depends on the inner diameter of the hexagon and the bit size
grip_diameter = 15;             // Diameter of the grip section
grip_length = 8;               // Length of the grip section

poop = 0.1;

// ===== ROUTER BLOCK =====

module router_block() {
    difference() {
        // Main block
        cube([block_width, block_height, block_thickness]);
        
        // Threaded hole in center using BOSL2
        translate([block_width/2, block_height/2, -poop]) {
            threaded_rod(
                d = threaded_hole_diameter,
                l = block_thickness + 2*poop,
                pitch = 25.4/thread_tpi,
                internal = true,
                // seems to be broken?
                //teardrop = true,
                $fn = 50
            );
        }
        
        // Mounting holes for router base
        translate([mount_hole_offset, mount_hole_offset, -poop]) {
            cylinder(h = block_thickness + 2*poop, d = mount_hole_diameter);
        }
        translate([block_width - mount_hole_offset, mount_hole_offset, -poop]) {
            cylinder(h = block_thickness + 2*poop, d = mount_hole_diameter);
        }
        translate([mount_hole_offset, block_height - mount_hole_offset, -poop]) {
            cylinder(h = block_thickness + 2*poop, d = mount_hole_diameter);
        }
        translate([block_width - mount_hole_offset, block_height - mount_hole_offset, -poop]) {
            cylinder(h = block_thickness + 2*poop, d = mount_hole_diameter);
        }
    }
}

// ===== HEXAGON SCREW =====

module tapered_hexagon(length, face_to_face, taper_angle) {
    // Calculate hexagon points
    hex_radius = face_to_face / (2 * cos(30));
    
    // Create tapered hexagon using hull of two hexagons
    hull() {
        // Bottom hexagon (larger due to taper)
        translate([0, 0, 0]) {
            cylinder(h = 0.001, r = hex_radius + length * tan(taper_angle), $fn = 6);
        }
        // Top hexagon
        translate([0, 0, length]) {
            cylinder(h = 0.001, r = hex_radius, $fn = 6);
        }
    }
}

module hexagon_screw() {
    union() {
        difference() {
        translate([0, 0, screw_length/2]) {
            threaded_rod(
                d = threaded_hole_diameter,
                l = screw_length,
                pitch = 25.4/thread_tpi,
                internal = true,
                $fn = 50
            );
        }
            // Tapered hexagon section
            translate([hex_offset, 0, -poop]) {
                tapered_hexagon(hex_cutout_length, hex_face_to_face, hex_taper_angle);
            }
        }
        
        // Add 6 grip cylinders around the top of the screw
        for (angle = [0:60:360]) {
            rotate([0, 0, angle]) {
                translate([0, 0, screw_length-grip_length]) {
                    translate([threaded_hole_diameter/2, 0, 0]) {
                        cylinder(h = grip_length, d = grip_diameter, center = false);
                    }
                }
            }
        }
        
    }
}

// ===== RENDERING =====

// Uncomment the part you want to render

// Router block
router_block();

hexagon_screw();

