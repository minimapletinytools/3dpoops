"""
Funny bumpy vase, built with build123d.

An experiment in "soft extrude of a non-round shape": instead of a
spherical-cap bump (radially symmetric by construction), each bump is a
genuine loft of the actual Voronoi cell's own polygon, shrinking as it
rises so the surface eases from flat (tangent, zero slope) at the cell's
own boundary up to a small rounded cap - a soft pillow in the exact
silhouette of its cell, not just a circle.

Design:
  1. A simple cylindrical vase profile (inner wall, floor, outer wall) is
     revolved 360 degrees around the Z axis. The top rim is filleted and
     the bottom-outer corner is chamfered (not filleted - see the cat
     bowl's notes on why a fillet there prints badly).
  2. The underside gets the same kind of Voronoi-island tapered feet as
     the ant-moat cat bowl.
  3. The outer wall gets a dense field of soft "pillow" bumps: the wall
     is unrolled into (arc-length, height) space and Voronoi-tessellated
     (tiled periodically so it wraps seamlessly), each cell is eroded a
     bit for spacing, and then lofted through a stack of progressively
     shrunk, progressively-raised copies of itself (eased with a
     smoothstep, so the height gradient is tangent to the wall at the
     base and flat at the apex - no hard creases anywhere). Cells that
     fail to loft cleanly (can happen for thin/concave slivers) fall back
     to a simple spherical-cap bump instead of aborting the whole part.

Run this file directly to build the model and export STL/STEP to this
folder:

    uv run python funny_bumpy_vase.py
"""

from __future__ import annotations

import numpy as np
from scipy.spatial import Voronoi
from shapely.geometry import Point, Polygon, box
from ocp_vscode import show

from build123d import (
    Axis,
    BuildLine,
    BuildPart,
    BuildSketch,
    Locations,
    Mode,
    Part,
    Plane,
    Polyline,
    Sphere,
    chamfer,
    export_step,
    export_stl,
    fillet,
    make_face,
    extrude,
    loft,
    revolve,
)

# ---------------------------------------------------------------------------
# Parameters (mm)
# ---------------------------------------------------------------------------

vase_outer_r = 38.0
vase_wall_t = 3.2
vase_inner_r = vase_outer_r - vase_wall_t
vase_height = 95.0
vase_base_h = 3.0  # floor thickness

top_fillet = 1.6  # rounds the top rim (both the inner and outer top edges)
bottom_chamfer = 3.2  # 45-degree chamfer on the outside bottom corner - see the cat
# bowl's notes: a fillet there prints badly (its tangent point is a momentarily
# horizontal, unsupported overhang), a constant-angle chamfer is self-supporting

# Feet (Voronoi islands extruded downward from the bottom, z = 0) - same technique
# as the ant-moat cat bowl.
foot_depth = 3.0
foot_taper_deg = 10.0
foot_region_r = vase_outer_r - bottom_chamfer  # bleed to the edge of the flat part
# of the bottom, same reasoning as the cat bowl
foot_gap = 0.9
foot_count = 80
foot_seed = 7
foot_min_area = 4.0

# Soft "pillow" Voronoi bumps on the outer wall.
wall_bump_protrusion = 1.8  # mm the bump pokes out past the wall at its apex
wall_bump_embed = 1.4  # mm the bump's (full-size) base is embedded INTO the wall -
# without this the loft is merely tangent to the wall (zero volumetric overlap) and
# won't fuse into one solid; must stay well under vase_wall_t
wall_bump_min_r = 3.0  # mm, smallest cell equivalent radius
wall_bump_max_r = 6.0  # mm, largest cell equivalent radius
wall_bump_fill_scale = 0.85  # shrinks each cell's equivalent radius, leaving gaps
# between bumps so they read as distinct pillows rather than a fused ridge
wall_bump_max_inset_frac = 0.6  # the apex cross-section is shrunk to this fraction of
# the (gapped) cell's equivalent (area-based) radius. Equivalent radius overestimates
# the true inradius for elongated/irregular cells, so this has to stay well under 1.0
# or erosion empties out the cell before reaching the apex; 0.6 was the largest value
# that produced zero loft failures across a test batch
wall_bump_steps = 10  # number of loft sections beyond the embedded base
wall_bump_count = 170
wall_bump_seed = 11
wall_bump_margin = wall_bump_max_r + 1.0  # keep bumps clear of the top fillet and
# bottom chamfer transitions
wall_band_bottom = bottom_chamfer + wall_bump_margin
wall_band_top = (vase_height - top_fillet) - wall_bump_margin


