import copy as cp
from typing import Union, List

import vertex as v


class State:

    def __init__(self, current_vertex: v.Vertex, vertices_saved: dict, vertices_broken: dict):
        self.current_vertex = current_vertex
        self.vertices_saved = cp.copy(vertices_saved)
        self.vertices_broken = cp.copy(vertices_broken)

    def __str__(self):
        s = "Current vertex: " + str(self.current_vertex) + "\n{"
        for vertex, saved in self.vertices_saved.items():
            s += vertex.id + ": " + ("saved" if saved else "not saved") + "\n"
        for vertex, broken in self.vertices_broken.items():
            s += vertex.id + ": " + ("broken" if broken else "intact") + "\n"
        return s + "}"

    def save_current_vertex(self) -> None:
        if self.current_vertex in self.vertices_saved:
            self.vertices_saved[self.current_vertex] = True

    def break_current_vertex_if_brittle(self) -> None:
        if self.current_vertex in self.vertices_broken:
            self.vertices_broken[self.current_vertex] = True

    def get_unsaved_vertices(self) -> List[v.Vertex]:
        unsaved = []
        for vertex, saved in self.vertices_saved.items():
            if not saved:
                unsaved.append(vertex)
        return unsaved

    def get_intact_vertices(self) -> List[v.Vertex]:
        intact = []
        for vertex, broken in self.vertices_broken.items():
            if not broken:
                intact.append(vertex)
        return intact

    def num_of_vertices_to_save(self) -> int:
        return len(self.get_unsaved_vertices())

    def update_vertices_saved(self) -> None:
        for vertex in self.vertices_saved:
            if vertex.people_to_rescue == 0:
                self.vertices_saved[vertex] = True
            else:
                self.vertices_saved[vertex] = False

    def update_vertices_broken(self) -> None:
        for vertex in self.vertices_broken:
            if vertex.form == v.Form.broken:
                self.vertices_broken[vertex] = True
            else:
                self.vertices_broken[vertex] = False

    def does_current_vertex_need_saving(self):
        if self.current_vertex in self.vertices_saved:
            return not self.vertices_saved[self.current_vertex]
        return False

    def is_vertex_broken(self, vertex):
        if vertex in self.vertices_broken:
            return self.vertices_broken[vertex]
        return False


class StateWrapper(object):

    def __init__(self, state: State, parent_wrapper: Union['StateWrapper', None], acc_weight: int):
        self.state = state
        self.parent_wrapper = parent_wrapper
        self.acc_weight = acc_weight
