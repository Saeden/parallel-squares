from model.world import *
from graphs.reconfiguration import ReconGraph
from networkx import is_weakly_connected, subgraph_view
from graphs.drawing import *
from graphs.utils import is_move_valid_can_blocked, is_move_valid_not_blocked, is_move_valid_with_prev_move

def transform_xy_monot(world: World):
    rc_graph = ReconGraph(world=world)
    move_num = 1
    while rc_graph.src_blocks:
        # draw_path_graph(rc_graph)
        split_path_pos, split_path = find_split_path_max(world, rc_graph)
        max_path_pos, max_path = find_max_path(world, rc_graph)
        if not max_path_pos and not split_path_pos:
            pos_path, path = find_min_path(world, rc_graph)
            if not pos_path:
                all_paths = rc_graph.find_all_paths_max() + rc_graph.find_all_paths_min()
                draw_all_paths_and_move_colors(rc_graph, all_paths)
                raise ValueError("There are no connected paths :(")

        num_blocks_max_path = sum(isinstance(item, int) for item in max_path)
        num_blocks_split_path = sum([sublist.count(item) for sublist in split_path for item in sublist if isinstance(item, int)])
        if num_blocks_max_path >= num_blocks_split_path:
            pos_path = max_path_pos
            world.execute_path(pos_path)
            print(f"\nThe current number of moves that have been made is {move_num}\n")
            world.print_world()
            move_num += 1
            # draw_all_paths(rc_graph, [max_path])
        else:
            # if move_num > 90:
            #     draw_all_paths(rc_graph, split_path)
            for ind, pos_path in enumerate(split_path_pos):
                try:
                    world.execute_path(pos_path)
                    print(f"\nThe current number of moves that have been made is {move_num}\n")
                    world.print_world()
                    move_num += 1
                except Exception as error:
                    temp_graph = ReconGraph(world=world)
                    graph_diff = rc_graph.path_G.edges - temp_graph.path_G.edges
                    print("Tried to do something illegal while executing this path.")
                    print(error)
                    # draw_all_paths(rc_graph, split_path[:ind+1])#[ind:])
                    print("The world looks like this currently. The moves that were succesful have been completed.")
                    # if graph_diff:
                    #     print(f"\nThe current number of moves that have been made is {move_num}\n")
                    #     move_num += 1
                    world.add_targets()
                    world.print_world()
                    print("Continuing with this configuration...")
                    
                    del temp_graph
                    break
                
            
        # rc_graph.draw_move_colors()
        # rc_graph.draw_path_graph()
        
        # rc_graph.draw_all_paths_and_move_colors([path])
        rc_graph = ReconGraph(world=world)
    
    draw_path_graph(rc_graph)

def find_max_path(world, rc_graph: ReconGraph):
    all_paths = rc_graph.find_all_paths_max(strictly_connected=True)
    #draw_all_paths(rc_graph, all_paths)
    # rc_graph.draw_all_paths_and_move_colors(all_paths)
    i=0
    all_paths = sorted(all_paths, key=lambda lst: sum(isinstance(item, int) for item in lst), reverse=True)
    path = all_paths[0]
    pos_path = rc_graph.convert_ids_to_pos(path)
    # rc_graph.draw_all_paths(all_paths)
    while (not check_path_connectivity(graph=rc_graph, world=world, path=pos_path, path_ids=path)):
        i += 1
        if i == len(all_paths):
                # rc_graph.draw_all_paths(all_paths)
            print("Currently no strictly connected max paths...")
            return [[],[]]
            
        path = all_paths[i]
        pos_path = rc_graph.convert_ids_to_pos(path)
    
    #draw_all_paths(rc_graph, path)

    return pos_path, path

def find_min_path(world, rc_graph):
    all_paths = rc_graph.find_all_paths_min()
    # rc_graph.draw_all_paths(all_paths)
    # rc_graph.draw_all_paths_and_move_colors(all_paths)
    i=0
    all_paths = sorted(all_paths, key=len, reverse=True)
    path = all_paths[0]
    pos_path = rc_graph.convert_ids_to_pos(path)
    while (not check_path_connectivity(graph=rc_graph, world=world, path=pos_path, path_ids=path)):
        i += 1
        if i == len(all_paths):
                # rc_graph.draw_all_paths(all_paths)
            print("Currently no connected paths, will now try splitting paths...")
            return [[],[]]
            rc_graph.draw_all_paths_and_move_colors(all_paths)
            raise ValueError("There are no connected paths :(")
        path = all_paths[i]
        pos_path = rc_graph.convert_ids_to_pos(path)
    return pos_path, path



