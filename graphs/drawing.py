import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('gtk3agg')


def draw_normal_colors(graph: nx.DiGraph):
    pos = nx.get_node_attributes(graph.cnct_G, 'loc')
    node_color = nx.get_node_attributes(graph.cnct_G, 'color')
    nx.draw(graph.cnct_G, with_labels=True, pos=pos, node_color=node_color.values(), font_color="whitesmoke")
    plt.show()

def draw_move_colors(graph: nx.DiGraph):
    pos = nx.get_node_attributes(graph.path_G, 'loc')
    node_color = nx.get_node_attributes(graph.path_G, 'move_color')
    nx.draw(graph.path_G, with_labels=True, pos=pos, node_color=node_color.values())
    plt.show()

def draw_path_graph(graph: nx.DiGraph):
    pos = nx.get_node_attributes(graph.cnct_G, 'loc')
    node_color = nx.get_node_attributes(graph.path_G, 'color')
    nx.draw(graph.path_G, with_labels=True, pos=pos, node_color=node_color.values())
    plt.show()

def draw_all_paths(graph, paths: list):
    edges = []
    for p in paths:
        path_edges = [(p[n],p[n+1]) for n in range(len(p)-1)]
        edges.append(path_edges)

    pos = nx.get_node_attributes(graph.path_G, 'loc')
    node_color = nx.get_node_attributes(graph.path_G, 'color')
    nx.draw_networkx_nodes(graph.path_G,pos=pos, node_color=node_color.values())
    nx.draw_networkx_labels(graph.path_G,pos=pos, font_color="whitesmoke")
    nx.draw_networkx_edges(graph.path_G, pos=pos, edgelist=graph.path_G.edges, edge_color = "black", width=1)
    colors = ['r', 'b', 'y']
    linewidths = [5,3,2]
    for ctr, edgelist in enumerate(edges):
        nx.draw_networkx_edges(graph.path_G,pos=pos,edgelist=edgelist,edge_color = colors[ctr%3], width=linewidths[ctr%3])
    plt.show()

def draw_all_paths_and_move_colors(graph, paths: list):
    edges = []
    for p in paths:
        path_edges = [(p[n],p[n+1]) for n in range(len(p)-1)]
        edges.append(path_edges)

    pos = nx.get_node_attributes(graph.path_G, 'loc')
    node_color = nx.get_node_attributes(graph.path_G, 'move_color')
    nx.draw_networkx_nodes(graph.path_G,pos=pos, node_color=node_color.values())
    nx.draw_networkx_labels(graph.path_G,pos=pos, font_color="white")
    nx.draw_networkx_edges(graph.path_G, pos=pos, edgelist=graph.path_G.edges, edge_color = "black", width=1)
    colors = ['r', 'b', 'y']
    linewidths = [5,3,2]
    for ctr, edgelist in enumerate(edges):
        nx.draw_networkx_edges(graph.path_G,pos=pos,edgelist=edgelist,edge_color = colors[ctr%3], width=linewidths[ctr%3])
    plt.show() 

def draw_match_labels(self):
    pos = nx.get_node_attributes(self.match_G, 'loc')
    node_color = nx.get_node_attributes(self.match_G, 'color')
    labels = nx.get_node_attributes(self.match_G, 'match_ID')
    nx.draw_networkx_nodes(self.match_G,pos=pos, node_color=node_color.values())
    nx.draw_networkx_labels(self.match_G,pos=pos, labels=labels, font_color="whitesmoke")
    nx.draw_networkx_edges(self.match_G, pos=pos, edgelist=self.match_G.edges, edge_color = "black", width=1)
    plt.show()