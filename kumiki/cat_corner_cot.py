"""Cat Corner Cot - A timber frame cat cot designed against a corner supporting structure.

Defines:
1. house_footprint: The supporting "r"-shaped corner structure footprint.
   - Inside corner is at (0, 0).
   - Inside walls along +X (100") and -Y (70").
   - Wraps around back (+50" Y, -200" X, -120" Y).
2. cot_footprint: The 6' (X) x 64" (Y) footprint for the cot structure.
   - Corner nearest the inside corner sits at (1/2", -1/2").
3. Supporting structure timbers:
   - Two 15' tall timbers on corners 1 and 5 filling up the footprint and forming the 2 inside walls.
   - Trimmed along the roof slope using a custom HalfSpace joint to remove everything above the roof plane.
4. Supporting structure sloped roof:
   - Intersects with the front of the structure (Y = -70") at 11' (Z = 132").
   - Slopes upwards in +Y at 20 degrees.
   - Overhangs by 18" on all sides (including 18" overhanging into the inside corner).
   - Uses `cut_free_house_joint` with a cutout block located 18" out of the corner.
"""

from kumiki import *
from kumiki.cutcsg import HalfSpace, adopt_csg
from kumiki.joints.workshop.free_joints import cut_free_house_joint


# ============================================================================
# DIMENSIONS & CONSTANTS (Rule types)
# ============================================================================

# House supporting structure footprint dimensions
house_inside_corner_x = inches(100)           # Inside wall length along +X
house_inside_corner_y = inches(70)            # Inside wall length along -Y
house_back_right_up = inches(50)              # Up along +Y from right point
house_back_top_left = inches(200)             # Left along -X across top back
house_back_left_down = inches(120)            # Down along -Y along left back
house_wall_height = feet(15)                  # 15' tall supporting structure walls before roof trim

# Roof dimensions & parameters
roof_front_wall_intersect_z = feet(11)        # Roof intersects front wall (Y = -70") at 11' (132")
roof_slope_deg = degrees(20)                  # 20 degree upward slope along +Y
roof_overhang = inches(18)                    # 18" overhang on all sides
roof_thickness = inches(6)                    # 6" roof thickness

# Cat cot footprint dimensions
cot_width_x = feet(6)                         # 6' (72") width along X
cot_length_y = inches(64)                     # 64" length along Y
cot_corner_offset_x = inches(1, 2)            # 1/2" gap from house wall along X
cot_corner_offset_y = -inches(1, 2)           # 1/2" gap from house wall along Y (-0.5")


# ============================================================================
# FOOTPRINTS
# ============================================================================

# 1. Supporting structure ("r" corner shape wrapping around the back)
house_footprint_corners = [
    create_v2(inches(0), inches(0)),                                               # (0, 0) Inside corner
    create_v2(house_inside_corner_x, inches(0)),                                  # (100", 0) Right point (Corner 1)
    create_v2(house_inside_corner_x, house_back_right_up),                        # (100", 50") Up 50" (Corner 2)
    create_v2(house_inside_corner_x - house_back_top_left, house_back_right_up),  # (-100", 50") Left 200" (Corner 3)
    create_v2(-house_inside_corner_x, house_back_right_up - house_back_left_down), # (-100", -70") Down 120" (Corner 4)
    create_v2(inches(0), -house_inside_corner_y),                                 # (0, -70") Connects to inside -Y point (Corner 5)
]
house_footprint = Footprint(house_footprint_corners)

# 2. Cot structure footprint (6' x 64" starting at (1/2", -1/2"))
cot_footprint_corners = [
    create_v2(cot_corner_offset_x, cot_corner_offset_y - cot_length_y),                # (0.5", -64.5") Bottom-left
    create_v2(cot_corner_offset_x + cot_width_x, cot_corner_offset_y - cot_length_y),  # (72.5", -64.5") Bottom-right
    create_v2(cot_corner_offset_x + cot_width_x, cot_corner_offset_y),                 # (72.5", -0.5") Top-right
    create_v2(cot_corner_offset_x, cot_corner_offset_y),                                # (0.5", -0.5") Top-left
]
cot_footprint = Footprint(cot_footprint_corners)


# ============================================================================
# TIMBERS & JOINTS
# ============================================================================

def create_supporting_structure_timbers() -> list[Timber]:
    """
    Creates two 15' tall timbers on the bottom-right corners of the house footprint
    (corner 1 and corner 5) that fill the footprint and form the 2 inside walls.
    """
    # Top block (Corner 1 at (100", 0)):
    # Size: width=50" along +Y, depth=200" along -X -> spans [-100", 100"] x [0", 50"]
    top_wall = create_vertical_timber_on_footprint_corner(
        footprint=house_footprint,
        corner_index=1,
        length=house_wall_height,
        location_type=FootprintLocation.INSIDE,
        size=create_v2(house_back_right_up, house_back_top_left),
        ticket=TimberTicket(path="supporting_wall_top", tags=("house", "supporting_structure")),
    )

    # Left block (Corner 5 at (0, -70")):
    # Size: width=70" along +Y, depth=100" along -X -> spans [-100", 0"] x [-70", 0"]
    left_wall = create_vertical_timber_on_footprint_corner(
        footprint=house_footprint,
        corner_index=5,
        length=house_wall_height,
        location_type=FootprintLocation.INSIDE,
        size=create_v2(house_inside_corner_y, house_inside_corner_x),
        ticket=TimberTicket(path="supporting_wall_left", tags=("house", "supporting_structure")),
    )

    return [top_wall, left_wall]