# ---------------------------------------------------------------------------
# Main vase body: one profile, revolved around Z
# ---------------------------------------------------------------------------

def build_vase_body() -> Part:
    with BuildPart() as bp:
        with BuildSketch(Plane.XZ):
            with BuildLine() as profile_line:
                Polyline(
                    (0, vase_base_h),  # center of the floor
                    (vase_inner_r, vase_base_h),  # inner edge of the floor
                    (vase_inner_r, vase_height),  # up the inner wall to the rim
                    (vase_outer_r, vase_height),  # across the top rim's lip
                    (vase_outer_r, 0),  # down the outside to the table
                    (0, 0),  # across the bottom back to the axis
                    close=True,
                )
                # Round both top corners (inner + outer) for a comfortable rim.
                top_corners = profile_line.vertices().filter_by(
                    lambda v: abs(v.Y - vase_height) < 1e-6
                )
                fillet(top_corners, radius=top_fillet)

                # Chamfer (not fillet) the outside bottom corner - see module
                # docstring / cat bowl notes on why.
                bottom_corner = profile_line.vertices().filter_by(
                    lambda v: abs(v.X - vase_outer_r) < 1e-6 and abs(v.Y) < 1e-6
                )
                chamfer(bottom_corner, length=bottom_chamfer)
            make_face()
        revolve(axis=Axis.Z)

    return bp.part


# ---------------------------------------------------------------------------
# Voronoi feet (same technique as the ant-moat cat bowl)
# ---------------------------------------------------------------------------

def voronoi_foot_polygons(
    radius: float,
    n_points: int,
    seed: int,
    gap: float,
    min_area: float,
) -> list[Polygon]:
    """Jittered seed points -> bounded Voronoi cells -> clipped to a disc ->
    eroded apart so each cell becomes a standalone island."""

    rng = np.random.default_rng(seed)
    min_sep = radius * 0.14

    pts: list[tuple[float, float]] = []
    attempts = 0
    while len(pts) < n_points and attempts < 200000:
        attempts += 1
        r = radius * 0.96 * np.sqrt(rng.random())
        theta = rng.random() * 2 * np.pi
        x, y = r * np.cos(theta), r * np.sin(theta)
        if all((x - px) ** 2 + (y - py) ** 2 > min_sep**2 for px, py in pts):
            pts.append((x, y))
    seeds = np.array(pts)

    guard_r = radius * 6.0
    guard_angles = np.linspace(0, 2 * np.pi, 12, endpoint=False)
    guards = np.array([[guard_r * np.cos(a), guard_r * np.sin(a)] for a in guard_angles])

    vor = Voronoi(np.vstack([seeds, guards]))
    disc = Point(0, 0).buffer(radius, quad_segs=32)

    polygons: list[Polygon] = []
    for i in range(len(seeds)):
        region = vor.regions[vor.point_region[i]]
        if not region or -1 in region:
            continue
        cell = Polygon([vor.vertices[v] for v in region])
        clipped = cell.intersection(disc)
        island = clipped.buffer(-gap / 2, join_style="mitre", mitre_limit=3.0)
        if island.is_empty:
            continue
        if island.geom_type == "MultiPolygon":
            island = max(island.geoms, key=lambda g: g.area)
        island = island.simplify(0.05, preserve_topology=True)
        if island.area < min_area:
            continue
        polygons.append(island)

    return polygons


def build_voronoi_feet() -> Part:
    polygons = voronoi_foot_polygons(
        radius=foot_region_r,
        n_points=foot_count,
        seed=foot_seed,
        gap=foot_gap,
        min_area=foot_min_area,
    )
    if not polygons:
        raise RuntimeError("Voronoi foot generation produced no usable cells")

    with BuildPart() as bp:
        for poly in polygons:
            coords = list(poly.exterior.coords)[:-1]
            with BuildSketch(Plane.XY):
                with BuildLine():
                    Polyline(*coords, close=True)
                make_face()
            extrude(amount=-foot_depth, taper=foot_taper_deg, mode=Mode.ADD)

    return bp.part


# ---------------------------------------------------------------------------
# Soft pillow Voronoi bumps on the outer wall
# ---------------------------------------------------------------------------

