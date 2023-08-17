import networkx as nx
from model.world import World
from graphs.utils import *
from model.block import Block
from graphs.drawing import draw_path_graph, draw_move_colors

class ConnectGraph:
    def __init__(self, world: World) -> None:
        self.cnct_G = nx.DiGraph()
        self.world = world

        self.add_nodes()
        self.add_edges()
        self.mark_blocks()

        self.src_blocks = get_source_blocks(graph=self.cnct_G)
        self.trgt_blocks = get_target_blocks(graph=self.cnct_G)

        
        

    def add_nodes(self):
        perimeterID = 0
        num_cols = len(self.world.used_cells)
        num_rows = len(self.world.used_cells[0])

        for x in range(num_cols):
            for y in range(num_rows):
                cell_type: int = self.world.used_cells[x][y]
                
                if cell_type == -2: #Perimeter node
                    self.cnct_G.add_node(
                            f"P{perimeterID}", 
                            loc=(x-1, y-1), 
                            color="gray",
                            move_color="gray", 
                            move_status=None, 
                            type="perimeter", 
                            status=None)
                    perimeterID += 1

                elif cell_type >= 0: #Block node
                    block = self.world.configuration.get_block_p((x-1, y-1))
                    if block.status == 'source':
                        self.cnct_G.add_node(
                                block.id, 
                                loc=block.p, 
                                color="green",
                                move_color="blue",
                                move_status="normal",
                                type="block", 
                                status="source")

                    elif block.status == 'block':
                        self.cnct_G.add_node(
                                block.id, 
                                loc=block.p, 
                                color="blue",
                                move_color="blue", 
                                move_status="normal", 
                                type="block", 
                                status=None)
                
                elif cell_type == -3: #Target node
                    block = self.world.get_target_p((x-1, y-1))
                    self.cnct_G.add_node(
                            f"T{block.id}", 
                            loc=block.p, 
                            color="black", 
                            move_color="black", 
                            move_status="None", 
                            type="perimeter", 
                            status="target")
        

    def add_edges(self):
        for node in self.cnct_G.nodes(data=True):
            node_type = node[1]["type"]
            node_status = node[1]["status"]

            if node_type == "block" and (node_status == None or node_status == "source"):
                self.add_block_neighbours(node)

            elif node_type == "perimeter":
                self.add_perimeter_neighbours(node)

 
    def add_block_neighbours(self, node):
        nb_xy_diff = [(0,1),(1, 1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1)]
        nb_tags = ['N','NE','E','SE', 'S','SW', 'W', 'NW']
        block: Block = self.world.configuration.get_block_id(node[0])

        for tag_index, pos_val in enumerate(nb_xy_diff):
            nb_tag = nb_tags[tag_index]

            nb: Block or None = block.neighbours[nb_tag]
            if nb and nb_tag in ['N', 'E', 'S', 'W']:
                nb_node = get_node_frm_attr(graph=self.cnct_G, attr="loc", val=nb.p)
                self.cnct_G.add_edge(node[0], nb_node, edge_connected=True, edge_dir=nb_tag)
            elif nb and nb_tag not in ['N', 'E', 'S', 'W']:
                nb_node = get_node_frm_attr(graph=self.cnct_G, attr="loc", val=nb.p)
                self.cnct_G.add_edge(node[0], nb_node, edge_connected=False, edge_dir=nb_tag)

            nb_node = get_node_frm_attr(graph=self.cnct_G, attr="loc", val=(block.p[0]+pos_val[0], block.p[1]+pos_val[1]))
            if nb_node and nb_tag in ['N', 'E', 'S', 'W']:
                self.cnct_G.add_edge(node[0], nb_node, edge_connected=True, edge_dir=nb_tag)
            elif nb_node and nb_tag not in ['N', 'E', 'S', 'W']:
                self.cnct_G.add_edge(node[0], nb_node, edge_connected=False, edge_dir=nb_tag)

    
    def add_perimeter_neighbours(self, node):
        nb_xy_diff = [(0,1),(1, 1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1)]
        nb_tags = ['N','NE','E','SE', 'S','SW', 'W', 'NW']
        for tag_index, nb_pos_diff in enumerate(nb_xy_diff):
            nb_tag = nb_tags[tag_index]
            node_pos = node[1]["loc"]
            nb_x = nb_pos_diff[0] + node_pos[0]
            nb_y = nb_pos_diff[1] + node_pos[1]
            
            num_cols = len(self.world.used_cells)
            num_rows = len(self.world.used_cells[0])
            if nb_x < -1 or nb_y < - 1 or nb_x > num_cols - 2 or nb_y >= num_rows - 2:
                continue

            nb_type = self.world.used_cells[nb_x+1][nb_y+1]
            if nb_type != -1:
                nb_node = get_node_frm_attr(graph=self.cnct_G, attr="loc", val=(nb_x, nb_y))
                self.cnct_G.add_edge(node[0], nb_node, edge_connected=None, edge_dir=nb_tag)
                          
    def mark_blocks(self):
        for node in self.cnct_G.nodes.data("type"):
            orth_nbs = get_orth_in_neighbours(graph=self.cnct_G, node=node)
            if node[1] == "block" and len(orth_nbs) == 1:
                self.cnct_G.nodes[node[0]]["move_status"] = "loose"
                self.cnct_G.nodes[node[0]]["move_color"] = "yellow"
                
                self.cnct_G.nodes[orth_nbs[0]]["move_status"] = "critical"
                self.cnct_G.nodes[orth_nbs[0]]["move_color"] = "red"

                if self.world.num_blocks <= 3:
                    continue

                nb_nbs = get_orth_in_neighbours(graph=self.cnct_G, node=orth_nbs[0])
                try:
                    nb_nbs.remove(node[0])
                except:
                    pass
                if len(nb_nbs) == 1:
                    self.cnct_G.nodes[nb_nbs[0]]["move_status"] = "critical"
                    self.cnct_G.nodes[nb_nbs[0]]["move_color"] = "red"
            elif node[1] == "block":
                block = self.world.configuration.get_block_id(node[0])
                if not self.world.is_connected(skip=block):
                    self.cnct_G.nodes[node[0]]["move_status"] = "critical"
                    self.cnct_G.nodes[node[0]]["move_color"] = "red"
