import sympy_util
import itertools

def check_qubo(sym_tuple, v_states, qubo):
    # Get the set of all variables in the qubo and subtract from it
    # the set of the logical variables to obtain the set of auxiliary
    # variables.
    all_vars = sympy_util.poly_vars(qubo)
    aux_vars = list(all_vars - set(sym_tuple))

    # For each setting of the logical variables, compute the minimum
    # objective for all possible settings of the auxiliary variables.
    # Save this into the all_obj dict:
    all_obj = dict()
    for state in itertools.product([0,1], repeat=len(sym_tuple)):
        substitutions = [(sym_tuple[i], state[i]) for i in range(len(sym_tuple))]
        min_obj = None
        for aux_state in itertools.product([0,1], repeat=len(aux_vars)):
            aux_substitutions = [(aux_vars[i], aux_state[i]) for i in range(len(aux_vars))]
            all_substitutions = substitutions + aux_substitutions
            obj = qubo.subs(all_substitutions)
            if min_obj is None or obj < min_obj:
                min_obj = obj
        all_obj[tuple(state)] = min_obj

    # Iterate over all logical states (skipping the auxiliary
    # variables).  For valid states, compute the minimum and maximum
    # objective seen.  For invalid states, compute the minimum
    # objective seen.
    min_valid_obj = None
    max_valid_obj = None
    min_invalid_obj = None
    for state in itertools.product([0,1], repeat=len(sym_tuple)):
        obj = all_obj[state]
        if state in v_states:
            if min_valid_obj is None or obj < min_valid_obj:
               min_valid_obj = obj
            if max_valid_obj is None or obj > max_valid_obj:
               max_valid_obj = obj
        else:
            if min_invalid_obj is None or obj < min_invalid_obj:
                min_invalid_obj = obj

    return min_valid_obj, max_valid_obj, min_invalid_obj


def spectrum(sym_tuple, v_states, qubo):
    # Get the set of all variables in the qubo and subtract from it
    # the set of the logical variables to obtain the set of auxiliary
    # variables.
    all_vars = sympy_util.poly_vars(qubo)
    aux_vars = list(all_vars - set(sym_tuple))

    # For each valid state, compute the objective for all possible settings
    # of the auxiliary variables and save the entire set of objective values
    # and number of occurrences into a histogram which is keyed by the valid_states:
    valid_states_hist = dict()
    for state in v_states:
        this_state_hist = dict()
        substitutions = [(sym_tuple[i], state[i]) for i in range(len(sym_tuple))]
        for aux_state in itertools.product([0,1], repeat=len(aux_vars)):
            aux_substitutions = [(aux_vars[i], aux_state[i]) for i in range(len(aux_vars))]
            all_substitutions = substitutions + aux_substitutions
            obj = qubo.subs(all_substitutions)
            if obj in this_state_hist:
                this_state_hist[obj] += 1
            else:
                this_state_hist[obj] = 1
            if obj == 0:
                ground_state_aux_vars = aux_substitutions
        valid_states_hist[state] = (this_state_hist, ground_state_aux_vars)

    # For each invalid state, compute the objective for all possible settings
    # of the logical and auxiliary variables and save the entire set of objective
    # values and number of occurrences into a single histogram:
    invalid_states_hist = dict()
    for state in itertools.product([0,1], repeat=len(sym_tuple)):
        if state in v_states: continue
        substitutions = [(sym_tuple[i], state[i]) for i in range(len(sym_tuple))]
        for aux_state in itertools.product([0,1], repeat=len(aux_vars)):
            aux_substitutions = [(aux_vars[i], aux_state[i]) for i in range(len(aux_vars))]
            all_substitutions = substitutions + aux_substitutions
            obj = qubo.subs(all_substitutions)
            if obj in invalid_states_hist:
                invalid_states_hist[obj] += 1
            else:
                invalid_states_hist[obj] = 1

    return valid_states_hist, invalid_states_hist

