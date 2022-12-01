def semi_cooperative_comparator(id, best_value_tup, curr_value_tup):
	# TODO: fix signature to reorder from outside scope without sending id inside, ok?
	best = (best_value_tup[id], best_value_tup[1 - id], best_value_tup[2])
	curr = (curr_value_tup[id], curr_value_tup[1 - id], curr_value_tup[2])

	if best > curr:
		return best_value_tup
	else:
		return curr_value_tup


def fully_cooperative_comparator(best_value_tup, curr_value_tup):
	best = (best_value_tup[0] + best_value_tup[1], best_value_tup[2])
	curr = (curr_value_tup[0] + curr_value_tup[1], curr_value_tup[2])

	if best > curr:
		return best_value_tup
	else:
		return curr_value_tup