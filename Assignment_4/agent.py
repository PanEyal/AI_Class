from copy import copy
from typing import Dict, Union, Tuple, List

from graph import Graph
from state import State, Status
from vertex import Vertex


def find_target(graph: Graph,
                hidden_brittle_vertices_status: [Vertex, Status],
                policies: Dict[State, Union[Tuple[float, Tuple[Vertex, Vertex]], Tuple[float, None]]],
                states: List[State],
                starting_vertex_id: int) -> None:
    current_state = get_starting_state(states, hidden_brittle_vertices_status, graph.get_vertex(starting_vertex_id))
    while not in_target_state(current_state, graph):
        optimal_action = policies[current_state][1]
        if optimal_action is None:
            print('No optimal action')
            break
        print(f'({optimal_action[0].id} -> {optimal_action[1].id}), ')
        known_vertices_status = copy(current_state.brittle_vertices_status)
        destination_vertex = optimal_action[1]
        for neighbor in destination_vertex.get_neighbors():
            if neighbor in hidden_brittle_vertices_status.keys():
                known_vertices_status[neighbor] = hidden_brittle_vertices_status[neighbor]
        current_state = get_state_from_states(states, destination_vertex.id, known_vertices_status)


def in_target_state(state: State, graph: Graph) -> bool:
    return state.current_vertex.id == graph.get_target_vertex_id()


def get_starting_state(states: List[State], hidden_brittle_vertices_status: Dict[Vertex, Status],
                       starting_vertex: Vertex) -> State:
    required_brittle_vertices_status = {}
    for vertex in hidden_brittle_vertices_status.keys():
        if vertex in starting_vertex.get_neighbors():
            required_brittle_vertices_status[vertex] = hidden_brittle_vertices_status[vertex]
        else:
            required_brittle_vertices_status[vertex] = Status.UNKNOWN
    return get_state_from_states(states, starting_vertex.id, required_brittle_vertices_status)


def get_state_from_states(states: List[State], required_vertex_id: int,
                          required_brittle_vertices_status: Dict[Vertex, Status]) -> State:
    for state in states:
        if state.current_vertex.id == required_vertex_id \
                and state.brittle_vertices_status == required_brittle_vertices_status:
            return state

    raise Exception('state not found')
