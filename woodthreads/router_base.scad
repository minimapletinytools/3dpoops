// Router attachment base for direct threader block
// Attaches to the bottom of the router, threader block attaches to this

include <BOSL2/std.scad>

// Base dimensions
base_width = 120;    // mm
base_length = 120;   // mm  
base_height = 10;    // mm




// Center hole
center_hole_diameter = 35.5;  

// Router mounting holes (attach to router, default values fit Makita RT0701C)
router_hole_width = 54;     // spacing between router holes in width direction
router_hole_height = 45;    // spacing between router holes in height direction
router_hole_height_offset = 3.5; // holes offset in the height direction, becaues not all routers have centered hole spacing. See README.md for specific example of how this works.
router_hole_diameter = 4;   // diameter of router mounting holes

// Counterbore parameters for router holes
router_hole_counterbore_diameter = 8;   // diameter of counterbore
router_hole_counterbore_depth = 3;      // depth of counterbore

// Mounting holes (for threader block to attach)
mounting_hole_width = 100;   // spacing between mounting holes in width direction
mounting_hole_height = 100;  // spacing between mounting holes in height direction
mounting_hole_diameter = 5;  // diameter of mounting holes

// Chamfer radius for rounded edges
chamfer_radius = 2; // 2mm radius for rounded corners

// Small value for OpenSCAD operations
poop = 0.01;

module router_base() {
    difference() {
        // Main base body with chamfered edges
        minkowski() {
            translate([-base_length/2 + chamfer_radius, -base_width/2 + chamfer_radius, -base_height/2 + chamfer_radius])
                cube([base_length - 2*chamfer_radius, base_width - 2*chamfer_radius, base_height - 2*chamfer_radius]);
            sphere(r = chamfer_radius, $fn = 32);
        }
        
        // Center hole (goes all the way through)
        translate([0, 0, 0])
            cylinder(h = base_height + 2*poop, d = center_hole_diameter, center = true);
        
        // Router mounting holes with counterbores (attach to router)
        for (i = [-1, 1]) {
            for (j = [-1, 1]) {
                translate([i * router_hole_width/2, j * router_hole_height/2 + router_hole_height_offset, 0]) {
                    // Through hole
                    cylinder(h = base_height + 2*poop, d = router_hole_diameter, center = true);
                    
                    // Counterbore from bottom
                    translate([0, 0, -base_height/2 + router_hole_counterbore_depth/2 - poop])
                        cylinder(h = router_hole_counterbore_depth + poop, d = router_hole_counterbore_diameter, center = true);
                }
            }
        }
        
        // Mounting holes (for threader block to attach from top)
        for (i = [-1, 1]) {
            for (j = [-1, 1]) {
                translate([i * mounting_hole_width/2, j * mounting_hole_height/2, 0])
                    cylinder(h = base_height + 2*poop, d = mounting_hole_diameter, center = true);
            }
        }
    }
}

// Generate the model
router_base();
