from codetocad import *


base_offset = -30
# Create the rectangular base
base = Part("base")
base.create_cube(115, 203, 12)
base.translate_y(base_offset)

# Create landmarks for hole positioning
base.create_landmark("main_hole_center", 0, 0, 0)  # Center of base
base.create_landmark("mounting_hole1", -16, 55, 0)  # Left mounting hole
base.create_landmark("mounting_hole2", 16, 55, 0)   # Right mounting hole

# Get landmark positions
main_hole_landmark = base.get_landmark("main_hole_center")
mounting_hole1_landmark = base.get_landmark("mounting_hole1")
mounting_hole2_landmark = base.get_landmark("mounting_hole2")

# Get landmark world positions
main_hole_pos = main_hole_landmark.get_location_world()
mounting_hole1_pos = mounting_hole1_landmark.get_location_world()
mounting_hole2_pos = mounting_hole2_landmark.get_location_world()

# Create the main hole
hole = Part("hole")
hole.create_cylinder(39.5, 12.7)  # radius = diameter/2, height = base thickness
hole.translate_xyz(main_hole_pos.x, main_hole_pos.y, main_hole_pos.z)

# Create two mounting holes on the +y side
# 30.48mm apart in X, 53.34mm in Y from the main hole
mounting_hole1 = Part("mounting_hole1")
mounting_hole1.create_cylinder(2.87, 12.7)  # 6.35mm diameter hole
mounting_hole1.translate_xyz(mounting_hole1_pos.x, mounting_hole1_pos.y, mounting_hole1_pos.z)

mounting_hole2 = Part("mounting_hole2")
mounting_hole2.create_cylinder(2.87, 12.7)  # 6.35mm diameter hole
mounting_hole2.translate_xyz(mounting_hole2_pos.x, mounting_hole2_pos.y, mounting_hole2_pos.z)

# Subtract all holes from the base
base.subtract(hole)
base.subtract(mounting_hole1)
base.subtract(mounting_hole2)

# Add two narrow support rectangles along the long edges
support_width = 10
support_height = 10
base_length =203
base_width = 115

# Left support - runs along the left long edge
left_support = Part("left_support")
left_support.create_cube(support_width, base_length, support_height)
# Position: flush with left side, on top of base
left_support.translate_xyz(-base_width/2 + support_width/2, base_offset, support_height)

# Right support - runs along the right long edge
right_support = Part("right_support")
right_support.create_cube(support_width, base_length, support_height)
# Position: flush with right side, on top of base
right_support.translate_xyz(base_width/2 - support_width/2, base_offset, support_height)

# make a clamping platform between the supports and the left 1/3 of the base
clamping_platform = Part("clamping_platform")
clamping_platform.create_cube(base_width, base_length/3, support_height)
clamping_platform.translate_xyz(0, base_offset - base_length/3, support_height)

# Union supports to base
base.union(left_support)
base.union(right_support)
base.union(clamping_platform)

# Fillet all edges
base.fillet_all_edges(5)

# Export the result
base.export("locline_tablemount.stl")

