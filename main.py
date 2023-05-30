import shapes
from world import *
from algorithms import transform_xy_monot, mark_finished_blocks
from GT_graph import reconfig_graph
#import matplotlib
#matplotlib.use('gtk3agg')
from graph_tool.all import *

import networkx as nx
from NX_graph import ReconGraph



DEBUG = True

def main():
    # start: Configuration = shapes.xy_monotone(max_x=6, max_y=6, max_vol=12, seed=19)
    # out_start: Configuration = shapes.xy_monotone(max_x=6, max_y=6, max_vol=10, seed=19)
    # target: Configuration = shapes.xy_monotone(max_x=5, max_y=5, max_vol=12, seed=1)

    # start: Configuration = shapes.xy_monotone(max_x=6, max_y=6, max_vol=20, seed=19)
    # out_start: Configuration = shapes.xy_monotone(max_x=6, max_y=6, max_vol=10, seed=19)
    # target: Configuration = shapes.xy_monotone(max_x=6, max_y=6, max_vol=20, seed=1)

    # start: Configuration = shapes.xy_monotone(max_x=10, max_y=10, max_vol=10, seed=5)
    # out_start: Configuration = shapes.xy_monotone(max_x=10, max_y=10, max_vol=10, seed=5)
    # target: Configuration = shapes.xy_monotone(max_x=10, max_y=10, max_vol=10, seed=1)

    # start: Configuration = shapes.xy_monotone(max_x=10, max_y=10, max_vol=20, seed=9)
    # out_start: Configuration = shapes.xy_monotone(max_x=10, max_y=10, max_vol=10, seed=5)
    # target: Configuration = shapes.xy_monotone(max_x=10, max_y=10, max_vol=20, seed=1)

    # Example D in [[Transforming one xy-monotone shape to another]]
    # start: Configuration = shapes.xy_monotone(max_x=6, max_y=6, max_vol=10, seed=19)
    # out_start: Configuration = shapes.xy_monotone(max_x=6, max_y=6, max_vol=10, seed=19)
    # target: Configuration = shapes.xy_monotone(max_x=5, max_y=5, max_vol=10, seed=1)

    # Bigger example
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


    max_x: int = max((start.boundary[0], target.boundary[0]))
    max_y: int = max((start.boundary[1], target.boundary[1]))

    world: World = World(max_x, max_y)
    world.add_configuration(start)
    world.print_world()
    world.add_targets(target=target)
    # outworld: World = World(max_x, max_y)
    # outworld.add_configuration(out_start)

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

    


if __name__ == "__main__":
    main()
