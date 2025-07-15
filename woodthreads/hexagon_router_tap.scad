// jig for cutting inside threads on a hexagon nut with a router

// Include BOSL2 library for threads
include <BOSL2/std.scad>
include <BOSL2/threading.scad>

// ===== PARAMETERS =====

// Router block parameters
block_thickness = 25;           // Thickness of the router mounting block
block_diameter = 150;           // Diameter of the cylindrical block
threaded_hole_diameter = 110;    // Diameter of the threaded hole
thread_tpi = 6;                 // Threads per inch

// Router mounting parameters
mount_hole_diameter = 4;        // Diameter of mounting holes
mount_hole_distance = 130;      // Distance from center to each mounting hole
support_disk_diameter = 40;     // Diameter of support disks around mounting holes
support_disk_height = block_thickness;

// Router mounting plate parameters
// TODO


// Minkowski parameters
minkowski_radius = 1;           // Radius for Minkowski operation

// Hexagon screw parameters
max_threading_length = block_thickness*6/7;
screw_length = block_thickness*5/3;             // Total length of the screw
hex_cutout_length = max_threading_length+3;
hex_face_to_face = 50.8;         // Face-to-face distance of the hexagon (make this ever so slightly smaller than the hex nut)
hex_taper_angle = 1;            // Taper out angle in degrees
grip_diameter = 15;             // Diameter of the grip section
grip_length = 8;               // Length of the grip section

poop = 0.1;

// ===== ROUTER BLOCK =====

module router_block() {
    difference() {
        minkowski() {
            translate([0, 0, minkowski_radius]) {
                union() {
                    // Main cylindrical block - centered at origin (adjusted for Minkowski)
                    cylinder(h = block_thickness - 2*minkowski_radius, d = block_diameter - 2*minkowski_radius, center = false);
                    
                    // Support disks around mounting holes (adjusted for Minkowski)
                    translate([-mount_hole_distance/2, 0, 0]) {
                        cylinder(h = support_disk_height - 2*minkowski_radius, d = support_disk_diameter - 2*minkowski_radius, center = false);
                    }
                    translate([mount_hole_distance/2, 0, 0]) {
                        cylinder(h = support_disk_height - 2*minkowski_radius, d = support_disk_diameter - 2*minkowski_radius, center = false);
                    }
                }
            }
            sphere(r = minkowski_radius, $fn = 16);
        }
        
        // Threaded hole in center using BOSL2
        translate([0, 0, -poop]) {
            threaded_rod(
                d = threaded_hole_diameter,
                l = max_threading_length*2,
                pitch = 25.4/thread_tpi,
                internal = true,
                $fn = 50,
                center = false
            );
        }

        // hole in the center for the router
        translate([0, 0, -poop]) {
            cylinder(h = block_thickness + 2*poop, d = threaded_hole_diameter/2);
        }
        
        // Mounting holes on X axis
        translate([-mount_hole_distance/2, 0, -poop]) {
            cylinder(h = block_thickness + 2*poop, d = mount_hole_diameter);
        }
        translate([mount_hole_distance/2, 0, -poop]) {
            cylinder(h = block_thickness + 2*poop, d = mount_hole_diameter);
        }
    }
}

// ===== HEXAGON SCREW =====

module tapered_hexagon(length, face_to_face, taper_angle) {
    // Calculate hexagon points
    hex_radius = face_to_face / (2 * cos(30));
    large_radius = hex_radius + length * tan(taper_angle);
    
    // Create tapered hexagon using hull of two hexagons
    hull() {
        // Bottom hexagon (larger due to taper)
        translate([0, 0, 0]) {
            cylinder(h = 0.001, r = large_radius, $fn = 6);
        }
        // Top hexagon
        translate([0, 0, length]) {
            cylinder(h = 0.001, r = hex_radius, $fn = 6);
        }
    }

    // chamfer the bottom part
    translate([0, 0, -poop]) {
        cylinder(h = minkowski_radius, d1 = large_radius*2+minkowski_radius, d2 = hex_radius*2, center = false, $fn = 6);
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
            // Tapered hexagon section with inside chamfer
            translate([0, 0, -poop]) {
                tapered_hexagon(hex_cutout_length, hex_face_to_face, hex_taper_angle);
            }
        }
        
        // Add 6 grip cylinders and central cylinder with Minkowski
        minkowski() {
            union() {
                // Add 6 grip cylinders around the top of the screw (adjusted for Minkowski)
                for (angle = [0:60:360]) {
                    rotate([0, 0, angle]) {
                        translate([0, 0, screw_length-grip_length]) {
                            translate([threaded_hole_diameter/2, 0, 0]) {
                                cylinder(h = grip_length, d = grip_diameter, center = false);
                            }
                        }
                    }
                }
                
                // Add central cylinder at the same height as grip handles (adjusted for Minkowski)
                translate([0, 0, screw_length-grip_length]) {
                    cylinder(h = grip_length , d = threaded_hole_diameter, center = false);
                }
            }
            sphere(r = minkowski_radius, $fn = 16);
        }
        
    }
}

// ===== RENDERING =====

// Uncomment the part you want to render

// Router block
//router_block();

hexagon_screw();

