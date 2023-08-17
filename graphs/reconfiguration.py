import networkx as nx
from model.world import World
from graphs.utils import *
from model.block import Block
from graphs.drawing import draw_path_graph, draw_all_paths_and_move_colors


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
        
        

    def add_nodes(self):
        perimeterID = 0
        num_cols = len(self.world.used_cells)
        num_rows = len(self.world.used_cells[0])

        for x in range(num_cols):
            for y in range(num_rows):
                cell_type: int = self.world.used_cells[x][y]
                
                if cell_type == -2: #Perimeter node
                    self.cnct_G.add_node(
                            f"P{perimeterID}", 
                            loc=(x-1, y-1), 
                            color="gray",
                            move_color="gray", 
                            move_status=None, 
                            type="perimeter", 
                            status=None)
                    perimeterID += 1

                elif cell_type >= 0: #Block node
                    block = self.world.configuration.get_block_p((x-1, y-1))
                    if block.status == 'source':
                        self.cnct_G.add_node(
                                block.id, 
                                loc=block.p, 
                                color="green",
                                move_color="blue",
                                move_status="normal",
                                type="block", 
                                status="source")

                    elif block.status == 'block':
                        self.cnct_G.add_node(
                                block.id, 
                                loc=block.p, 
                                color="blue",
                                move_color="blue", 
                                move_status="normal", 
                                type="block", 
                                status=None)
                
                elif cell_type == -3: #Target node
                    block = self.world.get_target_p((x-1, y-1))
                    self.cnct_G.add_node(
                            f"T{block.id}", 
                            loc=block.p, 
                            color="black", 
                            move_color="black", 
                            move_status="None", 
                            type="perimeter", 
                            status="target")
        

    def add_edges(self):
        for node in self.cnct_G.nodes(data=True):
            node_type = node[1]["type"]
            node_status = node[1]["status"]

            if node_type == "block" and (node_status == None or node_status == "source"):
                self.add_block_neighbours(node)

            elif node_type == "perimeter":
                self.add_perimeter_neighbours(node)

 
    def add_block_neighbours(self, node):
        nb_xy_diff = [(0,1),(1, 1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1)]
        nb_tags = ['N','NE','E','SE', 'S','SW', 'W', 'NW']
        block: Block = self.world.configuration.get_block_id(node[0])

        for tag_index, pos_val in enumerate(nb_xy_diff):
            nb_tag = nb_tags[tag_index]

            nb: Block or None = block.neighbours[nb_tag]
            if nb and nb_tag in ['N', 'E', 'S', 'W']:
                nb_node = get_node_frm_attr(graph=self.cnct_G, attr="loc", val=nb.p)
                self.cnct_G.add_edge(node[0], nb_node, edge_connected=True, edge_dir=nb_tag)
            elif nb and nb_tag not in ['N', 'E', 'S', 'W']:
                nb_node = get_node_frm_attr(graph=self.cnct_G, attr="loc", val=nb.p)
                self.cnct_G.add_edge(node[0], nb_node, edge_connected=False, edge_dir=nb_tag)

            nb_node = get_node_frm_attr(graph=self.cnct_G, attr="loc", val=(block.p[0]+pos_val[0], block.p[1]+pos_val[1]))
            if nb_node and nb_tag in ['N', 'E', 'S', 'W']:
                self.cnct_G.add_edge(node[0], nb_node, edge_connected=True, edge_dir=nb_tag)
            elif nb_node and nb_tag not in ['N', 'E', 'S', 'W']:
                self.cnct_G.add_edge(node[0], nb_node, edge_connected=False, edge_dir=nb_tag)

    
    def add_perimeter_neighbours(self, node):
        nb_xy_diff = [(0,1),(1, 1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1)]
        nb_tags = ['N','NE','E','SE', 'S','SW', 'W', 'NW']
        for tag_index, nb_pos_diff in enumerate(nb_xy_diff):
            nb_tag = nb_tags[tag_index]
            node_pos = node[1]["loc"]
            nb_x = nb_pos_diff[0] + node_pos[0]
            nb_y = nb_pos_diff[1] + node_pos[1]
            
            num_cols = len(self.world.used_cells)
            num_rows = len(self.world.used_cells[0])
            if nb_x < -1 or nb_y < - 1 or nb_x > num_cols - 2 or nb_y >= num_rows - 2:
                continue

            nb_type = self.world.used_cells[nb_x+1][nb_y+1]
            if nb_type != -1:
                nb_node = get_node_frm_attr(graph=self.cnct_G, attr="loc", val=(nb_x, nb_y))
                self.cnct_G.add_edge(node[0], nb_node, edge_connected=None, edge_dir=nb_tag)
                          

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
                
    def rm_illegal_block_moves(self, node):
        out_edges = self.cnct_G.out_edges(nbunch=node)
        edges_to_rm = []
        node_pos = self.cnct_G.nodes[node]["loc"]
        for edge in out_edges:
            nb_pos = self.cnct_G.nodes[edge[1]]["loc"]
            if not is_move_valid_can_blocked(self.cnct_G, move=(node_pos, nb_pos), node=node):
                edges_to_rm.append(edge)

        for edge in edges_to_rm:
            try:
                self.path_G.remove_edge(edge[0], edge[1])
            except:
                pass
                #print(f"Apparently edge {edge} is not in the graph, even though that should be impossible....")


    def rm_crit_block_edges(self, node):
        edges_to_rm = []
        if self.path_G.nodes[node]["move_status"] == "critical":
            for edge in self.path_G.out_edges(node):
                edges_to_rm.append(edge[1])
            for edge in edges_to_rm:
                self.path_G.remove_edge(node, edge)

    def rm_invalid_perim_edges(self, node):
        edges = self.cnct_G.out_edges(nbunch=node)
        node_pos = self.cnct_G.nodes[node]["loc"]
        edges_to_rm = []
        for edge in edges:
            nb_pos = self.cnct_G.nodes[edge[1]]["loc"]
            if not is_move_valid_can_blocked(self.cnct_G, move=(node_pos, nb_pos), node=node):
                edges_to_rm.append(edge)

        for edge in edges_to_rm:
            try:
                self.path_G.remove_edge(edge[0], edge[1])
            except:
                pass
                # print(f"Apparently edge {edge} is not in the graph, even though that should be impossible....")

    def rm_split_pair_edge(self):
        edges_to_rm = []
        
        for edge in self.path_G.edges:
            def filter_node(node):
                if node in edge:
                    return False
                elif type(node) == int:
                    return True
                else:
                    return False
        
            def filter_edge(node1, node2):
                return self.cnct_G[node1][node2].get("edge_connected", True)
            
            subgraph = nx.subgraph_view(self.cnct_G, filter_node=filter_node, filter_edge=filter_edge)
            if not nx.is_weakly_connected(subgraph):
                edges_to_rm.append(edge)

        for edge in edges_to_rm:
            try:
                self.path_G.remove_edge(edge[0], edge[1])
            except:
                pass
                # print(f"Apparently edge {edge} is not in the graph, even though that should be impossible....")

    def rm_created_cut_block_edge(self):
        edges_to_rm = []
        cut_blocks = list(nx.articulation_points(self.path_G.to_undirected()))
        for edge in self.path_G.edges:
            if type(edge[0]) != int:
                continue

            def filter_node(node):
                if node == edge[1]:
                    return True
                elif node == edge[0]:
                    return False
                elif type(node) == int:
                    return True
                else:
                    return False
        
            def filter_edge(node1, node2):
                return self.cnct_G[node1][node2].get("edge_connected", True)
            
            subgraph = nx.subgraph_view(self.cnct_G, filter_node=filter_node, filter_edge=filter_edge)
            cut_blocks_after_move = list(nx.articulation_points(subgraph.to_undirected()))
            if len(cut_blocks_after_move) > len(cut_blocks):
                edges_to_rm.append(edge)

        for edge in edges_to_rm:
            try:
                self.path_G.remove_edge(edge[0], edge[1])
            except:
                pass
                # print(f"Apparently edge {edge} is not in the graph, even though that should be impossible....")

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
                # self.rm_unreachable_edges(node=node[0])
                self.rm_crit_block_edges(node=node[0])
                self.rm_illegal_block_moves(node=node[0])
            if node[1] == "perimeter":
                self.rm_invalid_perim_edges(node=node[0])

        self.rm_split_pair_edge()
        # self.rm_created_cut_block_edge()


                
    def find_all_paths_max(self, strictly_connected: bool) -> list[list]:
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
                sorted_paths_to_targets = sorted(paths_to_targets, key=lambda lst: sum(isinstance(item, int) for item in lst), reverse=True)
                if strictly_connected:
                    while not is_pathless_subgraph_connected(self.cnct_G, self.world.configuration.blocks, sorted_paths_to_targets[0]):
                        del sorted_paths_to_targets[0]
                all_paths.append(sorted_paths_to_targets[0])
            except:
                # print(f"No path between {src_block} and any target block.")
                pass
                
        if not all_paths:
            # draw_path_graph(graph=self)
            draw_all_paths_and_move_colors(graph=self, paths=[])
            raise ValueError("There are no max paths from any source block to any target block.")

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
            #self.draw_path_graph()
            pass
            # raise ValueError("There are no paths from any source block to any target block.")

        return all_paths
     


    def convert_ids_to_pos(self, path: list):
        output = []
        for id in path:
            output.append(self.path_G.nodes[id]["loc"])

        return output


