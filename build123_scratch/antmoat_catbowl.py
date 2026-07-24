"""
Ant-moat cat food bowl, built with build123d.

Design:
  1. A single 2D profile (food bowl + surrounding water moat + outer rim) is
     revolved 360 degrees around the Z axis to form the main body. Ants
     climbing the outside of the bowl have to cross the water-filled moat
     to reach the food well, which they won't do.
  2. The underside gets a ring of little tapered feet. Their footprint
     shapes come from a 2D Voronoi diagram, clipped to a disc and eroded
     apart so each cell becomes an isolated island, then each island is
     extruded downward with an inward draft angle.
  3. The outer wall gets a band of soft Voronoi bumps: the wall is unrolled
     into (arc-length, height) space and Voronoi-tessellated (tiled
     periodically so it wraps seamlessly), and each cell becomes a shallow
     spherical-cap bump - not a hard extrusion - so the overhang angle
     tapers gently to zero at the wall instead of printing an unsupported
     ledge.

Run this file directly to build the model and export STL/STEP to this
folder:

    uv run python antmoat_catbowl.py
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
    GeomType,
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
    revolve,
)

# ---------------------------------------------------------------------------
# Parameters (mm)
# ---------------------------------------------------------------------------

wall_t = 5.76  # wall / rim thickness throughout (1.2x thicker again)

base_h = 3.0  # solid base thickness under the food well floor

food_top_r = 31.7  # radius of the food well (shrunk so overall diameter is ~80%)
food_rim_z = 28.0  # height of the food well's rim (top of inner wall) - much taller
# -> food well depth = food_rim_z - base_h = 25 mm

moat_width = 10.0  # radial width of the water moat channel
moat_floor_z = 9.0  # height of the moat floor above the table
# -> moat holds water up to (min(food_rim_z, outer_rim_z) - moat_floor_z) deep
#    before it spills

moat_inner_r = food_top_r + wall_t
moat_outer_r = moat_inner_r + moat_width
bowl_outer_r = moat_outer_r + wall_t

outer_rim_z = 21.0  # outer rim height - deliberately lower than the food rim
# (0.7x of the previous 30 mm outer rim), so it's now the shorter of the two
# rims; overflow spills outward off the table rather than into the food

rim_fillet = 1.6  # rounds the touch-edges (food rim + outer rim) for comfort/cleaning
inner_bottom_fillet = 4.0  # rounds the INSIDE corner (food well floor -> inner wall)
outer_bottom_chamfer = 4.5  # 45-degree chamfer on the OUTSIDE bottom corner - a fillet
# there prints badly (its tangent point is a horizontal, unsupported overhang); a
# constant-angle chamfer is self-supporting

# Feet (Voronoi islands extruded downward from the bottom, z = 0)
foot_depth = 3.0  # mm, extrude distance
foot_taper_deg = 10.0  # inward taper (draft) angle
foot_region_r = bowl_outer_r - outer_bottom_chamfer  # bleed to the edge of the flat
# part of the bottom (beyond this the profile chamfers up into the outer wall, so
# feet placed there would float unsupported)
foot_gap = 0.9  # mm gap carved between neighboring feet
foot_count = 144  # ~3x denser again (9x the original density)
foot_seed = 7
foot_min_area = 5.0  # discard slivers smaller than this (mm^2)

# Soft Voronoi bumps decorating the outer wall. Each bump is a spherical cap
# (not a hard-edged boss) so its overhang angle tapers gently to zero at the
# wall instead of jumping straight to a 90-degree unsupported ledge.
wall_bump_protrusion = 1.4  # mm the bump pokes out past the wall - kept shallow/soft
wall_bump_min_r = 2.0  # mm, smallest bump footprint radius - kept comfortably above
# wall_bump_protrusion so every sphere is solidly embedded in the wall (a radius too
# close to the protrusion leaves it barely attached, which OCCT's boolean solver
# can turn into a degenerate sliver instead of a clean union)
wall_bump_max_r = 2.6  # mm, largest bump footprint radius (also caps how deep the
# sphere reaches back into the wall: stay well under wall_t so it can't poke
# through into the moat)
wall_bump_fill_scale = 0.8  # shrinks each cell's equivalent radius, leaving gaps
# between bumps so they read as distinct soft dots rather than a fused blob
wall_bump_count = 130
wall_bump_seed = 11
wall_bump_margin = wall_bump_max_r + 0.6  # keep bump centers (and their radius) clear
# of the bottom chamfer and top rim fillet, both of which are curved transitions
wall_band_bottom = outer_bottom_chamfer + wall_bump_margin
wall_band_top = (outer_rim_z - rim_fillet) - wall_bump_margin


# ---------------------------------------------------------------------------
# Main bowl + moat body: one profile, revolved around Z
# ---------------------------------------------------------------------------

def build_bowl_body() -> Part:
    with BuildPart() as bp:
        with BuildSketch(Plane.XZ):
            with BuildLine() as profile_line:
                Polyline(
                    (0, base_h),  # center of food well floor
                    (food_top_r, base_h),  # outer edge of food well floor
                    (food_top_r, food_rim_z),  # up the food well's inner wall
                    (moat_inner_r, food_rim_z),  # across the food rim's top lip
                    (moat_inner_r, moat_floor_z),  # down into the moat
                    (moat_outer_r, moat_floor_z),  # across the moat floor
                    (moat_outer_r, outer_rim_z),  # up the outer wall's inner face
                    (bowl_outer_r, outer_rim_z),  # across the outer rim's top lip
                    (bowl_outer_r, 0),  # down the outside to the table
                    (0, 0),  # across the bottom back to the axis
                    close=True,
                )
                # Round the INSIDE bottom corner (food well floor meeting its
                # wall) directly in the profile, so the revolve produces a
                # smooth, bowl-like interior instead of a sharp seam.
                inner_corner = profile_line.vertices().filter_by(
                    lambda v: abs(v.X - food_top_r) < 1e-6 and abs(v.Y - base_h) < 1e-6
                )
                fillet(inner_corner, radius=inner_bottom_fillet)

                # Chamfer (not fillet) the OUTSIDE bottom corner - a constant
                # 45-degree cut prints cleanly with no support, unlike a fillet
                # whose tangent point at the floor is a flat overhang.
                outer_corner = profile_line.vertices().filter_by(
                    lambda v: abs(v.X - bowl_outer_r) < 1e-6 and abs(v.Y) < 1e-6
                )
                chamfer(outer_corner, length=outer_bottom_chamfer)
            make_face()
        revolve(axis=Axis.Z)

        # Round over the two touch-rims (food rim lip + outer rim lip) for
        # a comfortable, easy-to-clean edge.
        rim_edges = (
            bp.edges()
            .filter_by(GeomType.CIRCLE)
            .filter_by(lambda e: abs(e.center().Z - food_rim_z) < 1e-6 or abs(e.center().Z - outer_rim_z) < 1e-6)
        )
        fillet(rim_edges, radius=rim_fillet)

    return bp.part


# ---------------------------------------------------------------------------
# Voronoi feet
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
    min_sep = radius * 0.10

    pts: list[tuple[float, float]] = []
    attempts = 0
    while len(pts) < n_points and attempts < 200000:
        attempts += 1
        r = radius * 0.97 * np.sqrt(rng.random())
        theta = rng.random() * 2 * np.pi
        x, y = r * np.cos(theta), r * np.sin(theta)
        if all((x - px) ** 2 + (y - py) ** 2 > min_sep**2 for px, py in pts):
            pts.append((x, y))
    seeds = np.array(pts)

    # Guard points far outside the disc so every real cell's Voronoi region
    # is bounded (no infinite ridges to deal with).
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
# Soft Voronoi bumps on the outer wall
# ---------------------------------------------------------------------------

def wall_bump_specs(
    wall_radius: float,
    z_lo: float,
    z_hi: float,
    n_points: int,
    seed: int,
    min_r: float,
    max_r: float,
    fill_scale: float,
) -> list[tuple[float, float, float]]:
    """Voronoi-tessellate the outer wall unrolled into (arc-length, z) space,
    tiled periodically so the pattern wraps seamlessly around the cylinder,
    and return (theta, z, bump_radius) for one soft bump per cell."""

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
            ds = min(ds, circumference - ds)  # periodic (wraparound) distance
            if ds * ds + (z - pz) ** 2 < min_sep * min_sep:
                ok = False
                break
        if ok:
            pts.append((s, z))
    pts_arr = np.array(pts)
    n = len(pts_arr)

    # Tile a copy on either side so the Voronoi cells wrap correctly at the seam.
    tiled = np.vstack(
        [pts_arr + [-circumference, 0], pts_arr, pts_arr + [circumference, 0]]
    )
    vor = Voronoi(tiled)
    clip_rect = box(-circumference, z_lo, 2 * circumference, z_hi)

    specs: list[tuple[float, float, float]] = []
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
        r_eq = float(np.clip(np.sqrt(clipped.area / np.pi) * fill_scale, min_r, max_r))
        s, z = pts_arr[i]
        specs.append((float(s / wall_radius), float(z), r_eq))

    return specs


def build_wall_bumps() -> Part:
    specs = wall_bump_specs(
        wall_radius=bowl_outer_r,
        z_lo=wall_band_bottom,
        z_hi=wall_band_top,
        n_points=wall_bump_count,
        seed=wall_bump_seed,
        min_r=wall_bump_min_r,
        max_r=wall_bump_max_r,
        fill_scale=wall_bump_fill_scale,
    )
    if not specs:
        raise RuntimeError("Wall bump generation produced no cells")

    with BuildPart() as bp:
        for theta, z, r in specs:
            center_r = bowl_outer_r - (r - wall_bump_protrusion)
            cx = center_r * np.cos(theta)
            cy = center_r * np.sin(theta)
            with Locations((cx, cy, z)):
                Sphere(radius=r, mode=Mode.ADD)

    return bp.part


# ---------------------------------------------------------------------------

def main() -> None:
    bowl = build_bowl_body()
    feet = build_voronoi_feet()
    wall_bumps = build_wall_bumps()
    part = bowl + feet + wall_bumps

    bbox = part.bounding_box()
    moat_max_depth = min(food_rim_z, outer_rim_z) - moat_floor_z
    water_capacity_ml = (
        np.pi * (moat_outer_r**2 - moat_inner_r**2) * moat_max_depth / 1000.0
    )

    print(f"Outer diameter: {2 * bowl_outer_r:.1f} mm")
    print(f"Food well diameter / depth: {2 * food_top_r:.1f} / {food_rim_z - base_h:.1f} mm")
    print(f"Moat channel width / max depth before spill: {moat_width:.1f} / {moat_max_depth:.1f} mm")
    print(f"Approx. moat water capacity: {water_capacity_ml:.0f} mL")
    print(f"Overall bounding box: {bbox.size.X:.1f} x {bbox.size.Y:.1f} x {bbox.size.Z:.1f} mm")
    print(f"Volume: {part.volume / 1000.0:.1f} cm^3")

    export_stl(part, "antmoat_catbowl.stl")
    export_step(part, "antmoat_catbowl.step")
    print("Exported antmoat_catbowl.stl and antmoat_catbowl.step")

    show(part)


if __name__ == "__main__":
    main()
