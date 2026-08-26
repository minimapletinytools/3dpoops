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
   - 3 3/8" square posts on corners:
     - BL post stops under front rail at Z = 50 5/8".
     - BR post connects into underside of front roof beam.
     - TR post connects into underside of back roof beam.
     - Upper front-left post sits on front rail, offset 1.5" from wall, and connects into front roof beam.
     - Door post on right side connects into underside of right side tie beam.
   - 3 3/8" square rim joists around the entire footprint perimeter at floor height 16" (top of rim joist at 16").
   - 3 evenly spaced 3 3/8" square floor joists running from the front to back rim joists (center joist aligned with mid stud).
   - Mortise and tenon joints connecting rim joists to corner posts:
     - 1" x 1.5" tenons, 3" long (stopped, not extending beyond posts).
     - Offset vertically (+13/16" for X-running rim joists, -13/16" for Y-running rim joists) to prevent intersection.
     - Held in place by 5/8" square through-pegs.
   - 3 3/8" square front rail at 54" rail height (top of rail at 54") between the two front posts:
     - BL post connects into underside of front rail with 1.5" x 1" tenon (offset from rail end to prevent blowout).
     - Upper left post connects into top of front rail with 1.5" x 1" tenon offset to the right so it doesn't intersect with the bottom post tenon.
     - Front rail connects into BR post with 3" x 1" tenon.
   - 3 3/8" square vertical center stud connecting the front rail to the front rim joist right in the middle.
   - 3 3/8" square door post on the right rim joist with a 28" door opening from the front post.
   - 3 3/8" square right rail at 54" rail height connecting the door post to the back-right post (3" x 1" tenons).
   - 3 3/8" square right side tie beam:
     - Placed 4" below the top of the front roof beam.
     - Connects post BR to post TR with mortise and tenon joints.
     - Mid door post connects into its underside with a mortise and tenon joint.
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
from kumiki.construction import ButtJointTimberArrangement
from kumiki.joints.workshop.mortise_and_tenon_joints import cut_mortise_and_tenon_joint_on_face_aligned_timbers
from kumiki.joints.workshop.shavings.build_a_butt import SimplePegParameters, PegShape


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
cot_floor_height = inches(16)                 # Top of rim joists at 16" from ground
cot_rail_height = inches(54)                  # Top of rails at 54" from ground
cot_door_width = inches(28)                   # 28" clear door opening on right side

# Floor joist parameters
cot_num_floor_joists = 3                      # 3 evenly spaced floor joists

# Mortise and Tenon joint parameters
cot_rim_tenon_thickness = inches(1)           # 1" tenon thickness
cot_rim_tenon_height = inches(3, 2)           # 1.5" tenon height for rim joists
cot_rim_tenon_length = inches(3)              # 3" tenon length (stopped within 3 3/8" post)
cot_peg_size = inches(5, 8)                   # 5/8" square peg
cot_rail_tenon_width = inches(3)              # 3" wide tenon for non-intersecting rail joints

# Upper left post parameters
cot_upper_left_post_offset_x = inches(3, 2)   # 1.5" offset away from house wall at X = 0

# Right side tie beam parameters
cot_side_beam_drop_from_plate = inches(4)     # 4" below top of front roof plate

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
    top_wall = create_vertical_timber_on_footprint_corner(
        footprint=house_footprint,
        corner_index=1,
        length=house_wall_height,
        location_type=FootprintLocation.INSIDE,
        size=create_v2(house_back_right_up, house_back_top_left),
        ticket=TimberTicket(path="supporting_wall_top", tags=("house", "supporting_structure")),
    )

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
    house_x_min = -house_inside_corner_x       # -100"
    house_x_max = house_inside_corner_x        # 100"
    house_y_min = -house_inside_corner_y       # -70"
    house_y_max = house_back_right_up          # 50"

    roof_x_min = house_x_min - roof_overhang   # -118"
    roof_x_max = house_x_max + roof_overhang   # 118"
    roof_width_x = roof_x_max - roof_x_min     # 236"

    roof_y_min = house_y_min - roof_overhang   # -88"
    roof_y_max = house_y_max + roof_overhang   # 68"
    roof_span_y = roof_y_max - roof_y_min      # 156"

    roof_length = roof_span_y / cos(roof_slope_deg)

    length_dir = create_v3(scalar(0), cos(roof_slope_deg), sin(roof_slope_deg))
    width_dir = create_v3(scalar(1), scalar(0), scalar(0))

    z_at_front_eave = roof_front_wall_intersect_z - roof_overhang * tan(roof_slope_deg)

    bottom_pos = create_v3(
        scalar(0),
        roof_y_min,
        z_at_front_eave,
    )

    roof_timber = create_timber(
        length=roof_length,
        size=create_v2(roof_width_x, roof_thickness),
        bottom_position=bottom_pos,
        length_direction=length_dir,
        width_direction=width_dir,
        ticket=TimberTicket(path="supporting_roof", tags=("roof", "supporting_structure")),
    )

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

    roof_joint = cut_free_house_joint(
        housing_timber=roof_timber,
        housed_timbers=[cutout_timber],
    )

    return CutTimber(
        timber=roof_timber,
        cuts=[roof_joint.cuttings["housing_timber"]],
    )


def compute_front_beam_height() -> Numeric:
    """Computes the top elevation of the front roof support beam based on roof pitch."""
    timber_cs = cot_timber_cross_section
    y_start = cot_corner_offset_y - cot_length_y
    y_end = cot_corner_offset_y
    y_back_center = y_end - timber_cs / scalar(2)
    y_front_center = y_start + timber_cs / scalar(2)
    delta_y = y_back_center - y_front_center
    delta_z = delta_y * tan(roof_slope_deg)
    return back_beam_height - delta_z


def create_cot_posts() -> list[Timber]:
    """
    Creates four 3 3/8" square posts on the cat cot:
    - Corner 0: Bottom-Left post connects into underside of front rail (top at 50 5/8")
    - Corner 1: Bottom-Right post connects into underside of front beam
    - Corner 2: Top-Right post connects into underside of back beam
    - Upper Left Post: sits on front rail (offset 1.5" from house wall) and reaches front beam
    """
    timber_cs = cot_timber_cross_section
    front_beam_top_z = compute_front_beam_height()
    front_beam_bottom_z = front_beam_top_z - timber_cs
    back_beam_bottom_z = back_beam_height - timber_cs

    bl_post_height = cot_rail_height - timber_cs  # 50 5/8"

    # 1. Bottom-Left Post
    post_bl = create_vertical_timber_on_footprint_corner(
        footprint=cot_footprint,
        corner_index=0,
        length=bl_post_height,
        location_type=FootprintLocation.INSIDE,
        size=cot_timber_size,
        ticket=TimberTicket(path="cot_post_BL", tags=("post", "cot", "3_3_8x3_3_8")),
    )

    # 2. Bottom-Right Post
    post_br = create_vertical_timber_on_footprint_corner(
        footprint=cot_footprint,
        corner_index=1,
        length=front_beam_bottom_z,
        location_type=FootprintLocation.INSIDE,
        size=cot_timber_size,
        ticket=TimberTicket(path="cot_post_BR", tags=("post", "cot", "3_3_8x3_3_8")),
    )

    # 3. Top-Right Post
    post_tr = create_vertical_timber_on_footprint_corner(
        footprint=cot_footprint,
        corner_index=2,
        length=back_beam_bottom_z,
        location_type=FootprintLocation.INSIDE,
        size=cot_timber_size,
        ticket=TimberTicket(path="cot_post_TR", tags=("post", "cot", "3_3_8x3_3_8")),
    )

    # 4. Upper Left Post (between front rail and front beam, offset 1.5" from wall at X=0)
    upper_left_x_center = cot_upper_left_post_offset_x + timber_cs / scalar(2)
    y_front_center = cot_corner_offset_y - cot_length_y + timber_cs / scalar(2)
    upper_left_length = front_beam_bottom_z - cot_rail_height

    upper_left_post = create_axis_aligned_timber(
        bottom_position=create_v3(upper_left_x_center, y_front_center, cot_rail_height),
        length=upper_left_length,
        size=cot_timber_size,
        length_direction=TimberFace.TOP,
        width_direction=TimberFace.RIGHT,
        ticket=TimberTicket(path="cot_post_front_upper_left", tags=("post", "cot", "upper_post", "3_3_8x3_3_8")),
    )

    return [post_bl, post_br, post_tr, upper_left_post]


def create_cot_rim_joists() -> list[Timber]:
    """
    Creates four 3 3/8" square rim joists around the cot footprint perimeter.
    The top of the rim joists is at 16" from the ground (floor height).
    """
    z_center = cot_floor_height - cot_timber_cross_section / scalar(2)

    x_start = cot_corner_offset_x
    x_length = cot_width_x
    x_end = x_start + x_length

    y_start = cot_corner_offset_y - cot_length_y
    y_length = cot_length_y
    y_end = cot_corner_offset_y

    front_rim = create_axis_aligned_timber(
        bottom_position=create_v3(x_start, y_start + cot_timber_cross_section / scalar(2), z_center),
        length=x_length,
        size=cot_timber_size,
        length_direction=TimberFace.RIGHT,
        width_direction=TimberFace.TOP,
        ticket=TimberTicket(path="cot_rim_joist_front", tags=("rim_joist", "floor", "cot")),
    )

    right_rim = create_axis_aligned_timber(
        bottom_position=create_v3(x_end - cot_timber_cross_section / scalar(2), y_start, z_center),
        length=y_length,
        size=cot_timber_size,
        length_direction=TimberFace.FRONT,
        width_direction=TimberFace.TOP,
        ticket=TimberTicket(path="cot_rim_joist_right", tags=("rim_joist", "floor", "cot")),
    )

    back_rim = create_axis_aligned_timber(
        bottom_position=create_v3(x_start, y_end - cot_timber_cross_section / scalar(2), z_center),
        length=x_length,
        size=cot_timber_size,
        length_direction=TimberFace.RIGHT,
        width_direction=TimberFace.TOP,
        ticket=TimberTicket(path="cot_rim_joist_back", tags=("rim_joist", "floor", "cot")),
    )

    left_rim = create_axis_aligned_timber(
        bottom_position=create_v3(x_start + cot_timber_cross_section / scalar(2), y_start, z_center),
        length=y_length,
        size=cot_timber_size,
        length_direction=TimberFace.FRONT,
        width_direction=TimberFace.TOP,
        ticket=TimberTicket(path="cot_rim_joist_left", tags=("rim_joist", "floor", "cot")),
    )

    return [front_rim, right_rim, back_rim, left_rim]


def cut_rim_joist_corner_joints(
    posts: list[Timber],
    rim_joists: list[Timber],
) -> tuple[dict[str, list[Cutting]], list[Accessory]]:
    """
    Connects each of the rim joists to the corner posts using mortise and tenon joints:
    - Tenons: 1" x 1.5", 3" long (stopped mortise inside 3 3/8" posts).
    - Offsets:
      - X-running rim joists (front, back): Upper offset (+13/16" along Z).
      - Y-running rim joists (left, right): Lower offset (-13/16" along Z).
      This separates the tenons vertically by 1/8", preventing intersection within the corner posts.
    - Fasteners: 5/8" square through-pegs with 1/16" draw-bore offset.
    """
    post_bl, post_br, post_tr = posts[:3]
    front_rim, right_rim, back_rim, left_rim = rim_joists

    peg_params = SimplePegParameters(
        shape=PegShape.SQUARE,
        peg_positions=[(inches(3, 2), scalar(0))],
        size=cot_peg_size,
        depth=None,
        tenon_hole_offset=inches(1, 16),
    )

    offset_upper = Matrix([inches(13, 16), scalar(0)])
    offset_lower = Matrix([-inches(13, 16), scalar(0)])

    # 1. Front Rim @ BL Post (Upper tenon)
    j_front_bl = cut_mortise_and_tenon_joint_on_face_aligned_timbers(
        arrangement=ButtJointTimberArrangement(
            receiving_timber=post_bl,
            butt_timber=front_rim,
            butt_timber_end=TimberEnd.BOTTOM,
            front_face_on_butt_timber=TimberLongFace.FRONT,
        ),
        tenon_width_relative_to_joint=cot_rim_tenon_height,
        tenon_height_relative_to_joint=cot_rim_tenon_thickness,
        tenon_length=cot_rim_tenon_length,
        mortise_depth=cot_rim_tenon_length,
        tenon_position=offset_upper,
        peg_parameters=peg_params,
    )

    # 2. Left Rim @ BL Post (Lower tenon)
    j_left_bl = cut_mortise_and_tenon_joint_on_face_aligned_timbers(
        arrangement=ButtJointTimberArrangement(
            receiving_timber=post_bl,
            butt_timber=left_rim,
            butt_timber_end=TimberEnd.BOTTOM,
            front_face_on_butt_timber=TimberLongFace.BACK,
        ),
        tenon_width_relative_to_joint=cot_rim_tenon_height,
        tenon_height_relative_to_joint=cot_rim_tenon_thickness,
        tenon_length=cot_rim_tenon_length,
        mortise_depth=cot_rim_tenon_length,
        tenon_position=offset_lower,
        peg_parameters=peg_params,
    )

    # 3. Front Rim @ BR Post (Upper tenon)
    j_front_br = cut_mortise_and_tenon_joint_on_face_aligned_timbers(
        arrangement=ButtJointTimberArrangement(
            receiving_timber=post_br,
            butt_timber=front_rim,
            butt_timber_end=TimberEnd.TOP,
            front_face_on_butt_timber=TimberLongFace.FRONT,
        ),
        tenon_width_relative_to_joint=cot_rim_tenon_height,
        tenon_height_relative_to_joint=cot_rim_tenon_thickness,
        tenon_length=cot_rim_tenon_length,
        mortise_depth=cot_rim_tenon_length,
        tenon_position=offset_upper,
        peg_parameters=peg_params,
    )

    # 4. Right Rim @ BR Post (Lower tenon)
    j_right_br = cut_mortise_and_tenon_joint_on_face_aligned_timbers(
        arrangement=ButtJointTimberArrangement(
            receiving_timber=post_br,
            butt_timber=right_rim,
            butt_timber_end=TimberEnd.BOTTOM,
            front_face_on_butt_timber=TimberLongFace.FRONT,
        ),
        tenon_width_relative_to_joint=cot_rim_tenon_height,
        tenon_height_relative_to_joint=cot_rim_tenon_thickness,
        tenon_length=cot_rim_tenon_length,
        mortise_depth=cot_rim_tenon_length,
        tenon_position=offset_lower,
        peg_parameters=peg_params,
    )

    # 5. Back Rim @ TR Post (Upper tenon)
    j_back_tr = cut_mortise_and_tenon_joint_on_face_aligned_timbers(
        arrangement=ButtJointTimberArrangement(
            receiving_timber=post_tr,
            butt_timber=back_rim,
            butt_timber_end=TimberEnd.TOP,
            front_face_on_butt_timber=TimberLongFace.BACK,
        ),
        tenon_width_relative_to_joint=cot_rim_tenon_height,
        tenon_height_relative_to_joint=cot_rim_tenon_thickness,
        tenon_length=cot_rim_tenon_length,
        mortise_depth=cot_rim_tenon_length,
        tenon_position=offset_upper,
        peg_parameters=peg_params,
    )

    # 6. Right Rim @ TR Post (Lower tenon)
    j_right_tr = cut_mortise_and_tenon_joint_on_face_aligned_timbers(
        arrangement=ButtJointTimberArrangement(
            receiving_timber=post_tr,
            butt_timber=right_rim,
            butt_timber_end=TimberEnd.TOP,
            front_face_on_butt_timber=TimberLongFace.FRONT,
        ),
        tenon_width_relative_to_joint=cot_rim_tenon_height,
        tenon_height_relative_to_joint=cot_rim_tenon_thickness,
        tenon_length=cot_rim_tenon_length,
        mortise_depth=cot_rim_tenon_length,
        tenon_position=offset_lower,
        peg_parameters=peg_params,
    )

    joints = [j_front_bl, j_left_bl, j_front_br, j_right_br, j_back_tr, j_right_tr]

    cuts_by_path: dict[str, list[Cutting]] = {}
    accessories: list[Accessory] = []

    for j in joints:
        for cutting in j.cuttings.values():
            path = cutting.timber.ticket.path
            cuts_by_path.setdefault(path, []).append(cutting)
        accessories.extend(j.jointAccessories.values())

    return cuts_by_path, accessories


def create_cot_side_beam() -> Timber:
    """
    Creates a 3 3/8" square tie beam along the right wall connecting post BR and post TR.
    Top of beam sits 4" below the top of the front roof plate.
    """
    timber_cs = cot_timber_cross_section
    x_end = cot_corner_offset_x + cot_width_x
    x_right_center = x_end - timber_cs / scalar(2)
    y_start = cot_corner_offset_y - cot_length_y

    front_beam_top_z = compute_front_beam_height()
    side_beam_top_z = front_beam_top_z - cot_side_beam_drop_from_plate
    side_beam_z_center = side_beam_top_z - timber_cs / scalar(2)

    return create_axis_aligned_timber(
        bottom_position=create_v3(x_right_center, y_start, side_beam_z_center),
        length=cot_length_y,
        size=cot_timber_size,
        length_direction=TimberFace.FRONT,
        width_direction=TimberFace.TOP,
        ticket=TimberTicket(path="cot_beam_right_side", tags=("beam", "girt", "cot", "3_3_8x3_3_8")),
    )


def cut_rail_and_post_joints(
    posts: list[Timber],
    rails_and_studs: list[Timber],
    roof_beams: list[Timber],
    side_beam_right: Timber,
) -> tuple[dict[str, list[Cutting]], list[Accessory]]:
    """
    Connects rails, posts, roof beams, and the right side tie beam using mortise and tenon joints with 5/8" square pegs:
    - Front rail to BR post: 3" x 1" tenon, centered.
    - Right rail to door post: 3" x 1" tenon, centered.
    - Right rail to TR post: 3" x 1" tenon, centered.
    - BL post top into front rail underside: 1.5" x 1" tenon, offset +9/16" along X to preserve end grain relish.
    - Upper left post bottom into front rail top: 1.5" x 1" tenon, offset +15/16" along X (to the right)
      so it does not intersect with the bottom post tenon inside the rail.
    - Upper left post top into front beam: 1.5" x 1" tenon, centered.
    - BR post top into front beam: 1.5" x 1" tenon, centered.
    - TR post top into back beam: 1.5" x 1" tenon, centered.
    - Side beam front into BR post: 3" x 1" tenon, centered.
    - Side beam back into TR post: 3" x 1" tenon, centered.
    - Door post top into side beam underside: 1.5" x 1" tenon, centered.
    """
    post_bl, post_br, post_tr, upper_left_post = posts
    front_rail, front_mid_stud, door_post_right, right_rail = rails_and_studs
    back_beam, front_beam = roof_beams

    peg_params = SimplePegParameters(
        shape=PegShape.SQUARE,
        peg_positions=[(inches(3, 2), scalar(0))],
        size=cot_peg_size,
        depth=None,
        tenon_hole_offset=inches(1, 16),
    )

    # 1. Front Rail @ BR Post (3" wide x 1" thick tenon, centered)
    j_front_rail_br = cut_mortise_and_tenon_joint_on_face_aligned_timbers(
        arrangement=ButtJointTimberArrangement(
            receiving_timber=post_br,
            butt_timber=front_rail,
            butt_timber_end=TimberEnd.TOP,
            front_face_on_butt_timber=TimberLongFace.FRONT,
        ),
        tenon_width_relative_to_joint=cot_rail_tenon_width,
        tenon_height_relative_to_joint=cot_rim_tenon_thickness,
        tenon_length=cot_rim_tenon_length,
        mortise_depth=cot_rim_tenon_length,
        tenon_position=Matrix([scalar(0), scalar(0)]),
        peg_parameters=peg_params,
    )

    # 2. Right Rail @ Door Post (3" wide x 1" thick tenon, centered)
    j_right_rail_door = cut_mortise_and_tenon_joint_on_face_aligned_timbers(
        arrangement=ButtJointTimberArrangement(
            receiving_timber=door_post_right,
            butt_timber=right_rail,
            butt_timber_end=TimberEnd.BOTTOM,
            front_face_on_butt_timber=TimberLongFace.FRONT,
        ),
        tenon_width_relative_to_joint=cot_rail_tenon_width,
        tenon_height_relative_to_joint=cot_rim_tenon_thickness,
        tenon_length=cot_rim_tenon_length,
        mortise_depth=cot_rim_tenon_length,
        tenon_position=Matrix([scalar(0), scalar(0)]),
        peg_parameters=peg_params,
    )

    # 3. Right Rail @ TR Post (3" wide x 1" thick tenon, centered)
    j_right_rail_tr = cut_mortise_and_tenon_joint_on_face_aligned_timbers(
        arrangement=ButtJointTimberArrangement(
            receiving_timber=post_tr,
            butt_timber=right_rail,
            butt_timber_end=TimberEnd.TOP,
            front_face_on_butt_timber=TimberLongFace.FRONT,
        ),
        tenon_width_relative_to_joint=cot_rail_tenon_width,
        tenon_height_relative_to_joint=cot_rim_tenon_thickness,
        tenon_length=cot_rim_tenon_length,
        mortise_depth=cot_rim_tenon_length,
        tenon_position=Matrix([scalar(0), scalar(0)]),
        peg_parameters=peg_params,
    )

    # 4. BL Post top into bottom of Front Rail (1.5" x 1" tenon, offset +9/16" along X)
    j_post_bl_rail = cut_mortise_and_tenon_joint_on_face_aligned_timbers(
        arrangement=ButtJointTimberArrangement(
            receiving_timber=front_rail,
            butt_timber=post_bl,
            butt_timber_end=TimberEnd.TOP,
            front_face_on_butt_timber=TimberLongFace.FRONT,
        ),
        tenon_width_relative_to_joint=cot_rim_tenon_height,
        tenon_height_relative_to_joint=cot_rim_tenon_thickness,
        tenon_length=inches(5, 2),
        mortise_depth=inches(5, 2),
        tenon_position=Matrix([inches(9, 16), scalar(0)]),
        peg_parameters=peg_params,
    )

    # 5. Upper Left Post bottom into Front Rail top (1.5" x 1" tenon, offset +15/16" along X)
    j_upper_left_rail = cut_mortise_and_tenon_joint_on_face_aligned_timbers(
        arrangement=ButtJointTimberArrangement(
            receiving_timber=front_rail,
            butt_timber=upper_left_post,
            butt_timber_end=TimberEnd.BOTTOM,
            front_face_on_butt_timber=TimberLongFace.FRONT,
        ),
        tenon_width_relative_to_joint=cot_rim_tenon_height,
        tenon_height_relative_to_joint=cot_rim_tenon_thickness,
        tenon_length=inches(5, 2),
        mortise_depth=inches(5, 2),
        tenon_position=Matrix([inches(15, 16), scalar(0)]),
        peg_parameters=peg_params,
    )

    # 6. Upper Left Post top into Front Beam (1.5" x 1" tenon, centered)
    j_upper_left_beam = cut_mortise_and_tenon_joint_on_face_aligned_timbers(
        arrangement=ButtJointTimberArrangement(
            receiving_timber=front_beam,
            butt_timber=upper_left_post,
            butt_timber_end=TimberEnd.TOP,
            front_face_on_butt_timber=TimberLongFace.FRONT,
        ),
        tenon_width_relative_to_joint=cot_rim_tenon_height,
        tenon_height_relative_to_joint=cot_rim_tenon_thickness,
        tenon_length=inches(5, 2),
        mortise_depth=inches(5, 2),
        tenon_position=Matrix([scalar(0), scalar(0)]),
        peg_parameters=peg_params,
    )

    # 7. Post BR top into Front Beam (1.5" x 1" tenon, centered)
    j_post_br_beam = cut_mortise_and_tenon_joint_on_face_aligned_timbers(
        arrangement=ButtJointTimberArrangement(
            receiving_timber=front_beam,
            butt_timber=post_br,
            butt_timber_end=TimberEnd.TOP,
            front_face_on_butt_timber=TimberLongFace.LEFT,
        ),
        tenon_width_relative_to_joint=cot_rim_tenon_height,
        tenon_height_relative_to_joint=cot_rim_tenon_thickness,
        tenon_length=inches(5, 2),
        mortise_depth=inches(5, 2),
        tenon_position=Matrix([scalar(0), scalar(0)]),
        peg_parameters=peg_params,
    )

    # 8. Post TR top into Back Beam (1.5" x 1" tenon, centered)
    j_post_tr_beam = cut_mortise_and_tenon_joint_on_face_aligned_timbers(
        arrangement=ButtJointTimberArrangement(
            receiving_timber=back_beam,
            butt_timber=post_tr,
            butt_timber_end=TimberEnd.TOP,
            front_face_on_butt_timber=TimberLongFace.BACK,
        ),
        tenon_width_relative_to_joint=cot_rim_tenon_height,
        tenon_height_relative_to_joint=cot_rim_tenon_thickness,
        tenon_length=inches(5, 2),
        mortise_depth=inches(5, 2),
        tenon_position=Matrix([scalar(0), scalar(0)]),
        peg_parameters=peg_params,
    )

    # 9. Right Side Tie Beam @ Post BR (3" x 1" tenon, centered)
    j_side_beam_br = cut_mortise_and_tenon_joint_on_face_aligned_timbers(
        arrangement=ButtJointTimberArrangement(
            receiving_timber=post_br,
            butt_timber=side_beam_right,
            butt_timber_end=TimberEnd.BOTTOM,
            front_face_on_butt_timber=TimberLongFace.FRONT,
        ),
        tenon_width_relative_to_joint=cot_rail_tenon_width,
        tenon_height_relative_to_joint=cot_rim_tenon_thickness,
        tenon_length=cot_rim_tenon_length,
        mortise_depth=cot_rim_tenon_length,
        tenon_position=Matrix([scalar(0), scalar(0)]),
        peg_parameters=peg_params,
    )

    # 10. Right Side Tie Beam @ Post TR (3" x 1" tenon, centered)
    j_side_beam_tr = cut_mortise_and_tenon_joint_on_face_aligned_timbers(
        arrangement=ButtJointTimberArrangement(
            receiving_timber=post_tr,
            butt_timber=side_beam_right,
            butt_timber_end=TimberEnd.TOP,
            front_face_on_butt_timber=TimberLongFace.FRONT,
        ),
        tenon_width_relative_to_joint=cot_rail_tenon_width,
        tenon_height_relative_to_joint=cot_rim_tenon_thickness,
        tenon_length=cot_rim_tenon_length,
        mortise_depth=cot_rim_tenon_length,
        tenon_position=Matrix([scalar(0), scalar(0)]),
        peg_parameters=peg_params,
    )

    # 11. Door Post top into Right Side Tie Beam underside (1.5" x 1" tenon, centered)
    j_door_post_side_beam = cut_mortise_and_tenon_joint_on_face_aligned_timbers(
        arrangement=ButtJointTimberArrangement(
            receiving_timber=side_beam_right,
            butt_timber=door_post_right,
            butt_timber_end=TimberEnd.TOP,
            front_face_on_butt_timber=TimberLongFace.BACK,
        ),
        tenon_width_relative_to_joint=cot_rim_tenon_height,
        tenon_height_relative_to_joint=cot_rim_tenon_thickness,
        tenon_length=inches(5, 2),
        mortise_depth=inches(5, 2),
        tenon_position=Matrix([scalar(0), scalar(0)]),
        peg_parameters=peg_params,
    )

    joints = [
        j_front_rail_br,
        j_right_rail_door,
        j_right_rail_tr,
        j_post_bl_rail,
        j_upper_left_rail,
        j_upper_left_beam,
        j_post_br_beam,
        j_post_tr_beam,
        j_side_beam_br,
        j_side_beam_tr,
        j_door_post_side_beam,
    ]

    cuts_by_path: dict[str, list[Cutting]] = {}
    accessories: list[Accessory] = []

    for j in joints:
        for cutting in j.cuttings.values():
            path = cutting.timber.ticket.path
            cuts_by_path.setdefault(path, []).append(cutting)
        accessories.extend(j.jointAccessories.values())

    return cuts_by_path, accessories


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
    - Right door post: 3 3/8" square, stops at right side tie beam underside
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

    # Elevation of right side tie beam underside:
    front_beam_top_z = compute_front_beam_height()
    side_beam_top_z = front_beam_top_z - cot_side_beam_drop_from_plate
    side_beam_bot_z = side_beam_top_z - timber_cs

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
        length=side_beam_bot_z,
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

    front_beam_height = compute_front_beam_height()                      # ~109.934"

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
    """Build the complete cat corner cot frame with all timbers, joints, and accessories."""
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

    # 4. Cat cot posts, rim joists, rails, studs, roof beams, and right side tie beam
    cot_posts = create_cot_posts()
    cot_rim_joists = create_cot_rim_joists()
    cot_rails_and_studs = create_cot_rails_and_studs()
    cot_roof_beams = create_cot_roof_beams()
    cot_side_beam_right = create_cot_side_beam()

    # 5. Cut mortise and tenon joints with square pegs
    rim_cuts_by_path, rim_pegs = cut_rim_joist_corner_joints(cot_posts, cot_rim_joists)
    rail_cuts_by_path, rail_pegs = cut_rail_and_post_joints(
        posts=cot_posts,
        rails_and_studs=cot_rails_and_studs,
        roof_beams=cot_roof_beams,
        side_beam_right=cot_side_beam_right,
    )

    all_cuts: dict[str, list[Cutting]] = {}
    for path, cuts in rim_cuts_by_path.items():
        all_cuts.setdefault(path, []).extend(cuts)
    for path, cuts in rail_cuts_by_path.items():
        all_cuts.setdefault(path, []).extend(cuts)

    all_accessories = rim_pegs + rail_pegs

    # Build CutTimbers for posts, rim joists, rails, studs, beams, and side tie beam
    cut_posts = [CutTimber(timber=p, cuts=all_cuts.get(p.ticket.path, [])) for p in cot_posts]
    cut_rim_joists = [CutTimber(timber=r, cuts=all_cuts.get(r.ticket.path, [])) for r in cot_rim_joists]
    cut_rails_and_studs = [CutTimber(timber=m, cuts=all_cuts.get(m.ticket.path, [])) for m in cot_rails_and_studs]
    cut_roof_beams = [CutTimber(timber=bm, cuts=all_cuts.get(bm.ticket.path, [])) for bm in cot_roof_beams]
    cut_side_beam = CutTimber(timber=cot_side_beam_right, cuts=all_cuts.get(cot_side_beam_right.ticket.path, []))

    # 6. Cat cot 3 evenly spaced floor joists
    cot_floor_joists = create_cot_floor_joists()

    # 7. Infill wall boards for all 3 bays
    cot_infill_boards = create_cot_infill_boards()

    return Frame(
        cut_timbers=[
            cut_top_wall,
            cut_left_wall,
            cut_roof,
            *cut_posts,
            *cut_rim_joists,
            *cut_rails_and_studs,
            *cut_roof_beams,
            cut_side_beam,
            *[CutTimber(j) for j in cot_floor_joists],
            *[CutTimber(b) for b in cot_infill_boards],
        ],
        accessories=all_accessories,
        name="Cat Corner Cot",
        footprints=[house_footprint, cot_footprint],
    )


example = build_frame
