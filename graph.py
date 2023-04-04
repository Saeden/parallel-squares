from world import *
import matplotlib
matplotlib.use('gtk3agg')
from graph_tool.all import *

def reconfig_graph(start: World, target: Configuration) -> Graph:
    g = Graph()
    vertices = {}
    
    perimeter = g.new_vertex_property("bool")
    blocks = g.new_vertex_property("bool")
    pos = g.new_vertex_property("vector<float>")
    disp_pos = g.new_vertex_property("vector<float>")
    v_type = g.new_vertex_property("string")
    v_color = g.new_vertex_property("string")

    
    
    for x in range(len(start.used_cells)):
        for y in range(len(start.used_cells[x])):
            rev_y = list(reversed(range(len(start.used_cells[x]))))[y]
            cell_type = start.used_cells[x][y]
            if cell_type == -2:
                v = g.add_vertex()
                vertices[f"({x-1}, {y-1})"] = v
                perimeter[v] = True
                blocks[v] = False
                pos[v] = [x-1, y-1]
                disp_pos[v] = [x, rev_y]
                v_type[v] = "P"
                v_color[v] = "grey"
            elif cell_type >= 0:
                v = g.add_vertex()
                vertices[f"({x-1}, {y-1})"] = v
                perimeter[v] = False
                blocks[v] = True
                pos[v] = [x-1, y-1]
                disp_pos[v] = [x, rev_y]
                v_type[v] = "B"
                v_color[v] = "blue"


    edge_connected = g.new_edge_property("bool")
    for v in g.vertices():
        if blocks[v]:
            p = pos[v]
            block = start.configuration.get_block_p(p=p)
            for nb_p, nb_i in [((0,1),'N'), ((1, 1), 'NE'), ((1,0),'E'), ((1,-1), 'SE'),((0,-1),'S'), ((-1,-1), 'SW'), ((-1,0),'W'), ((-1,1), 'NW')]:
            #for nb_p, nb_i in [((0,1),'N'), ((1,0),'E'),((0,-1),'S'),((-1,0),'W')]:
                nb = block.neighbours[nb_i]
                if nb:
                    e = g.add_edge(vertices[str(block.p)], vertices[str(nb.p)])
                    if nb_i in ['N', 'E', 'S', 'W']:
                        edge_connected[e] = True
                    else:
                        edge_connected[e] = False
                elif f"({block.p[0]+nb_p[0]}, {block.p[1]+nb_p[1]})" in vertices:
                    e = g.add_edge(vertices[str(block.p)], vertices[f"({block.p[0]+nb_p[0]}, {block.p[1]+nb_p[1]})"])
                    if nb_i in ['N', 'E', 'S', 'W']:
                        edge_connected[e] = True
                    else:
                        edge_connected[e] = False



    loose_blocks = g.new_vertex_property("bool")
    crit_blocks = g.new_vertex_property("bool")
    for v in g.iter_vertices():
        nb = get_orth_in_neighbours(g, v, edge_connected)
        if blocks[v] and len(nb) == 1:
            loose_blocks[v] = True
            v_color[v] = "yellow"
            crit_blocks[nb[0]] = True
            v_color[nb[0]] = "red"

            nb_nb = get_orth_in_neighbours(g, nb[0], edge_connected)
            nb_nb.remove(v)
            if len(nb_nb) == 1:
                crit_blocks[nb_nb[0]] = True
                v_color[nb_nb[0]] = "red"

    legal_moves = g.new_edge_property("bool")

    for v in g.iter_vertices():
        if crit_blocks[v]:
            continue
        
        for in_nb in g.get_in_neighbors(v):
            for nbs_out_nb in get_orth_out_neighbours(g, in_nb, edge_connected): # v's neighbour's out neighbour
                e = g.edge(v, nbs_out_nb)
                if perimeter[nbs_out_nb] and e:
                    legal_moves[e] = True
                    debug = ""
    
    e_color = g.new_edge_property("string")
    for e in g.edges():
        if legal_moves[e]:
            e_color[e] = "green"
        else:
            e_color[e] = "grey"




        



    





            
        
    g.vertex_properties["position"] = pos
    g.vertex_properties["disp_position"] = disp_pos
    g.vertex_properties["blocks"] = blocks
    g.vertex_properties["perimeter"] = perimeter
    g.vertex_properties["type"] = v_type
    g.vertex_properties["color"] = v_color

    g.edge_properties["orth_neighbours"] = edge_connected
    g.edge_properties["legal_moves"] = legal_moves
    g.edge_properties["color"] = e_color

    return g


# Returns the indexes of the vertices with an outgoing edge to v
# In other words v's incoming neighbours
# This only returns blocks as perimeter nodes never have outgoing edges
def get_orth_in_neighbours(g: Graph, v: int, edge_connected: EdgePropertyMap) -> list:
    nb = g.get_in_neighbours(v) #nb -> neighbours
    orth_nb = []
    for nb_i in nb:
        e = g.edge(nb_i, v)
        if edge_connected[e]:
            orth_nb.append(nb_i)

    return orth_nb

# Returns the indexes of the vertices with an incoming edge to v
# In other words v's outgoing neighbours
# This list contains perimeter and block nodes
def get_orth_out_neighbours(g: Graph, v: int, edge_connected: EdgePropertyMap) -> list:
    nb = g.get_out_neighbours(v) #nb -> neighbours
    orth_nb = []
    for nb_i in nb:
        e = g.edge(v, nb_i)
        if edge_connected[e]:
            orth_nb.append(nb_i)

    return orth_nb