import copy as c
from typing import Callable, Dict, List

import graph as g
import priority_queue as pq
import state as s
import vertex as v


def generate_sequence(get_edge_weight: Callable, state_wrapper: s.StateWrapper) -> List[v.Vertex]:
    if state_wrapper.parent_wrapper is None:
        return []
    edge_weight = get_edge_weight(state_wrapper.parent_wrapper.state.current_vertex, state_wrapper.state.current_vertex)
    current_move = []
    for i in range(edge_weight):
        current_move.append(state_wrapper.state.current_vertex)
    current_sequence = generate_sequence(get_edge_weight, state_wrapper.parent_wrapper)
    current_sequence.extend(current_move)
    return current_sequence


def get_g(state_wrapper: s.StateWrapper) -> int:
    return state_wrapper.acc_weight


def validate_back_traversing(state_wrapper: s.StateWrapper) -> bool:
    current_vertex = state_wrapper.state.current_vertex

    parent_wrapper = state_wrapper.parent_wrapper
    if parent_wrapper is None:
        return True
    parent_unsaved_vertices = parent_wrapper.state.get_unsaved_vertices()

    grand_parent_wrapper = parent_wrapper.parent_wrapper
    if grand_parent_wrapper is None:
        return True
    grand_parent_vertex = grand_parent_wrapper.state.current_vertex
    grand_parent_unsaved_vertices = grand_parent_wrapper.state.get_unsaved_vertices()

    # make sure that either this is not a back traversal or it was necessary for saving people
    return current_vertex != grand_parent_vertex or parent_unsaved_vertices != grand_parent_unsaved_vertices


class Agent:

    def __init__(self, starting_vertex: v.Vertex, vertices_saved: Dict[v.Vertex, bool],
                 vertices_broken: Dict[v.Vertex, bool], h: Callable, expansion_limit: int, time_limit: int, T: float):
        self.state: s.State = s.State(starting_vertex, vertices_saved, vertices_broken)
        self.h: Callable = h
        self.score: int = 0
        self.terminated: bool = False
        self.act_sequence: List[v.Vertex] = []
        self.num_of_expansions: int = 0
        self.num_of_movements: int = 0
        self.time_passed: int = 0
        self.expansion_limit: int = expansion_limit
        self.time_limit: int = time_limit
        self.T: float = T

    def _search_fringe(self, world: g.Graph, fringe: pq.PriorityQueue) -> int:
        counter = 0
        state_wrapper_of_self_state = s.StateWrapper(c.copy(self.state), None, 0)
        fringe.insert(state_wrapper_of_self_state)
        while not fringe.is_empty():
            current_state_wrapper = fringe.pop()
            current_vertex = current_state_wrapper.state.current_vertex
            acc_weight = current_state_wrapper.acc_weight
            current_state_wrapper.state.save_current_vertex()
            current_state_wrapper.state.break_current_vertex_if_brittle()
            if counter == self.expansion_limit or current_state_wrapper.state.goal_test():
                self.act_sequence = generate_sequence(world.get_edge_weight, current_state_wrapper)
                break
            counter += 1
            for neighbor, edge_weight in world.expand(current_vertex):
                if not current_state_wrapper.state.is_vertex_broken(neighbor):
                    neighbor_state = s.State(neighbor, c.copy(current_state_wrapper.state.vertices_saved),
                                             c.copy(current_state_wrapper.state.vertices_broken))
                    neighbor_state_wrapper = s.StateWrapper(neighbor_state, current_state_wrapper,
                                                            acc_weight + edge_weight)
                    if validate_back_traversing(neighbor_state_wrapper):
                        fringe.insert(neighbor_state_wrapper)
        self.num_of_expansions += counter
        return counter

    def _search(self, world: g.Graph) -> int:
        pass

    def _expand(self, world: g.Graph) -> None:
        expansions_in_search = self._search(world)
        self.terminated = len(self.act_sequence) == 0
        self.time_passed += self.T * expansions_in_search

    def _enter_dest_vertex(self, vertex: v.Vertex) -> None:
        if vertex.people_to_rescue > 0:
            print("Saving: " + str(vertex))
            self.score += vertex.people_to_rescue
            vertex.people_to_rescue = 0
        if vertex.form == v.Form.brittle:
            print("Breaking: " + str(vertex))
            vertex.form = v.Form.broken

    def _move(self) -> None:
        print("Current vertex: " + str(self.state.current_vertex))
        print("Current sequence: " + v.vertex_list_to_string(self.act_sequence))
        self.num_of_movements += 1
        next_vertex = self.act_sequence[0]
        print("Moving to: " + str(next_vertex))
        if next_vertex != self.state.current_vertex:
            self._enter_dest_vertex(self.state.current_vertex)
        self.state.current_vertex = next_vertex
        self.time_passed += 1
        self.act_sequence = self.act_sequence[1:]
        if len(self.act_sequence) == 0:
            self._enter_dest_vertex(self.state.current_vertex)

    def _no_op(self) -> None:
        print("Current vertex: " + str(self.state.current_vertex))
        print("Current sequence: " + v.vertex_list_to_string(self.act_sequence))
        print("No-Op: Staying in current vertex")
        self.time_passed += 1

    def act(self, world: g.Graph) -> None:
        if not self.terminated:
            self.state.update_vertices_saved()
            self.state.update_vertices_broken()
            if len(self.act_sequence) == 0:
                self._expand(world)
                print("Search returned sequence: " + v.vertex_list_to_string(self.act_sequence))
            if not self.terminated and self.time_passed + 1 < self.time_limit:
                next_vertex = self.act_sequence[0]
                if next_vertex != self.state.current_vertex and next_vertex.form == v.Form.broken:
                    self.act_sequence = []
                    self._no_op()
                    return
                self._move()
            else:
                self.terminated = True
                print("TERMINATED")
        else:
            print("TERMINATED")

    def __str__(self):
        agent_str = f"Score: {str(self.score)}\n"
        agent_str += f"Number of expansions: {str(self.num_of_expansions)}\n"
        agent_str += f"Number of movements: {(self.num_of_movements)}\n"
        agent_str += f"Total time passed: {str(self.time_passed)}\n"
        agent_str += f"Agent reached goal!!! \U0001f60e\n" if self.state.goal_test() else "Goal wasn't reached \U0001f61f"
        return agent_str


