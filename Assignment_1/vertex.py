class Vertex(object):
	def __init__(self, id: int, people_to_rescue: int, brittle: bool):
		self.id = id
		self.people_to_rescue = people_to_rescue
		self.brittle = brittle

	def __str__(self):
		return "[V:" + str(self.id) + ", P:" + str(self.people_to_rescue) + ", B:" + str(self.brittle) + "]"


def get_vertices_list_as_string(vertices_list):
	s = "[ "
	for vertex in vertices_list:
		s += str(vertex) + ", "
	last_index_of_comma = s.rfind(",")
	if last_index_of_comma != -1:
		s = s[:last_index_of_comma] + s[last_index_of_comma + 1:]

	return s + "]"
