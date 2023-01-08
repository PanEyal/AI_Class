import itertools
from typing import Dict, List, Tuple, Set


class Node:
    empty = 'EMPTY'
    all_false = 'ALL_FALSE'

    def __init__(self, _name: str):
        self.name = _name
        self.probs_table: Dict[str, Dict[str, float]] = {}
        self.parents: Set[Node] = set()
        self.children: Set[Node] = set()

    @staticmethod
    def add_relation(parent: 'Node', child: 'Node') -> None:
        parent.add_child(child)
        child.add_parent(parent)

    def add_parent(self, parent: 'Node'):
        self.parents.add(parent)

    def add_child(self, child: 'Node'):
        self.children.add(child)

    def get_parents(self):
        return self.parents

    def get_children(self):
        return self.children

    def add_prob(self, value: str, cond_value: str, prob: float):
        if value not in self.probs_table.keys():
            self.probs_table[value] = {}
        self.probs_table[value][cond_value] = prob

    def get_prob(self, value: str, cond_values: List[str]) -> float:
        if len(cond_values) == 0:
            raise ValueError('No conditional values')
        if len(cond_values) == 1:
            return self.probs_table[value][cond_values[0]]
        else:
            prod = 1
            for cond_value in cond_values:
                prod *= (1 - self.probs_table[value][cond_value])
            return 1 - prod

    def get_prob_given_parents_evidence(self, value: str, parents_evidence: Set[str]) -> float:
        if len(parents_evidence) != len(self.parents):
            raise ValueError('Wrong number of parents evidence')
        if len(parents_evidence) == 0:
            parents_evidence = [Node.empty]
        else:
            parents_evidence = [pe for pe in parents_evidence if pe[:3] != 'not']
            if len(parents_evidence) == 0:
                parents_evidence = [Node.all_false]
        if value[:3] == 'not':
            return 1 - self.get_prob(value[4:], parents_evidence)
        else:
            return self.get_prob(value, parents_evidence)

    def get_conds_combinations(self, my_value: str) -> Tuple[List[List[str]], List[List[str]]]:
        conditions = list(self.probs_table[my_value].keys())
        conditions.remove(Node.all_false)
        true_conds_combs = [[Node.all_false]]
        for num_true in range(1, len(conditions) + 1):
            true_conds_combs.extend(itertools.combinations(conditions, num_true))
        true_conds_combs = [list(cond) for cond in true_conds_combs]

        # get all complementary conditions
        false_conds_combs = []
        for true_conds in true_conds_combs:
            false_conds = []
            for cond in conditions:
                if cond not in true_conds:
                    false_conds.append('not ' + cond)
            false_conds_combs.append(false_conds)

        return true_conds_combs, false_conds_combs

    def get_values(self):
        if self.name == 'W':
            return list(self.probs_table.keys())
        else:
            values_list = list(self.probs_table.keys())
            values_list.append('not ' + values_list[0])
            return values_list

    def get_ev_str(self):
        s = ''
        for my_value in self.probs_table.keys():
            true_conds_combs, false_conds_combs = self.get_conds_combinations(my_value)
            for true_conds, false_conds in zip(true_conds_combs, false_conds_combs):
                s += f'\tP(evacuees|'
                for cond in true_conds:
                    if cond == Node.all_false:
                        continue
                    s += f'{cond}, '
                for cond in false_conds:
                    s += f'{cond}, '
                s = s[:-2]
                s += f') = {self.get_prob(my_value, true_conds):.2f}\n'
        return s

    def get_bv_str(self):
        s = ''
        for my_value in self.probs_table.keys():
            for cond_value in self.probs_table[my_value].keys():
                s += f'\tP(blocked|{cond_value}) = {self.get_prob(my_value, [cond_value]):.2f}\n'
        return s

    def get_w_str(self):
        s = ''
        for my_value in self.probs_table.keys():
            s += f'\tP({my_value}) = {self.get_prob(my_value, [Node.empty]):.2f}\n'
        return s

    def __str__(self):
        if self.name == 'W':
            return self.get_w_str()
        elif self.name[:2] == 'BV':
            return self.get_bv_str()
        elif self.name[:2] == 'EV':
            return self.get_ev_str()