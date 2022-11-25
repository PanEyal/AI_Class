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

    def generate_edges(self):
        edges = []
        for vertex in self.graph_dict:
            for neighbor_tuple in self.graph_dict[vertex]:
                edges.append((vertex, neighbor_tuple[0], neighbor_tuple[1]))
        return edges

    def __str__(self):
        res = "vertices: "
        for k in self.graph_dict:
            res += str(k) + ", "

        res = res[:len(res)-2]
        res += "\nedges: "
        for edge in self.generate_edges():
            res += "(" + str(edge[0].id) + ", " + str(edge[1].id) + ", " + str(edge[2]) + "), "
        res = res[:len(res)-2]
        return res

