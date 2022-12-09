from typing import List

import yaml

import agent as a
import graph as g
import vertex as v
import state as s


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


def create_agent(game_type: int, world: g.Graph, starting_vertices: List[v.Vertex], _id: int, ply_limit: int):
    vertices_saved = savable_vertex_list_to_vertices_saved_dict(world.get_savable_vertices())
    vertices_broken = Breakable_vertex_list_to_vertices_broken_dict(world.get_brittle_vertices())
    initial_state = s.State(starting_vertices, vertices_saved, vertices_broken, ply_limit)

    if game_type == 'ADVERSARIAL':
        return a.AdversarialAgent(initial_state, _id)
    elif game_type == 'SEMI-COOP':
        return a.SemiCoopAgent(initial_state, _id)
    elif game_type == 'FULLY-COOP':
        return a.FullyCoopAgent(initial_state, _id)


def simulator():
    print('----Welcome to Hurricane Evacuation Problem----')

    print('loading config.yaml file...')
    with open("Inputs/config.yaml", "r") as f:
        config = yaml.safe_load(f)

    world = generate_graph(config['GAME_SPECS']['INPUT_PATH'])
    vertices_ids = world.vertices_ids()

    agents = []
    agents_names = []
    starting_vertices = [world.get_vertex(vertices_ids[i - 1]) for i in config['GAME_SPECS']['STARTING_VERTICES']]
    game_type = config['GAME_SPECS']['TYPE']
    agents.append(create_agent(game_type, world, starting_vertices, 0, config['GAME_SPECS']['PLY_LIMIT']))
    agents_names.append('Agent 0')
    agents.append(create_agent(game_type, world, starting_vertices, 1, config['GAME_SPECS']['PLY_LIMIT']))
    agents_names.append('Agent 1')
    print('agents: ')
    for agent_name, starting_vertex in zip(agents_names, starting_vertices):
        print(agent_name + ' starting vertex index: ' + str(starting_vertex.id))
    print('world: ')
    print(world)
    print('game type: ' + game_type)
    input('Press Enter to start...')
    new_state = None
    while not a.all_agents_terminated(agents):
        for agent in agents:
            if new_state is not None:
                agent.state = new_state
            print(f'\nAGENT {agent.id})')
            new_state = agent.act(world)

    print("\n\n\nAGENTS SCORES: ")
    for agent_idx, agent in enumerate(agents):
        print(f'\n#### AGENT {agent_idx + 1}): {str(agents_names[agent_idx])} ####')
        print(agent)

    print("World at End: ")
    print(world)


if __name__ == "__main__":
    simulator()
