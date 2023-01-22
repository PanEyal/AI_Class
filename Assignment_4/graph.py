from typing import Dict, List, Tuple, Set

from vertex import Vertex


class Graph(object):

    def __init__(self, parsed_file: Dict, max_edge: int):
        self.vertices_dict: Dict[int, Vertex] = {}
        self.s = None
        self.t = None
        self.initialize_graph(parsed_file, max_edge)

    def initialize_graph(self, parsed: Dict, max_edge: int) -> None:
        n: int = parsed['N']
        edges: Dict[int, Tuple[int, int, int]] = parsed['Es']
        blockage_probs: Dict[int, float] = parsed['Bs']
        self.s: int = parsed['S']
        self.t: int = parsed['T']

        for vertex_id in range(1, n + 1):
            self.vertices_dict[vertex_id] = Vertex(vertex_id, blockage_probs.get(vertex_id, 0.))

        for v1, v2, w in edges.values():
            self.vertices_dict[v1].add_neighbor(self.vertices_dict[v2], w)
            self.vertices_dict[v2].add_neighbor(self.vertices_dict[v1], w)

        self.vertices_dict[self.s].add_neighbor(self.vertices_dict[self.t], max_edge)
        self.vertices_dict[self.t].add_neighbor(self.vertices_dict[self.s], max_edge)

    def get_vertices(self) -> List[Vertex]:
        return list(self.vertices_dict.values())

    def get_start_vertex_id(self) -> int:
        return self.s

    def get_target_vertex_id(self) -> int:
        return self.t

    # def get_adjacent_blockable_edges(self,vertex):
    #     blockable_edges = []
    #     for neighbor_tup in self.expand(vertex):
    #         if neighbor_tup[2].blocked_in_prob > 0:
    #             blockable_edges.append(neighbor_tup[2])
    #     return blockable_edges

    # def get_edges(self):
    #     return self.generate_edges()

    def get_brittle_vertices(self) -> List[Vertex]:
        vertices = self.get_vertices()
        return [vertex for vertex in vertices if vertex.is_brittle()]

    def get_vertex(self, _id):
        vertex_to_ret = None
        for vertex in self.get_vertices():
            if vertex.id == _id:
                vertex_to_ret = vertex
        return vertex_to_ret

    # def vertices_ids(self) -> List[int]:
    #     id_list = []
    #     for vertex in self.get_vertices():
    #         id_list.append(vertex.id)
    #     return id_list

    # def expand(self, vertex: v.Vertex) -> List[Tuple[v.Vertex, int]]:
    #     return self.vertices_dict[vertex]

    # def expand_just_vertices(self, vertex: v.Vertex) -> map:
    #     return map(lambda neighbor_tup: neighbor_tup[0], self.expand(vertex))

    # def expand_just_edges(self, vertex):
    #     return list(map(lambda neighbor_tup: neighbor_tup[2], self.expand(vertex)))

    # def get_edge_weight(self, vertex1: v.Vertex, vertex2: v.Vertex) -> int:
    #     neighbors = self.expand(vertex1)
    #     for neighbor in neighbors:
    #         if neighbor[0].id == vertex2.id:
    #             return neighbor[1]

    def vertex_exists(self, vertex: Vertex) -> bool:
        return vertex.id in self.vertices_dict.keys()

    # def edge_exists(self, vertex1: v.Vertex, vertex2: v.Vertex) -> bool:
    #     neighbor_list = self.expand(vertex1)
    #     for neighbor_tup in neighbor_list:
    #         if vertex2 == neighbor_tup[0]:
    #             return True
    #     return False

    # def get_edge(self, vertex1: v.Vertex, vertex2: v.Vertex) -> Edge:
    #     neighbor_list = self.expand(vertex1)
    #     for neighbor_tup in neighbor_list:
    #         if vertex2 == neighbor_tup[0]:
    #             return neighbor_tup[2]
    #     return None

    def add_vertex(self, vertex: Vertex) -> None:
        if not self.vertex_exists(vertex):
            self.vertices_dict[vertex.id] = vertex

    def add_edge(self, vertex1_id: int, vertex2_id: int, weight) -> None:
        vertex1 = self.vertices_dict[vertex1_id]
        vertex2 = self.vertices_dict[vertex2_id]
        if vertex2 not in vertex1.edges and vertex1 not in vertex2.edges:
            vertex1.add_neighbor(vertex2, weight)
            vertex2.add_neighbor(vertex1, weight)

    def generate_edges(self) -> Set[Tuple[int, int, int]]:
        edges = set()
        for vertex in self.vertices_dict.values():
            for neighbor, weight in vertex.get_edges().items():
                edges.add((vertex.id, neighbor.id, weight))
        return edges

    # def copy_graph(self) -> 'Graph':
    #     new_graph = Graph()
    #     for vertex in self.get_vertices():
    #         new_graph.vertices_dict[vertex] = list(self.expand(vertex))
    #     return new_graph

    def __str__(self):
        res = "vertices: "
        for k in self.vertices_dict:
            res += str(k) + ", "

        res = res[:len(res) - 2]
        res += "\nedges: "
        for v1_id, v2_id, w in self.generate_edges():
            res += "(" + str(v1_id) + ", " + str(v2_id) + ", " + str(w) + "), "
        res = res[:len(res) - 2] + "\n"

        res += "Start Vertex: " + str(self.s) + "\n"
        res += "Target Vertex: " + str(self.t)

        return res
