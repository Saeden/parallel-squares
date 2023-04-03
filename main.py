import shapes
from world import *
from algorithms import transform_xy_monot, mark_finished_blocks
from graph import reconfig_graph
import matplotlib
matplotlib.use('gtk3agg')
from graph_tool.all import *


DEBUG = True

def main():
    # start: Configuration = shapes.xy_monotone(max_x=6, max_y=6, max_vol=10, seed=19)
    # out_start: Configuration = shapes.xy_monotone(max_x=6, max_y=6, max_vol=10, seed=19)
    # target: Configuration = shapes.xy_monotone(max_x=5, max_y=5, max_vol=10, seed=1)

    # start: Configuration = shapes.xy_monotone(max_x=10, max_y=10, max_vol=10, seed=5)
    # out_start: Configuration = shapes.xy_monotone(max_x=10, max_y=10, max_vol=10, seed=5)
    # target: Configuration = shapes.xy_monotone(max_x=10, max_y=10, max_vol=10, seed=1)

    start: Configuration = shapes.xy_monotone(max_x=10, max_y=10, max_vol=20, seed=9)
    out_start: Configuration = shapes.xy_monotone(max_x=10, max_y=10, max_vol=10, seed=5)
    target: Configuration = shapes.xy_monotone(max_x=10, max_y=10, max_vol=10, seed=1)

    max_x: int = max((start.boundary[0], target.boundary[0]))
    max_y: int = max((start.boundary[1], target.boundary[1]))

    world: World = World(max_x, max_y)
    world.add_configuration(start)
    outworld: World = World(max_x, max_y)
    outworld.add_configuration(out_start)

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

    #print("\nRun the algorithm: ")
    #world = transform_xy_monot(world, target)

    # Init graph
    rc_graph: Graph = reconfig_graph(start=world, target=target)
    # rc_graph.set_edge_filter(rc_graph.edge_properties["orth_neighbours"])
    # rc_graph.set_vertex_filter(rc_graph.vertex_properties["blocks"])
    graph_draw(rc_graph, vertex_text=rc_graph.vertex_properties["position"], pos=rc_graph.vertex_properties["disp_position"], \
        vertex_fill_color=rc_graph.vertex_properties["color"])

    # graph after move
    block = world.configuration.get_block_p((2, 4))
    world.move_block_to(block, to=(3,3))
    world.print_world()
    rc_graph: Graph = reconfig_graph(start=world, target=target)
    # rc_graph.set_edge_filter(rc_graph.edge_properties["orth_neighbours"])
    # rc_graph.set_vertex_filter(rc_graph.vertex_properties["blocks"])
    graph_draw(rc_graph, vertex_text=rc_graph.vertex_properties["position"], pos=rc_graph.vertex_properties["disp_position"], \
        vertex_fill_color=rc_graph.vertex_properties["color"])    


if __name__ == "__main__":
    main()
