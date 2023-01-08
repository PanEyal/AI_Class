from typing import Dict

import yaml

from bayes_network import BayesNetwork, enumeration_ask


def parse_file(input_file: str) -> Dict:
    n = None
    vs = {}
    es = {}
    w = None
    with open(input_file, 'r') as graph_file:
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
                edge_id = int(words_array[0][2:])
                first_vertex_id = int(words_array[1])
                second_vertex_id = int(words_array[2])
                edge_weight = int(words_array[3][1])
                es[edge_id] = (first_vertex_id, second_vertex_id, edge_weight)

            if object_type == 'W':
                mild_prob = float(words_array[1])
                stormy_prob = float(words_array[2])
                extreme_prob = float(words_array[3])
                w = (mild_prob, stormy_prob, extreme_prob)

    return {'N': n, 'Vs': vs, 'Es': es, 'W': w}


def main() -> None:
    print('loading config.yaml file...')
    with open("Inputs/config.yaml", "r") as f:
        config = yaml.safe_load(f)

    parsed_file = parse_file(config['input_file'])

    network = BayesNetwork(parsed_file, config['p1'], config['p2'])
    evidence_set = set()

    while True:
        print('Choose one of the following options:')
        print('1. Print network')
        print('2. Reset evidence list to empty')
        print('3. Add evidence to the evidence list')
        print('4. Print the evidence list')
        print('5. Do probabilistic reasoning')
        print('6. Quit')
        option = int(input('\nEnter your choice: '))
        if option == 1:
            print(network)
        elif option == 2:
            evidence_set = set()
        elif option == 3:
            while True:
                print('Enter a variable and its value to add to the evidence list')
                print('Example: var val')
                print('Enter empty string to exit')
                evidence = input('Enter: ').split(' ')
                if len(evidence) == 1 and evidence[0] == '':
                    break
                if len(evidence) != 2:
                    print('Invalid input')
                    continue
                var = network.get_node(evidence[0])
                if var is None:
                    print('Invalid variable')
                    continue
                val = evidence[1]
                evidence_set = set.union(evidence_set, {(var, val)})
        elif option == 4:
            print(evidence_set)
        elif option == 5:
            print('Choose one of the following query types:')
            print('1) What is the probability that each of the vertices contains evacuees?')
            print('2) What is the probability that each of the vertices is blocked?')
            print('3) What is the distribution of the weather variable?')
            print('4) What is the probability that a certain path (set of edges) is free from blockages?')
            query_type = int(input('\nEnter your choice: '))
            if query_type == 1:
                query = input("Type vertices ids: ").split(' ')
                x_query = [network.get_node(f'EV{vertex_id}') for vertex_id in query]
                distribution = enumeration_ask(x_query, evidence_set, network)
                all_evacuees_entry = [f'ev{vertex_id}' for vertex_id in query]
                print('The probability is: ', distribution[tuple(all_evacuees_entry)])
            elif query_type == 2:
                query = input("Type vertices ids: ").split(' ')
                x_query = [network.get_node(f'BV{vertex_id}') for vertex_id in query]
                distribution = enumeration_ask(x_query, evidence_set, network)
                all_blocked_entry = [f'bv{vertex_id}' for vertex_id in query]
                print('The probability is: ', distribution[tuple(all_blocked_entry)])
            elif query_type == 3:
                distribution = enumeration_ask([network.get_node('W')], evidence_set, network)
                print('The distribution is: ', distribution)
            elif query_type == 4:
                query = set()
                edges = input("Type edges ids: ").split(' ')
                for edge_id in edges:
                    v1, v2, _ = parsed_file['Es'][int(edge_id)]
                    query.add(v1)
                    query.add(v2)
                x_query = [network.get_node(f'BV{vertex_id}') for vertex_id in query]
                distribution = enumeration_ask(x_query, evidence_set, network)
                all_blocked_entry = [f'not bv{vertex_id}' for vertex_id in query]
                print('The probability is: ', distribution[tuple(all_blocked_entry)])


if __name__ == '__main__':
    main()
