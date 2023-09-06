from model.world import *
from graphs.matched import MatchGraph
from graphs.drawing import draw_match_labels, draw_convex_transition
from graphs.utils import get_node_frm_attr
from scipy.spatial.distance import chebyshev

def matching_monotone(world: World) -> World:
    move_num = 0
    # Fill the boundary while preserving monotonicity
    world, fill_move_num = fill_boundary(world)
    print(f"Filling the boundary cost {fill_move_num} moves.")
    world.print_world()
    move_num += fill_move_num
    
    

    # Make the matching
    islands = get_islands(world=world)
    matching = make_matching(islands=islands, world=world)
    for island in matching:
        # flow = island[0][2]
        
        # if flow == "left":
        #     # move highest x+y of source blocks, if many blocks with equal x+y move target with lowest x+y (now trying highest)
        #     island = sorted(island, key=lambda pos: (pos[0][0] + pos[0][1],  -(pos[1][0] + pos[1][1])), reverse=True)
            
        # elif flow == "right":
        #     island = sorted(island, key=lambda pos: (pos[0][0] + pos[0][1],  -(pos[1][0] + pos[1][1])), reverse=True)
        
        for matched_blocks in island:
            source = matched_blocks[0]
            target = matched_blocks[1]
            if is_convex_trans(source, target):
                move_num += 1
                print(f"This matching is close enough for a single convex transition. Executing now.")
                print(f"The total number of moves is {move_num}.")
                source_block = world.configuration.get_block_p(source)
                execute_convex_trans(source=source_block, to=target, world=world)
            elif 0 in source:
                move_num += 3
                print(f"Executing a boundary L-shaped move. The total number of moves is {move_num}")
                execute_boundary_L_move(source=source, target=target, world=world)
            elif 0 in target:
                raise ValueError("The boundary should be filled but it is not.")
            else:
                move_num += 2
                print(f"Executing an L-shaped move. The total number of moves is {move_num}")
                execute_L_move(source=source, target=target, world=world)
                
    # empty boundary while preserving monotonicity
    world, empty_move_num = empty_boundary(world)
    print(f"Emptying the excess boundary cost {empty_move_num} moves.")
    world.print_world()
    move_num += empty_move_num
    print(f"The total number of moves is {move_num}.")

    return world, move_num


def is_convex_trans(source: Block, target: Block) -> bool:
    diff_x = target[0] - source[0]
    diff_y = target[1] - source[1]

    if (diff_x, diff_y) in [(-1, 1), (1, -1)]:
        return True
    else:
        return False

def fill_boundary(world: World) -> (World, int):
    graph = MatchGraph(world)
    row_targets = []
    col_targets = []
    for target in graph.trgt_blocks:
        location = graph.match_G.nodes[target]["loc"]
        if location[0] == 0 and location[1] != 0:
            col_targets.append((target, location))
        elif location[1] == 0 and location[0] != 0:
            row_targets.append((target, location))
        elif sum(location) == 0:
            raise ValueError("Configuration does not contain the origin.")
        

    row_targets = sorted(row_targets, key=lambda x: x[1][0])
    col_targets = sorted(col_targets, key=lambda x: x[1][1])

    if not row_targets and not col_targets:
        return world, 0

    row_sources = []
    ind = 1
    while len(row_sources) < len(row_targets):
        column_ind = row_targets[0][1][0] - ind
        block_loc = world.get_highest_block_col(column_ind)
        while block_loc[1] > 0:
            row_sources.append(block_loc)
            block_loc = (block_loc[0], block_loc[1]-1)

        ind += 1

    
    col_sources = []
    ind = 1
    while len(col_sources) < len(col_targets):
        row_ind = col_targets[0][1][1] - ind
        block_loc = world.get_highest_block_row(row_ind)
        while block_loc[0] > 0:
            col_sources.append(block_loc)
            block_loc = (block_loc[0]-1, block_loc[1])

        ind += 1
    
    del graph
    
    move_num = 0

    for ind, target in enumerate(row_targets):
        source = row_sources[ind]
        move_num += calc_seq_move_num(world, source, target[1])
        world.move_sequentially(source, target[1])
        # world.print_world()
        

    for ind, target in enumerate(col_targets):
        source = col_sources[ind]
        move_num += calc_seq_move_num(world, source, target[1])
        world.move_sequentially(source, target[1])
        # world.print_world()

    return world, move_num

