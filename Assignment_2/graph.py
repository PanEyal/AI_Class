from typing import Tuple, List, Dict

import vertex as v


class Graph(object):

    def __init__(self, graph_dict=None):
        if graph_dict is None:
            graph_dict = {}
        self.graph_dict: Dict[v.Vertex, (v.Vertex, v.Vertex, int)] = graph_dict

    def get_vertices(self) -> List[v.Vertex]:
        return list(self.graph_dict.keys())

    def get_savable_vertices(self) -> List[v.Vertex]:
        return list(filter(lambda ve: ve.people_to_rescue > 0, self.graph_dict.keys()))

    def get_brittle_vertices(self) -> List[v.Vertex]:
        return list(filter(lambda ve: ve.form == v.Form.brittle, self.graph_dict.keys()))

    def get_vertex(self, _id):
        vertex_to_ret = None
        for vertex in self.get_vertices():
            if vertex.id == _id:
                vertex_to_ret = vertex
        return vertex_to_ret

    def vertices_ids(self) -> List[int]:
        id_list = []
        for vertex in self.get_vertices():
            id_list.append(vertex.id)
        return id_list

    def expand(self, vertex: v.Vertex) -> List[Tuple[v.Vertex, int]]:
        return self.graph_dict[vertex]

    def expand_just_vertices(self, vertex: v.Vertex) -> map:
        return map(lambda neighbor_tup: neighbor_tup[0], self.expand(vertex))

    def is_vertex_exists(self, vertex: v.Vertex) -> bool:
        return vertex.id in self.vertices_ids()

    def add_vertex(self, vertex: v.Vertex) -> None:
        if not self.is_vertex_exists(vertex):
            self.graph_dict[vertex] = []

    def add_edge(self, vertex1, vertex2, weight) -> None:
        if vertex2 not in self.expand_just_vertices(vertex1) and vertex1 not in self.expand_just_vertices(vertex2):
            self.graph_dict[vertex1].append((vertex2, weight))
            self.graph_dict[vertex2].append((vertex1, weight))

    def generate_edges(self) -> List[Tuple]:
        edges = []
        for vertex in self.graph_dict:
            for neighbor_tuple in self.graph_dict[vertex]:
                edges.append((vertex, neighbor_tuple[0], neighbor_tuple[1]))
        return edges

    def __str__(self):
        res = "vertices: "
        for k in self.graph_dict:
            res += str(k) + ", "

        res = res[:len(res) - 2]
        res += "\nedges: "
        for edge in self.generate_edges():
            res += "(" + str(edge[0].id) + ", " + str(edge[1].id) + ", " + str(edge[2]) + "), "
        res = res[:len(res) - 2]
        return res