def wall_cells(
    wall_radius: float,
    z_lo: float,
    z_hi: float,
    n_points: int,
    seed: int,
    min_r: float,
    max_r: float,
    fill_scale: float,
) -> list[tuple[float, float, Polygon]]:
    """Voronoi-tessellate the outer wall unrolled into (arc-length, z) space,
    tiled periodically so the pattern wraps seamlessly, and return
    (theta, z, local_cell_polygon) for each cell - the polygon is centered
    on its own seed point, ready to be placed on a tangent plane."""

    circumference = 2 * np.pi * wall_radius
    band_h = z_hi - z_lo
    rng = np.random.default_rng(seed)

    approx_spacing = np.sqrt(circumference * band_h / n_points)
    min_sep = approx_spacing * 0.55

    pts: list[tuple[float, float]] = []
    attempts = 0
    while len(pts) < n_points and attempts < 200000:
        attempts += 1
        s = rng.random() * circumference
        z = z_lo + rng.random() * band_h
        ok = True
        for ps, pz in pts:
            ds = abs(s - ps)
            ds = min(ds, circumference - ds)
            if ds * ds + (z - pz) ** 2 < min_sep * min_sep:
                ok = False
                break
        if ok:
            pts.append((s, z))
    pts_arr = np.array(pts)
    n = len(pts_arr)

    tiled = np.vstack(
        [pts_arr + [-circumference, 0], pts_arr, pts_arr + [circumference, 0]]
    )
    vor = Voronoi(tiled)
    clip_rect = box(-circumference, z_lo, 2 * circumference, z_hi)

    cells: list[tuple[float, float, Polygon]] = []
    for i in range(n):
        region = vor.regions[vor.point_region[n + i]]
        if not region or -1 in region:
            continue
        cell = Polygon([vor.vertices[v] for v in region])
        clipped = cell.intersection(clip_rect)
        if clipped.is_empty:
            continue
        if clipped.geom_type == "MultiPolygon":
            clipped = max(clipped.geoms, key=lambda g: g.area)

        s, z = pts_arr[i]
        raw_r_eq = np.sqrt(clipped.area / np.pi)
        # Erode enough to BOTH create a gap to neighbors (fill_scale) AND
        # clamp the cell to [min_r, max_r] - clamping only the reported
        # number while leaving the polygon itself unshrunk was a real bug:
        # an oversized raw Voronoi cell (sparse point regions produce these)
        # would keep its true, much larger size while every later
        # calculation assumed it was <= max_r, so the eroded/raised loft
        # profile was wildly undersized relative to the actual shape -
        # that mismatch was the real source of the long spike artifacts,
        # not the resampling method.
        target_r = float(np.clip(raw_r_eq * fill_scale, min_r, max_r))
        erosion = max(0.0, raw_r_eq - target_r)
        local = Polygon([(x - s, y - z) for x, y in clipped.exterior.coords])
        gapped = local.buffer(-erosion, join_style="round", quad_segs=6) if erosion > 1e-9 else local
        if gapped.is_empty or gapped.geom_type != "Polygon" or gapped.area < 1.0:
            continue
        eq_r = float(np.sqrt(gapped.area / np.pi))
        cells.append((float(s / wall_radius), float(z), gapped, eq_r))

    return cells


def tangent_plane(theta: float, radius: float, z: float) -> Plane:
    origin = (radius * np.cos(theta), radius * np.sin(theta), z)
    normal = (np.cos(theta), np.sin(theta), 0.0)
    x_dir = (-np.sin(theta), np.cos(theta), 0.0)
    return Plane(origin=origin, x_dir=x_dir, z_dir=normal)


