// WIP NOT WORKING
// BOSL library import
use <BOSL/constants.scad>;
use <BOSL/threading.scad>;

// Parameters
thread_tpi = 6;                // Threads per inch
screw_diameter = 25;          // Diameter of screw (inches or mm as desired)
outer_thread_diameter = 50;    // Outer thread diameter (inches or mm)
threading_block_length = 50;   // Length of threading block (inches or mm)

taper_angle = 5;
taper_min_thickness = 2;

// Derived
thread_pitch = 25.4 / thread_tpi; // If using inches, convert TPI to mm pitch
poop = 0.1;

// Block with threaded hole
module threaded_block() {
    block_size = [outer_thread_diameter*2, threading_block_length, outer_thread_diameter*2];
    difference() {
        cube(block_size, center=true);
        // Threaded hole (internal)
        translate([0,0,0])
            rotate([90,0,0])
                threaded_rod(
                    d = outer_thread_diameter,
                    l = threading_block_length+2, // slightly longer for clearance
                    pitch = thread_pitch,
                    internal = true,
                    $fn = 64
                );
    }
}

// Central tapered hole
taper_base_d = screw_diameter + taper_min_thickness;
taper_height = threading_block_length + 2*poop;
taper_radius_increase = tan(taper_angle) * (taper_height/2);
taper_top_d = taper_base_d + 2 * taper_radius_increase;

// Cylinder with external threads and central hole
module threaded_cylinder() {
    difference() {
        // External threads
        rotate([90,0,0])
            threaded_rod(
                d = outer_thread_diameter,
                l = threading_block_length,
                pitch = thread_pitch,
                internal = false,
                $fn = 64
            );
        
        // tapered central hole to fit wedge
        rotate([90,0,0])
            translate([0,0,0])
                cylinder(h=taper_height, d1=taper_base_d, d2=taper_top_d, center=true);
    }
}

// wedge
module wedge() {
    wedge_extension = 10;
    difference() {
        // Tapered solid, large end extended by 10mm
        translate([0,0,0])
            cylinder(h=taper_height + wedge_extension, d1=taper_base_d, d2=taper_top_d);
        // Central cylindrical cutout
        translate([0,0,-poop])
            cylinder(h=taper_height + wedge_extension + 2*poop, d=screw_diameter);
        // split the wedge in half
        // Remove 1mm from the middle along the YZ plane (X=0)
        translate([-0.5, -taper_top_d, -taper_height])
            cube([1, 2*taper_top_d, 2*(taper_height + wedge_extension)], center=false);
    }
}


// Show both for reference
translate([-outer_thread_diameter*1.5,0,0]) threaded_block();
translate([outer_thread_diameter*1.5,0,0]) threaded_cylinder();
translate([0,0,0]) wedge();
