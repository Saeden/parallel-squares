import random
from world import *

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