def empty_boundary(world: World) -> World:
    # raise NotImplementedError
    graph = MatchGraph(world)
    row_sources = []
    col_sources = []
    second_row_top_block = world.get_highest_block_row(1)
    second_col_top_block = world.get_highest_block_col(1)
    for source in graph.src_blocks:
        location = graph.match_G.nodes[source]["loc"]
        #neighbours = graph.match_G.out_edges(target).data("loc")
        if location[0] == 0 and location[1] != 0 and not location[1] <= second_col_top_block[1]:
            col_sources.append((source, location))
        elif location[1] == 0 and location[0] != 0 and not location[0] <= second_row_top_block[0]:
            row_sources.append((source, location))
        elif sum(location) == 0:
            raise ValueError("Configuration does not contain the origin.")
        

    row_sources = sorted(row_sources, key=lambda x: x[1][0], reverse=True)
    col_sources = sorted(col_sources, key=lambda x: x[1][1], reverse=True)

    if not row_sources and not col_sources:
        return world, 0

    row_targets = []
    ind = 1
    while len(row_targets) < len(row_sources):
        if len(row_sources) == len(graph.src_blocks):
            row_targets = [target.p for target in world.target_list]
            break
        lowest_source_block = row_sources[-1][1]
        row_ind = row_sources[0][1][1] + ind
        block_loc = world.get_highest_block_row(row_ind)
        cell_loc = (block_loc[0]+1, block_loc[1])
        while cell_loc[0] < lowest_source_block[0] and len(row_targets)<len(row_sources):
            row_targets.append(cell_loc)
            cell_loc = (cell_loc[0]+1, cell_loc[1])

        ind += 1

    
    col_targets = []
    ind = 1
    while len(col_targets) < len(col_sources):
        if len(col_sources) == len(graph.src_blocks):
            col_targets = [target.p for target in world.target_list]
            break
        lowest_source_block = col_sources[-1][1]
        col_ind = col_sources[0][1][0] + ind
        block_loc = world.get_highest_block_col(col_ind)
        cell_loc = (block_loc[0], block_loc[1]+1)
        while cell_loc[1] < lowest_source_block[1] and len(col_targets)<len(col_sources):
            col_targets.append(cell_loc)
            cell_loc = (cell_loc[0], cell_loc[1]+1)

        ind += 1

    move_num = 0
    for ind, source in enumerate(row_sources):
        target = row_targets[ind]
        move_num += calc_seq_move_num(world, source[1], target)
        world.move_sequentially(source[1], target)
        # world.print_world()
       

    for ind, source in enumerate(col_sources):
        target = col_targets[ind]
        move_num += calc_seq_move_num(world, source[1], target)
        world.move_sequentially(source[1], target)
        # world.print_world()
        

    return world, move_num


def make_matching(islands, world) -> list:
    matching_lst = []
    output = []
    for island in islands:
        first_source_x = island[0][0][0]
        first_target_x = island[1][0][0]
        sources = [source for source in island[0] if source[0] != 0 and source[1] != 0]
        if first_source_x < first_target_x: # right flow:
            sources = sorted(sources, key= lambda pos: (pos[0] + pos[1],  pos[1]), reverse=True)
            targets = sorted(island[1], key= lambda pos: (pos[1], pos[0]))
        else:
            sources = sorted(sources, key= lambda pos: (pos[0] + pos[1],  -pos[1]), reverse=True)
            targets = sorted(island[1])

        for ind, source in enumerate(sources):
            matching_lst.append((source, targets[ind], None, ind))
        output.append(matching_lst)
        matching_lst = []
    
    graph = MatchGraph(world=world)
    graph.add_match_labels(output)
    # draw_match_labels(graph)

    del graph

    return output

