import shapes
from world import *
from algorithms import transform_xy_monot

def test_moves():
    
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