import vertex as v

class Graph(object):

    def __init__(self, graph_dict=None):
        if graph_dict is None:
            graph_dict = {}
        self.graph_dict = graph_dict

    def get_vertices(self):
        return list(self.graph_dict.keys())

    def vertices_ids(self):
        id_list = []
        for vertex in self.get_vertices():
            id_list.append(vertex.id)
        return id_list

    def expand(self, vertex):
        return self.graph_dict[vertex]

    def expand_just_vertices(self, vertex):
        return map(lambda neighbor_tup: neighbor_tup[0], self.expand(vertex))

    def vertex_exists(self, vertex):
        return vertex.id in self.vertices_ids()

    def add_vertex(self, vertex):
        if not self.vertex_exists(vertex):
            self.graph_dict[vertex] = []

    def add_edge(self, vertex1, vertex2, weight):
        if vertex2 not in self.expand_just_vertices(vertex1) and vertex1 not in self.expand_just_vertices(vertex2):
            self.graph_dict[vertex1].append((vertex2, weight))
            self.graph_dict[vertex2].append((vertex1, weight))
