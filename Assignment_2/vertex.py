from enum import Enum


class Form(Enum):
    stable = 0
    brittle = 1
    broken = 2


class Vertex(object):
    def __init__(self, id: int, people_to_rescue: int, form: Form):
        self.id = id
        self.people_to_rescue = people_to_rescue
        self.form = form

    def __str__(self):
        return "[V:" + str(self.id) + ", P:" + str(self.people_to_rescue) + ", F:" + str(self.form.name) + "]"
