from enum import Enum
from typing import List


class Form(Enum):
    stable = 0
    brittle = 1
    broken = 2


class Vertex(object):
    def __init__(self, id: int, people_to_rescue: int, form: Form):
        self.id = id
        self.people_to_rescue = people_to_rescue
        self.form = form

    def __str__(self):
        return "[V:" + str(self.id) + ", P:" + str(self.people_to_rescue) + ", F:" + str(self.form) + "]"


def vertex_list_to_string(vertices_list: List[Vertex]) -> str:
    s = "[ "
    for vertex in vertices_list:
        s += str(vertex) + ", "
    last_index_of_comma = s.rfind(",")
    if last_index_of_comma != -1:
        s = s[:last_index_of_comma] + s[last_index_of_comma + 1:]

    return s + "]"
