import copy as cp
from typing import List, Dict

import graph as g
import vertex as v


class State:

    def __init__(self, current_vertices: List[v.Vertex], vertices_saved: Dict[v.Vertex, bool],
                 vertices_broken: Dict[v.Vertex, bool], remaining_plys: int, agent_scores: List[int] = None):
        self.current_vertices: List[v.Vertex] = cp.copy(current_vertices)
        self.vertices_saved: Dict[v.Vertex, bool] = cp.copy(vertices_saved)
        self.vertices_broken: Dict[v.Vertex, bool] = cp.copy(vertices_broken)
        self.agent_scores: List[int] = cp.copy(agent_scores) if agent_scores is not None else [0, 0]
        self.remaining_plys: int = remaining_plys

    def __str__(self):
        s = ''
        for i, vertex in enumerate(self.current_vertices):
            s += f'Agent {i}: vertex - {vertex}, score - {self.agent_scores[i]} '
        for vertex, saved in self.vertices_saved.items():
            s += f'Vertex {vertex.id}: {"saved" if saved else "not saved"} '
        for vertex, broken in self.vertices_broken.items():
            s += f'Vertex {vertex.id}: {"broken" if broken else "not broken"} '
        s += f'Search depth: {self.remaining_plys}'
        return s + '\n'

    def save_current_vertex(self, agent_id: int) -> None:
        if self.current_vertices[agent_id] in self.vertices_saved \
                and not self.vertices_saved[self.current_vertices[agent_id]]:
            self.vertices_saved[self.current_vertices[agent_id]] = True
            self.agent_scores[agent_id] += self.current_vertices[agent_id].people_to_rescue

    def break_current_vertex_if_brittle(self, agent_id: int) -> None:
        if self.current_vertices[agent_id] in self.vertices_broken:
            self.vertices_broken[self.current_vertices[agent_id]] = True

    def get_unsaved_vertices(self) -> List[v.Vertex]:
        unsaved = []
        for vertex, saved in self.vertices_saved.items():
            if not saved:
                unsaved.append(vertex)
        return unsaved

    def num_of_vertices_to_save(self) -> int:
        return len(self.get_unsaved_vertices())

    def is_all_saved(self) -> bool:
        return self.num_of_vertices_to_save() == 0

    def update_vertices_broken(self) -> None:
        for vertex in self.vertices_broken:
            if vertex.form == v.Form.broken:
                self.vertices_broken[vertex] = True
            else:
                self.vertices_broken[vertex] = False

    def update_vertices_saved(self) -> None:
        for vertex in self.vertices_saved:
            if vertex.people_to_rescue == 0:
                self.vertices_saved[vertex] = True
            else:
                self.vertices_saved[vertex] = False

    def does_current_vertex_need_saving(self, agent_id: int) -> bool:
        if self.current_vertices[agent_id] in self.vertices_saved:
            return not self.vertices_saved[self.current_vertices[agent_id]]
        return False

    def is_vertex_broken(self, vertex):
        if vertex in self.vertices_broken:
            return self.vertices_broken[vertex]
        return False

    def clone(self):
        return State(self.current_vertices, self.vertices_saved, self.vertices_broken, self.remaining_plys,
                     self.agent_scores)

    def no_op(self):
        return State(self.current_vertices, self.vertices_saved, self.vertices_broken, self.remaining_plys - 1,
                     self.agent_scores)

    def successor(self, agent_id: int, world: g.Graph) -> List["State"]:
        successors = []
        for vertex, _ in world.expand(self.current_vertices[agent_id]):
            if not self.is_vertex_broken(vertex):
                successor = self.clone()
                successor.current_vertices[agent_id] = vertex
                successor.save_current_vertex(agent_id)
                successor.break_current_vertex_if_brittle(agent_id)
                successor.remaining_plys -= 1
                successors.append(successor)
        successors.append(self.no_op())
        return successors

    def evaluate(self):
        return *self.agent_scores, self.remaining_plys

    def evaluate_alpha_beta(self, agent_id: int):
        return self.agent_scores[agent_id] - self.agent_scores[1 - agent_id]

    def terminal_state(self):
        return self.remaining_plys == 0 \
               or self.is_all_saved()
