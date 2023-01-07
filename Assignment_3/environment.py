from bayes_network import create_bayes_network
from bayes_network import enumeration_ask
import names


def get_variables_assignment_set(vars_list):
    output_set = set()

    for item in vars_list.split(' '):
        item = item.split(',')
        if len(item) == 1:
            return output_set
        var = item[0]
        val = item[1]
        if val == 'T':
            val = True
        elif val == 'F':
            val = False
        output_set.add((var, val))
    return output_set


if __name__ == '__main__':
    network = create_bayes_network(names.input_file)
    print(network)
    print('Query Options: ')
    print('1) What is the probability that each of the vertices contains evacuees?')
    print('2) What is the probability that each of the edges is blocked?')
    print('3) What is the probability that a certain path (set of edges) is free from blockages?')
    query_number = int(input('Please insert choice (number) \n'))
    variables_list = (input(
        'Insert evidence separated by space for each variable followed by its boolean value \n (i.e v1,F e1_t:0,T for v1 NOT containing evacuees and edge 1 is blocked at time 0) \n'))
    evidence = get_variables_assignment_set(variables_list)
    x_query = []
    if query_number == 1:
        x_query = [input("Type vertex name\n")]
        distribution = enumeration_ask(x_query, evidence, network)
        all_evacuees_entry = [True for item in x_query]
        print('The probability is: ', distribution[tuple(all_evacuees_entry)])
    elif query_number == 2:
        x_query = [input("Type Edge name name and time (i.e e1_t:0 e2_t:1)\n")]
        distribution = enumeration_ask(x_query, evidence, network)
        all_blocked_entry = [True for item in x_query]
        print('The probability is: ', distribution[tuple(all_blocked_entry)])
    elif query_number == 3:
        x_query = input('Specify edges to check (i.e e1_t:0 e2_t:1) \n').split(' ')
        distribution = enumeration_ask(x_query, evidence, network)
        not_blocked_entry = [False for item in x_query]
        print('The probability is: ', distribution[tuple(not_blocked_entry)])
    print('See you in the next assignment NOA')
