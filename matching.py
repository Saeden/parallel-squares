from world import *
from NX_graph import MatchGraph


def matching_monotone(world: World) -> World:
    # Fill the boundary while preserving monotonicity
    world = fill_boundary(world)


    # Make the matching
    matching = make_matching(world)

    for island in matching:
        # make legal moves in each island, we need to reverse because we want to move the outer matches first (which are found last)
        for matched_blocks in reversed(island):
            source = matched_blocks[0]
            target = matched_blocks[1]
            if 0 in source.p or 0 in target.p:
                execute_boundary_L_move(source=source, target=target, world=world)
            else:
                execute_L_move(source=source, target=target, world=world)

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

def make_matching(world: World) -> list[list]:
    source_blocks: list = [block for block in world.configuration.blocks if block is not None and block.status == "source"]
    target_blocks: list = world.target_list

    source_blocks = sorted(source_blocks, key=lambda block: (block.p[0], -block.p[1]))
    target_blocks = sorted(target_blocks, key= lambda block: (-block.p[1], -block.p[0]))


    matching_lst = []
    islands = []
    stack = []
    for ind, src_block in enumerate(source_blocks):
        # if the x value of the next item in the source block list is smaller than the x value of the next item in the 
        # target cell list then we know there is a source block between the current source block and the next target cell
        # so put the current source block on the stack 
        if ind+1<len(source_blocks) and source_blocks[ind+1].p[0] < target_blocks[0].p[0]:
            stack.append(src_block)
        # else we have found the first matching
        else:
            stack.append(src_block)
            while(ind+1==len(source_blocks) or target_blocks[0].p[0] < source_blocks[ind+1].p[0]):
                matched_blocks = (stack[-1], target_blocks[0])
                del target_blocks[0]
                del stack[-1]
                print(f"Source block; ID:{matched_blocks[0].id}, pos: {matched_blocks[0].p} | Target block; ID:{matched_blocks[1].id}, pos: {matched_blocks[1].p}")
                matching_lst.append(matched_blocks)
                if not stack:
                    islands.append(matching_lst)
                    matching_lst = []
                if not target_blocks:
                    break
        
        
    graph = MatchGraph(world=world)
    graph.add_match_labels(islands)
    graph.draw_match_labels()

    return islands

def execute_L_move(source: Block, target: Block, world: World):
    first_chain = []
    second_chain = []

    if source.p[0] < target.p[0]:
        current_block = (source.p[0], target.p[1])
        while current_block[0] <= target.p[0]:
            first_chain.append(current_block)
            current_block = (current_block[0]+1, current_block[1])

    else:
        raise NotImplementedError

def execute_boundary_L_move(source: Block, target: Block):
    raise NotImplementedError
