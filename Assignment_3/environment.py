import yaml
from typing import Dict
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


def get_ints_from_user(message: str) -> list:
    while True:
        try:
            return [int(x) for x in input(message).split(', ')]
        except ValueError:
            print('Invalid input')


def check_val(var: str, val: str) -> bool:
    if var == 'W':
        return val in ['mild', 'stormy', 'extreme']
    var_lower = var.lower()
    return var_lower == val or 'not ' + var_lower == val


def main() -> None:
    print('loading config.yaml file...')
    with open("Inputs/config.yaml", "r") as f:
        config = yaml.safe_load(f)

    parsed_file = parse_file(config['input_file'])

    network = BayesNetwork(parsed_file, config['p1'], config['p2'])
    evidence_set = set()

    while True:
        print('\nChoose one of the following options:')
        print('1. Print network')
        print('2. Reset evidence list to empty')
        print('3. Add evidence to the evidence list')
        print('4. Print the evidence list')
        print('5. Do probabilistic reasoning')
        print('6. Quit')
        option = int(input('Enter your choice: '))
        if option == 1:
            print(network)
        elif option == 2:
            evidence_set = set()
            print('->\tEvidence list is now empty')
        elif option == 3:
            while True:
                print('\nEnter a variable and its value to add to the evidence list')
                print('Example: BV1, not bv1')
                print('Enter empty string to exit')
                evidence = input('Enter: ').split(', ')
                if len(evidence) == 1 and evidence[0] == '':
                    break
                if len(evidence) != 2:
                    print('->\tInvalid input')
                    continue
                var = network.get_node(evidence[0])
                if var is None:
                    print('->\tInvalid variable')
                    continue
                val = evidence[1]
                if not check_val(var.name, val):
                    print('->\tInvalid value')
                    continue
                evidence_set = set.union(evidence_set, {(var, val)})
                print(f'->\tAdded ({var.name}, {val}) to the evidence list')
        elif option == 4:
            if len(evidence_set) == 0:
                print('->\tEvidence list is empty')
                continue
            s = '['
            for var, val in evidence_set:
                s += f'{var.name} = {val}, '
            s = s[:-2] + ']'
            print(f'->\tThe evidence list is: {s}')
        elif option == 5:
            print('Choose one of the following query types:')
            print('1) What is the probability that each of the vertices contains evacuees?')
            print('2) What is the probability that each of the vertices is blocked?')
            print('3) What is the distribution of the weather variable?')
            print('4) What is the probability that a certain path (set of edges) is free from blockages?')
            query_type = int(input('Enter your choice: '))
            if query_type == 1:
                query = get_ints_from_user('Type vertices ids: ')
                x_query = [network.get_node(f'EV{vertex_id}') for vertex_id in query]
                distribution = enumeration_ask(x_query, evidence_set, network)
                all_evacuees_entry = [f'ev{vertex_id}' for vertex_id in query]
                prob = distribution.get(tuple(all_evacuees_entry), 0.0)
                print(f'->\tThe probability is: {prob}')
            elif query_type == 2:
                query = get_ints_from_user('Type vertices ids: ')
                x_query = [network.get_node(f'BV{vertex_id}') for vertex_id in query]
                distribution = enumeration_ask(x_query, evidence_set, network)
                all_blocked_entry = [f'bv{vertex_id}' for vertex_id in query]
                prob = distribution.get(tuple(all_blocked_entry), 0.0)
                print(f'->\tThe probability is: {prob}')
            elif query_type == 3:
                distribution = enumeration_ask([network.get_node('W')], evidence_set, network)
                print('->\tThe distribution is: ', distribution)
            elif query_type == 4:
                query = set()
                edges = get_ints_from_user('Type edges ids: ')
                for edge_id in edges:
                    v1, v2, _ = parsed_file['Es'][int(edge_id)]
                    query.add(v1)
                    query.add(v2)
                x_query = [network.get_node(f'BV{vertex_id}') for vertex_id in query]
                distribution = enumeration_ask(x_query, evidence_set, network)
                all_not_blocked_entry = [f'not bv{vertex_id}' for vertex_id in query]
                prob = distribution.get(tuple(all_not_blocked_entry), 0.0)
                print(f'->\tThe probability is: {prob}')
        elif option == 6:
            print('\nBye!')
            break


if __name__ == '__main__':
    main()
