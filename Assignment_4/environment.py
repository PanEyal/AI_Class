import random
import yaml
from typing import Dict

import agent
from graph import Graph
from mdp import value_iteration, print_policies
from state import Status, generate_states
from vertex import Vertex


def parse_file(input_file: str) -> Dict:
    n = None
    edges = {}
    blockages_prob = {}
    start = None
    target = None

    with open(input_file, 'r') as graph_file:
        for line in graph_file.readlines():
            words_array = (line.partition(';'))[0].split(' ')
            if len(words_array[0]) <= 1:
                continue
            object_type = words_array[0][1]

            if object_type == 'V':
                n = int(words_array[1])

            elif object_type == 'E':
                edge_id = int(words_array[0][2:])
                first_vertex_id = int(words_array[1])
                second_vertex_id = int(words_array[2])
                edge_weight = int(words_array[3][1:])
                edges[edge_id] = (first_vertex_id, second_vertex_id, edge_weight)

            if object_type == 'B':
                vertex_id = int(words_array[1])
                vertex_blockage_prob = float(words_array[2])
                blockages_prob[vertex_id] = vertex_blockage_prob

            if object_type == 'S':
                start = int(words_array[1])

            if object_type == 'T':
                target = int(words_array[1])

    return {'N': n, 'Es': edges, 'Bs': blockages_prob, 'S': start, 'T': target}


if __name__ == '__main__':
    print('loading config.yaml file...')
    with open('Inputs/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    parsed_file = parse_file(config['INPUT_PATH'])

    graph = Graph(parsed_file, -(config['MIN_UTILITY'] + 1))
    print('The vertices:', graph.get_vertices())
    states = generate_states(graph)
    policies = value_iteration(states, graph, config['MIN_UTILITY'])
    print_policies(policies)
    print(f'\n\n\n----------------------SIMULATION----------------------\n')
    while True:
        s = 'Chosen Brittle vertices statuses: '
        brittle_vertices_status: Dict[Vertex, Status] = {}
        for brittle_vertex in graph.get_brittle_vertices():
            blockage_prob = brittle_vertex.get_blockage_prob()
            brittle_vertices_status[brittle_vertex] = random.choices((Status.BLOCKED, Status.UNBLOCKED),
                                                                     weights=(blockage_prob, 1 - blockage_prob))[0]
            s += f'(V{brittle_vertex.id}: {brittle_vertices_status[brittle_vertex].name}), '
        print(s)
        print('Running...')

        agent.find_target(graph, brittle_vertices_status, policies, states, graph.get_start_vertex_id())
        if input('Do you want to run another simulation? (y/n) ') != 'y':
            break
