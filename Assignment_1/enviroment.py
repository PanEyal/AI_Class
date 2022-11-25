import graph as g
import vertex as v

def generate_graph(file_name):
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
            pass # what is it good for?
            
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
            
            u = v.Vertex(id, people_to_rescue, brittle)
            vertices[u.id] = u
            graph.add_vertex(u)
            print(u)
        
        elif object_type == 'E':
            id = int(line[0][2])
            v1 = vertices[int(line[1])]
            v2 = vertices[int(line[2])]
            edge_weight = int(line[3][1:])
            graph.add_edge(v1, v2, edge_weight)
    
    file.close()
    return graph



if __name__ == "__main__":
    print('----Welcome to Hurricane Evacuation Problem----')
    world = generate_graph("input.txt")

