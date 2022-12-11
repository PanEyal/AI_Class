from typing import List, Union, Callable

import state as s
import vertex as v


class PriorityQueue(object):

    def __init__(self, f: Callable):
        self.queue: List[s.StateWrapper] = []
        self.f = f

    def __str__(self):
        return ' '.join([str(i) for i in self.queue])

    def is_empty(self) -> bool:
        return len(self.queue) == 0

    def insert(self, data: s.StateWrapper) -> None:
        self.queue.append(data)

    def pop(self) -> Union[s.StateWrapper, None]:
        if self.is_empty():
            return None
        min_elem = self.queue[0]
        min_value = self.f(self.queue[0])
        min_element_amount_to_save = self.queue[0].state.num_of_vertices_to_save()

        for elem in self.queue[1:]:
            elem_value = self.f(elem)
            elem_amount_to_save = elem.state.num_of_vertices_to_save()

            if elem_value < min_value \
                    or (elem_value == min_value
                        and elem.state.current_vertex.form != v.Form.brittle
                        and min_elem.state.current_vertex.form == v.Form.brittle) \
                    or (elem_value == min_value
                        and elem.state.current_vertex.form == min_elem.state.current_vertex.form
                        and elem.state.current_vertex.id < min_elem.state.current_vertex.id):
                min_elem = elem
                min_value = elem_value
                min_element_amount_to_save = elem_amount_to_save

        self.queue.remove(min_elem)
        print(min_elem.state.current_vertex, min_value)
        return min_elem
