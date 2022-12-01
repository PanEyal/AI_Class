import yaml
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

def simulator():
    print('----Welcome to Hurricane Evacuation Problem----')

    print('loading config.yaml file...')
    with open("Inputs/config.yaml", "r") as f:
        config =  yaml.safe_load(f)

    world = generate_graph(config['RUN']['INPUT_PATH'])
    vertices_ids = world.vertices_ids()

    agents = []
    agents_locs_name = []
    for agent_name, starting_vertex_index in config['RUN']['AGENTS']:
        starting_vertex = world.get_vertex(vertices_ids[starting_vertex_index - 1])
        new_agent = create_agent(config[agent_name]['ID'], starting_vertex, world, config[agent_name]['TIME_LIMIT'], config['WORLD']['TIME_LIMIT'], config['WORLD']['T'])
        agents.append(new_agent)
        agents_locs_name.append((agent_name, starting_vertex_index))
    print('agents: ')
    print(agents_locs_name)
    print('world: ')
    print(world)
    input('Press Enter to start..')

    while not a.all_agents_terminated(agents):
        for agent_idx, agent in enumerate(agents):
            print(f'\nAGENT {agent_idx+1}): {str(agents_locs_name[agent_idx][0])}')
            agent.act(world)

    print("\n\n\nAGENTS SCORES: ")
    for agent_idx, agent in enumerate(agents):
        print(f'\n#### AGENT {agent_idx + 1}): {str(agents_locs_name[agent_idx][0])} ####')
        print(agent)

    print("World at End: ")
    print(world)



if __name__ == "__main__":
    simulator()