def cut_roof_slope_trim_joint(wall_timbers: list[Timber], roof_plane_point: V3, roof_slope_angle: Numeric) -> Joint:
    """
    Custom joint that removes everything above the sloped roof plane from the given wall timbers
    by cutting away a HalfSpace matching the roof slope.
    """
    # Normal vector pointing UP perpendicular to the sloped roof: (0, -sin(theta), cos(theta))
    normal = create_v3(scalar(0), -sin(roof_slope_angle), cos(roof_slope_angle))
    offset = safe_dot_product(roof_plane_point, normal)
    global_halfspace = HalfSpace(normal=normal, offset=offset)

    cuttings = {}
    for i, timber in enumerate(wall_timbers):
        timber_local_hs = adopt_csg(None, timber.transform, global_halfspace)
        cutting = Cutting(timber=timber, negative_csg=timber_local_hs, label=f"roof_slope_cut_{i}")
        cuttings[f"wall_timber_{i}"] = cutting

    return Joint(
        cuttings=cuttings,
        ticket=JointTicket(path="roof_slope_wall_trim", joint_type="custom_halfspace_trim", tags=("roof", "wall_trim")),
    )


def create_supporting_roof_cut_timber() -> CutTimber:
    """
    Creates the sloped roof over the supporting structure:
    - 18" overhang on all sides
    - Intersects front wall (Y = -70") at 11' (Z = 132")
    - Slopes upward in +Y at 20 degrees
    - Uses cut_free_house_joint to remove the courtyard quadrant (18" out of the corner)
    """
    # House bounds
    house_x_min = -house_inside_corner_x       # -100"
    house_x_max = house_inside_corner_x        # 100"
    house_y_min = -house_inside_corner_y       # -70"
    house_y_max = house_back_right_up          # 50"

    # Overhanging roof dimensions
    roof_x_min = house_x_min - roof_overhang   # -118"
    roof_x_max = house_x_max + roof_overhang   # 118"
    roof_width_x = roof_x_max - roof_x_min     # 236"

    roof_y_min = house_y_min - roof_overhang   # -88"
    roof_y_max = house_y_max + roof_overhang   # 68"
    roof_span_y = roof_y_max - roof_y_min      # 156"

    # Length along the 20 degree slope
    roof_length = roof_span_y / cos(roof_slope_deg)

    # Direction vectors for sloped timber
    length_dir = create_v3(scalar(0), cos(roof_slope_deg), sin(roof_slope_deg))
    width_dir = create_v3(scalar(1), scalar(0), scalar(0))

    # Elevation: intersects front wall at 11' (Y = -70", Z = 11' = 132")
    z_at_front_eave = roof_front_wall_intersect_z - roof_overhang * tan(roof_slope_deg)

    bottom_pos = create_v3(
        scalar(0),
        roof_y_min,
        z_at_front_eave,
    )

    # Full blank overhanging roof timber
    roof_timber = create_timber(
        length=roof_length,
        size=create_v2(roof_width_x, roof_thickness),
        bottom_position=bottom_pos,
        length_direction=length_dir,
        width_direction=width_dir,
        ticket=TimberTicket(path="supporting_roof", tags=("roof", "supporting_structure")),
    )

    # Cutout block: 18" out of the corner (starts at X = 18", Y = -18")
    cutout_x_start = roof_overhang             # 18"
    cutout_y_start = -roof_overhang            # -18"
    cutout_width_x = inches(150)               # Extends past X = 118"
    cutout_depth_y = inches(120)               # Extends past Y = -88"
    cutout_height = feet(25)                   # Tall enough to clear 25'

    cutout_bottom_center = create_v3(
        cutout_x_start + cutout_width_x / scalar(2),
        cutout_y_start - cutout_depth_y / scalar(2),
        scalar(0),
    )

    cutout_timber = create_axis_aligned_timber(
        bottom_position=cutout_bottom_center,
        length=cutout_height,
        size=create_v2(cutout_width_x, cutout_depth_y),
        length_direction=TimberFace.TOP,
        width_direction=TimberFace.RIGHT,
        ticket=TimberTicket(path="roof_cutout_block", tags=("cutter",)),
    )

    # Free house joint to remove the cutout block from the roof timber
    roof_joint = cut_free_house_joint(
        housing_timber=roof_timber,
        housed_timbers=[cutout_timber],
    )

    return CutTimber(
        timber=roof_timber,
        cuts=[roof_joint.cuttings["housing_timber"]],
    )


# ============================================================================
# FRAME DEFINITION
# ============================================================================

def build_frame() -> Frame:
    """Build the cat corner cot frame with supporting walls and trimmed sloped roof."""
    # 1. Create the two supporting wall timbers
    top_wall, left_wall = create_supporting_structure_timbers()

    # 2. Trim the walls along the 20 degree roof slope plane intersecting at 11' at front wall
    roof_plane_datum = create_v3(scalar(0), -house_inside_corner_y, roof_front_wall_intersect_z)
    wall_trim_joint = cut_roof_slope_trim_joint([top_wall, left_wall], roof_plane_datum, roof_slope_deg)

    cut_top_wall = CutTimber(
        timber=top_wall,
        cuts=[wall_trim_joint.cuttings["wall_timber_0"]],
    )
    cut_left_wall = CutTimber(
        timber=left_wall,
        cuts=[wall_trim_joint.cuttings["wall_timber_1"]],
    )

    # 3. Create the cut roof timber
    cut_roof = create_supporting_roof_cut_timber()

    return Frame(
        cut_timbers=[
            cut_top_wall,
            cut_left_wall,
            cut_roof,
        ],
        accessories=[],
        name="Cat Corner Cot",
        footprints=[house_footprint, cot_footprint],
    )


example = build_frame
