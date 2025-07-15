// replacement threader block for the beall threader
// this design prints the block larger than the beall delrin blocks and does not fit with the wood board that comes with the threader
// it is not necessary, just clamp directly to the block

use <BOSL/threading.scad>

// primary screw parameters
// screw diameter, you may want to make this slightly larger than the nominal size of the rod.
screw_diameter = 26; 
// threads per inch (6 to match the beall threader)
tpi = 6; 

// Convert to inches for calculations (1 inch = 25.4 mm)
screw_diameter_inch = screw_diameter / 25.4;

router_hole_gap = 3/8 * 25.4;

// Main dimensions
// screw goes in this direction, make this longer for more support I guess. 2.5 seems fine.
width = 2.5 * 25.4;  
// length of the threading block
length = screw_diameter * 2.5;
// height of the threading block
height = (screw_diameter_inch) * 25.4 + router_hole_gap*2;

// alignment and screw hole dimensions (these are the same as the beall threader)
center_hole_diameter = 3/8 * 25.4; // 3/8 inch in mm
side_hole_diameter = 7/32 * 25.4;  // 7/32 inch in mm
side_hole_spacing = 1.375 * 25.4;  // 1 3/8 inches in mm
side_hole_bore_diameter = 10;
side_hole_non_bore_thickness = router_hole_gap*3/5;

// increase mounting hole dimensions by this amount to account for FDM overextrusion
fdm_overextrusion_offset = 0.05; 



// chamfer radius for rounded edges
chamfer_radius = 2; // 2mm radius for rounded corners

// annoying openSCAD stuff
poop = 0.01;

module wood_threader() {
    difference() {
        // Main rectangular body
        // chamfer the edges of the block
        minkowski() {
            translate([-length/2 + chamfer_radius, -width/2 + chamfer_radius, -height/2 + chamfer_radius])
            cube([length - 2*chamfer_radius, width - 2*chamfer_radius, height - 2*chamfer_radius]);
            sphere(r = chamfer_radius, $fn = 32);
        }
    
        {
            // Center hole (3/8" diameter, halfway down)
            translate([0, 0, -height/4])
            cylinder(h = height/2 + poop, d = center_hole_diameter, center = true);
        }
        
        // Side holes (7/32" diameter, all the way through)
        // Calculate positions for holes along the 3" dimension (width)
        for (i = [-1, 1]) {
            translate([0, i * side_hole_spacing / 2, 0])
            cylinder(h = height + poop, d = side_hole_diameter, center = true);
        }

        // now counterbore the 2 holes we just made
        for (i = [-1, 1]) {
            translate([0, 0 + i * side_hole_spacing / 2, side_hole_non_bore_thickness + screw_diameter/4 - height/2])
            cylinder(h = screw_diameter/2, d = side_hole_bore_diameter, center = true);
        }

        // Threaded hole using BOSL library
        {
            translate([0, 0, 0])
            rotate([90, 0, 0])
            // the center of the thread starts on the +x axis in the center of therod so we need to rotate by 90 degrees for alignment
            rotate([0, 0, 90])
            // this uses the default thread angle of 30 which matches the beall tap
            threaded_rod(
                d = screw_diameter,
                l = width + poop*2,
                pitch = 25.4/tpi, // Convert TPI to pitch in mm
                internal = true,
                // the center of the thread starts on the +x axis in the center of therod so we need to rotate by 90 degrees for alignment
                //bevel = true,
                $fn=64
            );
        }

        // we actually only want half the hole threaded, cut out the threads from the other half with a screw_diameter cylinder with some awkward cutouts
        {
            difference()
            {
                
                // make the cylinder go 1/4 of a tooth past the center
                overstep = 25.4/tpi*1/4;
                translate([0, width/2 - overstep, 0])
                    rotate([90, 0, 0])
                        cylinder(h = width, d = screw_diameter, center = true);

                // now chop off the bottom corner of the cylinder so that the threads reach the hole
                translate([screw_diameter/2, -overstep*4/3, -screw_diameter/2])
                   cube([screw_diameter, overstep*8/3, screw_diameter], center = true);
            }
        }

        // now clean out the pointy thread ends to match the beall tap
        {
            translate([0, -width/2, 0])
            rotate([90, 0, 0])
            cylinder(h = width*2, d = screw_diameter - 1/8 * 25.4, center = true);
        }

        // cut off the top so we can see what's going on
        translate([0, 0, height])
            cube([100, 100, 100], center = true);
    }
}

// Generate the model
wood_threader();
