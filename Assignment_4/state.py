import itertools
from copy import copy
from enum import Enum
from typing import List, Dict, Tuple

from graph import Graph
from vertex import Vertex


class Status(Enum):
    UNKNOWN = -1
    UNBLOCKED = 0
    BLOCKED = 1


class State:

    def __init__(self, current_vertex: Vertex, brittle_vertices_status: Dict[Vertex, Status]):
        self.current_vertex: Vertex = current_vertex
        self.brittle_vertices_status: Dict[Vertex, Status] = copy(brittle_vertices_status)

    def same_status(self, other) -> bool:
        return self.brittle_vertices_status == other.brittle_vertices_status

    def get_actions(self) -> List[Tuple[Vertex, Vertex]]:
        legal_actions = []
        for neighbor in self.current_vertex.get_neighbors():
            status = self.get_brittle_vertex_status(neighbor)
            if status is Status.UNKNOWN:
                raise Exception('neighbor vertex state unknown, it should be known')
            if status is Status.UNBLOCKED:
                legal_actions.append((self.current_vertex, neighbor))
        return legal_actions

    def get_brittle_vertex_status(self, vertex: Vertex) -> Status:
        status = self.brittle_vertices_status.get(vertex)
        if status is None:
            return Status.UNBLOCKED
        return status

    def get_brittle_vertices_status(self) -> Dict[Vertex, Status]:
        return self.brittle_vertices_status

    def consistent_with_state(self, s: 'State') -> bool:
        for vertex, status in self.brittle_vertices_status.items():
            if status is Status.UNKNOWN:
                continue
            elif s.brittle_vertices_status[vertex] != status:
                return False
        return True

    def get_transition_prob(self, s: 'State') -> float:
        prob = 1.
        for vertex, status in self.brittle_vertices_status.items():
            if status is Status.UNKNOWN:
                if s.brittle_vertices_status[vertex] is Status.UNKNOWN:
                    continue
                elif s.brittle_vertices_status[vertex] is Status.BLOCKED:
                    prob *= vertex.get_blockage_prob()
                elif s.brittle_vertices_status[vertex] is Status.UNBLOCKED:
                    prob *= (1 - vertex.get_blockage_prob())

        return prob

    def __str__(self):
        s = 'STATE: '
        s += '{Location: ' + str(self.current_vertex.id)
        for vertex in self.brittle_vertices_status:
            s += ', V' + str(vertex.id) + ': ' + str(self.brittle_vertices_status[vertex].name)
        return s + '}'


def generate_states(graph: Graph) -> List[State]:
    states = []
    vertices = graph.get_vertices()
    blockable_vertices = list(filter(lambda ver: ver.is_brittle(), vertices))
    possibilities_for_brittle_vertices = itertools.product([Status.UNKNOWN, Status.UNBLOCKED, Status.BLOCKED],
                                                           repeat=len(blockable_vertices))
    for possibility in possibilities_for_brittle_vertices:
        vertices_status = dict(zip(blockable_vertices, possibility))
        for vertex in vertices:
            states.append(State(vertex, vertices_status))
    return filter_bad_states(states)


def filter_bad_states(states: List[State]) -> List[State]:
    filtered_states = []
    for state in states:
        blockable_neighbors = list(filter(lambda ver: ver.is_brittle(), state.current_vertex.get_neighbors()))
        bad_state = False
        for neighbor in blockable_neighbors:
            if state.get_brittle_vertex_status(neighbor) is Status.UNKNOWN:
                bad_state = True
                break
        if state.get_brittle_vertex_status(state.current_vertex) is not Status.UNBLOCKED:
            bad_state = True
        if not bad_state:
            filtered_states.append(state)
    return filtered_states

