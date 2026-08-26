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
5. Cat cot structure:
   - 3 3/8" square posts (12' tall) on the bottom-left, bottom-right, and top-right corners of cot_footprint.
   - 3 3/8" square rim joists around the entire footprint perimeter at floor height 16" (top of rim joist at 16").
   - 3 evenly spaced 3 3/8" square floor joists running from the front to back rim joists (center joist aligned with mid stud).
   - 3 3/8" square front rail at 54" rail height (top of rail at 54") between the two front posts.
   - 3 3/8" square vertical center stud connecting the front rail to the front rim joist right in the middle.
   - 3 3/8" square door post on the right rim joist with a 28" door opening from the front post.
   - 3 3/8" square right rail at 54" rail height connecting the door post to the back-right post.
   - Horizontal infill wall boards (3/4" thick, 3-6" wide face) filling the bays between posts, rim joists, and rails,
     extending 3/8" into posts and rails, resting flush on the rim joists.
   - 3 3/8" square upper roof support beams:
     - Back beam at back_beam_height (top at 11' / 132"), reaching inside corner to the left and sticking out 6" to the right.
     - Front beam over front posts, lowered based on the 20 degree roof pitch to match the support structure roof pitch.
"""

import math
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

# Cat cot timber dimensions
cot_timber_cross_section = inches(27, 8)      # 3 3/8" square (nominal 4x4 actual size)
cot_timber_size = create_v2(cot_timber_cross_section, cot_timber_cross_section)
cot_post_height = feet(12)                    # 12' tall posts (reach past 11' roof beams)
cot_floor_height = inches(16)                 # Top of rim joists at 16" from ground
cot_rail_height = inches(54)                  # Top of rails at 54" from ground
cot_door_width = inches(28)                   # 28" clear door opening on right side

# Floor joist parameters
cot_num_floor_joists = 3                      # 3 evenly spaced floor joists

# Infill board dimensions
cot_board_thickness = inches(3, 4)            # 3/4" thick boards
cot_board_post_penetration = inches(3, 8)     # 3/8" into each post
cot_board_rail_penetration = inches(3, 8)     # 3/8" into rail underside
cot_board_rim_penetration = scalar(0)         # 0" into rim joist (rests flush)
cot_board_max_width = inches(6)               # Max board face width (prefer wider)
cot_board_min_width = inches(3)               # Min board face width

# Upper roof support beam dimensions
back_beam_height = feet(11)                   # Top of back beam at 11' (132") from ground
beam_stickout_right = inches(6)               # 6" stickout past right posts


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
    create_v2(cot_corner_offset_x, cot_corner_offset_y - cot_length_y),                # (0.5", -64.5") Bottom-left (Corner 0)
    create_v2(cot_corner_offset_x + cot_width_x, cot_corner_offset_y - cot_length_y),  # (72.5", -64.5") Bottom-right (Corner 1)
    create_v2(cot_corner_offset_x + cot_width_x, cot_corner_offset_y),                 # (72.5", -0.5") Top-right (Corner 2)
    create_v2(cot_corner_offset_x, cot_corner_offset_y),                                # (0.5", -0.5") Top-left (Corner 3)
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


def create_cot_posts() -> list[Timber]:
    """
    Creates three 12' tall, 3 3/8" square posts on the cat cot footprint:
    - Corner 0: Bottom-Left (0.5", -64.5")
    - Corner 1: Bottom-Right (72.5", -64.5")
    - Corner 2: Top-Right (72.5", -0.5")
    """
    # 1. Bottom-Left post
    post_bl = create_vertical_timber_on_footprint_corner(
        footprint=cot_footprint,
        corner_index=0,
        length=cot_post_height,
        location_type=FootprintLocation.INSIDE,
        size=cot_timber_size,
        ticket=TimberTicket(path="cot_post_BL", tags=("post", "cot", "3_3_8x3_3_8")),
    )

    # 2. Bottom-Right post
    post_br = create_vertical_timber_on_footprint_corner(
        footprint=cot_footprint,
        corner_index=1,
        length=cot_post_height,
        location_type=FootprintLocation.INSIDE,
        size=cot_timber_size,
        ticket=TimberTicket(path="cot_post_BR", tags=("post", "cot", "3_3_8x3_3_8")),
    )

    # 3. Top-Right post
    post_tr = create_vertical_timber_on_footprint_corner(
        footprint=cot_footprint,
        corner_index=2,
        length=cot_post_height,
        location_type=FootprintLocation.INSIDE,
        size=cot_timber_size,
        ticket=TimberTicket(path="cot_post_TR", tags=("post", "cot", "3_3_8x3_3_8")),
    )

    return [post_bl, post_br, post_tr]


def create_cot_rim_joists() -> list[Timber]:
    """
    Creates four 3 3/8" square rim joists around the cot footprint perimeter.
    The top of the rim joists is at 16" from the ground (floor height).
    - Front rim joist: spans along X between BL and BR
    - Right rim joist: spans along Y between BR and TR
    - Back rim joist: spans along X between TR and the open corner (wall supported)
    - Left rim joist: spans along Y between the open corner and BL (wall supported)
    """
    z_center = cot_floor_height - cot_timber_cross_section / scalar(2)

    x_start = cot_corner_offset_x
    x_length = cot_width_x
    x_end = x_start + x_length

    y_start = cot_corner_offset_y - cot_length_y
    y_length = cot_length_y
    y_end = cot_corner_offset_y

    # 1. Front Rim Joist (along +X, at y_start)
    front_rim = create_axis_aligned_timber(
        bottom_position=create_v3(x_start, y_start + cot_timber_cross_section / scalar(2), z_center),
        length=x_length,
        size=cot_timber_size,
        length_direction=TimberFace.RIGHT,
        width_direction=TimberFace.TOP,
        ticket=TimberTicket(path="cot_rim_joist_front", tags=("rim_joist", "floor", "cot")),
    )

    # 2. Right Rim Joist (along +Y, at x_end)
    right_rim = create_axis_aligned_timber(
        bottom_position=create_v3(x_end - cot_timber_cross_section / scalar(2), y_start, z_center),
        length=y_length,
        size=cot_timber_size,
        length_direction=TimberFace.FRONT,
        width_direction=TimberFace.TOP,
        ticket=TimberTicket(path="cot_rim_joist_right", tags=("rim_joist", "floor", "cot")),
    )

    # 3. Back Rim Joist (along +X, at y_end)
    back_rim = create_axis_aligned_timber(
        bottom_position=create_v3(x_start, y_end - cot_timber_cross_section / scalar(2), z_center),
        length=x_length,
        size=cot_timber_size,
        length_direction=TimberFace.RIGHT,
        width_direction=TimberFace.TOP,
        ticket=TimberTicket(path="cot_rim_joist_back", tags=("rim_joist", "floor", "cot")),
    )

    # 4. Left Rim Joist (along +Y, at x_start)
    left_rim = create_axis_aligned_timber(
        bottom_position=create_v3(x_start + cot_timber_cross_section / scalar(2), y_start, z_center),
        length=y_length,
        size=cot_timber_size,
        length_direction=TimberFace.FRONT,
        width_direction=TimberFace.TOP,
        ticket=TimberTicket(path="cot_rim_joist_left", tags=("rim_joist", "floor", "cot")),
    )

    return [front_rim, right_rim, back_rim, left_rim]


def create_cot_floor_joists() -> list[Timber]:
    """
    Creates 3 evenly spaced 3 3/8" square floor joists running from the front
    rim joist to the back rim joist at 16" floor height.
    Middle joist (joist 2) aligns with the front center stud at X = 36.5".
    """
    z_center = cot_floor_height - cot_timber_cross_section / scalar(2)

    x_start = cot_corner_offset_x
    x_length = cot_width_x
    y_start = cot_corner_offset_y - cot_length_y
    y_length = cot_length_y

    spacing = x_length / scalar(cot_num_floor_joists + 1)

    joists = []
    for i in range(1, cot_num_floor_joists + 1):
        x_pos = x_start + spacing * scalar(i)
        joist = create_axis_aligned_timber(
            bottom_position=create_v3(x_pos, y_start, z_center),
            length=y_length,
            size=cot_timber_size,
            length_direction=TimberFace.FRONT,
            width_direction=TimberFace.TOP,
            ticket=TimberTicket(path=f"cot_floor_joist_{i}", tags=("floor_joist", "floor", "cot", "3_3_8x3_3_8")),
        )
        joists.append(joist)

    return joists


def create_cot_rails_and_studs() -> list[Timber]:
    """
    Creates front rail, front middle stud, right door post, and right rail.
    - Front rail: 3 3/8" square, top at 54", spans between front posts
    - Front mid stud: 3 3/8" square, right in the middle (X = 36.5"), connecting rim joist to rail
    - Right door post: 3 3/8" square, 12' tall, 28" door opening from the front-right post
    - Right rail: 3 3/8" square, top at 54", connecting door post to back-right post
    """
    timber_cs = cot_timber_cross_section
    x_start = cot_corner_offset_x                                        # 0.5"
    x_length = cot_width_x                                               # 72"
    x_end = x_start + x_length                                           # 72.5"
    x_center = x_start + x_length / scalar(2)                            # 36.5"
    x_right_center = x_end - timber_cs / scalar(2)                       # 70.8125"

    y_start = cot_corner_offset_y - cot_length_y                         # -64.5"
    y_length = cot_length_y                                              # 64"
    y_end = cot_corner_offset_y                                          # -0.5"
    y_front_center = y_start + timber_cs / scalar(2)                     # -62.8125"

    z_center_rail = cot_rail_height - timber_cs / scalar(2)

    # 1. Front Rail
    front_rail = create_axis_aligned_timber(
        bottom_position=create_v3(x_start, y_front_center, z_center_rail),
        length=x_length,
        size=cot_timber_size,
        length_direction=TimberFace.RIGHT,
        width_direction=TimberFace.TOP,
        ticket=TimberTicket(path="cot_rail_front", tags=("rail", "cot", "3_3_8x3_3_8")),
    )

    # 2. Middle Stud connecting front rail to front rim joist
    stud_bottom_z = cot_floor_height                                     # 16"
    stud_length = (cot_rail_height - timber_cs) - cot_floor_height       # 34 5/8"

    front_mid_stud = create_axis_aligned_timber(
        bottom_position=create_v3(x_center, y_front_center, stud_bottom_z),
        length=stud_length,
        size=cot_timber_size,
        length_direction=TimberFace.TOP,
        width_direction=TimberFace.RIGHT,
        ticket=TimberTicket(path="cot_stud_front_mid", tags=("stud", "cot", "3_3_8x3_3_8")),
    )

    # 3. Right Door Post (space between front-right post and door post is door_width = 28")
    door_post_y_front = y_start + timber_cs + cot_door_width             # -33.125"
    door_post_y_center = door_post_y_front + timber_cs / scalar(2)       # -31.4375"

    door_post_right = create_axis_aligned_timber(
        bottom_position=create_v3(x_right_center, door_post_y_center, scalar(0)),
        length=cot_post_height,
        size=cot_timber_size,
        length_direction=TimberFace.TOP,
        width_direction=TimberFace.FRONT,
        ticket=TimberTicket(path="cot_post_door_right", tags=("post", "cot", "door_post", "3_3_8x3_3_8")),
    )

    # 4. Right Rail connecting door post to back-right post (top at 54")
    rail_right_start_y = door_post_y_front
    rail_right_length = y_end - rail_right_start_y

    right_rail = create_axis_aligned_timber(
        bottom_position=create_v3(x_right_center, rail_right_start_y, z_center_rail),
        length=rail_right_length,
        size=cot_timber_size,
        length_direction=TimberFace.FRONT,
        width_direction=TimberFace.TOP,
        ticket=TimberTicket(path="cot_rail_right", tags=("rail", "cot", "3_3_8x3_3_8")),
    )

    return [front_rail, front_mid_stud, door_post_right, right_rail]


def fill_bay_with_horizontal_boards(
    start_along_span: Numeric,
    end_along_span: Numeric,
    span_direction: TimberFace,
    fixed_coordinate: Numeric,
    bottom_z: Numeric,
    top_z: Numeric,
    penetration_posts: Numeric = cot_board_post_penetration,
    penetration_rail: Numeric = cot_board_rail_penetration,
    penetration_rim: Numeric = cot_board_rim_penetration,
    board_thickness: Numeric = cot_board_thickness,
    max_board_width: Numeric = cot_board_max_width,
    bay_label: str = "bay",
) -> list[Timber]:
    """
    Helper function to fill a rectangular wall bay formed by posts, a rim joist below,
    and a rail above with horizontal wall boards.
    - Boards extend into bounding posts by `penetration_posts` (3/8") on each end.
    - Top board extends into the rail underside by `penetration_rail` (3/8").
    - Bottom board rests on the rim joist top face (`penetration_rim` = 0").
    - Calculates the number of boards to prefer wider boards (up to `max_board_width` = 6"),
      distributing the total height evenly so boards fit perfectly as flat wall boards.
    """
    total_height = (top_z + penetration_rail) - (bottom_z - penetration_rim)
    num_boards = math.ceil(float(total_height) / float(max_board_width))
    board_width = total_height / scalar(num_boards)

    span_length = (end_along_span - start_along_span) + scalar(2) * penetration_posts
    start_pos = start_along_span - penetration_posts

    boards = []
    for i in range(num_boards):
        z_bot = (bottom_z - penetration_rim) + board_width * scalar(i)
        z_mid = z_bot + board_width / scalar(2)

        if span_direction == TimberFace.RIGHT:
            bot_pos = create_v3(start_pos, fixed_coordinate, z_mid)
            length_dir = TimberFace.RIGHT
            width_dir = TimberFace.TOP
        else:
            bot_pos = create_v3(fixed_coordinate, start_pos, z_mid)
            length_dir = TimberFace.FRONT
            width_dir = TimberFace.TOP

        board = create_axis_aligned_timber(
            bottom_position=bot_pos,
            length=span_length,
            size=create_v2(board_width, board_thickness),
            length_direction=length_dir,
            width_direction=width_dir,
            ticket=TimberTicket(path=f"{bay_label}_board_{i}", tags=("board", "infill", "cot")),
        )
        boards.append(board)

    return boards


def create_cot_infill_boards() -> list[Timber]:
    """
    Creates horizontal infill boards for all walled bays:
    1. Front-Left Bay: between BL post and center stud
    2. Front-Right Bay: between center stud and BR post
    3. Right-Back Bay: between door post and TR post
    """
    timber_cs = cot_timber_cross_section
    x_start = cot_corner_offset_x
    x_length = cot_width_x
    x_end = x_start + x_length
    x_mid = x_start + x_length / scalar(2)

    y_start = cot_corner_offset_y - cot_length_y
    y_end = cot_corner_offset_y
    y_front_center = y_start + timber_cs / scalar(2)
    x_right_center = x_end - timber_cs / scalar(2)

    bottom_z = cot_floor_height
    top_z = cot_rail_height - timber_cs

    # 1. Front-Left Bay
    post_bl_inner_x = x_start + timber_cs
    stud_left_x = x_mid - timber_cs / scalar(2)
    front_left_boards = fill_bay_with_horizontal_boards(
        start_along_span=post_bl_inner_x,
        end_along_span=stud_left_x,
        span_direction=TimberFace.RIGHT,
        fixed_coordinate=y_front_center,
        bottom_z=bottom_z,
        top_z=top_z,
        bay_label="bay_fl",
    )

    # 2. Front-Right Bay
    stud_right_x = x_mid + timber_cs / scalar(2)
    post_br_inner_x = x_end - timber_cs
    front_right_boards = fill_bay_with_horizontal_boards(
        start_along_span=stud_right_x,
        end_along_span=post_br_inner_x,
        span_direction=TimberFace.RIGHT,
        fixed_coordinate=y_front_center,
        bottom_z=bottom_z,
        top_z=top_z,
        bay_label="bay_fr",
    )

    # 3. Right-Back Bay
    door_post_y_back = y_start + timber_cs + cot_door_width + timber_cs
    post_tr_y_front = y_end - timber_cs
    right_back_boards = fill_bay_with_horizontal_boards(
        start_along_span=door_post_y_back,
        end_along_span=post_tr_y_front,
        span_direction=TimberFace.FRONT,
        fixed_coordinate=x_right_center,
        bottom_z=bottom_z,
        top_z=top_z,
        bay_label="bay_rb",
    )

    return front_left_boards + front_right_boards + right_back_boards


def create_cot_roof_beams() -> list[Timber]:
    """
    Creates upper roof support beams across the cot:
    - Back beam: top at back_beam_height (11' / 132"), reaches inside corner to the left (X = 0.5")
      and sticks out 6" past the right posts (X = 78.5").
    - Front beam: over front posts, lowered based on the 20 degree roof pitch:
      delta_z = delta_y * tan(20 degrees) so a roof placed over both beams matches the roof pitch.
    """
    timber_cs = cot_timber_cross_section
    x_start = cot_corner_offset_x                                        # 0.5"
    x_length = cot_width_x                                               # 72"
    beam_length = x_length + beam_stickout_right                         # 78"

    y_start = cot_corner_offset_y - cot_length_y                         # -64.5"
    y_end = cot_corner_offset_y                                          # -0.5"

    y_back_center = y_end - timber_cs / scalar(2)                        # -2.1875"
    y_front_center = y_start + timber_cs / scalar(2)                     # -62.8125"

    delta_y = y_back_center - y_front_center                             # 60.625"
    delta_z = delta_y * tan(roof_slope_deg)                              # ~22.066"
    front_beam_height = back_beam_height - delta_z                       # ~109.934"

    z_center_back_beam = back_beam_height - timber_cs / scalar(2)
    z_center_front_beam = front_beam_height - timber_cs / scalar(2)

    # 1. Back Beam
    back_beam = create_axis_aligned_timber(
        bottom_position=create_v3(x_start, y_back_center, z_center_back_beam),
        length=beam_length,
        size=cot_timber_size,
        length_direction=TimberFace.RIGHT,
        width_direction=TimberFace.TOP,
        ticket=TimberTicket(path="cot_beam_back", tags=("beam", "cot", "3_3_8x3_3_8")),
    )

    # 2. Front Beam
    front_beam = create_axis_aligned_timber(
        bottom_position=create_v3(x_start, y_front_center, z_center_front_beam),
        length=beam_length,
        size=cot_timber_size,
        length_direction=TimberFace.RIGHT,
        width_direction=TimberFace.TOP,
        ticket=TimberTicket(path="cot_beam_front", tags=("beam", "cot", "3_3_8x3_3_8")),
    )

    return [back_beam, front_beam]


# ============================================================================
# FRAME DEFINITION
# ============================================================================

def build_frame() -> Frame:
    """Build the complete cat corner cot frame."""
    # 1. Supporting structure walls
    top_wall, left_wall = create_supporting_structure_timbers()

    # 2. Trim walls along the 20 degree roof slope plane
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

    # 3. Supporting structure sloped roof
    cut_roof = create_supporting_roof_cut_timber()

    # 4. Cat cot 3 posts (BL, BR, TR)
    cot_posts = create_cot_posts()

    # 5. Cat cot 4 rim joists at 16" floor height
    cot_rim_joists = create_cot_rim_joists()

    # 6. Cat cot 3 evenly spaced floor joists
    cot_floor_joists = create_cot_floor_joists()

    # 7. Cat cot rails, studs, and door post
    cot_rails_and_studs = create_cot_rails_and_studs()

    # 8. Infill wall boards for all 3 bays
    cot_infill_boards = create_cot_infill_boards()

    # 9. Upper roof support beams (back and front)
    cot_roof_beams = create_cot_roof_beams()

    return Frame(
        cut_timbers=[
            cut_top_wall,
            cut_left_wall,
            cut_roof,
            *[CutTimber(p) for p in cot_posts],
            *[CutTimber(r) for r in cot_rim_joists],
            *[CutTimber(j) for j in cot_floor_joists],
            *[CutTimber(m) for m in cot_rails_and_studs],
            *[CutTimber(b) for b in cot_infill_boards],
            *[CutTimber(bm) for bm in cot_roof_beams],
        ],
        accessories=[],
        name="Cat Corner Cot",
        footprints=[house_footprint, cot_footprint],
    )


example = build_frame
