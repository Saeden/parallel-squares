from model.world import *
from graphs.matched import MatchGraph
from graphs.drawing import draw_match_labels


def matching_monotone(world: World) -> World:
    # Fill the boundary while preserving monotonicity
    world = fill_boundary(world, False)


    # Make the matching
    matching = make_matching(world)
    move_num = 0
    for island in matching:
        # make legal moves in each island, we need to order the island such that the move order does not create hanging blocks
        # island = order_island(island)
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
    matching_lst = []
    islands = []
    col_stack = []
    row_stack = []

    max_num_matches = len(world.target_list)
    num_matches = 0

    max_x = len(world.used_cells)
    max_y = len(world.used_cells[0])

    found_pos = {}
    for x in range(max_x):
        if num_matches == max_num_matches:
            break
        for y in reversed(range(max_y)):
            try:
                found = found_pos[(x-1, y-1)]
            except:
                found = False

            current_cell = world.used_cells[x][y]
            cell_type: str or None = world.get_cell_type(x=x, y=y, id=current_cell)
            if not cell_type or found:
                continue
            elif not col_stack or col_stack[-1][2] == cell_type:
                col_stack.append((x-1, y-1, cell_type))
            elif col_stack[-1][2] != cell_type:
                temp_x = x
                while cell_type != None:
                    row_stack.append((temp_x-1, y-1, cell_type))
                    found_pos[(temp_x-1, y-1)] = True
                    temp_x += 1
                    current_cell = world.used_cells[temp_x][y]
                    cell_type: str or None = world.get_cell_type(x=temp_x, y=y, id=current_cell)
                while row_stack:
                    if row_stack[-1][2] == "source":
                        source_item = row_stack[0][:2]
                        target_item = col_stack[-1][:2]
                        print(f"Source block; pos: {source_item} | Target block; pos: {target_item}")
                        matching_lst.append((source_item, target_item, "left"))
                        num_matches += 1
                        del row_stack[0]
                        del col_stack[-1]
                    elif row_stack[-1][2] == "target":
                        source_item = col_stack[-1][:2]
                        target_item = row_stack[-1][:2]
                        print(f"Source block; pos: {source_item} | Target block; pos: {target_item}")
                        matching_lst.append((source_item, target_item, "right"))
                        num_matches += 1
                        del row_stack[-1]
                        del col_stack[-1]
                if not col_stack:
                    islands.append(matching_lst)
                    matching_lst = []
                    if num_matches == max_num_matches:
                        break
  
            found_pos[(x-1, y-1)] = True
    graph = MatchGraph(world=world)
    graph.add_match_labels(islands)
    draw_match_labels(graph)

    return islands



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
