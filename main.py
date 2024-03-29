import shapes.shapes as shapes
from model.world import *
from model.configuration import Configuration
from model.util import deserialize
from algorithms.path_finding import transform_xy_monot, transform_shortest_path, transform_shortest_split
from algorithms.block_matching import matching_monotone
from graph_tool.all import *
from graphs.reconfiguration import ReconGraph
from results.monotone import get_monotone_results
import random


DEBUG = True

def main3():
    # # # hard coded specific example 2 | 3 islands
    # start: Configuration = shapes.specific_example2(start=True)
    # target: Configuration = shapes.specific_example2(start=False)

    # world = create_world(start, target)
    # world.print_world()
    # world, move_num = matching_monotone(world)
    get_monotone_results()

def main():
    start: Configuration = deserialize(path="gridsize_10x10_filledpercentage_70_id_8.json", dim=10)
    target: Configuration = deserialize(path="gridsize_10x10_filledpercentage_70_id_9.json", dim=10)

    world = create_world(start, target)
    world.print_world()

    print("\nRun the algorithm: ")
    world = transform_shortest_split(world)
    # world = transform_xy_monot(world)

def create_world(start: Configuration, target: Configuration) -> World:
    max_x: int = max((start.boundary[0], target.boundary[0]))
    max_y: int = max((start.boundary[1], target.boundary[1]))

    world: World = World(max_x, max_y)
    world.add_configuration(start)
    world.print_world()
    world.add_targets(target=target)

    return world
    

def main2():
    # start: Configuration = shapes.xy_monotone(max_x=6, max_y=6, max_vol=12, seed=19)
    # out_start: Configuration = shapes.xy_monotone(max_x=6, max_y=6, max_vol=10, seed=19)
    # target: Configuration = shapes.xy_monotone(max_x=5, max_y=5, max_vol=12, seed=1)

    # # This example is now hard coded in example 2
    # start: Configuration = shapes.xy_monotone(max_x=6, max_y=6, max_vol=20, seed=19)
    # out_start: Configuration = shapes.xy_monotone(max_x=6, max_y=6, max_vol=10, seed=19)
    # target: Configuration = shapes.xy_monotone(max_x=6, max_y=6, max_vol=20, seed=1)

    # start: Configuration = shapes.xy_monotone(max_x=10, max_y=10, max_vol=10, seed=5)
    # out_start: Configuration = shapes.xy_monotone(max_x=10, max_y=10, max_vol=10, seed=5)
    # target: Configuration = shapes.xy_monotone(max_x=10, max_y=10, max_vol=10, seed=1)

    # start: Configuration = shapes.xy_monotone(max_x=10, max_y=10, max_vol=20, seed=9)
    # out_start: Configuration = shapes.xy_monotone(max_x=10, max_y=10, max_vol=10, seed=5)
    # target: Configuration = shapes.xy_monotone(max_x=10, max_y=10, max_vol=20, seed=1)

    # # #Example D in [[Transforming one xy-monotone shape to another]]
    # start: Configuration = shapes.xy_monotone(max_x=6, max_y=6, max_vol=10, seed=19)
    # out_start: Configuration = shapes.xy_monotone(max_x=6, max_y=6, max_vol=10, seed=19)
    # target: Configuration = shapes.xy_monotone(max_x=5, max_y=5, max_vol=10, seed=1)

    # # Bigger example
    # start: Configuration = shapes.xy_monotone(max_x=50, max_y=50, max_vol=100, seed=9)
    # out_start: Configuration = shapes.xy_monotone(max_x=10, max_y=10, max_vol=10, seed=5)
    # target: Configuration = shapes.xy_monotone(max_x=50, max_y=50, max_vol=100, seed=1)

    # # STRIP 1 - small strip, x-axis to y-axis
    # start: Configuration = shapes.strip(axis=0, size=10)
    # target: Configuration = shapes.strip(axis=1, size=10)

    # # STRIP 2 - big strip, y-axis to x-axis
    # start: Configuration = shapes.strip(axis=1, size=40)
    # target: Configuration = shapes.strip(axis=0, size=40)

    # Rectangle 1 - tall to flat rectangle, no loose block
    start: Configuration = shapes.rectangle(5, 10)
    target: Configuration = shapes.rectangle(10, 5)

    # # hard coded specific example 1 ONLY right flow | 2 islands
    # start: Configuration = shapes.specific_example1(start=True)
    # target: Configuration = shapes.specific_example1(start=False)

    # # hard coded specific example 2 | 3 islands
    # start: Configuration = shapes.specific_example2(start=True)
    # target: Configuration = shapes.specific_example2(start=False)

    # # hard coded specific example 3 ONLY left flow | 1 island
    # start: Configuration = shapes.specific_example3(start=True)
    # target: Configuration = shapes.specific_example3(start=False)
    
    # # hard coded specific example 4 left flow | 1 island
    # start: Configuration = shapes.left_flow_complicated(start=True)
    # target: Configuration = shapes.left_flow_complicated(start=False)

    
    create_world(start=start, target=target)
    print(f"\nThe world contains {world.num_blocks} blocks")

    print("The world looks as follows:")
    world.print_world()

    
    

    # target_world: World = World(max_x, max_y)
    # target_world.add_configuration(target)

    # print("\nThe target world looks like this:")
    # target_world.print_world()

    # print("\nThe overlap of the start conf to the target conf:")
    # outworld = mark_finished_blocks(outworld, target)
    
    # outworld.print_world()
    # #world.print_world()

    # print("\nThe overlap from the target conf to the start conf:")
    # target_world = mark_finished_blocks(target_world, start)
    # target_world.print_world()
    # print()

    print("\nRun the algorithm: ")
    world = transform_xy_monot(world)

    # print("Make a matching...")
    # world =  matching_monotone(world) 


if __name__ == "__main__":
    main()
