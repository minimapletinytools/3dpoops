/*
 * Parametric Inline Hex Wrench Tool for Tight Spaces
 * 
 * This OpenSCAD file creates a specialized hex wrench with an opening on one side
 * to allow insertion into tight spaces where a traditional closed wrench won't fit.
 * 
 * Features:
 * - Parametric design for different hex sizes
 * - Side opening for tight space access
 * - Grip pattern for better handling
 * - Engraved size label
 * - Customizable parameters
 * 
 * Author: 吕 minimaple
 * License: MIT License
 * 
 * Usage:
 * 1. Adjust the parameters at the top of the file
 * 2. Render in OpenSCAD
 * 3. Export as STL for 3D printing
 * 
 * Parameter Guide:
 * - hex_size: Face-to-face distance of the hex nut (mm)
 * - wrench_depth: Thickness of the working part (mm)
 * - opening_size: Angle of the side opening (degrees)
 * - wall_thickness: Thickness of the wrench body walls (mm)
 * - label_text: Text to engrave on the wrench
 * - extrude_depth: Depth of the engraved text (mm)
 */

// =============================================================================
// PARAMETERS
// =============================================================================

// Hex wrench size (mm, face-to-face distance) 
hex_size = 17.4625;    // 11/16" = 17.4625mm

// Thickness of the working part (mm)
wrench_depth = 8;

// Wall thickness of the wrench body (mm)
wall_thickness = 10;

// Angle to open up one side (degrees)
opening_size = 120;

// Text to engrave on the wrench (update this to match the hex size in your choice of units)
label_text = "11/16\"";

// Depth of the engraved text (mm)
extrude_depth = 2;

// =============================================================================
// CONSTANTS
// =============================================================================

// Z-fighting prevention, do not change this
poop = 0.1;

// =============================================================================
// MODULES
// =============================================================================

/**
 * Engraves text on the top of the wrench
 */
module engrave_text() {
    hex_radius = hex_size * 1/sqrt(3);
    outer_radius = hex_radius + wall_thickness;
    
    // Position text at the top of the wrench with translation and rotation
    translate([-(hex_radius + outer_radius)/2, 0, wrench_depth - 0.5])
    rotate([0, 0, 90])
    linear_extrude(height = extrude_depth)
    text(label_text, 
         size = min(outer_radius * 0.3, 4), 
         halign = "center", 
         valign = "center",
         $fn = 20);
}

/**
 * Creates the main wrench body with hex cutout and side opening
 */
module hex_wrench() {
    // Convert face-to-face distance to radius
    // For hexagons: radius = face_distance / sqrt(3)
    hex_radius = hex_size * 1/sqrt(3);
    outer_radius = hex_radius + wall_thickness;
    
    difference() {
        // Outer cylinder (wrench body)
        cylinder(h = wrench_depth, r = outer_radius, $fn = 60);
        
        // Inner hex cutout (for the nut)
        translate([0, 0, -poop])
        cylinder(h = wrench_depth + 2*poop, r = hex_radius, $fn = 6);
        
        // Side opening cutout
        rotate([0, 0, -opening_size/2])
        translate([0, 0, -0.5])
        linear_extrude(height = wrench_depth + 1)
        polygon([
            [0, 0],
            [outer_radius * 2, 0],
            [outer_radius * 2 * cos(opening_size), outer_radius * 2 * sin(opening_size)],
            [0, 0]
        ]);
    }
}

/**
 * Adds grip pattern to the wrench body
 */
module wrench_with_grip() {
    hex_radius = hex_size * 1/sqrt(3);
    outer_radius = hex_radius + wall_thickness;
    
    union() {
        // Main wrench body
        hex_wrench();
        
        // Grip pattern on the outer surface
        for (i = [0:10]) {
            angle = i * 30;
            // Skip protrusions in the opening area
            if (angle < 360 - opening_size/2 && angle > opening_size/2) {
                rotate([0, 0, angle])
                translate([outer_radius, 0, 0])
                cylinder(h = wrench_depth, r = 1.5, $fn = 6);
            }
        }
    }
}

/**
 * Complete wrench with text engraving
 */
module complete_wrench() {
    difference() {
        // Wrench with grip pattern
        wrench_with_grip();
        
        // Engraved text
        engrave_text();
    }
}

// =============================================================================
// RENDERING
// =============================================================================

// Render the complete wrench
complete_wrench();

// =============================================================================
// DEBUG INFORMATION
// =============================================================================

// Echo parameters for verification
echo("=== Inline Hex Wrench Parameters ===");
echo("Hex size (face to face):", hex_size, "mm");
echo("Wrench depth:", wrench_depth, "mm");
echo("Opening angle:", opening_size, "degrees");
echo("Wall thickness:", wall_thickness, "mm");
echo("Label text:", label_text);
echo("Text depth:", extrude_depth, "mm");
echo("=====================================");
