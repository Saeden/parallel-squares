import shapes
from world import *
from GT_graph import *
from algorithms import transform_xy_monot

def test_moves(world: World):
    
    print("\nAfter a move the world looks like this")
    block = world.configuration.get_block_id(2)
    world.move_block_to(block, (block.p[0]+1, block.p[1]))
    world.print_world()
    print("\nAfter another move the world looks like this")
    world.move_block_to(block, (block.p[0]+1, block.p[1]-1))
    world.print_world()

    print("\nAfter a move that disconnects throw an error")
    world.move_block_to(block, (block.p[0], block.p[1]+1))
    world.print_world()

    print("\nAfter a colliding move throw an error")
    world.move_block_to(block, (block.p[0]+1, block.p[1]-1))
    world.print_world()



def test_graph():
    block0 = Block((1,1), 0)

    blockN = Block((1,2), 3)
    blockE = Block((2,1), 2)
    blockS = Block((1,0), 1)
    blockW = Block((0,1), 4)

    blockNE = Block((2,2), 5)
    blockSE = Block((2,0), 6)
    blockSW = Block((0,0), 7)
    blockNW = Block((0,2), 8)

    # Testcase 1
    start1 = Configuration((1, 2))
    start1.add_list([block0, blockS])
    world1 = World(max_x=5, max_y=5)
    world1.add_configuration(start1)
    rc_world1 = reconfig_graph(world=world1)
    rc_world1.set_edge_filter(rc_world1.edge_properties["legal_moves"])
    graph_draw(rc_world1, vertex_text=rc_world1.vertex_index, pos=rc_world1.vertex_properties["disp_position"], \
        vertex_fill_color=rc_world1.vertex_properties["color"], edge_color=rc_world1.edge_properties["color"])

    # Testcase 2
    start1 = Configuration((2, 2))
    start1.add_list([block0, blockS, blockE])
    world1 = World(max_x=5, max_y=5)
    world1.add_configuration(start1)
    rc_world1 = reconfig_graph(world=world1)
    rc_world1.set_edge_filter(rc_world1.edge_properties["legal_moves"])
    graph_draw(rc_world1, vertex_text=rc_world1.vertex_index, pos=rc_world1.vertex_properties["disp_position"], \
        vertex_fill_color=rc_world1.vertex_properties["color"], edge_color=rc_world1.edge_properties["color"])


    # Testcase 3
    start1 = Configuration((3, 3))
    start1.add_list([block0, blockS, blockE, blockSE])
    world1 = World(max_x=5, max_y=5)
    world1.add_configuration(start1)
    rc_world1 = reconfig_graph(world=world1)
    rc_world1.set_edge_filter(rc_world1.edge_properties["legal_moves"])
    graph_draw(rc_world1, vertex_text=rc_world1.vertex_index, pos=rc_world1.vertex_properties["disp_position"], \
        vertex_fill_color=rc_world1.vertex_properties["color"], edge_color=rc_world1.edge_properties["color"])
    
    # Testcase 4
    start1 = Configuration((3, 3))
    start1.add_list([block0, blockS, blockE, blockN])
    world1 = World(max_x=5, max_y=5)
    world1.add_configuration(start1)
    rc_world1 = reconfig_graph(world=world1)
    rc_world1.set_edge_filter(rc_world1.edge_properties["legal_moves"])
    graph_draw(rc_world1, vertex_text=rc_world1.vertex_index, pos=rc_world1.vertex_properties["disp_position"], \
        vertex_fill_color=rc_world1.vertex_properties["color"], edge_color=rc_world1.edge_properties["color"])
    
    # Testcase 5
    start1 = Configuration((3, 3))
    start1.add_list([block0, blockS, blockNW, blockW, blockSW])
    world1 = World(max_x=5, max_y=5)
    world1.add_configuration(start1)
    rc_world1 = reconfig_graph(world=world1)
    rc_world1.set_edge_filter(rc_world1.edge_properties["legal_moves"])
    graph_draw(rc_world1, vertex_text=rc_world1.vertex_index, pos=rc_world1.vertex_properties["disp_position"], \
        vertex_fill_color=rc_world1.vertex_properties["color"], edge_color=rc_world1.edge_properties["color"])


if __name__ == "__main__":
    test_graph()