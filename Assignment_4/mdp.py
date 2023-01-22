from copy import copy
from typing import List, Dict, Tuple, Union

from graph import Graph
from state import State, Status
from vertex import Vertex


def transition(origin_state: State, dest_state: State) -> float:
    # nothing changed
    if origin_state.same_status(dest_state):
        return 1
    # vertices changed fixed status
    if not origin_state.consistent_with_state(dest_state):
        return 0
    # vertices changed unknown status to fixed status only for dest vertex neighbors
    for brittle_vertex, brittle_status in origin_state.brittle_vertices_status.items():
        if brittle_status == Status.UNKNOWN and dest_state.brittle_vertices_status[brittle_vertex] != Status.UNKNOWN:
            if brittle_vertex not in dest_state.current_vertex.get_neighbors():
                return 0
        elif brittle_status == Status.UNKNOWN and dest_state.brittle_vertices_status[brittle_vertex] == Status.UNKNOWN:
            if brittle_vertex in dest_state.current_vertex.get_neighbors():
                return 0

    return round(origin_state.get_transition_prob(dest_state), 2)


def get_initial_policy(states: List[State], graph: Graph, min_utility: int) \
        -> Dict[State, Union[Tuple[float, Tuple[Vertex, Vertex]], Tuple[float, None]]]:
    policy = {}
    for state in states:
        if graph.get_target_vertex_id() == state.current_vertex.id:
            policy[state] = (0, None)
        else:
            policy[state] = (min_utility, None)
    return policy


def value_iteration(states: List[State], graph: Graph, min_utility: int) \
        -> Dict[State, Union[Tuple[float, Tuple[Vertex, Vertex]], Tuple[float, None]]]:
    policies_prev = get_initial_policy(states, graph, min_utility)
    policies_next = get_initial_policy(states, graph, min_utility)
    change = True
    while change:
        change = False
        for state in states:
            if graph.get_target_vertex_id() == state.current_vertex.id:
                continue
            max_expectation = min_utility
            best_action = None
            for source_vertex, destination_vertex in state.get_actions():
                expectation_for_vertex = 0
                for destination_state in states:
                    destination_state_vertex = destination_state.current_vertex
                    if destination_vertex == destination_state_vertex:
                        prob = transition(state, destination_state)
                        weight = source_vertex.get_weight(destination_vertex)
                        expectation_for_vertex += prob * (-weight + policies_prev[destination_state][0])
                if expectation_for_vertex > max_expectation:
                    max_expectation = expectation_for_vertex
                    best_action = (source_vertex, destination_vertex)
            if max_expectation > policies_prev[state][0]:
                change = True
                policies_next[state] = (round(max_expectation, 2), best_action)
        policies_prev = copy(policies_next)
    return policies_next


def print_policies(policies: Dict[State, Union[Tuple[float, Tuple[Vertex, Vertex]], Tuple[float, None]]]):
    for state, (utility, action) in policies.items():
        if action is None:
            print(f'\n{state}\nUtility: {utility}\nAction: (None)')
        else:
            print(f'\n{state}\nUtility: {utility}\nAction: ({action[0].id} -> {action[1].id})')
