# This is a container class for the blocks/modules in the configuration, it contains the current location of the block in the world 
# (p for point), the id of the block which is an integer label, a list of the blocks it is connected to (neighbours) 
# and finally the the status which shows whether the block is intending to be part of the backbone during the next tick or will start 
# to move during that tick
class Block:
    def __init__(self, p: tuple[int, int], id: int):
        self.p = p
        self.id = id
        self.status: str = 'source'                         # status is in ['source', 'block', 'target']
        self.neighbours: dict[Block] = {'N': None, 'NE': None, 'E': None, 'SE': None, \
                                        'S': None, 'SW': None, 'W': None, 'NW': None}

    def degree(self):
        out = 0
        for nb in ['N', 'E', 'S', 'W']:
            if self.neighbours[nb]:
                out += 1
        return out
    
    # When the block moves it must set itself to None in the neighbour lists of its neighbours. 
    # So when block B1 has neighbour B2 in 'N' we must set the 'S' neighbour of B2 to None.
    def rm_neighbours(self):
        for nb in ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']:
            neighbour: Block or None = self.neighbours[nb]
            if neighbour:
                neighbour.rm_opposite(loc=nb)
                self.neighbours[nb] = None

    def rm_opposite(self, loc: str):
        if loc == 'N':
            self.neighbours['S'] = None
        elif loc == 'NE':
            self.neighbours['SW'] = None
        elif loc == 'E':
            self.neighbours['W'] = None
        elif loc == 'SE':
            self.neighbours['NW'] = None
        elif loc == 'S':
            self.neighbours['N'] = None
        elif loc == 'SW':
            self.neighbours['NE'] = None
        elif loc == 'W':
            self.neighbours['E'] = None
        elif loc == 'NW':
            self.neighbours['SE'] = None