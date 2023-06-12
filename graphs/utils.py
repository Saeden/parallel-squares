import networkx as nx
import math

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