def all_agents_terminated(agent_list: List[Agent]) -> bool:
    for agent in agent_list:
        if not agent.terminated:
            return False
    return True


class GreedyAgent(Agent):
    def __init__(self, starting_vertex: v.Vertex, vertices_saved: Dict[v.Vertex, bool],
                 vertices_broken: Dict[v.Vertex, bool],
                 h: Callable, expansion_limit: int, time_limit: int, T: float):
        super().__init__(starting_vertex, vertices_saved, vertices_broken, h, expansion_limit, time_limit, T)

    def _search(self, world: g.Graph) -> int:
        fringe = pq.PriorityQueue(lambda x: self.h(x, world))
        return self._search_fringe(world, fringe)


class AStarAgent(Agent):

    def __init__(self, starting_vertex: v.Vertex, vertices_saved: Dict[v.Vertex, bool],
                 vertices_broken: Dict[v.Vertex, bool],
                 h: Callable, expansion_limit: int, time_limit: int, T: float):
        super().__init__(starting_vertex, vertices_saved, vertices_broken, h, expansion_limit, time_limit, T)

    def _search(self, world: g.Graph) -> int:
        fringe = pq.PriorityQueue(lambda x: self.h(x, world) + get_g(x))
        return self._search_fringe(world, fringe)

class RealTimeAStarAgent(Agent):

    def __init__(self, starting_vertex: v.Vertex, vertices_saved: Dict[v.Vertex, bool],
                 vertices_broken: Dict[v.Vertex, bool],
                 h: Callable, expansion_limit: int, time_limit: int, T: float):
        super().__init__(starting_vertex, vertices_saved, vertices_broken, h, expansion_limit, time_limit, T)

    def _search(self, world: g.Graph) -> int:
        fringe = pq.PriorityQueue(lambda x: self.h(x, world) + get_g(x))
        return self._search_fringe(world, fringe)