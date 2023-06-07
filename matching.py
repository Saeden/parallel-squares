from world import *
from NX_graph import MatchGraph


def matching_monotone(world: World) -> World:
    # Fill the boundary while preserving monotonicity
    world = fill_boundary(world)


    # Make the matching
    matching = make_matching(world)

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

def make_matching(world: World):
    source_blocks: list = [block for block in world.configuration.blocks if block is not None and block.status == "source"]
    target_blocks: list = world.target_list

    source_blocks = sorted(source_blocks, key=lambda block: (-block.p[0], -block.p[1]))
    target_blocks = sorted(target_blocks, key= lambda block: (block.p[1], block.p[0]))


    matching_lst = []
    for ind, src_block in enumerate(source_blocks):
        matched_blocks = (src_block, target_blocks[ind])
        print(f"Source block; ID:{src_block.id}, pos: {src_block.p} | Target block; ID:{target_blocks[ind].id}, pos: {target_blocks[ind].p}")
        matching_lst.append(matched_blocks)

    return


