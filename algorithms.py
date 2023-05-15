from world import *
from NX_graph import ReconGraph
import copy

def transform_xy_monot_old(start: World, target: Configuration):
    #start = mark_finished_blocks(start=start, target=target)
    unfin_blocks, target_blocks = src_trgt_blocks(start=start, target=target)

    while(unfin_blocks):
        for block in unfin_blocks:
            closest_target = None
            cl_dist = 0
            for target_block in target_blocks:
                if not closest_target:
                    closest_target = target_block
                else:
                    x_dist = target_block.p[0] - block.p[0]
                    cl_dist = closest_target.p[0] - block.p[0]
                    if abs(x_dist) < cl_dist:
                        closest_target = target_block
            
            if cl_dist > 0:
                if not block.neighbours['E'] and block.neighbours['SE'] and block.neighbours['S']:
                    block.intention = 'E'
                elif not block.neighbours['E'] and not block.neighbours['SE'] and block.neighbours['S']:
                    block.intention = 'SE'
                elif not block.neighbours['E'] and not block.neighbours['SE'] and not block.neighbours['S']:
                    block.intention = 'S'
                elif block.neighbours['E'].intention in ['E', 'SE']:
                    block.intention = 'E'
                else:
                    raise Exception("Something unexpected happened...")
                

            elif cl_dist < 0:
                raise NotImplementedError

        for block in unfin_blocks:
            block.check_intention()

        for block in unfin_blocks:
            to = block.intention_to_loc()
            if to == ():
                continue
            start.move_block_to(block, to)
            #block = start.configuration.get_block_id[block.id]
            if block in target_blocks:
                block.status = 'finished'
                unfin_blocks.remove(block)
                target_block.remove(block)

        start.print_world()




    return start

def transform_xy_monot(world: World, target: Configuration):
    rc_graph = ReconGraph(world=world)
    # rc_graph.draw_path_graph()
    # rc_graph.draw_move_colors()
    move_num = 1
    while rc_graph.src_blocks:
        all_paths = rc_graph.finds_all_paths()
        # rc_graph.draw_move_colors()
        # rc_graph.draw_path_graph()
        # rc_graph.draw_all_paths(all_paths)
        # rc_graph.draw_all_paths_and_move_colors(all_paths)
        # choose the longest path that doesn't disconnect the configuration
        all_paths = sorted(all_paths, key=len, reverse=True)
        #path = max(all_paths, key=len)
        i = 0
        path = all_paths[0]
        pos_path = rc_graph.convert_ids_to_pos(path)
        while (not check_path_connectivity(world=world, path=pos_path)):
            i += 1
            if i == len(all_paths):
                raise IndexError("There are no connected paths :(")
            path = all_paths[i]
            pos_path = rc_graph.convert_ids_to_pos(path)
        # rc_graph.draw_all_paths([path])
        world.execute_path(pos_path)
        print(f"\nThe current number of moves that have been made is {move_num}\n")
        world.print_world()
        move_num += 1
        rc_graph = ReconGraph(world=world)
    
    rc_graph.draw_path_graph()

def check_path_connectivity(world: World, path: list) -> bool:
    path_edges = reversed([(path[n],path[n+1]) for n in range(len(path)-1)])
    copy_world = World(len(world.used_cells), len(world.used_cells[0]))
    copy_config = copy.deepcopy(world.configuration)
    copy_world.add_configuration(copy_config)
    for edge in path_edges:
        block = copy_world.configuration.get_block_p(edge[0])
        if block:
            try:
                copy_world.is_valid(block=block, to=edge[1])
            except:
                return False
            
            copy_world.rm_block(block=block)
    return True

def mark_finished_blocks(start: World, target: Configuration):
    unfinished_blocks = []
    # target_blocks = []
    for block in start.configuration.blocks:
        if not block:
            break
        target_block = target.get_block_p(block.p)
        if target_block != None:
            block.status = 'finished'
            #target_block.status = 'finished'
        else:
            unfinished_blocks.append(block)

    # for block in target.blocks:
    #     if not block:
    #         break
    #     elif block.status != 'finished':
    #         target_blocks.append(block)

    return start

def src_trgt_blocks(start: World, target: Configuration) -> tuple[list, list]:
    src_blocks = []
    target_blocks = []
    for block in start.configuration.blocks:
        if not block:
            break
        target_block = target.get_block_p(block.p)
        if not target_block:
            src_blocks.append(block)

    for block in target.blocks:
        if not block:
            break
        src_block = start.configuration.get_block_p(block.p)
        if not src_block:
            target_blocks.append(block)

    return src_blocks, target_blocks
