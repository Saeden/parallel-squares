from block import Block
import numpy as np

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
        block.rm_neighbours()
        # self.blocks[block.id] = None
        # np.delete(self.blocks, block.id)

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