def build_pillow_bump(theta: float, z: float, cell: Polygon, eq_r: float) -> Part | None:
    """Loft a soft pillow bump in the exact silhouette of `cell`, by
    uniformly scaling the cell toward an interior anchor point at each
    loft step - not eroding it with repeated shapely buffer() calls.
    Scaling a simple polygon toward an interior point can never introduce
    self-intersections and always keeps the exact same vertex count/order,
    so loft() always gets perfectly-corresponding cross-sections. Erosion
    (tried first) doesn't have either guarantee for irregular/concave
    cells, which is what produced twisted, long spike artifacts. Returns
    None if the cell is unsuitable, so the caller can fall back to a
    sphere instead."""

    # eq_r is an AREA-based equivalent radius, which a long thin sliver cell
    # can satisfy (small area) while still having a large bounding box, and
    # scaling such a sliver toward an interior point still leaves a sliver
    # (just a smaller one) rather than something dome-shaped. Reject
    # elongated cells outright; the caller falls back to a sphere sized
    # from eq_r, which doesn't care about the cell's shape.
    #
    # Note the ratio (max bounding-box dimension / eq_r) has a natural floor
    # even for perfectly regular cells - a regular hexagon alone already
    # sits at ~2.2 - so the threshold has to clear that baseline by a good
    # margin or it rejects ordinary, well-behaved cells, not just slivers.
    bx0, by0, bx1, by1 = cell.bounds
    if max(bx1 - bx0, by1 - by0) > 4.2 * eq_r:
        return None

    base = cell.simplify(0.15, preserve_topology=True)
    coords = list(base.exterior.coords)[:-1]
    if len(coords) < 3:
        return None

    anchor = base.representative_point()
    ax, ay = anchor.x, anchor.y

    ts = np.linspace(0.0, 1.0, wall_bump_steps + 1)
    smoothstep = 3 * ts**2 - 2 * ts**3  # zero slope at both t=0 and t=1
    total_rise = wall_bump_embed + wall_bump_protrusion
    radial_offsets = -wall_bump_embed + total_rise * smoothstep
    min_scale = 1.0 - wall_bump_max_inset_frac  # fraction of full size left at the apex
    # Scale eased with the same smoothstep (not t**2, which only eases the
    # start) so the shrink also levels off approaching the apex instead of
    # still shrinking at full rate right up to the top - that's what was
    # giving the bumps a slightly pinched tip instead of a rounded one.
    scales = 1.0 - (1.0 - min_scale) * smoothstep

    sections = [
        ([(ax + s * (x - ax), ay + s * (y - ay)) for x, y in coords], dr)
        for dr, s in zip(radial_offsets, scales)
    ]

    try:
        with BuildPart() as bump_bp:
            for pts, dr in sections:
                plane = tangent_plane(theta, vase_outer_r + dr, z)
                with BuildSketch(plane):
                    with BuildLine():
                        Polyline(*pts, close=True)
                    make_face()
            loft()
        if bump_bp.part is None or bump_bp.part.volume < 1e-6:
            return None
    except Exception:
        return None

    return bump_bp.part


def sphere_fallback_spec(theta: float, z: float, eq_r: float) -> tuple[float, float, float, float]:
    r = float(np.clip(eq_r, wall_bump_min_r, wall_bump_max_r))
    center_r = vase_outer_r - (r - wall_bump_protrusion)
    cx, cy = center_r * np.cos(theta), center_r * np.sin(theta)
    return (cx, cy, z, r)


def build_wall_bumps_onto(base: Part) -> Part:
    """Fuse each bump directly into `base` one at a time, rather than
    unioning the (mutually disjoint, non-touching) bumps together first.
    Fusing disjoint solids pairwise before they ever touch the main body
    is exactly the degenerate case that produces thousands of spurious
    zero-volume sliver fragments in the boolean result - fusing each small
    piece straight into the one large solid it actually overlaps avoids it
    almost entirely."""

    cells = wall_cells(
        wall_radius=vase_outer_r,
        z_lo=wall_band_bottom,
        z_hi=wall_band_top,
        n_points=wall_bump_count,
        seed=wall_bump_seed,
        min_r=wall_bump_min_r,
        max_r=wall_bump_max_r,
        fill_scale=wall_bump_fill_scale,
    )
    if not cells:
        raise RuntimeError("Wall bump generation produced no cells")

    result = base
    n_pillow = 0
    n_fallback = 0
    for theta, z, cell, eq_r in cells:
        bump = build_pillow_bump(theta, z, cell, eq_r)
        if bump is not None:
            result = result + bump
            n_pillow += 1
        else:
            cx, cy, zc, r = sphere_fallback_spec(theta, z, eq_r)
            with BuildPart() as sp:
                with Locations((cx, cy, zc)):
                    Sphere(radius=r, mode=Mode.ADD)
            result = result + sp.part
            n_fallback += 1

    print(
        f"Wall bumps: {len(cells)} cells -> {n_pillow} pillow lofts, "
        f"{n_fallback} sphere fallbacks"
    )
    return result


# ---------------------------------------------------------------------------

def main() -> None:
    vase = build_vase_body()
    feet = build_voronoi_feet()
    base = vase + feet
    part = build_wall_bumps_onto(base)

    bbox = part.bounding_box()
    print(f"Outer diameter: {2 * vase_outer_r:.1f} mm")
    print(f"Height: {vase_height:.1f} mm")
    print(f"Wall thickness: {vase_wall_t:.1f} mm")
    print(f"Overall bounding box: {bbox.size.X:.1f} x {bbox.size.Y:.1f} x {bbox.size.Z:.1f} mm")
    print(f"Volume: {part.volume / 1000.0:.1f} cm^3")

    export_stl(part, "funny_bumpy_vase.stl")
    export_step(part, "funny_bumpy_vase.step")
    print("Exported funny_bumpy_vase.stl and funny_bumpy_vase.step")
    
    show(part)  # Display the final part in the OCCT viewer


if __name__ == "__main__":
    main()
