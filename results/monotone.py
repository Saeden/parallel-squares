import shapes.shapes as shapes
from model.world import *
from model.configuration import Configuration
from model.util import deserialize
from algorithms.block_matching import matching_monotone, sequential_transform
from graph_tool.all import *
from graphs.matched import MatchGraph
import random
import time
import os
import json

def get_monotone_results():
    number_of_blocks = [10,25,50,100,200,500,1000]
    # number_of_blocks = [10]

    seed_list = range(1000)
#    seed_list = [1]

   

    for block_num in number_of_blocks:
        if block_num == 200:
            seed_list = range(100)
        if block_num == 500:
            seed_list = range(50)
        if block_num == 1000:
            seed_list = range(10)

        num_err_configs_monotone = 0
        error_configs_monotone = []

        num_err_configs_seq = 0
        error_configs_seq = []

        moves_per_solve_monotone = []
        all_moves_per_solve_monotone = []
        moves_per_solve_seq = []

        time_per_solve_monotone = []
        time_per_solve_seq = []


        print(f"\n\n\nStarting reconfiguration of shapes of size {block_num}")

        for seed in seed_list:
            start_path = f"results/shapes/{block_num}/shape_{seed+1}_size_{block_num}_start.json"
            target_path = f"results/shapes/{block_num}/shape_{seed+1}_size_{block_num}_target.json"

            monotone_move_num, all_move_nums, correct, error, mono_time = get_monotone_match_result(start_path, target_path, seed, block_num)
            if error or not correct:
                num_err_configs_monotone += 1
                error_configs_monotone.append(f"Type: {block_num}, Seed: {seed}, Correct:{correct}, Error: {error}")
                error = None
            else:
                moves_per_solve_monotone.append(monotone_move_num)
                all_moves_per_solve_monotone.append(all_move_nums)
                time_per_solve_monotone.append(mono_time)
                
            sequential_move_num, correct, error, seq_time = get_sequential_result(start_path,target_path,seed, block_num)
            if error or not correct:
                num_err_configs_seq += 1
                error_configs_seq.append(f"Type: {block_num}, Seed: {seed}, Correct: {correct}, Error: {error}")
                error = None
            else:
                moves_per_solve_seq.append(sequential_move_num)
                time_per_solve_seq.append(seq_time)
                
        
        average_move_monotone = sum(moves_per_solve_monotone)/len(moves_per_solve_monotone)
        average_time_monotone = sum(time_per_solve_monotone)/len(time_per_solve_monotone)

        average_move_seq = sum(moves_per_solve_seq)/len(moves_per_solve_seq)
        average_time_seq = sum(time_per_solve_seq)/len(time_per_solve_seq)

        # print("\n\n\n")
        print(f"Tested {len(seed_list)} cases, with {block_num} blocks for the start and target config.")
        print(f"Out of these {len(seed_list)} cases {num_err_configs_monotone} gave an error during monotone matching reconfiguration")
        print(f"Out of these {len(seed_list)} cases {num_err_configs_seq} gave an error during sequential reconfiguration")
        print(f"The configurations that errored for the monotone alg were: {error_configs_monotone}")
        print(f"The configurations that errored for the seq alg were: {error_configs_seq}\n")
        print(f"The average number of moves for each case during monotone matching was {average_move_monotone}")
        # print(f"The number of moves for each case were: {moves_per_solve_monotone}")
        print(f"The average time for each case during monotone matching was {average_time_monotone}") 
        print(f"The total time to complete all reconfigurations with the monotone alg was: {sum(time_per_solve_monotone)}")
        # print(f"The time for each case was: {time_per_solve_monotone}\n")
        print(f"The average number of moves for each case during sequential reconf was {average_move_seq}")
        # print(f"The number of moves for each case were: {moves_per_solve_seq}")
        print(f"The average time for each case during sequential reconf was {average_time_seq}")
        print(f"The total time to complete the sequential reconf was: {sum(time_per_solve_seq)}\n\n")
        # print(f"The time for each case was: {time_per_solve_seq}")


        directory = f"results/json_results"
        file_name = f"results_size_{block_num}_shapes_{len(seed_list)}.json"

        if not os.path.exists(directory):
            os.makedirs(directory)

        path = os.path.join(directory, file_name)
            
        obj = { 
            '_version': 1,
            'avg_moves_monotone': average_move_monotone,
            'avg_time_monotone':  average_time_monotone,
            'avg_moves_seq': average_move_seq,
            'avg_time_seq': average_time_seq,
            'total_move_nums_monotone': moves_per_solve_monotone, 
            'all_move_nums': all_moves_per_solve_monotone,
            'times_monotone': time_per_solve_monotone,
            'errors_monotone': error_configs_monotone,
            'total_move_nums_seq': moves_per_solve_seq,
            'times_seq': time_per_solve_seq,
            'errors_seq': error_configs_seq
            }
        
        with open(path, "w") as json_file:
            json.dump(obj, json_file, cls=Int64Encoder)

            num_err_configs = 0
            moves_per_solve = []


# somehow the json does not recognise one of the number so this is necessary        
class Int64Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.int64):
            return int(obj)
        return super(Int64Encoder, self).default(obj)

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
        # print(f"\nRun the monotone algorithm for shape {seed+1} of size {block_num}:\nThe shape currently looks like this...")
        # world_monotone.print_world()
        # print()
        start_time = time.time()
        world_monotone, move_num, all_move_nums = matching_monotone(world_monotone)
        end_time = time.time() - start_time
        # print("The finished shape looks like this.")
        # world_monotone.print_world()
        # print()
        error = None
        correct = check_configuration(world=world_monotone, target=deserialize(target_path))

    except Exception as e:
        print(f"An error occured in the monotone alg during reconfiguration of shape {seed+1} of size {block_num}...")
        print(e)
        print("At the time of error the shape looked like this:")
        world_monotone.print_world()
        print()
        correct = False
        error = e
        end_time = -1
        all_move_nums = (0,0,0)

    

    return move_num, all_move_nums, correct, error, end_time
 

def get_sequential_result(start_path, target_path, seed, block_num):
    start_seq = deserialize(start_path)
    # target_seq: Configuration = deepcopy(target)
    target_seq = deserialize(target_path)
    world_seq = create_world(start_seq, target_seq)

    move_num = 0           
    try:
        # print(f"\nRun the sequential algorithm for shape {seed+1} of size {block_num}:\nThe shape currently looks like this...")
        # world_seq.print_world()
        # print()
        start_time = time.time()
        world_seq, move_num = sequential_transform(world_seq)
        end_time = time.time() - start_time
        # print("The finished shape looks like this.")
        # world_seq.print_world()
        # print()
        error = None
        correct = check_configuration(world=world_seq, target=deserialize(target_path))
    except Exception as e:
        print(f"An error occured during the sequential reconfiguration of of shape {seed+1} and size {block_num}...")
        print(e)
        print("At the time of error the shape looked like this:")
        world_seq.print_world()
        print()
        correct=False
        error=e
        end_time = -1
       

    return move_num, correct, error, end_time

def create_world(start: Configuration, target: Configuration) -> World:
    max_x: int = max((start.boundary[0], target.boundary[0]))
    max_y: int = max((start.boundary[1], target.boundary[1]))

    world: World = World(max_x, max_y)
    world.add_configuration(start)
    world.add_targets(target=target)
    # world.add_boundary(max_x, max_y)

    return world