def get_islands(world):
    sources = []
    targets = []
    islands = []
    col_stack = []
    row_stack = []

    max_num_matches = len(world.target_list)
    num_matches = 0

    max_x = len(world.used_cells)
    max_y = len(world.used_cells[0])

    found_pos = {}
    for x in range(1, max_x):
        if num_matches == max_num_matches:
            break
        for y in reversed(range(1, max_y)):
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
                while row_stack and col_stack:
                    if row_stack[-1][2] == "source":
                        source_item = row_stack[-1][:2]
                        target_item = col_stack[-1][:2]
                        #print(f"Source block; pos: {source_item} | Target block; pos: {target_item}")
                        sources.append(source_item)
                        targets.append(target_item)
                        #matching_lst.append((source_item, target_item, "left", num_matches))
                        num_matches += 1
                        del row_stack[-1]
                        del col_stack[-1]
                    elif row_stack[-1][2] == "target":
                        source_item = col_stack[-1][:2]
                        target_item = row_stack[-1][:2]
                        #print(f"Source block; pos: {source_item} | Target block; pos: {target_item}")
                        sources.append(source_item)
                        targets.append(target_item)
                        #matching_lst.append((source_item, target_item, "right", num_matches))
                        num_matches += 1
                        del row_stack[-1]
                        del col_stack[-1]
                if not col_stack:
                    islands.append((sources, targets))
                    sources = []
                    targets = []
                    if num_matches == max_num_matches:
                        break
  
            found_pos[(x-1, y-1)] = True
            

    return islands

def make_matching_old(world: World) -> list[list]:
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
                        source_item = row_stack[-1][:2]
                        target_item = col_stack[-1][:2]
                        print(f"Source block; pos: {source_item} | Target block; pos: {target_item}")
                        matching_lst.append((source_item, target_item, "left", num_matches))
                        num_matches += 1
                        del row_stack[-1]
                        del col_stack[-1]
                    elif row_stack[-1][2] == "target":
                        source_item = col_stack[-1][:2]
                        target_item = row_stack[-1][:2]
                        print(f"Source block; pos: {source_item} | Target block; pos: {target_item}")
                        matching_lst.append((source_item, target_item, "right", num_matches))
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
    # draw_match_labels(graph)

    return islands



def execute_convex_trans(source: Block, to: tuple[int], world: World):
    try:
        world.move_block_to(source, to=to)
        world.add_targets()
        # world.print_world()
    except:
        if source.p[0] < to[0]:
            top_block = world.get_highest_block_row(source.p[1]-1)
            target = (top_block[0]+1, top_block[1])
            execute_L_move(source.p, target, world)
        else:
            top_block = world.get_highest_block_col(source.p[0]-1)
            target = (top_block[0], top_block[1]+1)
            execute_L_move(source.p, target, world)

def execute_L_move(source: tuple, target: tuple, world: World):
    first_chain = []
    second_chain = []

    if source[0] < target[0]:
        current_block = (source[0], target[1])
        while current_block[0] <= target[0]:
            first_chain.append(current_block)
            current_block = (current_block[0]+1, current_block[1])

        world.execute_path(first_chain)
        #for debugging
        # world.print_world()


        current_block = source
        while current_block[1] >= target[1]:
            second_chain.append(current_block)
            current_block = (current_block[0], current_block[1]-1)

        world.execute_path(second_chain)
        #for debugging
        # world.print_world()

    else:
        current_block = (target[0], source[1])
        while current_block[1] <= target[1]:
            first_chain.append(current_block)
            current_block = (current_block[0], current_block[1]+1)

        world.execute_path(first_chain)
        #for debugging
        # world.print_world()


        current_block = source
        while current_block[0] >= target[0]:
            second_chain.append(current_block)
            current_block = (current_block[0]-1, current_block[1])

        world.execute_path(second_chain)
        #for debugging
        # world.print_world()

