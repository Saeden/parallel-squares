import shapes.shapes as shapes
from model.world import *
from model.configuration import Configuration
from model.util import deserialize
from algorithms.block_matching import matching_monotone
from graph_tool.all import *
from graphs.matched import MatchGraph
import random


def get_monotone_results():
    number_of_blocks = [10,25]#,50]#,100,200]
    number_of_blocks = [25]

    seed_list = range(10)
#    seed_list = [1]

    num_err_configs = 0
    error_configs = []

    for block_num in number_of_blocks:
        moves_per_solve = []
        correct_seeds = []
        #print(f"Testing shapes with {block_num} blocks:")
        for seed in seed_list:
            random.seed(seed)
            max_x = int(block_num/2)
            start: Configuration = shapes.xy_monotone_new(blocks=block_num,x=random.randint(2, max_x), seed=seed)
            target: Configuration = shapes.xy_monotone_new(blocks=block_num,x=random.randint(2, max_x), seed=seed)

            world = create_world(start, target)

            # if check_boundary(world):
            #     correct_seeds.append(seed)
            #     world.print_world()
            #     continue

            try:
                print(f"\nRun the monotone algorithm for shape {seed+1} of size {block_num}:\nThe shape currently looks like this...")
                world.print_world()
                print()
                world, move_num = matching_monotone(world)
                moves_per_solve.append(move_num)
                print("The finished shape looks like this.")
                world.print_world()
                print()
            except Exception as e:
                print("An error occured during reconfiguration...")
                print(e)
                print("At the time of error the shape looked like this:")
                world.print_world()
                print()
                num_err_configs += 1
                error_configs.append(f"Type: {block_num}, Seed: {seed}")
        
        print("\n\n\n")
        print(f"Tested {len(seed_list)} cases, with {block_num} blocks for the start and target config.")
        print(f"Out of these {len(seed_list)} cases {num_err_configs} gave an error during reconfiguration")
        print(f"The average number of moves for each case was {sum(moves_per_solve)/len(moves_per_solve)}")
        print(f"The number of moves for each case were: {moves_per_solve}")

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

def create_world(start: Configuration, target: Configuration) -> World:
    max_x: int = max((start.boundary[0], target.boundary[0]))
    max_y: int = max((start.boundary[1], target.boundary[1]))

    world: World = World(max_x, max_y)
    world.add_configuration(start)
    world.add_targets(target=target)
    # world.add_boundary(max_x, max_y)

    return world