def find_split_path_max(world, rc_graph: ReconGraph):
    all_paths = rc_graph.find_all_paths_max(strictly_connected=False)
    # draw_all_paths(graph=rc_graph, paths=all_paths)
    # rc_graph.draw_all_paths_and_move_colors(all_paths)
    i=0
    all_paths = sorted(all_paths, key=lambda lst: sum(isinstance(item, int) for item in lst), reverse=True)
    path = all_paths[i]
    pos_path = rc_graph.convert_ids_to_pos(path)
    cnct_path, discnct_path =  split_path_check(graph=rc_graph, world=world, path=pos_path, path_ids=path)
    output = [cnct_path[0]]
    output_ids = [cnct_path[1]]
    while discnct_path[0]:
        cnct_path, discnct_path = split_path_check(graph=rc_graph, world=world, path=discnct_path[0], path_ids=discnct_path[1])
        output += [cnct_path[0]]
        output_ids += [cnct_path[1]]

    
    #draw_all_paths(rc_graph, output_ids)

    return output, output_ids

def check_path_connectivity(graph: ReconGraph, world: World, path: list, path_ids: list) -> bool:
    path_edges = reversed([(path[n],path[n+1]) for n in range(len(path)-1)])
    edge_ids = [(path_ids[n],path_ids[n+1]) for n in range(len(path_ids)-1)]
    blocks = {block.id:True for block in world.configuration.blocks if block}
    for block in path_ids:
        if type(block) == int:
            blocks[block] = False


    def filter_node(node):
        try:
            return blocks[node]
        except:
            return False
    
    def filter_edge(node1, node2):
        return graph.cnct_G[node1][node2].get("edge_connected", True)

    for ind, edge in enumerate(path_edges):
        block = world.configuration.get_block_p(edge[0])
        if block:
            blocks[edge_ids[(-ind)-1][1]] = True
            only_blocks_view = subgraph_view(graph.cnct_G, filter_node=filter_node, filter_edge=filter_edge)
            if not is_move_valid_can_blocked(graph.cnct_G, edge, node=edge_ids[(-ind)-1][0]):
                return False
            if not is_weakly_connected(only_blocks_view):
                return False
            blocks[edge_ids[(-ind)-1][1]] = False
           
    return True

def split_path_check(graph: ReconGraph, world: World, path: list, path_ids: list) -> list:
    path_edges = reversed([(path[n],path[n+1]) for n in range(len(path)-1)])
    edge_ids = [(path_ids[n],path_ids[n+1]) for n in range(len(path_ids)-1)]
    blocks = {block.id:True for block in world.configuration.blocks if block}
    # for block in path_ids:
    #     if type(block) == int:
    #         blocks[block] = False


    def filter_node(node):
        try:
            return blocks[node]
        except:
            return False
    
    def filter_edge(node1, node2):
        return graph.cnct_G[node1][node2].get("edge_connected", True)

    prev_move = None

    for ind, edge in enumerate(path_edges):
        block = world.configuration.get_block_p(edge[0])
        if block:
            blocks[edge_ids[(-ind)-1][0]] = False
            # blocks[edge_ids[(-ind)-1][1]] = True
            only_blocks_view = subgraph_view(graph.cnct_G, filter_node=filter_node, filter_edge=filter_edge)
            if not is_move_valid_with_prev_move(cur_move = edge, prev_move = prev_move):
                connected_split = path[(-ind)-1:]
                connected_split_ids = path_ids[(-ind)-1:]
                discnct_split = path[:(-ind)]
                discnct_split_ids = path_ids[:(-ind)]
                return (connected_split, connected_split_ids), (discnct_split, discnct_split_ids)
            if not is_move_valid_can_blocked(graph=graph.cnct_G, move=edge, node=edge_ids[(-ind)-1][0]):
                connected_split = path[(-ind)-1:]
                connected_split_ids = path_ids[(-ind)-1:]
                discnct_split = path[:(-ind)]
                discnct_split_ids = path_ids[:(-ind)]
                return (connected_split, connected_split_ids), (discnct_split, discnct_split_ids)
            if not is_weakly_connected(only_blocks_view):
                connected_split = path[(-ind)-1:]
                connected_split_ids = path_ids[(-ind)-1:]
                discnct_split = path[:(-ind)]
                discnct_split_ids = path_ids[:(-ind)]
                return (connected_split, connected_split_ids), (discnct_split, discnct_split_ids)
            # blocks[edge_ids[(-ind)-1][0]] = False
            # blocks[edge_ids[(-ind)-1][1]] = False
            prev_move = edge
           
    return (path, path_ids), ([],[])


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
