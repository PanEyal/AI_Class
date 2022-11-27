import fnmatch
import os
import sys
from typing import List

import agent as a
import graph as g
import state as s
import vertex as v


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


def savable_vertex_list_to_vertices_saved_dict(v_list: List[v.Vertex]):
    v_dict = dict()
    for vertex in v_list:
        v_dict[vertex] = False
    return v_dict


def Breakable_vertex_list_to_vertices_broken_dict(v_list: List[v.Vertex]):
    v_dict = dict()
    for vertex in v_list:
        v_dict[vertex] = False
    return v_dict


def mst_heuristic(state_wrapper: s.StateWrapper, world: g.Graph) -> int:
    unsaved_vertices = state_wrapper.state.get_unsaved_vertices()
    essential_vertices = unsaved_vertices
    if state_wrapper.state.current_vertex not in essential_vertices:
        essential_vertices.append(state_wrapper.state.current_vertex)
    zipped_graph = g.zip_graph(world, essential_vertices)
    mst_zipped = zipped_graph.MST()
    return mst_zipped.get_sum_weights()


def query_number_from_user(text, limit):
    inserted_valid_value = False
    inserted_num = 0
    while not inserted_valid_value:
        inserted_value = input(text)
        if inserted_value == 'exit':
            exit(0)
        try:
            inserted_num = int(inserted_value)
            if limit > inserted_num > 0:
                inserted_valid_value = True
            else:
                print(f'invalid value: {inserted_value}. should be a number between 0 and {str(limit)}')
        except ValueError:
            print(f'invalid value: {inserted_value}. should be a number between 0 and {str(limit)}')
    return inserted_num


def create_agent(agent_type: int, starting_vertex: v.Vertex, world: g.Graph, expansion_limit: int, time_limit: int,
                 T: float):
    vertices_saved = savable_vertex_list_to_vertices_saved_dict(world.get_savable_vertices())
    vertices_broken = Breakable_vertex_list_to_vertices_broken_dict(world.get_brittle_vertices())
    if agent_type == 1:
        return a.GreedyAgent(starting_vertex, vertices_saved, vertices_broken, mst_heuristic, expansion_limit,
                             time_limit, T)
    elif agent_type == 2:
        return a.AStarAgent(starting_vertex, vertices_saved, vertices_broken, mst_heuristic, expansion_limit,
                            time_limit, T)
    elif agent_type == 3:
        return a.RealTimeAStarAgent(starting_vertex, vertices_saved, vertices_broken, mst_heuristic, expansion_limit,
                                    time_limit, T)


def main():
    T = 0.01
    GREEDY_LIMIT = 1
    ASTAR_LIMIT = 10000
    REALTIME_ASTAR_LIMIT = 10
    expansion_limits = [GREEDY_LIMIT, ASTAR_LIMIT, REALTIME_ASTAR_LIMIT]

    print('----Welcome to Hurricane Evacuation Problem----')

    dir_path = r'Inputs/'
    num_of_inputs = len(fnmatch.filter(os.listdir(dir_path), '*.txt')) + 1

    input_num = query_number_from_user('Please enter the number of the input file: ', num_of_inputs)
    world = generate_graph(f"Inputs/input{input_num}.txt")

    agent_list = []
    agents_num = query_number_from_user('Please enter the number of desired agents: ', 1000)

    time_limit = query_number_from_user('Enter program time limit: ', 10001)

    for i in range(1, agents_num + 1):
        print('Please enter the desired type for agent number ' + str(i) + ':')
        print('for greedy press 1')
        print('a* press 2')
        print('for a* real time press 3')
        agent_type = query_number_from_user('', 4)
        vertices_ids = world.vertices_ids()
        print('Please enter starting vertex number: ')
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
        new_agent = create_agent(agent_type, starting_vertex, world, expansion_limits[agent_type - 1], time_limit, T)
        agent_list.append(new_agent)
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


if __name__ == "__main__":
    main()
