from typing import List

import graph as g
import vertex as v
import agent as a
import state as s
import program_variables

world = None


def generate_graph(file_name: str):
    graph = g.Graph()
    file = open(file_name)
    lines = file.readlines()
    vertices = {}

    for line in lines:
        line = (line.partition(';'))[0].split(' ')
        if len(line[0]) <= 1:
            continue
        object_type = line[0][1]

        if object_type == 'N':
            pass  # what is it good for?

        elif object_type == 'V':
            id = int(line[0][2])
            people_to_rescue = 0
            brittle = False
            for property in line[1:]:
                if len(property) == 0:
                    continue
                if property[0] == 'P':
                    people_to_rescue = int(property[1])
                elif property[0] == 'B':
                    brittle = True

            u = v.Vertex(id, people_to_rescue, v.Form.brittle if brittle else v.Form.stable)
            vertices[u.id] = u
            graph.add_vertex(u)

        elif object_type == 'E':
            id = int(line[0][2])
            v1 = vertices[int(line[1])]
            v2 = vertices[int(line[2])]
            edge_weight = int(line[3][1:])
            graph.add_edge(v1, v2, edge_weight)

    file.close()
    return graph


def get_vertices_with_positive_num_of_people(world: g.Graph):
    list_of_positives = []
    for vertex in world.get_vertices():
        if vertex.people_to_rescue > 0:
            list_of_positives.append(vertex)
    return list_of_positives


def get_vertices_list_as_vertices_saved_dict(vertices_list: List[v.Vertex]):
    vertices_saved_dict = dict()
    for vertex in vertices_list:
        vertices_saved_dict[vertex] = False
    return vertices_saved_dict


def mst_heuristic(state_wrapper: s.StateWrapper) -> int:
    global world
    unsaved_vertices = state_wrapper.state.get_unsaved_vertices()
    essential_vertices = unsaved_vertices
    if state_wrapper.state.current_vertex not in essential_vertices:
        essential_vertices.append(state_wrapper.state.current_vertex)
    zipped_graph = g.zip_graph(world, essential_vertices)
    mst_zipped = zipped_graph.MST()
    return mst_zipped.get_sum_weights()


# def create_vertices_list_size(n):
#     v_list = []
#     for i in range(n):
#         v = 'v' + str(i + 1)
#         v_list.append(v)
#     return v_list


# def create_clique_graph_file_size(n):
#     v_list = create_vertices_list_size(n)
#     with open('graph.txt', 'w+') as file:
#         for vertex_name in v_list:
#             str_to_write = 'V ' + vertex_name + ' ' + '3' + '\n'
#             file.write(str_to_write)
#         for vertex_name in v_list:
#             for other_vertex_name in v_list:
#                 if vertex_name != other_vertex_name:
#                     if abs(int(vertex_name[1:]) - int(other_vertex_name[1:])) == 1 or (
#                             (vertex_name[1:] == "1" and other_vertex_name[1:] == str(n)) or (
#                             vertex_name[1:] == str(n) and other_vertex_name[1:] == "1")):
#                         file.write('E ' + vertex_name + ' ' + other_vertex_name + ' 6' + '\n')
#                     else:
#                         file.write('E ' + vertex_name + ' ' + other_vertex_name + ' 1' + '\n')


def query_number_from_user(text, limit):
    inserted_valid_value = False
    inserted_num = 0
    inserted_value = None
    while not inserted_valid_value:
        inserted_value = input(text)
        if inserted_value == 'exit':
            exit(0)
        try:
            inserted_num = int(inserted_value)
            if limit > inserted_num > 0:
                inserted_valid_value = True
            else:
                print('invalid value: ' + inserted_value + '.. should be a number smaller than ' + str(limit))
        except ValueError:
            print('invalid value: ' + inserted_value + '.. should be a number smaller than ' + str(limit))
    return inserted_num


# def create_basic_agent(agent_type, starting_vertex, world):
#     positive_vertices = get_vertices_with_positive_num_of_people(world)
#     # vertices_saved = get_vertices_list_as_vertices_saved_dict(positive_vertices)
#     # if agent_type == 1:
#     #     return a.GreedyAgent(starting_vertex, vertices_saved, mst_heuristic)
#     # elif agent_type == 2:
#     #     return a.AStarAgent(starting_vertex, vertices_saved, mst_heuristic)
#     # elif agent_type == 3:
#     #     return a.RealTimeAStarAgent(starting_vertex, vertices_saved, mst_heuristic)

def create_agent(agent_type: int, starting_vertex: v.Vertex, world: g.Graph):
    need_rescue_vertices = get_need_rescue_vertices(world)
    brittle_vertices = get_brittle_vertices(world)
    vertices_saved = get_vertices_list_as_vertices_saved_dict(need_rescue_vertices)
    vertices_broken = get_vertices_list_as_vertices_broken_dict(brittle_vertices)
    if agent_type == 1:
        return a.GreedyAgent(starting_vertex, vertices_saved, vertices_broken, mst_heuristic)
    elif agent_type == 2:
        return a.AStarAgent(starting_vertex, vertices_saved, vertices_broken, mst_heuristic)
    elif agent_type == 3:
        return a.RealTimeAStarAgent(starting_vertex, vertices_saved, vertices_broken, mst_heuristic)


if __name__ == "__main__":
    print('----Welcome to Hurricane Evacuation Problem----')
    world = generate_graph("input.txt")

    agent_list = []
    num_of_agents = query_number_from_user('Please enter the number of desired agents: ', 1000)

    for i in range(1, num_of_agents + 1):
        print('Please enter the desired type for agent number ' + str(i) + ':')
        print('for greedy press 1')
        print('a* press 2')
        print('for a* real time press 3')
        agent_type = query_number_from_user('', 4)
        vertices_ids = world.vertices_ids()
        print('Please enter starting vertex number: ')
        picked_valid_vertex = False
        starting_vertex = None
        while True:
            for j in range(1, len(vertices_ids) + 1):
                print(str(j) + ') ' + str(vertices_ids[j - 1]))
            starting_vertex_index = query_number_from_user('insert vertex number and press Enter ',
                                                           len(vertices_ids) + 1)
            starting_vertex_index -= 1
            starting_vertex = world.get_vertex(vertices_ids[starting_vertex_index])
            if starting_vertex is not None:
                break
            else:
                print('Please pick a valid vertex')
        new_agent = create_agent(agent_type, starting_vertex, world)
        agent_list.append(new_agent)
    program_deadline = query_number_from_user('Enter program time limit: ', 10001)
    program_variables.TIME_LIMIT = program_deadline

    print('world: ')
    print(world)
    input('Press Enter to start..')

    while not a.all_agents_terminated(agent_list):
        for agent in agent_list:
            agent.act(world)

    for agent in agent_list:
        print(agent)

    print("World at End: ")
    print(world)
