import numpy as np
from termcolor import colored

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
        self.intention: str = ''                                # intention is in ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', '']

    def degree(self):
        out = 0
        for nb in ['N', 'E', 'S', 'W']:
            if self.neighbours[nb]:
                out += 1
        return out

    def check_intention(self):
        for neighbour in ['N', 'E', 'S', 'W']:
            if not self.neighbours[neighbour]:
                continue
            nb_intention = self.neighbours[neighbour].intention
            if nb_intention == '':
                continue
            if (self.intention in nb_intention or nb_intention in self.intention) and neighbour in ['E', 'W']:
                continue
            elif self.intention in nb_intention and neighbour == 'N':
                self.intention = ''
            elif self.intention in nb_intention and neighbour == 'S':
                nb_intention = ''
            else:
                raise Exception("This is a new case")

    # Transforms an intention str to an actual (x, y) location of where the block intends to move
    def intention_to_loc(self) -> tuple[int, int]:
        if self.intention == '':
            return ()
        if self.intention == 'N':
            return (self.p[0], self.p[1] + 1)
        if self.intention == 'NE':
            return (self.p[0] + 1, self.p[1] + 1)
        if self.intention == 'E':
            return (self.p[0] + 1, self.p[1])
        if self.intention == 'SE':
            return (self.p[0] + 1, self.p[1] - 1)
        if self.intention == 'S':
            return (self.p[0], self.p[1] - 1)
        if self.intention == 'SW':
            return (self.p[0] - 1, self.p[1] - 1)
        if self.intention == 'W':
            return (self.p[0] - 1, self.p[1])
        if self.intention == 'NW':
            return (self.p[0] - 1, self.p[1] + 1)
    
    # When the block moves it must set itself to None in the neighbour lists of its neighbours. 
    # So when block B1 has neighbour B2 in 'N' we must set the 'S' neighbour of B2 to None.
    def rm_neighbours(self):
        for nb in ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']:
            neighbour = self.neighbours[nb]
            if neighbour:
                neighbour.rm_opposite(loc=nb)

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




def direction(frm: tuple[int, int], to: tuple[int, int]) -> str:
    direction = (to[0]-frm[0], to[1]-frm[1])
    if direction == (0, 1):
        return 'N'
    if direction == (1, 1):
        return 'NE'
    if direction == (1, 0):
        return 'E'
    if direction == (1, -1):
        return 'SE'
    if direction == (0, -1):
        return 'S'
    if direction == (-1, -1):
        return 'SW'
    if direction == (-1, 0):
        return 'W'
    if direction == (-1, 1):
        return 'NW'
    else:
        raise Exception("Tried to move more than one block.")

