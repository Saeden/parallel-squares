import networkx as nx
from world import World
import matplotlib
matplotlib.use('gtk3agg')
import matplotlib.pyplot as plt
from itertools import islice



class ReconGraph:
    def __init__(self, world: World) -> None:
        self.cnct_G = nx.DiGraph()
        self.path_G = None
        self.world = world

        self.add_nodes()
        self.add_edges()
        self.mark_blocks()

        self.src_blocks = get_source_blocks(graph=self.cnct_G)
        self.trgt_blocks = get_target_blocks(graph=self.cnct_G)
        


    def add_nodes(self): # world: World, G: nx.DiGraph):
        perimeterID = 0
        for x in range(len(self.world.used_cells)):
            for y in range(len(self.world.used_cells[x])):
                cell_type = self.world.used_cells[x][y]
                if cell_type == -2:
                    self.cnct_G.add_node(f"P{perimeterID}", loc=(x-1, y-1), color="gray", \
                        move_color="gray", move_status=None, type="perimeter", status=None)
                    perimeterID += 1
                elif cell_type >= 0:
                    block = self.world.configuration.get_block_p((x-1, y-1))
                    if block.status == 'source':
                        self.cnct_G.add_node(block.id, loc=block.p, color="green", \
                            move_color="blue", move_status="normal", type="block", status="source")

                    elif block.status == 'block':
                        self.cnct_G.add_node(block.id, loc=block.p, color="blue", \
                            move_color="blue", move_status="normal", type="block", status=None)
                elif cell_type == -3:
                    block = self.world.configuration.get_block_p((x-1, y-1))
                    self.cnct_G.add_node(block.id, loc=block.p, color="black", \
                        move_color="black", move_status="None", type="block", status="target")

    def add_edges(self): # world: World, G: nx.DiGraph):
        for node in self.cnct_G.nodes(data=True):
            if node[1]["type"] == "block" and (node[1]["status"] == None or node[1]["status"] == "source"):
                block = self.world.configuration.get_block_id(node[0])
                for nb_p, nb_i in [((0,1),'N'), ((1, 1), 'NE'), ((1,0),'E'), ((1,-1), 'SE')\
                                    ,((0,-1),'S'), ((-1,-1), 'SW'), ((-1,0),'W'), ((-1,1), 'NW')]:
                    nb = block.neighbours[nb_i]
                    if nb:
                        nb_node = get_node_frm_attr(graph=self.cnct_G, attr="loc", val=nb.p)
                        if nb_i in ['N', 'E', 'S', 'W']:
                            self.cnct_G.add_edge(node[0], nb_node, edge_connected=True, edge_dir=nb_i)
                        else:
                            self.cnct_G.add_edge(node[0], nb_node, edge_connected=False, edge_dir=nb_i)
                        continue
                    nb_node = get_node_frm_attr(graph=self.cnct_G, attr="loc", val=(block.p[0]+nb_p[0], block.p[1]+nb_p[1]))
                    if nb_node:
                        if nb_i in ['N', 'E', 'S', 'W']:
                            self.cnct_G.add_edge(node[0], nb_node, edge_connected=True, edge_dir=nb_i)
                        else:
                            self.cnct_G.add_edge(node[0], nb_node, edge_connected=False, edge_dir=nb_i)

        #self.add_perimeter_edges()

    
    def add_perimeter_edges(self, path=False):
        if path:
            for node in self.path_G.nodes(data=True):
                if node[1]["type"] == "perimeter":
                    for nb_p, nb_i in [((0,1),'N'), ((1, 1), 'NE'), ((1,0),'E'), ((1,-1), 'SE')\
                                        ,((0,-1),'S'), ((-1,-1), 'SW'), ((-1,0),'W'), ((-1,1), 'NW')]:
                        p = node[1]["loc"]
                        x = nb_p[0] + p[0]
                        y = nb_p[1] + p[1]
                        if x < -1 or y < - 1 or x > len(self.world.used_cells) - 2 or y >= len(self.world.used_cells[0]) - 2:
                            continue
                        if self.world.used_cells[x+1][y+1] != -1:
                            nb_node = get_node_frm_attr(graph=self.path_G, attr="loc", val=(x, y))
                            self.path_G.add_edge(node[0], nb_node, edge_connected=None, edge_dir=nb_i)
        
        else:
            for node in self.cnct_G.nodes(data=True):
                if node[1]["type"] == "perimeter":
                    for nb_p, nb_i in [((0,1),'N'), ((1, 1), 'NE'), ((1,0),'E'), ((1,-1), 'SE')\
                                        ,((0,-1),'S'), ((-1,-1), 'SW'), ((-1,0),'W'), ((-1,1), 'NW')]:
                        p = node[1]["loc"]
                        x = nb_p[0] + p[0]
                        y = nb_p[1] + p[1]
                        if x < -1 or y < - 1 or x > len(self.world.used_cells) - 2 or y >= len(self.world.used_cells[0]) - 2:
                            continue
                        if self.world.used_cells[x+1][y+1] != -1:
                            nb_node = get_node_frm_attr(graph=self.cnct_G, attr="loc", val=(x, y))
                            self.cnct_G.add_edge(node[0], nb_node, edge_connected=None, edge_dir=nb_i)

        

    def mark_blocks(self): # G: nx.DiGraph):
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

    def make_path_graph(self):
        self.path_G = nx.DiGraph(self.cnct_G)
        for node in self.path_G.nodes(data="type"):
            if node[1] == "block":
                self.rm_blocked_diag_edges(node=node[0])
                self.rm_unreachable_edges(node=node[0])
        
        self.add_perimeter_edges(path=True)

        # self.draw_path_graph()
                

    def finds_all_paths(self) -> list[list]:
        self.make_path_graph()

        all_paths = []
        for src_block in self.src_blocks:
            path_to_targets = []
            for target_block in self.trgt_blocks:
                try:
                    # paths = list(nx.shortest_simple_paths(self.path_G, src_block, target_block))
                    # path_to_targets.append(paths[0])
                    path = nx.shortest_path(self.path_G, src_block, target_block)
                    path_to_targets.append(path)
                except:
                    print(f"No path between {src_block} and {target_block}. Moving to next pair...")
            if path_to_targets:
                all_paths.append(min(path_to_targets, key=len))
            else:
                raise ValueError("There are no paths from {src_block} to any target block.")

        return all_paths
        #self.draw_all_paths(all_paths)

    def rm_blocked_diag_edges(self, node):
        edges = self.path_G.out_edges(nbunch=node, data="edge_dir")
        edges_to_rm = []
        for edge in edges:
            if edge[2] == 'NE':
                nb1 = [x for (_, x, d) in edges if d == 'N' ]
                nb2 = [x for (_, x, d) in edges if d == 'E' ]
                if nb1 and nb2:
                    if self.path_G.nodes[nb1[0]]["type"] == "block" and self.path_G.nodes[nb2[0]]["type"] == "block":
                        edges_to_rm.append(edge[0:2])
            
            elif edge[2] == 'SE':
                nb1 = [x for (_, x, d) in edges if d == 'S' ]
                nb2 = [x for (_, x, d) in edges if d == 'E' ]
                if nb1 and nb2:
                    if self.path_G.nodes[nb1[0]]["type"] == "block" and self.path_G.nodes[nb2[0]]["type"] == "block":
                        edges_to_rm.append(edge[0:2])

            elif edge[2] == 'SW':
                nb1 = [x for (_, x, d) in edges if d == 'S' ]
                nb2 = [x for (_, x, d) in edges if d == 'W' ]
                if nb1 and nb2:
                    if self.path_G.nodes[nb1[0]]["type"] == "block" and self.path_G.nodes[nb2[0]]["type"] == "block":
                        edges_to_rm.append(edge[0:2])
            
            elif edge[2] == 'NW':
                nb1 = [x for (_, x, d) in edges if d == 'N' ]
                nb2 = [x for (_, x, d) in edges if d == 'W' ]
                if nb1 and nb2:
                    if self.path_G.nodes[nb1[0]]["type"] == "block" and self.path_G.nodes[nb2[0]]["type"] == "block":
                        edges_to_rm.append(edge[0:2])

        for edge in edges_to_rm:
            self.path_G.remove_edge(edge[0], edge[1])
                
    def rm_unreachable_edges(self, node):
        edges = self.cnct_G.out_edges(nbunch=node, data="edge_dir")
        edges_to_rm = []
        for edge in edges:
            if self.cnct_G.nodes[edge[1]]["type"] == "perimeter" and edge[2] in ['N', 'E', 'S', 'W']:
                found = False
                for my_nb in get_orth_out_neighbours(self.cnct_G, node):
                    for my_nbs_nb in get_orth_out_neighbours(self.cnct_G, my_nb):
                        if my_nbs_nb == node:
                            continue
                        for my_nbs_nbs_nb in get_orth_out_neighbours(self.cnct_G,my_nbs_nb):
                            if my_nbs_nbs_nb == node or my_nbs_nbs_nb == my_nb:
                                continue
                            try:
                                self.cnct_G.edges[node, my_nbs_nbs_nb]
                            except:
                                continue
                            if (node, my_nbs_nbs_nb) == edge[0:2]:
                                found = True
                                break
                        if found:
                            break
                    if found:
                        break
                
                if not found:
                    edges_to_rm.append(edge)
                    
                
            elif self.cnct_G.nodes[edge[1]]["type"] == "perimeter" and edge[2] in ['NE', 'SE', 'SW', 'NW']:
                found = False
                for my_nb in get_orth_out_neighbours(self.cnct_G, node):
                    for my_nbs_nb in get_orth_out_neighbours(self.cnct_G, my_nb):
                        if my_nbs_nb == node:
                            continue
                        try:
                            self.cnct_G.edges[node, my_nbs_nb]
                        except:
                            continue
                        if (node, my_nbs_nb) == edge[0:2]:
                            found = True
                            break
                    if found:
                        break
                
                if not found:
                    edges_to_rm.append(edge)

            elif self.cnct_G.nodes[edge[1]]["type"] == "block" and self.cnct_G.nodes[edge[1]]["status"] == "target"\
                                                                and edge[2] in ['N', 'E', 'S', 'W']:
                found = False
                for my_nb in get_orth_out_neighbours(self.cnct_G, node):
                    for my_nbs_nb in get_orth_out_neighbours(self.cnct_G, my_nb):
                        if my_nbs_nb == node:
                            continue
                        for my_nbs_nbs_nb in get_orth_out_neighbours(self.cnct_G,my_nbs_nb):
                            if my_nbs_nbs_nb == node or my_nbs_nbs_nb == my_nb:
                                continue
                            try:
                                self.cnct_G.edges[node, my_nbs_nbs_nb]
                            except:
                                continue
                            if (node, my_nbs_nbs_nb) == edge[0:2]:
                                found = True
                                break
                        if found:
                            break
                    if found:
                        break
                
                if not found:
                    edges_to_rm.append(edge)
                    
            elif self.cnct_G.nodes[edge[1]]["type"] == "block" and self.cnct_G.nodes[edge[1]]["status"] == "target"\
                                                                and edge[2] in ['NE', 'SE', 'SW', 'NW']:
                found = False
                for my_nb in get_orth_out_neighbours(self.cnct_G, node):
                    for my_nbs_nb in get_orth_out_neighbours(self.cnct_G, my_nb):
                        if my_nbs_nb == node:
                            continue
                        try:
                            self.cnct_G.edges[node, my_nbs_nb]
                        except:
                            continue
                        if (node, my_nbs_nb) == edge[0:2]:
                            found = True
                            break
                    if found:
                        break
                
                if not found:
                    edges_to_rm.append(edge)

        for edge in edges_to_rm:
            try:
                self.path_G.remove_edge(edge[0], edge[1])
            except:
                print(f"Apparently edge {edge} is not in the graph, even though that should be impossible....")
                    
            
            
    def rm_unreachable_edges_old(self, node):
        # Check the neighbours of each of my (node) neighbours
        # If my neighbour is a block, its neighbour must be empty/perimeter
        # and I must have a direct connection to that perimeter node in the
        # adjacency graph
        for edge in get_orth_out_neighbours(self.path_G, node):
            # edge[0] is me, edge[1] is one of my neighbours
            if self.cnct_G.nodes[edge[1]]["type"] == "block" and self.cnct_G.nodes[edge[1]]["status"] != "target":
                for edge2 in get_orth_out_neighbours(self.path_G, edge[1]):
                    # edge2[0] is my neighbour and edge2[1] is my neighbours neighbour
                    if edge2[1] == node:
                        continue
                    



    def convert_ids_to_pos(self, path: list):
        output = []
        for id in path:
            output.append(self.path_G.nodes[id]["loc"])

        return output


    def draw_normal_colors(self):
        pos = nx.get_node_attributes(self.cnct_G, 'loc')
        node_color = nx.get_node_attributes(self.cnct_G, 'color')
        nx.draw(self.cnct_G, with_labels=True, pos=pos, node_color=node_color.values(), font_color="whitesmoke")
        plt.show()

    def draw_move_colors(self):
        pos = nx.get_node_attributes(self.cnct_G, 'loc')
        node_color = nx.get_node_attributes(self.cnct_G, 'move_color')
        nx.draw(self.cnct_G, with_labels=True, pos=pos, node_color=node_color.values())
        plt.show()

    def draw_path_graph(self):
        pos = nx.get_node_attributes(self.cnct_G, 'loc')
        node_color = nx.get_node_attributes(self.path_G, 'color')
        nx.draw(self.path_G, with_labels=True, pos=pos, node_color=node_color.values())
        plt.show()

    def draw_all_paths(self, paths: list):
        edges = []
        for p in paths:
            path_edges = [(p[n],p[n+1]) for n in range(len(p)-1)]
            edges.append(path_edges)

        pos = nx.get_node_attributes(self.path_G, 'loc')
        node_color = nx.get_node_attributes(self.path_G, 'color')
        nx.draw_networkx_nodes(self.path_G,pos=pos, node_color=node_color.values())
        nx.draw_networkx_labels(self.path_G,pos=pos, font_color="whitesmoke")
        nx.draw_networkx_edges(self.path_G, pos=pos, edgelist=self.path_G.edges, edge_color = "black", width=1)
        colors = ['r', 'b', 'y']
        linewidths = [5,3,2]
        for ctr, edgelist in enumerate(edges):
            nx.draw_networkx_edges(self.path_G,pos=pos,edgelist=edgelist,edge_color = colors[ctr%3], width=linewidths[ctr%3])
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

def get_orth_out_neighbours(graph: nx.DiGraph, node) -> list:
    all_neighbours = graph.out_edges(node, data="edge_dir")
    output = []
    for nb in all_neighbours:
        if nb[2] in ['N', 'E', 'S', 'W']:
            output.append(nb[1])
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


