import itertools
from typing import Dict, List, Tuple


class Node:
    empty = 'EMPTY'
    all_false = 'ALL_FALSE'

    def __init__(self, _name: str):
        self.name = _name
        self.probs_table: Dict[str, Dict[str, float]] = {}

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

    def __str__(self):
        s = ''
        for my_value in self.probs_table.keys():
            if my_value == 'mild' or my_value == 'stormy' or my_value == 'extreme':
                s += f'\tP({my_value}) = {self.get_prob(my_value, [Node.empty]):.2f}\n'
            elif my_value == 'blocked':
                for cond_value in self.probs_table[my_value].keys():
                    s += f'\tP({my_value}|{cond_value}) = {self.get_prob(my_value, [cond_value]):.2f}\n'
            elif my_value == 'evacuees':

                true_conds_combs, false_conds_combs = self.get_conds_combinations(my_value)
                for true_conds, false_conds in zip(true_conds_combs, false_conds_combs):
                    s += f'\tP({my_value}|'
                    for cond in true_conds:
                        if cond == Node.all_false:
                            continue
                        s += f'{cond}, '
                    for cond in false_conds:
                        s += f'{cond}, '
                    s = s[:-2]
                    s += f') = {self.get_prob(my_value, true_conds):.2f}\n'
        return s
