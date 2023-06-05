from world import *
from NX_graph import MatchGraph


def matching_monotone(world: World) -> World:
    # Fill the boundary while preserving monotonicity
    world = fill_boundary(world)


    # Make the matching
    # matching = make_matching(world)

    # for island in matching:
        # make legal moves in each island
        # pass

    return world


def fill_boundary(world: World) -> World:
    graph = MatchGraph(world)
    boundary_targets = []
    for target in graph.trgt_blocks:
        location = graph.match_G.nodes[target]["loc"]
        if location[0] == 0 or location[1] == 0:
            boundary_targets.append((target, location))

    boundary_targets = sorted(boundary_targets, key = lambda x: x[1])

    return world

