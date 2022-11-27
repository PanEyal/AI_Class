import itertools
from typing import Callable, Dict, List

import vertex as v
import graph as g
import state as s
import copy as c
import priority_queue as pq
import program_variables


def generate_sequence(get_edge_weight: Callable, state_wrapper: s.StateWrapper) -> List[v.Vertex]:
    if state_wrapper.parent_wrapper is None:
        return []
    edge_weight = get_edge_weight(state_wrapper.parent_wrapper.state.current_vertex, state_wrapper.state.current_vertex)
    current_move = []
    for i in range(edge_weight - 1):
        current_move.append(state_wrapper.parent_wrapper.state.current_vertex)
    current_move.append(state_wrapper.state.current_vertex)
    current_sequence = generate_sequence(get_edge_weight, state_wrapper.parent_wrapper)
    current_sequence.extend(current_move)
    return current_sequence


def get_g(state_wrapper: s.StateWrapper) -> int:
    return state_wrapper.acc_weight


def goal_test(state: s.State) -> bool:
    return state.num_of_vertices_to_save() == 0


class Agent:

    def __init__(self, starting_vertex: v.Vertex, vertices_saved: Dict[v.Vertex, bool], vertices_broken: Dict[v.Vertex, bool], h: Callable,
                 save_people: bool = True):
        self.state: s.State = s.State(starting_vertex, vertices_saved, vertices_broken)
        self.h: Callable = h
        self.score: int = 0
        self.terminated: bool = False
        self.act_sequence: List[v.Vertex] = []
        self.num_of_expansions: int = 0
        self.num_of_movements: int = 0
        self.time_passed: int = 0
        self.save_people: bool = save_people

    def _search_fringe(self, world: g.Graph, fringe: pq.PriorityQueue, limit: int) -> int:
        counter = 0
        state_wrapper_of_self_state = s.StateWrapper(c.copy(self.state), None, 0)
        fringe.insert(state_wrapper_of_self_state)
        while not fringe.is_empty():
            current_state_wrapper = fringe.pop()
            current_vertex = current_state_wrapper.state.current_vertex
            acc_weight = current_state_wrapper.acc_weight
            current_state_wrapper.state.save_current_vertex()
            current_state_wrapper.state.break_current_vertex_if_brittle()
            if counter == limit or goal_test(current_state_wrapper.state):
                self.act_sequence = generate_sequence(world.get_edge_weight, current_state_wrapper)
                break
            counter += 1
            for neighbor, edge_weight in world.expand(current_vertex):
                if not current_state_wrapper.state.is_vertex_broken(neighbor):
                    neighbor_state = s.State(neighbor, c.copy(current_state_wrapper.state.vertices_saved),
                                             c.copy(current_state_wrapper.state.vertices_broken))
                    neighbor_state_wrapper = s.StateWrapper(neighbor_state, current_state_wrapper,
                                                            acc_weight + edge_weight)
                    fringe.insert(neighbor_state_wrapper)
        self.num_of_expansions += counter
        return counter

    def _search(self, world: g.Graph, limit: int) -> int:
        pass

    def _expand(self, world: g.Graph, limit: int) -> None:
        expansions_in_search = self._search(world, limit)
        self.terminated = len(self.act_sequence) == 0
        print("Searched, output act sequence is: " + v.vertex_list_to_string(self.act_sequence))
        self.time_passed += program_variables.T * expansions_in_search

    def _enter_dest_vertex(self, vertex: v.Vertex) -> None:
        if vertex.people_to_rescue > 0 and self.save_people:
            print("Saving: " + str(vertex))
            self.score += vertex.people_to_rescue
            vertex.people_to_rescue = 0
        if vertex.form == v.Form.brittle:
            print("Breaking: " + str(vertex))
            vertex.form = v.Form.broken

    def _move(self) -> None:
        self.num_of_movements += 1
        print("Current sequence: " + v.vertex_list_to_string(self.act_sequence))
        next_vertex = self.act_sequence[0]
        print("Current Vertex: " + str(self.state.current_vertex))
        print("Moving to: " + str(next_vertex))
        if next_vertex != self.state.current_vertex:
            self._enter_dest_vertex(next_vertex)
        self.state.current_vertex = next_vertex
        self.time_passed += 1
        self.act_sequence = self.act_sequence[1:]

    def _act_with_limit(self, world: g.Graph, limit: int) -> None:
        print("------ " + type(self).__name__ + " ------")
        if not self.terminated:
            self.state.update_vertices_saved()
            self.state.update_vertices_broken()
            if len(self.act_sequence) == 0:
                self._expand(world, limit)
            if not self.terminated and self.time_passed + 1 < program_variables.TIME_LIMIT:
                next_vertex = self.act_sequence[0]
                if next_vertex != self.state.current_vertex and next_vertex.form == v.Form.broken:
                    if self.state.current_vertex.form == v.Form.broken:
                        self.terminated = True
                        print("TERMINATED\n")
                        return
                    print("Destination vertex is broken, traversing back")
                    back_steps = world.get_edge_weight(next_vertex, self.state.current_vertex) - 1
                    if back_steps == 0:
                        self._expand(world, limit)
                    else:
                        self.act_sequence = [self.state.current_vertex for _ in range(back_steps)]
                self._move()
            else:
                self.terminated = True
                print("TERMINATED\n")
        else:
            print("TERMINATED\n")

    def __str__(self):
        agent_str = "-------------------------\n"
        agent_str += type(self).__name__ + "\n"
        agent_str += "Score: " + str(self.score) + "\n"
        agent_str += "Number of expansions: " + str(self.num_of_expansions) + "\n"
        agent_str += "Number of movements: " + str(self.num_of_movements) + "\n"
        agent_str += "Total time passed: " + str(self.time_passed) + "\n"
        agent_str += "-------------------------\n"
        return agent_str


