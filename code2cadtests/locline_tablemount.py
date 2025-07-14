from codetocad import *

Scene().set_default_unit("in")

# Create the rectangular base
# Dimensions: 4" x 6" x 0.5" thick
base = Part("base")
base.create_cube(4, 8, 0.5)
base.translate_y(1.5)

# Create the hole
# Hole diameter: 3 3/32 inches (3.09375 inches)
# Position: centered in 4" dimension, 1" from side in 6" dimension
hole = Part("hole")
hole.create_cylinder(3.09375/2, 0.5)  # radius = diameter/2, height = base thickness


# Create two mounting holes on the +y side
# 1.2 inches apart in X, 2.1 inches in Y from the main hole
mounting_hole1 = Part("mounting_hole1")
mounting_hole1.create_cylinder(0.125, 0.5)  # 1/4 inch diameter hole
mounting_hole1.translate_x(-0.6)  # 0.6 inches to the left (1.2 inches apart = 0.6 inches each side)
mounting_hole1.translate_y(2.1)  # 2.1 inches in +y direction

mounting_hole2 = Part("mounting_hole2")
mounting_hole2.create_cylinder(0.125, 0.5)  # 1/4 inch diameter hole
mounting_hole2.translate_x(0.6)   # 0.6 inches to the right (1.2 inches apart = 0.6 inches each side)
mounting_hole2.translate_y(2.1)  # 2.1 inches in +y direction

# Subtract all holes from the base
base.subtract(hole)
base.subtract(mounting_hole1)
base.subtract(mounting_hole2)

# Export the result
base.export("locline_tablemount.stl")
