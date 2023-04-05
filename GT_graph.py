from world import *
import matplotlib
matplotlib.use('gtk3agg')
from graph_tool.all import *

# pass the combined world, so the start world with the target config applied to it, with the blocks marked
def reconfig_graph(world: World) -> Graph:
    g = Graph()
    vertices = {}
        

    perimeter = g.new_vertex_property("bool")
    blocks = g.new_vertex_property("bool")
    pos = g.new_vertex_property("vector<float>")
    disp_pos = g.new_vertex_property("vector<float>")
    v_type = g.new_vertex_property("string")
    v_color = g.new_vertex_property("string")

    
    # Add all the vertices and their properties (perimeter/block, pos(ition), disp(lay)_pos, v(ertex)_type, v_color)
    # TODO: Add dealing with the target blocks, really they are perimeter nodes (for now)
    for x in range(len(world.used_cells)):
        for y in range(len(world.used_cells[x])):
            rev_y = list(reversed(range(len(world.used_cells[x]))))[y]
            cell_type = world.used_cells[x][y]
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

    g.vertex_properties["position"] = pos
    g.vertex_properties["disp_position"] = disp_pos
    g.vertex_properties["blocks"] = blocks
    g.vertex_properties["perimeter"] = perimeter
    g.vertex_properties["type"] = v_type
    g.vertex_properties["color"] = v_color


    # Add all the edges: add outgoing edges from all block nodes to all neighbouring nodes in the grid. This implies that
    # perimeter nodes only have incoming edges.
    edge_connected = g.new_edge_property("bool")
    edge_dir = g.new_edge_property("string")
    for v in g.vertices():
        if blocks[v]:
            p = pos[v]
            block = world.configuration.get_block_p(p=p)
            for nb_p, nb_i in [((0,1),'N'), ((1, 1), 'NE'), ((1,0),'E'), ((1,-1), 'SE')\
                                ,((0,-1),'S'), ((-1,-1), 'SW'), ((-1,0),'W'), ((-1,1), 'NW')]:
            #for nb_p, nb_i in [((0,1),'N'), ((1,0),'E'),((0,-1),'S'),((-1,0),'W')]:
                nb = block.neighbours[nb_i]
                if nb:
                    e = g.add_edge(vertices[str(block.p)], vertices[str(nb.p)])
                    if nb_i in ['N', 'E', 'S', 'W']:
                        edge_connected[e] = True
                        edge_dir[e] = nb_i
                    else:
                        edge_connected[e] = False
                        edge_dir[e] = nb_i
                elif f"({block.p[0]+nb_p[0]}, {block.p[1]+nb_p[1]})" in vertices:
                    e = g.add_edge(vertices[str(block.p)], vertices[f"({block.p[0]+nb_p[0]}, {block.p[1]+nb_p[1]})"])
                    if nb_i in ['N', 'E', 'S', 'W']:
                        edge_connected[e] = True
                        edge_dir[e] = nb_i
                    else:
                        edge_connected[e] = False
                        edge_dir[e] = nb_i

    g.edge_properties["orth_neighbours"] = edge_connected


    # Add all the loose and critical blocks. Loose blocks are blocks with only one orthogonal neighbour and critical blocks
    # are the orthogonal neighbours of loose blocks and if that critical block only has one neighbour then that neighbour is
    # also critical. Special case is when there are only three blocks in the configuration, then only the middle block is
    # critical. 
    loose_blocks = g.new_vertex_property("bool")
    crit_blocks = g.new_vertex_property("bool")
    for v in g.iter_vertices():
        nb = get_orth_in_neighbours(g, v, edge_connected)
        if blocks[v] and len(nb) == 1:
            loose_blocks[v] = True
            crit_blocks[v] = False # Makes sure that a block cannot be loose and critical at the same time
            v_color[v] = "yellow"
            crit_blocks[nb[0]] = True
            v_color[nb[0]] = "red"

            if world.num_blocks <= 3:
                continue
            nb_nb = get_orth_in_neighbours(g, nb[0], edge_connected)
            nb_nb.remove(v)
            if len(nb_nb) == 1:
                crit_blocks[nb_nb[0]] = True
                v_color[nb_nb[0]] = "red"

    # Add all the legal moves each block can take
    legal_moves = g.new_edge_property("bool")
    for v in g.iter_vertices():
        if crit_blocks[v]:
            continue
        
        in_nbs = get_orth_in_neighbours(g, v, edge_connected)
        if len(in_nbs) == 4:
            continue

        for in_nb in in_nbs:
            for nbs_out_nb in get_orth_out_neighbours(g, in_nb, edge_connected): # v's neighbour's out neighbour
                if nbs_out_nb == v:
                    continue
                e = g.edge(v, nbs_out_nb)
                if perimeter[nbs_out_nb] and e and legal_moves[e]:
                    legal_moves[e] = False
                elif perimeter[nbs_out_nb] and e:
                    legal_moves[e] = True

                if blocks[nbs_out_nb]:
                    for nbs_out_nb2 in get_orth_out_neighbours(g, nbs_out_nb, edge_connected):
                        e = g.edge(v, nbs_out_nb2)
                        if perimeter[nbs_out_nb2] and e:
                            legal_moves[e] = True
                            debug = ""


    g.edge_properties["legal_moves"] = legal_moves
    


    # Add the chain moves a block can take
    chain_moves = g.new_edge_property('bool')
    for v in g.iter_vertices():
        break
        legal_fr_v = get_legal_edges(g, v, legal_moves=legal_moves)
        if not legal_fr_v:
            continue
        
        # v is the head of the chain, I want to search "behind" any legal moves that v has
        # because if v has legal moves that follow the move v can make then we can make a chain
        for e in legal_fr_v:
            break





    # Color the edges according to the move legality or chain move
    e_color = g.new_edge_property("string")
    for e in g.edges():
        if legal_moves[e]:
            e_color[e] = "green"
        elif chain_moves[e]:
            e_color[e] = "orange"
        else:
            e_color[e] = "grey"
    
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

# Returns the indexes of the edges that are legal from v
def get_legal_edges(g: Graph, v: int, legal_moves: EdgePropertyMap) -> list:
    nb = g.get_all_edges(v) 
    legal_e = []
    for e in nb:
        if legal_moves[e]:
            legal_e.append(e)

    return legal_e
