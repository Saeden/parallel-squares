from world import *
from NX_graph import MatchGraph


def matching_monotone(world: World) -> World:
    # Fill the boundary while preserving monotonicity
    world = fill_boundary(world, False)


    # Make the matching
    matching = make_matching(world)
    move_num = 0
    for island in matching:
        # make legal moves in each island, we need to order the island such that the move order does not create hanging blocks
        island = order_island(island)
        for matched_blocks in island:
            source = matched_blocks[0]
            target = matched_blocks[1]
            if is_convex_trans(source, target):
                move_num += 1
                print(f"\nThis matching is close enough for a single convex transition. Executing now.")
                print(f"The total number of moves is {move_num}")
                source_block = world.configuration.get_block_p(source)
                execute_convex_trans(source=source_block, to=target, world=world)
            elif 0 in source or 0 in target:
                execute_boundary_L_move(source=source, target=target, world=world)
            else:
                move_num += 2
                print(f"\nExecuting an L-shaped move. The total number of moves is {move_num}")
                execute_L_move(source=source, target=target, world=world)
                

    return world


def is_convex_trans(source: Block, target: Block) -> bool:
    diff_x = target[0] - source[0]
    diff_y = target[1] - source[1]

    if (diff_x, diff_y) in [(-1, 1), (1, -1)]:
        return True
    else:
        return False

def fill_boundary(world: World, exec: bool) -> World:
    graph = MatchGraph(world)
    boundary_targets = []
    for target in graph.trgt_blocks:
        location = graph.match_G.nodes[target]["loc"]
        if location[0] == 0 or location[1] == 0:
            boundary_targets.append((target, location))

    boundary_targets = sorted(boundary_targets, key = lambda x: x[1])

    if exec:
        # Hard coded for now....
        path = [(7, 2), (7, 1), (8,0)]
        print("Executing hard-coded boundary fill move 1")
        world.execute_path(path)
        world.print_world()

        path2 = [(7,1), (8, 1)]
        print("Executing hard-coded boundary fill move 2")
        world.execute_path(path2)
        world.print_world()

        path3 = [(8,1), (9,0)]
        print("Executing hard-coded boundary fill move 3")
        world.execute_path(path3)
        world.print_world()

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
            # leaving this in because I am a code hoarder
            #  or
            # first_log_var = target_blocks[0].p[0] < source_blocks[ind+1].p[0]
            # second_log_var = not target_blocks[len(stack)-1].p[0] < source_blocks[ind].p[0]
            while(ind+1==len(source_blocks) or target_blocks[0].p[0] < source_blocks[ind+1].p[0] and \
                  not target_blocks[len(stack)-1].p[0] < source_blocks[ind].p[0] and stack):
                for_print = (stack[-1], target_blocks[0])
                matched_blocks = (stack[-1].p, target_blocks[0].p)
                del target_blocks[0]
                del stack[-1]
                print(f"Source block; ID:{for_print[0].id}, pos: {for_print[0].p} | Target block; ID:{for_print[1].id}, pos: {for_print[1].p}")
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

def order_island(island: list[tuple]) -> list[tuple]:
    output = []
    if len(island) == 1:
        return island
    
    for matched_blocks in island:
        source = matched_blocks[0]
        target = matched_blocks[1]
        if source[0]<target[0]:
            # this match is right flowing
            pass

    return output

def execute_convex_trans(source: Block, to: tuple[int], world: World):
    world.move_block_to(source, to=to)
    world.add_targets()
    world.print_world()

def execute_L_move(source: Block, target: Block, world: World):
    first_chain = []
    second_chain = []

    if source[0] < target[0]:
        current_block = (source[0], target[1])
        while current_block[0] <= target[0]:
            first_chain.append(current_block)
            current_block = (current_block[0]+1, current_block[1])

        world.execute_path(first_chain)
        #for debugging
        world.print_world()


        current_block = source
        while current_block[1] >= target[1]:
            second_chain.append(current_block)
            current_block = (current_block[0], current_block[1]-1)

        world.execute_path(second_chain)
        #for debugging
        world.print_world()

    else:
        current_block = (target[0], source[1])
        while current_block[1] <= target[1]:
            first_chain.append(current_block)
            current_block = (current_block[0], current_block[1]+1)

        world.execute_path(first_chain)
        #for debugging
        world.print_world()


        current_block = source
        while current_block[0] >= target[0]:
            second_chain.append(current_block)
            current_block = (current_block[0]-1, current_block[1])

        world.execute_path(second_chain)
        #for debugging
        world.print_world()

def execute_boundary_L_move(source: Block, target: Block, world: World):
    raise NotImplementedError
