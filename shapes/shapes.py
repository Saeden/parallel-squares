import random
from model.world import *
from model.block import Block


DEBUG = False

def xy_monotone(max_x = 10, max_y = 10, max_vol = 50, DEBUG = DEBUG, seed = None):
    column_heights: list[int] = []
    if seed:
        random.seed(seed)
    #output: Configuration = Configuration((max_x, max_y))

    for i in range(max_x):
        rand_int = random.randrange(1, max_y)
        max_vol -= rand_int
        if max_vol <= 0:
            column_heights.append(rand_int + max_vol)
            max_vol -= max_vol
            #max_x = i + 1
            break
        elif i == max_x - 1 and max_vol > 0:
            column_heights.append(rand_int + max_vol)
            #if rand_int + max_vol > max_y:
            #    max_y = rand_int + max_vol
            max_vol -= max_vol
            break
        column_heights.append(rand_int)
    
    max_x = len(column_heights)  + 3
    max_y = max(column_heights)  + 3
    output: Configuration = Configuration((max_x, max_y))
    
    column_heights.sort(reverse=True)
    if DEBUG:
        shape = []

    id = 0
    for x in range(len(column_heights)):
        if DEBUG:
            column = []
        
        for y in range(column_heights[x]):
            if DEBUG:
                column.append(x)
            
            square = Block(p = (x, y), id = id)
            id += 1
            output.add(square)
        
        if DEBUG:
            shape.append(column)
   

    if DEBUG:
        tr_shape = transpose_monotone(shape)
        print_lists(tr_shape)
        print(f"MAX_VOL: {max_vol} (should be 0)")

    return output

def xy_monotone_new(blocks=50, x=10, DEBUG=DEBUG, seed=None):
    if seed:
        random.seed(seed)
        
    if x <= 0:
        raise ValueError("Number of groups (x) must be a positive integer.")
    
    if blocks <= 0:
        raise ValueError("Number to partition must be a positive integer.")
    

    groups = [0] * x
    
    # Distribute the blocks into x groups
    for i in range(blocks):
        while True:
            # Randomly select a group
            group_index = random.randint(0, x - 1)
            groups[group_index] += 1
            # Check if adding to this group would exceed the blocks
            if sum(groups) > blocks:
                groups[group_index] -= 1
                break

    max_x = len(groups)
    max_y = max(groups)
    output: Configuration = Configuration((max_x, max_y))

    if DEBUG:
        shape = []

    groups.sort(reverse=True)
    id = 0
    for x in range(len(groups)):
        if DEBUG:
            column = []
        
        for y in range(groups[x]):
            if DEBUG:
                column.append(x)
            
            square = Block(p = (x, y), id = id)
            id += 1
            output.add(square)
        
        if DEBUG:
            shape.append(column)
   

    if DEBUG:
        tr_shape = transpose_monotone(shape)
        print_lists(tr_shape)
        print(f"MAX_VOL: {max_vol} (should be 0)")

    return output


def specific_example1(start: bool):
    shape_coordinates = []
    if start:
        output: Configuration = Configuration((8+1, 9+1))
        source_block_coords = [(1,8), (2, 6), (3, 6), (6, 3), (6, 2), (7, 2)]
        shape_coordinates += source_block_coords
    else:
        output: Configuration = Configuration((10+1, 9+1))
        target_cell_coords = [(4, 4), (4, 5), (5, 4), (8, 1), (8, 0), (9, 0)]
        shape_coordinates += target_cell_coords


    #these are the shared blocks between the start and target
    shape_coordinates += [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8),\
                          (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7),\
                          (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), \
                          (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), \
                          (4, 0), (4, 1), (4, 2), (4, 3), \
                          (5, 0), (5, 1), (5, 2), (5, 3), \
                          (6, 0), (6, 1), \
                          (7, 0), (7, 1)]

    for id, coord in enumerate(shape_coordinates):
        output.add(Block(p=coord, id=id))
    

    return output

def specific_example2(start: bool):
    shape_coordinates = []
    if start:
        output: Configuration = Configuration((7+1, 8+1))
        source_block_coords = [(0, 7), (3, 3), (5, 1)]
        shape_coordinates += source_block_coords
    else:
        output: Configuration = Configuration((7+1, 10+1))
        target_cell_coords = [(1,6), (2,5), (4, 2)]
        shape_coordinates += target_cell_coords


    #these are the shared blocks between the start and target
    shape_coordinates += [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), \
                          (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5),\
                          (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), \
                          (3, 0), (3, 1), (3, 2),  \
                          (4, 0), (4, 1), \
                          (5, 0),
                          (6,0)]

    for id, coord in enumerate(shape_coordinates):
        output.add(Block(p=coord, id=id))
    

    return output

def specific_example3(start: bool):
    shape_coordinates = []
    if start:
        output: Configuration = Configuration((7+1, 8+1))
        source_block_coords = [(4, 1), (4, 2), (5, 1),]
        shape_coordinates += source_block_coords
    else:
        output: Configuration = Configuration((7+1, 10+1))
        target_cell_coords = [(2, 3), (2, 4),(1, 6)]
        shape_coordinates += target_cell_coords


    #these are the shared blocks between the start and target
    shape_coordinates += [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), \
                          (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5),\
                          (2, 0), (2, 1), (2, 2),  \
                          (3, 0), (3, 1), (3, 2),  \
                          (4, 0), \
                          (5, 0),
                          (6,0)]

    for id, coord in enumerate(shape_coordinates):
        output.add(Block(p=coord, id=id))
    

    return output

def left_flow_complicated(start: bool):
    shape_coordinates = []
    if start:
        output: Configuration = Configuration((7+1, 7+1))
        source_block_coords = [(3, 4), (5, 2), (6, 1), (6, 2)]
        shape_coordinates += source_block_coords
    else:
        output: Configuration = Configuration((7+1, 7+1))
        target_cell_coords = [(1, 6), (2, 5), (2, 6),(4, 3)]
        shape_coordinates += target_cell_coords


    #these are the shared blocks between the start and target
    shape_coordinates += [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6),
                          (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5),
                          (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), 
                          (3, 0), (3, 1), (3, 2), (3, 3), 
                          (4, 0), (4, 1), (4, 2), 
                          (5, 0), (5, 1),
                          (6,0)]

    for id, coord in enumerate(shape_coordinates):
        output.add(Block(p=coord, id=id))
    

    return output

def strip(axis: int, size: int):
    if axis == 0: # denotes the x axis
        output = Configuration((size, 1))
        for id in range(size):
            block = Block((id, 0), id=id)
            output.add(block=block)

    elif axis == 1:
        output = Configuration((1, size))
        for id in range(size):
            block = Block((0, id), id=id)
            output.add(block=block)

    else:
        raise ValueError("Axis needs to be either 0 or 1 (0 for a strip along the x-axis and 1 for a strip along the y-axis).")

    return output

def rectangle(x: int, y: int, loose_block: bool = False):
    output = Configuration((x, y))
    id = 0
    for col in range(x):
        for row in range(y):
            block = Block((col, row), id=id)
            output.add(block=block)
            id += 1

    if loose_block:
        rand = random.randint(0, 1)
        if rand:
            block = Block((col + 1, 0), id=id+1)
            output.add(block=block)
        else:
            block = Block((0, row + 1), id= id+1)
            output.add(block=block)

    return output

def transpose_monotone(lists):
    output = []

    for i, column in enumerate(lists):
        if i == 0:
            for char in column:
                output.append([char])
        else:
            column_diff = len(output) - len(column)
            for j, char in enumerate(column):
                output[j+column_diff].append(char)
    
    return output
