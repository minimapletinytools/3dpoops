from codetocad import *

# Create the rectangular base
# Dimensions: 101.6mm x 203.2mm x 12.7mm thick
base = Part("base")
base.create_cube(101.6, 203.2, 12.7)
base.translate_y(38.1)

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

# Fillet all edges
base.fillet_all_edges(5)

# Export the result
base.export("locline_tablemount.stl")

