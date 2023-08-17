from model.world import *
from graphs.connect import ConnectGraph
from networkx import is_weakly_connected, subgraph_view
from graphs.drawing import *
from graphs.utils import is_move_valid_can_blocked, is_move_valid_not_blocked, is_move_valid_with_prev_move

def transform_shortest_path(world: World):
    graph = ConnectGraph(world=world)
    move_num = 1
    print(f"The current number of source blocks is: {len(rc_graph.src_blocks)}\n")
    while graph.src_blocks:
        # draw_path_graph(rc_graph)

        max_path_pos, max_path = find_min_path(world, rc_graph)
        if not max_path_pos:
            pos_path, path = find_min_path(world, rc_graph)
            draw_all_paths_and_move_colors(rc_graph, max_path)
            raise ValueError("There are no connected paths :(")

        pos_path = max_path_pos
        try:
            world.execute_path(pos_path)
            print(f"\nThe current number of moves that have been made is {move_num}")
            print(f"The current number of source blocks is: {len(rc_graph.src_blocks)}\n")
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
            # draw_all_paths(rc_graph, [max_path])
                
                
            
        # rc_graph.draw_move_colors()
        # rc_graph.draw_path_graph()
        
        # rc_graph.draw_all_paths_and_move_colors([path])
        rc_graph = ReconGraph(world=world)
    
    draw_path_graph(rc_graph)