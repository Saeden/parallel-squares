import networkx as nx
from world import World
import matplotlib
matplotlib.use('gtk3agg')
import matplotlib.pyplot as plt
import math



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

        self.make_path_graph()
        
        


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
                    block = self.world.get_target_p((x-1, y-1))
                    self.cnct_G.add_node(f"T{block.id}", loc=block.p, color="black", \
                        move_color="black", move_status="None", type="perimeter", status="target")
        

    def add_edges(self): # world: World, G: nx.DiGraph):
        for node in self.cnct_G.nodes(data=True):
            if node[1]["type"] == "block" and (node[1]["status"] == None or node[1]["status"] == "source"):
                block = self.world.configuration.get_block_id(node[0])
                for pos_val, nb_tag in [((0,1),'N'), ((1, 1), 'NE'), ((1,0),'E'), ((1,-1), 'SE')\
                                    ,((0,-1),'S'), ((-1,-1), 'SW'), ((-1,0),'W'), ((-1,1), 'NW')]:
                    nb = block.neighbours[nb_tag]
                    if nb:
                        nb_node = get_node_frm_attr(graph=self.cnct_G, attr="loc", val=nb.p)
                        if nb_tag in ['N', 'E', 'S', 'W']:
                            self.cnct_G.add_edge(node[0], nb_node, edge_connected=True, edge_dir=nb_tag)
                        else:
                            self.cnct_G.add_edge(node[0], nb_node, edge_connected=False, edge_dir=nb_tag)
                        continue
                    nb_node = get_node_frm_attr(graph=self.cnct_G, attr="loc", val=(block.p[0]+pos_val[0], block.p[1]+pos_val[1]))
                    if nb_node:
                        if nb_tag in ['N', 'E', 'S', 'W']:
                            self.cnct_G.add_edge(node[0], nb_node, edge_connected=True, edge_dir=nb_tag)
                        else:
                            self.cnct_G.add_edge(node[0], nb_node, edge_connected=False, edge_dir=nb_tag)
            
            if node[1]["type"] == "perimeter" and node[1]["status"] == "target":
                for pos_val, nb_tag in [((0,1),'N'), ((1, 1), 'NE'), ((1,0),'E'), ((1,-1), 'SE')\
                                    ,((0,-1),'S'), ((-1,-1), 'SW'), ((-1,0),'W'), ((-1,1), 'NW')]:
                    pos = node[1]["loc"]
                    nb_pos = (pos[0]+pos_val[0], pos[1]+pos_val[1])
                    nb_ind = get_node_frm_attr(graph=self.cnct_G, attr="loc", val=nb_pos)
                    if nb_ind:
                        neighbour = self.cnct_G.nodes[nb_ind]
                        if neighbour["type"] == "perimeter" and neighbour["status"] == "target" and nb_tag in ['N', 'E', 'S', 'W']:
                            self.cnct_G.add_edge(node[0], nb_ind, edge_connected=True, edge_dir=nb_tag)
                        elif neighbour["type"] == "perimeter" and neighbour["status"] == "target" and nb_tag not in ['N', 'E', 'S', 'W']:
                            self.cnct_G.add_edge(node[0], nb_ind, edge_connected=False, edge_dir=nb_tag)


        #self.add_perimeter_edges()

    
    def add_perimeter_edges(self ):
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
                        my_in_edges = self.cnct_G.in_edges(node[0])
                        nb_node = get_node_frm_attr(graph=self.path_G, attr="loc", val=(x, y))
                        nb_in_edges = self.cnct_G.in_edges(nb_node)
                        # self.path_G.add_edge(node[0], nb_node, edge_connected=None, edge_dir=nb_i)
                        for my_edge in my_in_edges:
                            for nb_edge in nb_in_edges:
                                if my_edge[0] == nb_edge[0] and self.cnct_G.nodes[my_edge[0]]["type"] == "block":
                                    self.path_G.add_edge(node[0], nb_node, edge_connected=None, edge_dir=nb_i)

 

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

    def make_path_graph(self):
        self.path_G = nx.DiGraph(self.cnct_G)
        for node in self.path_G.nodes(data="type"):
            if node[1] == "block":
                self.rm_blocked_diag_edges(node=node[0])
                self.rm_unreachable_edges(node=node[0])
                self.rm_crit_block_edges(node=node[0])
        
        self.add_perimeter_edges()

        # self.draw_path_graph()
                
    def find_all_paths_max(self) -> list[list]:
        all_paths = []
        for src_block in self.src_blocks:
            paths_to_targets = []
            for target_block in self.trgt_blocks:
                try:
                    path = dijkstra_with_weights(self.path_G, source=src_block, target=target_block)
                    paths_to_targets.append(path)
                except:
                    # print(f"No path between {src_block} and {target_block}. Moving to next pair...")
                    pass
            try:
                all_paths.append(max(paths_to_targets, key=len))
            except:
                # print(f"No path between {src_block} and any target block.")
                pass
                
        if not all_paths:
            self.draw_path_graph()
            raise ValueError("There are no paths from any source block to any target block.")

        return all_paths
        #self.draw_all_paths(all_paths)

    def find_all_paths_min(self) -> list[list]:
        all_paths = []
        for src_block in self.src_blocks:
            paths_to_targets = []
            for target_block in self.trgt_blocks:
                try:
                    path = dijkstra_with_weights(self.path_G, source=src_block, target=target_block)
                    paths_to_targets.append(path)
                except:
                    # print(f"No path between {src_block} and {target_block}. Moving to next pair...")
                    pass
            try:
                all_paths.append(min(paths_to_targets, key=len))
            except:
                # print(f"No path between {src_block} and any target block.")
                pass
                
        if not all_paths:
            self.draw_path_graph()
            raise ValueError("There are no paths from any source block to any target block.")

        return all_paths
     

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
                    if self.path_G.nodes[nb1[0]]["type"] == "perimeter" and self.path_G.nodes[nb2[0]]["type"] == "perimeter":
                        edges_to_rm.append(edge[0:2])
            
            elif edge[2] == 'SE':
                nb1 = [x for (_, x, d) in edges if d == 'S' ]
                nb2 = [x for (_, x, d) in edges if d == 'E' ]
                if nb1 and nb2:
                    if self.path_G.nodes[nb1[0]]["type"] == "block" and self.path_G.nodes[nb2[0]]["type"] == "block":
                        edges_to_rm.append(edge[0:2])
                    if self.path_G.nodes[nb1[0]]["type"] == "perimeter" and self.path_G.nodes[nb2[0]]["type"] == "perimeter":
                        edges_to_rm.append(edge[0:2])
                

            elif edge[2] == 'SW':
                nb1 = [x for (_, x, d) in edges if d == 'S' ]
                nb2 = [x for (_, x, d) in edges if d == 'W' ]
                if nb1 and nb2:
                    if self.path_G.nodes[nb1[0]]["type"] == "block" and self.path_G.nodes[nb2[0]]["type"] == "block":
                        edges_to_rm.append(edge[0:2])
                    if self.path_G.nodes[nb1[0]]["type"] == "perimeter" and self.path_G.nodes[nb2[0]]["type"] == "perimeter":
                        edges_to_rm.append(edge[0:2])
                

            elif edge[2] == 'NW':
                nb1 = [x for (_, x, d) in edges if d == 'N' ]
                nb2 = [x for (_, x, d) in edges if d == 'W' ]
                if nb1 and nb2:
                    if self.path_G.nodes[nb1[0]]["type"] == "block" and self.path_G.nodes[nb2[0]]["type"] == "block":
                        edges_to_rm.append(edge[0:2])
                    if self.path_G.nodes[nb1[0]]["type"] == "perimeter" and self.path_G.nodes[nb2[0]]["type"] == "perimeter":
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
                    
    def rm_crit_block_edges(self, node):
        edges_to_rm = []
        if self.path_G.nodes[node]["move_status"] == "critical":
            for edge in self.path_G.out_edges(node):
                edges_to_rm.append(edge[1])
            for edge in edges_to_rm:
                self.path_G.remove_edge(node, edge)


    def convert_ids_to_pos(self, path: list):
        output = []
        for id in path:
            output.append(self.path_G.nodes[id]["loc"])

        return output


    def is_move_valid(self, move: tuple[tuple[int, int]], node) -> bool:
        def get_nb_frm_dir(node, dir: str) -> bool:
            all_neighbours = self.cnct_G.out_edges(node, data="edge_dir")
            for nb in all_neighbours:
                if type(nb[1]) == int and nb[2] == dir:
                    return True
            return False
        
        dir = (move[1][0]-move[0][0], move[1][1]-move[0][1])
        if dir == (0, 1):    #N
            if get_nb_frm_dir(node, 'E') and get_nb_frm_dir(node, 'NE')\
                or get_nb_frm_dir(node,'W') and get_nb_frm_dir(node, 'NW'):
                return True
        elif dir == (1, 1):  #NE or EN
            if get_nb_frm_dir(node, 'E') and not get_nb_frm_dir(node, 'N')\
                or get_nb_frm_dir(node,'N') and not get_nb_frm_dir(node, 'E'):
                return True
        elif dir == (1, 0):  #E
            if get_nb_frm_dir(node, 'N') and get_nb_frm_dir(node, 'NE')\
                or get_nb_frm_dir(node,'S') and get_nb_frm_dir(node, 'SE'):
                return True
        elif dir == (1, -1): #SE or ES
            if get_nb_frm_dir(node, 'E') and not get_nb_frm_dir(node, 'S')\
                or get_nb_frm_dir(node,'S') and not get_nb_frm_dir(node, 'E'):
                return True
        elif dir == (0, -1): #S
            if get_nb_frm_dir(node, 'E') and get_nb_frm_dir(node, 'SE')\
                or get_nb_frm_dir(node,'W') and get_nb_frm_dir(node, 'SW'):
                return True
        elif dir == (-1, -1):#SW or WS
            if get_nb_frm_dir(node, 'W') and not get_nb_frm_dir(node, 'S')\
                or get_nb_frm_dir(node,'S') and not get_nb_frm_dir(node, 'W'):
                return True
        elif dir == (-1, 0): #W
            if get_nb_frm_dir(node, 'N') and get_nb_frm_dir(node, 'NW')\
                or get_nb_frm_dir(node,'S') and get_nb_frm_dir(node, 'SW'):
                return True
        elif dir == (-1, 1): #NW or WN
            if get_nb_frm_dir(node, 'W') and not get_nb_frm_dir(node, 'N')\
                or get_nb_frm_dir(node,'N') and not get_nb_frm_dir(node, 'W'):
                return True
        else:
            return False

    def draw_normal_colors(self):
        pos = nx.get_node_attributes(self.cnct_G, 'loc')
        node_color = nx.get_node_attributes(self.cnct_G, 'color')
        nx.draw(self.cnct_G, with_labels=True, pos=pos, node_color=node_color.values(), font_color="whitesmoke")
        plt.show()

    def draw_move_colors(self):
        pos = nx.get_node_attributes(self.path_G, 'loc')
        node_color = nx.get_node_attributes(self.path_G, 'move_color')
        nx.draw(self.path_G, with_labels=True, pos=pos, node_color=node_color.values())
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

    def draw_all_paths_and_move_colors(self, paths: list):
        edges = []
        for p in paths:
            path_edges = [(p[n],p[n+1]) for n in range(len(p)-1)]
            edges.append(path_edges)

        pos = nx.get_node_attributes(self.path_G, 'loc')
        node_color = nx.get_node_attributes(self.path_G, 'move_color')
        nx.draw_networkx_nodes(self.path_G,pos=pos, node_color=node_color.values())
        nx.draw_networkx_labels(self.path_G,pos=pos, font_color="white")
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


def dijkstra_with_weights(G: nx.DiGraph, source, target):
    dist = {}
    prev = {}
    queue = []

    for node in G.nodes:
        dist[node] = math.inf
        prev[node] = None
        queue.append(node)

    dist[source] = 0

    while queue:
        min_dist = math.inf
        for q in queue:
            if dist[q] < min_dist:
                n = q
                min_dist = dist[q]
        queue.remove(n)

        if n == target:
            break

        for _, nb in G.out_edges(n):
            new_dist = dist[n] + edge_length(G, n, nb)
            if new_dist < dist[nb]:
                dist[nb] = new_dist
                prev[nb] = n

    path = []
    node = target
    if prev[node] or node == source:
        while node != None:
            path = [node] + path
            node = prev[node]

    return path

def edge_length(G: nx.DiGraph, node1, node2) -> int:
    type1 = G.nodes[node1]["type"]
    status1 = G.nodes[node1]["status"]

    type2 = G.nodes[node2]["type"]
    status2 = G.nodes[node2]["status"]

    if type1 == "perimeter" and type2 == "perimeter" and not status1 and not status2:
        return 3
    else:
        return 1
    

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
