from codetocad import *

# Create the rectangular base
# Dimensions: 101.6mm x 203.2mm x 12.7mm thick
base = Part("base")
base.create_cube(101.6, 203.2, 12.7)
base.translate_y(38.1)
base.hole(base.PresetLandmark.bottom, 39.29, 100)

# Create landmarks for hole positioning
base.create_landmark("main_hole_center", 0, 0, 0)  # Center of base
base.create_landmark("mounting_hole1", -15.24, 53.34, 0)  # Left mounting hole
base.create_landmark("mounting_hole2", 15.24, 53.34, 0)   # Right mounting hole

# Get landmark positions
main_hole_landmark = base.get_landmark("main_hole_center")
mounting_hole1_landmark = base.get_landmark("mounting_hole1")
mounting_hole2_landmark = base.get_landmark("mounting_hole2")

# Get landmark world positions
main_hole_pos = main_hole_landmark.get_location_world()
mounting_hole1_pos = mounting_hole1_landmark.get_location_world()
mounting_hole2_pos = mounting_hole2_landmark.get_location_world()

# Create holes using the hole() function
# Main hole diameter: 78.58mm (3.09375 inches)
base.hole(main_hole_landmark, 39.29, 100)  # landmark, radius, depth

# Create two mounting holes on the +y side
# 30.48mm apart in X, 53.34mm in Y from the main hole
base.hole(mounting_hole1_landmark, 3.175, 12.7)  # 6.35mm diameter hole
base.hole(mounting_hole2_landmark, 3.175, 12.7)  # 6.35mm diameter hole

# Export the result
base.export("locline_tablemount.stl")

