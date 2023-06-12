import networkx as nx
from model.world import World
import matplotlib
matplotlib.use('gtk3agg')
import matplotlib.pyplot as plt
from graphs.utils import *

class MatchGraph:
    def __init__(self, world: World) -> None:
        self.match_G = nx.DiGraph()
        self.world = world

        self.add_nodes()
        self.add_edges()
        # self.mark_blocks()

        self.src_blocks = get_source_blocks(graph=self.match_G)
        self.trgt_blocks = get_target_blocks(graph=self.match_G)

        # self.make_path_graph()

    def add_nodes(self):
        perimeterID = 0
        for x in range(len(self.world.used_cells)):
            for y in range(len(self.world.used_cells[x])):
                cell_type = self.world.used_cells[x][y]
                if cell_type == -2:
                    self.match_G.add_node(f"P{perimeterID}", loc=(x-1, y-1), color="gray", \
                        move_color="gray", move_status=None, type="perimeter", status=None)
                    perimeterID += 1
                elif cell_type >= 0:
                    block = self.world.configuration.get_block_p((x-1, y-1))
                    if block.status == 'source':
                        self.match_G.add_node(block.id, loc=block.p, color="green", \
                            move_color="blue", move_status="normal", type="block", status="source")

                    elif block.status == 'block':
                        self.match_G.add_node(block.id, loc=block.p, color="blue", \
                            move_color="blue", move_status="normal", type="block", status=None)
                elif cell_type == -3:
                    block = self.world.get_target_p((x-1, y-1))
                    self.match_G.add_node(f"T{block.id}", loc=block.p, color="black", \
                        move_color="black", move_status="None", type="perimeter", status="target")
        

    def add_edges(self):
        for node in self.match_G.nodes(data=True):
            if node[1]["type"] == "block" and (node[1]["status"] == None or node[1]["status"] == "source"):
                block = self.world.configuration.get_block_id(node[0])
                for pos_val, nb_tag in [((0,1),'N'), ((1, 1), 'NE'), ((1,0),'E'), ((1,-1), 'SE')\
                                    ,((0,-1),'S'), ((-1,-1), 'SW'), ((-1,0),'W'), ((-1,1), 'NW')]:
                    nb = block.neighbours[nb_tag]
                    if nb:
                        nb_node = get_node_frm_attr(graph=self.match_G, attr="loc", val=nb.p)
                        if nb_tag in ['N', 'E', 'S', 'W']:
                            self.match_G.add_edge(node[0], nb_node, edge_connected=True, edge_dir=nb_tag)
                        else:
                            self.match_G.add_edge(node[0], nb_node, edge_connected=False, edge_dir=nb_tag)
                        continue
                    nb_node = get_node_frm_attr(graph=self.match_G, attr="loc", val=(block.p[0]+pos_val[0], block.p[1]+pos_val[1]))
                    if nb_node:
                        if nb_tag in ['N', 'E', 'S', 'W']:
                            self.match_G.add_edge(node[0], nb_node, edge_connected=True, edge_dir=nb_tag)
                        else:
                            self.match_G.add_edge(node[0], nb_node, edge_connected=False, edge_dir=nb_tag)
            
            if node[1]["type"] == "perimeter" and node[1]["status"] == "target":
                for pos_val, nb_tag in [((0,1),'N'), ((1, 1), 'NE'), ((1,0),'E'), ((1,-1), 'SE')\
                                    ,((0,-1),'S'), ((-1,-1), 'SW'), ((-1,0),'W'), ((-1,1), 'NW')]:
                    pos = node[1]["loc"]
                    nb_pos = (pos[0]+pos_val[0], pos[1]+pos_val[1])
                    nb_ind = get_node_frm_attr(graph=self.match_G, attr="loc", val=nb_pos)
                    if nb_ind:
                        neighbour = self.match_G.nodes[nb_ind]
                        if neighbour["type"] == "perimeter" and neighbour["status"] == "target" and nb_tag in ['N', 'E', 'S', 'W']:
                            self.match_G.add_edge(node[0], nb_ind, edge_connected=True, edge_dir=nb_tag)
                        elif neighbour["type"] == "perimeter" and neighbour["status"] == "target" and nb_tag not in ['N', 'E', 'S', 'W']:
                            self.match_G.add_edge(node[0], nb_ind, edge_connected=False, edge_dir=nb_tag)
        
    def add_perimeter_edges(self):
        for node in self.path_G.nodes(data=True) :
            if node[1]["type"] == "perimeter" and not node[1]["status"]:
                for nb_p, nb_i in [((0,1),'N'), ((1, 1), 'NE'), ((1,0),'E'), ((1,-1), 'SE')\
                                    ,((0,-1),'S'), ((-1,-1), 'SW'), ((-1,0),'W'), ((-1,1), 'NW')]:
                    p = node[1]["loc"]
                    x = nb_p[0] + p[0]
                    y = nb_p[1] + p[1]
                    if x < -1 or y < - 1 or x > len(self.world.used_cells) - 2 or y >= len(self.world.used_cells[0]) - 2:
                        continue
                    if self.world.used_cells[x+1][y+1] != -1:
                        my_in_edges = self.match_G.in_edges(node[0])
                        nb_node = get_node_frm_attr(graph=self.path_G, attr="loc", val=(x, y))
                        nb_in_edges = self.match_G.in_edges(nb_node)
                        # self.path_G.add_edge(node[0], nb_node, edge_connected=None, edge_dir=nb_i)
                        for my_edge in my_in_edges:
                            for nb_edge in nb_in_edges:
                                if my_edge[0] == nb_edge[0] and self.match_G.nodes[my_edge[0]]["type"] == "block":
                                    self.path_G.add_edge(node[0], nb_node, edge_connected=None, edge_dir=nb_i)

    def add_match_labels(self, matching_islands: list):
        match_id = 0
        for matching_lst in matching_islands:
            for matched_blocks in matching_lst:
                node1 = get_node_frm_attr(graph=self.match_G, attr="loc", val=matched_blocks[0])
                node2 = get_node_frm_attr(graph=self.match_G, attr="loc", val=matched_blocks[1])
                self.match_G.nodes[node1]["match_ID"] = match_id
                self.match_G.nodes[node2]["match_ID"] = match_id
                match_id += 1


    def draw_match_labels(self):
        pos = nx.get_node_attributes(self.match_G, 'loc')
        node_color = nx.get_node_attributes(self.match_G, 'color')
        labels = nx.get_node_attributes(self.match_G, 'match_ID')
        nx.draw_networkx_nodes(self.match_G,pos=pos, node_color=node_color.values())
        nx.draw_networkx_labels(self.match_G,pos=pos, labels=labels, font_color="whitesmoke")
        nx.draw_networkx_edges(self.match_G, pos=pos, edgelist=self.match_G.edges, edge_color = "black", width=1)
        plt.show()

