import networkx as nx
import math
import numpy as np

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
    # prev_dir = {}
    queue = []

    for node in G.nodes:
        dist[node] = math.inf
        prev[node] = None
        # prev_dir[node] = None
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
        
        prev_dir: None or str = G.get_edge_data(prev[n], n)
        prev_dir = prev_dir['edge_dir'] if prev_dir else None

        neighbours = legal_neighbours(n, prev_dir, G.out_edges(n, data=True))
        for nb, direction in neighbours:
            new_dist = dist[n] + edge_length(G, n, nb)
            if new_dist < dist[nb]:
                dist[nb] = new_dist
                prev[nb] = n
                # prev_dir[nb] = direction if nb else pass

    path = []
    node = target
    if prev[node] or node == source:
        while node != None:
            path = [node] + path
            node = prev[node]

    return path

def legal_neighbours(node: int, prev_dir: str, neighbour_edges: list):
    if not prev_dir:
        return [(nb, data['edge_dir']) for _, nb, data in neighbour_edges]
    vec_from_prev = dir_to_vec(prev_dir)
    output = []
    for _, nb, data in neighbour_edges:
        vec_to_next = dir_to_vec(data["edge_dir"])
        dot_prod = np.dot(vec_from_prev, vec_to_next)
        if dot_prod > 0:
            output.append((nb, data["edge_dir"]))


def edge_length(G: nx.DiGraph, node1, node2) -> int:
    type1 = G.nodes[node1]["type"]
    status1 = G.nodes[node1]["status"]

    type2 = G.nodes[node2]["type"]
    status2 = G.nodes[node2]["status"]

    if type1 == "perimeter" and type2 == "perimeter":
        return 3
    elif type1 == "block" and type2 == "perimeter":
        return 2
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

def dir_to_vec(direction: str) -> tuple[int]:
    if direction == 'N':
        return (0, 1)
    if direction == 'NE':
        return (1, 1)
    if direction == 'E':
        return (1, 0)
    if direction == 'SE':
        return (1, -1)
    if direction == 'S':
        return (0, -1)
    if direction == 'SW':
        return (-1, -1)
    if direction == 'W':
        return (-1, 0)
    if direction == 'NW':
        return (-1, 1)
    else:
        raise Exception("Invalid direction")
    
def is_move_valid_not_blocked(graph: nx.DiGraph, move: tuple[tuple[int, int]], node: int) -> bool:
        def get_nb_frm_dir(node, dir: str) -> bool:
            all_neighbours = graph.out_edges(node, data="edge_dir")
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
            if get_nb_frm_dir(node, 'E') and not get_nb_frm_dir(node, 'N') and not get_nb_frm_dir(node, 'NE')\
                or get_nb_frm_dir(node,'N') and not get_nb_frm_dir(node, 'E') and not get_nb_frm_dir(node, 'NE'):
                return True
        elif dir == (1, 0):  #E
            if get_nb_frm_dir(node, 'N') and get_nb_frm_dir(node, 'NE')\
                or get_nb_frm_dir(node,'S') and get_nb_frm_dir(node, 'SE'):
                return True
        elif dir == (1, -1): #SE or ES
            if get_nb_frm_dir(node, 'E') and not get_nb_frm_dir(node, 'S') and not get_nb_frm_dir(node, 'SE')\
                or get_nb_frm_dir(node,'S') and not get_nb_frm_dir(node, 'E')and not get_nb_frm_dir(node, 'SE'):
                return True
        elif dir == (0, -1): #S
            if get_nb_frm_dir(node, 'E') and get_nb_frm_dir(node, 'SE')\
                or get_nb_frm_dir(node,'W') and get_nb_frm_dir(node, 'SW'):
                return True
        elif dir == (-1, -1):#SW or WS
            if get_nb_frm_dir(node, 'W') and not get_nb_frm_dir(node, 'S') and not get_nb_frm_dir(node, 'SW')\
                or get_nb_frm_dir(node,'S') and not get_nb_frm_dir(node, 'W') and not get_nb_frm_dir(node, 'SW'):
                return True
        elif dir == (-1, 0): #W
            if get_nb_frm_dir(node, 'N') and get_nb_frm_dir(node, 'NW')\
                or get_nb_frm_dir(node,'S') and get_nb_frm_dir(node, 'SW'):
                return True
        elif dir == (-1, 1): #NW or WN
            if get_nb_frm_dir(node, 'W') and not get_nb_frm_dir(node, 'N') and not get_nb_frm_dir(node, 'NW')\
                or get_nb_frm_dir(node,'N') and not get_nb_frm_dir(node, 'W') and not get_nb_frm_dir(node, 'NW'):
                return True
        else:
            return False
        
def is_move_valid_can_blocked(graph: nx.DiGraph, move: tuple[tuple[int, int]], node: int) -> bool:
        def get_nb_frm_dir(node, dir: str) -> bool:
            all_neighbours = graph.out_edges(node, data="edge_dir")
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
        
def is_pathless_subgraph_connected(graph: nx.DiGraph, world_blocks, path_ids):
    blocks = {block.id:True for block in world_blocks if block}
    for block in path_ids:
        if type(block) == int:
            blocks[block] = False

    def filter_node(node):
        try:
            return blocks[node]
        except:
            return False
    
    def filter_edge(node1, node2):
        return graph[node1][node2].get("edge_connected", True)
    
    pathless_subgraph = nx.subgraph_view(graph, filter_node=filter_node, filter_edge=filter_edge)
    return nx.is_weakly_connected(pathless_subgraph)
    