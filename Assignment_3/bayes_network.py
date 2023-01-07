from typing import Dict, List, Union
from node import Node
import itertools


class BayesNetwork:
    def __init__(self, _input_file: str, _p1: float, _p2: float):
        self.n = None
        self.children_dict: Dict[Node, List[Node]] = {}
        self.parents_dict: Dict[Node, List[Node]] = {}
        self.input_file = _input_file
        self.initialize_bayes_network(self.parse_file(_input_file), _p1, _p2)

    def parse_file(self, _input_file: str) -> Dict:
        n = None
        vs = {}
        es = []
        w = None
        with open(self.input_file, 'r') as graph_file:
            for line in graph_file.readlines():
                words_array = (line.partition(';'))[0].split(' ')
                if len(words_array[0]) <= 1:
                    continue
                object_type = words_array[0][1]

                if object_type == 'N':
                    n = int(words_array[1])

                elif object_type == 'V':
                    vertex_id = int(words_array[1])
                    blockage_prob = float(words_array[3])
                    vs[vertex_id] = blockage_prob

                elif object_type == 'E':
                    first_vertex_id = int(words_array[1])
                    second_vertex_id = int(words_array[2])
                    edge_weight = int(words_array[3][1])
                    es.append((first_vertex_id, second_vertex_id, edge_weight))

                if object_type == 'W':
                    mild_prob = float(words_array[1])
                    stormy_prob = float(words_array[2])
                    extreme_prob = float(words_array[3])
                    w = (mild_prob, stormy_prob, extreme_prob)

        return {'N': n, 'Vs': vs, 'Es': es, 'W': w}

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
            blocked_node.add_prob('blocked', 'mild', min(1.0, blockage_prob))
            blocked_node.add_prob('blocked', 'stormy', min(1.0, blockage_prob * 2.0))
            blocked_node.add_prob('blocked', 'extreme', min(1.0, blockage_prob * 3.0))

            self.add_node(blocked_node)
            self.add_relation(weather_node, blocked_node)

            evacuees_node = Node(f'EV{vertex_id}')
            evacuees_node.add_prob('evacuees', Node.all_false, 0.0)
            evacuees_node.add_prob('evacuees', f'blockage {vertex_id}', 1.0 - p2)
            self.add_node(evacuees_node)
            self.add_relation(blocked_node, evacuees_node)

        for v1, v2, w in parsed['Es']:
            bv1 = self.get_node(f'BV{v1}')
            ev1 = self.get_node(f'EV{v1}')
            bv2 = self.get_node(f'BV{v2}')
            ev2 = self.get_node(f'EV{v2}')

            ev1.add_prob('evacuees', f'blockage {v2}', 1.0 - min(1.0, p1 * w))
            ev2.add_prob('evacuees', f'blockage {v1}', 1.0 - min(1.0, p1 * w))

            self.add_relation(bv1, ev2)
            self.add_relation(bv2, ev1)

    def add_node(self, node: Node) -> None:
        if not self.children_dict.get(node):
            self.children_dict[node] = []
        if not self.parents_dict.get(node):
            self.parents_dict[node] = []

    def add_relation(self, parent: Node, child: Node) -> None:
        if child not in self.children_dict[parent]:
            self.children_dict[parent].append(child)
        if parent not in self.parents_dict[child]:
            self.parents_dict[child].append(parent)

    def get_node(self, node_name: str) -> Union[Node, None]:
        for node in self.children_dict.keys():
            if node.name == node_name:
                return node
        return None

    def get_parents(self, child_name: str) -> List:
        child_node = self.get_node(child_name)
        return self.parents_dict[child_node]

    def get_all_nodes(self) -> List:
        return list(self.children_dict.keys())

    def __str__(self):
        s = 'WEATHER:\n'
        weather_node = self.get_node('W')
        s += str(weather_node) + '\n'

        for vertex_id in range(1, self.n + 1):
            s += f'VERTEX {vertex_id}:\n'
            bvi = self.get_node(f'BV{vertex_id}')
            evi = self.get_node(f'EV{vertex_id}')
            s += str(bvi) + '\n'
            s += str(evi) + '\n'

        return s


# evidence = {(v1, 0.5),..., (vn, 0.4)}
def has_value_in_evidence(Y, evidence):
    for tup in evidence:
        if tup[0] == Y:
            return True, tup[1]
    return False, -1


def get_parent_assignment_in_evidence(Y: str, evidence: set, bayes_network: BayesNetwork) -> list:
    parents_in_evidence = []
    parents_in_bayes = bayes_network.get_parents(Y)
    parents_in_bayes_names = list(map(lambda node: node.name, parents_in_bayes))
    for assignment in evidence:
        parent_name = assignment[0]
        if parent_name in parents_in_bayes_names:
            parents_in_evidence.append(assignment)
    return parents_in_evidence


def normalize(distribution):
    acc = 0
    for value in distribution.values():
        acc += value
    if not acc == 0:
        for key_value in distribution.items():
            key = key_value[0]
            value = key_value[1]
            distribution[key] = round(value / acc, 3)
    return distribution


def enumeration_ask(x_query: list, evidence: set, bayes_network: BayesNetwork):
    distribution_x = {}  # Q(X)
    options = [False, True]
    variables = list(map(lambda node: node.name, bayes_network.get_all_nodes()))
    x_query_possible_values = list(itertools.product(options, repeat=len(x_query)))
    for assignment in x_query_possible_values:
        extended_evidence = evidence.union(set(zip(x_query, assignment)))
        prob = enumeration_all(variables, extended_evidence, bayes_network)
        distribution_x[assignment] = prob
    return normalize(distribution_x)


def enumeration_all(variables, evidence, bayes_network):
    if len(variables) == 0:
        return 1
    Y = variables[0]
    Y_node = bayes_network.get_node(Y)
    has_val, val = has_value_in_evidence(Y, evidence)
    Y_parents = get_parent_assignment_in_evidence(Y, evidence, bayes_network)
    if has_val:
        prob_Y_given_parents = Y_node.table.get_probability_given_parents(val, Y_parents)
        return prob_Y_given_parents * enumeration_all(variables[1:], evidence, bayes_network)
    else:
        prob_Y_false = Y_node.table.get_probability_given_parents(False, Y_parents) * enumeration_all(variables[1:],
                                                                                                      evidence.union(
                                                                                                          {(Y, False)}),
                                                                                                      bayes_network)
        prob_Y_true = Y_node.table.get_probability_given_parents(True, Y_parents) * enumeration_all(variables[1:],
                                                                                                    evidence.union(
                                                                                                        {(Y, True)}),
                                                                                                    bayes_network)
        return prob_Y_false + prob_Y_true


if __name__ == '__main__':
    bayes_network = BayesNetwork('Inputs/input.txt', 0.2, 0.3)
    print(bayes_network)