# A glorified list of Blocks, which contains the the size of the boundary square of the configuration
class Configuration:
    def __init__(self, boundary: tuple[int, int] = (None, None)):
        self.blocks: np.array = np.empty(shape=boundary[1]*boundary[0], dtype=object)
        #self.blocks: list[Block] = []
        self.boundary: tuple[int, int] = boundary

    def add(self, block: Block) -> None:
        #cur_id = len(self.blocks)
        self.blocks[block.id] = block

        #self.blocks.append(block)

    def add_target(self, target: Block) -> None:
        end = len(self.blocks) - 1
        while(self.blocks[end]):
            end -= 1
        self.blocks[end] = target
        target.id = end

    def add_list(self, blocks: list) -> None:
        for block in blocks:
            self.add(block)
    
    def remove(self, block: Block) -> None:
        raise NotImplementedError
        #self.blocks.remove(block)

    # return a block given an ID
    # NB. the id is the index of the block in the blocks array
    def get_block_id(self, id: int) -> Block:
        return self.blocks[id]
        # for block in self.blocks:
        #     if block.id == id:
        #         return block
        # return None
    
    def get_block_p(self, p: tuple[int, int]) -> Block:
        for block in self.blocks:
            if not block:
                continue
            if block.p == p:
                return block
        return None

    def get_neighbours(self, block: Block) -> None:
        north = self.get_block_p((block.p[0], block.p[1] + 1))
        if north:
            block.neighbours['N'] = north
            north.neighbours['S'] = block
        else:
            block.neighbours['N'] = None

        north_east = self.get_block_p((block.p[0] + 1, block.p[1] + 1))
        if north_east:
            block.neighbours['NE'] = north_east
            north_east.neighbours['SW'] = block
        else:
            block.neighbours['NE'] = None

        east = self.get_block_p((block.p[0] + 1, block.p[1]))
        if east:
            block.neighbours['E'] = east
            east.neighbours['W'] = block
        else:
            block.neighbours['E'] = None

        south_east = self.get_block_p((block.p[0] + 1, block.p[1] - 1))
        if south_east:
            block.neighbours['SE'] = south_east
            south_east.neighbours['NW'] = block
        else:
            block.neighbours['SE'] = None

        south = self.get_block_p((block.p[0], block.p[1] - 1))
        if south:
            block.neighbours['S'] = south
            south.neighbours['N'] = block
        else:
            block.neighbours['S'] = None

        south_west = self.get_block_p((block.p[0] - 1, block.p[1] - 1))
        if south_west:
            block.neighbours['SW'] = south_west
            south_west.neighbours['NE'] = block
        else:
            block.neighbours['SW'] = None

        west = self.get_block_p((block.p[0] - 1, block.p[1]))
        if west:
            block.neighbours['W'] = west
            west.neighbours['E'] = block
        else:
            block.neighbours['W'] = None

        north_west = self.get_block_p(((block.p[0] - 1, block.p[1] + 1)))
        if north_west:
            block.neighbours['NW'] = north_west
            north_west.neighbours['SE'] = block
        else:
            block.neighbours['NW'] = None

    



