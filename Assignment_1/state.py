import vertex as v
import copy as cp
import graph as g

class State:

	def __init__(self, current_vertex: v.Vertex, vertices_saved: dict, vertices_broken: dict):
		self.current_vertex = current_vertex
		self.vertices_saved = cp.copy(vertices_saved)
		self.vertices_broken = cp.copy(vertices_broken)

	def __str__(self):
		s = "Current vertex: " + str(self.current_vertex) + "\n{"
		for vertex, saved in self.vertices_saved.items():
			s += vertex.id + ": " + ("saved" if saved else "not saved") +"\n"
		for vertex, broken in self.vertices_broken.items():
			s += vertex.id + ": " + ("broken" if broken else "intact") + "\n"
		return s+"}"

	def save_current_vertex(self):
		self.vertices_saved[self.current_vertex] = True

	def break_current_vertex(self):
		if not self.current_vertex.brittle:
			raise Exception("Tried to break a non-brittle vertex")
		self.vertices_broken[self.current_vertex] = True

	def get_unsaved_vertices(self):
		unsaved = []
		for vertex, saved in self.vertices_saved.items():
			if not saved:
				unsaved.append(vertex)
		return unsaved

	def get_intact_vertices(self):
		intact = []
		for vertex, broken in self.vertices_broken.items():
			if not broken:
				intact.append(vertex)
		return intact

	def num_of_vertices_to_save(self):
		return len(self.get_unsaved_vertices())

	# def update_vertices_status(self, world: g.Graph):
	# 	for vertex in world.get_vertices():
	# 		if vertex.people_to_rescue > 0:
	# 			self.vertices_saved[vertex] = False
	# 		else:
	# 			self.vertices_saved[vertex] = True
	# 		if vertex.brittle:
	# 			self.vertices_broken[vertex] = False
	# 		else:
	# 			self.vertices_broken[vertex] = True

	# def does_current_vertex_need_saving(self):
	# 	return not self.vertices_saved[self.current_vertex]

class StateWrapper(object):

	def __init__(self, state: State, parent_wrapper: 'StateWrapper', acc_weight: int):
		self.state = state
		self.parent_wrapper = parent_wrapper
		self.acc_weight = acc_weight