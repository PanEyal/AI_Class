class Vertex(object):
	def __init__(self, id, people_to_rescue, brittle):
		self.id = id
		self.people_to_rescue = people_to_rescue
		self.brittle = brittle

	def __str__(self):
		return "[V:" + str(self.id) + ", P:" + str(self.people_to_rescue) + ", B:" + str(self.brittle) + "]"