class World:
    def __init__(self, max_x, max_y) -> None:
        self.used_cells: np.array = np.full((max_x+2, max_y+2), -1) #maybe add 2 to the (expected) boundary to allow for boundary moves
        self.num_blocks: int = 0
        self.configuration: Configuration = None
        self.perimeter: list = []

    def add_block(self, p: tuple[int, int], id):
       self.used_cells[p[0]+1][p[1]+1] = id
       self.num_blocks += 1

    def rm_block(self, p: tuple[int, int]):
        self.used_cells[p[0]][p[1]] = -1
        self.num_blocks -= 1

    def add_configuration(self, conf: Configuration):
        self.configuration = conf
        for block in conf.blocks:
            if not block:
                continue
            self.configuration.get_neighbours(block)
            self.add_block(block.p, block.id)

        self.get_perimeter()

    def add_targets(self, target: Configuration):
        for block in target.blocks:
            if not block:
                continue

            id = self.used_cells[block.p[0]+1][block.p[1]+1]
            if id >=0:
                conf_block = self.configuration.get_block_id(id)
                conf_block.status = 'block'
            else:
                self.used_cells[block.p[0]+1][block.p[1]+1] = -3
                block.status = 'target'
                self.configuration.add_target(block)
                self.configuration.get_neighbours(block)
        
        self.get_perimeter()
                
    
    def get_perimeter(self):
        for block in self.configuration.blocks:
            if not block:
                continue
            for p, nb in [((1,2),'N'), ((2,1),'E'), ((1,0),'S'), ((0,1),'W')]:
                if not block.neighbours[nb]:
                    self.perimeter.append((block.p, (block.p[0]+p[0]-1, block.p[1]+p[1]-1)))
                    self.used_cells[block.p[0]+p[0]][block.p[1]+p[1]] = -2

            


    def move_block_to(self, block: Block, to: tuple[int, int]):
        if self.is_valid(block, to):
            self.used_cells[block.p[0]+1][block.p[1]+1] = -1
            self.used_cells[to[0]+1][to[1]+1] = block.id
            block.p = to
            block.rm_neighbours()
            self.configuration.get_neighbours(block)
            self.get_perimeter()

    def is_valid(self, block: Block, to: tuple[int, int]) -> bool:
        try:
            self.has_collision(to)
        except:
            raise Exception(f"There was a collision moving block {block.id} from {block.p} to {to}")

        if not self.has_valid_neighbours(block, to):
            raise Exception(f"Tried to move block {block.id} from {block.p} to {to} but neighbours were not valid.")

        if not self.is_connected(skip=block):
            raise Exception(f"By moving block {block.id} from {block.p} to {to} the configuration disconnects.")

        return True

    def has_collision(self, to: tuple[int, int]) -> bool:
        target = self.used_cells[to[0]][to[1]]
        if target >= 0:
            return True
        return False

    def has_valid_neighbours(self, block: Block, to: tuple[int,int]) -> bool:
        direction = (to[0]-block.p[0], to[1]-block.p[1])
        if direction == (0, 1):    #N
            if block.neighbours['E'] and block.neighbours['NE'] or block.neighbours['W'] and block.neighbours['NW']:
                return True
        elif direction == (1, 1):  #NE or EN
            if block.neighbours['E'] and not block.neighbours['N'] or block.neighbours['N'] and not block.neighbours['E']:
                return True
        elif direction == (1, 0):  #E
            if block.neighbours['N'] and block.neighbours['NE'] or block.neighbours['S'] and  block.neighbours['SE']:
                return True
        elif direction == (1, -1): #SE or ES
            if block.neighbours['E'] and not block.neighbours['S'] or block.neighbours['S'] and not block.neighbours['E']:
                return True
        elif direction == (0, -1): #S
            if block.neighbours['E'] and block.neighbours['SE'] or block.neighbours['W'] and block.neighbours['SW']:
                return True
        elif direction == (-1, -1):#SW or WS
            if block.neighbours['W'] and not block.neighbours['S'] or block.neighbours['S'] and not block.neighbours['W']:
                return True
        elif direction == (-1, 0): #W
            if block.neighbours['N'] and block.neighbours['NW'] or block.neighbours['S'] and block.neighbours['SW']:
                return True
        elif direction == (-1, 1): #NW or WN
            if block.neighbours['W'] and not block.neighbours['N'] or block.neighbours['N'] and not block.neighbours['W']:
                return True
        else:
            return False



    def is_connected(self, skip: Block = None):
        seen = np.full(self.num_blocks, False)
        seenCount = 0
        queue = [0]

        if skip:
            seen[skip.id] = True
            seenCount += 1

            # special case: if we were about to start our BFS with the
			# skipped cube, then pick another cube to start with
			# (note that if the configuration has exactly 1 cube, which
			# is then skipped, the function should return true
			# but that works because the BFS starting at the skipped
			# cube will not encounter any cubes)
            # Thanks to Hakitaya et al. for this code/special case
            if skip.id == 0 and self.num_blocks > 1:
                queue = [1]

        while queue:
            currID = queue[0]
            if currID >= self.num_blocks:
                del queue[0]
                continue

            if seen[currID]:
                del queue[0]
                continue

            cur_block = self.configuration.get_block_id(currID)
            seen[currID] = True
            seenCount += 1


            for orth_nb in ['N', 'E', 'S', 'W']:
                neighbour = cur_block.neighbours[orth_nb]
                if neighbour:
                    queue.append(neighbour.id)
            
            del queue[0]

        return seenCount == self.num_blocks

    
    # Formats the world into a string format with the correct colors for different statuses
    def print_world(self):
        rows = self.used_cells.T
        rows = np.flipud(rows)
        output = []
        for row in rows:
            out_row = []
            for cell in row:
                if cell == -1:
                    out_row.append('  ')
                elif cell == -2:
                    out_row.append(colored('■ ', 'grey'))
                elif cell == -3:
                    out_row.append(colored('■ ', 'blue'))
                elif self.configuration.get_block_id(cell).status == 'source':
                    out_row.append(colored('■ ', 'red'))
                elif self.configuration.get_block_id(cell).status == 'finished':
                    out_row.append(colored('■ ', 'green'))
                else:
                    out_row.append('■ ')
        
            output.append(out_row)

        print_lists(output)




# Prints a list of lists to terminal in proper string format rather than in list format
def print_lists(lists):
        for row in lists:
            line = ""
            for char in row:
                line += str(char)
            print(line)