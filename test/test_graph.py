import matplotlib
matplotlib.use('gtk3agg')

from graph_tool.all import *

def test():
    g = Graph()
    v1 = g.add_vertex()
    v2 = g.add_vertex()

    e = g.add_edge(v1, v2)

    graph_draw(g, vertex_text=g.vertex_index)

if __name__ == "__main__":
    test()