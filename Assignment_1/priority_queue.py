import sys
import state as s

class PriorityQueue(object):

    def __init__(self, f):
        self.queue : [s.StateWrapper] = []
        self.f = f

    def __str__(self):
        return ' '.join([str(i) for i in self.queue])

    def is_empty(self):
        return len(self.queue) == 0

    def insert(self, data):
        self.queue.append(data)

    def pop(self):
        if self.is_empty():
            return None
        min_elem = self.queue[0]
        min_value = self.f(self.queue[0])
        min_element_amount_to_save = self.queue[0].state.num_of_vertices_to_save()

        for elem in self.queue[1:]:
            elem_value = self.f(elem)
            elem_amount_to_save = elem.state.num_of_vertices_to_save()

            if elem_value < min_value\
                or (elem_value == min_value
                    and elem_amount_to_save < min_element_amount_to_save)\
                or (elem_value == min_value
                    and elem_amount_to_save == min_element_amount_to_save
                    and (elem.state.does_current_vertex_need_saving()
                        and (not min_elem.state.does_current_vertex_need_saving()))):
                min_elem = elem
                min_value = elem_value
                min_element_amount_to_save = elem_amount_to_save

        self.queue.remove(min_elem)
        return min_elem