def all_agents_terminated(agent_list: List[Agent]) -> bool:
    for agent in agent_list:
        if not agent.terminated:
            return False
    return True


class HumanAgent(Agent):

    def __init__(self, starting_vertex: v.Vertex, vertices_saved: Dict[v.Vertex, bool], vertices_broken: Dict[v.Vertex, bool],
                 h: Callable):
        super().__init__(starting_vertex, vertices_saved, vertices_broken, h)

    def act(self, world: g.Graph) -> None:
        print("------ " + type(self).__name__ + " ------")
        if not self.terminated:
            if len(self.act_sequence) == 0:
                print("HumanAgent: you are here: " + str(self.state.current_vertex))
                neighbors = world.expand(self.state.current_vertex)
                print("-----------------------world-----------------------")
                print(world)
                print("---------------------neighbors---------------------")
                neighbors = list(itertools.filterfalse(lambda ve: ve.form == v.Form.broken, neighbors))
                i = -1
                for i, vertex, weight in enumerate(neighbors):
                    print("option: " + str(i) + ", vertex: " + str(vertex) + ", with weight: " + str(weight))
                print("option: " + str(i + 1) + ", no-op")
                neighbors.append(("no-op", 1))
                selection = -1
                while selection < 0 or selection > i:
                    selection = input("HumanAgent: pick the desired option NOW: ")
                self.act_sequence = [self.state.current_vertex for _ in range(neighbors[selection][1] - 1)].append(
                    neighbors[selection][0])
            elif self.act_sequence[-1].form == v.Form.broken:
                if self.state.current_vertex.form == v.Form.broken:
                    self.terminated = True
                    print("TERMINATED\n")
                    return
                print("Destination vertex is broken, traversing back")
                back_steps = world.get_edge_weight(self.act_sequence[-1], self.state.current_vertex) - 1
                self.act_sequence = [self.state.current_vertex for _ in range(back_steps)]
            else:
                print("HumanAgent: traversing across previous selected edge")
            self._move()
        else:
            print("TERMINATED\n")


class SaboteurAgent(Agent):

    def __init__(self, starting_vertex: v.Vertex, vertices_saved: Dict[v.Vertex, bool], vertices_broken: Dict[v.Vertex, bool],
                 h: Callable):
        super().__init__(starting_vertex, vertices_saved, vertices_broken, h, True)

    def _search(self, world: g.Graph, limit: int) -> int:
        fringe = pq.PriorityQueue(self.h)
        return self._search_fringe(world, fringe, limit)

    def act(self, world: g.Graph) -> None:
        self._act_with_limit(world, program_variables.ASTAR_LIMIT)


class GreedyAgent(Agent):

    def __init__(self, starting_vertex: v.Vertex, vertices_saved: Dict[v.Vertex, bool], vertices_broken: Dict[v.Vertex, bool],
                 h: Callable):
        super().__init__(starting_vertex, vertices_saved, vertices_broken, h)

    def _search(self, world: g.Graph, limit: int) -> int:
        fringe = pq.PriorityQueue(self.h)
        return self._search_fringe(world, fringe, limit)

    def act(self, world: g.Graph) -> None:
        self._act_with_limit(world, program_variables.GREEDY_LIMIT)


class AStarAgent(Agent):

    def __init__(self, starting_vertex: v.Vertex, vertices_saved: Dict[v.Vertex, bool], vertices_broken: Dict[v.Vertex, bool],
                 h: Callable):
        super().__init__(starting_vertex, vertices_saved, vertices_broken, h)

    def _search(self, world: g.Graph, limit: int) -> int:
        fringe = pq.PriorityQueue(lambda x: self.h(x) + get_g(x))
        return self._search_fringe(world, fringe, limit)

    def act(self, world: g.Graph) -> None:
        self._act_with_limit(world, program_variables.ASTAR_LIMIT)


class RealTimeAStarAgent(Agent):

    def __init__(self, starting_vertex: v.Vertex, vertices_saved: Dict[v.Vertex, bool], vertices_broken: Dict[v.Vertex, bool],
                 h: Callable):
        super().__init__(starting_vertex, vertices_saved, vertices_broken, h)

    def _search(self, world: g.Graph, limit: int) -> int:
        fringe = pq.PriorityQueue(lambda x: self.h(x) + get_g(x))
        return self._search_fringe(world, fringe, limit)

    def act(self, world: g.Graph) -> None:
        self._act_with_limit(world, program_variables.REALTIME_ASTAR_LIMIT)
