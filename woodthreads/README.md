# Parametric 3D Printable Wood Threading Router Jig

This folder contains a bunch of OpenSCAD files for creating wood threading tools.

## Requirements

Use the latest build of OpenSCAD (not the 2021 version) and install the [BOSL2 library](https://github.com/revarbat/BOSL2).

## How it all works

There are a number of different files here that work together to allow you to create threaded rods and nuts.


### Mounting the Jig

To mount the jigs on the router, you can use the `router_base.scad`. It has 2 sets of holes, one to match the holes in the threading jigs and another set to match your router. Not all routers have the same hole pattern and some hole patterns are not centered. You can use the offset parameter to account for this. For example here are the Makita trim router (Makita RT0701C) mounting hole dimensions:

![Makita RT0701C Mounting Holes](makita_trim_router_mounting_holes.png)

As you can see the center holes are offset by (45/2 - 26)  so we set `router_hole_height_offset = 9.5`. The default parameters in `router_base.scad` are set to match the Makita RT0701C trim router. 

### Threading Dowels

`direct_threading.scad` is a router jig that allows you to cut threads into a wood dowel. It requires a trim router with a 1/4 shank 60 degree v-groove bit. Mount the jig onto the router base and plugin the bit so that you can see the tip just past the internal thread guide on the inside. turn on the router, and stick the wood in while turning to cut the threads.

### Cutting Hexagon Nuts

`hexagon_jig.scad` is a simple jig for cutting hexagons on the tablesaw. It requires you to cut a strip of wood with the same thickness as the face to face length of the hexagon nut you want to cut. Next you must drill holes along the center line of the strip of wood. Place the hole into the hole in the jig and run it through the tablesaw. Turn 60 degrees registering the newly cut face on the jig's fence and repeat until you have cut all 6 faces.


### Threading Hexagon Nuts

TODO NOT DONE YET COME BACK LATER

`heaxagon_router_tap.scad` is a router jig that allows you to cut internal threads on a hexagon nut. It requires a trim router with a 1/4 shank 60 degree double chamfer bit. These are somewhat hard to find so here are some non affiliate links. TODO LINKS


## Files

- `direct_threading.scad`: A router jig for threading wood dowels.
- `heaxagon_router_tap.scad`: A router jig for cutting internal threads on a hexagon nut.
- `hexagon_jig.scad`: A jig for cutting hexagons on the tablesaw. 
- `router_base.scad`: An optional base for your router that allows you to attach the threading jigs.  
- `beall_threaderblock_replacement.scad`: Replacement for the delrin guide block on the Beall wood threader. Not recommended as I think the direct threading option is better. (note: uses BOSL library, not BOSL2)




