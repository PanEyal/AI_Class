from typing import List, Tuple, Union

import graph as g
import state as s
import vertex as v


class Agent:

    def __init__(self, initial_state: s.State, _id: int):

        self.state: s.State = initial_state
        self.score: int = 0
        self.terminated: bool = False
        self.id: int = _id

        self._enter_dest_vertex(initial_state.current_vertices[_id])

    def _enter_dest_vertex(self, vertex: v.Vertex) -> None:
        if vertex.people_to_rescue > 0:
            print("Saving: " + str(vertex))
            self.score += vertex.people_to_rescue
            vertex.people_to_rescue = 0
        if vertex.form == v.Form.brittle:
            print("Breaking: " + str(vertex))
            vertex.form = v.Form.broken

    def _move(self, next_vertex: v.Vertex) -> None:
        print("Current vertex: " + str(self.state.current_vertices[self.id]))
        print("Moving to: " + str(next_vertex))
        self._enter_dest_vertex(next_vertex)
        self.state.current_vertices[self.id] = next_vertex

    def _no_op(self) -> None:
        print("Current vertex: " + str(self.state.current_vertices[self.id]))
        print('No-Op: Staying in current vertex')

    def act(self, world: g.Graph) -> Union[s.State, None]:
        self.state.update_vertices_saved()
        self.state.update_vertices_broken()

        next_vertex = None
        if self.state.is_all_saved():
            self.terminated = True
        else:
            next_vertex = self._search(world)

        if next_vertex is None:
            self.terminated = True
        elif next_vertex == self.state.current_vertices[self.id]:
            self._no_op()
        else:
            self._move(next_vertex)

        if self.terminated:
            print("TERMINATED")
            return None
        else:
            return self.state

    def __str__(self):
        agent_str = f"Score: {str(self.score)}\n"
        agent_str += f"All people saved!\n" if self.state.is_all_saved() else \
            "Not all people saved..."
        return agent_str

    def _search(self, world: g.Graph) -> v.Vertex:
        pass


def all_agents_terminated(agent_list: List[Agent]) -> bool:
    for agent in agent_list:
        if not agent.terminated:
            return False
    return True


class AdversarialAgent(Agent):
    def __init__(self, initial_state, _id: int):
        super().__init__(initial_state, _id)

    def _search(self, world: g.Graph) -> v.Vertex:
        return self._search_minimax(world)

    def _search_minimax(self, world: g.Graph) -> v.Vertex:
        best_vertex = None
        val = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        for next_state in self.state.successor(self.id, world):
            value_of_new_state = self.min_value_alpha_beta(next_state, world, alpha, beta)
            if val < value_of_new_state:
                val = value_of_new_state
                best_vertex = next_state.current_vertices[self.id]
            alpha = max(val, alpha)
        return best_vertex

    def max_value_alpha_beta(self, state: s.State, world: g.Graph, alpha: float, beta: float) -> float:
        if state.terminal_state():
            return state.evaluate_alpha_beta(self.id)
        val = float('-inf')
        for next_state in state.successor(self.id, world):
            val = max(val, self.min_value_alpha_beta(next_state, world, alpha, beta))
            if val >= beta:
                return val
            alpha = max(alpha, val)
        return val

    def min_value_alpha_beta(self, state: s.State, world: g.Graph, alpha: float, beta: float) -> float:
        if state.terminal_state():
            return state.evaluate_alpha_beta(self.id)
        val = float('inf')
        for next_state in state.successor(1 - self.id, world):
            val = min(val, self.max_value_alpha_beta(next_state, world, alpha, beta))
            if val <= alpha:
                return val
            beta = min(beta, val)
        return val


class MaxAgent(Agent):
    def __init__(self, initial_state, _id: int):
        super().__init__(initial_state, _id)

    def _search(self, world: g.Graph) -> v.Vertex:
        return self._search_max(world)

    def _search_max(self, world: g.Graph) -> v.Vertex:
        best_value = None
        best_vertex = None
        for next_state in self.state.successor(self.id, world):
            value_of_new_state = self.max_value(next_state, 1 - self.id, world)
            if best_value is None:
                best_value = value_of_new_state
                best_vertex = next_state.current_vertices[self.id]
            elif self._compare_vals(self._order_val_tup(value_of_new_state, self.id),
                                    self._order_val_tup(best_value, self.id)):
                best_value = value_of_new_state
                best_vertex = next_state.current_vertices[self.id]
        return best_vertex

    def max_value(self, state, agent_id, world: g.Graph) -> Tuple[int, int, int]:
        if state.terminal_state():
            return state.evaluate()
        best_value = None
        for next_state in state.successor(agent_id, world):
            next_state_vertices = next_state.current_vertices
            current_vertices = self.state.current_vertices
            curr_value = self.max_value(next_state, 1 - agent_id, world)
            if best_value is None:
                best_value = curr_value
            elif self._compare_vals(self._order_val_tup(curr_value, agent_id),
                                    self._order_val_tup(best_value, agent_id)):
                best_value = curr_value
        return best_value

    @staticmethod
    def _order_val_tup(tup: Tuple[int, int, int], agent_id: int) -> Tuple[int, int, int]:
        return tup[agent_id], tup[1 - agent_id], tup[2]

    @staticmethod
    def _compare_vals(val1: Tuple[int, int, int], val2: Tuple[int, int, int]) -> Tuple[int, int, int]:
        pass


class SemiCoopAgent(MaxAgent):
    def __init__(self, initial_state, _id: int):
        super().__init__(initial_state, _id)

    @staticmethod
    def _compare_vals(val1: Tuple[int, int, int], val2: Tuple[int, int, int]) -> bool:
        return val1 > val2


class FullyCoopAgent(MaxAgent):
    def __init__(self, initial_state, _id: int):
        super().__init__(initial_state, _id)

    @staticmethod
    def _compare_vals(val1: Tuple[int, int, int], val2: Tuple[int, int, int]) -> bool:
        temp1 = (val1[0] + val1[1], val1[2])
        temp2 = (val2[0] + val2[1], val2[2])

        return temp1 > temp2
