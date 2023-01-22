from typing import List, Union, Dict


class Vertex(object):
    def __init__(self, _id: int, blockage_prob: float):
        self.id: int = _id
        self.blockage_prob: float = blockage_prob
        self.edges: Dict['Vertex', int] = {}

    def add_neighbor(self, neighbor: 'Vertex', weight: int):
        self.edges[neighbor] = weight

    def get_neighbors(self) -> List['Vertex']:
        return list(self.edges.keys())

    def get_blockage_prob(self) -> float:
        return self.blockage_prob

    def get_edges(self) -> Dict['Vertex', int]:
        return self.edges

    def get_weight(self, neighbor: 'Vertex') -> Union[int, None]:
        return self.edges.get(neighbor)

    def is_brittle(self) -> bool:
        return self.blockage_prob > 0

    def __str__(self):
        return "[Vertex:" + str(self.id) + ", Breakage_Prob:" + str(self.blockage_prob) + "]"

    def __repr__(self):
        return self.__str__()


def vertex_list_to_string(vertices_list: List[Vertex]) -> str:
    s = "["
    for vertex in vertices_list:
        s += f'V{str(vertex.id)}, '
    last_index_of_comma = s.rfind(",")
    if last_index_of_comma != -1:
        s = s[:last_index_of_comma]

    return s + "]"