def execute_boundary_L_move(source: Block, target: Block, world: World):
    raise NotImplementedError
    first_chain = []
    second_chain = []
    top_block = world.configuration.get_block_p(source)

    if source[0] < target[0]: # right flow
        current_block = (source[0]+1, target[1])

        corner_block = world.configuration.get_block_p((source[0], target[1]))
        corner_block_to = (source[0]+1, target[1])

        while current_block[0] <= target[0]:
            first_chain.append(current_block)
            current_block = (current_block[0]+1, current_block[1])

        # first move (chain 1 and top block)
        world.execute_path(first_chain)
        top_block_to = (source[0]+1, source[1])
        world.move_block_to(block=top_block, to=top_block_to)
        #for debugging
        # world.print_world()

        # second move (corner block)
        world.move_block_to(block=corner_block, to=corner_block_to)
        # world.print_world()

        current_block = source
        while current_block[1] >= target[1]:
            second_chain.append(current_block)
            current_block = (current_block[0], current_block[1]-1)
        # third move (second chain and top block again)
        top_block_to = (source[0], source[1]-1)
        world.execute_path(second_chain)
        world.move_block_to(block=top_block, to=top_block_to)
        #for debugging
        # world.print_world()

    else: # left flow
        current_block = (target[0], source[1]+1)

        corner_block = world.configuration.get_block_p((target[0], source [1]))
        corner_block_to = (target[0], source[1]+1)

        while current_block[1] <= target[1]:
            first_chain.append(current_block)
            current_block = (current_block[0], current_block[1]+1)

        # first move (chain 1 and top block)
        world.execute_path(first_chain)
        top_block_to = (source[0], source[1]+1)
        world.move_block_to(block=top_block, to=top_block_to)
        #for debugging
        # world.print_world()

        # second move (corner block)
        world.move_block_to(block=corner_block, to=corner_block_to)
        # world.print_world()

        current_block = (source[0]-1, source[1])
        while current_block[0] >= target[0]:
            second_chain.append(current_block)
            current_block = (current_block[0]-1, current_block[1])
        # third move (second chain and top block again)
        top_block_to = (source[0]-1, source[1])
        world.execute_path(second_chain)
        world.move_block_to(block=top_block, to=top_block_to)

        #for debugging
        # world.print_world()

def calc_seq_move_num(world: World, start: tuple, target: tuple):
    if start[0] < target[0]: # right flow
        move_num = 0
        prev_location = start
        for row in reversed(range(target[1], start[1])):
            try:
                highest_block = world.get_highest_block_row(row)
                highest_block = (highest_block[0]+1, highest_block[1])
            except:
                highest_block = (prev_location[0]+1, 0)
            move_num += chebyshev(prev_location, highest_block)
            prev_location = highest_block
    elif start[0] > target[0]: # left flow either fill left column or empty bottom row
        move_num = 0
        prev_location = start
        for row in range(start[1]+1, target[1]+1):
            try:
                highest_block = world.get_highest_block_row(row)
                highest_block = (highest_block[0]+1, highest_block[1])
            except:
                highest_block = (0, prev_location[1]+1)
            move_num += chebyshev(prev_location, highest_block)
            prev_location = highest_block

    else: # impossible
        raise ValueError(f"Trying to fill or empty the same column. That should be impossible. From {start} to {target}")

    return move_num

def sequential_transform(world: World):
    sources = [block.p for block in world.configuration.blocks if block and block.status == "source"]
    targets = [block.p for block in world.target_list]

    sources = sorted(sources, key= lambda pos: (pos[0] + pos[1],  -pos[1]), reverse=True)
    targets = sorted(targets, key= lambda pos: (pos[0] + pos[1], -pos[1]))
    move_num = 0

    for ind, source in enumerate(sources):
        target = targets[ind]
        move_num += calc_seq_move_num(world, source, target)
        world.move_sequentially(source, target)
        # world.print_world(

    return world, move_num
