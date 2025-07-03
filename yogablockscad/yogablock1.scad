// Yoga Block by 吕 minimaple 

// standard block
// block size in mm
block_length = 228.6;  // 9 * 25.4
block_width  = 152.4;  // 6 * 25.4
block_height = 101.6;  // 4 * 25.4

// standard flat block
//block_length = 228.6;  // 9 * 25.4
//block_width  = 152.4;  // 6 * 25.4
//block_height = 76.2;   // 3 * 25.4

// minimaple sized block
//block_length = 177.8;  // 7 * 25.4
//block_width  = 127;    // 5 * 25.4
//block_height = 76.2;   // 3 * 25.4


// how much to chamfer the edges of the block in mm
chamfer_radius = 7;  

// "round" or "flat"
chamfer_style = "round";  

// increase for smoother edges, decrease for a cool polygon look I guess
chamfer_resolution = 64;  


// Logo parameters
enable_logo = true;
// size of the logo (top to bottom) in mm
logo_size = 9;
// depth of emboss (engrave) in mm
logo_depth = 2;         
// "emboss" or "engrave"   
logo_style = "engrave";  
// "corner" or "center"
logo_position = "corner";


yoga_block(block_length, block_width, block_height, chamfer_radius, chamfer_style);

//logo_on_block(block_length, block_width, block_height);

// ===================================
// Main Yoga Block Module
module yoga_block(length, width, height, chamfer_r, chamfer_style) {
    // To compensate for Minkowski expansion, shrink the base
    shrink = chamfer_r;

    base_length = length - 2*shrink;
    base_width  = width  - 2*shrink;
    base_height = height - 2*shrink;

    module round_block() {
            minkowski() {
            cube([base_length, base_width, base_height], center=true);
            sphere(r=chamfer_r, $fn=chamfer_resolution);
        };
    }

    module flat_block() {
        minkowski() {
            cube([base_length, base_width, base_height], center=true);
            octahedron(chamfer_r);
        };
    }

    module just_a_block() {
        cube([length, width, height], center=true);
    } 

    module block() {
        if (chamfer_style == "round") {
            round_block();
        } else if (chamfer_style == "flat") {
            flat_block();
        } else {
            just_a_block();
        }
    } 

    
    if (enable_logo) {
        if (logo_style == "engrave") {
            difference() {  
                block();
                logo_on_block(length, width, height);
            }
        } else if (logo_style == "emboss") {
            union() {
                block();
                logo_on_block(length, width, height);
            }
        } else {
            echo("Invalid logo_style. Use \"emboss\" or \"engrave\".");
            block();
        }
    } else {
        block();
    }

}


// ===================================
// Octahedron Module (dual of cube)
module octahedron(size) {
    polyhedron(
        points=[
            [ size,  0,  0],
            [-size,  0,  0],
            [ 0,  size,  0],
            [ 0, -size,  0],
            [ 0,  0,  size],
            [ 0,  0, -size]
        ],
        faces=[
            [0, 2, 4],
            [2, 1, 4],
            [1, 3, 4],
            [3, 0, 4],
            [0, 5, 2],
            [2, 5, 1],
            [1, 5, 3],
            [3, 5, 0]
        ]
    );
}


module logo_on_block(length, width, height) {
    logo_width = 7;           // Width of the bottom box
    logo_height = 4;           // Height of the bottom box
    logo_top_scale = 0.8;      // Ratio of top box width to bottom box
    logo_spacing = 1.5;          // Vertical gap between the two boxes

    module logo_scaled(scale_factor) {
        scale([scale_factor, scale_factor, 1])
            logo();
    }

    module logo() {
        minkowski() {
            union() {
                // Bottom box
                translate([-logo_width/2, -logo_height/2, 0])
                    cube([logo_width, logo_height, logo_depth]);
                
                // Top box
                translate([-logo_width*logo_top_scale/2, logo_height/2 + logo_spacing, 0])
                    cube([logo_width*logo_top_scale, logo_height, logo_depth]);
            }
            sphere(r = 0.2, $fn = 24); 
        }
        
    }


    // Calculate logo bounding box size in Y (height) before scaling
    original_height = logo_height + logo_spacing + logo_height;

    scale_factor = logo_size / original_height;

    padding = logo_size*1.5 + chamfer_radius;

    
    x_pos = (logo_position == "center") ? 0 :
            (logo_position == "corner") ? (length/2) - padding :
            0;

    y_pos = (logo_position == "center") ? 0 :
            (logo_position == "corner") ? (width/2) - padding :
            0;

    z_pos = height/2;

    if (!(logo_position == "center" || logo_position == "corner")) {
        echo("Invalid logo_position. Use \"center\" or \"corner\".");
    }

    translate([x_pos, y_pos, z_pos]) {
        logo_scaled(scale_factor);
    }
}