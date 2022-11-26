import vertex as v
from graph import Graph
import program_variables


class Saboteur:

	def __init__(self, current_vertex: v.Vertex):
		self.current_vertex = current_vertex
		self.amount_of_no_ops = 0
		self.terminate = False
		self.traverse_sequence = []

	def act(self, world: Graph):
		print("------ " + type(self).__name__ + " ------")
		if not self.terminate:
			if len(self.traverse_sequence) == 0:
				if self.amount_of_no_ops < program_variables.V:
					print("Waiting: " + str(self.amount_of_no_ops))
					self.amount_of_no_ops += 1
				else:
					self.delete_lowest_edge_and_generate_traverse_sequence(world)
					self.amount_of_no_ops = 0
			else:
				self.move()
		else:
			print("TERMINATED")

	def move(self):
		print("Current vertex: " + str(self.current_vertex))
		self.current_vertex = self.traverse_sequence[0]
		print("Moving to: " + str(self.current_vertex))
		self.traverse_sequence = self.traverse_sequence[1:]

	def delete_lowest_edge_and_generate_traverse_sequence(self, world):
		closest_neighbor_tup = world.get_closest_neighbor(self.current_vertex)
		if closest_neighbor_tup is None:
			self.terminate = True
		if not self.terminate:
			closest_neighbor = closest_neighbor_tup[0]
			print("Deleting edge: " + "(" + str(self.current_vertex) +", " + str(closest_neighbor) + ", " + str(closest_neighbor_tup[1]) + ")")
			world.delete_edge(self.current_vertex, closest_neighbor)
			closest_neighbor_tup = world.get_closest_neighbor(self.current_vertex)
			if closest_neighbor_tup is None:
				self.terminate = True
			if not self.terminate:
				closest_neighbor = closest_neighbor_tup[0]
				edge_weight = closest_neighbor_tup[1]
				for i in range(edge_weight):
					self.traverse_sequence.append(closest_neighbor)
				print("Generated sequence: " + v.vertex_list_to_string(self.traverse_sequence))
			else:
				print("TERMINATED")
		else:
			print("TERMINATED")
