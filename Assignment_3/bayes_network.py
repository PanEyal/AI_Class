from typing import Dict, List, Union, Set, Tuple
from node import Node
import itertools


class BayesNetwork:
    def __init__(self, parsed_file: Dict, _p1: float, _p2: float):
        self.nodes = {}
        self.n = None
        self.initialize_bayes_network(parsed_file, _p1, _p2)

    def initialize_bayes_network(self, parsed: Dict, p1: float, p2: float):

        mild_prob, stormy_prob, extreme_prob = parsed['W']
        weather_node = Node('W')
        weather_node.add_prob('mild', Node.empty, mild_prob)
        weather_node.add_prob('stormy', Node.empty, stormy_prob)
        weather_node.add_prob('extreme', Node.empty, extreme_prob)
        self.add_node(weather_node)

        initial_vertices = parsed['Vs']
        self.n = parsed['N']
        for vertex_id in range(1, self.n + 1):
            blocked_node = Node(f'BV{vertex_id}')
            blockage_prob = 0.0 if vertex_id not in initial_vertices else initial_vertices[vertex_id]
            blocked_node.add_prob(f'bv{vertex_id}', 'mild', min(1.0, blockage_prob))
            blocked_node.add_prob(f'bv{vertex_id}', 'stormy', min(1.0, blockage_prob * 2.0))
            blocked_node.add_prob(f'bv{vertex_id}', 'extreme', min(1.0, blockage_prob * 3.0))

            self.add_node(blocked_node)
            Node.add_relation(weather_node, blocked_node)

            evacuees_node = Node(f'EV{vertex_id}')
            evacuees_node.add_prob(f'ev{vertex_id}', Node.all_false, 0.0)
            evacuees_node.add_prob(f'ev{vertex_id}', f'bv{vertex_id}', 1.0 - p2)
            self.add_node(evacuees_node)
            Node.add_relation(blocked_node, evacuees_node)

        for v1, v2, w in parsed['Es'].values():
            bv1 = self.get_node(f'BV{v1}')
            ev1 = self.get_node(f'EV{v1}')
            bv2 = self.get_node(f'BV{v2}')
            ev2 = self.get_node(f'EV{v2}')

            ev1.add_prob(f'ev{v1}', f'bv{v2}', 1.0 - min(1.0, p1 * w))
            ev2.add_prob(f'ev{v2}', f'bv{v1}', 1.0 - min(1.0, p1 * w))

            Node.add_relation(bv1, ev2)
            Node.add_relation(bv2, ev1)

    def add_node(self, node: Node) -> None:
        self.nodes[node.name] = node

    def get_node(self, node_name: str) -> Union[Node, None]:
        return self.nodes.get(node_name)

    def get_nodes(self) -> List[Node]:
        ordered_nodes = []
        for vertex_id in range(1, self.n + 1):
            ordered_nodes.insert(0, self.get_node(f'BV{vertex_id}'))
            ordered_nodes.append(self.get_node(f'EV{vertex_id}'))
        ordered_nodes.insert(0, self.get_node('W'))
        return ordered_nodes

    def __str__(self):
        s = 'WEATHER:\n'
        weather_node = self.get_node('W')
        s += str(weather_node) + '\n'

        for vertex_id in range(1, self.n + 1):
            s += f'VERTEX {vertex_id}:\n'
            bvi = self.get_node(f'BV{vertex_id}')
            evi = self.get_node(f'EV{vertex_id}')
            s += str(bvi) + '\n'
            s += str(evi)

        return s


def get_value_in_evidence(Y: Node, e: Set[Tuple[Node, str]]) -> Union[str, None]:
    for var, val in e:
        if var == Y:
            return val
    return None


def get_parent_assignment_in_evidence(Y: Node, evidence: Set[Tuple[Node, str]]) -> Set[str]:
    parents_assignments_in_evidence = set()
    node_parents = Y.get_parents()
    for var, val in evidence:
        if var in node_parents:
            parents_assignments_in_evidence.add(val)
    return parents_assignments_in_evidence


def normalize(distribution: Dict[Tuple[str, ...], float]) -> Dict[Tuple[str, ...], float]:
    acc = sum(distribution.values())
    if not acc == 0:
        for key, value in distribution.items():
            distribution[key] = round(value / acc, 3)
    return distribution


def get_query_values_given_evidence(x: Node, evidence: Set[Tuple[Node, str]]) -> List[str]:
    for var, val in evidence:
        if var == x:
            return [val]
    return x.get_values()


def enumeration_ask(x_query: List[Node], e: Set[Tuple[Node, str]], bn: BayesNetwork) -> Dict[Tuple[str, ...], float]:
    distribution_x = {}  # Q(X)
    possible_values = [get_query_values_given_evidence(x, e) for x in x_query]
    x_query_possible_assignments = list(itertools.product(*possible_values))
    bn_variables = bn.get_nodes()
    for assignment in x_query_possible_assignments:
        extended_evidence = set.union(e, set(zip(x_query, assignment)))
        prob = enumerate_all(bn_variables, extended_evidence)
        distribution_x[assignment] = prob
    return normalize(distribution_x)


def enumerate_all(_vars: List[Node], e: Set[Tuple[Node, str]]) -> float:
    if len(_vars) == 0:
        return 1.0
    Y = _vars[0]
    val = get_value_in_evidence(Y, e)
    Y_parents = get_parent_assignment_in_evidence(Y, e)
    if val is not None:
        prob_Y_given_parents = Y.get_prob_given_parents_evidence(val, Y_parents)
        return prob_Y_given_parents * enumerate_all(_vars[1:], e)
    else:
        prob = 0.0
        for y_val in Y.get_values():
            prob_Y_given_parents = Y.get_prob_given_parents_evidence(y_val, Y_parents)
            prob += prob_Y_given_parents * enumerate_all(_vars[1:], set.union(e, {(Y, y_val)}))
        return prob

