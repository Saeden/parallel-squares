import networkx as nx
from world import World
import matplotlib.pyplot as plt
from itertools import islice



class ReconGraph:
    def __init__(self, world: World) -> None:
        self.con_G = nx.DiGraph()
        self.path_G = None
        self.world = world
        self.add_nodes()
        self.add_edges()
        self.mark_blocks()



        
    def add_nodes(self): # world: World, G: nx.DiGraph):
        perimeterID = 0
        for x in range(len(self.world.used_cells)):
            for y in range(len(self.world.used_cells[x])):
                cell_type = self.world.used_cells[x][y]
                if cell_type == -2:
                    self.con_G.add_node(f"P{perimeterID}", loc=(x-1, y-1), color="gray", \
                        move_color="gray", move_status=None, type="perimeter", status=None)
                    perimeterID += 1
                elif cell_type >= 0:
                    block = self.world.configuration.get_block_p((x-1, y-1))
                    if block.status == 'source':
                        self.con_G.add_node(block.id, loc=block.p, color="green", \
                            move_color="blue", move_status="normal", type="block", status="source")

                    elif block.status == 'block':
                        self.con_G.add_node(block.id, loc=block.p, color="blue", \
                            move_color="blue", move_status="normal", type="block", status=None)
                elif cell_type == -3:
                    block = self.world.configuration.get_block_p((x-1, y-1))
                    self.con_G.add_node(block.id, loc=block.p, color="black", \
                        move_color="black", move_status="None", type="block", status="target")

    def add_edges(self): # world: World, G: nx.DiGraph):
        for node in self.con_G.nodes.data("type"):
            if node[1] == "block":
                block = self.world.configuration.get_block_id(node[0])
                for nb_p, nb_i in [((0,1),'N'), ((1, 1), 'NE'), ((1,0),'E'), ((1,-1), 'SE')\
                                    ,((0,-1),'S'), ((-1,-1), 'SW'), ((-1,0),'W'), ((-1,1), 'NW')]:
                    nb = block.neighbours[nb_i]
                    if nb:
                        nb_node = get_node_frm_attr(graph=self.con_G, attr="loc", val=nb.p)
                        if nb_i in ['N', 'E', 'S', 'W']:
                            self.con_G.add_edge(node[0], nb_node, edge_connected=True, edge_dir=nb_i)
                        else:
                            self.con_G.add_edge(node[0], nb_node, edge_connected=False, edge_dir=nb_i)
                        continue
                    nb_node = get_node_frm_attr(graph=self.con_G, attr="loc", val=(block.p[0]+nb_p[0], block.p[1]+nb_p[1]))
                    if nb_node:
                        if nb_i in ['N', 'E', 'S', 'W']:
                            self.con_G.add_edge(node[0], nb_node, edge_connected=True, edge_dir=nb_i)
                        else:
                            self.con_G.add_edge(node[0], nb_node, edge_connected=False, edge_dir=nb_i)

    def mark_blocks(self): # G: nx.DiGraph):
        for node in self.con_G.nodes.data("type"):
            orth_nbs = get_orth_in_neighbours(graph=self.con_G, node=node)
            if node[1] == "block" and len(orth_nbs) == 1:
                self.con_G.nodes[node[0]]["move_status"] = "loose"
                self.con_G.nodes[node[0]]["move_color"] = "yellow"
                
                self.con_G.nodes[orth_nbs[0]]["move_status"] = "critical"
                self.con_G.nodes[orth_nbs[0]]["move_color"] = "red"

                if self.world.num_blocks <= 3:
                    continue

                nb_nbs = get_orth_in_neighbours(graph=self.con_G, node=orth_nbs[0])
                nb_nbs.remove(node[0])
                if len(nb_nbs) == 1:
                    self.con_G.nodes[nb_nbs[0]]["move_status"] = "critical"
                    self.con_G.nodes[nb_nbs[0]]["move_color"] = "red"

    def finds_all_paths(self):
        src_blocks = get_source_blocks(graph=self.con_G)
        trgt_blocks = get_target_blocks(graph=self.con_G)

        all_paths = []
        for src_block in src_blocks:
            path_to_targets = []
            for target_block in trgt_blocks:
                paths = list(nx.shortest_simple_paths(self.con_G, src_block, target_block))
                path_to_targets.append(paths[0])
            all_paths.append(min(path_to_targets))

        self.draw_all_paths(all_paths)


    def draw_normal_colors(self):
        pos = nx.get_node_attributes(self.con_G, 'loc')
        node_color = nx.get_node_attributes(self.con_G, 'color')
        nx.draw(self.con_G, with_labels=True, pos=pos, node_color=node_color.values())
        plt.show()

    def draw_move_colors(self):
        pos = nx.get_node_attributes(self.con_G, 'loc')
        node_color = nx.get_node_attributes(self.con_G, 'move_color')
        nx.draw(self.con_G, with_labels=True, pos=pos, node_color=node_color.values())
        plt.show()

    def draw_all_paths(self, paths: list):
        edges = []
        for p in paths:
            path_edges = [(p[n],p[n+1]) for n in range(len(p)-1)]
            edges.append(path_edges)

        pos = nx.get_node_attributes(self.con_G, 'loc')
        nx.draw_networkx_nodes(self.con_G,pos=pos)
        nx.draw_networkx_labels(self.con_G,pos=pos)
        nx.draw_networkx_edges(self.con_G, pos=pos, edgelist=self.con_G.edges, edge_color = "black", width=1)
        colors = ['r', 'b', 'y']
        linewidths = [5,3,2]
        for ctr, edgelist in enumerate(edges):
            nx.draw_networkx_edges(self.con_G,pos=pos,edgelist=edgelist,edge_color = colors[ctr%3], width=linewidths[ctr%3])
        plt.show()

def get_node_frm_attr(graph: nx.DiGraph, attr: str, val) -> int:
    for node in graph.nodes.data(attr):
        if node[1] == val:
            return node[0] # graph.nodes[node[0]]
    
    return None

def get_orth_in_neighbours(graph: nx.DiGraph, node) -> list:
    all_neighbours = graph.in_edges(node, data="edge_dir")
    output = []
    for nb in all_neighbours:
        if nb[2] in ['N', 'E', 'S', 'W']:
            output.append(nb[0])
    return output

def get_source_blocks(graph: nx.DiGraph) -> list[int]:
    output = []
    for node in graph.nodes(data="status"):
        if node[1] == "source":
            output.append(node[0])
    return output

def get_target_blocks(graph: nx.DiGraph) -> list[int]:
    output = []
    for node in graph.nodes(data="status"):
        if node[1] == "target":
            output.append(node[0])
    return output
