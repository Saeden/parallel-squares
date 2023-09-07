import shapes.shapes as shapes
from model.world import *
from model.configuration import Configuration
from model.util import deserialize
from algorithms.block_matching import matching_monotone, sequential_transform
from graph_tool.all import *
from graphs.matched import MatchGraph
import random

def get_monotone_results():
    # number_of_blocks = [10,25,50,100,200]
    number_of_blocks = [500]

    seed_list = range(1)
#    seed_list = [1]

    num_err_configs_monotone = 0
    error_configs_monotone = []

    num_err_configs_seq = 0
    error_configs_seq = []

    for block_num in number_of_blocks:
        moves_per_solve_monotone = []
        moves_per_solve_seq = []

        for seed in seed_list:
            start_path = f"results/shapes/{block_num}/shape_{seed+1}_size_{block_num}_start.json"
            target_path = f"results/shapes/{block_num}/shape_{seed+1}_size_{block_num}_target.json"

            monotone_move_num, correct, error = get_monotone_match_result(start_path, target_path, seed, block_num)
            if error or not correct:
                num_err_configs_monotone += 1
                error_configs_monotone.append(f"Type: {block_num}, Seed: {seed}, Correct:{correct}, Error: {error}")
                error = None
            else:
                moves_per_solve_monotone.append(monotone_move_num)
                
            sequential_move_num, correct, error = get_sequential_result(start_path,target_path,seed, block_num)
            if error or not correct:
                num_err_configs_seq += 1
                error_configs_seq.append(f"Type: {block_num}, Seed: {seed}, Correct: {correct}, Error: {error}")
                error = None
            else:
                moves_per_solve_seq.append(sequential_move_num)
                
        
        print("\n\n\n")
        print(f"Tested {len(seed_list)} cases, with {block_num} blocks for the start and target config.")
        print(f"Out of these {len(seed_list)} cases {num_err_configs_monotone} gave an error during monotone matching reconfiguration")
        print(f"Out of these {len(seed_list)} cases {num_err_configs_seq} gave an error during sequential reconfiguration")
        print(f"The average number of moves for each case during monotone matching was {sum(moves_per_solve_monotone)/len(moves_per_solve_monotone)}")
        print(f"The number of moves for each case were: {moves_per_solve_monotone}")
        print(f"The average number of moves for each case during sequential reconf was {sum(moves_per_solve_seq)/len(moves_per_solve_seq)}")
        print(f"The number of moves for each case were: {moves_per_solve_seq}")

        num_err_configs = 0
        moves_per_solve = []
        


def check_boundary(world: World) -> bool:
    graph = MatchGraph(world)
    row_targets = []
    column_targets = []
    for target in graph.trgt_blocks:
        location = graph.match_G.nodes[target]["loc"]
        if location[0] == 0 and location[1] != 0:
            column_targets.append((target, location))
        elif location[1] == 0 and location[0] != 0:
            row_targets.append((target, location))
        elif sum(location) == 0:
            raise ValueError("Configuration does not contain the origin.")
    
    row_sources = []
    col_sources = []
    for target in graph.src_blocks:
        location = graph.match_G.nodes[target]["loc"]
        if location[0] == 0 and location[1] != 0:
            col_sources.append((target, location))
        elif location[1] == 0 and location[0] != 0:
            row_sources.append((target, location))
        elif sum(location) == 0:
            raise ValueError("Configuration does not contain the origin.")   
    
    if col_sources or row_sources or row_targets or column_targets:
        return False
    else:
        return True

def check_configuration(world: World, target: Configuration) -> bool:
    for block in target.blocks:
        if block and not world.configuration.get_block_p(block.p):
            return False

    return True

def get_monotone_match_result(start_path:str, target_path:str, seed:int, block_num:int):
    start: Configuration = deserialize(start_path)
    target: Configuration = deserialize(target_path)

    world_monotone = create_world(start, target)
    move_num = 0
    try:
        print(f"\nRun the monotone algorithm for shape {seed+1} of size {block_num}:\nThe shape currently looks like this...")
        world_monotone.print_world()
        print()
        world_monotone, move_num = matching_monotone(world_monotone)
        print("The finished shape looks like this.")
        world_monotone.print_world()
        print()
        error = None
        correct = check_configuration(world=world_monotone, target=deserialize(target_path))

    except Exception as e:
        print("An error occured in the monotone alg during reconfiguration...")
        print(e)
        print("At the time of error the shape looked like this:")
        world_monotone.print_world()
        print()
        correct = False
        error = e

    

    return move_num, correct, error
 

def get_sequential_result(start_path, target_path, seed, block_num):
    start_seq = deserialize(start_path)
    # target_seq: Configuration = deepcopy(target)
    target_seq = deserialize(target_path)
    world_seq = create_world(start_seq, target_seq)

    move_num = 0           
    try:
        print(f"\nRun the sequential algorithm for shape {seed+1} of size {block_num}:\nThe shape currently looks like this...")
        world_seq.print_world()
        print()
        world_seq, move_num = sequential_transform(world_seq)
        print("The finished shape looks like this.")
        world_seq.print_world()
        print()
        error = None
        correct = check_configuration(world=world_seq, target=deserialize(target_path))
    except Exception as e:
        print("An error occured during the sequential reconfiguration...")
        print(e)
        print("At the time of error the shape looked like this:")
        world_seq.print_world()
        print()
        correct=False
        error=e
       

    return move_num, correct, error

def create_world(start: Configuration, target: Configuration) -> World:
    max_x: int = max((start.boundary[0], target.boundary[0]))
    max_y: int = max((start.boundary[1], target.boundary[1]))

    world: World = World(max_x, max_y)
    world.add_configuration(start)
    world.add_targets(target=target)
    # world.add_boundary(max_x, max_y)

    return world
